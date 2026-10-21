package main

import (
	"fmt"
	"sync/atomic"
)

var s []int // a slice header is 3 words: pointer, length, capacity

//go:noinline
func load() []int { return s } // one racy read of all 3 words

func main() {
	short, long := make([]int, 1), make([]int, 1000)
	var stop atomic.Bool
	go func() { // writer: alternate between the two slices (racy!)
		for i := 0; !stop.Load(); i++ {
			if i%2 == 0 {
				s = short
			} else {
				s = long
			}
		}
	}()
	torn := 0
	for range 10_000_000 {
		v := load()
		if len(v) != cap(v) { // len from one slice, cap from the other
			torn++
		}
	}
	stop.Store(true)
	fmt.Println("torn reads:", torn, "of 10,000,000")
}
