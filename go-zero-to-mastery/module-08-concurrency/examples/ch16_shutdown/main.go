package main

import (
	"context"
	"fmt"
	"os"
	"os/signal"
	"sync"
	"syscall"
	"time"
)

func worker(ctx context.Context, id int, jobs <-chan int) {
	for {
		select {
		case j, ok := <-jobs:
			if !ok {
				return
			}
			time.Sleep(60 * time.Millisecond) // finish the job in hand
			fmt.Printf("worker %d finished job %d\n", id, j)
		case <-ctx.Done():
			fmt.Printf("worker %d: shutting down\n", id)
			return
		}
	}
}

func main() {
	// ctx is cancelled on SIGINT (Ctrl+C) or SIGTERM.
	ctx, stop := signal.NotifyContext(context.Background(),
		os.Interrupt, syscall.SIGTERM)
	defer stop()

	jobs := make(chan int)
	var wg sync.WaitGroup
	for id := 1; id <= 2; id++ {
		wg.Go(func() { worker(ctx, id, jobs) })
	}
	go func() { // simulate the operator pressing Ctrl+C
		time.Sleep(150 * time.Millisecond)
		syscall.Kill(os.Getpid(), syscall.SIGINT)
	}()
	for j := 1; ; j++ {
		select {
		case jobs <- j:
			continue
		case <-ctx.Done():
		}
		break
	}
	fmt.Println("signal received:", context.Cause(ctx))
	wg.Wait() // drain: let in-flight jobs finish
	fmt.Println("clean exit")
}
