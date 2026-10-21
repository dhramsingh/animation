from kit import *

CH, NAME = "8.12", "Sharing Memory: sync and atomics"

GOT = nums("ch12_race_counter", r"got (\d+)", int)[0]
LOST = 1_000_000 - GOT
G1C, G2C = T.GO, T.ORANGE


def _bench():
    """{name: (ns_1_goroutine, ns_4_goroutines)} from the ch12_bench output."""
    text = (EX_DIR / "ch12_bench" / "output.txt").read_text()
    r = {}
    for name, par, ns in re.findall(r"Benchmark(\w+?)(-4)?\s+\d+\s+([\d.]+) ns/op", text):
        r.setdefault(name, [0.0, 0.0])[1 if par else 0] = float(ns)
    return r


def _pool():
    text = (EX_DIR / "ch12_pool" / "output.txt").read_text()
    rows = re.findall(r"Benchmark(\w+?)-\d+\s+\d+\s+([\d.]+) ns/op\s+(\d+) B/op\s+(\d+) allocs/op", text)
    return {n: (float(a), int(b), int(c)) for n, a, b, c in rows}


class C12Opener(Opener):
    NUM, NAME = CH, NAME
    TAGLINE = "Channels move data between goroutines. Sometimes the data must stay put and many goroutines must touch it. The sync and sync/atomic packages make that safe."
    LEARN = ["Explain why `counter++` loses updates under concurrency",
             "Guard state with `Mutex` and `RWMutex`, and know their rules",
             "Look inside the Mutex: fast path, spinning, starvation mode",
             "Use `Once`, `OnceValue`, `Cond`, `Pool` and `sync.Map` correctly",
             "Write lock-free code with atomics, and pick the right tool"]
    QUESTION = (f"1,000 goroutines each add 1 to a shared counter 1,000 times. We expect 1,000,000; "
                f"one run printed {GOT:,}. Where did the other {LOST:,} increments go?")

    def art(self):
        g = VGroup()
        cell = node("counter = 41", w=2.6, h=0.75, color=T.YELLOW, size=20).move_to(P(3.6, 1.55))
        g.add(cell, txt("shared memory", size=13, color=T.MUTED).next_to(cell, UP, buff=0.1))
        a = gopher(1.35, mood="run", look=(0.3, 0.3)).move_to(P(1.75, -0.25))
        b = gopher(1.35, mood="run", look=(-0.3, 0.3)).move_to(P(5.45, -0.25))
        g.add(a, b)
        g.add(txt("**G1**", size=15, color=G1C).next_to(a, DOWN, buff=0.08))
        g.add(txt("**G2**", size=15, color=G2C).next_to(b, DOWN, buff=0.08))
        g.add(arrow(a.get_top() + RIGHT * 0.2, cell.get_bottom() + LEFT * 0.7, G1C, 3, 0.08))
        g.add(arrow(b.get_top() + LEFT * 0.2, cell.get_bottom() + RIGHT * 0.7, G2C, 3, 0.08))
        g.add(txt("read 41, write 42", size=14, color=G1C, font=T.MONO).move_to(P(1.65, 0.85)))
        g.add(txt("read 41, write 42", size=14, color=G2C, font=T.MONO).move_to(P(5.55, 0.85)))
        res = node("after both: 42, not 43", w=3.4, h=0.6, color=T.RED, size=16).move_to(P(3.6, -1.75))
        g.add(res)
        lk = lock_icon(T.GREEN, s=0.42).move_to(P(2.0, -2.65))
        g.add(lk, txt("a lock or an atomic makes each\nread-add-write indivisible", size=14, color=T.GREEN)
              .next_to(lk, RIGHT, buff=0.18))
        return g


