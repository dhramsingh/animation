package main

import (
	"fmt"
	"time"
)

// transfer sends n ints from one goroutine to another through a
// channel with the given capacity and returns the time per value.
func transfer(capacity, n int) time.Duration {
	ch := make(chan int, capacity)
	done := make(chan struct{})
	go func() {
		for range ch {
		}
		close(done)
	}()
	start := time.Now()
	for i := range n {
		ch <- i
	}
	close(ch)
	<-done
	return time.Since(start) / time.Duration(n)
}

func main() {
	const n = 2_000_000
	for _, c := range []int{0, 1, 8, 64, 512} {
		best := time.Hour
		for range 3 { // best of 3: the machine is shared
			best = min(best, transfer(c, n))
		}
		fmt.Printf("cap %-4d %5.0f ns per value\n", c, float64(best.Nanoseconds()))
	}
}
