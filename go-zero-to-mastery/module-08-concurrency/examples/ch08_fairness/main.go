package main

import "fmt"

func main() {
	a := make(chan int, 1)
	b := make(chan int, 1)
	counts := map[string]int{}
	for range 100_000 {
		a <- 1 // both cases are ready every time
		b <- 1
		select {
		case <-a:
			counts["a"]++
			<-b
		case <-b:
			counts["b"]++
			<-a
		}
	}
	fmt.Println("case a chosen:", counts["a"])
	fmt.Println("case b chosen:", counts["b"])
}
