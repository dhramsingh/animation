package main

import (
	"context"
	"errors"
	"fmt"
	"math/rand/v2"
	"time"
)

var calls int

func flaky() error { // fails twice, then succeeds
	calls++
	if calls < 3 {
		return errors.New("503 unavailable")
	}
	return nil
}

func retry(ctx context.Context, attempts int, base time.Duration,
	f func() error) error {
	var err error
	for i := range attempts {
		if err = f(); err == nil {
			return nil
		}
		// exponential backoff with "full jitter"
		wait := time.Duration(rand.Int64N(int64(base << i)))
		fmt.Printf("attempt %d failed (%v); retry in %v\n",
			i+1, err, wait.Round(time.Millisecond))
		select {
		case <-time.After(wait):
		case <-ctx.Done():
			return errors.Join(err, ctx.Err())
		}
	}
	return err
}

func main() {
	ctx, cancel := context.WithTimeout(context.Background(), time.Second)
	defer cancel()
	err := retry(ctx, 5, 50*time.Millisecond, flaky)
	fmt.Println("result:", err, "after", calls, "calls")
}
