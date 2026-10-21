package main

import (
	"fmt"
	"sync"
	"time"
)

func main() {
	var a, b sync.Mutex
	var wg sync.WaitGroup
	wg.Go(func() {
		a.Lock()
		time.Sleep(10 * time.Millisecond)
		b.Lock() // waits for b ... held by the other goroutine
		fmt.Println("never")
	})
	wg.Go(func() {
		b.Lock()
		time.Sleep(10 * time.Millisecond)
		a.Lock() // waits for a ... held by the first goroutine
		fmt.Println("never")
	})
	wg.Wait()
}
