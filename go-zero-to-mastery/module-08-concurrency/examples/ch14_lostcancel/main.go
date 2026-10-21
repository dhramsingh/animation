package main

import (
	"context"
	"fmt"
	"time"
)

func main() {
	// BUG: the CancelFunc is thrown away. The timer and the link to
	// the parent live on until the deadline fires.
	ctx, _ := context.WithTimeout(context.Background(), time.Hour)
	fmt.Println(ctx.Err())
}
