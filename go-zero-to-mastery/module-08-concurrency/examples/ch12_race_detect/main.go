package main

import (
	"fmt"
	"sync"
)

func main() {
	balance := 100
	var wg sync.WaitGroup
	wg.Go(func() { balance += 50 }) // write
	wg.Go(func() { balance -= 20 }) // concurrent write
	wg.Wait()
	fmt.Println("balance:", balance)
}
