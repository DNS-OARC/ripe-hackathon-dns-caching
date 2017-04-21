from ripe.atlas.cousteau import AtlasResultsRequest, AtlasStream
import attr
import logging
from pprint import pprint as pp
import pyasn
import base64
import dnslib
import click
from enum import IntEnum

# TODO use ripestats for realtime info
asndb = pyasn.pyasn('ipasn.20170420.1200')

HOMEPROBE = 27635

"""
   * https://atlas.ripe.net/measurements/8310245/ (akamai 'whoami')
    * https://atlas.ripe.net/measurements/8310250/ (qname minimisation test)
    * https://atlas.ripe.net/measurements/8310360/ (TCP IPv4 capability)
    * https://atlas.ripe.net/measurements/8310364/ (TCP IPv6 capability)
    * https://atlas.ripe.net/measurements/8310366/ (IPv6 capability)"""

# TODO qname minin: would be nice to have ip as payload
# 'system-resolver-mangles-case', -> inform about 0x20 encoding?

# measurements to listen to
class MeasurementType(IntEnum):
    akamai_whois = 8310245
    google_whois = 8310237
    qname_minim = 8310250
    ipv4_tcp = 8310360
    ipv6_tcp = 8310364
    ipv6_cap = 8310366

    # TODO dnssec, normal check, needs some merge work
    #


def get_asn(ip):
    try:
        return asndb.lookup(ip)
    except ValueError as ex:
        _LOGGER.error("%s", ex)

logging.basicConfig(level=logging.DEBUG)
logging.getLogger("socketIO-client").setLevel(logging.WARNING) # silence socketio client
_LOGGER = logging.getLogger(__name__)

@attr.s
class ResolverInfo:
    ts = attr.ib()
    from_ip = attr.ib()
    from_probe = attr.ib()
    measurement_type = attr.ib()

    internal_resolvers = attr.ib()
    external_resolvers = attr.ib()
    resolver_asn = attr.ib()
    resolver_net = attr.ib()
    probe_info = attr.ib()

    def merge(self, y):
        self.external_resolvers = self.external_resolvers.union(y.external_resolvers)
        self.resolver_asn = self.resolver_asn.union(y.resolver_asn)
        self.internal_resolvers = self.internal_resolvers.union(y.internal_resolvers)

        return self

def parse_result(results):
    for res in results:
        pp(res)
        if "resultset" in res:
            res_set = res["resultset"]
            from_ip = res["from"]
            from_probe = res["prb_id"]
            probe_info = {}
            meas_type = MeasurementType(res["msm_id"])
            if "probe" in res:
                probe_info = res["probe"]

            for res_measure in res_set:
                if "result" not in res_measure:
                    _LOGGER.error("no results in measure: %s", res_measure)
                    continue
                dns_buf = dnslib.DNSRecord.parse(base64.b64decode(res_measure["result"]["abuf"]))

                int_resolver = res_measure["dst_addr"]
                if dns_buf.a.rdata is None:
                    _LOGGER.error("got no rdata")
                    # TODO gotta return non-true indicator here
                    continue
                ext_resolver = str(dns_buf.a.rdata).strip('"')
                x = get_asn(ext_resolver)
                if x is None:
                    asn = net = None
                else:
                    asn, net = x


                """
                <DNS RR: 'whoami.akamai.net.' rtype=A rclass=IN ttl=180 rdata='134.147.25.250'>
                <DNS RR: 'o-o.myaddr.l.google.com.' rtype=TXT rclass=IN ttl=60 rdata='"134.147.25.250"'>
                """

                info = ResolverInfo(ts=res["timestamp"],
                                    from_ip=from_ip,
                                    from_probe=from_probe,
                                    internal_resolvers=int_resolver,
                                    external_resolvers=ext_resolver,
                                    resolver_net=net,
                                    resolver_asn=asn,
                                    probe_info=probe_info,
                                    measurement_type=meas_type)
                yield info

def get_resolver_info(probe_ids, measurement):
    kwargs = {
        "msm_id": measurement,
        # "start": datetime(2017, 4, 1),
        # "stop": datetime(2017, 4, 2),
        "probe_ids": probe_ids
    }
    is_success, results = AtlasResultsRequest(**kwargs).create()
    if not is_success:
        _LOGGER.error("Request failed: %s %s", probe_ids, measurement)
        return []

    return parse_result(results)


def get_info(probe):
    #nlnet = get_resolver_info(probe)
    import itertools
    measurements = [get_resolver_info(probe, measure) for measure in MeasurementType]
    if measurements is None:
        _LOGGER.error("could not get any requested info")
        return
    for x in itertools.chain(*measurements):
        yield x
        #if x.from_probe in res:
        #    res[x.from_probe].merge(x)
        #else:
        #    res[x.from_probe] = x

    #return res

@click.group()
def cli():
    pass

@cli.command()
def stored():
    q = [HOMEPROBE]  # , 1,2,3,4]
    q = None
    for res in get_info(q):
        pp(attr.asdict(res))

def got_result(results):
    for result in parse_result([results]):
        pp(attr.asdict(result))

@cli.command()
def stream():
    stream = AtlasStream()
    stream.connect()

    try:
        stream.bind_channel("result", got_result)

        for meas in MeasurementType:
            stream_parameters = {"msm": meas,
                                 "type": "dns",
                                 "enrichProbes": True,
                                 "sendBacklog": False,
                                 }
            stream.start_stream(stream_type="result", **stream_parameters)
            stream.timeout(5)

        while True:
            import time
            time.sleep(0.1)

    except Exception as ex:
        _LOGGER.warning("Got ex: %s" % ex)
    finally:
        stream.disconnect()

if __name__ == "__main__":
    cli()