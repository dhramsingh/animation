from kit import *

CH, NAME = "8.17", "Leaks, Deadlocks and Debugging"


class C17Opener(Opener):
    NUM, NAME = CH, NAME
    TAGLINE = "Concurrency bugs rarely crash on the first try. They leak, stall or slow down. This chapter shows how they happen and the tools that make them visible."
    LEARN = ["Recognise the five ways a goroutine leaks",
             "Find leaks with the goroutineleak profile (Go 1.27)",
             "Read deadlock reports and goroutine dumps",
             "Choose the right profile: goroutine, block, mutex, trace",
             "Map common panics and symptoms to their causes"]
    QUESTION = ("A service's goroutine count climbs from 200 to 2 million over a week and memory grows with it. "
                "Nothing crashes. What is happening, and how do you find the line responsible?")

    def art(self):
        g = VGroup()
        x0, x1, y0, y1 = 0.9, 6.3, -2.2, 2.0
        g.add(arrow(P(x0, y0), P(x1, y0), T.MUTED, 2, 0), arrow(P(x0, y0), P(x0, y1), T.MUTED, 2, 0))
        g.add(txt("days", size=13, color=T.MUTED).move_to(P(x1 - 0.2, y0 - 0.25)))
        g.add(txt("goroutines", size=13, color=T.MUTED).move_to(P(x0 + 0.65, y1 + 0.05)))
        pts = [P(x0 + 0.1 + i * 0.85, y0 + 0.2 + 0.1 * i * i) for i in range(7)]
        line = VMobject().set_points_smoothly(pts).set_stroke(T.RED, 4)
        g.add(line)
        for i, p in enumerate(pts[1:], 1):
            g.add(Dot(p, radius=0.06, fill_color=T.RED))
        stack = VGroup(*[gopher(0.42, mood="sleep") for _ in range(9)]).arrange_in_grid(3, 3, h_buff=0.04, v_buff=0.02)
        stack.move_to(P(2.6, 0.9))
        g.add(stack, txt("blocked forever,\nnever collected", size=13, color=T.TEXT2, align="CENTER").next_to(stack, DOWN, buff=0.1))
        return g


