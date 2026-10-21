package main

import (
	"fmt"
	"runtime"
	"time"
)

// search leaks a goroutine every time the timeout wins.
func search(q string) (string, error) {
	ch := make(chan string) // unbuffered: the bug
	go func() {
		time.Sleep(50 * time.Millisecond) // slow backend
		ch <- "result for " + q           // blocks forever if nobody receives
	}()
	select {
	case r := <-ch:
		return r, nil
	case <-time.After(10 * time.Millisecond):
		return "", fmt.Errorf("timeout")
	}
}

func main() {
	fmt.Println("goroutines before:", runtime.NumGoroutine())
	for i := range 100 {
		search(fmt.Sprint("q", i))
	}
	time.Sleep(100 * time.Millisecond) // every backend has answered by now
	fmt.Println("goroutines after: ", runtime.NumGoroutine())
	// Fix: make(chan string, 1) so the late send never blocks.
}
