package main

import (
	"fmt"
	"time"
)

func main() {
	tick := time.NewTicker(100 * time.Millisecond)
	defer tick.Stop() // release the ticker
	stop := time.After(450 * time.Millisecond)
	start := time.Now()

	for {
		select {
		case t := <-tick.C:
			ms := t.Sub(start).Round(10 * time.Millisecond)
			fmt.Printf("tick at +%v\n", ms)
		case <-stop:
			fmt.Println("stop")
			return
		}
	}
}
