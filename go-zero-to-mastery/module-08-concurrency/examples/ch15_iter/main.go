package main

import (
	"fmt"
	"iter"
)

// Same sequence with a Go 1.23 iterator: no goroutine, no channel.
func fib() iter.Seq[int] {
	return func(yield func(int) bool) {
		a, b := 0, 1
		for yield(a) { // yield returns false when the loop breaks
			a, b = b, a+b
		}
	}
}

func main() {
	for v := range fib() {
		if v > 100 {
			break
		}
		fmt.Print(v, " ")
	}
	fmt.Println()
}
