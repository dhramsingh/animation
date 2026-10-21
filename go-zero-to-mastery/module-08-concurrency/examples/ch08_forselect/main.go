package main

import (
	"fmt"
	"time"
)

func worker(jobs <-chan int, done <-chan struct{}) {
	beat := time.NewTicker(40 * time.Millisecond)
	defer beat.Stop()
	for {
		select {
		case j, ok := <-jobs:
			if !ok {
				fmt.Println("jobs closed: exit")
				return
			}
			time.Sleep(25 * time.Millisecond) // do the job
			fmt.Println("did job", j)
		case <-beat.C:
			fmt.Println("heartbeat")
		case <-done:
			fmt.Println("told to stop: exit")
			return
		}
	}
}

func main() {
	jobs := make(chan int)
	done := make(chan struct{})
	finished := make(chan struct{})
	go func() { worker(jobs, done); close(finished) }()
	for j := 1; j <= 3; j++ {
		jobs <- j
	}
	time.Sleep(100 * time.Millisecond) // idle: heartbeats only
	close(done)
	<-finished
}
