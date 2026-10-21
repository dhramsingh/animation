package main

import (
	"fmt"
	"time"
	"unsafe"
)

func main() {
	var empty struct{}
	fmt.Println("size of struct{}:", unsafe.Sizeof(empty), "bytes")

	ready := make(chan struct{}) // a pure signal: no data
	var config string
	go func() {
		time.Sleep(20 * time.Millisecond)
		config = "loaded" // (1) write
		close(ready)      // (2) signal: wakes EVERY receiver
	}()
	for i := 1; i <= 3; i++ {
		go func() {
			<-ready // (3) all three wait here
			fmt.Println("reader", i, "sees config =", config)
		}()
	}
	time.Sleep(50 * time.Millisecond)
}
