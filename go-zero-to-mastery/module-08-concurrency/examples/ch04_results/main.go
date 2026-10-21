package main

import (
	"fmt"
	"strings"
	"sync"
)

func main() {
	words := []string{"go", "chan", "select", "mutex"}
	upper := make([]string, len(words)) // a slot each

	var wg sync.WaitGroup
	for i, w := range words {
		wg.Go(func() {
			upper[i] = strings.ToUpper(w) // own slot: no race
		})
	}
	wg.Wait()
	fmt.Println(upper)
}
