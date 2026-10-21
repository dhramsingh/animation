from kit import *

CH, NAME = "8.15", "Concurrency Patterns I: Pipelines and Pools"


def _stage(lab, color=T.GO, w=1.5, h=0.62, n=1, size=13, mood="run"):
    """A pipeline stage: a box with n small gophers above it."""
    b = node(lab, w=w, h=h, color=color, size=size)
    g = VGroup(b)
    gs = VGroup(*[gopher(0.55, mood=mood) for _ in range(n)]).arrange(RIGHT, buff=0.04)
    gs.next_to(b, UP, buff=0.05)
    g.add(gs)
    g.box = b.box
    return g


def _pipe(a, b, cap=2, items=(), color=T.GREEN, cell=0.36, item_color=T.PINK):
    """A channel tube centred between two stage boxes, with arrows."""
    p = chan_pipe(cap, items, cell=cell, color=color, item_color=item_color)
    ax, bx = a.box.get_right()[0], b.box.get_left()[0]
    y = a.box.get_center()[1]
    p.move_to(P((ax + bx) / 2, y))
    g = VGroup(p)
    if p.get_left()[0] - ax > 0.12:
        g.add(arrow(P(ax, y), P(p.get_left()[0], y), color, 2, 0.02))
    if bx - p.get_right()[0] > 0.12:
        g.add(arrow(P(p.get_right()[0], y), P(bx, y), color, 2, 0.02))
    return g


class C15Opener(Opener):
    NUM, NAME = CH, NAME
    TAGLINE = "Goroutines and channels are building blocks. A handful of patterns built from them solve most real problems: generators, pipelines, fan-out and fan-in, worker pools and semaphores."
    LEARN = ["Write generators, and know when an iterator is better",
             "Chain stages into a cancellable pipeline",
             "Fan work out to many goroutines and fan results back in",
             "Size a worker pool, and bound concurrency with a semaphore",
             "Keep results in order without a lock"]
    QUESTION = ("10,000 images must be downloaded, resized and uploaded. How many goroutines should you start, and "
                "how do they hand work to each other?")

    def art(self):
        g = VGroup()
        d = _stage("download", T.BLUE, w=1.45, n=2).move_to(P(1.45, 0.6))
        r = _stage("resize", T.AMBER, w=1.45, n=3).move_to(P(3.7, 0.6))
        u = _stage("upload", T.GREEN, w=1.45, n=2).move_to(P(5.85, 0.6))
        g.add(d, r, u)
        g.add(_pipe(d, r, cap=2, items=("i", "i")), _pipe(r, u, cap=2, items=("i",)))
        g.add(txt("I/O bound: limit by\nconnections", size=13, color=T.BLUE, align="CENTER").next_to(d.box, DOWN, buff=0.25))
        g.add(txt("CPU bound: about\none per core", size=13, color=T.AMBER, align="CENTER").next_to(r.box, DOWN, buff=0.25))
        g.add(txt("I/O bound: limit by\nthe server's quota", size=13, color=T.GREEN, align="CENTER").next_to(u.box, DOWN, buff=0.25))
        g.add(txt("stages run concurrently; channels connect them", size=15, color=T.TEXT2).move_to(P(3.65, -1.9)))
        return g


