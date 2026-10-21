package main

import (
	"fmt"
	"sync"
	"sync/atomic"
	"time"
)

func main() {
	var wg sync.WaitGroup
	var finished atomic.Int32
	for range 5 {
		go func() {
			wg.Add(1) // BUG: may run after Wait
			defer wg.Done()
			time.Sleep(10 * time.Millisecond)
			finished.Add(1)
		}()
	}
	wg.Wait() // the counter may still be 0 here
	fmt.Println("finished before Wait returned:", finished.Load(), "of 5")
}
