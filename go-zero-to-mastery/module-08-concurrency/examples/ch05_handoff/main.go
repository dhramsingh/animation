package main

import (
	"fmt"
	"time"
)

func main() {
	start := time.Now()
	ms := func() int64 { return time.Since(start).Milliseconds() / 100 * 100 }
	ch := make(chan string)

	go func() {
		time.Sleep(300 * time.Millisecond) // receiver arrives late
		fmt.Printf("t=%dms receiver: ready\n", ms())
		v := <-ch
		fmt.Printf("t=%dms receiver: got %q\n", ms(), v)
	}()

	fmt.Printf("t=%dms sender:   sending...\n", ms())
	ch <- "hello" // blocks until the receiver takes it
	fmt.Printf("t=%dms sender:   send completed\n", ms())
	time.Sleep(10 * time.Millisecond)
}
