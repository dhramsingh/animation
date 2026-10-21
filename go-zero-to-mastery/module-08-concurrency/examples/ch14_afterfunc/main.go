package main

import (
	"context"
	"fmt"
	"time"
)

func main() {
	ctx, cancel := context.WithCancel(context.Background())

	// Run cleanup in its own goroutine when ctx is done (Go 1.21+).
	stop := context.AfterFunc(ctx, func() {
		fmt.Println("AfterFunc: closing the connection")
	})
	_ = stop // stop() would unregister it if called before cancel

	fmt.Println("working...")
	cancel()
	time.Sleep(20 * time.Millisecond)

	ctx2, cancel2 := context.WithCancel(context.Background())
	stop2 := context.AfterFunc(ctx2, func() { fmt.Println("never printed") })
	fmt.Println("stop() before cancel:", stop2()) // true: unregistered
	cancel2()
	time.Sleep(20 * time.Millisecond)
}
