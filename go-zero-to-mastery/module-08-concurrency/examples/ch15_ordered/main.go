package main

import (
	"fmt"
	"math/rand/v2"
	"sync"
	"time"
)

func main() {
	inputs := []string{"alpha", "bravo", "charlie", "delta", "echo"}
	out := make([]string, len(inputs)) // result i goes to slot i

	var wg sync.WaitGroup
	for i, s := range inputs {
		wg.Go(func() {
			time.Sleep(time.Duration(rand.IntN(40)) * time.Millisecond)
			out[i] = fmt.Sprintf("%s:%d", s, len(s))
		})
	}
	wg.Wait() // finish order is random, but the output order is not
	fmt.Println(out)
}
