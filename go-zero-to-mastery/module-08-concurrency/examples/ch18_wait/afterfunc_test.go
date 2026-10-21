package afterfunc

import (
	"context"
	"testing"
	"testing/synctest"
)

func TestAfterFunc(t *testing.T) {
	synctest.Test(t, func(t *testing.T) {
		ctx, cancel := context.WithCancel(t.Context())
		called := false
		context.AfterFunc(ctx, func() { called = true })

		synctest.Wait() // every other goroutine in the bubble is blocked
		if called {
			t.Fatal("called before cancel")
		}

		cancel()
		synctest.Wait() // the AfterFunc goroutine has run and exited
		if !called {
			t.Fatal("not called after cancel")
		}
		t.Log("called exactly when expected; no sleeps, no flakes")
	})
}
