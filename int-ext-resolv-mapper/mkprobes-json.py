#!/usr/bin/env python3

from int_to_ext import *
import json

if __name__ == "__main__":
	probes = dict()
	resolvers = dict()
	
	for res in get_info(None):
		pid = res.from_probe
		if pid not in probes:
			p = probes[pid] = dict()
			rs = p['resolvers'] = dict()
		else:
			p = probes[pid]
			rs = p['resolvers']

		if res.internal_resolvers not in rs:
			r = rs[res.internal_resolvers] = dict()
		else:
			r = rs[res.internal_resolvers]

		r['internal'] = res.internal_resolvers
		if res.resolver_net:
			r['resolver_net'] = res.resolver_net
		if res.resolver_asn:
			r['resolver_asn'] = res.resolver_asn
		if res.edns0_subnet_info:
			r['edns0_client_subnet'] = res.edns0_subnet_info
		if res.qname_minimization:
			r['qname_minimization'] = True

		if res.measurement_type == MeasurementType.ipv4_tcp and res.external_resolvers:
			r['ipv4_tcp'] = True

		if res.measurement_type == MeasurementType.ipv6_tcp and res.external_resolvers:
			r['ipv6_tcp'] = True

		if res.measurement_type == MeasurementType.ipv6_cap and res.external_resolvers:
			r['ipv6_cap'] = True



	for pid, p in probes.items():
		p['probe_id'] = pid
		p['resolvers'] = list(p['resolvers'].values())
		with open('probes/%d.json' % pid, 'w') as f:
			json.dump(p, f)

