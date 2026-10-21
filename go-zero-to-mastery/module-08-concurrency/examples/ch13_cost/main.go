package main

import (
	"fmt"
	"os"
	"slices"
	"strings"
	"sync"
	"time"
)

// A small, typical workload: goroutines, a mutex-guarded map, sorting.
func work() int {
	var mu sync.Mutex
	counts := map[int]int{}
	var wg sync.WaitGroup
	for w := range 4 {
		wg.Go(func() {
			local := make([]int, 0, 250_000)
			for i := range 250_000 {
				local = append(local, (i*7919+w)%100_003)
			}
			slices.Sort(local)
			mu.Lock()
			for _, v := range local[:1000] {
				counts[v]++
			}
			mu.Unlock()
		})
	}
	wg.Wait()
	return len(counts)
}

// peakRSS reports the most physical memory the process ever used.
func peakRSS() string {
	b, _ := os.ReadFile("/proc/self/status")
	for _, l := range strings.Split(string(b), "\n") {
		if v, ok := strings.CutPrefix(l, "VmHWM:"); ok {
			return strings.TrimSpace(v)
		}
	}
	return "?"
}

func main() {
	t0 := time.Now()
	for range 5 {
		work()
	}
	fmt.Printf("time: %v   peak memory: %s\n",
		time.Since(t0).Round(time.Millisecond), peakRSS())
}
