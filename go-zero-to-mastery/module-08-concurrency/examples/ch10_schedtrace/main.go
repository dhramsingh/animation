package main

import (
	"sync"
	"time"
)

func spin(d time.Duration) {
	for end := time.Now().Add(d); time.Now().Before(end); {
	}
}

func main() {
	time.Sleep(50 * time.Millisecond) // idle at first
	var wg sync.WaitGroup
	for range 12 { // 12 CPU-bound goroutines on 4 Ps
		wg.Go(func() { spin(250 * time.Millisecond) })
	}
	wg.Wait()
	time.Sleep(120 * time.Millisecond) // idle again
}
