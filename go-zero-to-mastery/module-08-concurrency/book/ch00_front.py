from kit import *


def _page_of(cls_name, default="?"):
    return PAGES.get("pages", {}).get(cls_name, default)


def _chapter_page(num, default="?"):
    return PAGES.get("chapters", {}).get(num, {}).get("page", default)


class Cover(Page):
    CHROME = False

    def build(self):
        self.add(Rectangle(width=FW + 0.2, height=FH + 0.2).set_fill(T.BG_DEEP, 1).set_stroke(width=0))
        pts = [P(x, y) for x in np.arange(-7.0, 7.2, 0.4) for y in np.arange(-3.9, 4.0, 0.4)]
        self.add(DotCloud(pts, radius=0.012, color=T.STROKE2).set_opacity(0.6))
        # glow behind the illustration
        for r, o in ((3.6, 0.04), (2.6, 0.05), (1.6, 0.05)):
            self.add(Circle(radius=r).set_fill(T.GO, o).set_stroke(width=0).move_to(P(3.9, 0.2)))

        top = pill("GO: ZERO TO MASTERY", T.GO, size=16, filled=False, padx=0.22, pady=0.09)
        mod = txt("**MODULE 8**", size=30, color=T.GO)
        title = txt("**The Concurrency Model**", size=78, color=T.TEXT, width=7.2, lsh=0.55)
        sub = txt("Goroutines, Channels, and the Scheduler", size=30, color=T.TEXT2, width=7.0)
        bar = Rectangle(width=1.6, height=0.06).set_fill(T.GO, 1).set_stroke(width=0)
        aud = txt("A graphic book for graduate and postgraduate students: "
                  "from the `go` keyword to the runtime's work-stealing scheduler.",
                  size=20, color=T.TEXT2, width=6.4)
        col = vstack(top, mod, title, sub, bar, aud, buff=0.28)
        self.at(col, -6.6, 3.2)
        n = PAGES.get("count", "")
        facts = txt(f"19 chapters  ·  {n} illustrated pages  ·  every listing runs on Go 1.27.3",
                    size=15, color=T.MUTED)
        self.at(facts, -6.6, -3.45, DL)

        # --- illustration: channels (top) and the scheduler (bottom)
        cx = 3.9
        frame1 = rbox(5.8, 2.55, color=T.STROKE2, fill=T.PANEL, fill_opacity=0.7, radius=0.25)
        frame1.move_to(P(cx, 2.05))
        lab1 = pill("CHANNELS", T.GREEN, size=12, filled=False).move_to(frame1.get_corner(UL) + P(0.75, -0.25))
        g1 = gopher(1.25, look=(0.6, 0)).move_to(P(cx - 2.15, 1.75))
        g2 = gopher(1.25, look=(-0.6, 0)).move_to(P(cx + 2.15, 1.75))
        pipe = chan_pipe(4, ["1", "2", "3"], cell=0.5).move_to(P(cx, 1.85))
        a1 = arrow(g1.get_right() + P(0.02, 0.1), pipe.get_left() + P(-0.02, 0), T.GREEN, thick=3)
        a2 = arrow(pipe.get_right() + P(0.02, 0), g2.get_left() + P(-0.02, 0.1), T.GREEN, thick=3)
        s1 = mono("ch <- v", size=15, color=T.YELLOW).next_to(pipe, UP, buff=0.22).shift(LEFT * 1.0)
        s2 = mono("v := <-ch", size=15, color=T.YELLOW).next_to(pipe, UP, buff=0.22).shift(RIGHT * 1.0)
        self.add(frame1, lab1, pipe, a1, a2, g1, g2, s1, s2)

        frame2 = rbox(5.8, 4.1, color=T.STROKE2, fill=T.PANEL, fill_opacity=0.7, radius=0.25)
        frame2.move_to(P(cx, -1.55))
        lab2 = pill("SCHEDULER", T.VIOLET, size=12, filled=False).move_to(frame2.get_corner(UL) + P(0.8, -0.25))
        self.add(frame2, lab2)
        xs = [cx - 1.6, cx, cx + 1.6]
        for i, x in enumerate(xs):
            g = gtok(f"G{i + 1}", w=0.8, h=0.38).move_to(P(x, -0.35))
            p = pchip(f"P{i}", s=0.62).move_to(P(x, -1.2))
            m = mthread(f"M{i}", w=0.95, h=0.46).move_to(P(x, -2.05))
            c = cpu_core(f"core {i}", w=1.05, h=0.55, size=11).move_to(P(x, -2.9))
            links = VGroup(Line(g.get_bottom(), p.get_top()), Line(p.get_bottom(), m.get_top()),
                           Line(m.get_bottom(), c.get_top())).set_stroke(T.STROKE2, 2)
            self.add(links, g, p, m, c)
            q = VGroup(*[gtok("", w=0.32, h=0.2, state="ready", eyes=False) for _ in range(2 - (i % 2))])
            q.arrange(DOWN, buff=0.05).next_to(p, RIGHT, buff=0.12)
            self.add(q)
        sleepy = gopher(0.55, mood="sleep").move_to(P(cx + 2.45, -0.05))
        self.add(sleepy)


