package counter

import (
	"sync"
	"sync/atomic"
	"testing"
)

func BenchmarkMutexInc(b *testing.B) {
	var mu sync.Mutex
	n := 0
	b.RunParallel(func(pb *testing.PB) {
		for pb.Next() {
			mu.Lock()
			n++
			mu.Unlock()
		}
	})
}

func BenchmarkAtomicInc(b *testing.B) {
	var n atomic.Int64
	b.RunParallel(func(pb *testing.PB) {
		for pb.Next() {
			n.Add(1)
		}
	})
}

func BenchmarkChannelInc(b *testing.B) {
	inc := make(chan struct{}, 128)
	done := make(chan struct{})
	go func() { // one owner goroutine holds the counter
		n := 0
		for range inc {
			n++
		}
		close(done)
	}()
	b.RunParallel(func(pb *testing.PB) {
		for pb.Next() {
			inc <- struct{}{}
		}
	})
	close(inc)
	<-done
}

func BenchmarkMutexRead(b *testing.B) {
	var mu sync.Mutex
	m := map[int]int{1: 1}
	b.RunParallel(func(pb *testing.PB) {
		for pb.Next() {
			mu.Lock()
			_ = m[1]
			mu.Unlock()
		}
	})
}

func BenchmarkRWMutexRead(b *testing.B) {
	var mu sync.RWMutex
	m := map[int]int{1: 1}
	b.RunParallel(func(pb *testing.PB) {
		for pb.Next() {
			mu.RLock()
			_ = m[1]
			mu.RUnlock()
		}
	})
}
