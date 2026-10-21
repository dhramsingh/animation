package main

import (
	"fmt"
	"sync"
	"sync/atomic"
	"time"

	"golang.org/x/sync/singleflight"
)

var backendCalls atomic.Int32

func loadUser(id string) (any, error) {
	backendCalls.Add(1)
	time.Sleep(50 * time.Millisecond) // a slow database query
	return "user " + id, nil
}

func main() {
	var g singleflight.Group
	var wg sync.WaitGroup
	var shared atomic.Int32
	for range 10 { // 10 requests for the same key arrive at once
		wg.Go(func() {
			// Only one loadUser runs per key; the others wait for it.
			_, _, sh := g.Do("42", func() (any, error) { return loadUser("42") })
			if sh {
				shared.Add(1)
			}
		})
	}
	wg.Wait()
	fmt.Println("requests:      10")
	fmt.Println("backend calls:", backendCalls.Load())
	fmt.Println("shared result:", shared.Load())
}
