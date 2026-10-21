package main

import "fmt"

type request struct {
	n     int
	reply chan int // where to send the answer
}

// server owns its work; clients reach it only through reqs.
func server(reqs <-chan request) {
	for r := range reqs {
		r.reply <- r.n * r.n
	}
}

func main() {
	reqs := make(chan request)
	go server(reqs)
	for _, n := range []int{3, 4, 5} {
		r := request{n, make(chan int)}
		reqs <- r // ask...
		fmt.Println(n, "squared is", <-r.reply) // ...and wait
	}
	close(reqs)
}
