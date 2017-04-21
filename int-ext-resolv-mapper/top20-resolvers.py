#!/usr/bin/env python3

from int_to_ext import *
import json

if __name__ == "__main__":
	probes = dict()
	resolvers = dict()
	
	for res in get_info(None):
		if not res.resolver_net:
			continue

		if res.resolver_net not in resolvers:
			r = resolvers[res.resolver_net] = dict()
			r['probes'] = set()
			r['edns0_client_subnet'] = False
		else:
			r = resolvers[res.resolver_net]

		if not res.probe_info:
			continue

		r['probes'].add((res.from_probe, res.probe_info['latitude'], res.probe_info['longitude']))
		if res.edns0_subnet_info:
			r['edns0_client_subnet'] = True

	i = 1
	top20 = set()
	top20_list = list()
	rest = set()
	rest_list = list()

	for n, k in sorted([(len(r['probes']), k) for k, r in resolvers.items()], reverse = True):
		r = resolvers[k]
		for p in [{'probe_id': p, 'latitude': lat, 'longitude': lon} for p, lat, lon in list(r['probes'])]:
			if i <= 20:
				if p['probe_id'] not in top20:
					top20.add(p['probe_id'])
					top20_list.append(p)
			elif p['probe_id'] not in top20:
				if p['probe_id'] not in rest:
					rest.add(p['probe_id'])
					rest_list.append(p)
		i += 1
	with open('top-20-resolvers.json', 'w') as f:
		json.dump(top20_list, f)
	with open('remaining-resolvers.json', 'w') as f:
		json.dump(rest_list, f)


		
