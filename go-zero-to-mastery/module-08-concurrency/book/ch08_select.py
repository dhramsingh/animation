from kit import *

CH, NAME = "8.8", "select and Timers"


class C8Opener(Opener):
    NUM, NAME = CH, NAME
    TAGLINE = "`select` waits on several channel operations at once and proceeds with whichever is ready first. It is how Go programs do timeouts, cancellation and non-blocking I/O."
    LEARN = ["State the six rules of `select`",
             "Add timeouts, and try-send / try-receive with `default`",
             "Disable cases with nil channels",
             "Measure select's fairness and add priorities yourself",
             "Explain selectgo's three passes, and Go 1.23's timers"]
    QUESTION = "Two channels are ready at the same instant. Which case does select pick, and may you rely on it?"

    def art(self):
        g = VGroup()
        hub = gopher(1.5, look=(0.0, 0.6), mood="think").move_to(P(2.4, -0.2))
        g.add(hub, txt("**select**", size=18, color=T.GO).next_to(hub, DOWN, buff=0.1))
        cases = [("<-results", T.GREEN, 1.8), ("<-time.After(1s)", T.BLUE, 0.3), ("<-ctx.Done()", T.AMBER, -1.2), ("default", T.GREY, -2.5)]
        for lab, col, y in cases:
            p = chan_pipe(2, ["v"] if col == T.GREEN else [], cell=0.36, color=col).move_to(P(5.3, y))
            a = arrow(hub.get_right() + P(0.05, 0.2), p.get_left(), col, 2.3, 0.05)
            t = mono(lab, size=14, color=col).next_to(p, UP, buff=0.08)
            if lab == "default":
                p = node("default", w=1.4, h=0.45, color=T.GREY, size=13).move_to(P(5.3, y))
                a = dashed_arrow(hub.get_right() + P(0.05, -0.2), p.get_left(), T.GREY, 2)
                t = VectorizedPoint()
            g.add(a, p, t)
        g.add(check_mark(T.GREEN, 0.2).next_to(g[3], RIGHT, buff=0.15))
        return g


