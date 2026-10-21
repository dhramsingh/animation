package main

import (
	"fmt"
	"sync"
)

type Counter struct {
	mu sync.Mutex // guards n
	n  int
}

func (c *Counter) Inc() {
	c.mu.Lock()
	defer c.mu.Unlock()
	c.n++ // critical section: one goroutine at a time
}

func main() {
	var c Counter
	var wg sync.WaitGroup
	for range 1000 {
		wg.Go(func() {
			for range 1000 {
				c.Inc()
			}
		})
	}
	wg.Wait()
	fmt.Println("expected 1000000, got", c.n)
}
