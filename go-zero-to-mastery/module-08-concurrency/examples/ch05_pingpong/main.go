package main

import "fmt"

func player(name string, table chan int, done chan struct{}) {
	for ball := range table { // receive the ball
		if ball == 6 {
			close(done)
			return
		}
		fmt.Println(name, "hits", ball)
		table <- ball + 1 // send it back
	}
}

func main() {
	table := make(chan int) // unbuffered: every pass is a hand-off
	done := make(chan struct{})
	go player("ping", table, done)
	go player("pong", table, done)
	table <- 1 // serve
	<-done
}