class C12Race(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "counter++ is three steps, not one"
    SUB = "An increment reads the value, adds one and writes it back. Two goroutines can interleave those steps, and one update silently disappears."

    def build(self):
        w = 6.25
        cd = code_ex("ch12_race_counter", lines=(8, 20), size=14, width=w, hl=[(14, T.RED)], marks={14: "!"})
        self.at(cd, X0, Y0)
        tm = terminal(out("ch12_race_counter"), title="go run . (the result changes every run)", width=w, size=14)
        self.at(tm, X0, cd.get_bottom()[1] - 0.15)
        hood = callout("hood", "On amd64 the compiler turns `*p++` into one instruction, `INCQ (AX)`. It is still a "
                       "read, an add and a write inside the core, and without a LOCK prefix another core can use the "
                       "same memory in between. To Go it is a **data race**: no result is promised at all (8.13).",
                       width=w, size=13, title="EVEN ONE INSTRUCTION IS NOT ATOMIC")
        self.at(hood, X0, tm.get_bottom()[1] - 0.2)

        # interleaving diagram
        x = X0 + w + 0.4
        cols = [(0.38, None), (2.3, ("G1 on core 1", G1C)), (1.2, ("counter", T.YELLOW)), (2.3, ("G2 on core 2", G2C))]
        xs, cx = [], x
        for cw_, _ in cols:
            xs.append(cx + cw_ / 2)
            cx += cw_ + 0.1
        y = Y0 - 0.15
        for (cw_, hd), xc in zip(cols, xs):
            if hd:
                self.add(txt(f"**{hd[0]}**", size=14, color=hd[1]).move_to(P(xc, y)))
        rows = [(1, "load  r1 = 41", None, "41"), (2, None, "load  r2 = 41", "41"),
                (3, "add   r1 = 42", None, "41"), (4, None, "add   r2 = 42", "41"),
                (5, "store r1 → 42", None, "42"), (6, None, "store r2 → 42", "42")]
        step = 0.47
        for i, (n, a, b, m) in enumerate(rows):
            yy = y - 0.5 - i * step
            self.add(badge(str(n), T.MUTED, r=0.14, size=12).move_to(P(xs[0], yy)))
            if a:
                self.add(node(a, w=2.3, h=0.38, color=G1C, size=13).move_to(P(xs[1], yy)))
            if b:
                c = T.RED if n == 6 else G2C
                self.add(node(b, w=2.3, h=0.38, color=c, size=13).move_to(P(xs[3], yy)))
            mc = T.RED if n == 6 else (T.YELLOW)
            self.add(node(m, w=0.9, h=0.38, color=mc, size=15, fill_opacity=0.2 if n >= 5 else 0.08).move_to(P(xs[2], yy)))
        ybot = y - 0.5 - 5 * step - 0.3
        self.add(arrow(P(xs[3] + 1.0, ybot + 0.05), P(xs[3] + 1.0, ybot - 0.25), T.RED, 2, 0))
        lost = callout("warn", f"Two increments ran, but the counter moved 41 → 42 **once**. G2 overwrote G1's "
                       f"result with a value computed from a stale read: a **lost update**. In the run above, "
                       f"{LOST:,} of 1,000,000 updates were lost this way.",
                       width=X1 - x, size=13, title="LOST UPDATE")
        self.at(lost, x, ybot - 0.3)
        k = callout("key", "Steps 1-3 and 5 must happen as one indivisible unit. A **mutex** makes the "
                    "whole block exclusive; an **atomic** makes the single operation indivisible in hardware.",
                    width=X1 - x, size=13)
        self.at(k, x, lost.get_bottom()[1] - 0.2)


class C12Mutex(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "sync.Mutex: one goroutine at a time"
    SUB = "A mutex (mutual exclusion lock) guards a critical section: the code between Lock and Unlock runs in at most one goroutine at any moment."

    def build(self):
        w = 6.25
        cd = code_ex("ch12_mutex_counter", lines=(8, 17), size=14, width=w, hl=[9, 14, 15, 16],
                     marks={9: "1", 14: "2", 15: "3", 16: "4"})
        self.at(cd, X0, Y0)
        st = num_steps([("Pair the lock with its data.", "The zero `sync.Mutex` is unlocked and ready; no constructor."),
                        ("Lock.", "If another goroutine holds it, this one sleeps until it is free."),
                        ("defer Unlock.", "Runs on every return path, even during a panic."),
                        ("Critical section.", "Only the holder runs here, so the read-add-write cannot interleave.")],
                       width=w, color=T.RED, size=13, gap=0.08)
        self.at(st, X0, cd.get_bottom()[1] - 0.2)
        tm = terminal(out("ch12_mutex_counter"), title="same 1,000 × 1,000 loop, now calling c.Inc()", width=w, size=13)
        self.at(tm, X0, st.get_bottom()[1] - 0.2)

        # the room
        x = X0 + w + 0.45
        room = rbox(3.3, 2.2, color=T.RED, fill=T.RED, fill_opacity=0.06, radius=0.2)
        room.move_to(P(x + 1.6 + 1.65, Y0 - 1.35))
        self.add(room, txt("**critical section**", size=14, color=T.RED).move_to(room.get_top() + DOWN * 0.25))
        gin = gtok("G1", G1C, w=0.9, h=0.44, state="run").move_to(room.get_center() + UP * 0.05)
        self.add(gin, mono("c.n++", size=15, color=T.YELLOW).next_to(gin, DOWN, buff=0.15))
        lk = lock_icon(T.RED, s=0.42).move_to(room.get_left() + UP * 0.1)
        self.add(lk)
        for i, lab in enumerate(("G2", "G3", "G4")):
            t = gtok(lab, T.GREY, w=0.9, h=0.44, state="wait").move_to(P(x + 0.55, room.get_top()[1] - 0.45 - i * 0.62))
            self.add(t)
        self.add(txt("blocked in Lock(),\nasleep, no CPU used", size=12, color=T.TEXT2, align="CENTER")
                 .move_to(P(x + 0.55, room.get_bottom()[1] - 0.35)))
        self.add(arrow(P(x + 1.05, Y0 - 1.25), lk.get_left() + LEFT * 0.05, T.MUTED, 2, 0.04))
        out_ = arrow(room.get_right() + DOWN * 0.3, room.get_right() + DOWN * 0.3 + RIGHT * 0.75, T.GREEN, 2.4, 0)
        self.add(out_)
        ex = txt("Unlock():\nnext waiter\nmay enter", size=12, color=T.GREEN).next_to(out_, UP, buff=0.1)
        self.add(ex)
        ybot = room.get_bottom()[1] - 0.6
        k = callout("key", "Locking gives two guarantees: **exclusion** (one holder at a time) and **visibility**: "
                    "whatever the previous holder wrote before Unlock is seen by the next holder after Lock. "
                    "That second half is the Go memory model's happens-before (8.13).",
                    width=X1 - x, size=13)
        self.at(k, x, ybot)
        tip = callout("tip", "Keep critical sections short: compute outside, lock, update, unlock. Never "
                      "block on I/O or a channel while holding a lock if you can avoid it.",
                      width=X1 - x, size=13)
        self.at(tip, x, k.get_bottom()[1] - 0.2)


class C12MutexRules(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Mutex rules that prevent real bugs"
    SUB = "A mutex is simple to call and easy to misuse. These rules come straight from the sync docs and the vet checks."

    def build(self):
        w = 6.25
        cd = code_ex("ch12_copylock", lines=(8, 24), size=14, width=w, hl=[(14, T.RED), (16, T.RED)],
                     marks={14: "!"})
        self.at(cd, X0, Y0)
        tm = terminal(out("ch12_copylock"), title="go vet (copylocks analyzer)", width=w, size=13)
        self.at(tm, X0, cd.get_bottom()[1] - 0.15)
        fix = callout("tip", "**Fix**: use a pointer receiver, `func (c *Counter) Inc()`. Every method on a type that "
                      "contains a lock should take a pointer, and the value must never be copied after first use. "
                      "The program above prints `n = 0`.", width=X1 - X0 - w - 0.45, size=13)
        x = X0 + w + 0.45
        ww = X1 - x
        self.at(section("DO", T.GREEN), x, Y0)
        do = bullets(["Lock, then `defer mu.Unlock()` on the very next line.",
                      "Put the mutex right above the fields it guards and say so in a comment.",
                      "Use pointer receivers; let `go vet` catch accidental copies.",
                      "Hold the lock for as little work as possible.",
                      "Always take several locks in one fixed global order."],
                     width=ww, size=14, marker="check", marker_color=T.GREEN, gap=0.1)
        self.at(do, x, Y0 - 0.45)
        y = do.get_bottom()[1] - 0.25
        self.at(section("DON'T", T.RED), x, y)
        dont = bullets(["Lock twice in one goroutine: Go mutexes are **not re-entrant**, the second Lock waits forever.",
                        "Unlock an unlocked mutex: fatal error \"sync: unlock of unlocked mutex\". `recover` cannot catch it.",
                        "Call unknown code (callbacks, interface methods) while holding the lock.",
                        "Rely on `TryLock` (Go 1.18): the docs say correct uses are rare.",
                        "Assume a lock belongs to a goroutine: any goroutine may Unlock it (legal, rarely clear)."],
                       width=ww, size=14, marker="cross", marker_color=T.RED, gap=0.1)
        self.at(dont, x, y - 0.45)
        self.at(fix, x, dont.get_bottom()[1] - 0.3)


class C12MutexHood(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Inside sync.Mutex: one word of state, a smart slow path"
    SUB = "The whole lock is 8 bytes. The uncontended case is a single atomic instruction; contention takes a slower, fairer path."

    def build(self):
        w = 6.3
        st = code('''type Mutex struct {
    state int32  // flags + number of waiters
    sema  uint32 // where sleeping waiters park
}''', size=14, title="internal/sync/mutex.go", width=w, numbers=False)
        self.at(st, X0, Y0)
        # bit layout
        y = st.get_bottom()[1] - 0.5
        parts = [("waiter count", "31 … 3", 3.3, T.GREY), ("starving", "2", 1.0, T.RED),
                 ("woken", "1", 1.0, T.YELLOW), ("locked", "0", 1.0, T.GREEN)]
        xx = X0
        for lab, bits, ww, col in parts:
            r = rbox(ww - 0.05, 0.5, color=col, fill=col, fill_opacity=0.18, radius=0.06)
            r.move_to(P(xx + ww / 2, y))
            self.add(r, txt(f"**{lab}**", size=13, color=col).move_to(r))
            self.add(txt(f"bit {bits}", size=11, color=T.MUTED, font=T.MONO).next_to(r, UP, buff=0.06))
            xx += ww
        self.add(txt("state (int32)", size=12, color=T.TEXT2).next_to(P(X0 + 6.3, y), RIGHT, buff=0.1).shift(LEFT * 6.3 + DOWN * 0.45))
        # flow
        fy = y - 0.75
        n1 = node("Lock(): CAS state 0 → locked", w=3.2, h=0.5, color=T.GREEN, size=13)
        self.at(n1, X0, fy)
        ok = node("got it: fast path, inlined", w=2.85, h=0.5, color=T.GREEN, size=13, fill_opacity=0.25)
        self.at(ok, X0 + 3.45, fy)
        self.add(connect(n1, ok, T.GREEN, 2.2), txt("ok", size=11, color=T.GREEN).move_to(P(X0 + 3.32, fy + 0.08)))
        n2 = node("spin: up to 4 × 30 PAUSE", w=3.2, h=0.5, color=T.YELLOW, size=13)
        self.at(n2, X0, fy - 0.72)
        self.add(connect(n1, n2, T.MUTED, 2.2), txt("held", size=11, color=T.MUTED).move_to(P(X0 + 1.95, fy - 0.61)))
        sp = txt("only if multicore, other Ps busy and this P's run queue empty: the holder may release within nanoseconds",
                 size=12, color=T.TEXT2, width=2.85)
        self.at(sp, X0 + 3.45, fy - 0.66)
        n3 = node("waiters++; sleep on sema", w=3.2, h=0.5, color=T.RED, size=13)
        self.at(n3, X0, fy - 1.44)
        self.add(connect(n2, n3, T.MUTED, 2.2))
        n4 = node("Unlock wakes one: retry", w=3.2, h=0.5, color=T.BLUE, size=13)
        self.at(n4, X0, fy - 2.16)
        self.add(connect(n3, n4, T.MUTED, 2.2))
        se = txt("the G parks in a runtime semaphore table: 251 buckets by address, each a balanced tree of "
                 "sudogs (8.7). No thread is blocked.", size=12, color=T.TEXT2, width=2.85)
        self.at(se, X0 + 3.45, fy - 1.4)

        # modes
        x = X0 + w + 0.45
        ww = X1 - x
        nm = card("Normal mode: throughput", "Waiters queue in FIFO order, but a woken waiter must **compete** "
                  "with goroutines that just arrived. Newcomers are already running on a CPU, so they usually win, "
                  "and the woken one goes back to the front of the queue. Lock handoff is cheap; a waiter can lose "
                  "many times in a row.", w=ww, color=T.GREEN, size=13)
        self.at(nm, x, Y0)
        sv = card("Starvation mode: fairness", "If a waiter fails to get the lock for more than **1 ms**, the mutex "
                  "switches mode. Unlock now **hands ownership directly** to the waiter at the front; newcomers do not "
                  "spin or grab it, they queue at the tail. The mutex returns to normal mode when the owner is the "
                  "last waiter or waited less than 1 ms.", w=ww, color=T.RED, size=13)
        self.at(sv, x, nm.get_bottom()[1] - 0.2)
        # mini lanes
        ly = sv.get_bottom()[1] - 0.4
        x0 = x + 1.35
        self.add(txt("**normal**", size=12, color=T.GREEN).move_to(P(x0 - 0.12, ly), aligned_edge=RIGHT))
        for a, b, lab, col in ((0, 1.2, "new G", T.GO), (1.25, 2.45, "new G", T.GO), (2.5, 3.7, "new G", T.GO)):
            self.add(seg(x0 + a, x0 + b, ly, col, h=0.3, lab=lab, size=11))
        self.add(seg(x0 + 3.75, x0 + 4.9, ly, T.GREY, h=0.3, lab="old waiter", size=11))
        ly2 = ly - 0.45
        self.add(txt("**starving**", size=12, color=T.RED).move_to(P(x0 - 0.12, ly2), aligned_edge=RIGHT))
        for a, b, lab, col in ((0, 1.2, "old waiter", T.RED), (1.25, 2.45, "new G", T.GO), (2.5, 3.7, "new G", T.GO)):
            self.add(seg(x0 + a, x0 + b, ly2, col, h=0.3, lab=lab, size=11))
        self.add(txt("lock owners over time →", size=11, color=T.MUTED).move_to(P(x0 + 3.9, ly2 - 0.32)))
        v = callout("version", "Starvation mode arrived in Go 1.9 (2017). It caps a waiter's delay; the price is "
                    "slower handoffs under heavy contention.", width=ww, size=13, inline=True)
        self.at(v, x, ly2 - 0.55)
        un = callout("hood", "**Unlock** clears the locked bit with one atomic add. If waiters exist and none is already "
                     "awake, it releases the semaphore to wake one (normal mode) or hands the lock straight over "
                     "(starvation mode).", width=ww, size=12, title="AND UNLOCK?")
        self.at(un, x, v.get_bottom()[1] - 0.18)


class C12RWMutex(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "sync.RWMutex: many readers or one writer"
    SUB = "Reads that do not change state can safely overlap. An RWMutex lets any number of readers in together, but a writer gets the data alone."

    def build(self):
        w = 6.25
        cd = code_ex("ch12_rwmutex_cache", lines=(8, 24), size=13, width=w,
                     hl=[(14, T.GREEN), (21, T.RED)], marks={14: "R", 21: "W"})
        self.at(cd, X0, Y0)
        tbl = table([["", "readers", "writer"],
                     ["**RLock / RUnlock**", "share with other readers", "waits for all of them"],
                     ["**Lock / Unlock**", "wait", "waits for other writers"]],
                    widths=[2.1, 2.05, 2.1], size=12, pad=0.08)
        self.at(tbl, X0, cd.get_bottom()[1] - 0.18)
        b = _bench()
        mr, rr = b["MutexRead"][1], b["RWMutexRead"][1]
        k = callout("note", f"Measured on 4 cores, tiny critical section (one map read): Mutex {mr:.1f} ns, "
                    f"RWMutex {rr:.1f} ns per read. RLock is an atomic add on a shared counter, so the cache line "
                    f"still bounces between cores. RWMutex pays off when reads dominate **and** take a while.",
                    width=w, size=12, title="IS IT FASTER?")
        self.at(k, X0, tbl.get_bottom()[1] - 0.18)

        x = X0 + w + 0.45
        x0 = x + 0.75
        ww = X1 - x0
        unit = ww / 12
        y = Y0 - 0.2
        lanes = [("R1", G1C, [(0, 4, "read", "run")]),
                 ("R2", G1C, [(1, 4.6, "read", "run")]),
                 ("W", T.RED, [(2, 4.6, "wait for readers", "wait"), (4.6, 8, "write", "run")]),
                 ("R3", G2C, [(3, 8, "wait: writer first", "wait"), (8, 11, "read", "run")])]
        for i, (lab, col, segs) in enumerate(lanes):
            yy = y - i * 0.55
            self.add(txt(f"**{lab}**", size=14, color=col).move_to(P(x0 - 0.12, yy), aligned_edge=RIGHT))
            self.add(dashed(P(x0, yy), P(X1, yy), T.STROKE2, 1.0, 0.06))
            for a, bb, sl, kind in segs:
                c = col if kind == "run" else T.GREY
                self.add(seg(x0 + a * unit, x0 + bb * unit - 0.03, yy, c, h=0.34, lab=sl, size=11,
                             outline=(kind == "wait"), text_color=T.TEXT2 if kind == "wait" else None))
        yb = y - 3 * 0.55 - 0.45
        self.add(time_axis(x0, X1, yb, lab="time"))
        for t_, lab in ((2, "W calls Lock"), (3, "R3 calls RLock"), (4.6, "last reader leaves")):
            self.add(Line(P(x0 + t_ * unit, y + 0.3), P(x0 + t_ * unit, yb)).set_stroke(T.YELLOW, 1.2, 0.5))
        self.add(txt("2: W calls Lock   3: R3 calls RLock   4.6: last reader leaves, W enters", size=12, color=T.YELLOW)
                 .move_to(P(x0, yb - 0.35), aligned_edge=LEFT))
        hood = callout("hood", "`readerCount` counts readers. Lock subtracts 2^30 (`rwmutexMaxReaders`) from it, so "
                       "a **negative** count tells every new RLock \"a writer is waiting: queue up\". That is why R3 "
                       "waits even though only readers hold the lock: writers cannot be starved by a stream of readers.",
                       width=X1 - x, size=13, title="UNDER THE HOOD")
        self.at(hood, x, yb - 0.65)
        warn = callout("warn", "No upgrades: RLock then Lock in one goroutine deadlocks. No recursive RLock either: "
                       "if a writer arrives between the two RLocks, everyone waits forever.",
                       width=X1 - x, size=13)
        self.at(warn, x, hood.get_bottom()[1] - 0.2)


class C12Once(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "sync.Once and OnceValue: initialise exactly once"
    SUB = "Lazy initialisation from many goroutines: the first caller runs the function, everyone else waits for it and then sees its result."

    def build(self):
        w = 6.25
        cd = code_ex("ch12_once", lines=(8, 25), size=13, width=w, hl=[11, 20], marks={11: "1", 20: "2"})
        self.at(cd, X0, Y0)
        tm = terminal(out("ch12_once"), title="go run . (five callers, one load)", width=w, size=13)
        self.at(tm, X0, cd.get_bottom()[1] - 0.15)
        x = X0 + w + 0.45
        ww = X1 - x
        st = code('''type Once struct {
    done atomic.Bool // first: the hot path is inlined
    m    Mutex
}''', size=13, title="sync/once.go", width=ww, numbers=False)
        self.at(st, x, Y0)
        y = st.get_bottom()[1] - 0.3
        d = node("Do(f): done?", w=1.9, h=0.48, color=T.YELLOW, size=13)
        self.at(d, x, y)
        fast = node("yes: return (one load)", w=2.3, h=0.48, color=T.GREEN, size=13)
        self.at(fast, x + 2.25, y)
        self.add(connect(d, fast, T.GREEN, 2.0))
        slow = node("m.Lock(); if !done { f(); done = true }; m.Unlock()", w=ww, h=0.48, color=T.RED, size=13)
        self.at(slow, x, y - 0.75)
        self.add(arrow(P(d.get_center()[0], d.get_bottom()[1]), P(d.get_center()[0], slow.get_top()[1]), T.RED, 2.0, 0.03))
        self.add(txt("no", size=11, color=T.RED).move_to(P(d.get_center()[0] + 0.2, (d.get_bottom()[1] + slow.get_top()[1]) / 2)))
        why = txt("Why a mutex and not just a CAS on done? Late callers must **wait until f has finished**, "
                  "or they could use a half-built config.", size=13, color=T.TEXT2, width=ww)
        self.at(why, x, slow.get_bottom()[1] - 0.15)
        tbl = table([["API (since)", "returns", "use for"],
                     ["`Once.Do(f)` (1.0)", "nothing", "side effects"],
                     ["`OnceFunc(f)` (1.21)", "`func()`", "a callable once-only action"],
                     ["`OnceValue(f)` (1.21)", "`func() T`", "a lazily built value"],
                     ["`OnceValues(f)` (1.21)", "`func() (T, error)`", "value plus error"]],
                    widths=[2.35, 1.85, ww - 4.2], size=12)
        self.at(tbl, x, why.get_bottom()[1] - 0.2)
        wn = callout("warn", "If f panics, `Once.Do` counts it as done and never retries; `OnceFunc`/`OnceValue` "
                     "re-panic with the same value on every call. Calling `Do` on the same Once from inside f deadlocks.",
                     width=w, size=13)
        self.at(wn, X0, tm.get_bottom()[1] - 0.18)


class C12Cond(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "sync.Cond: wait until a condition becomes true"
    SUB = "A condition variable lets goroutines sleep until some state guarded by a mutex changes, then wakes one (Signal) or all (Broadcast)."

    def build(self):
        w = 6.25
        cd = code_ex("ch12_cond", lines=(9, 33), size=13, width=w, hl=[11, 18, 19, 31], marks={18: "1", 19: "2", 31: "3"})
        self.at(cd, X0, Y0)
        x = X0 + w + 0.45
        ww = X1 - x
        tm = terminal(out("ch12_cond"), title="go run . (order varies)", width=ww, size=12)
        self.at(tm, x, Y0)
        self.at(section("WHAT cond.Wait() DOES", T.YELLOW, size=15), x, tm.get_bottom()[1] - 0.2)
        steps = num_steps([("Register", "on the Cond's notify list (takes a ticket)."),
                           ("Unlock", "`c.L`, so others can change the state."),
                           ("Sleep", "until Signal (one waiter) or Broadcast (all)."),
                           ("Lock", "`c.L` again before returning."),
                           ("Re-check", "the condition: another goroutine may have changed it first.")],
                          width=ww, color=T.YELLOW, size=12, gap=0.04)
        self.at(steps, x, tm.get_bottom()[1] - 0.58)
        # waiters picture
        y = steps.get_bottom()[1] - 0.35
        for i, lab in enumerate(("runner 1", "runner 2", "runner 3")):
            self.add(gtok(lab, T.GREY, w=1.25, h=0.38, state="wait", size=12).move_to(P(x + 0.65 + i * 1.35, y)))
        sig = node("Broadcast()", w=1.6, h=0.4, color=T.GREEN, size=12).move_to(P(x + 5.6, y))
        self.add(sig, arrow(sig.get_left(), P(x + 4.15, y), T.GREEN, 2, 0.04))
        self.add(txt("Broadcast wakes all three; Signal would wake only the longest waiter.",
                     size=12, color=T.TEXT2, width=ww).move_to(P(x, y - 0.3), aligned_edge=UL))
        q = callout("note", "The sync docs: \"For many simple use cases, users will be better off using channels than a "
                    "Cond (Broadcast corresponds to closing a channel, and Signal corresponds to sending on a channel).\" "
                    "Cond wins when the same state is waited on repeatedly.", width=ww, size=12, title="PREFER CHANNELS", inline=True)
        self.at(q, x, y - 0.68)


class C12Atomic(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "sync/atomic: indivisible operations on one word"
    SUB = "An atomic operation is done by the hardware as a single, uninterruptible step. No lock, no sleeping, no scheduler."

    def build(self):
        w = 6.25
        cd = code_ex("ch12_atomic_counter", lines=(9, 25), size=13, width=w, hl=[10, 15, 23], marks={15: "1", 23: "2"})
        self.at(cd, X0, Y0)
        tm = terminal(out("ch12_atomic_counter"), title="go run .", width=w, size=13)
        self.at(tm, X0, cd.get_bottom()[1] - 0.15)
        x = X0 + w + 0.45
        ww = X1 - x
        aw = (ww - 0.25) / 2
        a = code("INCQ (AX)", size=14, lang="text", title="*p++ on an int", width=aw, numbers=False, hl=[(1, T.RED)])
        b = code("MOVL  $1, CX\nLOCK\nXADDQ CX, (AX)", size=14, lang="text", title="p.Add(1), atomic.Int64",
                 width=aw, numbers=False, hl=[(2, T.GREEN), (3, T.GREEN)])
        self.at(b, x + aw + 0.25, Y0)
        self.at(a, x, Y0)
        cap_ = txt("Compiled by Go 1.27 on amd64 (`go build -gcflags=-S`). The LOCK prefix makes the core own "
                   "the cache line for the whole read-add-write.", size=12, color=T.TEXT2, width=ww)
        self.at(cap_, x, min(a.get_bottom()[1], b.get_bottom()[1]) - 0.12)
        Y, N = "{green|✓}", "{muted|–}"
        tbl = table([["type (Go 1.19+)", "Load Store Swap CAS", "Add", "And Or"],
                     ["`atomic.Bool`", Y, N, N],
                     ["`atomic.Int32`, `Int64`", Y, Y, "1.23"],
                     ["`atomic.Uint32`, `Uint64`, `Uintptr`", Y, Y, "1.23"],
                     ["`atomic.Pointer[T]`", Y, N, N],
                     ["`atomic.Value` (any, 1.4)", Y, N, N]],
                    widths=[3.05, 1.65, 0.7, ww - 5.4], size=12, center_cols=(1, 2, 3))
        self.at(tbl, x, cap_.get_bottom()[1] - 0.2)
        k = callout("key", "Go's atomics are **sequentially consistent**: all goroutines see all atomic operations in "
                    "one order, and they synchronise like locks do (memory model, 2022).", width=ww, size=12)
        self.at(k, x, tbl.get_bottom()[1] - 0.18)
        wn = callout("warn", "An atomic protects **one** word. Two fields that must change together (a balance and a "
                     "history) need a mutex. Mixing atomic and plain access to the same variable is a race.",
                     width=ww, size=12)
        self.at(wn, x, k.get_bottom()[1] - 0.15)


class C12CAS(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Compare-and-swap loops and atomic.Pointer"
    SUB = "CAS writes a new value only if the old one is still there. Retrying it in a loop builds any lock-free update out of one primitive."

    def build(self):
        w = 6.25
        a = code_ex("ch12_cas", lines=(9, 21), size=13, width=w, hl=[12, 16], marks={12: "1", 13: "2", 16: "3"})
        self.at(a, X0, Y0)
        b = code_ex("ch12_cas", lines=(35, 38), size=13, width=w, hl=[37])
        self.at(b, X0, a.get_bottom()[1] - 0.12)
        tm = terminal(out("ch12_cas"), title="go run .", width=w, size=13)
        self.at(tm, X0, b.get_bottom()[1] - 0.12)

        x = X0 + w + 0.45
        ww = X1 - x
        self.at(section("THE CAS LOOP", T.YELLOW, size=16), x, Y0)
        n1 = node("1  old := m.Load()", w=2.6, h=0.46, color=T.BLUE, size=13)
        self.at(n1, x, Y0 - 0.45)
        d1 = diamond("2  v <= old?", w=2.6, h=0.75, size=13)
        self.at(d1, x, n1.get_bottom()[1] - 0.22)
        r1 = node("return: nothing to do", w=2.9, h=0.46, color=T.GREY, size=13)
        r1.move_to(P(X1 - 1.45, d1.get_center()[1]))
        self.add(n1, d1, r1, connect(n1, d1, T.MUTED, 2), connect(d1, r1, T.MUTED, 2))
        self.add(txt("yes", size=11, color=T.MUTED).next_to(connect(d1, r1), UP, buff=0.04))
        d2 = diamond("3  CAS(old, v)?", w=2.6, h=0.75, size=13)
        self.at(d2, x, d1.get_bottom()[1] - 0.22)
        r2 = node("return: our write won", w=2.9, h=0.46, color=T.GREEN, size=13)
        r2.move_to(P(X1 - 1.45, d2.get_center()[1]))
        self.add(d2, r2, connect(d1, d2, T.MUTED, 2), connect(d2, r2, T.GREEN, 2))
        self.add(txt("no", size=11, color=T.MUTED).move_to(P(x + 1.45, d1.get_bottom()[1] - 0.14)))
        self.add(txt("true", size=11, color=T.GREEN).next_to(connect(d2, r2), UP, buff=0.04))
        loop = elbow_arrow([d2.get_left(), d2.get_left() + LEFT * 0.25, n1.get_left() + LEFT * 0.25, n1.get_left()],
                           T.RED, 2.4)
        self.add(loop, txt("false: someone changed m, retry", size=12, color=T.RED)
                 .move_to(P(x + 0.0, d2.get_bottom()[1] - 0.2), aligned_edge=LEFT))
        # pointer swap
        y = d2.get_bottom()[1] - 0.45
        self.at(section("PUBLISHING WITH atomic.Pointer", T.VIOLET, size=16), x, y)
        y -= 0.4
        ptr = node("cfg", w=0.9, h=0.5, color=T.VIOLET, size=14)
        self.at(ptr, x, y - 0.3)
        v1 = node("Config{Limit: 10}", w=2.3, h=0.45, color=T.GREY, size=12)
        self.at(v1, x + 1.6, y)
        v2 = node("Config{Limit: 20}", w=2.3, h=0.45, color=T.GREEN, size=12)
        self.at(v2, x + 1.6, y - 0.58)
        self.add(dashed_arrow(ptr.get_right(), v1.get_left(), T.MUTED, 1.8))
        self.add(arrow(ptr.get_right(), v2.get_left(), T.GREEN, 2.4, 0.04))
        self.add(txt("old readers keep v1,\nGC frees it later", size=11, color=T.MUTED).next_to(v1, RIGHT, buff=0.12))
        self.add(txt("Swap: new readers\nsee v2", size=11, color=T.GREEN).next_to(v2, RIGHT, buff=0.12))
        k = callout("tip", "Copy-on-write: never modify a published value. Build a new one and swap the pointer; "
                    "readers see the old or the new value, never a mix.", width=ww, size=12)
        self.at(k, x, v2.get_bottom()[1] - 0.15)


class C12Bench(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "What does each tool cost? Measured"
    SUB = "Five benchmarks hammer one shared counter or map, first from 1 goroutine, then from 4 goroutines on 4 cores (-cpu=1,4)."

    def build(self):
        b = _bench()
        rows = [("atomic Add", "AtomicInc", T.GREEN), ("Mutex Lock/Unlock", "MutexInc", T.RED),
                ("Mutex read of a map", "MutexRead", T.RED), ("RWMutex RLock read", "RWMutexRead", T.VIOLET),
                ("channel send to an owner", "ChannelInc", T.GO)]
        vmax = max(max(v) for v in b.values())
        x0 = X0 + 2.75
        bw = 3.65
        y = Y0 - 0.3
        self.add(legend_row([(Rectangle(width=0.3, height=0.16).set_fill(T.TEXT2, 0.35).set_stroke(T.TEXT2, 1), "1 goroutine"),
                             (Rectangle(width=0.3, height=0.16).set_fill(T.TEXT2, 1).set_stroke(width=0), "4 goroutines, 4 cores")],
                            size=13).move_to(P(x0, Y0 + 0.02), aligned_edge=LEFT))
        for i, (lab, key, col) in enumerate(rows):
            yy = y - i * 0.82
            self.add(txt(f"**{lab}**", size=14, color=T.TEXT, width=2.6).move_to(P(x0 - 0.15, yy - 0.17), aligned_edge=RIGHT))
            for j, v in enumerate(b[key]):
                L = bw * v / vmax
                r = Rectangle(width=L, height=0.26).set_fill(col, 0.35 if j == 0 else 1).set_stroke(col, 1 if j == 0 else 0)
                r.move_to(P(x0 + L / 2, yy - j * 0.32))
                self.add(r, txt(f"{v:.1f} ns", size=13, color=T.TEXT, weight="BOLD").next_to(r, RIGHT, buff=0.1))
        yb = y - 4 * 0.82 - 0.55
        self.add(hline(x0, x0 + bw, yb + 0.12, T.STROKE2, 1.2))
        self.add(txt("ns per operation (shorter is better)", size=12, color=T.MUTED).move_to(P(x0, yb - 0.08), aligned_edge=LEFT))
        x = X0 + 7.35
        ww = X1 - x
        a, m, c = b["AtomicInc"], b["MutexInc"], b["ChannelInc"]
        pts = bullets([
            f"**Contention, not the primitive, is the cost.** Going from 1 to 4 goroutines makes a mutex "
            f"{m[1] / m[0]:.1f}× slower: the lock's cache line ping-pongs between cores and waiters spin or sleep.",
            f"**Atomics are cheapest**: {a[1]:.1f} ns contended, {m[1] / a[1]:.1f}× faster than the mutex. One "
            "LOCK XADD, never a sleep.",
            f"**A channel is the slowest counter** ({c[1]:.1f} ns): every increment is a send that the owner "
            "goroutine must receive. Channels are for moving work and data, not for bumping a number.",
            "**RWMutex barely helps** for a nanosecond-long read: RLock itself writes a shared counter.",
            f"Even the slowest here is about {c[1]:.0f} ns. Pick the clearest tool first, measure, then optimise.",
        ], width=ww, size=14, gap=0.14, marker="arrow", marker_color=T.YELLOW)
        self.at(pts, x, Y0)
        n = callout("note", "Single runs on a 4-vCPU cloud VM (Xeon 2.1 GHz). The 1-goroutine numbers include "
                    "RunParallel's own loop overhead. Your hardware will differ; the ratios are what matter.",
                    width=ww, size=12)
        self.at(n, x, pts.get_bottom()[1] - 0.25)
        cd = code_ex("ch12_bench", file="counter_test.go", lines=(21, 28), size=13, width=ww, hl=[25])
        self.at(cd, x, n.get_bottom()[1] - 0.2)


class C12Pool(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "sync.Pool: recycle temporary objects"
    SUB = "A Pool is a cache of reusable objects that the garbage collector is allowed to empty. It cuts allocations on hot paths."

    def build(self):
        w = 6.25
        cd = code_ex("ch12_pool", file="pool_test.go", lines=(9, 34), size=12, width=w, hl=[10, 29, 30, 32],
                     marks={29: "1", 30: "2", 32: "3"})
        self.at(cd, X0, Y0)
        x = X0 + w + 0.45
        ww = X1 - x
        p = _pool()
        nb, pb = p["NewBuffer"], p["PooledBuffer"]
        self.at(section("BENCHMARK  go test -bench . -benchmem", T.GREEN, size=15), x, Y0)
        hb = hbars([("new each time", nb[0]), ("from the pool", pb[0])], x, Y0 - 0.6, ww - 4.4, row_h=0.42,
                   size=13, label_w=1.85, fmt="{:.0f}", unit=" ns", colors=[T.RED, T.GREEN])
        self.add(hb)
        self.add(txt(f"{nb[1]:,} B, {nb[2]} allocs/op", size=12, color=T.RED).move_to(P(X1, Y0 - 0.6), aligned_edge=RIGHT))
        self.add(txt(f"{pb[1]} B, {pb[2]} allocs/op", size=12, color=T.GREEN).move_to(P(X1, Y0 - 1.02), aligned_edge=RIGHT))
        # per-P picture
        y = Y0 - 1.5
        self.at(section("ONE CACHE PER P, SO GET RARELY CONTENDS", T.VIOLET, size=15), x, y)
        y -= 0.55
        for i in range(3):
            px = x + 0.35 + i * 2.1
            chip = pchip(f"P{i}", s=0.42, size=12).move_to(P(px, y - 0.2))
            pr = rbox(0.5, 0.32, color=T.YELLOW, fill=T.YELLOW, fill_opacity=0.15, radius=0.05).move_to(P(px + 0.75, y))
            sh = VGroup(*[rbox(0.26, 0.26, color=T.GO, fill=T.GO, fill_opacity=0.35, radius=0.04) for _ in range(4)]).arrange(RIGHT, buff=0.04)
            sh.move_to(P(px + 0.95, y - 0.42))
            self.add(chip, pr, sh)
            self.add(txt("private", size=10, color=T.YELLOW).next_to(pr, RIGHT, buff=0.06))
        self.add(txt("shared queue: owner pushes/pops the head, other Ps steal from the tail", size=11, color=T.GO)
                 .move_to(P(x, y - 0.78), aligned_edge=LEFT))
        y -= 1.12
        self.add(txt("**Get() looks in this order**", size=13, color=T.TEXT).move_to(P(x, y), aligned_edge=LEFT))
        y -= 0.42
        chain = [("own private", T.YELLOW), ("own shared", T.GO), ("steal", T.GO), ("victim", T.GREY), ("New()", T.RED)]
        nw = (ww - 0.25 * 4) / 5
        prev = None
        for i, (lab, col) in enumerate(chain):
            n = node(lab, w=nw, h=0.44, color=col, size=12).move_to(P(x + nw / 2 + i * (nw + 0.25), y))
            self.add(n)
            if prev is not None:
                self.add(arrow(prev.get_right(), n.get_left(), T.MUTED, 1.8, 0.03))
            prev = n
        gc = callout("hood", "Put() fills the private slot, else the own shared queue. At each GC the pool's objects "
                     "move to a **victim** cache; whatever is still unused at the next GC is freed (Go 1.13).",
                     width=ww, size=12)
        self.at(gc, x, y - 0.4)
        wn = callout("warn", "Reset objects after Get; never Put something still in use; don't pool huge buffers "
                     "(they stay alive); not for connections: entries vanish without notice.",
                     width=ww, size=12)
        self.at(wn, x, gc.get_bottom()[1] - 0.15)


class C12Map(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "sync.Map: a concurrent map for two special cases"
    SUB = "A map safe for many goroutines without your own lock. The docs are blunt: most code should use a plain map with a mutex."

    def build(self):
        w = 6.25
        cd = code_ex("ch12_syncmap", lines=(8, 23), size=13, width=w, hl=[9, 14, 21], marks={14: "1", 21: "2"})
        self.at(cd, X0, Y0)
        tm = terminal(out("ch12_syncmap"), title="go run .", width=w, size=13)
        self.at(tm, X0, cd.get_bottom()[1] - 0.15)
        nt = callout("note", "Values come back as `any`: you need type assertions, and the compiler cannot check "
                     "key or value types. Plain maps are not safe for concurrent writes: the runtime may stop the "
                     "program with \"fatal error: concurrent map writes\".", width=X1 - X0 - w - 0.45, size=12)
        x = X0 + w + 0.45
        ww = X1 - x
        self.at(section("USE IT WHEN (from the sync docs)", T.GREEN, size=15), x, Y0)
        c1 = card("1. Write once, read many", "a key is stored once and then only read, as in caches that only grow",
                  w=(ww - 0.2) / 2, color=T.GREEN, size=13)
        c2 = card("2. Disjoint keys", "goroutines read, write and overwrite entries for different sets of keys",
                  w=(ww - 0.2) / 2, color=T.GREEN, size=13)
        self.at(c1, x, Y0 - 0.45)
        self.at(c2, x + (ww + 0.2) / 2, Y0 - 0.45)
        y = min(c1.get_bottom()[1], c2.get_bottom()[1]) - 0.25
        tbl = table([["method", "does"],
                     ["`Load`, `Store`, `Delete`", "the basics"],
                     ["`LoadOrStore`", "insert if absent, in one atomic step"],
                     ["`LoadAndDelete`, `Swap`", "remove or replace, returning the old value"],
                     ["`CompareAndSwap`, `CompareAndDelete`", "change only if the value still matches"],
                     ["`Range`, `Clear` (1.23)", "visit every entry; empty the map"]],
                    widths=[3.4, ww - 3.4], size=12)
        self.at(tbl, x, y)
        h = callout("version", "Go 1.24 rebuilt sync.Map on a concurrent hash-trie (`internal/sync.HashTrieMap`), "
                    "the structure behind the `unique` package. The API did not change.", width=ww, size=12)
        self.at(h, x, tbl.get_bottom()[1] - 0.2)
        self.at(nt, x, h.get_bottom()[1] - 0.1)


class C12Choose(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Choosing: channel, mutex, atomic or something else?"
    SUB = "Ask what the goroutines are doing with the data. The answer usually picks the tool."

    def build(self):
        qs = [("Handing data or work to another goroutine, or announcing an event?", "channel  (8.5-8.8)", T.GREEN),
              ("Waiting for a group of goroutines to finish?", "WaitGroup / errgroup  (8.4)", T.GO),
              ("Initialising something once, lazily?", "Once / OnceValue", T.YELLOW),
              ("Several goroutines read and update shared state (struct, map, cache)?", "Mutex  (RWMutex if reads dominate)", T.RED),
              ("Just one counter, flag or pointer?", "atomic", T.VIOLET),
              ("Reusing short-lived buffers on a hot path?", "sync.Pool", T.TEAL)]
        y = Y0
        dw, rw = 5.0, 3.2
        for i, (q, a, col) in enumerate(qs):
            d = node(q, w=dw, h=0.62, color=T.YELLOW, size=13, fill_opacity=0.06, weight="NORMAL")
            self.at(d, X0, y)
            r = node(a, w=rw, h=0.62, color=col, size=14, fill_opacity=0.2)
            self.at(r, X0 + dw + 0.55, y)
            ar = connect(d, r, col, 2.2)
            self.add(ar, txt("yes", size=11, color=col).next_to(ar, UP, buff=0.03))
            if i < len(qs) - 1:
                self.add(arrow(P(X0 + 0.5, y - 0.62), P(X0 + 0.5, y - 0.86), T.MUTED, 1.8, 0))
                self.add(txt("no", size=11, color=T.MUTED).move_to(P(X0 + 0.7, y - 0.74)))
            y -= 0.86
        x = X0 + dw + rw + 0.85
        ww = X1 - x
        q = quote("Don't communicate by sharing memory; share memory by communicating.", "Go Proverbs (Rob Pike, 2015)",
                  width=ww, size=16)
        self.at(q, x, Y0)
        tbl = table([["channel", "mutex"],
                     ["passing ownership of data", "caches"],
                     ["distributing units of work", "state inside a struct"],
                     ["communicating async results", "a few fields updated together"]],
                    widths=[ww / 2, ww / 2], size=13, col_colors=[T.GREEN, T.RED])
        self.at(tbl, x, q.get_bottom()[1] - 0.3)
        self.add(txt("after the Go wiki page \"Use a sync.Mutex or a channel?\"", size=11, color=T.MUTED)
                 .next_to(tbl, DOWN, buff=0.08, aligned_edge=LEFT))
        k = callout("key", "\"Use whichever is most expressive and/or most simple.\" A mutex inside a type with a "
                    "small API is often clearer than a goroutine plus channels, and the reverse holds for pipelines.",
                    width=ww, size=13)
        self.at(k, x, tbl.get_bottom()[1] - 0.45)


class C12Recap(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Recap and check yourself"
    SUB = "Shared memory is safe when every access is ordered: by a lock, by an atomic, or by not sharing at all."

    def build(self):
        self.at(section("REMEMBER", T.GO), X0, Y0)
        rec = bullets([
            "`x++` on shared memory is read-add-write: concurrent increments get lost.",
            "Mutex: zero value ready, `Lock` + `defer Unlock`, not re-entrant, never copy it.",
            "Mutex inside: CAS fast path, brief spinning, sleep on a semaphore; starvation mode after 1 ms.",
            "RWMutex: readers share, writers exclude; a waiting writer blocks new readers.",
            "Once/OnceValue: run once, everyone waits for the result. Cond: wait in a loop, or use a channel.",
            "Atomics: one word, sequentially consistent; CAS loops for anything fancier.",
            "Pool recycles garbage-collectable objects; sync.Map fits two narrow cases.",
        ], width=6.1, size=15, marker="check", marker_color=T.GREEN, gap=0.12)
        self.at(rec, X0, Y0 - 0.5)
        x = 0.55
        self.at(section("CHECK YOURSELF", T.TEAL), x, Y0)
        qs = [("A method `func (c Cache) Get(k string)` locks `c.mu`. What is wrong?",
               "The value receiver copies the mutex, so each call locks its own copy: no exclusion. Use `*Cache`."),
              ("Why can new readers be blocked while only readers hold an RWMutex?",
               "A writer is waiting; readerCount is negative, so new readers queue behind it."),
              ("Two goroutines call `OnceValue`'s function while the first call is still running. What does the second see?",
               "It waits until the first call returns, then gets the same value."),
              ("When is a CAS loop better than a mutex?",
               "When the update is one word and retries are rare: no sleeping, no lock to forget.")]
        y = Y0 - 0.5
        for i, (q, a_) in enumerate(qs):
            grp = vstack(txt(f"**Q{i + 1}.** {q}", size=15, color=T.TEXT, width=6.0),
                         txt(f"{{teal|**Answer.**}} {a_}", size=14, color=T.TEXT2, width=6.0), buff=0.08)
            self.at(grp, x, y)
            y = grp.get_bottom()[1] - 0.26
