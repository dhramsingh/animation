from kit import *

CH, NAME = "8.11", "Preemption"


class C11Opener(Opener):
    NUM, NAME = CH, NAME
    TAGLINE = "A goroutine that never blocks would keep its P forever. Preemption is how the runtime takes the CPU back, and since Go 1.14 it works even inside tight loops."
    LEARN = ["List every point where a goroutine gives up its P",
             "Explain cooperative preemption through the stack guard",
             "Follow asynchronous preemption: sysmon, SIGURG, safe points",
             "Reproduce a pre-1.14 hang with `asyncpreemptoff=1`",
             "Use `Gosched` and `LockOSThread` for the right reasons"]
    QUESTION = "With GOMAXPROCS=1, one goroutine runs `for { counter++ }`. Will main ever run again?"

    def art(self):
        g = VGroup()
        loop = gopher(1.5, mood="run").move_to(P(2.6, 0.55))
        ring = Circle(radius=1.25).move_to(loop).set_stroke(T.RED, 3, 0.6)
        arr = Arrow(ring.point_at_angle(PI * 0.15), ring.point_at_angle(-PI * 0.05), path_arc=-0.6, buff=0, fill_color=T.RED, thickness=3)
        g.add(ring, arr, loop, mono("for { counter++ }", size=15, color=T.RED).next_to(ring, DOWN, buff=0.15))
        sm = mthread("sysmon", w=1.45, h=0.55, size=14).move_to(P(5.6, 1.85))
        bolt = Polygon(P(0, 0.35), P(-0.18, 0.0), P(0.0, 0.02), P(-0.12, -0.35), P(0.2, 0.08), P(0.02, 0.06)).set_fill(T.YELLOW, 1).set_stroke(width=0)
        bolt.scale(1.3).move_to(P(4.6, 1.05))
        g.add(sm, bolt, txt("SIGURG", size=14, color=T.YELLOW, font=T.MONO, weight="BOLD").next_to(bolt, RIGHT, buff=0.1))
        g.add(dashed_arrow(sm.get_bottom() + LEFT * 0.3, ring.get_right() + UP * 0.3, T.YELLOW, 2.2))
        mg = gopher(1.1, mood="happy").move_to(P(5.6, -1.6))
        g.add(mg, txt("main gets the P back", size=14, color=T.GREEN).next_to(mg, DOWN, buff=0.1))
        return g


