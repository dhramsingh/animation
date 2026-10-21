package main

import (
	"context"
	"fmt"
	"time"
)

// query honours cancellation: it returns as soon as ctx is done.
func query(ctx context.Context, d time.Duration) (string, error) {
	select {
	case <-time.After(d): // pretend work
		return "rows", nil
	case <-ctx.Done():
		return "", ctx.Err()
	}
}

func main() {
	ctx, cancel := context.WithTimeout(context.Background(), 100*time.Millisecond)
	defer cancel() // always release the timer and the child links

	r, err := query(ctx, 30*time.Millisecond)
	fmt.Printf("fast query: %q err=%v\n", r, err)

	r, err = query(ctx, 500*time.Millisecond)
	fmt.Printf("slow query: %q err=%v\n", r, err)
	deadline, _ := ctx.Deadline()
	fmt.Println("deadline was set:", !deadline.IsZero())
}
