package main

import (
	"fmt"
	"sync"
)

// BUG: wg is passed by value (a copy)
func worker(id int, wg sync.WaitGroup) {
	defer wg.Done() // lowers the copy
	fmt.Println("worker", id, "done")
}

func main() {
	var wg sync.WaitGroup
	wg.Add(1)
	go worker(1, wg)
	wg.Wait() // the original never reaches 0
}
