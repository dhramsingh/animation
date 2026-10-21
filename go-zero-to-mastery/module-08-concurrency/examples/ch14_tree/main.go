package main

import (
	"context"
	"fmt"
	"sync"
	"time"
)

func worker(ctx context.Context, name string, wg *sync.WaitGroup) {
	defer wg.Done()
	<-ctx.Done() // block until this context is cancelled
	fmt.Printf("%-12s stopped: %v\n", name, ctx.Err())
}

func main() {
	root, cancelRoot := context.WithCancel(context.Background())
	a, cancelA := context.WithCancel(root)
	b, cancelB := context.WithCancel(root)
	a1, cancelA1 := context.WithCancel(a)
	defer cancelB()
	defer cancelA1()

	var wg sync.WaitGroup
	for name, ctx := range map[string]context.Context{"a": a, "b": b, "a1 (child)": a1} {
		wg.Add(1)
		go worker(ctx, name, &wg)
	}

	fmt.Println("cancel a  -> a and its child a1 stop; b keeps running")
	cancelA()
	time.Sleep(50 * time.Millisecond)
	fmt.Println("cancel root -> everything left stops")
	cancelRoot()
	wg.Wait()
}
