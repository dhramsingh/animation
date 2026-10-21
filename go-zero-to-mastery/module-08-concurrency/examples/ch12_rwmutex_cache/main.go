package main

import (
	"fmt"
	"sync"
)

type Cache struct {
	mu sync.RWMutex
	m  map[string]string
}

func (c *Cache) Get(k string) (string, bool) {
	c.mu.RLock() // many readers may hold RLock together
	defer c.mu.RUnlock()
	v, ok := c.m[k]
	return v, ok
}

func (c *Cache) Set(k, v string) {
	c.mu.Lock() // a writer excludes readers AND writers
	defer c.mu.Unlock()
	c.m[k] = v
}

func main() {
	c := &Cache{m: map[string]string{}}
	c.Set("lang", "Go")
	var wg sync.WaitGroup
	for range 5 {
		wg.Go(func() {
			v, _ := c.Get("lang")
			_ = v
		})
	}
	wg.Wait()
	v, ok := c.Get("lang")
	fmt.Println(v, ok)
}
