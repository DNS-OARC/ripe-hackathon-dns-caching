# ripe-hackathon-dns-caching
Everything you ever wanted to know about caching resolvers but were afraid to ask

## Hackathon etherpad

```
* (Willem) Resolver properties and capabilities.
  * As mentioned above in previous proposals already, RIPE Atlas probes have a very nice inside perspective on resolvers in the networks where those probes are.  What are the properties and capabilities of those resolvers.
  (Jerry) See my note above on user probes
  (willem) I saw your comment. Maybe it doesn't matter. I know how the big public resolvers respond, It's the other ones that I'm interested in...  Also, isn't the origin of the upstream resolver (dhcp or manual entry) in the probes data?
  (jerry) if you dont specify target it will use the probes configured resolver and there is IPs in the result data so you see who answered
  (willem) What about the probes information... so not the result data, but the query for the probe ID.
           Just checked... so it is not in there.
           This hackathon is about giving feedback too.  This would be a nice addition.  Indicate the origin of the resolver.
    * The IP on the remote end whoami.akamai.net or o-o.myaddr.l.google.com. to inventory the resolver AS'es
    * DNSSEC capabilities
      * Is it validating? (Can we compare with APNIC Google-ad measurements at https://stats.labs.apnic.net/dnssec )
        * Which algorithms can be validated.  I know Olafur has a matrix of domains at cloudfare which can be used to test this.  He targeted it with his hackathon project in Prague I think... I could check.
      * If not validating, is the provided data usable by a validating stub?
        * Are signatures given?
        * Is valid proof for non-existant answers given?
        * Is valid proof for wildcard answers given?
    * Can it resolve IPv6-only domains / Qname minimisation / TCP support (Jerries cmdns things)
    (Jerry) This really requires a controllable authority to test against, it is possible to integrate Atlas with CheckMyDNS but that's going to be more work then what fits within the hackathon
    (Willem) So I know the anchors serve some domain names for testing PMTU.  Perhaps they could be equiped with more dynamic authoritatives as well (for example that echo the contacting IP, or that detect qname minimisation).
      * Yes Jerry, I think we have some of those authorities with internet.nl too... let me check.
        I cannot find it now, I have to ask Ralph again, but we do have queries you can do to test for
        qname minimisation... dig qnamemintest.internet.nl TXT
        (jerry) did a quick measurement, 3 out of 795(500 probes) had qname minimization :)
        Wow!  That's not bad!
        I know! Was expecting zero :) maybe I hit all of Stephane's probes :)
    * Are fragmented responses accepted/reassembled (with IPv4 and IPv6)
    * What is the maximum path MTU
   * etc.
```

## Teams etherpad

