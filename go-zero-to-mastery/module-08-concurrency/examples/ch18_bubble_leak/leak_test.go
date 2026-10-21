package leak

import (
	"testing"
	"testing/synctest"
)

func TestLeakyHelper(t *testing.T) {
	synctest.Test(t, func(t *testing.T) {
		results := make(chan int)
		go func() {
			results <- 42 // nobody ever receives: this goroutine leaks
		}()
		// the test body returns without reading results
	})
}
