package main

import (
	"fmt"
	"sync"
	"sync/atomic"
)

func main() {
	var counter atomic.Int64 // typed atomic (Go 1.19+)
	var wg sync.WaitGroup
	for range 1000 {
		wg.Go(func() {
			for range 1000 {
				counter.Add(1) // one indivisible read-modify-write
			}
		})
	}
	wg.Wait()
	fmt.Println("expected 1000000, got", counter.Load())

	var flag atomic.Bool
	fmt.Println("CAS false->true:", flag.CompareAndSwap(false, true))
	fmt.Println("CAS false->true:", flag.CompareAndSwap(false, true))
}
