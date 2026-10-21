package main

import (
	"fmt"
	"time"
)

// Go 1.23+: timer channels are unbuffered (capacity 0) and Reset/Stop
// guarantee that no stale value is received afterwards.
func main() {
	t := time.NewTimer(10 * time.Millisecond)
	fmt.Println("cap(t.C) =", cap(t.C))
	time.Sleep(50 * time.Millisecond) // the timer has expired by now
	t.Reset(200 * time.Millisecond)   // no need to drain t.C first

	start := time.Now()
	<-t.C
	fmt.Println("fired after", time.Since(start).Round(50*time.Millisecond))
}
