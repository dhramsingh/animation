package main

import (
	"fmt"
	"sync"
)

func main() {
	var seen sync.Map // map[string]int, safe for concurrent use
	var wg sync.WaitGroup
	for _, w := range []string{"go", "chan", "go", "select", "go"} {
		wg.Go(func() {
			// LoadOrStore: one atomic "insert if absent"
			if _, loaded := seen.LoadOrStore(w, len(w)); loaded {
				fmt.Println("duplicate:", w)
			}
		})
	}
	wg.Wait()
	n := 0
	seen.Range(func(k, v any) bool { n++; return true })
	fmt.Println("unique words:", n)
}
