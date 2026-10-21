package main

import (
	"fmt"
	"sync"
)

func main() {
	var wg sync.WaitGroup
	for i := 0; i < 3; i++ { // 1.22+: new i each time
		wg.Go(func() { fmt.Print(i, " ") })
	}
	wg.Wait()
	fmt.Println()
}
