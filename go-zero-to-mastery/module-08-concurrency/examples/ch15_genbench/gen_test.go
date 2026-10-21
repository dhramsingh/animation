package gen

import (
	"iter"
	"testing"
)

// chanGen: a goroutine sends each value over a channel.
func chanGen(n, buf int) <-chan int {
	out := make(chan int, buf)
	go func() {
		defer close(out)
		for i := range n {
			out <- i
		}
	}()
	return out
}

// iterGen: a Go 1.23 iterator; the loop body runs as a callback.
func iterGen(n int) iter.Seq[int] {
	return func(yield func(int) bool) {
		for i := range n {
			if !yield(i) {
				return
			}
		}
	}
}

func BenchmarkChannel(b *testing.B) {
	sum := 0
	for v := range chanGen(b.N, 0) {
		sum += v
	}
	_ = sum
}

func BenchmarkChannelBuf64(b *testing.B) {
	sum := 0
	for v := range chanGen(b.N, 64) {
		sum += v
	}
	_ = sum
}

func BenchmarkIterator(b *testing.B) {
	sum := 0
	for v := range iterGen(b.N) {
		sum += v
	}
	_ = sum
}
