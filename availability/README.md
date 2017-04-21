## Quick usage

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

