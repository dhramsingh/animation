package main

import (
	"fmt"
	"net"
	"os"
	"runtime"
	"strings"
	"time"
)

func threads() string {
	b, _ := os.ReadFile("/proc/self/status")
	for _, l := range strings.Split(string(b), "\n") {
		if strings.HasPrefix(l, "Threads:") {
			return strings.TrimSpace(l[8:])
		}
	}
	return "?"
}

func main() {
	ln, err := net.Listen("tcp", "127.0.0.1:0")
	if err != nil {
		panic(err)
	}
	go func() { // server: one goroutine per connection
		for {
			c, err := ln.Accept()
			if err != nil {
				return
			}
			go func() {
				buf := make([]byte, 1)
				c.Read(buf) // blocks in the netpoller, not on a thread
			}()
		}
	}()
	var conns []net.Conn
	for range 2000 { // 2000 idle clients
		c, err := net.Dial("tcp", ln.Addr().String())
		if err != nil {
			panic(err)
		}
		conns = append(conns, c)
	}
	time.Sleep(200 * time.Millisecond)
	fmt.Println("open connections:", len(conns))
	fmt.Println("goroutines:      ", runtime.NumGoroutine())
	fmt.Println("OS threads:      ", threads())
}
