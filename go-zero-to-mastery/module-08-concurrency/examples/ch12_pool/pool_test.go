package pool

import (
	"bytes"
	"sync"
	"testing"
)

var bufPool = sync.Pool{
	New: func() any { return new(bytes.Buffer) },
}

func render(buf *bytes.Buffer) int {
	for range 64 {
		buf.WriteString("hello, gopher ")
	}
	return buf.Len()
}

func BenchmarkNewBuffer(b *testing.B) {
	for b.Loop() {
		buf := new(bytes.Buffer) // fresh allocation every time
		render(buf)
	}
}

func BenchmarkPooledBuffer(b *testing.B) {
	for b.Loop() {
		buf := bufPool.Get().(*bytes.Buffer)
		buf.Reset() // pooled objects keep old contents: reset!
		render(buf)
		bufPool.Put(buf)
	}
}
