from kit import *

CH, NAME = "8.1", "Concurrency vs Parallelism"
TASK = {"A": T.GO, "B": T.PINK, "C": T.AMBER, "D": T.GREEN}


def lanes_panel(title, lanes, w=6.3, unit=0.55, lane_h=0.36, color=T.STROKE2, note=None):
    """A titled box with timeline lanes. lanes = [(label, [(t0, t1, task)])]."""
    head = txt(f"**{title}**", size=15, color=T.TEXT)
    rows = VGroup()
    x0 = 0.95
    for i, (lab, segs) in enumerate(lanes):
        y = -i * lane_h
        l = txt(lab, size=12, color=T.MUTED, weight="BOLD").move_to(P(x0 - 0.12, y), aligned_edge=RIGHT)
        base = Line(P(x0, y), P(w - 0.25, y)).set_stroke(T.STROKE, 1)
        rows.add(l, base)
        for t0, t1, k in segs:
            rows.add(seg(x0 + t0 * unit, x0 + t1 * unit - 0.03, y, TASK[k], h=lane_h * 0.72, lab=k, size=11))
    body = VGroup(head, rows)
    head.move_to(P(0.15, 0.42), aligned_edge=LEFT)
    if note:
        nt = txt(note, size=12, color=T.TEXT2).move_to(P(w - 0.15, 0.42), aligned_edge=RIGHT)
        body.add(nt)
    h = 0.42 + lane_h * (len(lanes) - 1) + 0.62
    b = rbox(w, h, color=color, fill=T.PANEL, radius=0.12, stroke_width=1.5)
    b.move_to(P(w / 2, 0.42 + 0.3 - h / 2))
    return VGroup(b, body)


class C1Opener(Opener):
    NUM, NAME = CH, NAME
    TAGLINE = "Two words that people use as synonyms. They are not, and the difference shapes every design decision in Go."
    LEARN = ["Define concurrency (structure) and parallelism (execution)",
             "Tell I/O-bound from CPU-bound work, and what each one gains",
             "Bound the speed-up of any program with Amdahl's law",
             "Place Go's CSP model among threads, actors and event loops",
             "Name the tools of Go concurrency you will meet in this module"]
    QUESTION = "If your machine had a single CPU core, could a Go program still be concurrent? Could it be parallel?"

    def art(self):
        g = VGroup()
        box1 = rbox(5.6, 3.2, color=T.STROKE2, fill=T.PANEL, fill_opacity=0.8, radius=0.2).move_to(P(3.7, 1.55))
        t1 = pill("CONCURRENT: one worker, many tasks", T.GO, size=12, filled=False)
        t1.move_to(box1.get_corner(UL) + P(0.2, -0.25), aligned_edge=LEFT)
        arc = Arc(start_angle=PI * 0.15, angle=PI * 0.7, radius=1.25).set_stroke(T.STROKE2, 2)
        arc.move_to(P(3.7, 2.5), aligned_edge=UP)
        jg = gopher(1.45, look=(0, 0.9)).move_to(P(3.7, 0.9))
        balls = VGroup(*[msg(k, TASK[k], s=0.42) for k in "ABC"])
        for b, a in zip(balls, (0.2, 0.5, 0.8)):
            b.move_to(arc.point_from_proportion(a))
        g.add(box1, t1, arc, jg, balls)
        box2 = rbox(5.6, 3.05, color=T.STROKE2, fill=T.PANEL, fill_opacity=0.8, radius=0.2).move_to(P(3.7, -1.85))
        t2 = pill("PARALLEL: many workers at the same instant", T.VIOLET, size=12, filled=False)
        t2.move_to(box2.get_corner(UL) + P(0.2, -0.25), aligned_edge=LEFT)
        g.add(box2, t2)
        for i, k in enumerate("ABC"):
            x = 2.0 + 1.7 * i
            gg = gopher(1.0).move_to(P(x, -2.25))
            b = msg(k, TASK[k], s=0.4).next_to(gg, UP, buff=0.1)
            c = txt(f"core {i}", size=12, color=T.MUTED, weight="BOLD").next_to(gg, DOWN, buff=0.06)
            g.add(gg, b, c)
        return g