class HowToRead(Page):
    TITLE = "How to read this book"
    SUB = "Every page is a picture first. Learn the cast once and you can read every diagram in the module."

    def build(self):
        # ---- column 1: the cast
        c1x, top = X0, Y0
        self.at(section("THE CAST", T.GO), c1x, top)
        states = VGroup(gtok("G1", w=0.7, h=0.32), gtok("G2", w=0.7, h=0.32, state="ready"),
                        gtok("G3", w=0.7, h=0.32, state="wait"), gtok("G4", w=0.7, h=0.32, state="dead"))
        states.arrange_in_grid(2, 2, buff=0.07)
        rows = [
            (gopher(0.6), "**A goroutine**, drawn as a gopher: the main character"),
            (states, "**G** states: {go|running}, {go|runnable} (outline), {grey|waiting}, dead"),
            (mthread("M0", w=0.85, h=0.4), "**M**: an operating-system thread ({amber|amber})"),
            (pchip("P0", s=0.46), "**P**: a logical processor that owns a run queue ({violet|violet})"),
            (cpu_core("core", w=0.85, h=0.46, size=10), "A hardware **CPU core**"),
            (chan_pipe(3, ["v"], cell=0.34), "A **channel** ({green|green}) carrying **values** ({pink|pink})"),
            (VGroup(lock_icon(s=0.3), clock_icon(r=0.16)).arrange(RIGHT, buff=0.15),
             "A **mutex** ({red|red}); **time**: timers, deadlines ({blue|blue})"),
            (kernel_band(1.1, 0.32, "KERNEL"), "The **operating system** kernel"),
        ]
        y = top - 0.5
        for icon, s in rows:
            t = txt(s, size=15, color=T.TEXT2, width=2.85)
            if icon.get_width() > 1.4:
                icon.set_width(1.4)
            h = max(icon.get_height(), t.get_height())
            icon.move_to(P(c1x + 0.72, y - h / 2))
            t.move_to(P(c1x + 1.6, y - h / 2), aligned_edge=LEFT)
            self.add(icon, t)
            y -= h + 0.13

        # ---- column 2: callouts
        c2x = -2.05
        self.at(section("THE CALLOUTS", T.YELLOW), c2x, top)
        samples = [("key", "The one idea to remember from the page."),
                   ("def", "A precise definition of a term."),
                   ("hood", "What the runtime really does, from the Go source."),
                   ("warn", "A bug students (and seniors) really write."),
                   ("tip", "Advice from production code."),
                   ("version", "Behaviour that changed in a Go release."),
                   ("try", "A small experiment to run yourself."),
                   ("q", "A question to test your understanding.")]
        y = top - 0.5
        for k, s in samples:
            c = callout(k, s, width=4.2, size=14, inline=True)
            self.at(c, c2x, y)
            y = c.get_bottom()[1] - 0.1

        # ---- column 3: code conventions
        c3x = 2.45
        self.at(section("THE CODE", T.GREEN), c3x, top)
        lst = code('ch := make(chan int)\ngo func() { ch <- 42 }()\nfmt.Println(<-ch)', size=15,
                   title="listing.go", hl=[2], marks={3: "1"}, width=4.25)
        self.at(lst, c3x, top - 0.55)
        n1 = bullets(["{yellow|Highlighted} lines carry the idea of the listing.",
                      (badge("1", T.YELLOW, r=0.11, size=11), "Numbered markers are explained next to the code."),
                      "Every listing is a real program in `examples/`."], width=4.25, size=14,
                     marker_color=T.YELLOW, gap=0.1)
        self.at(n1, c3x, lst.get_bottom()[1] - 0.18)
        term = terminal("$ go run .\n42", title="output", width=4.25)
        self.at(term, c3x, n1.get_bottom()[1] - 0.2)
        n2 = txt("Outputs are **real**: captured by `tools/run_examples.py` with Go 1.27.3 on "
                 "linux/amd64, 4 vCPUs. When the order can change from run to run, the panel says "
                 "{yellow|one possible output}.", size=14, color=T.TEXT2, width=4.25)
        self.at(n2, c3x, term.get_bottom()[1] - 0.18)
        tag = pill("ONE POSSIBLE OUTPUT", T.YELLOW, size=11, filled=False)
        self.at(tag, c3x, n2.get_bottom()[1] - 0.15)


