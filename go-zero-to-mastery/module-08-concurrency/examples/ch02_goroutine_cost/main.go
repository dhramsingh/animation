package main

import (
	"fmt"
	"runtime"
	"sync"
	"time"
)

func main() {
	const n = 100_000
	var before, after runtime.MemStats
	runtime.GC()
	runtime.ReadMemStats(&before)

	block := make(chan struct{})
	var started sync.WaitGroup
	t0 := time.Now()
	for range n {
		started.Add(1)
		go func() {
			started.Done()
			<-block // park until released
		}()
	}
	started.Wait()
	spawn := time.Since(t0)

	runtime.ReadMemStats(&after)
	fmt.Println("goroutines alive:", runtime.NumGoroutine())
	fmt.Printf("spawn time: %v total, %v per goroutine\n",
		spawn.Round(time.Millisecond), spawn/n)
	stack := after.StackInuse - before.StackInuse
	total := after.Sys - before.Sys
	fmt.Printf("stack memory: %.1f MB (%d bytes per goroutine)\n",
		float64(stack)/1e6, stack/n)
	fmt.Printf("all runtime memory: %.1f MB (%d bytes per goroutine)\n",
		float64(total)/1e6, total/n)
	close(block)
}
