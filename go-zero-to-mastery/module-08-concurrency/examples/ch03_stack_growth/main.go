package main

import (
	"fmt"
	"runtime"
)

//go:noinline
func stackInUse() uint64 {
	var ms runtime.MemStats
	runtime.ReadMemStats(&ms)
	return ms.StackInuse
}

// depth recurses n times; at the bottom it reports the stack memory in use.
func depth(n int) uint64 {
	var pad [64]byte // make each frame a little bigger
	if n == 0 {
		return stackInUse() + uint64(pad[0])
	}
	return depth(n - 1)
}

func main() {
	done := make(chan uint64)
	for _, n := range []int{10, 1_000, 100_000, 1_000_000} {
		go func() { done <- depth(n) }() // a fresh goroutine each time
		fmt.Printf("depth %-9d -> stack in use %8.2f MB\n", n, float64(<-done)/1e6)
	}
}
