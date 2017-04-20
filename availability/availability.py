#!/usr/bin/env python3

import os
import json
import time
import shutil
import pprint
import collections

import requests


def fetch_measurement_by_id(measurement_id):
    params = {
            'format': 'txt',
            'start': int(time.time()) - 3600 * 6,
    }
    url = "https://atlas.ripe.net/api/v2/measurements/{m}/results/".format(
        m=measurement_id)
    req = requests.get(url, params=params)
    # TODO check HTTP code
    return req.text


def get_measurement_by_id(measurement_id, caching=True):
    measurement_file = 'measurement-{m}.json'.format(m=measurement_id)
    use_cached_measurement = False
    if use_cached_measurement:
        try:
            with open(measurement_file) as fd:
                measurement = fd.read()
                print('Using cached measurement file {f}'.format(f=measurement_file))
        except (OSError, IOError):
            measurement = fetch_measurement_by_id(measurement_id)
    else:
        measurement = fetch_measurement_by_id(measurement_id)
    with open(measurement_file, 'w') as fd:
        fd.write(measurement)
    print('Saved to {f}'.format(f=measurement_file))
    return measurement


def main():
    measurement_id = 30001

    now = time.time()
    proberesults = collections.defaultdict(list)
    measurement = get_measurement_by_id(measurement_id, caching=False)
    for m in measurement.splitlines():
        jm = json.loads(m)
        if jm['type'] != 'dns':
            continue
        prb_id = jm['prb_id']
#        if prb_id == 1:
#            import pdb; pdb.set_trace()
        ts = jm['timestamp']
        for result in jm['resultset']:
            error = 'error' in result
            if error and 'nameserver' in result['error'] and \
                    result['error']['nameserver'] == 'no local resolvers found':
                # ignore misconfigured probes
                continue
            try:
                dst = result['dst_name']
            except KeyError:
                try:
                    dst = result['dst_addr']
                except KeyError:
                    dst = ''
            proberesults[prb_id].append({
                'dst': dst,
                'timestamp': ts,
                'error': error,
            })
#        if prb_id == 1:
#            import pdb; pdb.set_trace()

    availability = collections.defaultdict(dict)
    for prb_id, result in proberesults.items():
        last_hour_errors = collections.defaultdict(list)
        last_six_hours_errors = collections.defaultdict(list)
#        if prb_id == 32246:
#            import pdb; pdb.set_trace()
        for sample in result:
            # last hour
            if now - 3600 < sample['timestamp'] < now:
                last_hour_errors[sample['dst']].append(sample['error'])
            # last six hours
            if now - 3600 * 6 < sample['timestamp'] < now:
                last_six_hours_errors[sample['dst']].append(sample['error'])

        # last hour
        last_hour_availability = {}
        availability[prb_id] = collections.defaultdict(dict)
        for dst, data in last_hour_errors.items():
            if len(data) > 0:
                last_hour_availability[dst] = (
                    float(data.count(False)) / len(data)
                )
            else:
                last_hour_availability = 1.0
            availability[prb_id][dst]['1h'] = {
                'availability': last_hour_availability,
                'failing_samples': data.count(True),
                'total_samples': len(data),
            }
        else:
            availability[prb_id][dst]['1h'] = {
                'availability': 0.0,
                'failing_samples': 0,
                'total_samples': 0,
            }

        # last six hours
        last_six_hours_availability = {}
        for dst, data in last_six_hours_errors.items():
            if len(data) > 0:
                last_six_hours_availability[dst] = (
                    float(data.count(False)) / len(data)
                )
            else:
                last_sid_hours_availability = 1.0
            availability[prb_id][dst]['6h'] = {
                'availability': last_six_hours_availability,
                'failing_samples': data.count(True),
                'total_samples': len(data),
            }
        else:
            availability[prb_id][dst]['6h'] = {
                'availability': 0.0,
                'failing_samples': 0,
                'total_samples': 0,
            }

    pprint.pprint(availability)

    shutil.rmtree('availability/')
    os.mkdir('availability')
    for probe_id, data in availability.items():
        with open('availability/probe{n}.json'.format(n=probe_id), 'w') as fd:
            json.dump(data, fd)
    print('Saved to availability/probe*.json')


if __name__ == '__main__':
    main()
