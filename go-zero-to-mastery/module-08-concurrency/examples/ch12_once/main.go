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
	for i := range 5 {
		wg.Go(func() {
			cfg := loadConfig() // all 5 get the same *Config
			_ = cfg
			_ = i
		})
	}
	wg.Wait()
	fmt.Println("DSN:", loadConfig().DSN)
}
