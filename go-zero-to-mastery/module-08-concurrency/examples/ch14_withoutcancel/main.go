package main

import (
	"context"
	"fmt"
	"time"
)

type key struct{}

func main() {
	base := context.WithValue(context.Background(), key{}, "req-42")
	req, cancel := context.WithCancel(base)
	audit := context.WithoutCancel(req) // keeps values, drops cancellation
	cancel()                            // the request is finished

	fmt.Println("request ctx err:", req.Err())
	fmt.Println("audit ctx err:  ", audit.Err())
	fmt.Println("audit sees value:", audit.Value(key{}))
	select {
	case <-audit.Done():
		fmt.Println("audit cancelled")
	case <-time.After(10 * time.Millisecond):
		fmt.Println("audit log written after the request ended")
	}
}
