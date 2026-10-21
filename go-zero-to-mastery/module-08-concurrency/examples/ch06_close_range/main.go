package main

import "fmt"

func main() {
	ch := make(chan int, 3)
	go func() {
		for i := 1; i <= 3; i++ {
			ch <- i * i
		}
		close(ch) // "no more values" - only the sender closes
	}()

	for v := range ch { // loops until ch is closed AND drained
		fmt.Println("got", v)
	}

	v, ok := <-ch // receive from a closed, empty channel
	fmt.Printf("after close: v=%d ok=%v\n", v, ok)
}