class C8Rules(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "select: proceed with the first ready operation"
    SUB = "A select statement lists channel sends and receives. It runs exactly one of them, and blocks only if none can proceed."

    def build(self):
        cd = code('''select {
case v := <-in:             // a receive
    use(v)
case out <- result:         // a send
    sent++
case <-time.After(time.Second):
    timeout()               // a receive from a timer
default:                    // optional: never block
    idle()
}''', size=15, title="the shape of select", hl=[2, 4, 6, (8, T.GREY)], numbers=False)
        self.at(cd, X0, Y0)
        rules = num_steps([("Evaluate", "every channel expression and every value to send, once, top to bottom, before anything else."),
                           ("Choose", "if one or more cases can proceed, pick **one at random**, uniformly."),
                           ("Default", "if none can proceed and there is a `default`, run it immediately."),
                           ("Block", "otherwise wait until any case can proceed, then run that one."),
                           ("Nil", "a case on a nil channel can never proceed (it is ignored)."),
                           ("Empty", "`select {}` has no cases and blocks forever.")],
                          width=X1 - cd.get_right()[0] - 0.55, color=T.GO, size=15, gap=0.14)
        self.at(rules, cd.get_right()[0] + 0.55, Y0)
        w2 = callout("warn", "Rule 1 bites: `case out <- expensive():` calls `expensive()` **every time** the select runs, "
                     "even if another case wins. Likewise `time.After(...)` creates a new timer on each loop iteration.",
                     width=cd.get_width(), size=14)
        self.at(w2, X0, cd.get_bottom()[1] - 0.3)
        k = callout("key", "`select` is a **switch for communication**: cases are channel operations, and the order "
                    "they are written in means nothing.", width=cd.get_width(), size=14)
        self.at(k, X0, w2.get_bottom()[1] - 0.18)


class C8Timeout(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Timeouts: race the work against a timer"
    SUB = "Put the result channel and a timer channel in the same select. Whichever is ready first wins."

    def build(self):
        cd = code_ex("ch08_timeout", lines=(8, 27), size=14, hl=[(9, T.GREEN), 21, (23, T.BLUE)], marks={9: "1", 21: "2", 23: "3"})
        self.at(cd, X0, Y0)
        tm = terminal(out("ch08_timeout"), title="output", width=cd.get_width(), size=14)
        self.at(tm, X0, cd.get_bottom()[1] - 0.15)
        x = cd.get_right()[0] + 0.55
        w = X1 - x
        x0 = x + 0.9
        unit = (X1 - x0 - 0.1) / 320
        for k, (dur, lab) in enumerate(((50, "query 50 ms"), (300, "query 300 ms"))):
            y = Y0 - 0.4 - k * 1.55
            self.add(txt(f"**run {k + 1}**", size=14, color=T.TEXT).move_to(P(x, y + 0.15), aligned_edge=LEFT))
            self.add(txt("work", size=12, color=T.MUTED).move_to(P(x0 - 0.1, y - 0.25), aligned_edge=RIGHT))
            self.add(txt("timer", size=12, color=T.MUTED).move_to(P(x0 - 0.1, y - 0.65), aligned_edge=RIGHT))
            self.add(seg(x0, x0 + dur * unit, y - 0.25, T.GREEN, h=0.26, lab=lab, size=11))
            self.add(seg(x0, x0 + 100 * unit, y - 0.65, T.BLUE, h=0.26, lab="100 ms", size=11))
            win_x = x0 + min(dur, 100) * unit
            self.add(dashed(P(win_x, y + 0.05), P(win_x, y - 0.85), T.YELLOW, 2))
            self.add(txt("result wins" if dur < 100 else "timeout wins", size=13, color=T.YELLOW, weight="BOLD").move_to(P(win_x + 0.1, y + 0.12), aligned_edge=LEFT))
        self.add(time_axis(x0, X1, Y0 - 3.35, ticks=[(x0 + t * unit, f"{t}") for t in (0, 100, 200, 300)], lab="ms"))
        notes = bullets([(badge("1", T.YELLOW, r=0.11, size=11), "capacity **1**: if the timeout wins, the late send still succeeds and the goroutine exits (no leak, see 8.17)"),
                         (badge("2", T.YELLOW, r=0.11, size=11), "`slowQuery(d)` runs when the select is evaluated (rule 1)"),
                         (badge("3", T.YELLOW, r=0.11, size=11), "`time.After` returns a channel that receives once, after the duration")],
                        width=w, size=13, gap=0.06)
        self.at(notes, x, Y0 - 3.95)
        t = callout("tip", "In servers use `context.WithTimeout` and `case <-ctx.Done():` instead: the deadline then flows to everything the request calls (8.14).",
                    width=w, size=13, inline=True)
        self.at(t, x, notes.get_bottom()[1] - 0.15)


class C8NonBlocking(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Non-blocking operations: select with default"
    SUB = "With a `default` case, select never waits. That gives you try-send and try-receive."

    def build(self):
        cd = code_ex("ch08_nonblocking", lines=(5, 23), size=13, hl=[10, (12, T.GREY), 18, (20, T.GREY)])
        self.at(cd, X0, Y0)
        tm = terminal(out("ch08_nonblocking"), title="output", width=cd.get_width(), size=13)
        self.at(tm, X0, cd.get_bottom()[1] - 0.15)
        x = cd.get_right()[0] + 0.55
        w = X1 - x
        # drawing: event 1 queued, 2 and 3 dropped
        y = Y0 - 0.55
        p = chan_pipe(1, ["e1"], cell=0.55).move_to(P(x + w / 2 + 0.5, y))
        self.add(p, txt("events (cap 1)", size=12, color=T.GREEN).next_to(p, UP, buff=0.1))
        src = gtok("producer", w=1.3, h=0.36).move_to(P(x + 0.7, y))
        self.add(src, arrow(src.get_right(), p.get_left(), T.GREEN, 2.3))
        for k, ev in enumerate(("e2", "e3")):
            m = msg(ev, T.PINK, s=0.4, size=11).move_to(P(x + 1.8 + 0.8 * k, y - 0.9))
            self.add(m, cross_mark(T.RED, 0.1).next_to(m, RIGHT, buff=0.05))
        self.add(txt("dropped: the channel was full, and default ran", size=12, color=T.RED).move_to(P(x + 0.3, y - 1.4), aligned_edge=LEFT))
        uses = bullets(["**Try-send**: publish a metric or event, but never stall the hot path.",
                        "**Try-receive**: poll for work while doing something else.",
                        "**Coalesce**: a capacity-1 \"something changed\" channel; extra signals merge into one."],
                       width=w, size=14, gap=0.1)
        self.at(section("WHEN TO USE IT", T.GO), x, y - 1.85)
        self.at(uses, x, y - 2.35)
        w2 = callout("warn", "A `for` loop around a select with `default` and no blocking case is a **busy loop**: it burns a whole core doing nothing. "
                     "If you must wait, drop the `default`.", width=w, size=13)
        self.at(w2, x, uses.get_bottom()[1] - 0.2)


class C8NilTrick(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Switching cases off with nil channels"
    SUB = "A receive from a closed channel is always ready, which would spin. Setting the variable to nil disables that case for good."

    def build(self):
        cd = code_ex("ch08_merge_nil", lines=(16, 37), size=13, hl=[18, (22, T.AMBER), (29, T.AMBER)], marks={18: "1", 22: "2"})
        self.at(cd, X0, Y0)
        x = cd.get_right()[0] + 0.5
        w = X1 - x
        tm = terminal(out("ch08_merge_nil"), title="one possible output", width=w, size=13)
        self.at(tm, x, Y0)
        y = tm.get_bottom()[1] - 0.35
        stages = [("both open", [("a", T.GREEN, True), ("b", T.GREEN, True)]),
                  ("b closed → b = nil", [("a", T.GREEN, True), ("b", T.GREY, False)]),
                  ("a closed → a = nil: loop ends", [("a", T.GREY, False), ("b", T.GREY, False)])]
        for i, (t, chans) in enumerate(stages):
            yy = y - i * 0.5
            self.add(txt(t, size=13, color=T.TEXT2).move_to(P(x, yy), aligned_edge=LEFT))
            for j, (n, col, on) in enumerate(chans):
                c = pill(f"case <-{n}", col, size=11, filled=on).move_to(P(x + 3.0 + j * 1.35, yy))
                self.add(c)
        notes = bullets([(badge("1", T.YELLOW, r=0.11, size=11), "loop until **both** inputs are finished"),
                         (badge("2", T.YELLOW, r=0.11, size=11), "a closed channel is always ready; a nil one never is")],
                        width=w, size=14, gap=0.06)
        self.at(notes, x, y - 1.35)
        k = callout("tip", "The same trick turns a send off: keep `var out chan<- T` nil until you have something to send "
                    "(the crawler coordinator in 8.19 does exactly this).", width=w, size=13)
        self.at(k, x, notes.get_bottom()[1] - 0.18)


class C8Fairness(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Is select fair? We measured it"
    SUB = "When several cases are ready, the runtime shuffles them before looking. Over 100,000 rounds with two always-ready channels:"

    def build(self):
        cd = code_ex("ch08_fairness", lines=(5, 23), size=14, hl=[10, 11, 12])
        self.at(cd, X0, Y0)
        tm = terminal(out("ch08_fairness"), title="output", width=cd.get_width(), size=14)
        self.at(tm, X0, cd.get_bottom()[1] - 0.15)
        a, b = nums("ch08_fairness", r"chosen: (\d+)", int)
        x = cd.get_right()[0] + 0.6
        w = X1 - x
        H = 1.55
        base = Y0 - 0.55 - H
        for i, (lab, v) in enumerate((("case a", a), ("case b", b))):
            cx = x + 1.2 + i * 2.0
            h = H * v / 55000
            bar = RoundedRectangle(width=1.0, height=h, corner_radius=0.06).set_fill(T.GO, 0.9).set_stroke(width=0)
            bar.move_to(P(cx, base + h / 2))
            self.add(bar, txt(f"**{v:,}**", size=16, color=T.TEXT).next_to(bar, UP, buff=0.08),
                     txt(lab, size=14, color=T.TEXT2).next_to(P(cx, base), DOWN, buff=0.12))
        half = base + H * 50000 / 55000
        self.add(dashed(P(x + 0.4, half), P(x + 4.0, half), T.YELLOW, 2), txt("50,000", size=12, color=T.YELLOW).move_to(P(x + 4.1, half), aligned_edge=LEFT))
        self.add(hline(x + 0.4, x + 4.0, base, T.STROKE2, 1.5))
        self.add(txt(f"difference: {abs(a - b) / 1000:.2f}%", size=13, color=T.TEXT2).move_to(P(x + 2.2, base - 0.55)))
        prio = code('''// priority: drain "urgent" before anything else
for {
    select {
    case u := <-urgent:
        handle(u)
        continue
    default:
    }
    select {
    case u := <-urgent:
        handle(u)
    case n := <-normal:
        handle(n)
    }
}''', size=11, title="there is no priority; build one", width=w, hl=[(4, T.AMBER), (10, T.AMBER)], numbers=False)
        self.at(prio, x, base - 0.8)


class C8Selectgo(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Under the hood: selectgo in three passes"
    SUB = "The compiler rewrites simple selects; the general case calls runtime.selectgo (runtime/select.go), which works like this."

    def build(self):
        pre = node("compiler: 0 cases → block forever;  1 case → a plain send/receive;  1 case + default → selectnbsend / selectnbrecv",
                   w=CW, h=0.55, color=T.VIOLET, size=13)
        self.at(pre, X0, Y0)
        steps = [("Shuffle", "build `pollorder`: a random permutation of the non-nil cases (cheaprandn)", T.GO),
                 ("Sort", "build `lockorder`: cases sorted by channel **address** (heap sort)", T.GO),
                 ("Lock", "lock every channel once, in lockorder", T.RED),
                 ("Pass 1", "walk pollorder; the first case that can proceed runs now; unlock all, return", T.GREEN),
                 ("Default?", "if the select has a default: unlock all and run it", T.GREY),
                 ("Pass 2", "enqueue a sudog (isSelect = true) on **every** channel, then gopark (unlocks all)", T.AMBER),
                 ("Woken", "some channel's partner picked one of our sudogs and readied us", T.BLUE),
                 ("Pass 3", "lock all again and remove our sudogs from the other channels' queues", T.AMBER)]
        y = Y0 - 0.85
        for i, (t, d, col) in enumerate(steps):
            n = node(t, w=1.35, h=0.48, color=col, size=13).move_to(P(X0 + 0.68, y - 0.24))
            dd = txt(d, size=13, color=T.TEXT2, width=5.6).move_to(P(X0 + 1.55, y - 0.24), aligned_edge=LEFT)
            self.add(n, dd)
            if i:
                self.add(arrow(P(X0 + 0.68, y + 0.1), P(X0 + 0.68, y), T.MUTED, 1.6, 0))
            y -= 0.6
        x = X0 + 7.6
        w = X1 - x
        self.at(section("PASS 2, DRAWN", T.AMBER), x, Y0 - 0.85)
        g = gopher(0.95, mood="sleep").move_to(P(x + 0.6, Y0 - 2.6))
        self.add(g, txt("G (parked)", size=12, color=T.MUTED).next_to(g, DOWN, buff=0.04))
        for k, (nm, col) in enumerate((("ch1", T.GREEN), ("ch2", T.GREEN), ("ch3", T.GREEN))):
            yy = Y0 - 1.6 - k * 0.95
            body = rbox(2.4, 0.62, color=col, fill=col, fill_opacity=0.08, radius=0.1).move_to(P(x + 3.6, yy))
            sg = rbox(0.75, 0.34, color=T.VIOLET, fill=T.VIOLET, fill_opacity=0.2, radius=0.06).move_to(body.get_center() + RIGHT * 0.6)
            self.add(body, txt(f"**{nm}**  recvq", size=12, color=col).move_to(body.get_left() + P(0.12, 0), aligned_edge=LEFT),
                     sg, txt("sudog", size=10, color=T.VIOLET).move_to(sg))
            self.add(dashed_arrow(g.get_right() + P(0.05, 0.25 - 0.25 * k), sg.get_left(), T.VIOLET, 1.6))
        expl = bullets(["The first channel to fire dequeues **its** sudog and wins; it marks the select as done so the others cannot also fire.",
                        "Address order makes two selects on the same channels lock them in the same order: no lock-ordering deadlock.",
                        "Cost grows with the number of cases: a select with 2 cases is cheap, one with 50 is not."],
                       width=w, size=13, gap=0.08)
        self.at(expl, x, Y0 - 4.1)


class C8Timers(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Timers and tickers"
    SUB = "Timers deliver one value after a delay; tickers deliver one per period. Since Go 1.23 both are simpler to use correctly."

    def build(self):
        api = table([["Call", "Gives you", "Use for"],
                     ["`time.After(d)`", "`<-chan Time`, fires once", "one-off timeouts in a select"],
                     ["`time.NewTimer(d)`", "`*Timer` with `.C`, `Stop`, `Reset`", "timeouts you reuse or cancel"],
                     ["`time.NewTicker(p)`", "`*Ticker` with `.C`, `Stop`, `Reset`", "periodic work, heartbeats"],
                     ["`time.AfterFunc(d, f)`", "runs `f` in its own goroutine", "callbacks, expiry (8.18 test)"]],
                    [2.35, 2.75, 2.45], size=13)
        self.at(api, X0, Y0)
        v = callout("version", "**Go 1.23** changed timers: (1) a Timer or Ticker that is no longer referenced is garbage collected "
                    "even if you never called `Stop`; (2) timer channels are now **unbuffered** (`cap(t.C) == 0`), so after "
                    "`Stop` or `Reset` no stale value can be received. Modules declaring `go 1.22` or older keep the old behaviour.",
                    width=api.get_width(), size=13)
        self.at(v, X0, api.get_bottom()[1] - 0.25)
        cd = code_ex("ch08_timer_reset", lines=(10, 19), size=13, width=api.get_width(), hl=[12, 14])
        self.at(cd, X0, v.get_bottom()[1] - 0.2)
        x = api.get_right()[0] + 0.5
        w = X1 - x
        tm1 = terminal(out("ch08_timer_reset"), title="ch08_timer_reset output", width=w, size=13)
        self.at(tm1, x, Y0)
        ck = code_ex("ch08_ticker", lines=(14, 23), size=12, width=w, hl=[16, 18])
        self.at(ck, x, tm1.get_bottom()[1] - 0.15)
        tm2 = terminal(out("ch08_ticker"), title="ch08_ticker output", width=w, size=12)
        self.at(tm2, x, ck.get_bottom()[1] - 0.12)


class C8ForSelect(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "The for-select loop: a goroutine's main loop"
    SUB = "Most long-lived goroutines are a `for` around a `select`: one case for work, one for periodic chores, one for being told to stop."

    def build(self):
        cd = code_ex("ch08_forselect", lines=(8, 27), size=14, hl=[(13, T.GREEN), (20, T.BLUE), (22, T.RED)], marks={13: ("1", T.GREEN), 20: ("2", T.BLUE), 22: ("3", T.RED)})
        self.at(cd, X0, Y0)
        x = cd.get_right()[0] + 0.55
        w = X1 - x
        tm = terminal(out("ch08_forselect"), title="output", width=w, size=13)
        self.at(tm, x, Y0)
        roles = bullets([(badge("1", T.GREEN, r=0.11, size=11), "**work**: a job, or `ok == false` when the producer is done"),
                         (badge("2", T.BLUE, r=0.11, size=11), "**chores**: heartbeats, flushing, metrics, on a ticker"),
                         (badge("3", T.RED, r=0.11, size=11), "**stop**: a done channel or `ctx.Done()`, so the goroutine never leaks")],
                        width=w, size=14, gap=0.1)
        self.at(roles, x, tm.get_bottom()[1] - 0.25)
        k = callout("rule", "Every goroutine you start needs a way to **end**. In a for-select loop that is a `return` "
                    "in the stop case (and in the closed-input case).", width=w, size=14)
        self.at(k, x, roles.get_bottom()[1] - 0.25)
        n = callout("note", "A job in progress is not interrupted: `select` only chooses between operations that are "
                    "ready **when it runs**. Long jobs should check ctx themselves.", width=w, size=13)
        self.at(n, x, k.get_bottom()[1] - 0.15)


class C8Recap(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Recap and check yourself"
    SUB = "select is Go's multiplexer: the place where timeouts, cancellation and back-pressure meet."

    def build(self):
        a, b = nums("ch08_fairness", r"chosen: (\d+)", int)
        self.at(section("REMEMBER", T.GO), X0, Y0)
        rec = bullets([
            "All case expressions are evaluated first; then one ready case runs, chosen at random.",
            "`default` makes it non-blocking; no ready case and no default means wait.",
            "nil channels never fire: set a variable to nil to switch its case off.",
            f"Fairness is statistical, not ordered: {a:,} vs {b:,} in our run. Build priorities explicitly.",
            "selectgo: shuffle, sort by address, lock all, pass 1, park on all (pass 2), clean up (pass 3).",
            "Go 1.23 timers: collected when unreferenced, unbuffered channels, no stale values after Reset.",
        ], width=6.0, size=15, marker="check", marker_color=T.GREEN, gap=0.14)
        self.at(rec, X0, Y0 - 0.5)
        x = 0.55
        self.at(section("CHECK YOURSELF", T.TEAL), x, Y0)
        qs = [("A select has cases on two closed channels inside a for loop. What goes wrong?",
               "Both are always ready: the loop spins at full CPU. Set each to nil once it is drained."),
              ("Does case order inside a select give priority?", "No. Ready cases are chosen uniformly at random."),
              ("Why does the timeout example use `make(chan string, 1)`?",
               "So the late sender can complete its send and exit after the timeout wins; otherwise it leaks."),
              ("What does `select {}` do, and when is it useful?",
               "Blocks forever; e.g. at the end of main in a program whose work happens in other goroutines.")]
        y = Y0 - 0.5
        for i, (q, a_) in enumerate(qs):
            grp = vstack(txt(f"**Q{i + 1}.** {q}", size=15, color=T.TEXT, width=6.0),
                         txt(f"{{teal|**Answer.**}} {a_}", size=14, color=T.TEXT2, width=6.0), buff=0.08)
            self.at(grp, x, y)
            y = grp.get_bottom()[1] - 0.28
