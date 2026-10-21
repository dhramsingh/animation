package main

import "fmt"

func main() {
	ch := make(chan int) // unbuffered
	ch <- 42             // blocks: nobody will ever receive
	fmt.Println(<-ch)
}
