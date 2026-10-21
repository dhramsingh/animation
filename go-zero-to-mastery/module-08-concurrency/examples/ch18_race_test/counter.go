package counter

// Hits counts page views. BUG: no synchronization.
type Hits struct{ n int }

func (h *Hits) Inc()     { h.n++ }
func (h *Hits) Get() int { return h.n }
