from kit import *

CH, NAME = "8.13", "The Memory Model and the Race Detector"
G1C, G2C = T.GO, T.ORANGE


def _mini(w, h, events, arrows, lanes=("G1", "G2"), colors=(G1C, G2C), size=11):
    """Two short swim lanes with labelled events and synchronisation arrows.
    events: (lane, x_fraction, label); arrows: (i, j, color, kind) where kind is
    'sync' (solid), 'seq' (thin grey) or 'none' (crossed, dashed)."""
    g = VGroup()
    x0, x1 = 0.55, w - 0.15
    ys = [h * 0.72, h * 0.22]
    for (lab, col), y in zip(zip(lanes, colors), ys):
        g.add(txt(f"**{lab}**", size=size + 1, color=col).move_to(P(x0 - 0.1, y), aligned_edge=RIGHT))
        g.add(dashed(P(x0, y), P(x1, y), T.STROKE2, 1.0, 0.05))
    pts = []
    for lane, fx, lab in events:
        p = P(x0 + (x1 - x0) * fx, ys[lane])
        pts.append(p)
        g.add(Dot(p, radius=0.06, fill_color=colors[lane]))
        t = txt(lab, size=size, color=T.TEXT2, font=T.MONO)
        t.next_to(p, UP if lane == 0 else DOWN, buff=0.08)
        g.add(t)
    for i, j, col, kind in arrows:
        a, b = pts[i], pts[j]
        if kind == "none":
            g.add(dashed_arrow(a, b, T.RED, 1.8))
            m = (a + b) / 2
            g.add(cross_mark(T.RED, 0.12).move_to(m))
        elif kind == "seq":
            g.add(arrow(a, b, T.MUTED, 1.6, 0.08))
        else:
            g.add(arrow(a, b, col, 2.6, 0.08))
    return g


def _rule_card(title, body, mini, w, h, color=T.GREEN, size=13):
    b = rbox(w, h, color=color, fill=T.PANEL, radius=0.14, stroke_width=1.6)
    b.set_stroke(color, 1.6, 0.7)
    tt = txt(f"**{title}**", size=size + 2, color=color, width=w - 0.4)
    bd = txt(body, size=size, color=T.TEXT2, width=w - 0.4)
    head = VGroup(tt, bd).arrange(DOWN, aligned_edge=LEFT, buff=0.06)
    head.move_to(b.get_corner(UL) + P(0.2, -0.16), aligned_edge=UL)
    mini.move_to(P(b.get_center()[0], b.get_bottom()[1] + 0.12 + mini.get_height() / 2))
    return VGroup(b, head, mini)


class C13Opener(Opener):
    NUM, NAME = CH, NAME
    TAGLINE = "On real hardware one goroutine's writes reach another goroutine late, and not always in order. The Go memory model says exactly when a write is guaranteed to be seen; the race detector finds code that ignores it."
    LEARN = ["Measure a reordering that no interleaving can explain",
             "Reason with happens-before: sequenced plus synchronized",
             "List every synchronizing operation Go provides",
             "Define a data race and what Go still promises after one",
             "Run the race detector and read its reports"]
    QUESTION = ("Goroutine A sets `msg = \"hello\"` and then `done = true`. Goroutine B sees `done == true`. "
                "Is B guaranteed to see `msg == \"hello\"`?")

    def art(self):
        g = VGroup()
        a = gopher(1.15, mood="happy").move_to(P(1.75, 1.75))
        b = gopher(1.15, mood="think", look=(-0.3, 0.0)).move_to(P(5.45, 1.75))
        g.add(a, b, txt("**A**", size=15, color=G1C).next_to(a, DOWN, buff=0.06),
              txt("**B**", size=15, color=G2C).next_to(b, DOWN, buff=0.06))
        ca = code('msg = "hello"\ndone = true', size=14, numbers=False, width=2.6)
        cb = code('if done {\n    print(msg)\n}', size=14, numbers=False, width=2.6)
        ca.move_to(P(1.75, 0.05))
        cb.move_to(P(5.45, 0.05))
        g.add(ca, cb)
        mem = rbox(3.4, 1.25, color=T.YELLOW, fill=T.PANEL2, radius=0.14).move_to(P(3.6, -1.75))
        g.add(mem, txt("**what B's core sees**", size=13, color=T.YELLOW).move_to(mem.get_top() + DOWN * 0.22))
        g.add(node("done = true", w=1.45, h=0.42, color=T.GREEN, size=13).move_to(mem.get_center() + P(-0.78, -0.18)))
        g.add(node('msg = ""', w=1.45, h=0.42, color=T.RED, size=13).move_to(mem.get_center() + P(0.78, -0.18)))
        g.add(arrow(ca.get_bottom(), mem.get_left() + UP * 0.2, G1C, 2.4, 0.08))
        g.add(arrow(mem.get_right() + UP * 0.2, cb.get_bottom(), G2C, 2.4, 0.08))
        g.add(txt("?", size=64, color=T.YELLOW, weight="BOLD").move_to(P(3.6, 0.35)))
        return g


