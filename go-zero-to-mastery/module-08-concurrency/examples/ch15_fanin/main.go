package main

import (
	"fmt"
	"sync"
	"time"
)

func producer(name string, n int, d time.Duration) <-chan string {
	out := make(chan string)
	go func() {
		defer close(out)
		for i := range n {
			time.Sleep(d)
			out <- fmt.Sprintf("%s%d", name, i)
		}
	}()
	return out
}

// merge fans in any number of channels into one.
func merge[T any](ins ...<-chan T) <-chan T {
	out := make(chan T)
	var wg sync.WaitGroup
	for _, in := range ins {
		wg.Go(func() {
			for v := range in {
				out <- v
			}
		})
	}
	go func() { wg.Wait(); close(out) }() // close after ALL inputs end
	return out
}

func main() {
	all := merge(producer("a", 3, 30*time.Millisecond),
		producer("b", 3, 45*time.Millisecond))
	for v := range all {
		fmt.Print(v, " ")
	}
	fmt.Println()
}
