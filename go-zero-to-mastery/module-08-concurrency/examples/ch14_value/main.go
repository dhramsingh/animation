package main

import (
	"context"
	"fmt"
)

// An unexported key type: no other package can collide with it.
type ctxKey int

const requestIDKey ctxKey = 0

func WithRequestID(ctx context.Context, id string) context.Context {
	return context.WithValue(ctx, requestIDKey, id)
}

func RequestID(ctx context.Context) (string, bool) {
	id, ok := ctx.Value(requestIDKey).(string)
	return id, ok
}

func handle(ctx context.Context) {
	if id, ok := RequestID(ctx); ok {
		fmt.Println("handling request", id)
	}
}

func main() {
	ctx := WithRequestID(context.Background(), "7f3a-91c2")
	handle(ctx)
	_, ok := RequestID(context.Background())
	fmt.Println("background has an id:", ok)
}