class Roadmap(Page):
    TITLE = "The module at a glance"
    SUB = "Six parts, nineteen chapters. Each stop is a chapter; the number under it is its first page."

    def build(self):
        parts = [
            ("A", "Foundations", T.GO, [("8.1", "Concurrency vs parallelism"), ("8.2", "Threads & goroutines"),
                                         ("8.3", "Goroutines in depth"), ("8.4", "Waiting: WaitGroup & errgroup")]),
            ("B", "Channels", T.GREEN, [("8.5", "Channel basics"), ("8.6", "Buffers, close & range"),
                                        ("8.7", "Inside a channel"), ("8.8", "select & timers")]),
            ("C", "The runtime", T.VIOLET, [("8.9", "Scheduler I: G, M, P"), ("8.10", "Scheduler II: queues, syscalls, I/O"),
                                            ("8.11", "Preemption")]),
            ("D", "Shared memory", T.RED, [("8.12", "sync & atomics"), ("8.13", "The memory model")]),
            ("E", "Production", T.AMBER, [("8.14", "context"), ("8.15", "Patterns I"), ("8.16", "Patterns II"),
                                          ("8.17", "Pitfalls & debugging"), ("8.18", "Testing concurrency")]),
            ("F", "Capstone & reference", T.PINK, [("8.19", "Capstone: a crawler"), ("ref", "Cheat sheets"),
                                                  ("ref2", "Glossary & exercises")]),
        ]
        refs = {"ref": _page_of("CheatChannels"), "ref2": _page_of("Glossary")}
        blurbs = {"A": "what concurrency is and what a goroutine costs",
                  "B": "communicating by sending values",
                  "C": "how Go puts goroutines on CPUs",
                  "D": "when goroutines must share data",
                  "E": "cancellation, patterns, bugs, tests",
                  "F": "build it all; keep the cheat sheets"}
        y = Y0 - 0.35
        lx0, lx1 = -3.7, X1 - 0.3
        for key, name, col, stops in parts:
            lab = VGroup(badge(key, col, r=0.2, size=17),
                         txt(f"**{name}**", size=17, color=T.TEXT, width=2.2)).arrange(RIGHT, buff=0.16)
            self.at(lab, X0, y + 0.22, LEFT)
            d = txt(blurbs[key], size=13, color=T.MUTED, width=2.4)
            self.at(d, lab[1].get_left()[0], lab.get_bottom()[1] - 0.06)
            line = Line(P(lx0, y + 0.22), P(lx1, y + 0.22)).set_stroke(col, 7)
            self.add(line)
            n = 5
            step = (lx1 - lx0) / n
            for i, (num, s) in enumerate(stops):
                x = lx0 + step * (i + 0.5)
                st = Circle(radius=0.15).set_fill(T.BG, 1).set_stroke(col, 5).move_to(P(x, y + 0.22))
                self.add(st)
                if num.startswith("ref"):
                    nm = txt(f"**{s}**", size=14, color=T.TEXT, width=step - 0.15, align="CENTER")
                    pg = refs[num]
                else:
                    nm = txt(f"**{num}**  {s}", size=14, color=T.TEXT, width=step - 0.15, align="CENTER")
                    pg = _chapter_page(num)
                nm.next_to(st, DOWN, buff=0.12)
                pgt = txt(f"p. {pg}", size=12, color=col, weight="BOLD").next_to(nm, DOWN, buff=0.06)
                self.add(nm, pgt)
            # connector to the next part
            y -= 0.98
        g = gopher(0.62, mood="run").move_to(P(lx1 - 0.55, Y0 - 0.35 + 0.22 + 0.42))
        self.add(g)


