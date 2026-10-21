package main

func producer(out chan<- int) { // send-only
	out <- 1
	_ = <-out // compile error: receive from send-only channel
}

func consumer(in <-chan int) { // receive-only
	in <- 2 // compile error: send to receive-only channel
}

func main() {
	ch := make(chan int)
	go producer(ch) // chan int converts to chan<- int
	consumer(ch)    // chan int converts to <-chan int
}
