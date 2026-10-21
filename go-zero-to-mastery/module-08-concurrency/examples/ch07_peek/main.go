package main

import (
	"fmt"
	"unsafe"
)

// hchan mirrors the first fields of runtime.hchan in Go 1.27.
// Educational only: never depend on runtime internals in real code.
type hchan struct {
	qcount   uint
	dataqsiz uint
	buf      unsafe.Pointer
	elemsize uint16
	closed   uint32
	timer    unsafe.Pointer
	elemtype unsafe.Pointer
	sendx    uint
	recvx    uint
}

func peek(op string, ch chan int) {
	h := *(**hchan)(unsafe.Pointer(&ch))
	buf := unsafe.Slice((*int)(h.buf), h.dataqsiz)
	fmt.Printf("%-10s qcount=%d sendx=%d recvx=%d buf=%v closed=%d\n",
		op, h.qcount, h.sendx, h.recvx, buf, h.closed)
}

func main() {
	ch := make(chan int, 3)
	peek("make", ch)
	ch <- 10
	peek("send 10", ch)
	ch <- 20
	peek("send 20", ch)
	<-ch
	peek("recv", ch)
	ch <- 30
	ch <- 40 // sendx wraps around to 0: a ring buffer
	peek("send 30,40", ch)
	<-ch
	peek("recv", ch)
	close(ch)
	peek("close", ch)
}
