from kit import *

CH, NAME = "8.4", "Waiting for Goroutines"


def counter_box(v, col=T.GO, w=0.7, h=0.6, size=24):
    b = rbox(w, h, color=col, fill=col, fill_opacity=0.15, radius=0.1, stroke_width=2.2)
    t = txt(f"**{v}**", size=size, color=col, font=T.MONO).move_to(b)
    return VGroup(b, t)


class C4Opener(Opener):
    NUM, NAME = CH, NAME
    TAGLINE = "Starting goroutines is easy. Knowing when they have all finished, and collecting what they produced, is where real programs go wrong."
    LEARN = ["Use `sync.WaitGroup` correctly: Add, Done, Wait",
             "Let Go 1.25's `wg.Go` do the bookkeeping for you",
             "Recognise the four classic WaitGroup bugs",
             "Collect results safely in three different shapes",
             "Use `errgroup` to wait, fail fast, cancel and limit"]
    QUESTION = "Five goroutines each fetch a page. How does main know that all five are finished, and which one failed?"

    def art(self):
        g = VGroup()
        cb = counter_box("3", T.GO, w=1.4, h=1.1, size=56).move_to(P(3.9, 1.9))
        cl = txt("**WaitGroup counter**", size=15, color=T.GO).next_to(cb, UP, buff=0.12)
        g.add(cb, cl)
        for i in range(3):
            gt = gopher(0.85, mood="run").move_to(P(2.2 + 1.7 * i, 0.15))
            d = pill("Done()", T.GREEN, size=12, filled=False).next_to(gt, DOWN, buff=0.08)
            g.add(gt, d)
            g.add(arrow(gt.get_top() + UP * 0.05, cb.get_bottom() + P(-0.4 + 0.4 * i, -0.02), T.GREEN, 2, 0.05))
        m = gopher(1.1, mood="sleep").move_to(P(3.9, -2.15))
        w = pill("main: wg.Wait()  sleeps until the counter is 0", T.VIOLET, size=12, filled=False).next_to(m, DOWN, buff=0.1)
        g.add(m, w)
        return g


