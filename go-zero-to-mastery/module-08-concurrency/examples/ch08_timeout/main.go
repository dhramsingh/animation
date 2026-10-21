package main

import (
	"fmt"
	"time"
)

func slowQuery(d time.Duration) <-chan string {
	out := make(chan string, 1) // cap 1: the send never blocks
	go func() {
		time.Sleep(d)
		out <- fmt.Sprintf("result after %v", d)
	}()
	return out
}

func main() {
	for _, ms := range []int{50, 300} {
		d := time.Duration(ms) * time.Millisecond
		select {
		case r := <-slowQuery(d):
			fmt.Println("ok:", r)
		case <-time.After(100 * time.Millisecond):
			fmt.Println("timeout: gave up after 100ms")
		}
	}
}
