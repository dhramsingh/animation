package main

import (
	"fmt"
	"sync"
)

func main() {
	counter := 0
	var wg sync.WaitGroup
	for range 1000 {
		wg.Go(func() {
			for range 1000 {
				counter++ // DATA RACE: load, add, store
			}
		})
	}
	wg.Wait()
	fmt.Println("expected 1000000, got", counter)
}