class C4WaitGroup(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "sync.WaitGroup: a counter you can wait on"
    SUB = "`Add(n)` raises the counter, `Done()` lowers it by one, and `Wait()` blocks until it reaches zero."

    def build(self):
        cd = code_ex("ch04_waitgroup", lines=(9, 23), size=13, hl=[10, 18, 19, 21], marks={10: "1", 18: "2", 19: "3"})
        self.at(cd, X0, Y0)
        tm = terminal(out("ch04_waitgroup"), title="output", width=cd.get_width(), size=12)
        self.at(tm, X0, cd.get_bottom()[1] - 0.1)
        notes = bullets([(badge("1", T.YELLOW, r=0.12, size=12), "`defer wg.Done()` first, so the count drops even on an early return"),
                         (badge("2", T.YELLOW, r=0.12, size=12), "`Add` **before** `go`, in the goroutine that will call `Wait`"),
                         (badge("3", T.YELLOW, r=0.12, size=12), "pass `&wg`: a WaitGroup must never be copied")],
                        width=cd.get_width(), size=13, gap=0.05)
        self.at(notes, X0, tm.get_bottom()[1] - 0.06)
        # timeline with counter
        x = cd.get_right()[0] + 0.6
        w = X1 - x
        self.at(section("THE COUNTER OVER TIME", T.GO), x, Y0)
        x0 = x + 0.9
        unit = (X1 - x0 - 0.2) / 8
        y = Y0 - 0.85
        rows = [("main", T.GO, [(0, 1.1, "Add x3, go x3", False), (1.15, 4.0, "Wait (blocked)", True), (4.05, 8, "all workers finished", False)]),
                ("w1", T.PINK, [(1.1, 2.0, "work", False)]),
                ("w2", T.PINK, [(1.15, 3.0, "work", False)]),
                ("w3", T.PINK, [(1.2, 4.0, "work", False)])]
        for i, (lab, col, segs) in enumerate(rows):
            yy = y - i * 0.48
            self.add(txt(f"**{lab}**", size=13, color=col).move_to(P(x0 - 0.12, yy), aligned_edge=RIGHT))
            self.add(dashed(P(x0, yy), P(X1, yy), T.STROKE, 1, 0.06))
            for a, b, s, outline in segs:
                self.add(seg(x0 + a * unit, x0 + b * unit - 0.03, yy, col, h=0.34, lab=s, size=11, outline=outline))
            if i:
                end = segs[0][1]
                self.add(pill("Done", T.GREEN, size=10).move_to(P(x0 + end * unit + 0.02, yy + 0.3)))
        # counter step plot
        yc = y - 4 * 0.48 - 0.35
        self.add(txt("**counter**", size=13, color=T.YELLOW).move_to(P(x0 - 0.12, yc - 0.45), aligned_edge=RIGHT))
        steps = [(0, 0), (0.4, 3), (2.0, 2), (3.0, 1), (4.0, 0), (8, 0)]
        H = 0.3
        pts = []
        for (t0, v), (t1, _) in zip(steps[:-1], steps[1:]):
            pts += [P(x0 + t0 * unit, yc - 0.9 + v * H), P(x0 + t1 * unit, yc - 0.9 + v * H)]
        self.add(VMobject().set_points_as_corners(pts).set_stroke(T.YELLOW, 3))
        self.add(hline(x0, X1, yc - 0.9, T.STROKE2, 1.2))
        for (t0, v) in steps[1:-1]:
            self.add(txt(str(v), size=12, color=T.YELLOW, weight="BOLD").move_to(P(x0 + t0 * unit + 0.15, yc - 0.9 + v * H + 0.15)))
        rel = dashed(P(x0 + 4.0 * unit, yc - 0.95), P(x0 + 4.0 * unit, y + 0.25), T.GREEN, 2)
        self.add(rel, txt("counter = 0: Wait returns", size=12, color=T.GREEN).move_to(P(x0 + 4.1 * unit, yc - 1.15), aligned_edge=LEFT))
        k = callout("key", "WaitGroup answers one question: **are they all done?** It carries no results and no errors; "
                    "combine it with a channel or a slice for those.", width=w, size=14)
        self.at(k, x, yc - 1.45)


class C4WgGo(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Go 1.25: wg.Go does the bookkeeping"
    SUB = "`wg.Go(f)` is `Add(1)` + `go` + `defer Done()` in one call, so the two classic mistakes become impossible to write."

    def build(self):
        w = 6.35
        old = code('''var wg sync.WaitGroup
for _, url := range urls {
    wg.Add(1)               // must come first
    go func() {
        defer wg.Done()     // must not be forgotten
        fetch(url)
    }()
}
wg.Wait()''', size=13, title="before Go 1.25", width=w, hl=[(3, T.AMBER), (5, T.AMBER)])
        new = code('''var wg sync.WaitGroup
for _, url := range urls {
    wg.Go(func() {          // Add, go and Done in one
        fetch(url)
    })
}
wg.Wait()''', size=13, title="Go 1.25 and later", width=w, hl=[(3, T.GREEN)])
        self.at(old, X0, Y0)
        self.at(new, X1 - w, Y0)
        self.add(arrow(old.get_right() + P(0.03, 0), new.get_left() + P(-0.03, 0), T.GREEN, 3))
        y = min(old.get_bottom()[1], new.get_bottom()[1]) - 0.25
        impl = code('''func (wg *WaitGroup) Go(f func()) {
    wg.Add(1)
    go func() {
        defer func() {
            if x := recover(); x != nil {
                panic(x)  // f panicked: crash, no Done
            }
            wg.Done()     // f returned (or Goexit)
        }()
        f()
    }()
}''', size=12, title="sync/waitgroup.go, Go 1.27 (comments trimmed)", width=w, hl=[2, 8])
        self.at(impl, X0, y)
        cd = code_ex("ch04_wggo", lines=(12, 20), size=12, width=w, hl=[(13, T.GREEN)])
        self.at(cd, X1 - w, y)
        tm = terminal(out("ch04_wggo"), title="output", width=w, size=12)
        self.at(tm, X1 - w, cd.get_bottom()[1] - 0.1)
        v = callout("version", "`WaitGroup.Go` arrived in **Go 1.25** (August 2025). Its doc says: \"The function f must not panic.\"",
                    width=w, size=13, inline=True)
        self.at(v, X0, impl.get_bottom()[1] - 0.12)


class C4Pitfalls(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Four ways to misuse a WaitGroup, and what you see"
    SUB = "The first three outputs are real runs. The first bug is silent; the others crash or hang."

    def build(self):
        w, gap = 6.4, 0.25
        reuse = "wg.Add(1)\ngo job(&wg)\ngo wg.Wait()   // waiter A\nwg.Add(1)      // new batch: too early"
        cells = [
            ("1. Add inside the goroutine", code_ex("ch04_add_inside", lines=(13, 21), size=12, width=3.95, numbers=False, title=None,
                                                    hl=[(15, T.RED), (21, T.RED)]),
             "`Wait` may run before any `Add`: it sees 0 and returns at once. **Silent and wrong.**",
             out("ch04_add_inside").split("\n")[1:2]),
            ("2. Copying the WaitGroup", code_ex("ch04_copy", lines=(8, 19), size=12, width=3.95, numbers=False, title=None, hl=[(9, T.RED)]),
             "`Done` lowers the copy, so the original never reaches 0: the program deadlocks. `go vet` catches it:",
             out("ch04_copy_vet").split("\n")[1:2]),
            ("3. One Done too many", code_ex("ch04_negative", lines=(5, 10), size=12, width=3.95, numbers=False, title=None, hl=[(9, T.RED)]),
             "The counter would go below zero, so `Done` panics:", out("ch04_negative").split("\n")[1:2]),
            ("4. Reusing it too early", code(reuse, size=12, width=3.95, numbers=False, hl=[(4, T.RED)]),
             "A new `Add` while an old `Wait` is still returning panics with (from sync/waitgroup.go):",
             ["panic: sync: WaitGroup is reused before previous Wait has returned"]),
        ]
        for i, (title, c, note, lines) in enumerate(cells):
            cx = X0 + (i % 2) * (w + gap)
            cy = Y0 - (i // 2) * 2.75
            self.add(txt(f"**{title}**", size=16, color=T.RED).move_to(P(cx, cy), aligned_edge=UL))
            yy = cy - 0.38
            self.at(c, cx, yy)
            tx = cx + 4.1
            nt = txt(note, size=13, color=T.TEXT2, width=w - 4.1)
            self.at(nt, tx, yy)
            t = terminal("\n".join(lines), title=None, width=w - 4.1, size=11)
            self.at(t, tx, nt.get_bottom()[1] - 0.1)
        k = callout("rule", "**Add** before `go`, in the parent.  **Done** with `defer`, in the child.  **Pass a pointer**, never a copy.  "
                    "**One batch** per Wait.  Or simply use `wg.Go`.", width=CW, size=15, inline=True)
        self.at(k, X0, Y1 + k.get_height() + 0.05)


class C4Results(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Collecting results: three safe shapes"
    SUB = "A WaitGroup tells you when; it does not carry values. Pick a shape for the values, and make sure no two goroutines write the same memory."

    def build(self):
        data = [
            ("A slot per goroutine", T.GO, "Pre-size a slice; goroutine i writes only `out[i]`. Different elements are different memory: no lock, and the order is kept.",
             "ch04_results", (13, 20), [(16, T.GO)]),
            ("A results channel", T.GREEN, "Workers send; a closer goroutine waits for all of them, then closes; main ranges. Values arrive in finish order.",
             "ch06_multi_sender", (11, 20), [(13, T.GREEN), (19, T.GREEN)]),
            ("A shared total + lock", T.RED, "Workers update one variable under a mutex. Simple, but every worker queues for the same lock.",
             "ch04_wggo", (12, 20), [(14, T.RED), (15, T.RED), (16, T.RED)]),
        ]
        y = Y0
        for i, (t, col, d, ex, rng, hl) in enumerate(data):
            c = code_ex(ex, lines=rng, size=11, width=5.3, title=None, hl=hl)
            h = max(c.get_height() + 0.2, 1.55)
            bx = rbox(CW, h, color=col, fill=T.PANEL, radius=0.15, stroke_width=1.6)
            self.at(bx, X0, y)
            self.at(txt(f"**{t}**", size=17, color=col), X0 + 0.2, y - 0.15)
            dd = txt(d, size=13, color=T.TEXT2, width=2.35)
            self.at(dd, X0 + 0.2, y - 0.55)
            art = getattr(self, f"art{i}")(col)
            art.move_to(P(X0 + 3.65, y - h / 2 - 0.05))
            self.add(art)
            self.at(c, X0 + 4.95, y - 0.1)
            o = out(ex).split("\n")
            tm = terminal("\n".join(o[1:]), title=None, width=2.65, size=11)
            self.at(tm, X1 - 2.8, y - (h - tm.get_height()) / 2)
            y -= h + 0.12

    def art0(self, col):
        cells = slots_row(4, cell=0.36, color=col, items=[msg(s, T.PINK, s=0.26, size=10) for s in ("GO", "CH", "SE", "MU")])
        gs = VGroup(*[gtok(f"G{i}", w=0.36, h=0.2, eyes=False, size=9) for i in range(4)])
        for g_, c in zip(gs, cells.cells):
            g_.next_to(c, UP, buff=0.18)
        return VGroup(cells, gs, *[arrow(g_.get_bottom(), c.get_top(), T.TEXT2, 1.4, 0.02) for g_, c in zip(gs, cells.cells)])

    def art1(self, col):
        gs = VGroup(*[gtok(f"W{i}", w=0.42, h=0.22, eyes=False, size=9) for i in range(3)]).arrange(DOWN, buff=0.06)
        p = chan_pipe(2, ["r"], cell=0.32).next_to(gs, RIGHT, buff=0.25)
        m = gtok("main", w=0.6, h=0.26, size=10).next_to(p, RIGHT, buff=0.2)
        return VGroup(gs, p, m, *[arrow(g_.get_right(), p.get_left(), T.TEXT2, 1.3, 0.02) for g_ in gs],
                      arrow(p.get_right(), m.get_left(), T.TEXT2, 1.4, 0.02))

    def art2(self, col):
        gs = VGroup(*[gtok(f"G{i}", w=0.42, h=0.22, eyes=False, size=9) for i in range(3)]).arrange(DOWN, buff=0.06)
        box = rbox(0.75, 0.42, color=col, fill=T.PINK, fill_opacity=0.15).next_to(gs, RIGHT, buff=0.5)
        bt = txt("**sum**", size=12, color=T.PINK).move_to(box)
        lk = lock_icon(s=0.22).next_to(box, UP, buff=0.03)
        return VGroup(gs, box, bt, lk, *[arrow(g_.get_right(), box.get_left(), T.TEXT2, 1.3, 0.02) for g_ in gs])


class C4Errgroup(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "errgroup: wait, fail fast, cancel the rest"
    SUB = "`golang.org/x/sync/errgroup` adds three things a WaitGroup lacks: the first error, a context that is cancelled on failure, and a concurrency limit."

    def build(self):
        cd = code_ex("ch04_errgroup", lines=(12, 35), size=12, hl=[14, 15, 21, (28, T.GREEN), (29, T.GREEN), 31, 33],
                     marks={21: "1", 28: "2", 29: "3", 33: "4"})
        self.at(cd, X0, Y0)
        x = cd.get_right()[0] + 0.45
        w = X1 - x
        tm = terminal(out("ch04_errgroup"), title="one possible output", width=w, size=13)
        self.at(tm, x, Y0)
        # timeline
        y = tm.get_bottom()[1] - 0.35
        x0 = x + 0.55
        unit = (X1 - x0 - 0.1) / 240  # ms
        jobs = [(1, 0, 40, "ok"), (2, 0, 80, "ok"), (3, 0, 100, "err"), (4, 0, 100, "cancel"), (5, 40, 100, "cancel"), (6, 80, 100, "cancel")]
        planned = {4: 160, 5: 240, 6: 320}
        for i, (j, s, e, kind) in enumerate(jobs):
            yy = y - i * 0.27
            self.add(txt(f"{j}", size=12, color=T.MUTED, weight="BOLD").move_to(P(x0 - 0.12, yy), aligned_edge=RIGHT))
            col = {"ok": T.GREEN, "err": T.RED, "cancel": T.GREY}[kind]
            self.add(seg(x0 + s * unit, x0 + e * unit, yy, col, h=0.22))
            if j in planned:
                self.add(seg(x0 + e * unit, x0 + min(planned[j], 240) * unit, yy, T.GREY, h=0.22, outline=True))
        cut = dashed(P(x0 + 100 * unit, y + 0.2), P(x0 + 100 * unit, y - 1.55), T.RED, 2)
        self.add(cut, txt("job 3 fails at 100 ms:\nctx is cancelled", size=12, color=T.RED).move_to(P(x0 + 103 * unit, y + 0.05), aligned_edge=UL).shift(RIGHT * 0.05))
        self.add(time_axis(x0, X1, y - 1.62, ticks=[(x0 + t * unit, f"{t}") for t in (0, 40, 80, 120, 160, 200)], lab="ms"))
        leg = legend_row([(rbox(0.25, 0.16, color=T.GREEN, fill=T.GREEN), "done"), (rbox(0.25, 0.16, color=T.RED, fill=T.RED), "error"),
                          (rbox(0.25, 0.16, color=T.GREY, fill=T.GREY), "cancelled"), (rbox(0.25, 0.16, color=T.GREY, fill=T.GREY, fill_opacity=0.15), "never ran")], size=12, buff=0.2)
        self.at(leg, x, y - 2.05)
        api = bullets([(badge("1", T.YELLOW, r=0.11, size=11), "each task watches `ctx.Done()` and returns early"),
                       (badge("2", T.YELLOW, r=0.11, size=11), "`WithContext`: ctx is cancelled on the first error"),
                       (badge("3", T.YELLOW, r=0.11, size=11), "`SetLimit(4)`: `g.Go` blocks while 4 tasks run"),
                       (badge("4", T.YELLOW, r=0.11, size=11), "`Wait` returns the **first** non-nil error")],
                      width=w, size=13, gap=0.05)
        self.at(api, x, leg.get_bottom()[1] - 0.15)


class C4Choose(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Which waiting tool do I need?"
    SUB = "Follow the questions from the top left. Each answer is the simplest tool that does the job."

    def build(self):
        q1 = diamond("Only need to know when all are done?", w=3.2, h=1.25).move_to(P(-4.3, 1.3))
        a1 = node("`sync.WaitGroup`  (`wg.Go`)", w=3.0, h=0.62, color=T.GO).move_to(P(-4.3, -0.4))
        q2 = diamond("Do the tasks return errors?", w=3.0, h=1.15).move_to(P(-0.5, 1.3))
        a5 = node("a results channel, or one slot per task", w=3.2, h=0.7, color=T.PINK).move_to(P(3.75, 1.3))
        q3 = diamond("Stop the others on the first error?", w=3.1, h=1.2).move_to(P(-0.5, -0.6))
        a3 = node("`errgroup.WithContext`", w=2.9, h=0.62, color=T.GREEN).move_to(P(-0.5, -2.3))
        a2 = node("`errgroup.Group`, or collect a `[]error`", w=3.2, h=0.7, color=T.TEAL).move_to(P(3.75, -0.6))
        m = node("Too many tasks at once? add `g.SetLimit(n)` or a semaphore (8.15)", w=3.4, h=0.95, color=T.AMBER,
                 size=13).move_to(P(3.75, -2.3))
        for mo in (q1, a1, q2, a5, q3, a3, a2, m):
            self.add(mo)

        def go_(a, b, col, s, side=LEFT):
            ar = arrow(a, b, col, 2.5)
            self.add(ar, txt(f"**{s}**", size=13, color=col).next_to(ar, side, buff=0.08))
        go_(q1.get_bottom(), a1.get_top(), T.GREEN, "yes")
        go_(q1.get_right(), q2.get_left(), T.RED, "no", UP)
        go_(q2.get_right(), a5.get_left(), T.RED, "no", UP)
        go_(q2.get_bottom(), q3.get_top(), T.GREEN, "yes")
        go_(q3.get_bottom(), a3.get_top(), T.GREEN, "yes")
        go_(q3.get_right(), a2.get_left(), T.RED, "no", UP)
        self.add(dashed_arrow(a2.get_bottom(), m.get_top(), T.AMBER, 2.2))
        self.add(dashed_arrow(a3.get_right(), m.get_left(), T.AMBER, 2.2))
        side = callout("tip", "**One signal, many listeners?** Close a `done` channel: every receiver wakes at once. "
                       "This is how `context` cancellation works inside (8.14).", width=4.3, size=14)
        self.at(side, X0, -1.15)
        note = callout("note", "WaitGroup and errgroup both wait for **goroutines you started**. To wait for an "
                       "event (a value, a deadline), use a channel and `select` (8.8).", width=4.3, size=14)
        self.at(note, X0, side.get_bottom()[1] - 0.15)


class C4Recap(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Recap and check yourself"
    SUB = "Waiting is synchronisation too: get it wrong and the program either exits early or hangs."

    def build(self):
        self.at(section("REMEMBER", T.GO), X0, Y0)
        rec = bullets([
            "`Add` before `go`, `defer Done()` inside, `Wait` in the parent. Or use `wg.Go` (Go 1.25+).",
            "Never copy a WaitGroup; `go vet` reports \"passes lock by value\".",
            "A WaitGroup carries no data: use a slot per goroutine, a channel, or a locked aggregate.",
            "`errgroup.WithContext` returns the first error and cancels the siblings' context.",
            "`g.SetLimit(n)` caps how many tasks run at once; `g.Go` blocks when the limit is reached.",
        ], width=6.0, size=16, marker="check", marker_color=T.GREEN, gap=0.16)
        self.at(rec, X0, Y0 - 0.5)
        x = 0.55
        self.at(section("CHECK YOURSELF", T.TEAL), x, Y0)
        qs = [("Why does calling `wg.Add(1)` inside the new goroutine sometimes work in tests?",
               "Luck: the goroutines ran before `Wait`. On a loaded machine `Wait` sees 0 and returns early."),
              ("Ten goroutines append to one shared slice under a WaitGroup. Is it safe?",
               "No. `append` reads and writes the slice header: that is a data race. Use slots, a channel or a mutex."),
              ("errgroup task 2 fails while task 5 is blocked in a database call that ignores ctx. When does Wait return?",
               "Only after task 5 finishes: cancellation is cooperative, so pass ctx all the way down."),
              ("What does `wg.Go` do if f panics?", "It re-panics without calling Done, so the program crashes.")]
        y = Y0 - 0.5
        for i, (q, a) in enumerate(qs):
            grp = vstack(txt(f"**Q{i + 1}.** {q}", size=15, color=T.TEXT, width=6.0),
                         txt(f"{{teal|**Answer.**}} {a}", size=14, color=T.TEXT2, width=6.0), buff=0.08)
            self.at(grp, x, y)
            y = grp.get_bottom()[1] - 0.28
        g = gopher(1.0, mood="sleep").move_to(P(X0 + 0.9, -2.8))
        b = bubble("Wake me when the counter hits zero.", width=3.4, tail="left", tail_x=-0.1)
        b.next_to(g, RIGHT, buff=0.35)
        self.add(g, b)
