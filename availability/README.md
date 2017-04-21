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
./availability.py 12
Fetching 12 hours of data
Saved to measurement-30001.json
Analyzing local resolvers availability
Saved to availability_data/probe*.json
```

This will create a directory called `availability_data` containing files like
`probe<probeID>.json`. Each of these files contains the availability data of the
named probe, divided by one-hour buckets and by resolver address.

For example:

```
$ cat availability_data/probe32016.json | jq .
[
  {
    "192.168.0.254": {
      "failing_samples": 2,
      "start": 1492781785,
      "availability": 0.9764705882352941,
      "total_samples": 85,
      "end": 1492785384
    },
    "2a01:e00::2": {
      "failing_samples": 0,
      "start": 1492781785,
      "availability": 1,
      "total_samples": 85,
      "end": 1492785384
    },
    "2a01:e00::1": {
      "failing_samples": 0,
      "start": 1492781785,
      "availability": 1,
      "total_samples": 85,
      "end": 1492785384
    }
  },
  {
    "192.168.0.254": {
      "failing_samples": 2,
      "start": 1492778185,
      "availability": 0.9764705882352941,
      "total_samples": 85,
      "end": 1492781784
    },
    "2a01:e00::2": {
      "failing_samples": 0,
      "start": 1492778185,
      "availability": 1,
      "total_samples": 85,
      "end": 1492781784
    },
    "2a01:e00::1": {
      "failing_samples": 0,
      "start": 1492778185,
      "availability": 1,
      "total_samples": 85,
      "end": 1492781784
    }
  },
  {
    "192.168.0.254": {
      "failing_samples": 2,
      "start": 1492774585,
      "availability": 0.9764705882352941,
      "total_samples": 85,
      "end": 1492778184
    },
    "2a01:e00::2": {
      "failing_samples": 0,
      "start": 1492774585,
      "availability": 1,
      "total_samples": 85,
      "end": 1492778184
    },
    "2a01:e00::1": {
      "failing_samples": 0,
      "start": 1492774585,
      "availability": 1,
      "total_samples": 85,
      "end": 1492778184
    }
  },
  {
    "192.168.0.254": {
      "failing_samples": 2,
      "start": 1492770985,
      "availability": 0.9764705882352941,
      "total_samples": 85,
      "end": 1492774584
    },
    "2a01:e00::2": {
      "failing_samples": 0,
      "start": 1492770985,
      "availability": 1,
      "total_samples": 85,
      "end": 1492774584
    },
    "2a01:e00::1": {
      "failing_samples": 0,
      "start": 1492770985,
      "availability": 1,
      "total_samples": 85,
      "end": 1492774584
    }
  },
  {
    "192.168.0.254": {
      "failing_samples": 2,
      "start": 1492767385,
      "availability": 0.9764705882352941,
      "total_samples": 85,
      "end": 1492770984
    },
    "2a01:e00::2": {
      "failing_samples": 0,
      "start": 1492767385,
      "availability": 1,
      "total_samples": 85,
      "end": 1492770984
    },
    "2a01:e00::1": {
      "failing_samples": 0,
      "start": 1492767385,
      "availability": 1,
      "total_samples": 85,
      "end": 1492770984
    }
  },
  {
    "192.168.0.254": {
      "failing_samples": 2,
      "start": 1492763785,
      "availability": 0.9764705882352941,
      "total_samples": 85,
      "end": 1492767384
    },
    "2a01:e00::2": {
      "failing_samples": 0,
      "start": 1492763785,
      "availability": 1,
      "total_samples": 85,
      "end": 1492767384
    },
    "2a01:e00::1": {
      "failing_samples": 0,
      "start": 1492763785,
      "availability": 1,
      "total_samples": 85,
      "end": 1492767384
    }
  },
  {
    "192.168.0.254": {
      "failing_samples": 2,
      "start": 1492760185,
      "availability": 0.9764705882352941,
      "total_samples": 85,
      "end": 1492763784
    },
    "2a01:e00::2": {
      "failing_samples": 0,
      "start": 1492760185,
      "availability": 1,
      "total_samples": 85,
      "end": 1492763784
    },
    "2a01:e00::1": {
      "failing_samples": 0,
      "start": 1492760185,
      "availability": 1,
      "total_samples": 85,
      "end": 1492763784
    }
  },
  {
    "192.168.0.254": {
      "failing_samples": 2,
      "start": 1492756585,
      "availability": 0.9764705882352941,
      "total_samples": 85,
      "end": 1492760184
    },
    "2a01:e00::2": {
      "failing_samples": 0,
      "start": 1492756585,
      "availability": 1,
      "total_samples": 85,
      "end": 1492760184
    },
    "2a01:e00::1": {
      "failing_samples": 0,
      "start": 1492756585,
      "availability": 1,
      "total_samples": 85,
      "end": 1492760184
    }
  },
  {
    "192.168.0.254": {
      "failing_samples": 2,
      "start": 1492752985,
      "availability": 0.9764705882352941,
      "total_samples": 85,
      "end": 1492756584
    },
    "2a01:e00::2": {
      "failing_samples": 0,
      "start": 1492752985,
      "availability": 1,
      "total_samples": 85,
      "end": 1492756584
    },
    "2a01:e00::1": {
      "failing_samples": 0,
      "start": 1492752985,
      "availability": 1,
      "total_samples": 85,
      "end": 1492756584
    }
  },
  {
    "192.168.0.254": {
      "failing_samples": 2,
      "start": 1492749385,
      "availability": 0.9764705882352941,
      "total_samples": 85,
      "end": 1492752984
    },
    "2a01:e00::2": {
      "failing_samples": 0,
      "start": 1492749385,
      "availability": 1,
      "total_samples": 85,
      "end": 1492752984
    },
    "2a01:e00::1": {
      "failing_samples": 0,
      "start": 1492749385,
      "availability": 1,
      "total_samples": 85,
      "end": 1492752984
    }
  },
  {
    "192.168.0.254": {
      "failing_samples": 2,
      "start": 1492745785,
      "availability": 0.9764705882352941,
      "total_samples": 85,
      "end": 1492749384
    },
    "2a01:e00::2": {
      "failing_samples": 0,
      "start": 1492745785,
      "availability": 1,
      "total_samples": 85,
      "end": 1492749384
    },
    "2a01:e00::1": {
      "failing_samples": 0,
      "start": 1492745785,
      "availability": 1,
      "total_samples": 85,
      "end": 1492749384
    }
  },
  {
    "192.168.0.254": {
      "failing_samples": 2,
      "start": 1492742185,
      "availability": 0.9764705882352941,
      "total_samples": 85,
      "end": 1492745784
    },
    "2a01:e00::2": {
      "failing_samples": 0,
      "start": 1492742185,
      "availability": 1,
      "total_samples": 85,
      "end": 1492745784
    },
    "2a01:e00::1": {
      "failing_samples": 0,
      "start": 1492742185,
      "availability": 1,
      "total_samples": 85,
      "end": 1492745784
    }
  }
]
```

