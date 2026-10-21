package main

import (
	"fmt"
	"time"
)

var done bool // plain variable: NOT synchronized

func main() {
	go func() {
		time.Sleep(10 * time.Millisecond)
		done = true // write
	}()
	for !done { // read in a loop: the compiler may load it only once
	}
	fmt.Println("finished")
}
