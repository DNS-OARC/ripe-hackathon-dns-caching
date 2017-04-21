#!/usr/bin/env python3

from int_to_ext import *
import json

if __name__ == "__main__":
	probes = dict()
	geo = dict()
	
	for res in get_info(None):
		pid = res.from_probe

		if res.probe_info and pid not in geo:
			geo[pid] = {'latitude': res.probe_info['latitude'], 'longitude': res.probe_info['longitude']}
		if pid not in probes:
			p = probes[pid] = dict()
			rs = p['resolvers'] = dict()
		else:
			p = probes[pid]
			rs = p['resolvers']

		if res.probe_info and 'asn_v4' in res.probe_info:
			p['asn_v4'] = res.probe_info['asn_v4']

		if res.probe_info and 'asn_v6' in res.probe_info:
			p['asn_v6'] = res.probe_info['asn_v6']

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

	resolvers = dict()
	caps = ['qname_minimization', 'ipv6_cap', 'ipv4_tcp', 'ipv6_tcp', 'edns0_client_subnet']
	for pid, p in probes.items():
		p['probe_id'] = pid
		p['resolvers'] = list(p['resolvers'].values())
		for cap in caps:
			enabled = True
			for r in p['resolvers']:
				if cap not in r:
					enabled = False
			p[cap] = enabled

		with open('probes/%d.json' % pid, 'w') as f:
			json.dump(p, f)

		done = set()
		for r in p['resolvers']:
			if 'resolver_net' not in r:
				continue
			rid = r['resolver_net']
			if rid in done:
				continue
			done.add(rid)
			if rid not in resolvers:
				pr = resolvers[rid] = dict()
				ps = pr['probes'] = list()
			else:
				pr = resolvers[rid]
				ps = pr['probes']
			try:
				ps.append({'probe_id': pid, 'latitude': geo[pid]['latitude'], 'longitude': geo[pid]['longitude']})
			except KeyError:
				ps.append({'probe_id': pid})
			
			for cap in caps:
				if cap in r:
					pr[cap] = True
	
	for res_id, r in resolvers.items():
		res_id = res_id.replace('/', '-')
		for cap in caps:
			if cap not in r:
				r[cap] = False
		with open('resolvers/%s.json' % res_id, 'w') as f:
			json.dump(r, f)

