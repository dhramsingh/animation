package main

import (
	"fmt"
	"time"
)

// try runs op in a goroutine and reports what happened.
func try(op func() string) string {
	res := make(chan string, 1)
	go func() {
		defer func() {
			if r := recover(); r != nil {
				res <- fmt.Sprint("panic: ", r)
			}
		}()
		res <- op()
	}()
	select {
	case r := <-res:
		return r
	case <-time.After(50 * time.Millisecond):
		return "blocks" // still stuck after 50ms
	}
}

func main() {
	states := []struct {
		name string
		make func() chan int
	}{
		{"nil", func() chan int { return nil }},
		{"open, empty", func() chan int { return make(chan int, 1) }},
		{"open, full", func() chan int { c := make(chan int, 1); c <- 7; return c }},
		{"closed, empty", func() chan int { c := make(chan int, 1); close(c); return c }},
		{"closed, 1 left", func() chan int { c := make(chan int, 1); c <- 7; close(c); return c }},
	}
	for _, s := range states {
		send := try(func() string { s.make() <- 1; return "ok" })
		recv := try(func() string { v, ok := <-s.make(); return fmt.Sprintf("v=%d ok=%v", v, ok) })
		cls := try(func() string { close(s.make()); return "ok" })
		fmt.Printf("%s | send: %s | recv: %s | close: %s\n", s.name, send, recv, cls)
	}
}
