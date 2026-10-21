package main

import (
	"fmt"
	"sync/atomic"
)

// Store-buffer litmus test. Each goroutine writes one variable and
// then reads the other. Can BOTH reads see the old value 0?
var x, y, r1, r2 int              // plain variables (racy on purpose)
var ax, ay, ar1, ar2 atomic.Int64 // atomic variables

func round(n int, body func(id int), reset func(), both0 func() bool) int {
	var start, done atomic.Int64
	for id := range 2 {
		go func() {
			for i := int64(1); i <= int64(n); i++ {
				for start.Load() != i { // spin until round i starts
				}
				body(id)
				done.Add(1)
			}
		}()
	}
	hits := 0
	for i := 1; i <= n; i++ {
		reset()
		start.Store(int64(i))
		for done.Load() != int64(2*i) {
		}
		if both0() {
			hits++
		}
	}
	return hits
}

func main() {
	const n = 1_000_000
	plain := round(n,
		func(id int) {
			if id == 0 {
				x = 1
				r1 = y
			} else {
				y = 1
				r2 = x
			}
		},
		func() { x, y = 0, 0 },
		func() bool { return r1 == 0 && r2 == 0 })
	atom := round(n,
		func(id int) {
			if id == 0 {
				ax.Store(1)
				ar1.Store(ay.Load())
			} else {
				ay.Store(1)
				ar2.Store(ax.Load())
			}
		},
		func() { ax.Store(0); ay.Store(0) },
		func() bool { return ar1.Load() == 0 && ar2.Load() == 0 })
	fmt.Printf("plain  ints: r1 == r2 == 0 in %d of %d rounds\n", plain, n)
	fmt.Printf("atomic ints: r1 == r2 == 0 in %d of %d rounds\n", atom, n)
}
