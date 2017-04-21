package main

import (
	"log"
	"net/http"
    "time"
    "fmt"
    "io/ioutil"
    "encoding/json"
    "encoding/base64"
    "github.com/miekg/dns"
    "flag"
)

type Error struct {
    Timeout int `json:"timeout"` // query timeout (int)
    Getaddrinfo string `json:"getaddrinfo"` // error message (string)
}

type ErrorContainer struct {
    Error *Error
}

func (e *ErrorContainer) UnmarshalJSON(b []byte) error {
    e.Error = &Error{}
    if err := json.Unmarshal(b, &e.Error); err != nil {
        return err
    }
    return nil
}

func (e *ErrorContainer) Contained() *Error {
    if e.Error == nil {
        e.Error = &Error{}
    }
    return e.Error
}

type Answer struct {
    Mname string `json:"MNAME"` // domain name, RFC 1035, 3.1.13 (string)
    Name string `json:"NAME"` // domain name. (string)
    Rdata []string `json:"RDATA"` // [type TXT] txt value (from 4710, list of strings, before it was a single string)
    Rname string `json:"RNAME"` // [if type SOA] mailbox, RFC 1035 3.3.13 (string)
    Serial string `json:"SERIAL"` // [type SOA] zone serial number, RFC 1035 3.3.13 (string)
    Ttl int `json:"TTL"` // [type SOA] time to live, RFC 1035 4.1.3 (int)
    Type string `json:"TYPE"` // RR "SOA" or "TXT" (string), RFC 1035
}

type AnswerContainer struct {
    Answer *Answer
}

func (a *AnswerContainer) UnmarshalJSON(b []byte) error {
    a.Answer = &Answer{}
    if err := json.Unmarshal(b, &a.Answer); err != nil {
        return err
    }
    return nil
}

func (a *AnswerContainer) Contained() *Answer {
    if a.Answer == nil {
        a.Answer = &Answer{}
    }
    return a.Answer
}

type Result struct {
    Ancount int `json:"ANCOUNT"` // answer count, RFC 1035 4.1.1 (int)
    Arcount int `json:"ARCOUNT"` // additional record count, RFC 1035, 4.1.1 (int)
    Id int `json:"ID"` // query ID, RFC 1035 4.1.1 (int)
    Nscount int `json:"NSCOUNT"` // name server count (int)
    Qdcount int `json:"QDCOUNT"` // number of queries (int)
    Abuf string `json:"abuf"` // answer payload buffer from the server, UU encoded (string)
    Answers []AnswerContainer `json:"answers"` // first two records from the response decoded by the probe, if they are TXT or SOA; other RR can be decoded from "abuf" (array)
    Rt float64 `json:"rt"` // [optional] response time in milli seconds (float)
    Size int `json:"size"` // [optional] response size (int)
    SrcAddr string `json:"src_addr"` // [optional] the source IP address added by the probe (string).
    Subid int `json:"subid"` // [optional] sequence number of this result within a group of results, available if the resolution is done by the probe's local resolver
    Submax int `json:"submax"` // [optional] total number of results within a group (int)
}

func (r *Result) UnpackAbuf() (*dns.Msg, error) {
    m := &dns.Msg{}
    b, err := base64.StdEncoding.DecodeString(r.Abuf)
    if err != nil {
        return nil, err
    }
    if err := m.Unpack(b); err != nil {
        return nil, err
    }
    return m, nil
}

type ResultContainer struct {
    Result *Result
}

func (r *ResultContainer) UnmarshalJSON(b []byte) error {
    r.Result = &Result{}
    if err := json.Unmarshal(b, &r.Result); err != nil {
        return err
    }
    return nil
}

func (r *ResultContainer) Contained() *Result {
    if r.Result == nil {
        r.Result = &Result{}
    }
    return r.Result
}

