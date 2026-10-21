package main

import (
	"fmt"
	"runtime"
	"sync"
	"time"
)

// countPrimes counts primes in [lo, hi) by trial division (CPU-bound).
func countPrimes(lo, hi int) int {
	n := 0
	for x := max(lo, 2); x < hi; x++ {
		prime := true
		for d := 2; d*d <= x; d++ {
			if x%d == 0 {
				prime = false
				break
			}
		}
		if prime {
			n++
		}
	}
	return n
}

func run(workers, limit int) (int, time.Duration) {
	start := time.Now()
	counts := make([]int, workers)
	var wg sync.WaitGroup
	for w := range workers {
		wg.Go(func() {
			// interleave numbers so every worker gets similar work
			for lo := w * 1000; lo < limit; lo += workers * 1000 {
				counts[w] += countPrimes(lo, min(lo+1000, limit))
			}
		})
	}
	wg.Wait()
	total := 0
	for _, c := range counts {
		total += c
	}
	return total, time.Since(start)
}

func main() {
	const limit = 3_000_000
	fmt.Println("CPUs:", runtime.NumCPU())
	var base time.Duration
	for _, p := range []int{1, 2, 3, 4} {
		runtime.GOMAXPROCS(p)
		var primes int
		d := time.Hour
		for range 5 { // best of 5 runs: the machine is shared
			n, t := run(p, limit)
			primes, d = n, min(d, t)
		}
		if p == 1 {
			base = d
		}
		fmt.Printf("GOMAXPROCS=%d  primes=%d  time=%-7v speedup=%.2fx\n",
			p, primes, d.Round(time.Millisecond), float64(base)/float64(d))
	}
}
