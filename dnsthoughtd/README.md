# dnsthoughtd

Minimalistic DNS server to answer A/AAAA/TXT queries with the source address,
protocol and port the query came over. Add `tc` anywhere in the QNAME and it
will force fall over to TCP.

## Build

`make` if your on the target system, `make freebsd` if you want to build it
for FreeBSD but are on some other system.

## Usage

```
./dnsthoughtd [-debug] <list of IP addresses to listen on>
```