class C11Yield(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "When does a goroutine give up its P?"
    SUB = "Most of the time goroutines yield on their own, because they block. Preemption is the safety net for the ones that never do."

    def build(self):
        w = (CW - 0.4) / 2
        left = titled_box("It blocks or yields (voluntary)", w, 3.2, color=T.GREEN)
        self.at(left, X0, Y0)
        items = bullets(["channel send / receive / `select` that must wait",
                         "`sync.Mutex`, `RWMutex`, `WaitGroup.Wait`, `Cond.Wait`",
                         "`time.Sleep`, timers, tickers",
                         "network I/O through the netpoller (8.10)",
                         "a blocking system call (the P is handed off)",
                         "`runtime.Gosched()`: stay runnable, let others go first",
                         "GC assist work and waits"],
                        width=w - 0.4, size=15, gap=0.1, marker="check", marker_color=T.GREEN)
        self.at(items, X0 + 0.2, Y0 - 0.55)
        right = titled_box("It is stopped (involuntary: preemption)", w, 3.2, color=T.RED)
        self.at(right, X0 + w + 0.4, Y0)
        items2 = bullets(["it ran for more than **10 ms** (sysmon's `forcePreemptNS`)",
                          "the GC needs to scan its stack or stop the world",
                          "a debugger or profiler asks to suspend it",
                          "**How**: at its next function call (cooperative, Go 1.2+), or almost anywhere with a signal (asynchronous, Go 1.14+)"],
                         width=w - 0.4, size=15, gap=0.12, marker="dot", marker_color=T.RED)
        self.at(items2, X0 + w + 0.6, Y0 - 0.55)
        # timeline
        y = Y0 - 4.1
        x0 = X0 + 1.2
        unit = (X1 - x0 - 0.2) / 30
        self.add(txt("**G1**", size=13, color=T.GO).move_to(P(x0 - 0.15, y), aligned_edge=RIGHT))
        segs = [(0, 4, T.GO, "run"), (4, 7, T.GREY, "chan recv"), (7, 10, T.GO, "run"), (10, 13, T.GREY, "Sleep"),
                (13, 23, T.GO, "run 10 ms (CPU-bound)"), (23, 26, T.GREEN, "runnable")]
        for a, b, col, lab in segs:
            self.add(seg(x0 + a * unit, x0 + b * unit - 0.03, y, col, h=0.36, lab=lab, size=11, outline=(col == T.GREEN)))
        for t_, lab, col in ((4, "blocks", T.GREEN), (10, "blocks", T.GREEN), (23, "preempted", T.RED)):
            self.add(arrow(P(x0 + t_ * unit, y + 0.55), P(x0 + t_ * unit, y + 0.22), col, 2, 0))
            self.add(txt(lab, size=11, color=col, weight="BOLD").move_to(P(x0 + t_ * unit, y + 0.68)))
        self.add(time_axis(x0, X1, y - 0.4, lab="time"))


class C11Cooperative(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Cooperative preemption: hijacking the stack check"
    SUB = "Go 1.2 reused the prologue every function already has (chapter 8.3). To ask a G to stop, the runtime poisons its stack guard."

    def build(self):
        steps = num_steps([("Request", "`preemptone` sets `gp.preempt = true` and `gp.stackguard0 = stackPreempt`, a huge value (0xfffffffffffffade on 64-bit)."),
                           ("Trip", "at the next function call, `CMPQ SP, 16(R14)` sees SP below the guard: every stack looks \"too small\"."),
                           ("Divert", "`morestack` → `newstack` notices `stackPreempt`: this is not a real overflow."),
                           ("Yield", "`gopreempt_m` puts the G on the global run queue and calls `schedule()`.")],
                          width=6.4, color=T.VIOLET, size=14, gap=0.14)
        self.at(steps, X0, Y0)
        asm = code('''CMPQ  SP, 16(R14)   // 16(R14) = g.stackguard0
JLS   morestack     // poisoned guard: always taken''', size=13, lang="text", title="every function prologue", width=6.4, numbers=False, hl=[1])
        self.at(asm, X0, steps.get_bottom()[1] - 0.3)
        x = X0 + 6.9
        w = X1 - x
        w2 = callout("warn", "**The flaw**: a loop with no function calls never runs a prologue, so it can never be "
                     "stopped. Before Go 1.14 one such loop could freeze the whole program: the GC waited for it to "
                     "stop, and so did everyone else.", width=w, size=14, title="THE HOLE IN THE NET")
        self.at(w2, x, Y0)
        loop = code('''// no call inside: no prologue, no check
for i := 0; i < 1<<40; i++ {
    sum += i * i
}''', size=14, title="unstoppable before Go 1.14", width=w, hl=[(2, T.RED)])
        self.at(loop, x, w2.get_bottom()[1] - 0.25)
        stk = callout("hood", "The same `stackguard0` slot serves two masters: stack growth and preemption. Overloading "
                      "a check that already runs everywhere made cooperative preemption almost free.",
                      width=w, size=13)
        self.at(stk, x, loop.get_bottom()[1] - 0.25)


class C11Async(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Asynchronous preemption (Go 1.14+): a signal"
    SUB = "To stop a goroutine that makes no calls, the runtime interrupts its thread with a signal and makes the goroutine call the scheduler from wherever it is."

    def build(self):
        lanes = [("sysmon", T.AMBER), ("kernel", T.BLUE), ("M0 / G1", T.GO)]
        x0 = X0 + 1.4
        ys = [Y0 - 0.3, Y0 - 1.25, Y0 - 2.2]
        for (lab, col), y in zip(lanes, ys):
            self.add(txt(f"**{lab}**", size=14, color=col).move_to(P(x0 - 0.15, y), aligned_edge=RIGHT))
            self.add(dashed(P(x0, y), P(X1, y), T.STROKE2, 1.2, 0.06))
        st0 = x0 + 1.3
        stp = (X1 - 1.05 - st0) / 4
        steps_x = [st0 + k * stp for k in range(5)]
        boxes = [
            (0, "G1 ran > 10 ms:\npreemptM", T.AMBER),
            (1, "tgkill(M0, SIGURG)", T.BLUE),
            (2, "handler: doSigPreempt\nsafe point? push call", T.GO),
            (2, "asyncPreempt: save ALL\nregisters, call scheduler", T.GO),
            (2, "schedule(): G2 runs;\nG1 resumes later", T.GREEN),
        ]
        prev = None
        for i, ((lane, s, col), x) in enumerate(zip(boxes, steps_x)):
            n = node(s, w=2.05, h=0.68, color=col, size=12).move_to(P(x, ys[lane]))
            self.add(n, badge(str(i + 1), T.YELLOW, r=0.13, size=11).move_to(n.get_corner(UL) + P(0.02, -0.02)))
            if prev is not None:
                self.add(arrow(prev.get_right() if prev.get_center()[1] == n.get_center()[1] else prev.get_bottom() if prev.get_center()[1] > n.get_center()[1] else prev.get_top(),
                               n.get_left() if prev.get_center()[1] == n.get_center()[1] else n.get_left(), T.MUTED, 2.0, 0.04))
            prev = n
        x = X0
        w = 6.35
        safe = callout("def", "An **async safe point** is an instruction where the runtime can stop the G and still "
                       "find every pointer in its frame: not inside the runtime itself, not in assembly without "
                       "metadata, not in a write-barrier or atomic sequence. Elsewhere the handler does nothing "
                       "and the request is retried later.", width=w, size=13, title="SAFE POINT")
        self.at(safe, x, Y0 - 2.85)
        x2 = X0 + w + 0.3
        why = callout("hood", "Why SIGURG? From runtime/signal_unix.go: debuggers pass it through by default, libc does "
                      "not use it internally, and a spurious one is harmless. SIGUSR1/2 belong to applications; "
                      "SIGALRM cannot tell a real alarm from ours.", width=X1 - x2, size=13, title="WHY SIGURG")
        self.at(why, x2, Y0 - 2.85)
        k = callout("version", "Go 1.14 (Feb 2020), after Austin Clements' proposal \"non-cooperative goroutine "
                    "preemption\" (golang/go#24543). Turn it off with `GODEBUG=asyncpreemptoff=1`.",
                    width=CW, size=13, inline=True)
        self.at(k, X0, Y1 + k.get_height() + 0.02)


class C11Demo(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "See it for yourself: one P, one tight loop"
    SUB = "The same program, run twice. The only difference is the GODEBUG setting."

    def build(self):
        w = (CW - 0.35) / 2
        a = code_ex("ch11_preempt", lines=(8, 19), size=13, width=w, hl=[(12, T.RED), (13, T.RED), 16])
        self.at(a, X0, Y0)
        ta = terminal(out("ch11_preempt"), title="default: async preemption on", width=w, size=13)
        self.at(ta, X0, a.get_bottom()[1] - 0.15)
        b = code_ex("ch11_preempt_off", lines=(8, 19), size=13, width=w, hl=[(12, T.RED), (13, T.RED), 16])
        self.at(b, X0 + w + 0.35, Y0)
        tb = terminal(out("ch11_preempt_off"), title="asyncpreemptoff=1: like Go 1.13", width=w, size=13)
        self.at(tb, X0 + w + 0.35, b.get_bottom()[1] - 0.15)
        y = min(ta.get_bottom()[1], tb.get_bottom()[1]) - 0.3
        x0 = X0 + 1.0
        unit = (X0 + w - x0 - 0.1) / 120
        for col_i, (xx, timeline) in enumerate(((X0, [(0, 2, "main", T.GO), (2, 4.1, "loop", T.RED), (4.1, 6.2, "loop", T.RED), (6.2, 8.3, "loop", T.RED), (8.3, 10.4, "loop", T.RED), (10.4, 12.5, "loop", T.RED), (12.5, 15, "main prints", T.GREEN)]),
                                                (X0 + w + 0.35, [(0, 2, "main", T.GO), (2, 120, "loop ... forever", T.RED)]))):
            xs = xx + 1.0
            self.add(txt("**P0**", size=13, color=T.VIOLET).move_to(P(xs - 0.12, y - 0.2), aligned_edge=RIGHT))
            for a_, b_, lab, col in timeline:
                scale = unit if col_i else unit * 7.6
                self.add(seg(xs + a_ * scale, min(xs + b_ * scale, xx + w - 0.1), y - 0.2, col, h=0.36, lab=lab, size=11))
        self.add(txt("main sleeps 50 ms; the loop holds the P but is preempted every ~10 ms, so main runs soon after its timer fires", size=12, color=T.TEXT2, width=w)
                 .move_to(P(X0, y - 0.6), aligned_edge=UL))
        self.add(txt("no call, no signal: the loop never yields, main never runs, the run is killed after 4 s", size=12, color=T.RED, width=w)
                 .move_to(P(X0 + w + 0.35, y - 0.6), aligned_edge=UL))
        k = callout("key", "Async preemption bounds how long one goroutine can hold a P to about **10 ms**, whatever its code looks like.",
                    width=CW, size=14, inline=True)
        self.at(k, X0, Y1 + k.get_height() + 0.02)


class C11Tools(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Gosched, LockOSThread and latency"
    SUB = "You rarely need to touch the scheduler. Here are the two knobs that exist, and what preemption means for latency."

    def build(self):
        cd = code_ex("ch11_gosched", lines=(9, 21), size=13, hl=[15])
        self.at(cd, X0, Y0)
        tm = terminal(out("ch11_gosched"), title="GOMAXPROCS=1", width=cd.get_width(), size=13)
        self.at(tm, X0, cd.get_bottom()[1] - 0.12)
        g1 = callout("tip", "`runtime.Gosched()` moves the caller to the back of the queue and lets others run. With async "
                     "preemption it is almost never needed; if you reach for it, a channel or lock is usually missing.",
                     width=cd.get_width(), size=13)
        self.at(g1, X0, tm.get_bottom()[1] - 0.2)
        x = cd.get_right()[0] + 0.5
        w = X1 - x
        lt = card("runtime.LockOSThread()", "Wires the calling goroutine to its current thread: no other goroutine runs on that "
                  "M until `UnlockOSThread`. Needed for C libraries with thread-local state (OpenGL, some GUI toolkits), "
                  "for Linux namespaces and `setns`, and in `init` for code that must stay on the main thread. "
                  "If the goroutine exits while locked, the thread is destroyed.", w=w, color=T.AMBER, size=13)
        self.at(lt, x, Y0)
        lat = card("What preemption means for latency", "A runnable G may wait for the running G's slice to end: up to "
                   "~10 ms per G ahead of it in the queue. Many CPU-bound goroutines on few Ps therefore raise tail "
                   "latency for everyone. Fixes: fewer CPU-bound goroutines than Ps (a worker pool), or give "
                   "latency-critical work its own process.", w=w, color=T.RED, size=13)
        self.at(lat, x, lt.get_bottom()[1] - 0.2)
        np_ = card("Where preemption cannot happen", "Inside the runtime and assembly without safe-point "
                   "metadata, while the G holds runtime locks, and during cgo calls (the C code is not Go). "
                   "A long cgo call is treated like a blocking syscall instead.", w=w, color=T.VIOLET, size=13)
        self.at(np_, x, lat.get_bottom()[1] - 0.2)


class C11Recap(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Recap and check yourself"
    SUB = "Goroutines usually yield by blocking; preemption guarantees the rest yield within ~10 ms."

    def build(self):
        self.at(section("REMEMBER", T.GO), X0, Y0)
        rec = bullets([
            "Voluntary yields: channel/lock/select waits, sleeps, network I/O, syscalls, `Gosched`.",
            "sysmon requests preemption after 10 ms; the GC requests it to scan stacks.",
            "Cooperative (1.2+): poison `stackguard0`, the next call's prologue diverts to the scheduler.",
            "Asynchronous (1.14+): SIGURG to the thread; at a safe point the handler injects `asyncPreempt`.",
            "`GODEBUG=asyncpreemptoff=1` reproduces the old hang: our demo was killed after 4 s.",
            "`LockOSThread` is for thread-bound C state; `Gosched` is almost never the right fix.",
        ], width=6.0, size=15, marker="check", marker_color=T.GREEN, gap=0.14)
        self.at(rec, X0, Y0 - 0.5)
        x = 0.55
        self.at(section("CHECK YOURSELF", T.TEAL), x, Y0)
        qs = [("Why did pre-1.14 tight loops also block garbage collection?",
               "Stopping the world needs every G at a safe point; the loop never reached one."),
              ("Is a goroutine preempted in the middle of `x += 1` on a shared int?",
               "It can be, between instructions at a safe point: one more reason unsynchronised sharing is a race."),
              ("Which signal does the runtime use, and can your program also use it?",
               "SIGURG; you can, but must tolerate spurious ones."),
              ("What happens to a locked goroutine's thread when the goroutine exits without unlocking?",
               "The runtime terminates that thread instead of reusing it.")]
        y = Y0 - 0.5
        for i, (q, a_) in enumerate(qs):
            grp = vstack(txt(f"**Q{i + 1}.** {q}", size=15, color=T.TEXT, width=6.0),
                         txt(f"{{teal|**Answer.**}} {a_}", size=14, color=T.TEXT2, width=6.0), buff=0.08)
            self.at(grp, x, y)
            y = grp.get_bottom()[1] - 0.28
