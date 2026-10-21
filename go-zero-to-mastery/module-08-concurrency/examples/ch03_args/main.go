package main

import (
	"fmt"
	"time"
)

func main() {
	x := 1
	go fmt.Println("argument:", x)             // x evaluated NOW
	go func() { fmt.Println("closure:", x) }() // x read LATER
	x = 2
	time.Sleep(50 * time.Millisecond) // crude wait, fine for a demo
}
