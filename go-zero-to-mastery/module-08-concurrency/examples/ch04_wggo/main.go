package main

import (
	"fmt"
	"sync"
)

func main() {
	var wg sync.WaitGroup
	var mu sync.Mutex
	sum := 0
	for i := 1; i <= 100; i++ {
		wg.Go(func() { // Add(1) + go + defer Done()
			mu.Lock()
			sum += i
			mu.Unlock()
		})
	}
	wg.Wait()
	fmt.Println("sum =", sum)
}
