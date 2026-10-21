package main

import (
	"fmt"
	"sync"
	"sync/atomic"
)

// storeMax raises m to v if v is larger: a classic CAS loop.
func storeMax(m *atomic.Int64, v int64) {
	for {
		old := m.Load()
		if v <= old {
			return // nothing to do
		}
		if m.CompareAndSwap(old, v) {
			return // our write won
		}
		// m changed between Load and CAS: retry
	}
}

type Config struct{ Limit int }

func main() {
	var max atomic.Int64
	var wg sync.WaitGroup
	for i := range 100 {
		wg.Go(func() { storeMax(&max, int64(i*7%101)) })
	}
	wg.Wait()
	fmt.Println("max:", max.Load())

	// atomic.Pointer: publish a whole immutable value at once
	var cfg atomic.Pointer[Config]
	cfg.Store(&Config{Limit: 10})
	old := cfg.Swap(&Config{Limit: 20}) // readers see old OR new
	fmt.Println("old:", old.Limit, "new:", cfg.Load().Limit)
}
