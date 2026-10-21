package main

import (
	"fmt"
	"sync"
	"sync/atomic"
	"time"
)

func main() {
	sem := make(chan struct{}, 3) // at most 3 at a time
	var running, peak atomic.Int32
	var wg sync.WaitGroup

	for range 10 {
		wg.Go(func() {
			sem <- struct{}{}        // acquire a slot (blocks when full)
			defer func() { <-sem }() // release it

			n := running.Add(1)
			for {
				p := peak.Load()
				if n <= p || peak.CompareAndSwap(p, n) {
					break
				}
			}
			time.Sleep(20 * time.Millisecond) // the limited work
			running.Add(-1)
		})
	}
	wg.Wait()
	fmt.Println("tasks: 10, peak concurrency:", peak.Load())
}
