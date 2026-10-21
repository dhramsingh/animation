package main

import (
	"context"
	"fmt"
)

// fib returns a channel that yields Fibonacci numbers until ctx is done.
func fib(ctx context.Context) <-chan int {
	out := make(chan int)
	go func() {
		defer close(out)
		a, b := 0, 1
		for {
			select {
			case out <- a:
				a, b = b, a+b
			case <-ctx.Done(): // consumer left: stop, do not leak
				return
			}
		}
	}()
	return out
}

func main() {
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()
	for v := range fib(ctx) {
		if v > 100 {
			break // cancel() (deferred) stops the generator goroutine
		}
		fmt.Print(v, " ")
	}
	fmt.Println()
}
