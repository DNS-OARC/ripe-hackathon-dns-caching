SOURCES := $(wildcard *.go)

all: dnsthoughtd

fmt: format

clean:
	rm -f dnsthoughtd

format:
	gofmt -w *.go
	sed -i -e 's%	%    %g' *.go

dnsthoughtd: $(SOURCES)
	go build

freebsd: $(SOURCE) clean
	GOOS=freebsd GOARCH=amd64 go build
