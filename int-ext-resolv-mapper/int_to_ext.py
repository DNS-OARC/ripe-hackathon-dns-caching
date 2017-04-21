from ripe.atlas.cousteau import AtlasResultsRequest, AtlasStream
import attr
import logging
from pprint import pprint as pp
import pyasn
import base64
import dnslib
import click
import json
from ipaddress import ip_address
from enum import IntEnum
from datetime import datetime, timedelta

# TODO use ripestats for realtime info
asndb = pyasn.pyasn('ipasn.20170420.1200')
with open("../enrich-probe-info/prbid_to_info.json") as f:
    probe_db = json.load(f)

HOMEPROBE = 27635

"""
   * https://atlas.ripe.net/measurements/8310237/ (google 'whoami')
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

def get_probe_info(probe_id):
    try:
        return probe_db[str(probe_id)]
    except:
        return None

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
    edns0_subnet_info = attr.ib()

    def pretty(self):
        return "[%s] [%s] ext: %s, ext_resolver: %s, edns0: %s" % (self.from_probe,
                                                                   self.measurement_type,
                                                                   self.from_ip,
                                                                   self.external_resolvers,
                                                                   self.edns0_subnet_info)

    def merge(self, y):
        self.external_resolvers = self.external_resolvers.union(y.external_resolvers)
        self.resolver_asn = self.resolver_asn.union(y.resolver_asn)
        self.internal_resolvers = self.internal_resolvers.union(y.internal_resolvers)

        return self

def parse_result(results):
    for res in results:
        if "resultset" in res:
            res_set = res["resultset"]
            from_ip = res["from"]
            from_probe = res["prb_id"]
            probe_info = {}
            subnet_info = None
            meas_type = MeasurementType(res["msm_id"])
            if "probe" in res:
                probe_info = res["probe"]
            else:
                probe_info = get_probe_info(from_probe)

            for res_measure in res_set:
                if "result" not in res_measure:
                    _LOGGER.error("no results in measure: %s", res_measure)
                    continue

                ext_resolver = None

                #pp(res_measure)
                try:
                    dns_buf = dnslib.DNSRecord.parse(base64.b64decode(res_measure["result"]["abuf"]))
                except dnslib.dns.DNSError as ex:
                    _LOGGER.warning("Unable to parse abuf: %s" % ex)
                    continue

                int_resolver = res_measure["dst_addr"]
                if len(dns_buf.rr) < 1 or dns_buf.a.rdata is None:
                    _LOGGER.error("got no rdata")
                    # TODO gotta return non-true indicator here
                    continue

                for rr in dns_buf.rr:
                    rr_s = str(rr.rdata).strip('"')
                    if rr_s.startswith("edns0-client-subnet"):
                        subnet_info = rr_s.split(" ")[1]
                    else:
                        try:
                            ip = ip_address(rr_s)
                            if ext_resolver is not None:
                                #raise Exception("resolver was already set by another rr")
                                _LOGGER.warning("resolver was already set: %s" % dns_buf)
                            ext_resolver = str(ip)
                        except ValueError as ex:
                            _LOGGER.warning("got unknown rdata: %s" % rr_s)


                #pp(dns_buf.a)
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
                                    measurement_type=meas_type,
                                    edns0_subnet_info=subnet_info)
                yield info

def get_resolver_info(probe_ids, measurement):
    kwargs = {
        "msm_id": measurement,
        "start": datetime.utcnow() - timedelta(hours = 2),
        # "stop": datetime(2017, 4, 2),
    }
    if probe_ids:
    	kwargs["probe_ids"] = probe_ids
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
        print(res.pretty())
        #pp(attr.asdict(res))

def got_result(results):
    for res in parse_result([results]):
        print(res.pretty())
        #pp(attr.asdict(result))
        continue


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
        raise Exception() from ex
    finally:
        stream.disconnect()

if __name__ == "__main__":
    cli()
