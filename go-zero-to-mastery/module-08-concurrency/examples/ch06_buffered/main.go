package main

import "fmt"

func main() {
	ch := make(chan string, 3) // capacity 3
	fmt.Printf("empty:  len=%d cap=%d\n", len(ch), cap(ch))

	ch <- "a"
	ch <- "b" // no receiver needed: there is room
	fmt.Printf("2 sent: len=%d cap=%d\n", len(ch), cap(ch))

	ch <- "c"
	fmt.Printf("full:   len=%d cap=%d (a 4th send would block)\n", len(ch), cap(ch))

	fmt.Println("recv:", <-ch, "(FIFO: first in, first out)")
	fmt.Printf("now:    len=%d cap=%d\n", len(ch), cap(ch))
}
