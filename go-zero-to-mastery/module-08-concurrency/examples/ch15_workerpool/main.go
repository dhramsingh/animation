package main

import (
	"fmt"
	"sync"
	"time"
)

type Job struct{ ID, N int }
type Result struct {
	JobID, Worker, Out int
}

func worker(id int, jobs <-chan Job, results chan<- Result) {
	for j := range jobs { // each worker pulls the next free job
		time.Sleep(time.Duration(j.N) * 10 * time.Millisecond)
		results <- Result{j.ID, id, j.N * j.N}
	}
}

func main() {
	jobs := make(chan Job, 10)
	results := make(chan Result, 10)

	var wg sync.WaitGroup
	for w := 1; w <= 3; w++ { // a fixed pool of 3 workers
		wg.Go(func() { worker(w, jobs, results) })
	}
	for i, n := range []int{5, 1, 3, 2, 4, 1} {
		jobs <- Job{ID: i + 1, N: n}
	}
	close(jobs) // no more jobs: workers exit their range loops

	go func() { wg.Wait(); close(results) }()
	for r := range results {
		fmt.Printf("job %d -> %2d (worker %d)\n", r.JobID, r.Out, r.Worker)
	}
}
