package main

import (
	"os"
	"runtime/pprof"
	"sync"
	"time"
)

func main() {
	var mu sync.Mutex
	never := make(chan int)
	mu.Lock()
	for range 2 {
		go func() { <-never }() // stuck on a receive
	}
	go func() { mu.Lock() }() // waiting for a mutex
	go time.Sleep(time.Hour)  // sleeping
	time.Sleep(20 * time.Millisecond)

	// The same dump you get from SIGQUIT (Ctrl+\) or /debug/pprof/goroutine?debug=2
	pprof.Lookup("goroutine").WriteTo(os.Stdout, 2)
}