class C1Definitions(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Two different ideas"
    SUB = "Concurrency is about **structure**: dealing with many things at once. Parallelism is about **execution**: doing many things at once."

    def build(self):
        w = 5.9
        d1 = callout("def", "**Concurrency** is the composition of independently executing tasks. "
                     "A program is concurrent when it is built from tasks whose lifetimes **overlap**, "
                     "whether or not they ever run at the same instant.", width=w, title="CONCURRENCY")
        d2 = callout("def", "**Parallelism** is the **simultaneous** execution of computations on several "
                     "cores (or machines). It is a property of a particular run on particular hardware, "
                     "not of the source code.", width=w, title="PARALLELISM")
        q = quote("Concurrency is about dealing with lots of things at once. Parallelism is about doing lots of things at once.",
                  "Rob Pike, “Concurrency is not Parallelism”, 2012", width=w, size=19)
        k = callout("key", "Concurrency is a way to **structure** a program; parallelism is one way to **run** it. "
                    "A well-structured concurrent Go program becomes parallel for free when the machine has more cores.",
                    width=w)
        col = vstack(d1, d2, q, k, buff=0.26)
        self.at(col, X0, Y0)

        x = 0.35
        A, B, C = "A", "B", "C"
        p1 = lanes_panel("Concurrent, not parallel (1 core)",
                         [("core 0", [(0, 1, A), (1, 1.8, B), (1.8, 2.6, C), (2.6, 3.6, A), (3.6, 4.4, B),
                                      (4.4, 5.2, C), (5.2, 6.0, A), (6.0, 6.8, B), (6.8, 7.4, C)])],
                         note="tasks take turns")
        p2 = lanes_panel("Parallel (3 cores, one task each)",
                         [("core 0", [(0, 2.5, A)]), ("core 1", [(0, 2.4, B)]), ("core 2", [(0, 2.3, C)])],
                         note="same instant, finishes ~3x sooner")
        p3 = lanes_panel("Concurrent AND parallel (2 cores)",
                         [("core 0", [(0, 1, A), (1, 1.8, C), (1.8, 2.8, B), (2.8, 3.7, A)]),
                          ("core 1", [(0, 1.2, B), (1.2, 2.2, A), (2.2, 3.1, C), (3.1, 3.7, C)])],
                         note="a task may move between cores")
        stack = vstack(p1, p2, p3, buff=0.16)
        self.at(stack, x, Y0)
        ax = time_axis(x + 0.95, x + 6.1, stack.get_bottom()[1] - 0.2, lab="time")
        leg = legend_row([(msg("A", T.GO, s=0.26), "task A"), (msg("B", T.PINK, s=0.26), "task B"),
                          (msg("C", T.AMBER, s=0.26), "task C")], size=13)
        self.at(leg, x + 0.95, ax.get_bottom()[1] - 0.12)
        self.add(ax)


class C1Quadrant(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "The 2 × 2 of concurrency and parallelism"
    SUB = "The two properties are independent. Every program sits in one of four boxes; the hardware decides between the two on the right."

    def build(self):
        cw, chh = 3.05, 2.5
        ox, oy = X0 + 0.55, Y0
        cells = {
            (0, 0): ("Sequential", "One task, one core. A plain `for` loop over files.", T.GREY),
            (1, 0): ("Concurrent, not parallel", "Tasks interleave on one core: Go with `GOMAXPROCS=1`, a JS event loop.", T.GO),
            (0, 1): ("Parallel, not concurrent", "One instruction stream, many data lanes: SIMD maths, a GPU kernel.", T.VIOLET),
            (1, 1): ("Concurrent and parallel", "Many tasks on many cores: a Go web server on 32 cores.", T.GREEN),
        }
        for (cx, py), (t, d, col) in cells.items():
            bx = rbox(cw, chh, color=col, fill=col, fill_opacity=0.07, radius=0.14, stroke_width=1.8)
            bx.move_to(P(ox + cx * (cw + 0.12) + cw / 2, oy - (1 - py) * (chh + 0.12) - chh / 2))
            tt = txt(f"**{t}**", size=16, color=col, width=cw - 0.3)
            dd = txt(d, size=13, color=T.TEXT2, width=cw - 0.3)
            vstack(tt, dd, buff=0.08).move_to(bx.get_corner(UL) + P(0.15, -0.15), aligned_edge=UL)
            self.add(bx, tt, dd)
            ic = self.icon(cx, py).move_to(bx.get_center() + P(0, -0.55))
            self.add(ic)
        xl = txt("**CONCURRENT?**   no  →  yes", size=13, color=T.TEXT2)
        xl.move_to(P(ox + cw + 0.06, oy - 2 * chh - 0.12 - 0.25))
        yl = txt("**PARALLEL?**   no  →  yes", size=13, color=T.TEXT2).rotate(PI / 2)
        yl.move_to(P(ox - 0.3, oy - chh - 0.06))
        self.add(xl, yl)
        rx = 1.6
        a = callout("q", "With a single core a Go program can be fully **concurrent** (its goroutines "
                    "take turns) but never **parallel**. Give it four cores and the same binary runs four "
                    "goroutines at once, without a single code change.", width=X1 - rx, title="THE BIG QUESTION, ANSWERED")
        self.at(a, rx, Y0)
        b = bullets(["Concurrency is chosen by the **programmer**: how the code is split into tasks.",
                     "Parallelism is granted by the **runtime and hardware**: how many cores run them.",
                     "In Go the dial is `GOMAXPROCS`: how many goroutines may execute Go code at the same instant.",
                     "Parallel-but-not-concurrent code is rare in Go; it lives in vector instructions and GPUs."],
                    width=X1 - rx, size=16, gap=0.14)
        self.at(b, rx, a.get_bottom()[1] - 0.3)
        tip = callout("tip", "Design for concurrency first. Then measure, and tune parallelism with benchmarks.",
                      width=X1 - rx, inline=True)
        self.at(tip, rx, b.get_bottom()[1] - 0.3)

    def icon(self, cx, py):
        if (cx, py) == (0, 0):
            return VGroup(*[msg(str(i), T.GREY, s=0.3) for i in range(1, 5)]).arrange(RIGHT, buff=0.08)
        if (cx, py) == (1, 0):
            return VGroup(*[msg(k, TASK[k], s=0.3) for k in "ABCAB"]).arrange(RIGHT, buff=0.05)
        if (cx, py) == (0, 1):
            g = VGroup()
            for i in range(4):
                g.add(VGroup(msg(f"{i}", T.VIOLET, s=0.24), txt("+", size=12, color=T.TEXT2),
                             msg(f"{i}", T.VIOLET, s=0.24, filled=False)).arrange(RIGHT, buff=0.05))
            return g.arrange(DOWN, buff=0.03)
        g = VGroup()
        for r, ks in enumerate(("ABA", "CBC")):
            g.add(VGroup(*[msg(k, TASK[k], s=0.28) for k in ks]).arrange(RIGHT, buff=0.05))
        return g.arrange(DOWN, buff=0.08)


class C1IOBound(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "I/O-bound work: concurrency hides waiting"
    SUB = "Most server time is spent waiting for networks and disks. While one goroutine waits, another can run, even on one core."

    def build(self):
        c = code_ex("ch01_latency", lines=(9, 29), size=13, hl=[17, 18, 25], marks={18: "1", 25: "2"})
        self.at(c, X0, Y0)
        t = terminal(out("ch01_latency"), title="output", width=c.get_width())
        self.at(t, X0, c.get_bottom()[1] - 0.2)
        seq, conc = nums("ch01_latency", r"(?:sequential|concurrent): (\d+)ms")

        x = c.get_right()[0] + 0.85
        self.at(section("WHAT THE CPU SEES", T.GO), x - 0.5, Y0)
        unit = (X1 - x - 0.9) / 5
        y = Y0 - 0.7
        self.at(txt(f"**sequential**: 5 × 100 ms in a row", size=15), x - 0.5, y)
        y -= 0.5
        for i in range(5):
            self.add(seg(x + i * unit, x + (i + 1) * unit - 0.05, y, T.BLUE, h=0.34, lab=f"wait {i}", size=11, outline=True))
            self.add(seg(x + i * unit, x + i * unit + 0.07, y, T.GO, h=0.34))
        self.add(txt(f"**{seq:.0f} ms**", size=15, color=T.RED).move_to(P(x + 5 * unit + 0.1, y), aligned_edge=LEFT))
        y -= 0.6
        self.at(txt("**concurrent**: five goroutines wait together", size=15), x - 0.5, y)
        y -= 0.5
        for i in range(5):
            yy = y - i * 0.36
            self.add(txt(f"G{i}", size=12, color=T.MUTED, weight="BOLD").move_to(P(x - 0.1, yy), aligned_edge=RIGHT))
            self.add(seg(x + 0.02 * i, x + unit + 0.02 * i, yy, T.BLUE, h=0.3, lab="wait", size=11, outline=True))
            self.add(seg(x + 0.02 * i, x + 0.02 * i + 0.07, yy, T.GO, h=0.3))
        self.add(txt(f"**{conc:.0f} ms**", size=15, color=T.GREEN).move_to(P(x + unit + 0.25, y - 0.8), aligned_edge=LEFT))
        ax = time_axis(x, x + 5 * unit + 0.4, y - 1.85, ticks=[(x + unit * k, f"{k * 100}") for k in range(6)], lab="ms")
        self.add(ax)
        leg = legend_row([(rbox(0.3, 0.2, color=T.GO, fill=T.GO), "CPU busy"),
                          (rbox(0.3, 0.2, color=T.BLUE, fill=T.BLUE, fill_opacity=0.15), "waiting for I/O")], size=13)
        self.at(leg, x - 0.5, ax.get_bottom()[1] - 0.2)
        notes = bullets([(badge("1", T.YELLOW, r=0.12, size=12), "each call blocks for 100 ms while the CPU sits idle"),
                         (badge("2", T.YELLOW, r=0.12, size=12), "`wg.Go` starts one goroutine per call, so all five wait at once")],
                        width=X1 - x + 0.5, size=14, gap=0.1)
        self.at(notes, x - 0.5, leg.get_bottom()[1] - 0.25)
        self.add(txt(f"**{seq / conc:.0f}x faster**, same CPU", size=14, color=T.TEXT2)
                 .move_to(P(x + unit + 1.25, y - 0.8), aligned_edge=LEFT))


class C1CPUBound(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "CPU-bound work: only parallelism helps"
    SUB = "Counting primes never waits. Splitting it into goroutines pays off only when there are cores to run them at the same time."

    def build(self):
        c = code_ex("ch01_speedup", lines=(28, 46), size=13, hl=[32, 33, 36], marks={36: "1"})
        self.at(c, X0, Y0)
        t = terminal(out("ch01_speedup"), title="measured on this machine", size=12, width=c.get_width())
        self.at(t, X0, c.get_bottom()[1] - 0.2)
        data = nums("ch01_speedup", r"speedup=([\d.]+)x")
        x0 = c.get_right()[0] + 1.0
        self.at(section("SPEED-UP vs GOMAXPROCS (measured)", T.GO), x0 - 0.45, Y0)
        y0 = Y0 - 0.65
        H, W = 2.3, X1 - x0 - 0.1
        base_y = y0 - H
        sx = W / 4
        top = 4.4
        for v in (1, 2, 3, 4):
            yy = base_y + H * v / top
            self.add(hline(x0, x0 + W, yy, T.STROKE, 1))
            self.add(txt(f"{v}x", size=12, color=T.MUTED).move_to(P(x0 - 0.12, yy), aligned_edge=RIGHT))
        self.add(hline(x0, x0 + W, base_y, T.STROKE2, 1.5))
        for i, v in enumerate(data):
            cx = x0 + sx * (i + 0.5)
            hh = H * v / top
            bar = RoundedRectangle(width=0.55, height=hh, corner_radius=0.06).set_fill(T.GO, 0.9).set_stroke(width=0)
            bar.move_to(P(cx, base_y + hh / 2))
            iy = base_y + H * (i + 1) / top
            self.add(bar, Line(P(cx - 0.38, iy), P(cx + 0.38, iy)).set_stroke(T.YELLOW, 2.5))
            self.add(txt(f"**{v:.2f}x**", size=14, color=T.TEXT).next_to(bar, UP, buff=0.08 if v < i + 0.8 else 0.12))
            self.add(txt(f"{i + 1}", size=14, color=T.TEXT2).move_to(P(cx, base_y - 0.22)))
        self.add(txt("GOMAXPROCS (= worker goroutines)", size=13, color=T.TEXT2).move_to(P(x0 + W / 2, base_y - 0.5)))
        lg = legend_row([(Line(ORIGIN, RIGHT * 0.35).set_stroke(T.YELLOW, 2.5), "ideal (linear)"),
                         (rbox(0.3, 0.2, color=T.GO, fill=T.GO), "measured")], size=13)
        self.at(lg, x0 - 0.45, base_y - 0.68)
        notes = bullets([(badge("1", T.YELLOW, r=0.12, size=12), "each worker writes only its own slot `counts[w]`, so no lock is needed"),
                         f"Ideal is 4x; this cloud VM reached **{data[-1]:.2f}x**: nearly linear, because the work splits evenly and the workers share nothing.",
                         "Speed-up depends on what else runs: an earlier run of this very program, with two stray busy loops on the same VM, stalled at about **2x**."],
                        width=X1 - x0 + 0.45, size=13, gap=0.07)
        self.at(notes, x0 - 0.45, lg.get_bottom()[1] - 0.12)
        k = callout("key", "Parallel speed-up is a property of the **hardware** you run on. Measure it; never assume it.",
                    width=X1 - x0 + 0.45, inline=True, size=14)
        self.at(k, x0 - 0.45, notes.get_bottom()[1] - 0.12)


class C1Amdahl(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Amdahl's law: the serial part sets the ceiling"
    SUB = "If a fraction p of the work can run in parallel, n cores can never make the program more than 1 / (1 − p) times faster."

    def build(self):
        f = VGroup(txt("**S(n) =**", size=34, color=T.TEXT),
                   VGroup(txt("1", size=30, color=T.TEXT),
                          Line(ORIGIN, RIGHT * 3.0).set_stroke(T.TEXT, 2.5),
                          txt("(1 − p)  +  p / n", size=28, color=T.TEXT)).arrange(DOWN, buff=0.1)).arrange(RIGHT, buff=0.25)
        fc = panel(f, pad=0.3, color=T.GO, fill=T.PANEL)
        self.at(fc, X0, Y0)
        legend = bullets(["**S(n)**: speed-up on n cores", "**p**: fraction of the run time that can be parallelised",
                          "**1 − p**: the serial fraction (start-up, merging results, a lock everyone needs)",
                          "**limit**: as n → ∞, S → 1 / (1 − p)"], width=5.7, size=15, gap=0.08)
        self.at(legend, X0, fc.get_bottom()[1] - 0.25)
        ex = callout("try", "p = 0.9 on 8 cores:  S = 1 / (0.1 + 0.9/8) = 1 / 0.2125 = **4.7x**, not 8x. "
                     "On 1,000 cores: **9.9x**. The 10% serial part dominates.", width=5.8, title="WORKED EXAMPLE")
        self.at(ex, X0, legend.get_bottom()[1] - 0.25)
        gus = callout("note", "**Gustafson's law** looks at it the other way round: with more cores we usually "
                      "grow the problem (more requests, bigger data), so the parallel part grows and the "
                      "useful speed-up keeps rising.", width=5.8, size=15)
        self.at(gus, X0, ex.get_bottom()[1] - 0.2)

        x0, x1 = 1.2, 4.75
        yb, yt = -2.75, 1.65
        smax = 25.0
        self.at(section("SPEED-UP S(n) FOR FOUR VALUES OF p", T.GO), 0.6, Y0)

        def X(n):
            return x0 + (x1 - x0) * np.log2(n) / 10

        def Y(s_):
            return yb + (yt - yb) * s_ / smax
        for s_ in (5, 10, 15, 20, 25):
            self.add(hline(x0, x1, Y(s_), T.STROKE, 1))
            self.add(txt(f"{s_}x", size=12, color=T.MUTED).move_to(P(x0 - 0.1, Y(s_)), aligned_edge=RIGHT))
        self.add(hline(x0, x1, yb, T.STROKE2, 1.5))
        for k in range(0, 11, 2):
            n = 2 ** k
            self.add(txt(str(n), size=12, color=T.MUTED).move_to(P(X(n), yb - 0.2)))
        self.add(txt("cores n (log scale)", size=13, color=T.TEXT2).move_to(P((x0 + x1) / 2, yb - 0.5)))
        ramp = ["#1C6F86", "#1F9BBF", "#4CC6E4", "#B3EEF9"]
        for p_, col in zip((0.5, 0.9, 0.95, 0.99), ramp):
            ns = [n for n in np.logspace(0, 10, 120, base=2) if 1 / ((1 - p_) + p_ / n) <= smax]
            pts = [P(X(n), Y(1 / ((1 - p_) + p_ / n))) for n in ns]
            curve = VMobject().set_points_smoothly(pts).set_stroke(col, 4)
            self.add(curve)
            lim = 1 / (1 - p_)
            end = pts[-1]
            if p_ == 0.99:
                lbl = txt(f"p = 0.99 → max 100x (off the chart)", size=13, color=T.TEXT)
                lbl.next_to(end, RIGHT, buff=0.1)
                self.add(Triangle(fill_color=col, fill_opacity=1, stroke_width=0).set_height(0.12).move_to(end + UP * 0.05))
            else:
                lbl = txt(f"p = {p_} → max {lim:.0f}x", size=13, color=T.TEXT).next_to(end, RIGHT, buff=0.1)
            self.add(lbl)


class C1Models(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Four ways to structure a concurrent program"
    SUB = "Languages differ in who does the work, how tasks talk to each other, and who decides when they run."

    def build(self):
        w, h = 3.1, 2.65
        y = Y0
        xs = [X0 + i * (w + 0.26) for i in range(4)]
        data = [
            ("Threads + locks", T.RED, "Tasks share memory; locks protect it.", "C, C++, Java, Rust std"),
            ("Actors", T.AMBER, "Each actor owns its state and a mailbox; messages go to a named actor.", "Erlang/Elixir, Akka"),
            ("Event loop", T.BLUE, "One thread runs callbacks or `async` tasks whenever I/O is ready.", "JavaScript, Python asyncio"),
            ("CSP", T.GO, "Anonymous processes; values travel over typed channels.", "Go, occam, Clojure core.async"),
        ]
        for i, (t, col, d, ex) in enumerate(data):
            bx = rbox(w, h, color=col, fill=T.PANEL, radius=0.14, stroke_width=1.8)
            bx.move_to(P(xs[i] + w / 2, y - h / 2))
            tt = txt(f"**{t}**", size=18, color=col).move_to(bx.get_corner(UL) + P(0.15, -0.15), aligned_edge=UL)
            dd = txt(d, size=13, color=T.TEXT2, width=w - 0.3).move_to(bx.get_corner(DL) + P(0.15, 0.55), aligned_edge=DL)
            ee = txt(ex, size=12, color=T.MUTED, width=w - 0.3).move_to(bx.get_corner(DL) + P(0.15, 0.15), aligned_edge=DL)
            art = getattr(self, f"art{i}")().move_to(bx.get_center() + P(0, 0.2))
            self.add(bx, tt, dd, ee, art)
        rows = [["", "Threads + locks", "Actors", "Event loop", "CSP (Go)"],
                ["Unit of work", "OS thread", "actor (has identity)", "callback / async task", "goroutine (anonymous)"],
                ["Communication", "shared memory", "message to a mailbox", "shared memory, one thread", "value sent on a channel"],
                ["Blocking style", "blocks a thread", "never blocks the mailbox owner", "must never block the loop", "blocks the goroutine only"],
                ["Who schedules", "the OS kernel", "the actor runtime", "the event loop", "the Go runtime (M:N)"]]
        tb = table(rows, [2.0, 2.65, 2.65, 2.65, 3.25], size=14, col_colors=[T.TEXT2, None, None, None, T.GO_LIGHT])
        self.at(tb, X0, y - h - 0.3)
        k = callout("key", "Go is **CSP-first** but not CSP-only: package `sync` gives you threads-and-locks "
                    "tools too. This module teaches when to use each.", width=CW, inline=True)
        self.at(k, X0, tb.get_bottom()[1] - 0.2)

    def art0(self):
        box = rbox(0.7, 0.5, color=T.RED, fill=T.PINK, fill_opacity=0.2)
        l = lock_icon(s=0.26).next_to(box, UP, buff=0.02)
        a, b = mthread("T1", w=0.7, h=0.36), mthread("T2", w=0.7, h=0.36)
        a.next_to(box, LEFT, buff=0.35)
        b.next_to(box, RIGHT, buff=0.35)
        return VGroup(box, l, a, b, arrow(a.get_right(), box.get_left(), T.TEXT2, 2), arrow(b.get_left(), box.get_right(), T.TEXT2, 2))

    def art1(self):
        g = VGroup()
        for i, n in enumerate(("A1", "A2")):
            c = Circle(radius=0.3).set_fill(T.AMBER, 0.2).set_stroke(T.AMBER, 2)
            t = txt(f"**{n}**", size=13, color=T.AMBER).move_to(c)
            mb = VGroup(*[msg("", T.PINK, s=0.14) for _ in range(3)]).arrange(DOWN, buff=0.02).next_to(c, LEFT if i == 0 else RIGHT, buff=0.05)
            grp = VGroup(c, t, mb).move_to(P(-0.8 + 1.6 * i, 0))
            g.add(grp)
        g.add(arrow(g[0][0].get_right(), g[1][2].get_left(), T.TEXT2, 2))
        return g

    def art2(self):
        c = Circle(radius=0.42).set_stroke(T.BLUE, 3)
        arr = Arrow(c.point_at_angle(PI * 0.3), c.point_at_angle(PI * 0.05), buff=0, path_arc=-0.5, fill_color=T.BLUE, thickness=2)
        q = VGroup(*[msg("", T.GO, s=0.16) for _ in range(4)]).arrange(RIGHT, buff=0.04).next_to(c, LEFT, buff=0.2)
        t = txt("loop", size=12, color=T.BLUE, weight="BOLD").move_to(c)
        return VGroup(c, arr, q, t)

    def art3(self):
        a, b = gtok("G1", w=0.62, h=0.32), gtok("G2", w=0.62, h=0.32)
        p = chan_pipe(2, ["v"], cell=0.3)
        return VGroup(a, p, b).arrange(RIGHT, buff=0.12)


class C1CSP(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Go's choice: Communicating Sequential Processes"
    SUB = "In 1978 Tony Hoare proposed building programs from sequential processes that synchronise only by passing messages. Go is its most popular descendant."

    def build(self):
        y = Y0 - 0.45
        x0, x1 = X0 + 0.6, X1 - 0.6
        self.add(Line(P(x0 - 0.4, y), P(x1 + 0.4, y)).set_stroke(T.STROKE2, 4))
        events = [(1978, "CSP paper", "C. A. R. Hoare, CACM"), (1983, "occam", "language for the Transputer"),
                  (1989, "Newsqueak", "Rob Pike: channels as values"), (1992, "Alef", "Plan 9 systems language"),
                  (1995, "Limbo", "Inferno OS"), (2009, "Go", "open-sourced, Nov 2009"), (2012, "Go 1.0", "the compatibility promise")]
        step = (x1 - x0) / (len(events) - 1)
        for i, (yr, t, d) in enumerate(events):
            x = x0 + i * step
            col = T.GO if yr >= 2009 else T.TEXT2
            self.add(Dot(P(x, y), radius=0.09, fill_color=col))
            self.add(txt(f"**{yr}**", size=15, color=col).move_to(P(x, y + 0.3)))
            tt = txt(f"**{t}**", size=14, color=T.TEXT, width=1.7, align="CENTER").move_to(P(x, y - 0.32))
            dd = txt(d, size=12, color=T.MUTED, width=1.75, align="CENTER").next_to(tt, DOWN, buff=0.05)
            self.add(tt, dd)
        yy = Y0 - 1.65
        w, h = 6.4, 2.6
        left = titled_box("Communicate by sharing memory", w, h, color=T.RED)
        self.at(left, X0, yy)
        right = titled_box("Share memory by communicating", w, h, color=T.GREEN)
        self.at(right, X1 - w, yy)
        lc = left.box.get_center() + DOWN * 0.1
        data = rbox(1.1, 0.7, color=T.PINK, fill=T.PINK, fill_opacity=0.2).move_to(lc)
        dl = txt("**data**", size=14, color=T.PINK).move_to(data)
        lk = lock_icon(s=0.32).next_to(data, UP, buff=0.05)
        g1 = gopher(0.85).move_to(lc + LEFT * 2.0)
        g2 = gopher(0.85, look=(-0.4, 0)).move_to(lc + RIGHT * 2.0)
        a1 = arrow(g1.get_right(), data.get_left(), T.RED, 2.5)
        a2 = arrow(g2.get_left(), data.get_right(), T.RED, 2.5)
        cap = txt("Both goroutines touch the same memory; a lock decides who goes first.", size=13, color=T.TEXT2, width=w - 0.4)
        cap.move_to(left.box.get_bottom() + UP * 0.28)
        self.add(data, dl, lk, g1, g2, a1, a2, cap)
        rc = right.box.get_center() + DOWN * 0.1
        h1 = gopher(0.85).move_to(rc + LEFT * 2.2)
        h2 = gopher(0.85, look=(-0.4, 0)).move_to(rc + RIGHT * 2.2)
        pipe = chan_pipe(2, ["d"], cell=0.42).move_to(rc)
        b1 = arrow(h1.get_right(), pipe.get_left(), T.GREEN, 2.5)
        b2 = arrow(pipe.get_right(), h2.get_left(), T.GREEN, 2.5)
        cap2 = txt("The value travels through a channel and ownership travels with it.",
                   size=13, color=T.TEXT2, width=w - 0.4).move_to(right.box.get_bottom() + UP * 0.28)
        self.add(pipe, b1, b2, h1, h2, cap2)
        q = quote("Do not communicate by sharing memory; instead, share memory by communicating.",
                  "Effective Go", width=7.6, size=18)
        self.at(q, X0 + 0.35, yy - h - 0.3)
        k = callout("key", "A send is a **hand-off of ownership**: after `ch <- buf` the sender must not touch `buf` again.",
                    width=5.0, size=14)
        self.at(k, X1 - 5.0, yy - h - 0.3)


class C1Toolkit(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "The toolkit you will master in this module"
    SUB = "Language keywords, five standard packages, an extension module and the runtime's own instruments."

    def build(self):
        cx, cy = 0.0, -0.7
        hub = Circle(radius=0.95).set_fill(T.GO, 0.12).set_stroke(T.GO, 3).move_to(P(cx, cy))
        hg = gopher(0.95).move_to(P(cx, cy + 0.12))
        ht = txt("**Go concurrency**", size=14, color=T.GO).next_to(hg, DOWN, buff=0.02)
        branches = [
            ("Language", T.GO, "start goroutines, pass values", "`go f()`  `chan T`  `<-`  `select`  `close`  `range ch`", "8.3 - 8.8", (-4.45, 1.3)),
            ("sync", T.RED, "locks and coordination", "`Mutex`  `RWMutex`  `WaitGroup`  `Once`  `OnceValue`  `Cond`  `Map`  `Pool`", "8.4, 8.12", (0.0, 1.45)),
            ("sync/atomic", T.ORANGE, "lock-free single-word updates", "`atomic.Int64`  `Bool`  `Pointer[T]`  `Value`  `CompareAndSwap`", "8.12 - 8.13", (4.45, 1.3)),
            ("context", T.AMBER, "cancellation, deadlines, request values", "`WithCancel`  `WithTimeout`  `WithCancelCause`  `AfterFunc`  `WithoutCancel`", "8.14", (-4.55, -0.7)),
            ("runtime", T.VIOLET, "inspect and tune the scheduler", "`GOMAXPROCS`  `NumGoroutine`  `Gosched`  `LockOSThread`  `GODEBUG`", "8.9 - 8.11", (4.55, -0.7)),
            ("golang.org/x/sync", T.TEAL, "helpers maintained by the Go team", "`errgroup`  `semaphore`  `singleflight`", "8.4, 8.15", (-4.45, -2.75)),
            ("Tools", T.GREEN, "find races, leaks and latency", "`go run -race`  `pprof` profiles  `go tool trace`  `schedtrace`", "8.13, 8.17", (0.0, -2.85)),
            ("Testing", T.PINK, "deterministic tests for concurrent code", "`testing/synctest`  `b.RunParallel`  `go test -race`", "8.18", (4.45, -2.75)),
        ]
        for name, col, purpose, items, chs, (x, y) in branches:
            card_ = card(name, f"{{text2|{purpose}}}\n{items}", w=4.1, color=col, size=14, body_color=T.TEXT)
            card_.move_to(P(x, y))
            chp = pill(f"ch. {chs}", col, size=11, filled=False).move_to(card_.box.get_corner(UR) + P(-0.65, -0.24))
            d = card_.get_center() - hub.get_center()
            ln = Line(hub.get_center() + d / np.linalg.norm(d) * 0.95, card_.get_center()).set_stroke(col, 2.5, 0.6)
            self.add(ln, card_, chp)
        self.add(hub, hg, ht)


class C1Recap(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Recap and check yourself"
    SUB = "Five ideas to keep from this chapter, and four questions to make sure they stuck."

    def build(self):
        sp = nums("ch01_speedup", r"speedup=([\d.]+)x")[-1]
        seq, conc = nums("ch01_latency", r"(?:sequential|concurrent): (\d+)ms")
        self.at(section("REMEMBER", T.GO), X0, Y0)
        rec = bullets([
            "**Concurrency** = structure (tasks with overlapping lifetimes). **Parallelism** = simultaneous execution.",
            f"Concurrency helps **I/O-bound** work even on one core by overlapping waits ({seq:.0f} ms → {conc:.0f} ms).",
            f"**CPU-bound** work only speeds up with more cores, and only as much as the hardware allows: {sp:.2f}x on our 4 vCPUs.",
            "**Amdahl**: speed-up ≤ 1 / (1 − p). Shrink the serial part before buying cores.",
            "Go follows **CSP**: goroutines plus channels, with `sync` for the cases where sharing is simpler.",
        ], width=6.0, size=16, marker="check", marker_color=T.GREEN, gap=0.16)
        self.at(rec, X0, Y0 - 0.5)
        g = gopher(1.2, mood="think").move_to(P(X0 + 1.0, -2.6))
        b = bubble("Concurrency is not parallelism... but it **enables** it.", width=3.6, tail="left", tail_x=-0.1)
        b.next_to(g, RIGHT, buff=0.35).shift(UP * 0.2)
        self.add(g, b)
        x = 0.55
        self.at(section("CHECK YOURSELF", T.TEAL), x, Y0)
        qs = [
            ("A web crawler spends 95% of its time waiting for HTTP responses. Will raising GOMAXPROCS from 4 to 64 make it 16x faster?",
             "No. It is I/O-bound: more goroutines (more requests in flight) help; more cores barely do."),
            ("A job is 80% parallelisable. What is the best possible speed-up on infinitely many cores?",
             "1 / (1 − 0.8) = 5x."),
            ("Name one program that is parallel but not concurrent.",
             "A SIMD loop that adds two vectors: one instruction stream, many data lanes."),
            ("In CSP, how do processes find each other?",
             "They don't: they share a channel. Actors, by contrast, send to a named mailbox."),
        ]
        y = Y0 - 0.5
        for i, (q, a) in enumerate(qs):
            qt = txt(f"**Q{i + 1}.** {q}", size=16, color=T.TEXT, width=6.0)
            at = txt(f"{{teal|**Answer.**}} {a}", size=15, color=T.TEXT2, width=6.0)
            grp = vstack(qt, at, buff=0.08)
            self.at(grp, x, y)
            y = grp.get_bottom()[1] - 0.3
