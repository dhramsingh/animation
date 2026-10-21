package main

import (
	"fmt"
	"time"
)

var counter uint64

func main() {
	go func() {
		for { // a tight loop: no function calls, no channel ops
			counter++
		}
	}()
	time.Sleep(50 * time.Millisecond) // main gives up the only P
	// Async preemption (Go 1.14+) forces the loop off the CPU:
	fmt.Println("main is running again; the loop was preempted")
}
