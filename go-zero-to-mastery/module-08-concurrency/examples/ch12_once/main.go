package main

import (
	"fmt"
	"sync"
)

type Config struct{ DSN string }

// loadConfig runs at most once, on first use, even with many callers.
var loadConfig = sync.OnceValue(func() *Config {
	fmt.Println("loading config...")
	return &Config{DSN: "postgres://db"}
})

func main() {
	var wg sync.WaitGroup
	for range 5 {
		wg.Go(func() {
			_ = loadConfig() // all 5 get the same *Config
		})
	}
	wg.Wait()
	fmt.Println("DSN:", loadConfig().DSN)
}