class C13Reorder(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Memory is not one shared whiteboard"
    SUB = "Between one goroutine's write and another's read sit a compiler, an out-of-order CPU and a cache hierarchy. Each may change the order in which others see writes."

    def build(self):
        w = 6.5
        # hardware picture
        cw_ = 3.0
        cores = []
        for i, (lab, col, st, rd) in enumerate((("core 1 · G1", G1C, "x = 1", "r1 = y → 0"),
                                                ("core 2 · G2", G2C, "y = 1", "r2 = x → 0"))):
            cx = X0 + cw_ / 2 + i * (cw_ + 0.5)
            c = rbox(cw_, 2.35, color=col, fill=col, fill_opacity=0.07, radius=0.14).move_to(P(cx, Y0 - 1.2))
            self.add(c, txt(f"**{lab}**", size=14, color=col).move_to(c.get_top() + DOWN * 0.22))
            sb = titled_box("store buffer", cw_ - 0.4, 0.75, color=T.YELLOW, size=12).move_to(P(cx, Y0 - 1.05))
            self.add(sb, node(st, w=1.1, h=0.34, color=T.YELLOW, size=12).move_to(sb.get_center() + DOWN * 0.1))
            l1 = node("L1 cache", w=cw_ - 0.4, h=0.42, color=T.BLUE, size=12, fill_opacity=0.1).move_to(P(cx, Y0 - 1.95))
            self.add(l1)
            self.add(txt(rd, size=13, color=T.RED, font=T.MONO, weight="BOLD").move_to(P(cx, Y0 - 0.55)))
            cores.append((c, sb, l1))
        mem = node("shared L3 cache and RAM:   x = 0    y = 0", w=cw_ * 2 + 0.5, h=0.55, color=T.GREY, size=14)
        self.at(mem, X0, Y0 - 2.85)
        for c, sb, l1 in cores:
            self.add(darrow(l1.get_bottom(), P(l1.get_center()[0], mem.get_top()[1]), T.BLUE, 2, 0.04))
            self.add(dashed(sb.get_right() + LEFT * 0.12 + DOWN * 0.1, P(sb.get_right()[0] - 0.12, l1.get_top()[1]), T.YELLOW, 1.5, 0.05))
        st = num_steps([("core 1:", "`x = 1` goes into its store buffer, not yet into the cache."),
                        ("core 2:", "`y = 1` goes into its store buffer."),
                        ("core 1:", "loads `y` from the cache: still **0**."),
                        ("core 2:", "loads `x` from the cache: still **0**."),
                        ("later:", "both buffers drain; memory holds x = 1, y = 1. Too late for the reads.")],
                       width=w, color=T.YELLOW, size=13, gap=0.05)
        self.at(st, X0, mem.get_bottom()[1] - 0.2)
        x = X0 + w + 0.4
        ww = X1 - x
        c1 = card("1. The compiler", "keeps values in registers, hoists loads out of loops, reorders independent "
                  "loads and stores. All legal for a single goroutine.", w=ww, color=T.VIOLET, size=13)
        c2 = card("2. The CPU", "runs instructions out of order. Even x86 lets a later load pass an earlier store "
                  "(the store buffer); ARM and POWER reorder far more.", w=ww, color=T.AMBER, size=13)
        c3 = card("3. The caches", "agree on each single location eventually, but promise nothing about the order "
                  "in which different locations become visible.", w=ww, color=T.BLUE, size=13)
        y = Y0
        for c in (c1, c2, c3):
            self.at(c, x, y)
            y = c.get_bottom()[1] - 0.15
        k = callout("key", "Synchronizing operations (channels, locks, atomics) are where the compiler and CPU are "
                    "told to stop: they forbid code motion and emit memory barriers. Everything else may move.",
                    width=ww, size=13)
        self.at(k, x, y - 0.05)


class C13Litmus(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Measured: an outcome no interleaving can explain"
    SUB = "The store-buffer test. Each goroutine writes its own variable, then reads the other's. In every interleaving at least one read must see a 1."

    def build(self):
        w = 6.3
        cd = code_ex("ch13_litmus", lines=(38, 51), size=13, width=w, hl=[43, 44, 46, 47])
        self.at(cd, X0, Y0)
        tm = terminal(out("ch13_litmus"), title="go run . (both goroutines start each round together)", width=w, size=13)
        self.at(tm, X0, cd.get_bottom()[1] - 0.15)
        plain, atom = nums("ch13_litmus", r"in (\d+) of", int)
        k = callout("hood", f"**{plain:,}** times both reads saw 0: each core's store was still in its store buffer when "
                    f"its load read the old value. With `atomic.Int64`: **{atom}** times. Go's atomics are sequentially "
                    "consistent; on amd64 an atomic store is an XCHG, a full barrier.", width=w, size=13, title="WHAT HAPPENED")
        self.at(k, X0, tm.get_bottom()[1] - 0.2)
        x = X0 + w + 0.45
        ww = X1 - x
        self.at(section("ALL 6 INTERLEAVINGS", T.YELLOW, size=16), x, Y0)
        lg = txt("a: x = 1   b: r1 = y   (G1)      c: y = 1   d: r2 = x   (G2)", size=12, color=T.TEXT2, font=T.MONO)
        self.at(lg, x, Y0 - 0.45)
        rows = [["order", "r1", "r2"]]
        for order in ("a b c d", "a c b d", "a c d b", "c a b d", "c a d b", "c d a b"):
            pos = {e: i for i, e in enumerate(order.split())}
            r1 = 1 if pos["c"] < pos["b"] else 0
            r2 = 1 if pos["a"] < pos["d"] else 0
            rows.append([f"`{order}`", str(r1), str(r2)])
        rows.append(["{red|**measured, plain ints**}", "{red|**0**}", "{red|**0**}"])
        tbl = table(rows, widths=[ww - 2.2, 1.1, 1.1], size=14, center_cols=(1, 2))
        self.at(tbl, x, Y0 - 0.8)
        n = callout("note", "Sequential consistency means \"as if the operations of all goroutines were interleaved in "
                    "one order\". The hardware does not promise that for plain memory; Go promises it only for "
                    "race-free programs.", width=ww, size=13)
        self.at(n, x, tbl.get_bottom()[1] - 0.2)


class C13HB(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Happens before: the only order you can rely on"
    SUB = "The memory model defines one relation. If a write happens before a read, the read sees it. If neither happens before the other, you have a race."

    def build(self):
        w = 6.3
        cd = code_ex("ch13_publish", lines=(5, 17), size=14, width=w, hl=[9, 10, 15, 16],
                     marks={9: "1", 10: "2", 15: "3", 16: "4"})
        self.at(cd, X0, Y0)
        tm = terminal(out("ch13_publish"), title="go run .", width=w, size=14)
        self.at(tm, X0, cd.get_bottom()[1] - 0.15)
        drf = callout("key", "**DRF-SC**: a program with no data races behaves as if all goroutines ran interleaved on "
                      "one processor (sequentially consistent). Race-free code lets you forget store buffers and caches.",
                      width=w, size=13)
        self.at(drf, X0, tm.get_bottom()[1] - 0.2)
        # lanes, time going down
        x = X0 + w + 0.5
        ww = X1 - x
        xa, xb = x + 1.0, x + 3.6
        top = Y0 - 0.1
        self.add(txt("**setup()**", size=14, color=G1C).move_to(P(xa, top)))
        self.add(txt("**main**", size=14, color=G2C).move_to(P(xb, top)))
        for xx in (xa, xb):
            self.add(dashed(P(xx, top - 0.25), P(xx, top - 3.1), T.STROKE2, 1.2, 0.06))
        ev = {1: (xa, top - 0.6, 'msg = "hello..."', G1C), 2: (xa, top - 1.45, "close(ready)", G1C),
              3: (xb, top - 2.0, "<-ready returns", G2C), 4: (xb, top - 2.85, "print(msg)", G2C)}
        pts = {}
        for k_, (ex, ey, lab, col) in ev.items():
            n = node(lab, w=1.9, h=0.42, color=col, size=12).move_to(P(ex, ey))
            self.add(n, badge(str(k_), T.YELLOW, r=0.12, size=11).move_to(n.get_corner(UL) + P(0.0, 0.0)))
            pts[k_] = n
        self.add(arrow(pts[1].get_bottom(), pts[2].get_top(), T.MUTED, 2, 0.04))
        self.add(arrow(pts[3].get_bottom(), pts[4].get_top(), T.MUTED, 2, 0.04))
        self.add(arrow(pts[2].get_right(), pts[3].get_left(), T.GREEN, 3, 0.04))
        self.add(txt("synchronized\nbefore", size=12, color=T.GREEN, weight="BOLD").move_to(P((xa + xb) / 2 + 0.25, top - 1.45)))
        self.add(txt("sequenced", size=11, color=T.MUTED).move_to(P(xa + 0.55, top - 1.02), aligned_edge=LEFT))
        self.add(txt("sequenced", size=11, color=T.MUTED).move_to(P(xb + 0.55, top - 2.42), aligned_edge=LEFT))
        self.add(txt("happens before:  1 → 2 → 3 → 4,  so 4 sees 1", size=13, color=T.YELLOW, weight="BOLD")
                 .move_to(P(x, top - 3.4), aligned_edge=LEFT))
        defs = bullets(["**sequenced before**: program order inside one goroutine",
                        "**synchronized before**: a synchronizing write observed by a synchronizing read (a close seen by a receive, an Unlock by a Lock)",
                        "**happens before**: any chain of the two",
                        "a plain read **must** see write w if w happens before it and no other write to that variable comes in between"],
                       width=ww, size=13, gap=0.06, marker="arrow", marker_color=T.YELLOW)
        self.at(defs, x, top - 3.7)


class C13SyncChan(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Synchronizing edges (1): goroutines and channels"
    SUB = "Quoted from the Go memory model. Each green arrow means: everything before its tail is visible after its head."

    def build(self):
        cols, gap = 3, 0.2
        w = (CW - gap * (cols - 1)) / cols
        h = 2.36
        mw, mh = w - 0.3, 1.1
        cards = [
            ("go statement", "The `go` statement is synchronized before the new goroutine starts running.",
             _mini(mw, mh, [(0, 0.2, "go f()"), (1, 0.55, "f starts")], [(0, 1, T.GREEN, "sync")], ("main", "f")), T.GREEN),
            ("goroutine exit", "A goroutine's exit is synchronized before **nothing**. Wait for it with a channel or WaitGroup.",
             _mini(mw, mh, [(0, 0.45, "return"), (1, 0.8, "read")], [(0, 1, T.RED, "none")], ("f", "main")), T.RED),
            ("send → receive", "A send is synchronized before the matching receive **completes**.",
             _mini(mw, mh, [(0, 0.25, "ch <- v"), (1, 0.7, "<-ch done")], [(0, 1, T.GREEN, "sync")]), T.GREEN),
            ("close → receive", "Closing a channel is synchronized before a receive that returns a zero value because it is closed.",
             _mini(mw, mh, [(0, 0.25, "close(ch)"), (1, 0.7, "<-ch: 0, false")], [(0, 1, T.GREEN, "sync")]), T.GREEN),
            ("unbuffered: receive → send", "A receive from an **unbuffered** channel is synchronized before the matching send completes.",
             _mini(mw, mh, [(0, 0.7, "ch <- v done"), (1, 0.25, "<-ch")], [(1, 0, T.GREEN, "sync")]), T.GREEN),
            ("buffered: receive k → send k+C", "The kth receive on a channel of capacity C is synchronized before the (k+C)th send completes: a semaphore.",
             _mini(mw, mh, [(0, 0.75, "send #3 done"), (1, 0.25, "recv #1")], [(1, 0, T.GREEN, "sync")], ("G1", "G2")), T.GREEN),
        ]
        for i, (t, b, m, col) in enumerate(cards):
            r, c = divmod(i, cols)
            cdx = _rule_card(t, b, m, w, h, color=col)
            self.at(cdx, X0 + c * (w + gap), Y0 - r * (h + 0.2))
        k = callout("note", "The exit card is why `go f()` followed by reading f's results is a race unless something "
                    "waits for f. On a buffered channel, receive → send holds only in its k + C form.",
                    width=CW, size=13, inline=True)
        self.at(k, X0, Y1 + k.get_height() + 0.02)


class C13SyncMore(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Synchronizing edges (2): locks, Once, atomics and friends"
    SUB = "The sync and sync/atomic packages give the rest of the edges. Every other package must document its own."

    def build(self):
        cols, gap = 3, 0.2
        w = (CW - gap * (cols - 1)) / cols
        h = 2.36
        mw, mh = w - 0.3, 1.1
        cards = [
            ("Mutex, RWMutex", "Call n of `Unlock` is synchronized before call m of `Lock` returns, for every n < m.",
             _mini(mw, mh, [(0, 0.25, "Unlock()"), (1, 0.7, "Lock() returns")], [(0, 1, T.GREEN, "sync")])),
            ("RWMutex readers", "An Unlock is synchronized before the RLock that follows it; that reader's RUnlock before the next Lock.",
             _mini(mw, mh, [(0, 0.12, "Unlock"), (1, 0.45, "RLock"), (1, 0.62, "RUnlock"), (0, 0.92, "Lock")],
                   [(0, 1, T.GREEN, "sync"), (2, 3, T.GREEN, "sync")], ("W", "R"))),
            ("sync.Once", "The single call of f completes before **any** `once.Do(f)` returns, including in other goroutines.",
             _mini(mw, mh, [(0, 0.3, "f() done"), (1, 0.75, "Do returns")], [(0, 1, T.GREEN, "sync")])),
            ("Atomics", "If atomic B observes atomic A's effect, A is synchronized before B. All atomics act in one sequentially consistent order.",
             _mini(mw, mh, [(0, 0.25, "x.Store(1)"), (1, 0.7, "x.Load()==1")], [(0, 1, T.GREEN, "sync")])),
            ("WaitGroup, Cond, Map, Pool", "Documented per type. WaitGroup: each `Done` is synchronized before the `Wait` it unblocks returns.",
             _mini(mw, mh, [(0, 0.3, "wg.Done()"), (1, 0.75, "Wait returns")], [(0, 1, T.GREEN, "sync")], ("worker", "main"))),
            ("init and finalizers", "If p imports q, q's init finishes before p's starts; all init before `main.main`. "
             "`SetFinalizer(x, f)` is synchronized before `f(x)`.",
             _mini(mw, mh, [(0, 0.3, "init()"), (1, 0.75, "main()")], [(0, 1, T.GREEN, "sync")], ("init", "main"))),
        ]
        for i, (t, b, m) in enumerate(cards):
            r, c = divmod(i, cols)
            self.at(_rule_card(t, b, m, w, h), X0 + c * (w + gap), Y0 - r * (h + 0.2))
        k = callout("warn", "A **failed** `TryLock` synchronizes nothing, and as far as the memory model is concerned it "
                    "may fail even when the lock is free.", width=CW, size=13, inline=True)
        self.at(k, X0, Y1 + k.get_height() + 0.02)


class C13Race(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "What a data race is, and what Go still promises"
    SUB = "A race is defined by the happens-before relation, not by timing. A program can race even if the two accesses are seconds apart."

    def build(self):
        w = 6.3
        d = callout("def", "A **data race** is a write to a memory location and another read or write of the same "
                    "location, at least one of them not atomic, with **neither happening before the other**.",
                    width=w, size=14, title="DEFINITION")
        self.at(d, X0, Y0)
        mw, mh = 2.95, 1.1
        cases = [("RACE", T.RED, _mini(mw, mh, [(0, 0.3, "x = 1"), (1, 0.7, "print(x)")], [])),
                 ("no race: ordered", T.GREEN, _mini(mw, mh, [(0, 0.15, "x = 1"), (0, 0.45, "ch <- 0"), (1, 0.65, "<-ch"), (1, 0.95, "x")],
                                                     [(1, 2, T.GREEN, "sync")])),
                 ("no race: both reads", T.GREEN, _mini(mw, mh, [(0, 0.3, "print(x)"), (1, 0.7, "print(x)")], [])),
                 ("no race: both atomic", T.GREEN, _mini(mw, mh, [(0, 0.3, "a.Add(1)"), (1, 0.7, "a.Load()")], []))]
        y = d.get_bottom()[1] - 0.25
        for i, (lab, col, m) in enumerate(cases):
            r, c = divmod(i, 2)
            b = rbox(mw + 0.2, mh + 0.5, color=col, fill=T.PANEL, radius=0.12, stroke_width=1.5)
            self.at(b, X0 + c * (mw + 0.4), y - r * (mh + 0.65))
            m.move_to(b.get_center() + DOWN * 0.12)
            self.add(m, txt(f"**{lab}**", size=13, color=col).move_to(b.get_corner(UL) + P(0.15, -0.16), aligned_edge=UL))
        x = X0 + w + 0.45
        ww = X1 - x
        self.at(section("IF A PROGRAM RACES ANYWAY", T.RED, size=17), x, Y0)
        pts = bullets([
            "The implementation may **report the race and stop** the program. The race detector does exactly that.",
            "Otherwise, a read of a **word-sized** value sees some value that was really written to it and not yet "
            "overwritten. No values out of thin air.",
            "Values **larger than a word** (strings, slices, interfaces, structs) may be read half from one write and "
            "half from another.",
            "A torn (pointer, length) or (type, pointer) pair can cause **arbitrary memory corruption**: the one "
            "place where Go loses memory safety.",
        ], width=ww, size=14, gap=0.12, marker="arrow", marker_color=T.RED)
        self.at(pts, x, Y0 - 0.5)
        q = callout("note", "This makes Go more like Java or JavaScript, where most races have a limited set of outcomes, "
                    "and less like C and C++, where a racy program has no meaning at all. A race is still a bug.",
                    width=ww, size=13)
        self.at(q, x, pts.get_bottom()[1] - 0.25)


class C13Torn(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Measured: torn reads of a slice header"
    SUB = "A slice value is three machine words. Assigning one is three separate stores, so a racing reader can see a mix of two slices."

    def build(self):
        w = 6.3
        cd = code_ex("ch13_torn", lines=(8, 34), size=13, width=w, hl=[(19, T.RED), (21, T.RED), 27, 28], marks={27: "!"})
        self.at(cd, X0, Y0)
        tm = terminal(out("ch13_torn"), title="go run .", width=w, size=13)
        self.at(tm, X0, cd.get_bottom()[1] - 0.15)
        x = X0 + w + 0.45
        ww = X1 - x
        cw_ = (ww - 1.6) / 3

        def header(y, lab, vals, cols, note=None):
            self.add(txt(f"**{lab}**", size=13, color=T.TEXT).move_to(P(x + 1.5, y), aligned_edge=RIGHT))
            for i, (v, c) in enumerate(zip(vals, cols)):
                n = node(v, w=cw_ - 0.05, h=0.46, color=c, size=13).move_to(P(x + 1.6 + cw_ * i + cw_ / 2, y))
                self.add(n)
            if note:
                self.add(txt(note, size=11, color=T.MUTED).move_to(P(x + 1.6, y - 0.36), aligned_edge=LEFT))

        y = Y0 - 0.2
        for i, h_ in enumerate(("ptr", "len", "cap")):
            self.add(txt(h_, size=12, color=T.MUTED, font=T.MONO).move_to(P(x + 1.6 + cw_ * i + cw_ / 2, y)))
        header(y - 0.45, "short", ["→ [1]int", "1", "1"], [T.GREEN] * 3)
        header(y - 1.05, "long", ["→ [1000]int", "1000", "1000"], [T.BLUE] * 3)
        header(y - 1.85, "torn read", ["→ [1]int", "1000", "1"], [T.GREEN, T.BLUE, T.GREEN],
               "pointer and cap from short, len from long")
        torn = nums("ch13_torn", r"torn reads: (\d+)", int)[0]
        k = callout("warn", f"Here **{torn:,}** of 10,000,000 reads mixed the two slices. A torn header with the pointer "
                    "of the 1-element array and length 1000 lets `v[999]` read (or write) far past the end of the "
                    "array: memory corruption, without `unsafe`.", width=ww, size=13, title="WHY IT MATTERS")
        self.at(k, x, y - 2.55)
        k2 = callout("tip", "Interfaces are two words (type, data), strings two (ptr, len), slices three. Share them "
                     "through a channel, a mutex or `atomic.Pointer`, never through a plain variable.",
                     width=ww, size=13)
        self.at(k2, x, k.get_bottom()[1] - 0.2)


class C13BusyWait(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Broken idiom 1: spinning on a plain flag"
    SUB = "Waiting in a loop for another goroutine to set a bool looks harmless. The memory model says the loop is not even guaranteed to end."

    def build(self):
        w = 6.3
        cd = code_ex("ch13_busywait", lines=(8, 18), size=14, width=w, hl=[(13, T.RED), (15, T.RED)])
        self.at(cd, X0, Y0)
        tm = terminal(out("ch13_busywait", first=12), title="go run -race . (first lines)", width=w, size=12)
        self.at(tm, X0, cd.get_bottom()[1] - 0.15)
        x = X0 + w + 0.45
        ww = X1 - x
        aw = (ww - 0.5) / 2
        a = code("for !done {\n}", size=14, numbers=False, title="you wrote", width=aw)
        b = code("if !done {\n    for {}\n}", size=14, numbers=False, title="compiler may emit", width=aw)
        self.at(a, x, Y0)
        self.at(b, x + aw + 0.5, Y0)
        self.add(arrow(a.get_right(), b.get_left(), T.RED, 2.4, 0.06))
        ex = txt("Nothing in the loop synchronizes, so the compiler may read `done` once and keep it in a register. "
                 "The memory model's own example allows hoisting a load out of a loop like this.",
                 size=13, color=T.TEXT2, width=ww)
        self.at(ex, x, max(a.get_bottom()[1], b.get_bottom()[1]) - 0.15 - 0.2)
        fix = code_ex("ch13_busywait_atomic", lines=(9, 19), size=13, width=ww, hl=[(9, T.GREEN), (14, T.GREEN), (16, T.GREEN)],
                      title="examples/ch13_busywait_atomic/main.go (fixed)")
        self.at(fix, x, ex.get_bottom()[1] - 0.2)
        n = callout("note", "With Go 1.27 the racy loop happened to finish on this machine; the race detector still "
                    "flags it. Better than any spin: `close` a channel or call `wg.Wait()`, which also sleep instead of burning a core.",
                    width=ww, size=12)
        self.at(n, x, fix.get_bottom()[1] - 0.15)


class C13DCL(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Broken idiom 2: double-checked locking"
    SUB = "Checking a pointer without a lock to skip the lock \"when it's already set\" was a classic in C++ and Java. In Go it is a race, twice."

    def build(self):
        w = 6.3
        cd = code_ex("ch13_dcl", lines=(10, 34), size=13, width=w, hl=[(18, T.RED), (21, T.AMBER), (31, T.RED)],
                     marks={18: "1", 21: "W", 31: "2"})
        self.at(cd, X0, Y0)
        fix = code('''var get = sync.OnceValue(func() *Config {
    return &Config{Name: "prod"}
})''', size=13, title="fixed: let sync.OnceValue do it", width=X1 - X0 - w - 0.45, numbers=False, hl=[(1, T.GREEN)])
        x = X0 + w + 0.45
        ww = X1 - x
        rep = out("ch13_dcl").split("\n")
        keep = rep[:7] + rep[10:13] + ["  ...", rep[-2]]
        tm = terminal("\n".join(keep), title="go run -race . (abridged)", width=ww, size=12)
        self.at(tm, x, Y0)
        n = nums("ch13_dcl", r"Found (\d+) data race", int)[0]
        steps = num_steps([("Race 1:", "line 18 reads `instance` with no lock while another goroutine writes it at line 21."),
                           ("Race 2:", "line 31 reads `.Name`. Seeing the pointer does **not** mean seeing the fields "
                            "written before it was stored (the memory model's own example).")],
                          width=ww, color=T.RED, size=13, gap=0.1)
        self.at(steps, x, tm.get_bottom()[1] - 0.2)
        self.at(fix, x, steps.get_bottom()[1] - 0.25)
        k = txt(f"The detector found **{n}** races in one short run. `OnceValue` does the fast check correctly: "
                "an atomic load first, the lock only on the slow path.", size=13, color=T.TEXT2, width=ww)
        self.at(k, x, fix.get_bottom()[1] - 0.15)


class C13Detector(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "The race detector: -race"
    SUB = "Built on ThreadSanitizer from the LLVM project. It watches a real run and reports every pair of accesses that happened without a happens-before edge."

    def build(self):
        w = 6.3
        tbl = table([["command", "use it for"],
                     ["`go test -race ./...`", "every test run in CI"],
                     ["`go run -race .`", "trying a program"],
                     ["`go build -race`", "a canary or staging binary under real load"]],
                    widths=[2.7, w - 2.7], size=13)
        self.at(tbl, X0, Y0)
        steps = num_steps([("Instrument.", "The compiler inserts a call before every memory access and around every "
                            "channel op, lock, atomic and `go` statement."),
                           ("Track.", "Shadow memory records recent accesses to each 8-byte word: which goroutine, read "
                            "or write, at what logical time."),
                           ("Order.", "Vector clocks follow the synchronizing operations: that is the happens-before graph."),
                           ("Report.", "An access that conflicts with a recorded one not ordered by happens-before is a "
                            "race: print both stacks, keep going, exit with status 66.")],
                          width=w, color=T.GREEN, size=13, gap=0.1)
        self.at(steps, X0, tbl.get_bottom()[1] - 0.25)
        x = X0 + w + 0.45
        ww = X1 - x

        def secs(name):
            m = re.search(r"time: ([\d.]+)(ms|s)", (EX_DIR / name / "output.txt").read_text())
            return float(m.group(1)) / (1000 if m.group(2) == "ms" else 1)

        def mem(name):
            return int(re.search(r"peak memory: (\d+) kB", (EX_DIR / name / "output.txt").read_text()).group(1)) / 1024
        s0, s1, m0, m1 = secs("ch13_cost"), secs("ch13_cost_race"), mem("ch13_cost"), mem("ch13_cost_race")
        self.at(section("MEASURED COST (examples/ch13_cost)", T.AMBER, size=15), x, Y0)
        hb = hbars([("time, normal", s0), ("time, -race", s1)], x, Y0 - 0.55, ww - 3.4, row_h=0.42, size=13,
                   label_w=1.9, fmt="{:.2f}", unit=" s", colors=[T.GO, T.AMBER])
        self.add(hb)
        hb2 = hbars([("memory, normal", m0), ("memory, -race", m1)], x, Y0 - 1.5, ww - 3.4, row_h=0.42, size=13,
                    label_w=1.9, fmt="{:.0f}", unit=" MB", colors=[T.GO, T.AMBER])
        self.add(hb2)
        self.add(txt(f"{s1 / s0:.1f}× slower, {m1 / m0:.1f}× the memory for this workload (goroutines, a mutex, sorting)",
                     size=12, color=T.TEXT2, width=ww).move_to(P(x, Y0 - 2.2), aligned_edge=UL))
        lim = callout("warn", "It finds only races that **happen** in the run it watches: code your tests never execute "
                      "is never checked. Reports are real (no false positives), but silence proves nothing.",
                      width=ww, size=13, title="LIMITS")
        self.at(lim, x, Y0 - 2.75)
        opts = callout("note", "`GORACE=\"halt_on_error=1\"` stops at the first race; `log_path=race` writes reports to "
                       "files; `exitcode=N` changes 66. Supported on linux (amd64, arm64, loong64, ppc64le, riscv64, "
                       "s390x), darwin (amd64, arm64), and freebsd, netbsd, windows on amd64.",
                       width=ww, size=12, title="OPTIONS AND PLATFORMS")
        self.at(opts, x, lim.get_bottom()[1] - 0.18)


class C13Report(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Reading a race report"
    SUB = "Every report has the same four parts. Read them in order and the bug is usually obvious."

    def build(self):
        w = 6.1
        cd = code_ex("ch12_race_detect", lines=(8, 15), size=14, width=w, hl=[(11, T.RED), (12, T.RED)])
        self.at(cd, X0, Y0)
        text = out("ch12_race_detect")
        lines = text.split("\n")
        tm = terminal(text, title="go run -race .", width=X1 - X0 - w - 0.4 - 0.55, size=12)
        x = X0 + w + 0.4
        self.at(tm, x, Y0)

        def find(prefix):
            for i, l in enumerate(lines):
                if l.startswith(prefix):
                    return i + 1
            return None
        marks = [(find("Read at") or find("Write at"), "1", T.RED),
                 (find("Previous"), "2", T.AMBER),
                 (find("Goroutine"), "3", T.VIOLET),
                 (find("Found"), "4", T.GREEN)]
        for ln, lab, col in marks:
            if ln:
                yy = tm.y(ln)
                self.add(badge(lab, col, r=0.15, size=13).move_to(P(X1 - 0.2, yy)))
                self.add(Line(P(tm.get_right()[0] + 0.02, yy), P(X1 - 0.37, yy)).set_stroke(col, 1.5))
        steps = num_steps([("The access that tripped it:", "a read (or write), its address, the goroutine, and the stack "
                            "down to `file:line`."),
                           ("The earlier conflicting access:", "\"Previous write at\" the same address, from another "
                            "goroutine, with no happens-before edge between the two."),
                           ("Where each goroutine was born:", "the `go` statement (here inside `WaitGroup.Go`), and "
                            "whether it is still running."),
                           ("Summary and exit status 66.", "The program kept running: the result 130 was luck. "
                            "The order of the two goroutines changes from run to run.")],
                          width=w, color=T.YELLOW, size=13, gap=0.12)
        self.at(steps, X0, cd.get_bottom()[1] - 0.3)
        k = callout("tip", "Fix the **pair**: find the line in part 1 and the line in part 2 and add one "
                    "happens-before edge between them (a lock around both, a channel, or an atomic).",
                    width=w, size=13)
        self.at(k, X0, steps.get_bottom()[1] - 0.2)


class C13Habits(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Race-free by habit: common races and their fixes"
    SUB = "Nearly every race in real code is one of a handful of shapes. Each has a standard fix."

    def build(self):
        rows = [["the race", "the fix"],
                ["many goroutines do `count++`", "`atomic.Int64`, or a Mutex (8.12)"],
                ["a goroutine polls a plain `done` flag", "`close(ch)`, `wg.Wait()`, or `atomic.Bool`"],
                ["lazy init behind an unlocked nil check", "`sync.OnceValue`"],
                ["a config struct replaced while being read", "`atomic.Pointer[T]`, copy-on-write"],
                ["several goroutines write one map", "Mutex around the map, or `sync.Map`"],
                ["main reads results a goroutine wrote", "receive them from a channel, or `wg.Wait()` first"],
                ["a slice appended to from many goroutines", "one slot per goroutine, or a Mutex"],
                ["`go func(){ use(i) }()` in a loop before Go 1.22", "Go 1.22+ gives each iteration its own `i`"]]
        tbl = table(rows, widths=[4.2, 4.0], size=13, col_colors=[T.RED, T.GREEN])
        self.at(tbl, X0, Y0)
        x = X0 + 8.6
        ww = X1 - x
        mr = callout("warn", "The runtime also catches some map races by itself, cheaply and always on, by crashing:",
                     width=ww, size=13, title="MAPS CHECK THEMSELVES")
        self.at(mr, x, Y0)
        tm = terminal(out("ch13_map_race", first=3), title="examples/ch13_map_race", width=ww, size=12)
        self.at(tm, x, mr.get_bottom()[1] - 0.15)
        hb = bullets(["Run `go test -race ./...` in CI on every change.",
                      "Write tests that really run things concurrently: `t.Parallel()`, many goroutines, `-count=20`.",
                      "Run load tests against a `-race` build."],
                     width=ww, size=13, marker="check", marker_color=T.GREEN, gap=0.08)
        self.at(hb, x, tm.get_bottom()[1] - 0.25)
        q = quote("If you must read the rest of this document to understand the behavior of your program, you are "
                  "being too clever. Don't be clever.", "The Go Memory Model", width=8.4, size=15)
        self.at(q, X0 + 0.1, tbl.get_bottom()[1] - 0.35)


class C13Recap(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Recap and check yourself"
    SUB = "Synchronize every shared access, and let the race detector check that you did."

    def build(self):
        self.at(section("REMEMBER", T.GO), X0, Y0)
        rec = bullets([
            "Compilers, CPUs and caches reorder memory; we measured a \"0, 0\" no interleaving allows.",
            "Happens-before = sequenced-before (one goroutine) + synchronized-before (channels, locks, atomics, `go`, Once, WaitGroup).",
            "A goroutine's exit synchronizes nothing; buffered channels only order send → receive.",
            "Race-free programs are sequentially consistent (DRF-SC).",
            "Racy multiword values can tear: we measured mixed slice headers.",
            "`-race` finds races in the code you run, at several times the time and memory.",
        ], width=6.1, size=15, marker="check", marker_color=T.GREEN, gap=0.12)
        self.at(rec, X0, Y0 - 0.5)
        x = 0.55
        self.at(section("CHECK YOURSELF", T.TEAL), x, Y0)
        qs = [("A goroutine sets `result = 42`, and `main` sleeps 1 s before reading it. Race?",
               "Yes. Sleeping creates no happens-before edge, however long it is."),
              ("Unbuffered `ch`: G1 writes x then does `<-ch`; G2 does `ch <- 0` then reads x. Safe?",
               "Yes: the receive is synchronized before the send completes."),
              ("Same with `make(chan int, 1)`?",
               "No. With a buffer the send can finish before the receive, so x is racy."),
              ("Your tests pass under `-race`. Is the program race-free?",
               "Only the paths the tests ran were checked. Silence proves nothing about the rest.")]
        y = Y0 - 0.5
        for i, (q, a_) in enumerate(qs):
            grp = vstack(txt(f"**Q{i + 1}.** {q}", size=15, color=T.TEXT, width=6.0),
                         txt(f"{{teal|**Answer.**}} {a_}", size=14, color=T.TEXT2, width=6.0), buff=0.08)
            self.at(grp, x, y)
            y = grp.get_bottom()[1] - 0.26
