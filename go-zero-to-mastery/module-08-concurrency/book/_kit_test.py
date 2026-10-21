from kit import *


class KitTest(Page):
    CH = "8.0"
    CH_NAME = "Kit test"
    TITLE = "Every component on one page"
    SUB = "Text with **bold**, `inline code`, {red|colour} and __italic__ on a single wrapped line."

    def build(self):
        p = txt("A goroutine is a **function executing concurrently** with other goroutines "
                "in the same address space. Launch one with `go f(x)`; the channel operator "
                "`ch <- v` sends and `v := <-ch` receives.", width=4.2)
        self.at(p, X0, Y0)
        b = bullets(["Cheap: starts with a **2 KB** stack",
                     "Scheduled by the {go|Go runtime}, not the OS",
                     "Communicate with channels"], width=4.2, size=18)
        self.at(b, X0, p.get_bottom()[1] - 0.25)
        c = callout("warn", "Sending on a **closed** channel panics. Only the sender should close.", width=4.4)
        self.at(c, X0, b.get_bottom()[1] - 0.25)
        c2 = callout("hood", "`hchan` has a lock, a ring buffer and two wait queues.", width=4.4)
        self.at(c2, X0, c.get_bottom()[1] - 0.2)

        src = '''package main

import "fmt"

func main() {
    ch := make(chan int, 3) // buffered
    go func() {
        for i := range 3 {
            ch <- i * 10
        }
        close(ch)
    }()
    for v := range ch {
        fmt.Println("got", v)
    }
}'''
        cd = code(src, title="main.go", hl=[6, (9, T.GREEN)], marks={6: "1", 9: ("2", T.GREEN)})
        self.at(cd, -2.0, Y0)
        tm = terminal("$ go run .\ngot 0\ngot 10\ngot 20", title="output")
        self.at(tm, -2.0, cd.get_bottom()[1] - 0.2)

        tb = table([["Operation", "nil chan", "closed chan"],
                    ["send `ch <- v`", "blocks forever", "{red|panic}"],
                    ["receive `<-ch`", "blocks forever", "zero value, ok=false"]],
                   [1.7, 1.4, 1.8], size=15)
        self.at(tb, 2.0, Y0)

        icons = VGroup(gopher(0.9), gopher(0.9, mood="sleep"), gopher(0.9, mood="blocked"),
                       gopher(0.9, mood="run"), gopher(0.9, mood="dead")).arrange(RIGHT, buff=0.35)
        self.at(icons, 2.0, tb.get_bottom()[1] - 0.4)
        toks = VGroup(gtok("G1"), gtok("G2", state="ready"), gtok("G3", state="wait"),
                      gtok("G4", state="dead"), mthread("M0"), pchip("P0")).arrange(RIGHT, buff=0.2)
        self.at(toks, 2.0, icons.get_bottom()[1] - 0.35)
        misc = VGroup(cpu_core(), lock_icon(), lock_icon(locked=False), clock_icon(), gear_icon(),
                      chan_pipe(3, ["a", "b"], lab="chan int (cap 3)")).arrange(RIGHT, buff=0.25)
        self.at(misc, 2.0, toks.get_bottom()[1] - 0.35)
        bb = bubble("I am parked on `recvq` until someone sends.", width=3.0, tail="left", tail_x=0)
        self.at(bb, 1.0, -2.6)
        a = arrow(P(2.0, -3.2), P(4.0, -3.2), T.GO)
        self.add(a, arrow_label(a, "work stealing"))
        st = stat("2 KB", "initial goroutine stack", w=2.0)
        self.at(st, 4.6, -2.4)
