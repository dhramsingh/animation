package main

import (
	"fmt"
	"sync"
	"time"
)

func worker(id int, wg *sync.WaitGroup) {
	defer wg.Done() // always runs, even on panic
	time.Sleep(time.Duration(id) * 10 * time.Millisecond)
	fmt.Println("worker", id, "done")
}

func main() {
	var wg sync.WaitGroup
	for id := 1; id <= 3; id++ {
		wg.Add(1) // BEFORE the go statement
		go worker(id, &wg)
	}
	wg.Wait() // blocks until the counter is 0
	fmt.Println("all workers finished")
}
