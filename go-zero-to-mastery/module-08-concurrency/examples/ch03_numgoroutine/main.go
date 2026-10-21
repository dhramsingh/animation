package main

import (
	"fmt"
	"runtime"
	"time"
)

func main() {
	fmt.Println("start:", runtime.NumGoroutine())
	stop := make(chan struct{})
	for range 10 {
		go func() { <-stop }()
	}
	fmt.Println("go x10:", runtime.NumGoroutine())
	close(stop) // release all ten
	time.Sleep(10 * time.Millisecond)
	fmt.Println("closed:", runtime.NumGoroutine())
}
