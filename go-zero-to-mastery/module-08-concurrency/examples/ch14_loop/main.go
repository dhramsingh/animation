package main

import (
	"context"
	"errors"
	"fmt"
	"time"
)

// sumSquares is CPU-bound: it polls ctx.Err() every 65,536 steps.
func sumSquares(ctx context.Context, n int) (int, error) {
	sum := 0
	for i := range n {
		if i%(1<<16) == 0 {
			if err := ctx.Err(); err != nil {
				return 0, fmt.Errorf("stopped at step %d: %w", i, err)
			}
		}
		sum += i * i
	}
	return sum, nil
}

// produce blocks on sends, so it selects on ctx.Done() as well.
func produce(ctx context.Context, out chan<- int) {
	defer close(out)
	for i := 0; ; i++ {
		select {
		case out <- i:
		case <-ctx.Done():
			return
		}
	}
}

func main() {
	ctx, cancel := context.WithTimeout(context.Background(), 20*time.Millisecond)
	defer cancel()
	_, err := sumSquares(ctx, 1<<40)
	fmt.Println(err)
	fmt.Println("is DeadlineExceeded:", errors.Is(err, context.DeadlineExceeded))

	ctx2, cancel2 := context.WithCancel(context.Background())
	ch := make(chan int)
	go produce(ctx2, ch)
	for v := range ch {
		fmt.Println("got", v)
		if v == 2 {
			break
		}
	}
	cancel2() // the producer is blocked on a send: this frees it
	for range ch {
	} // ends when produce closes ch
	fmt.Println("producer stopped and closed its channel")
}