class C15Generator(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Generator: a goroutine that produces a stream"
    SUB = "A function starts a goroutine and returns the receive end of a channel. The caller ranges over the channel as values arrive."

    def build(self):
        w = 6.4
        cd = code_ex("ch15_generator", lines=(8, 36), size=12, width=w, hl=[9, 12, 16, 18, 28],
                     marks={9: "1", 12: "2", 18: "3", 28: "4"})
        self.at(cd, X0, Y0)
        x = X0 + w + 0.45
        ww = X1 - x
        gen = _stage("fib goroutine", T.GO, w=1.9, n=1).move_to(P(x + 1.0, Y0 - 1.0))
        con = _stage("main: range", T.VIOLET, w=1.9, n=1, mood="happy").move_to(P(X1 - 0.95, Y0 - 1.0))
        self.add(gen, con, _pipe(gen, con, cap=3, items=("2", "1", "1"), cell=0.42))
        ctxn = node("cancel()  →  ctx.Done()", w=2.6, h=0.42, color=T.RED, size=12).move_to(P(x + ww / 2, Y0 - 2.1))
        self.add(ctxn, arrow(ctxn.get_left(), gen.box.get_bottom() + RIGHT * 0.3, T.RED, 2, 0.04))
        self.add(Line(con.box.get_bottom(), P(con.box.get_center()[0], ctxn.get_center()[1])).set_stroke(T.RED, 2),
                 Line(P(con.box.get_center()[0], ctxn.get_center()[1]), ctxn.get_right()).set_stroke(T.RED, 2))
        steps = num_steps([("Return a receive-only channel.", "`<-chan int`: callers can only receive; the generator owns it."),
                           ("The owner closes it.", "`defer close(out)`, so `range` in the caller ends cleanly."),
                           ("Select on the context.", "If the caller stops early, the goroutine is not stuck on a send forever."),
                           ("Break, then cancel.", "The deferred `cancel()` is the consumer's way to say \"enough\".")],
                          width=ww, color=T.GO, size=13, gap=0.08)
        self.at(steps, x, Y0 - 2.6)
        wn = callout("warn", "Without the ctx case, `break` leaves the generator blocked on `out <- a` forever: a "
                     "**goroutine leak** (8.17). Every generator needs a way to be told to stop.",
                     width=ww, size=13)
        self.at(wn, x, steps.get_bottom()[1] - 0.2)
        res = out("ch15_generator").split("\n")[1].strip()
        tm = txt(f"**go run .** prints  {{#E7EEF8|{res}}}", size=13, color=T.GREEN, width=ww)
        self.at(tm, x, wn.get_bottom()[1] - 0.2)


class C15Iter(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Generator or iterator? Measure first"
    SUB = "Go 1.23 range-over-func iterators produce sequences without goroutines or channels. For plain sequences they win by a mile."

    def build(self):
        w = 6.4
        cd = code_ex("ch15_iter", lines=(8, 26), size=14, width=w, hl=[9, 12])
        self.at(cd, X0, Y0)
        tm = terminal(out("ch15_iter"), title="go run .", width=w, size=13)
        self.at(tm, X0, cd.get_bottom()[1] - 0.15)
        x = X0 + w + 0.45
        ww = X1 - x
        text = (EX_DIR / "ch15_genbench" / "output.txt").read_text()
        r = {n: float(v) for n, v in re.findall(r"Benchmark(\w+?)-\d+\s+\d+\s+([\d.]+) ns/op", text)}
        self.at(section("COST PER VALUE (examples/ch15_genbench)", T.AMBER, size=15), x, Y0)
        data = [("unbuffered channel", r["Channel"]), ("channel, cap 64", r["ChannelBuf64"]), ("iter.Seq", r["Iterator"])]
        hb = hbars(data, x, Y0 - 0.6, ww - 3.6, row_h=0.46, size=13, label_w=2.2, fmt="{:.2f}", unit=" ns",
                   colors=[T.RED, T.AMBER, T.GREEN])
        self.add(hb)
        ratio = r["Channel"] / r["Iterator"]
        self.add(txt(f"the iterator is about **{ratio:,.0f}×** cheaper: the compiler inlines the loop body; a channel "
                     "needs two goroutines to meet for every value", size=13, color=T.TEXT2, width=ww)
                 .move_to(P(x, Y0 - 1.95), aligned_edge=UL))
        tbl = table([["", "channel generator", "iter.Seq"],
                     ["extra goroutine", "yes", "no"],
                     ["leaks if caller stops early", "yes, unless ctx", "no: yield returns false"],
                     ["producer runs in parallel", "yes", "no, it runs in the loop"],
                     ["good for", "I/O, slow producers, many consumers", "walking data, lazy sequences"]],
                    widths=[2.1, (ww - 2.1) / 2, (ww - 2.1) / 2], size=12)
        self.at(tbl, x, Y0 - 2.75)
        k = callout("key", "Use a channel when the producer should run **concurrently** with the consumer. For "
                    "\"give me the next value\", use an iterator.", width=ww, size=13, inline=True)
        self.at(k, x, tbl.get_bottom()[1] - 0.2)


class C15Pipeline(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Pipeline: stages connected by channels"
    SUB = "Each stage receives from an inbound channel, does one job, and sends on an outbound channel. All stages run at the same time."

    def build(self):
        w = 6.4
        cd = code_ex("ch15_pipeline", lines=(23, 45), size=13, width=w, hl=[24, 26, 27, 29, 30, 42],
                     marks={26: "1", 27: "2", 30: "3"})
        self.at(cd, X0, Y0)
        note = txt("`gen` (lines 8-21) has the same shape: it sends its arguments, then closes `out`.",
                   size=13, color=T.TEXT2, width=w)
        self.at(note, X0, cd.get_bottom()[1] - 0.15)
        x = X0 + w + 0.45
        ww = X1 - x
        sw = 1.25
        names = [("gen", T.BLUE), ("square", T.AMBER), ("square", T.AMBER), ("main", T.VIOLET)]
        stages = []
        gap = (ww - 4 * sw) / 3
        for i, (n, c) in enumerate(names):
            s = _stage(n, c, w=sw, h=0.5, n=1, size=12)
            s.move_to(P(x + sw / 2 + i * (sw + gap), Y0 - 0.85))
            stages.append(s)
            self.add(s)
        for a, b in zip(stages, stages[1:]):
            self.add(arrow(a.box.get_right(), b.box.get_left(), T.GREEN, 2.4, 0.04))
        vals = [["1 2 3 4"], ["1 4 9 16"], ["1 16 81 256"]]
        for i, (a, b) in enumerate(zip(stages, stages[1:])):
            self.add(txt(vals[i][0], size=11, color=T.PINK, font=T.MONO).move_to(
                P((a.box.get_right()[0] + b.box.get_left()[0]) / 2, a.box.get_center()[1] - 0.42)))
        tm = terminal(out("ch15_pipeline"), title="go run .", width=2.4, size=13)
        self.at(tm, X1 - 2.4, Y0 - 1.75)
        rules = num_steps([("range over in:", "the stage ends when its inbound channel is closed."),
                           ("defer close(out):", "when a stage is done sending, it closes its outbound channel, "
                            "which ends the next stage."),
                           ("select on ctx.Done():", "if the consumer quits, every stage unblocks and returns. "
                            "One cancel tears down the whole pipeline.")],
                          width=ww - 2.6, color=T.GREEN, size=13, gap=0.1)
        self.at(rules, x, Y0 - 1.75)
        q = callout("note", "These rules come from the Go blog post \"Go Concurrency Patterns: Pipelines and "
                    "cancellation\" (Sameer Ajmani, 2014): stages close their outbound channels when all sends are "
                    "done, and keep receiving until inbound channels are closed or senders are unblocked.",
                    width=ww, size=12, title="SOURCE")
        self.at(q, x, min(rules.get_bottom()[1], tm.get_bottom()[1]) - 0.25)


class C15FanInOut(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Fan-out and fan-in"
    SUB = "Fan-out: several goroutines receive from one channel and share the work. Fan-in: several channels are merged into one."

    def build(self):
        w = 6.4
        cd = code_ex("ch15_fanin", lines=(21, 43), size=12, width=w, hl=[22, 26, 27, 28, 32], marks={26: "1", 32: "2"})
        self.at(cd, X0, Y0)
        st = bullets([(badge("1", T.YELLOW, r=0.12, size=11), "one forwarding goroutine per input channel"),
                      (badge("2", T.YELLOW, r=0.12, size=11), "a separate goroutine closes `out` after **all** "
                       "forwarders finish; no forwarder may close it alone")],
                     width=w, size=12, gap=0.05)
        self.at(st, X0, cd.get_bottom()[1] - 0.2)
        x = X0 + w + 0.45
        ww = X1 - x
        # merge diagram
        pa = node("producer a (30 ms)", w=2.2, h=0.44, color=T.GO, size=12).move_to(P(x + 1.1, Y0 - 0.3))
        pb = node("producer b (45 ms)", w=2.2, h=0.44, color=T.ORANGE, size=12).move_to(P(x + 1.1, Y0 - 1.0))
        mg = node("merge → out", w=1.7, h=0.95, color=T.GREEN, size=13).move_to(P(x + 3.6, Y0 - 0.65))
        mn = node("main", w=1.05, h=0.5, color=T.VIOLET, size=13).move_to(P(X1 - 0.53, Y0 - 0.65))
        self.add(pa, pb, mg, mn, arrow(pa.get_right(), mg.get_left() + UP * 0.2, T.GO, 2.2, 0.04),
                 arrow(pb.get_right(), mg.get_left() + DOWN * 0.2, T.ORANGE, 2.2, 0.04),
                 arrow(mg.get_right(), mn.get_left(), T.GREEN, 2.4, 0.04))
        # timeline of sends
        x0 = x + 0.9
        unit = (X1 - x0 - 0.2) / 140
        y = Y0 - 1.75
        for lab, col, d, yy in (("a", T.GO, 30, y), ("b", T.ORANGE, 45, y - 0.45)):
            self.add(txt(f"**{lab}**", size=13, color=col).move_to(P(x0 - 0.15, yy), aligned_edge=RIGHT))
            self.add(dashed(P(x0, yy), P(X1, yy), T.STROKE2, 1, 0.05))
            for k in range(3):
                t_ = d * (k + 1)
                self.add(Dot(P(x0 + t_ * unit, yy), radius=0.07, fill_color=col))
                self.add(txt(f"{lab}{k}", size=11, color=col, font=T.MONO).next_to(P(x0 + t_ * unit, yy), UP, buff=0.08))
        self.add(time_axis(x0, X1, y - 0.85, ticks=[(x0 + t * unit, f"{t}") for t in (0, 30, 45, 60, 90, 135)], lab="ms"))
        order = out("ch15_fanin").split("\n")[1].split()
        self.add(txt("**go run . printed:** " + "  ".join(order), size=13, color=T.GREEN, font=T.SANS)
                 .move_to(P(x, y - 1.55), aligned_edge=LEFT))
        k = callout("key", "Fan-in interleaves by **arrival time**, not by source. When order matters, carry an index "
                    "with each value (see the ordered-results page).", width=ww, size=12)
        self.at(k, x, y - 1.95)
        fo = callout("def", "**Fan-out** is the mirror image: start N goroutines that all `range` over the same "
                     "input channel. Each value goes to exactly one of them. The worker pool on the next page is fan-out "
                     "plus fan-in.", width=ww, size=12)
        self.at(fo, x, k.get_bottom()[1] - 0.18)


class C15WorkerPool(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Worker pool: a fixed team pulls from a queue"
    SUB = "N long-lived goroutines range over a jobs channel. Whoever is free takes the next job, so fast workers simply do more."

    def build(self):
        w = 6.4
        cd = code_ex("ch15_workerpool", lines=(14, 38), size=13, width=w, hl=[15, 26, 27, 32, 34],
                     marks={15: "1", 32: "2", 34: "3"})
        self.at(cd, X0, Y0)
        st = bullets([(badge("1", T.YELLOW, r=0.12, size=11), "each worker loops until `jobs` is closed and drained"),
                      (badge("2", T.YELLOW, r=0.12, size=11), "closing `jobs` is how main says \"no more work\""),
                      (badge("3", T.YELLOW, r=0.12, size=11), "close `results` only after every worker returned")],
                     width=w, size=13, gap=0.06)
        self.at(st, X0, cd.get_bottom()[1] - 0.2)
        x = X0 + w + 0.45
        ww = X1 - x
        tm = terminal(out("ch15_workerpool"), title="go run .", width=ww, size=12)
        self.at(tm, x, Y0)
        rows = re.findall(r"job (\d+) -> +\d+ \(worker (\d+)\)", out("ch15_workerpool"))
        dur = {i + 1: n * 10 for i, n in enumerate([5, 1, 3, 2, 4, 1])}
        per = {}
        for j, wk in rows:
            per.setdefault(int(wk), []).append(int(j))
        y0 = tm.get_bottom()[1] - 0.45
        x0 = x + 1.2
        dur_max = max(sum(dur[j] for j in js) for js in per.values()) if per else 60
        unit = (X1 - x0 - 0.1) / max(dur_max, 60)
        cols = [T.GO, T.ORANGE, T.VIOLET]
        for i, wk in enumerate(sorted(per)):
            yy = y0 - i * 0.5
            self.add(txt(f"**worker {wk}**", size=12, color=cols[i % 3]).move_to(P(x0 - 0.12, yy), aligned_edge=RIGHT))
            t = 0
            for j in sorted(per[wk]):
                self.add(seg(x0 + t * unit, x0 + (t + dur[j]) * unit - 0.03, yy, cols[i % 3], h=0.34, lab=f"job {j}", size=11))
                t += dur[j]
        yb = y0 - len(per) * 0.5 - 0.05
        self.add(time_axis(x0, X1, yb, ticks=[(x0 + t * unit, str(t)) for t in range(0, max(dur_max, 60) + 1, 20)], lab="ms"))
        self.add(txt("job lengths 50, 10, 30, 20, 40, 10 ms; the busy-until times balance out by themselves",
                     size=12, color=T.TEXT2, width=ww).move_to(P(x, yb - 0.45), aligned_edge=UL))
        k = callout("tip", "**How many workers?** CPU-bound work: about `runtime.GOMAXPROCS(0)`. I/O-bound work: as "
                    "many as the slowest shared resource allows (DB connections, API quota), found by measuring.",
                    width=ww, size=12)
        self.at(k, x, yb - 0.95)


class C15Semaphore(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Semaphore: at most N at a time"
    SUB = "Sometimes you want one goroutine per task but a cap on how many run at once. A buffered channel of capacity N is a counting semaphore."

    def build(self):
        w = 6.4
        cd = code_ex("ch15_semaphore", lines=(10, 33), size=13, width=w, hl=[11, 17, 18], marks={17: "1", 18: "2"})
        self.at(cd, X0, Y0)
        tm = terminal(out("ch15_semaphore"), title="go run .", width=w, size=13)
        self.at(tm, X0, cd.get_bottom()[1] - 0.15)
        x = X0 + w + 0.45
        ww = X1 - x
        sem = chan_pipe(3, ("T", "T", "T"), cell=0.48, color=T.GREEN, item_color=T.YELLOW)
        self.at(sem, x + 1.6, Y0 - 0.15)
        self.add(txt("**sem**: cap 3", size=13, color=T.GREEN).next_to(sem, LEFT, buff=0.2))
        waiting = VGroup(*[gtok(f"G{i}", T.GREY, w=0.62, h=0.32, state="wait", size=10) for i in range(4, 11)]).arrange(RIGHT, buff=0.06)
        self.at(waiting, x, Y0 - 0.95)
        self.add(txt("blocked on sem <- struct{}{} until a slot frees", size=12, color=T.TEXT2).next_to(waiting, DOWN, buff=0.08, aligned_edge=LEFT))
        y0 = Y0 - 2.0
        x0 = x + 0.9
        unit = (X1 - x0 - 0.1) / 85
        for s in range(3):
            yy = y0 - s * 0.45
            self.add(txt(f"slot {s + 1}", size=12, color=T.GREEN).move_to(P(x0 - 0.1, yy), aligned_edge=RIGHT))
            k = 0
            for t in range(s, 10, 3):
                a = k * 20
                self.add(seg(x0 + a * unit, x0 + (a + 20) * unit - 0.04, yy, T.GO, h=0.32, lab=f"task {t + 1}", size=10))
                k += 1
        self.add(time_axis(x0, X1, y0 - 1.4, ticks=[(x0 + t * unit, str(t)) for t in (0, 20, 40, 60, 80)], lab="ms"))
        tbl = table([["tool", "when"],
                     ["`chan struct{}` with cap N", "simplest; no extra package"],
                     ["`errgroup.Group.SetLimit(n)`", "tasks can fail; cancel the rest on error"],
                     ["`semaphore.NewWeighted(n)`", "tasks take different weights; `Acquire(ctx, w)`"]],
                    widths=[3.0, ww - 3.0], size=12)
        self.at(tbl, x, y0 - 2.0)


class C15Ordered(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Results in order, computed in any order"
    SUB = "Goroutines finish in random order. Give each one its own slot in a pre-sized slice and the order takes care of itself."

    def build(self):
        w = 6.4
        cd = code_ex("ch15_ordered", lines=(10, 23), size=14, width=w, hl=[12, 18, 21], marks={12: "1", 18: "2", 21: "3"})
        self.at(cd, X0, Y0)
        tm = terminal(out("ch15_ordered"), title="go run . (same output every run)", width=w, size=13)
        self.at(tm, X0, cd.get_bottom()[1] - 0.15)
        st = num_steps([("Pre-size", "the result slice: one element per input."),
                        ("Write only out[i]:", "every goroutine touches a different element, so there is no race and no lock."),
                        ("Wait, then read:", "`wg.Wait()` is the happens-before edge that makes all writes visible.")],
                       width=w, color=T.YELLOW, size=13, gap=0.08)
        self.at(st, X0, tm.get_bottom()[1] - 0.2)
        x = X0 + w + 0.45
        ww = X1 - x
        names = ["alpha", "bravo", "charlie", "delta", "echo"]
        finish = [3, 1, 4, 0, 2]  # an example finish order
        cw_ = (ww - 0.2) / 5
        self.add(txt("**finish order (random)**", size=13, color=T.TEXT2).move_to(P(x, Y0), aligned_edge=UL))
        for k, i in enumerate(finish):
            self.add(gtok(names[i], T.GO, w=cw_ - 0.08, h=0.36, size=11).move_to(P(x + cw_ * (k + 0.5), Y0 - 0.55)))
        self.add(txt("**out slice (fixed slots)**", size=13, color=T.TEXT2).move_to(P(x, Y0 - 1.25), aligned_edge=UL))
        for i, n in enumerate(names):
            c = node(f"{n}:{len(n)}", w=cw_ - 0.08, h=0.42, color=T.GREEN, size=11).move_to(P(x + cw_ * (i + 0.5), Y0 - 2.15))
            self.add(c, txt(f"[{i}]", size=11, color=T.MUTED, font=T.MONO).next_to(c, DOWN, buff=0.06))
        for k, i in enumerate(finish):
            self.add(arrow(P(x + cw_ * (k + 0.5), Y0 - 0.75), P(x + cw_ * (i + 0.5), Y0 - 1.92), T.MUTED, 1.4, 0.02))
        wn = do_dont("results = append(results, r) // from many goroutines",
                     "out[i] = r // one slot per goroutine", width=ww, size=12, vertical=True, gap=0.15,
                     bad_note="append reads and writes the shared slice header: a data race and lost results.",
                     good_note="distinct elements are distinct memory locations.")
        self.at(wn, x, Y0 - 2.75)


class C15Choose(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Patterns at a glance"
    SUB = "Match the shape of the problem to a pattern. Each one has a rule that keeps it from leaking or racing."

    def build(self):
        rows = [["pattern", "use it when", "shape", "the rule that keeps it safe"],
                ["generator", "a stream produced by one goroutine", "go f() → chan", "owner closes; select on ctx.Done() when sending"],
                ["iterator", "a lazy sequence, consumed in a loop", "iter.Seq", "no goroutine: prefer it when no concurrency is needed"],
                ["pipeline", "work passes through steps", "stage → stage → stage", "close outbound when done; one cancel stops all stages"],
                ["fan-out", "spread one stream over many workers", "1 chan → N goroutines", "each value is received exactly once"],
                ["fan-in", "merge many streams into one", "N chans → 1 chan", "close the merged channel after all inputs end"],
                ["worker pool", "many jobs, a bounded team", "jobs chan → N workers → results", "close jobs to stop; close results after wg.Wait"],
                ["semaphore", "one goroutine per task, capped", "chan struct{} with cap N", "acquire before work, release in defer"],
                ["errgroup", "tasks that can fail together", "g.Go(f); g.Wait()", "first error cancels the shared ctx (8.4)"],
                ["indexed results", "output order must match input", "out[i] = …", "each goroutine writes only its own slot"]]
        tbl = table(rows, widths=[1.75, 3.4, 3.0, CW - 8.15], size=13, col_colors=[T.GO, None, T.YELLOW, None])
        self.at(tbl, X0, Y0)
        k = callout("key", "Every pattern answers the same three questions: **who closes** each channel, **how does it "
                    "stop** early, and **how many** goroutines run at once. Answer them before you write the code.",
                    width=CW, size=14, inline=True)
        self.at(k, X0, tbl.get_bottom()[1] - 0.3)


class C15Recap(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Recap and check yourself"
    SUB = "Small, composable patterns; three questions for each: who closes, how it stops, how many run."

    def build(self):
        self.at(section("REMEMBER", T.GO), X0, Y0)
        rec = bullets([
            "Generators return `<-chan T`, close it themselves, and watch `ctx.Done()`.",
            "Iterators (`iter.Seq`) are hundreds of times cheaper when no concurrency is needed.",
            "Pipelines: range over in, `defer close(out)`, select on ctx for every send.",
            "Fan-in needs a separate closer goroutine waiting on all forwarders.",
            "Worker pools: close jobs to stop; close results after `wg.Wait()`.",
            "A buffered `chan struct{}` of cap N is a semaphore; `errgroup.SetLimit` too.",
            "Write results into `out[i]`, never `append` from many goroutines.",
        ], width=6.1, size=15, marker="check", marker_color=T.GREEN, gap=0.12)
        self.at(rec, X0, Y0 - 0.5)
        x = 0.55
        self.at(section("CHECK YOURSELF", T.TEAL), x, Y0)
        qs = [("In a fan-in, why can't each forwarder `close(out)` when its input ends?",
               "The others may still send: a send on a closed channel panics. Close once, after all finish."),
              ("A pipeline's consumer returns early. What stops the upstream stages?",
               "The cancelled ctx: every send selects on `ctx.Done()` and returns."),
              ("Your worker pool processes CPU-heavy jobs on 8 cores. How many workers?",
               "About 8 (`runtime.GOMAXPROCS(0)`); more only adds switching."),
              ("When is a channel generator better than an iterator?",
               "When the producer should run concurrently: I/O, slow sources, several consumers.")]
        y = Y0 - 0.5
        for i, (q, a_) in enumerate(qs):
            grp = vstack(txt(f"**Q{i + 1}.** {q}", size=15, color=T.TEXT, width=6.0),
                         txt(f"{{teal|**Answer.**}} {a_}", size=14, color=T.TEXT2, width=6.0), buff=0.08)
            self.at(grp, x, y)
            y = grp.get_bottom()[1] - 0.26
