package main

import "fmt"

func main() {
	events := make(chan string, 1)

	for i := 1; i <= 3; i++ {
		select {
		case events <- fmt.Sprintf("event %d", i): // try to send
			fmt.Println("queued  event", i)
		default: // channel full: do not wait
			fmt.Println("dropped event", i)
		}
	}

	select {
	case e := <-events: // try to receive
		fmt.Println("handled", e)
	default:
		fmt.Println("nothing to do")
	}
}
