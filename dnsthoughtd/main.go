package main

import (
    "flag"
    "github.com/miekg/dns"
    "net"
    "os"
    "os/signal"
    "strings"
    "syscall"
    //"time"
    "log"
    "strconv"
)

var debug bool

func init() {
    flag.BoolVar(&debug, "debug", false, "Enable debug output")
}

func main() {
    flag.Parse()

    dns.HandleFunc(".", func(w dns.ResponseWriter, r *dns.Msg) {
        if debug {
            log.Printf("%v", r.String())
        }

        var (
            v4  bool
            rr  dns.RR
            str string
            a   net.IP
        )

        m := new(dns.Msg)
        m.SetReply(r)
        m.Authoritative = true
        m.RecursionAvailable = false
        m.Compress = true

        if ip, ok := w.RemoteAddr().(*net.UDPAddr); ok {
    		str = "Port: " + strconv.Itoa(ip.Port) + " (udp)"
    		a = ip.IP
    		v4 = a.To4() != nil
    	}
    	if ip, ok := w.RemoteAddr().(*net.TCPAddr); ok {
    		str = "Port: " + strconv.Itoa(ip.Port) + " (tcp)"
    		a = ip.IP
    		v4 = a.To4() != nil
    	}

        if dom := m.Question[0].Name; dom != "" {
            if w.LocalAddr().Network() == "udp" {
                tc := false
                l := strings.Split(dom, ".")
                for _, i := range l {
                    if i == "tc" {
                        tc = true
                    }
                }
                if tc {
                    m.Truncated = true
                    if debug {
                        log.Printf("%v", m.String())
                    }
                    w.WriteMsg(m)
                    return
                }
            }

        	if v4 {
        		rr = &dns.A{
        			Hdr: dns.RR_Header{Name: dom, Rrtype: dns.TypeA, Class: dns.ClassINET, Ttl: 0},
        			A:   a.To4(),
        		}
        	} else {
        		rr = &dns.AAAA{
        			Hdr:  dns.RR_Header{Name: dom, Rrtype: dns.TypeAAAA, Class: dns.ClassINET, Ttl: 0},
        			AAAA: a,
        		}
        	}

        	t := &dns.TXT{
        		Hdr: dns.RR_Header{Name: dom, Rrtype: dns.TypeTXT, Class: dns.ClassINET, Ttl: 0},
        		Txt: []string{str},
        	}

            switch r.Question[0].Qtype {
        	case dns.TypeTXT:
        		m.Answer = append(m.Answer, t)
        		m.Extra = append(m.Extra, rr)
        	default:
        		fallthrough
        	case dns.TypeAAAA, dns.TypeA:
        		m.Answer = append(m.Answer, rr)
        		m.Extra = append(m.Extra, t)
        	}
        }

        if debug {
            log.Printf("%v", m.String())
        }
        w.WriteMsg(m)
    })

    var servers []*dns.Server
    for _, addr := range flag.Args() {
        servers = append(servers,
            &dns.Server{Addr: addr, Net: "tcp"},
            &dns.Server{Addr: addr, Net: "udp"},
        )
    }

    c := make(chan error)
    for _, i := range servers {
        d := i
        go func() {
            d.NotifyStartedFunc = func() {
                c <- nil
            }
            c <- d.ListenAndServe()
        }()

        if err := <-c; err != nil {
            log.Fatalf("ListenAndServe(%s://%s): %s", d.Net, d.Addr, err.Error())
        }

        var addr, net string
        if d.Listener != nil {
            addr = d.Listener.Addr().String()
            net = "tcp"
        } else if d.PacketConn != nil {
            addr = d.PacketConn.LocalAddr().String()
            net = "udp"
        } else {
            log.Fatalf("Invalid connection type")
        }

        if debug {
            log.Printf("Listening on %s://%s", net, addr)
        }
    }

    sig := make(chan os.Signal)
    signal.Notify(sig, syscall.SIGINT, syscall.SIGTERM)
    s := <-sig
    log.Fatalf("Signal (%v) received, stopping", s)
}
