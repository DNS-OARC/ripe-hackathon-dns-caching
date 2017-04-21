import json
import pprint


probe_dict = dict()

#URL to fetch a daily dump of probes
#http://ftp.ripe.net/ripe/atlas/probes/archive


with open('20170420.json', 'r') as data:
    probes = json.load(data)

    for i in probes["objects"]:
    	probe_dict[i["id"]] = i



with open('prbid_to_info.json', 'w') as data_file:
	json.dump(probe_dict,data_file)

