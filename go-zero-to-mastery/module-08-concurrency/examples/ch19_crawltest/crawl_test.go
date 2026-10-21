package crawler

import (
	"context"
	"testing"
	"testing/synctest"
	"time"
)

func TestCrawl(t *testing.T) {
	synctest.Test(t, func(t *testing.T) { // fake clock: no real waiting
		ctx, cancel := context.WithTimeout(t.Context(), 2*time.Second)
		defer cancel()
		start := time.Now()
		pages := Crawl(ctx, "/", 3, 4)
		if len(pages) != 10 {
			t.Fatalf("got %d pages, want 10", len(pages))
		}
		t.Logf("10 pages in %v of fake time", time.Since(start))
	})
}

func TestCrawlDeadline(t *testing.T) {
	synctest.Test(t, func(t *testing.T) {
		ctx, cancel := context.WithTimeout(t.Context(), 30*time.Millisecond)
		defer cancel()
		start := time.Now()
		pages := Crawl(ctx, "/", 3, 4) // must return, with no leaks
		t.Logf("deadline: %d pages, returned after %v", len(pages), time.Since(start))
	})
}
