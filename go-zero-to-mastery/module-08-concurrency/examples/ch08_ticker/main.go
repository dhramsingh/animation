package main

import (
	"fmt"
	"time"
)

func main() {
	tick := time.NewTicker(100 * time.Millisecond)
	defer tick.Stop()
	stop := time.After(450 * time.Millisecond)
	start := time.Now()

	for {
		select {
		case t := <-tick.C:
			fmt.Printf("tick at +%dms\n", t.Sub(start).Round(10*time.Millisecond).Milliseconds())
		case <-stop:
			fmt.Println("stop")
			return
		}
	}
}
