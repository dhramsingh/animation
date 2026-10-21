package counter

import (
	"sync"
	"testing"
)

func TestHitsConcurrent(t *testing.T) {
	var h Hits
	var wg sync.WaitGroup
	for range 8 { // a test must really run things concurrently
		wg.Go(func() {
			for range 100 {
				h.Inc()
			}
		})
	}
	wg.Wait()
	t.Log("hits:", h.Get())
}
