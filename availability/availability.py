#!/usr/bin/env python3

import os
import json
import time
import shutil
import pprint
import collections

import requests


def fetch_measurement_by_id(measurement_id, start, end):
    '''
    Fetch the last six hours of the given measurement
    '''
    if start >= end:
        raise ValueError('Start time must be smaller than end time')
    params = {
        'format': 'txt',
        'start': start,
        'end': end,
    }
    url = "https://atlas.ripe.net/api/v2/measurements/{m}/results/".format(
        m=measurement_id)
    req = requests.get(url, params=params)
    if req.status_code != 200:
        raise Exception('Status code is not 200. Output: {o}'.format(o=req.text))
    return req.text


def get_measurement_by_id(measurement_id, start, end, use_cache=True):
    measurement_file = 'measurement-{m}.json'.format(m=measurement_id)
    do_fetch = False
    if use_cache:
        # FIXME caching does not consider start and end time, better to remove?
        try:
            with open(measurement_file) as fd:
                measurement = fd.read()
                print('Using cached measurement file {f}'.format(f=measurement_file))
        except (OSError, IOError):
            do_fetch = True
    else:
        do_fetch = True

    if do_fetch:
        measurement = fetch_measurement_by_id(measurement_id, start, end)

    with open(measurement_file, 'w') as fd:
        fd.write(measurement)
    print('Saved to {f}'.format(f=measurement_file))
    return measurement


def get_availability_buckets(last_n=6):
    '''
    Return the `last_n` availability metrics divided in 1-hour buckets.
    E.g. return a list with 3 objects representing the local nameserver
    availability for the last three hours, one hour each.
    '''
    pass


def get_local_dns_results(measurement_id, start=None, end=None):
    if end is None:
        end = int(time.time())
    if start is None:
        start = end - 3600 * 6  # 6 hours of data
    measurement = get_measurement_by_id(
            measurement_id,
            start=start,
            end=end,
            use_cache=False)
    results = collections.defaultdict(list)
    for m in measurement.splitlines():
        jm = json.loads(m)
        if jm['type'] != 'dns':
            continue
        prb_id = jm['prb_id']
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
            results[prb_id].append({
                'dst': dst,
                'timestamp': ts,
                'error': error,
            })
    return results, start, end


def main():
    measurement_id = 30001  # random domains

    local_dns_results, start, end = get_local_dns_results(measurement_id)
    availability = collections.defaultdict(dict)
    for prb_id, result in local_dns_results.items():
        last_hour_errors = collections.defaultdict(list)
        last_six_hours_errors = collections.defaultdict(list)
        for sample in result:
            # last hour
            if end - 3600 < sample['timestamp'] < end:
                last_hour_errors[sample['dst']].append(sample['error'])
            # last six hours
            if end - 3600 * 6 < sample['timestamp'] < end:
                last_six_hours_errors[sample['dst']].append(sample['error'])

        # last hour
        last_hour_availability = {}
        availability[prb_id] = collections.defaultdict(dict)
        for dst, data in last_hour_errors.items():
            if len(data) > 0:
                last_hour_availability = (
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
                last_six_hours_availability = (
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

    availability_data_dir = 'availability_data'
    try:
        shutil.rmtree(availability_data_dir)
    except FileNotFoundError:
        pass
    os.mkdir(availability_data_dir)
    for probe_id, data in availability.items():
        outfile = os.path.join(
            availability_data_dir,
            'probe{n}.json'.format(n=probe_id))
        with open(outfile, 'w') as fd:
            json.dump(data, fd)
    print('Saved to {d}'.format(d=availability_data_dir))


if __name__ == '__main__':
    main()
