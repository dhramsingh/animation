package main

import (
	"fmt"
	"time"
)

func main() {
	requests := []int{1, 2, 3, 4, 5}
	limiter := time.NewTicker(100 * time.Millisecond) // 10 req/s
	defer limiter.Stop()

	// a bucket that allows a burst of 2 before the steady rate applies
	burst := make(chan struct{}, 2)
	burst <- struct{}{}
	burst <- struct{}{}
	go func() {
		for range limiter.C {
			select {
			case burst <- struct{}{}: // refill one token
			default: // bucket full: drop the token
			}
		}
	}()

	start := time.Now()
	for _, r := range requests {
		<-burst // wait for a token
		ms := time.Since(start).Round(10 * time.Millisecond).Milliseconds()
		fmt.Printf("request %d at +%3dms\n", r, ms)
	}
}
