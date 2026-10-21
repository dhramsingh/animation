package main

import (
	"context"
	"errors"
	"fmt"
	"time"
)

var errQuota = errors.New("tenant quota exceeded")

func main() {
	ctx, cancel := context.WithCancelCause(context.Background())
	cancel(errQuota)                          // cancel AND record why
	fmt.Println("Err:  ", ctx.Err())          // always context.Canceled
	fmt.Println("Cause:", context.Cause(ctx)) // the reason we gave

	tctx, tcancel := context.WithTimeoutCause(context.Background(),
		20*time.Millisecond, errors.New("payment API too slow"))
	defer tcancel()
	<-tctx.Done()
	fmt.Println("Err:  ", tctx.Err())
	fmt.Println("Cause:", context.Cause(tctx))
}
