package main

import (
	"fmt"
	"runtime"
	"sync"
	"time"
)

func main() {
	runtime.GOMAXPROCS(1) // one P: every hand-off is a goroutine switch

	// 1. create + finish a goroutine
	const n = 200_000
	var wg sync.WaitGroup
	t0 := time.Now()
	for range n {
		wg.Go(func() {})
	}
	wg.Wait()
	fmt.Printf("goroutine create+exit: %.0f ns\n", float64(time.Since(t0).Nanoseconds())/n)

	// 2. ping-pong over unbuffered channels = 2 switches per round
	const rounds = 500_000
	ping, pong := make(chan int), make(chan int)
	go func() {
		for v := range ping {
			pong <- v
		}
	}()
	t0 = time.Now()
	for i := range rounds {
		ping <- i
		<-pong
	}
	close(ping)
	fmt.Printf("goroutine switch (channel ping-pong): %.0f ns per switch\n",
		float64(time.Since(t0).Nanoseconds())/(2*rounds))
}
