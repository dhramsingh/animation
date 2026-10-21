package main

import "fmt"

func gen(vals ...int) <-chan int {
	ch := make(chan int)
	go func() {
		for _, v := range vals {
			ch <- v
		}
		close(ch)
	}()
	return ch
}

func main() {
	a, b := gen(1, 2, 3), gen(10, 20)
	for a != nil || b != nil { // until BOTH are finished
		select {
		case v, ok := <-a:
			if !ok {
				a = nil // a nil channel is never ready: case disabled
				fmt.Println("a closed")
				continue
			}
			fmt.Println("a:", v)
		case v, ok := <-b:
			if !ok {
				b = nil
				fmt.Println("b closed")
				continue
			}
			fmt.Println("b:", v)
		}
	}
	fmt.Println("merged everything")
}