```
Everything you ever wanted to know about caching resolvers but you were afraid to ask.com

Goal: provide insight into caching resolver capabilities

Output:
    * per probe Dashboard
    * world map per capability
    * per ASN dashboar
    * per cache dashboard (cache-cloud in / cache cloud out)

measurements:
    * https://atlas.ripe.net/measurements/8310237/  (google 'whoami')
    * https://atlas.ripe.net/measurements/8310245/ (akamai 'whoami')
    * https://atlas.ripe.net/measurements/8310250/ (qname minimisation test)
    * https://atlas.ripe.net/measurements/8310360/ (TCP IPv4 capability)
    * https://atlas.ripe.net/measurements/8310364/ (TCP IPv6 capability)
    * https://atlas.ripe.net/measurements/8310366/ (IPv6 capability)
    * https://atlas.ripe.net/measurements/8311760/ (DNSSEC reference)
    * https://atlas.ripe.net/measurements/8311763/ (DNSSEC bogus)
    * https://atlas.ripe.net/measurements/8311777/ (NXDOMAIN hijacking)

tasks:
    write python code for caching resolver availability (per probe: percentage for a time period: hour/day/week?) (andrea)
        curl "https://atlas.ripe.net/api/v2/measurements/30002/results/?format=txt" | head -50000 | jq -c "[.prb_id, .timestamp , .resultset[0].dst_addr, .resultset[0].result.rt]" | less  (but pretty)
    Writing a DNS server in Go to answer a few things we want to measure on the exit resolvers
    I have reconfigured a FreeBSD jail (which we don't use anymore) to host the go authoritative:
    bill.nlnetlabs.nl
    Anyone who pasts their ssh public key here, will be added to the authorized_keys file of the hackathon account thereon.
    The machine has 3 IPv4 and 3 IPv6 addresses:
    185.49.141.10, 185.49.141.17, 185.49.141.18, 2a04:b900:0:100::10, 2a04:b900:0:100::17, 2a04:b900:0:100::18
    The delegations in the nlnetlabs.nl zone:
    ripe-hackathon4         NS      ripe-hackathon4-ns
    ripe-hackathon4-ns      A       185.49.141.10
    ripe-hackathon6         NS      ripe-hackathon6-ns
    ripe-hackathon6-ns      AAAA    2a04:b900:0:100::10     
    ripe-hackathon          NS      bill
    bill                    A       185.49.141.17
                            AAAA    2a04:b900:0:100::17
    Identifying the resolvers in use by ATLAS Probes.
    Emile is creating a measurement to target whoami.akamai.net A and o-o.myaddr.l.google.com TXT
    The IPv6 addresses should come from the custom
    <probe_id>.ripe-hackathon6.nlnetlabs.nl AAAA
    Probe<->caching resolver mapping (Teemu) (DONE)


    DATA STRUCTURE

{'external_resolvers': '213.222.196.1',
 'from_ip': '213.222.196.2',
 'from_probe': 14813,
 'internal_resolvers': '213.222.196.1',
 'resolver_asn': 28785,
 'resolver_net': '213.222.192.0/21',
 'ts': 1492691456}

{
    "ts": <unixtime>,
    "from_ip": <probe external ip>,
    "from_probe": <probe id>,
    "internal_resolvers": '127.0.0.2',
    "external_resolvers": '123.123.123.123',
    "resolver_asn": Resolver AS,
    "resolver_net": '127.0.0.0/8'
}

    - All lists elements relates to each other on the same list position, e.i. internal_resolvers[0] is where the probe sent the query and external_resolvers[0] is where the query came from


TCP IPv4 capability: (DONE)
    <probe_id>.tc.ripe-hackathon4.nlnetlabs.nl A

    TCP IPv6 capability: (DONE)
    <probe_id>.tc.ripe-hackathon6.nlnetlabs.nl AAAA

    IPv6 capability:
    <probe-id>.ripe-hackathon6.nlnetlabs.nl AAAA


    Identify resolvers that do qname minimisation: (DONE)
    qnamemintest.internet.nl TXT


    Validating DNSSEC
    secure.ripe-hackathon2.nlnetlabs.nl A  (DONE)
    bogus.ripe-hackathon2.nlnetlabs.nl A   (DONE)


    Measure NXDOMAIN hijacking
    nxdomain.ripe-hackathon2.nlnetlabs.nl A (DONE)


    * Geoloc information of probes into result json?


Ideas for name
    resolvation
    resolver galore
    upstream galore
    what's up


Interesting findings:
    * google's whoami returns sometimes /32 as edns0 subnet


    Resolver capabilities json per probe <probe_id>.json
    {
        "probe_id": <probe_id>
        "resolvers": [
            {
                "internal": <internal_ip>,
                "resolver_net": <resolver_net>
                "resolver_asn": <resolver_asn>
                "edns0_client_subnet": "client subnet"
                "ipv6_cap": true or missing
                "ipv4_tcp": true or missing
                "ipv6_tcp": true or missing
                "qname_minimization": true or missing
            }, ...]
    }


Future work:
    *Geolocate caching resolvers


Result from the hackathon:
    * ripe atlas measurements that we'll continue on caching resolver capabilities


Feature request:
    * get ripe atlas anchors to do a whois.akamai.net type service
    * ability to set QR bit / EDNS1 / EDNS2 (think about testing things that can break things, is that in the remit of ripe atlas?)
    * RD bit not set: does still work for 'use probe resolver'. why?


    Availability data sample: https://insomniac.slackware.it/static/availability.json
           divided per probe: https://insomniac.slackware.it/static/availability.tar.gz


Website: http://sg-pub.ripe.net/petros/dnsthought/


https://github.com/DNS-OARC/ripe-hackathon-dns-caching

Name                     Github username               Email                       Affiliation
Andrea Barberio          insomniacslk                  insomniac@slackware.it      Facebook
Petros Gigis             pgigis                        pgkigkis@ripe.net           RIPE NCC/FORTH
Jerry Lundström          jelu                          jerry@dns-oarc.net          DNS-OARC
Teemu Rytilahti          rytilahti                     teemu.rytilahti@rub.de      HGI, Ruhr-University Bochum
Willem Tooroop           wtoorop                       willem@nlnetlabs.nl         NLnet Labs
```
