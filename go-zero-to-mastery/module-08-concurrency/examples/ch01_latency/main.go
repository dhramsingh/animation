package main

import (
	"fmt"
	"sync"
	"time"
)

// fetch pretends to call a slow service: it only waits.
func fetch(id int) string {
	time.Sleep(100 * time.Millisecond)
	return fmt.Sprintf("page-%d", id)
}

func main() {
	start := time.Now()
	for i := range 5 {
		fetch(i)
	}
	fmt.Println("sequential:", time.Since(start).Round(10*time.Millisecond))

	start = time.Now()
	var wg sync.WaitGroup
	for i := range 5 {
		wg.Go(func() { fetch(i) })
	}
	wg.Wait()
	fmt.Println("concurrent:", time.Since(start).Round(10*time.Millisecond))
}
