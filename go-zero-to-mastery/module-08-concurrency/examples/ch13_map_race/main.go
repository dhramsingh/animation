package main

import "sync"

func main() {
	m := map[int]int{}
	var wg sync.WaitGroup
	for g := range 2 {
		wg.Go(func() {
			for i := range 1_000_000 {
				m[i] = g // two goroutines write one plain map
			}
		})
	}
	wg.Wait()
}
