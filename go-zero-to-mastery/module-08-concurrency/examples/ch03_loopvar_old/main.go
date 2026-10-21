package main

import (
	"fmt"
	"sync"
)

// go.mod: "go 1.21" -> ONE i for all iterations
func main() {
	var wg sync.WaitGroup
	for i := 0; i < 3; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			fmt.Print(i, " ")
		}()
	}
	wg.Wait()
	fmt.Println()
}
