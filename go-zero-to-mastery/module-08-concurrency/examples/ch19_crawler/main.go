package main

import (
	"context"
	"fmt"
	"time"
)

func run(timeout time.Duration) {
	ctx, cancel := context.WithTimeout(context.Background(), timeout)
	defer cancel()
	start := time.Now()
	pages := Crawl(ctx, "/", 3, 4)
	for _, p := range pages {
		status := fmt.Sprintf("%d links", len(p.Links))
		if p.Err != nil {
			status = p.Err.Error()
		}
		fmt.Printf("  depth %d  %-11s %s\n", p.Depth, p.URL, status)
	}
	fmt.Printf("  => %d pages in %v\n", len(pages), time.Since(start).Round(10*time.Millisecond))
}

func main() {
	fmt.Println("crawl with a 2s budget:")
	run(2 * time.Second)
	fmt.Println("crawl with a 50ms budget:")
	run(50 * time.Millisecond)
}
