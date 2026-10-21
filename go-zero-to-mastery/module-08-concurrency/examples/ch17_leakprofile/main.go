package main

import (
	"fmt"
	"os"
	"runtime/pprof"
	"time"
)

func search() {
	ch := make(chan string) // unbuffered: the late send blocks forever
	go func() {
		time.Sleep(20 * time.Millisecond)
		ch <- "late result"
	}()
	select {
	case <-ch:
	case <-time.After(5 * time.Millisecond):
	}
}

func main() {
	for range 3 {
		search()
	}
	time.Sleep(50 * time.Millisecond)
	// Go 1.27: the GC finds goroutines blocked on channels that no
	// other goroutine can reach, and reports them as leaked.
	p := pprof.Lookup("goroutineleak")
	p.WriteTo(os.Stdout, 1)
	fmt.Println("leaked goroutines:", p.Count())
}