type Resultset struct {
    Af int `json:"af"` // [optional] IP version: "4" or "6" (int)
    DstAddr string `json:"dst_addr"` // [optional] IP address of the destination (string)
    DstName string `json:"dst_name"` // [optional] hostname of the destination (string)
    Error ErrorContainer `json:"error"` // [optional] error message (associative array)
    Lts int `json:"lts"` // last time synchronised. How long ago (in seconds) the clock of the probe was found to be in sync with that of a controller. The value -1 is used to indicate that the probe does not know whether it is in sync (from 4650) (int)
    Proto string `json:"proto"` // "TCP" or "UDP" (string)
    Qbuf string `json:"qbuf"` // [optional] query payload buffer which was sent to the server, UU encoded (string)
    Result ResultContainer `json:"result"` // [optional] response from the DNS server (associative array)
    Retry int `json:"retry"` // [optional] retry count (int)
    Timestamp int `json:"timestamp"` // start time, in Unix timestamp (int)
}

type ResultsetContainer struct {
    Resultset *Resultset
}

func (r *ResultsetContainer) UnmarshalJSON(b []byte) error {
    r.Resultset = &Resultset{}
    if err := json.Unmarshal(b, &r.Resultset); err != nil {
        return err
    }
    return nil
}

func (r *ResultsetContainer) Contained() *Resultset {
    if r.Resultset == nil {
        r.Resultset = &Resultset{}
    }
    return r.Resultset
}

type Measurement struct {
    Fw int `json:"fw"`
    Af int `json:"af"` // [optional] IP version: "4" or "6" (int)
    DstAddr string `json:"dst_addr"` // [optional] IP address of the destination (string)
    DstName string `json:"dst_name"` // [optional] hostname of the destination (string)
    Error ErrorContainer `json:"error"` // [optional] error message (associative array)
    From string `json:"from"` // [optional] IP address of the source (string)
    Lts int `json:"lts"` // last time synchronised. How long ago (in seconds) the clock of the probe was found to be in sync with that of a controller. The value -1 is used to indicate that the probe does not know whether it is in sync (from 4650) (int)
    MsmId int `json:"msm_id"` // measurement identifier (int)
    PrbId int `json:"prb_id"` // source probe ID (int)
    Proto string `json:"proto"` // "TCP" or "UDP" (string)
    Qbuf string `json:"qbuf"` // [optional] query payload buffer which was sent to the server, UU encoded (string)
    Result ResultContainer `json:"result"` // [optional] response from the DNS server (associative array)
    Resultset []ResultsetContainer `json:"resultset"` // [optional] an array of objects containing all the fields of a DNS result object, except for the fields: fw, from, msm_id, prb_id, and type. Available for queries sent to each local resolver.
    Retry int `json:"retry"` // [optional] retry count (int)
    Timestamp int `json:"timestamp"` // start time, in Unix timestamp (int)
    Type string `json:"type"` // "dns" (string)
}

var start int
var stop int
var last int

func init() {
    flag.IntVar(&start, "start", 0, "start unixtime for results")
    flag.IntVar(&stop, "stop", 0, "stop unixtime for results")
    flag.IntVar(&last, "last", 3600, "last N seconds of results (default 1 hour), not used if start/stop are used")
}

func main() {
    flag.Parse()

    var startTime, stopTime time.Time

    if last > 0 {
        stopTime = time.Now()
        startTime = stopTime.Add(time.Duration(-last)*time.Second)
    } else {
        startTime = time.Unix(int64(start), 0)
        stopTime = time.Unix(int64(stop), 0)
    }

    for _, id := range flag.Args() {
        url := fmt.Sprintf("%s/%s/results?start=%v&stop=%v&format=json", "https://atlas.ripe.net/api/v2/measurements", id, startTime.Unix(), stopTime.Unix())
        log.Printf("Get %s", url)
        resp, err := http.Get(url)
        if err != nil {
            log.Fatalf("http.Get(): %s", err.Error())
        }

        body, err := ioutil.ReadAll(resp.Body)
        resp.Body.Close()
        if err != nil {
            log.Fatalf("ioutil.ReadAll(): %s", err.Error())
        }

        var s []Measurement
        if err := json.Unmarshal(body, &s); err != nil {
            log.Fatalf("json.Unmarshal(): %s", err.Error())
        }

        for _, m := range s {
            log.Printf("%d", len(m.Resultset))
            for _, r := range m.Resultset {
                r := r.Contained().Result.Contained()
                m, _ := r.UnpackAbuf()
                log.Printf("%v", m)
            }
        }
    }
}
