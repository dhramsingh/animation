package main

import (
	"fmt"
	"sync"
)

func main() {
	results := make(chan string)
	var wg sync.WaitGroup
	for id := 1; id <= 3; id++ { // three senders
		wg.Go(func() {
			results <- fmt.Sprintf("worker %d", id)
		})
	}

	go func() { // closer: wait for ALL, then close
		wg.Wait()
		close(results)
	}()

	n := 0
	for r := range results {
		fmt.Println("received from", r)
		n++
	}
	fmt.Println("total:", n)
}
