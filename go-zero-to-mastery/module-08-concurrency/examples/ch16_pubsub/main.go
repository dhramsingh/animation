package main

import (
	"fmt"
	"sync"
)

type Broker struct {
	mu   sync.Mutex
	subs []chan string
}

func (b *Broker) Subscribe() <-chan string {
	ch := make(chan string, 4) // per-subscriber buffer
	b.mu.Lock()
	b.subs = append(b.subs, ch)
	b.mu.Unlock()
	return ch
}

func (b *Broker) Publish(msg string) {
	b.mu.Lock()
	defer b.mu.Unlock()
	for _, ch := range b.subs {
		select {
		case ch <- msg:
		default: // slow subscriber: drop instead of blocking everyone
		}
	}
}

func (b *Broker) Close() {
	b.mu.Lock()
	defer b.mu.Unlock()
	for _, ch := range b.subs {
		close(ch)
	}
}

func main() {
	var b Broker
	var wg sync.WaitGroup
	for id := 1; id <= 2; id++ {
		sub := b.Subscribe()
		wg.Go(func() {
			for m := range sub {
				fmt.Printf("subscriber %d got %q\n", id, m)
			}
		})
	}
	b.Publish("deploy started")
	b.Publish("deploy finished")
	b.Close()
	wg.Wait()
}
