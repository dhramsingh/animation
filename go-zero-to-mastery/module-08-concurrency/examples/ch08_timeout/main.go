package main

import (
	"fmt"
	"time"
)

func slowQuery(d time.Duration) <-chan string {
	out := make(chan string, 1) // buffered: the sender never leaks
	go func() {
		time.Sleep(d)
		out <- fmt.Sprintf("result after %v", d)
	}()
	return out
}

func main() {
	for _, d := range []time.Duration{50 * time.Millisecond, 300 * time.Millisecond} {
		select {
		case r := <-slowQuery(d):
			fmt.Println("ok:", r)
		case <-time.After(100 * time.Millisecond):
			fmt.Println("timeout: gave up after 100ms")
		}
	}
}
