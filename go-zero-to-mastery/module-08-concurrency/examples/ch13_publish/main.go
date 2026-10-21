package main

import "fmt"

var msg string
var ready = make(chan struct{})

func setup() {
	msg = "hello, world" // (1) write the data
	close(ready)         // (2) publish: close is synchronized before...
}

func main() {
	go setup()
	<-ready          // (3) ...this receive completes
	fmt.Println(msg) // (4) guaranteed to print "hello, world"
}
