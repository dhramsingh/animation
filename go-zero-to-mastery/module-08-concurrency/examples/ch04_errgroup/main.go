package main

import (
	"context"
	"errors"
	"fmt"
	"time"

	"golang.org/x/sync/errgroup"
)

func fetch(ctx context.Context, id int) error {
	if id == 3 {
		time.Sleep(100 * time.Millisecond)
		return errors.New("fetch 3: server error")
	}
	select {
	case <-time.After(time.Duration(id) * 40 * time.Millisecond):
		fmt.Println("fetched", id)
		return nil
	case <-ctx.Done(): // a sibling failed: stop early
		fmt.Println("cancelled", id)
		return ctx.Err()
	}
}

func main() {
	g, ctx := errgroup.WithContext(context.Background())
	g.SetLimit(4) // at most 4 goroutines at once
	for id := 1; id <= 6; id++ {
		g.Go(func() error { return fetch(ctx, id) })
	}
	err := g.Wait() // first non-nil error
	fmt.Println("Wait returned:", err)
}