class C17Leak(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "A goroutine leak in 20 lines"
    SUB = "A leaked goroutine is blocked forever. It is never collected, and neither is anything its stack points to."

    def build(self):
        w = 6.4
        cd = code_ex("ch17_leak", lines=(9, 32), size=13, width=w, hl=[(11, T.RED), (14, T.RED), 19, 20],
                     marks={11: "!", 14: "2", 20: "1"})
        self.at(cd, X0, Y0)
        tm = terminal(out("ch17_leak"), title="go run .", width=w, size=13)
        self.at(tm, X0, cd.get_bottom()[1] - 0.15)
        x = X0 + w + 0.45
        ww = X1 - x
        x0 = x + 1.25
        unit = (X1 - x0 - 0.2) / 70
        y = Y0 - 0.35
        self.add(txt("**search()**", size=12, color=T.GO).move_to(P(x0 - 0.1, y), aligned_edge=RIGHT))
        self.add(seg(x0, x0 + 10 * unit, y, T.GO, h=0.32, lab="select", size=10))
        self.add(txt("① timeout wins: returns", size=11, color=T.GO).move_to(P(x0 + 10 * unit + 0.1, y), aligned_edge=LEFT))
        y2 = y - 0.55
        self.add(txt("**helper G**", size=12, color=T.RED).move_to(P(x0 - 0.1, y2), aligned_edge=RIGHT))
        self.add(seg(x0, x0 + 50 * unit, y2, T.GO, h=0.32, lab="slow backend 50 ms", size=10))
        self.add(seg(x0 + 50 * unit, X1 - 0.05, y2, T.RED, h=0.32, lab="② ch <- r: blocked forever", size=10, outline=True,
                     text_color=T.RED))
        self.add(time_axis(x0, X1, y2 - 0.45, ticks=[(x0 + t * unit, str(t)) for t in (0, 10, 50)], lab="ms"))
        before, after = nums("ch17_leak", r"goroutines \w+:\s+(\d+)", int)
        st = stat(f"{before} → {after}", "goroutines after 100 calls: every timeout left one behind", T.RED, w=ww)
        self.at(st, x, y2 - 1.05)
        fixes = do_dont("ch := make(chan string)", "ch := make(chan string, 1)", width=ww, size=12,
                        bad_note="the late send has no receiver", good_note="the late send fits in the buffer; G exits")
        self.at(fixes, x, st.get_bottom()[1] - 0.25)
        k = txt("Also fine: select on `ctx.Done()` in the helper, so it can give up too.", size=12, color=T.TEXT2, width=ww)
        self.at(k, x, fixes.get_bottom()[1] - 0.12)


class C17Causes(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Five ways goroutines leak"
    SUB = "Every leak is a goroutine waiting for something that will never happen. These are the usual somethings."

    def build(self):
        cards = [
            ("1. A send nobody receives", "The receiver returned early (timeout, error, break).",
             "ch <- result // receiver is gone", "buffer of 1, or select on ctx.Done()", T.RED),
            ("2. A receive nobody satisfies", "The sender forgot to close, or died; `range` waits forever.",
             "for v := range jobs { … } // never closed", "the owner closes; defer close(ch)", T.RED),
            ("3. A nil channel", "Send and receive on nil block forever (handy in select, fatal elsewhere).",
             "var ch chan int; <-ch", "make the channel; check the init path", T.AMBER),
            ("4. A lock or WaitGroup never released", "A missing Unlock on an error path, a missing Done.",
             "mu.Lock(); if err != nil { return }", "defer mu.Unlock(); defer wg.Done()", T.AMBER),
            ("5. A loop with no way out", "Workers, tickers and pollers that never check for shutdown.",
             "for { work(); time.Sleep(d) }", "select on ctx.Done() each round", T.VIOLET),
        ]
        cols, gap = 3, 0.2
        w = (CW - gap * (cols - 1)) / cols
        h = 2.2
        for i, (t, d, bad, fix, col) in enumerate(cards):
            r, c = divmod(i, cols)
            b = rbox(w, h, color=col, fill=T.PANEL, radius=0.14, stroke_width=1.6)
            self.at(b, X0 + c * (w + gap), Y0 - r * (h + 0.22))
            tt = txt(f"**{t}**", size=15, color=col, width=w - 0.35)
            dd = txt(d, size=13, color=T.TEXT2, width=w - 0.35)
            cb = code(bad, size=12, numbers=False, width=w - 0.35, hl=[(1, T.RED)])
            ff = txt(f"{{green|**fix:**}} {fix}", size=13, color=T.TEXT, width=w - 0.35)
            grp = vstack(tt, dd, cb, ff, buff=0.1)
            grp.move_to(b.get_corner(UL) + P(0.17, -0.17), aligned_edge=UL)
            self.add(grp)
        x = X0 + 2 * (w + gap)
        y = Y0 - (h + 0.22)
        k = callout("key", "Ask of every `go` statement: **how does this goroutine end?** If the answer depends on "
                    "someone else doing something, make sure that someone always does it, or give the goroutine a "
                    "ctx to give up.", width=w, size=13)
        self.at(k, x, y)
        n = txt("Since Go 1.23 unreferenced timers and tickers are garbage-collected even if never stopped; "
                "the goroutine waiting on them is not.", size=12, color=T.MUTED, width=w)
        self.at(n, x, k.get_bottom()[1] - 0.15)


class C17LeakProfile(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Finding leaks: the goroutineleak profile"
    SUB = "Go 1.27 can prove that some goroutines are stuck forever: the garbage collector finds the ones blocked on channels or locks nobody else can reach."

    def build(self):
        w = 6.4
        cd = code_ex("ch17_leakprofile", lines=(10, 32), size=13, width=w, hl=[(11, T.RED), 29, 30], marks={29: "1"})
        self.at(cd, X0, Y0)
        tm = terminal(out("ch17_leakprofile", drop=(2, 4)), title="go run . (address line removed)", width=w, size=12)
        self.at(tm, X0, cd.get_bottom()[1] - 0.15)
        x = X0 + w + 0.45
        ww = X1 - x
        self.at(section("HOW THE GC DECIDES", T.VIOLET, size=15), x, Y0)
        # reachability picture
        roots = node("globals + runnable Gs", w=2.2, h=0.5, color=T.GREEN, size=12)
        self.at(roots, x, Y0 - 0.5)
        live = gtok("G main", T.GO, w=1.1, h=0.36, size=11)
        live.next_to(roots, RIGHT, buff=0.5)
        ch1 = node("ch A", w=0.9, h=0.4, color=T.GREEN, size=12).next_to(live, RIGHT, buff=0.5)
        self.add(live, ch1, arrow(roots.get_right(), live.get_left(), T.GREEN, 2, 0.04), arrow(live.get_right(), ch1.get_left(), T.GREEN, 2, 0.04))
        w1 = gtok("G1", T.GREY, w=0.8, h=0.36, state="wait", size=11).next_to(ch1, DOWN, buff=0.35)
        self.add(w1, arrow(w1.get_top(), ch1.get_bottom(), T.MUTED, 1.6, 0.03),
                 txt("waits on a reachable channel: maybe runnable", size=11, color=T.GREEN).next_to(w1, LEFT, buff=0.15))
        ch2 = node("ch B", w=0.9, h=0.4, color=T.RED, size=12)
        self.at(ch2, x + 4.5, Y0 - 1.95)
        w2 = gtok("G2", T.GREY, w=0.8, h=0.36, state="wait", size=11).next_to(ch2, LEFT, buff=0.5)
        self.add(w2, arrow(w2.get_right(), ch2.get_left(), T.MUTED, 1.6, 0.03))
        self.add(txt("only G2 refers to ch B → leaked", size=11, color=T.RED, weight="BOLD").next_to(w2, LEFT, buff=0.15))
        steps = num_steps([("Mark", "from globals and goroutines that can still run."),
                           ("Grow", "a blocked G whose channel or lock was reached may be woken: mark it too, repeat."),
                           ("Report", "Gs never reached are blocked on primitives nobody can touch: state "
                            "`_Gleaked`, listed by `pprof.Lookup(\"goroutineleak\")`.")],
                          width=ww, color=T.VIOLET, size=12, gap=0.06)
        self.at(steps, x, Y0 - 2.6)
        v = callout("version", "Experimental in Go 1.26 (`GOEXPERIMENT=goroutineleakprofile`), on by default in Go "
                    "1.27. It has no false positives, but misses leaks on channels that are still reachable, "
                    "for example from a global variable.", width=ww, size=12)
        self.at(v, x, steps.get_bottom()[1] - 0.18)


class C17Deadlock(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Deadlocks: a cycle of waiting"
    SUB = "Two goroutines each hold one lock and wait for the other's. The runtime notices only when every goroutine is stuck."

    def build(self):
        w = 6.4
        cd = code_ex("ch17_abba", lines=(9, 25), size=14, width=w, hl=[13, (15, T.RED), 19, (21, T.RED)],
                     marks={15: "!", 21: "!"})
        self.at(cd, X0, Y0)
        lines = out("ch17_abba").split("\n")
        keep = [l for l in lines if l.startswith(("$", "fatal", "goroutine")) or "main.go" in l]
        tm = terminal("\n".join(keep), title="go run . (abridged: headers and main.go lines)", width=w, size=12)
        self.at(tm, X0, cd.get_bottom()[1] - 0.15)
        x = X0 + w + 0.45
        ww = X1 - x
        cx, cy = x + ww / 2, Y0 - 1.35
        g1 = gtok("G1", T.GO, w=0.9, h=0.42, state="wait").move_to(P(cx - 1.8, cy))
        g2 = gtok("G2", T.ORANGE, w=0.9, h=0.42, state="wait").move_to(P(cx + 1.8, cy))
        la = VGroup(lock_icon(T.RED, 0.4), txt("**a**", size=14, color=T.RED)).arrange(RIGHT, buff=0.08).move_to(P(cx, cy + 0.85))
        lb = VGroup(lock_icon(T.RED, 0.4), txt("**b**", size=14, color=T.RED)).arrange(RIGHT, buff=0.08).move_to(P(cx, cy - 0.85))
        self.add(g1, g2, la, lb)
        self.add(arrow(la.get_left(), g1.get_top(), T.GO, 2.4, 0.06, arc=0.4), txt("held by", size=11, color=T.GO).move_to(P(cx - 1.35, cy + 0.85)))
        self.add(arrow(g1.get_bottom(), lb.get_left(), T.RED, 2.4, 0.06, arc=0.4), txt("waits for", size=11, color=T.RED).move_to(P(cx - 1.35, cy - 0.85)))
        self.add(arrow(lb.get_right(), g2.get_bottom(), T.ORANGE, 2.4, 0.06, arc=0.4), txt("held by", size=11, color=T.ORANGE).move_to(P(cx + 1.35, cy - 0.85)))
        self.add(arrow(g2.get_top(), la.get_right(), T.RED, 2.4, 0.06, arc=0.4), txt("waits for", size=11, color=T.RED).move_to(P(cx + 1.35, cy + 0.85)))
        st = bullets(["**Detection is global only.** \"all goroutines are asleep\" fires when nothing at all can run. In a "
                      "server, an HTTP listener is always alive, so the same cycle just hangs those two requests "
                      "forever: a __partial__ deadlock.",
                      "**Fix: one global lock order.** Every goroutine takes `a` before `b`. Or restructure so one "
                      "goroutine owns both pieces of state.",
                      "**Find them:** a goroutine dump shows goroutines in `[sync.Mutex.Lock]` for many minutes.",
                      "Channels deadlock the same way: G1 sends to G2 while G2 sends to G1, both unbuffered."],
                     width=ww, size=12, marker="arrow", marker_color=T.YELLOW, gap=0.08)
        self.at(st, x, cy - 1.45)


class C17Dump(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Reading a goroutine dump"
    SUB = "A dump lists every goroutine, what it is waiting for, and the line it is stuck on. It is the first thing to look at when a program hangs."

    def build(self):
        w = 6.4
        cd = code_ex("ch17_dump", lines=(10, 23), size=13, width=w, hl=[15, 17, 18, 22])
        self.at(cd, X0, Y0)
        tbl = table([["how to get one", ""],
                     ["`kill -QUIT <pid>` or Ctrl+\\", "dump all goroutines to stderr, then exit"],
                     ["`GOTRACEBACK=all`", "on a crash, print every user goroutine (default: only the crashing one)"],
                     ["`/debug/pprof/goroutine?debug=2`", "live, over HTTP, with `import _ \"net/http/pprof\"`"],
                     ["`pprof.Lookup(\"goroutine\")`", "from code, as above; `debug=1` groups identical stacks"]],
                    widths=[2.75, w - 2.75], size=12)
        self.at(tbl, X0, cd.get_bottom()[1] - 0.25)
        x = X0 + w + 0.45
        ww = X1 - x
        lines = out("ch17_dump").split("\n")
        keep = []
        for l in lines:
            if l.startswith(("goroutine", "main.", "created by", "time.Sleep", "sync.(*Mutex).Lock")) or "./main.go" in l:
                keep.append(l)
            elif l == "" and keep and keep[-1] != "":
                keep.append("")
        tm = terminal("\n".join(keep).strip(), title="go run . (abridged: runtime frames removed)", width=ww, size=12)
        self.at(tm, x, Y0)
        k = bullets(["`[chan receive]`, `[sync.Mutex.Lock]`, `[sleep]`: the wait reason, the same strings as the scheduler's G states (8.9).",
                     "Long waits show minutes: `[chan receive, 42 minutes]` is a strong leak hint.",
                     "\"created by … in goroutine 1\" tells you **who started** it: often the real culprit."],
                    width=ww, size=12, gap=0.06, marker="arrow", marker_color=T.YELLOW)
        self.at(k, x, tm.get_bottom()[1] - 0.2)


class C17Profiles(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Profiles and traces for concurrent programs"
    SUB = "Each tool answers a different question. Import net/http/pprof once and most of them are a URL away."

    def build(self):
        rows = [["tool", "answers", "turn it on / read it"],
                ["goroutine profile", "what is every goroutine doing right now?", "`/debug/pprof/goroutine`"],
                ["goroutineleak (1.27)", "which goroutines can never wake up?", "`/debug/pprof/goroutineleak`, `pprof.Lookup`"],
                ["block profile", "where do goroutines wait on channels, select, locks?", "`runtime.SetBlockProfileRate(n)`"],
                ["mutex profile", "which locks are contended, and who holds them too long?", "`runtime.SetMutexProfileFraction(n)`"],
                ["CPU profile", "where is CPU time spent (spinning, contention)?", "`/debug/pprof/profile?seconds=30`"],
                ["execution trace", "when did each G run, block, migrate; GC; syscalls?", "`go test -trace=t.out`, `go tool trace t.out`"],
                ["flight recorder (1.25)", "the last few seconds of trace, saved when something goes wrong", "`trace.NewFlightRecorder(cfg)`, `WriteTo`"],
                ["`-race`", "which accesses are unsynchronized?", "`go test -race ./...` (8.13)"]]
        tbl = table(rows, widths=[2.7, 5.5, CW - 8.2], size=14, col_colors=[T.GO, None, None])
        self.at(tbl, X0, Y0)
        x, y = X0, tbl.get_bottom()[1] - 0.3
        cmd = terminal("go tool pprof -http=:8080 http://localhost:6060/debug/pprof/block", title="read any profile in a browser",
                       width=6.4, size=13)
        self.at(cmd, x, y)
        k = callout("tip", "Block and mutex profiling cost something; sample (rate > 1) in production. The execution "
                    "trace is the only tool that shows **time**: use it for latency puzzles.", width=CW - 6.8, size=13)
        self.at(k, x + 6.8, y)


class C17Guide(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Field guide: symptom → cause → fix"
    SUB = "The messages and symptoms you will meet, and where in this module each one is explained."

    def build(self):
        rows = [["you see", "usual cause", "fix (chapter)"],
                ["fatal error: all goroutines are asleep - deadlock!", "everyone waits: a send with no receiver, a missing Done, a lock cycle", "find the cycle in the dump (8.5, 8.17)"],
                ["panic: send on closed channel", "a receiver or a second sender closed it", "only the sole sender closes (8.6)"],
                ["panic: close of closed channel", "two owners", "one owner, or sync.Once (8.6)"],
                ["panic: sync: negative WaitGroup counter", "more Done than Add", "Add before go, or wg.Go (8.4)"],
                ["fatal error: concurrent map writes", "a plain map shared between goroutines", "Mutex or sync.Map (8.12)"],
                ["WARNING: DATA RACE", "unsynchronized shared memory", "add a happens-before edge (8.13)"],
                ["goroutine count keeps growing", "a leak", "goroutineleak profile, ctx (8.17)"],
                ["hangs, CPU idle", "a partial deadlock or a missing close", "goroutine dump (8.17)"],
                ["CPU busy, little progress", "spinning or heavy lock contention", "CPU and mutex profiles (8.17)"],
                ["tail latency spikes", "too many CPU-bound Gs, GC, contention", "execution trace, worker pool (8.11, 8.15)"]]
        tbl = table(rows, widths=[4.7, 4.7, CW - 9.4], size=14, col_colors=[T.RED, None, T.GREEN])
        self.at(tbl, X0, Y0)
        k = callout("key", "Most of these are found by three habits: run tests with `-race`, give every goroutine an "
                    "exit path (ctx, close), and look at a goroutine dump before guessing.", width=CW, size=14, inline=True)
        self.at(k, X0, tbl.get_bottom()[1] - 0.3)


class C17Recap(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Recap and check yourself"
    SUB = "Every goroutine needs an exit; every hang leaves evidence in a dump or a profile."

    def build(self):
        self.at(section("REMEMBER", T.GO), X0, Y0)
        rec = bullets([
            "A leaked goroutine waits forever and pins all the memory its stack references.",
            "Leaks: sends without receivers, unclosed ranges, nil channels, unreleased locks, endless loops.",
            "Go 1.27's goroutineleak profile proves leaks with the GC; it misses reachable channels.",
            "The runtime detects only total deadlock; partial deadlocks need a goroutine dump.",
            "Dumps: SIGQUIT, `GOTRACEBACK=all`, `/debug/pprof/goroutine?debug=2`.",
            "Block, mutex and CPU profiles show waiting and contention; traces show time.",
        ], width=6.1, size=15, marker="check", marker_color=T.GREEN, gap=0.12)
        self.at(rec, X0, Y0 - 0.5)
        x = 0.55
        self.at(section("CHECK YOURSELF", T.TEAL), x, Y0)
        qs = [("Why doesn't the garbage collector simply free a goroutine blocked forever?",
               "In general it cannot know nobody will wake it. The leak profile proves it only when the primitive is unreachable."),
              ("A server hangs but never prints \"all goroutines are asleep\". Why?",
               "Some goroutine (a listener, a ticker) can still run, so the deadlock is only partial."),
              ("Where would you look first for lock contention?",
               "The mutex profile (who holds) and the block profile (who waits)."),
              ("What one-line change fixes the leak in ch17_leak?",
               "`make(chan string, 1)`: the late send completes into the buffer and the goroutine exits.")]
        y = Y0 - 0.5
        for i, (q, a_) in enumerate(qs):
            grp = vstack(txt(f"**Q{i + 1}.** {q}", size=15, color=T.TEXT, width=6.0),
                         txt(f"{{teal|**Answer.**}} {a_}", size=14, color=T.TEXT2, width=6.0), buff=0.08)
            self.at(grp, x, y)
            y = grp.get_bottom()[1] - 0.26