class Outcomes(Page):
    TITLE = "What you will be able to do"
    SUB = "Outcomes are written as things you can do, from explaining an idea to designing a system."

    def build(self):
        levels = [
            ("EXPLAIN", T.GO, "the difference between concurrency and parallelism, and why goroutines are cheap"),
            ("APPLY", T.GREEN, "goroutines, channels, `select`, `sync` and `context` to real programs"),
            ("ANALYZE", T.VIOLET, "how the G-M-P scheduler places work, and read `schedtrace` and race reports"),
            ("EVALUATE", T.AMBER, "channels versus mutexes versus atomics for a given problem, with data"),
            ("CREATE", T.PINK, "leak-free, cancellable, testable concurrent systems such as a crawler"),
        ]
        y = Y0
        stair_x = X0
        for i, (verb, col, s) in enumerate(levels):
            b = rbox(5.9, 0.78, color=col, fill=col, fill_opacity=0.10, radius=0.12)
            b.move_to(P(stair_x + 0.32 * i + 2.95, y - 0.39))
            v = txt(f"**{verb}**", size=17, color=col).move_to(b.get_left() + P(0.2, 0), aligned_edge=LEFT)
            t = txt(s, size=15, color=T.TEXT, width=3.95).move_to(b.get_left() + P(1.65, 0), aligned_edge=LEFT)
            self.add(b, v, t)
            y -= 0.92
        arr = arrow(P(X0 + 0.12, Y0 - 0.95), P(X0 + 0.12, Y0 - 4.45), T.MUTED, thick=2.5)
        al = txt("deeper", size=12, color=T.MUTED).next_to(arr, DOWN, buff=0.06)
        self.add(arr, al)
        # chapter anatomy strip
        steps = ["Opener", "Concepts", "Code + real output", "Under the hood", "Pitfalls", "Check yourself"]
        cols = [T.GO, T.GREEN, T.YELLOW, T.VIOLET, T.RED, T.TEAL]
        chips = VGroup(*[pill(s_, c, size=12, filled=False, padx=0.12) for s_, c in zip(steps, cols)])
        chips.arrange(RIGHT, buff=0.28)
        lab = txt("**EVERY CHAPTER FOLLOWS THE SAME ARC**", size=13, color=T.MUTED)
        grp = vstack(lab, chips, buff=0.14)
        self.at(grp, X0, Y1 + 0.75)
        for a_, b_ in zip(chips[:-1], chips[1:]):
            self.add(arrow(a_.get_right(), b_.get_left(), T.MUTED, thick=1.8, buff=0.03))

        # prerequisites
        px = 0.75
        self.at(section("BEFORE YOU START", T.AMBER), px, Y0)
        pre = bullets(["Functions, **closures** and methods",
                       "Structs, **interfaces** and error values",
                       "Slices and maps (and why they are not safe to share)",
                       "Generics: type parameters such as `[T any]`",
                       "Packages, modules and `go test`"], width=5.9, size=16, marker="check",
                      marker_color=T.AMBER, gap=0.1)
        self.at(pre, px, Y0 - 0.5)
        self.at(section("YOUR TOOLCHAIN", T.GREEN), px, pre.get_bottom()[1] - 0.35)
        tm = terminal("$ go version\ngo version go1.27.3 linux/amd64\n"
                      "$ cd examples/ch05_pingpong && go run .\npong hits 1\n...\n"
                      "$ CGO_ENABLED=0 go run -race .\ngo: -race requires cgo; enable cgo by setting CGO_ENABLED=1",
                      title="shell", width=5.95, size=14)
        self.at(tm, px, pre.get_bottom()[1] - 0.85)
        note = txt("Go 1.25 or newer runs almost every listing; a few use Go 1.27 features and say so. "
                   "The race detector (`-race`) needs cgo and a C compiler.", size=14, color=T.TEXT2, width=5.9)
        self.at(note, px, tm.get_bottom()[1] - 0.15)
