package main

import (
	"fmt"
	"runtime"
	"sync"
)

func main() {
	var wg sync.WaitGroup
	for _, name := range []string{"A", "B"} {
		wg.Go(func() {
			for i := range 3 {
				fmt.Print(name, i, " ")
				runtime.Gosched() // yield: go to the back of the run queue
			}
		})
	}
	wg.Wait()
	fmt.Println()
}
