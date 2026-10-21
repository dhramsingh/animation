package main

import (
	"fmt"
	"sync"
)

type Counter struct {
	mu sync.Mutex
	n  int
}

// BUG: a value receiver copies the struct, Mutex included.
func (c Counter) Inc() {
	c.mu.Lock()
	c.n++ // increments the copy, not the caller's Counter
	c.mu.Unlock()
}

func main() {
	var c Counter
	c.Inc()
	c.Inc()
	fmt.Println("n =", c.n)
}
