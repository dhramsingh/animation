package crawler

import (
	"context"
	"fmt"
	"sync"
	"time"
)

// A fake web: page -> links. Every fetch takes 20ms.
var web = map[string][]string{
	"/":          {"/go", "/blog", "/docs"},
	"/go":        {"/go/chan", "/go/select", "/"},
	"/blog":      {"/blog/1", "/blog/2", "/go"},
	"/docs":      {"/docs/mem", "/go/chan"},
	"/go/chan":   {"/go/select"},
	"/go/select": {},
	"/blog/1":    {"/blog/2"},
	"/blog/2":    {"/missing"},
	"/docs/mem":  {"/"},
}

type Page struct {
	URL   string
	Depth int
	Links []string
	Err   error
}

type task struct {
	url   string
	depth int
}

func fetch(ctx context.Context, url string) ([]string, error) {
	select {
	case <-time.After(20 * time.Millisecond):
	case <-ctx.Done():
		return nil, ctx.Err()
	}
	links, ok := web[url]
	if !ok {
		return nil, fmt.Errorf("404 not found")
	}
	return links, nil
}

// Crawl visits pages breadth-first up to maxDepth with a pool of workers.
func Crawl(ctx context.Context, root string, maxDepth, workers int) []Page {
	tasks := make(chan task)
	results := make(chan Page)
	limiter := time.NewTicker(5 * time.Millisecond) // at most 200 fetches/s
	defer limiter.Stop()

	var wg sync.WaitGroup
	for range workers { // 1. the fetcher pool: no shared state at all
		wg.Go(func() {
			for t := range tasks {
				select {
				case <-limiter.C: // wait for a rate-limit token
				case <-ctx.Done():
				}
				links, err := fetch(ctx, t.url)
				results <- Page{t.url, t.depth, links, err}
			}
		})
	}

	// 2. the coordinator: the ONLY goroutine that touches seen/queue
	seen := map[string]bool{root: true}
	queue := []task{{root, 0}}
	inflight, done := 0, ctx.Done()
	var pages []Page
	for len(queue) > 0 || inflight > 0 {
		var send chan task // nil -> this select case is disabled
		var next task
		if len(queue) > 0 {
			send, next = tasks, queue[0]
		}
		select {
		case send <- next:
			queue = queue[1:]
			inflight++
		case p := <-results:
			inflight--
			pages = append(pages, p)
			if p.Err != nil || p.Depth == maxDepth {
				continue
			}
			for _, l := range p.Links {
				if !seen[l] {
					seen[l] = true
					queue = append(queue, task{l, p.Depth + 1})
				}
			}
		case <-done: // cancelled: stop dispatching, keep draining
			queue, done = nil, nil
		}
	}
	close(tasks) // 3. shut the pool down and wait for it
	wg.Wait()
	return pages
}
