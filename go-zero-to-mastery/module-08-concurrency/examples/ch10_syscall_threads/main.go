package main

import (
	"fmt"
	"os"
	"strings"
	"sync"
	"syscall"
	"time"
)

func threads() string { // Linux: read our own thread count
	b, _ := os.ReadFile("/proc/self/status")
	for _, l := range strings.Split(string(b), "\n") {
		if strings.HasPrefix(l, "Threads:") {
			return strings.TrimSpace(l[8:])
		}
	}
	return "?"
}

func run(name string, block func()) {
	var wg sync.WaitGroup
	for range 50 {
		wg.Go(block)
	}
	time.Sleep(100 * time.Millisecond) // let them all block
	fmt.Printf("%-28s OS threads = %s\n", name, threads())
	wg.Wait()
}

func main() {
	fmt.Printf("%-28s OS threads = %s\n", "at start", threads())
	run("50 x time.Sleep (parked)", func() { time.Sleep(300 * time.Millisecond) })
	ts := syscall.Timespec{Nsec: 300_000_000}
	run("50 x blocking syscall", func() { syscall.Nanosleep(&ts, nil) })
}
