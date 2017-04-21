# What is this?

A small library and command line tool to extract information about the last N
hours of availability of the local DNS resolvers. The library uses the RIPE
Atlas probes data to get this information. The data is saved to JSON.

## How does it work?

The library fetches the data from all the Atlas probes for the last N hours (6
by default) and extract the local DNS resolvers' information from it. Then it
divides all the data into 1-hour buckets, and for each bucket and for each
internal resolver, it computes the DNS availability.
The availability is a number between 0 and 1 obtained by dividing the number of
successful queries by the total number of queries.

This data can be used to show the availability of DNS by probe, by resolver, and
by ASN (other aggregations are possible too).


## Quick usage example

```
./availability.py

[lots of output]

Saved to availability_data
```

This will create a directory called `availability_data` containing files like
`probe<probeID>.json`. Each of these files contains the availability data of the
named probe.

For example:

```
$ cat availability_data/probe32016.json | jq .
{
  "2a01:e00::2": {
    "1h": {
      "total_samples": 7,
      "availability": 1,
      "failing_samples": 0
    },
    "6h": {
      "total_samples": 42,
      "availability": 1,
      "failing_samples": 0
    }
  },
  "192.168.0.254": {
    "1h": {
      "total_samples": 7,
      "availability": 1,
      "failing_samples": 0
    },
    "6h": {
      "total_samples": 42,
      "availability": 0.9761904761904762,
      "failing_samples": 1
    }
  },
  "2a01:e00::1": {
    "1h": {
      "total_samples": 0,
      "availability": 0,
      "failing_samples": 0
    },
    "6h": {
      "total_samples": 0,
      "availability": 0,
      "failing_samples": 0
    }
  }
}
```

