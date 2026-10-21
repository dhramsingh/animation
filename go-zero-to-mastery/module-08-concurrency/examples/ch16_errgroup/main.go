package main

import (
	"context"
	"errors"
	"fmt"
	"time"

	"golang.org/x/sync/errgroup"
)

func fetch(ctx context.Context, page int) error {
	select {
	case <-time.After(time.Duration(20*page) * time.Millisecond):
	case <-ctx.Done():
		return ctx.Err() // a sibling failed: give up early
	}
	if page == 4 {
		return errors.New("500 internal server error")
	}
	return nil
}

func main() {
	g, ctx := errgroup.WithContext(context.Background())
	g.SetLimit(3) // at most 3 fetches in flight
	start := time.Now()
	for page := 1; page <= 8; page++ {
		g.Go(func() error { // blocks while 3 are running
			err := fetch(ctx, page)
			ms := time.Since(start).Round(10 * time.Millisecond).Milliseconds()
			fmt.Printf("+%3dms page %d: %v\n", ms, page, err)
			return err
		})
	}
	fmt.Println("g.Wait():", g.Wait())
}
