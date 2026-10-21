package main

import (
	"fmt"
	"runtime"
)

func main() {
	fmt.Println("logical CPUs (NumCPU):", runtime.NumCPU())
	fmt.Println("Ps (GOMAXPROCS):      ", runtime.GOMAXPROCS(0)) // 0 = query only

	prev := runtime.GOMAXPROCS(2) // set; returns the previous value
	fmt.Println("changed from", prev, "to", runtime.GOMAXPROCS(0))

	runtime.SetDefaultGOMAXPROCS() // Go 1.25+: back to the runtime default
	fmt.Println("default again:", runtime.GOMAXPROCS(0))
}
