package main

import (
	"fmt"
	"sync/atomic"
	"time"
)

var done atomic.Bool // synchronized

func main() {
	go func() {
		time.Sleep(10 * time.Millisecond)
		done.Store(true) // synchronized before the Load that sees it
	}()
	for !done.Load() {
	}
	fmt.Println("finished")
}
