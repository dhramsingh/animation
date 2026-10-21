package main

import (
	"fmt"
	"time"
)

func main() {
	defer func() {
		// runs in main's goroutine only
		if r := recover(); r != nil {
			fmt.Println("recovered:", r)
		}
	}()
	go func() {
		panic("boom in a worker") // nobody recovers HERE
	}()
	time.Sleep(100 * time.Millisecond)
	fmt.Println("unreachable")
}
