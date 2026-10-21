package cache

import (
	"sync"
	"time"
)

// Cache keeps an entry for ttl, then a background goroutine expires it.
type Cache struct {
	mu sync.Mutex
	m  map[string]string
}

func New() *Cache { return &Cache{m: map[string]string{}} }

func (c *Cache) Set(k, v string, ttl time.Duration) {
	c.mu.Lock()
	c.m[k] = v
	c.mu.Unlock()
	time.AfterFunc(ttl, func() {
		c.mu.Lock()
		delete(c.m, k)
		c.mu.Unlock()
	})
}

func (c *Cache) Get(k string) (string, bool) {
	c.mu.Lock()
	defer c.mu.Unlock()
	v, ok := c.m[k]
	return v, ok
}
