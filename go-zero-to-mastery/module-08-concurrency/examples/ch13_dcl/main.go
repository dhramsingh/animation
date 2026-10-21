package main

import (
	"fmt"
	"sync"
)

type Config struct{ Name string }

var (
	mu       sync.Mutex
	instance *Config
)

// BROKEN "double-checked locking": the first check reads
// instance without any synchronization.
func get() *Config {
	if instance == nil { // racy read
		mu.Lock()
		if instance == nil {
			instance = &Config{Name: "prod"} // write under the lock
		}
		mu.Unlock()
	}
	return instance
}

func main() {
	var wg sync.WaitGroup
	for range 4 {
		wg.Go(func() { _ = get().Name })
	}
	wg.Wait()
	fmt.Println(get().Name)
}
