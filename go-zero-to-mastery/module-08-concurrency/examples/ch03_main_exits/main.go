package main

import "fmt"

func say(s string) {
	for i := range 3 {
		fmt.Println(s, i)
	}
}

func main() {
	go say("goroutine") // scheduled, not waited for
	fmt.Println("main is done")
} // return -> exit(0) -> every goroutine dies
