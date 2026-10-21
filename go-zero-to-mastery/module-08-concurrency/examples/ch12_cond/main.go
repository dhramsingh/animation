package main

import (
	"fmt"
	"sync"
	"time"
)

func main() {
	var mu sync.Mutex
	cond := sync.NewCond(&mu)
	ready := false

	var wg sync.WaitGroup
	for id := 1; id <= 3; id++ {
		wg.Go(func() {
			mu.Lock()
			for !ready { // ALWAYS wait in a loop
				cond.Wait() // atomically unlocks mu and sleeps
			}
			mu.Unlock()
			fmt.Println("runner", id, "starts")
		})
	}

	time.Sleep(50 * time.Millisecond)
	mu.Lock()
	ready = true
	mu.Unlock()
	fmt.Println("GO! (Broadcast)")
	cond.Broadcast() // wake every waiter
	wg.Wait()
}
