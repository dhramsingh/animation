from kit import *

CH, NAME = "8.6", "Buffers, close and range"


def axioms():
    """Parse examples/ch06_axioms output into {state: {op: result}}."""
    rows = {}
    for line in out("ch06_axioms").split("\n")[1:]:
        parts = [p.strip() for p in line.split("|")]
        st = parts[0]
        rows[st] = {k.split(":", 1)[0]: k.split(":", 1)[1].strip() for k in parts[1:]}
    return rows


class C6Opener(Opener):
    NUM, NAME = CH, NAME
    TAGLINE = "A buffer lets a sender run ahead of its receiver. `close` says that no more values are coming. Together they shape the life of every channel."
    LEARN = ["Use buffered channels as bounded FIFO queues",
             "Choose between unbuffered, size 1 and size N, with data",
             "Close channels, drain them, and loop with `range`",
             "Recite the channel axioms, verified by experiment",
             "Decide who closes a channel when there are many senders"]
    QUESTION = "A channel has a buffer of 3 and nobody is receiving. What happens on the fourth send?"

    def art(self):
        g = VGroup()
        pipe = chan_pipe(3, ["1", "2", "3"], cell=0.75).move_to(P(4.3, 0.6))
        snd = gopher(1.3, mood="blocked", look=(0.6, 0)).move_to(P(1.6, 0.6))
        box4 = msg("4", T.PINK, s=0.55).next_to(snd, RIGHT, buff=0.12)
        g.add(pipe, snd, box4)
        g.add(txt("**full**: the 4th send waits", size=16, color=T.AMBER).next_to(pipe, DOWN, buff=0.3))
        g.add(txt("cap = 3, len = 3", size=14, color=T.TEXT2, font=T.MONO).next_to(pipe, UP, buff=0.25))
        rcv = gopher(1.1, mood="sleep").move_to(P(5.7, -1.6))
        g.add(rcv, txt("the receiver is busy elsewhere", size=13, color=T.MUTED).next_to(rcv, DOWN, buff=0.08))
        return g


class C6Buffered(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Buffered channels: a queue with a capacity"
    SUB = "`make(chan T, n)` holds up to n values. A send blocks only when the buffer is full; a receive blocks only when it is empty. Order is FIFO."

    def build(self):
        cd = code_ex("ch06_buffered", lines=(5, 18), size=14, hl=[6, 9, 10, 13, 16])
        self.at(cd, X0, Y0)
        tm = terminal(out("ch06_buffered"), title="output", width=cd.get_width(), size=13)
        self.at(tm, X0, cd.get_bottom()[1] - 0.15)
        x = cd.get_right()[0] + 0.55
        w = X1 - x
        frames = [("make(chan string, 3)", [], "len 0", None),
                  ('ch <- "a"; ch <- "b"', ["a", "b"], "len 2: sends did not wait", None),
                  ('ch <- "c"', ["a", "b", "c"], "len 3: full", None),
                  ('ch <- "d"  (would block)', ["a", "b", "c"], "a 4th sender waits for room", "d"),
                  ("<-ch  returns \"a\"", ["b", "c"], "oldest value leaves first", None)]
        y = Y0
        for i, (lab, items, note, waiting) in enumerate(frames):
            col = T.AMBER if waiting else T.GREEN
            self.add(badge(str(i + 1), col, r=0.14, size=12).move_to(P(x + 0.15, y - 0.45)))
            self.add(mono(lab, size=13, color=T.YELLOW).move_to(P(x + 0.45, y - 0.2), aligned_edge=LEFT))
            p = chan_pipe(3, items, cell=0.42).move_to(P(x + 1.75, y - 0.68))
            self.add(p)
            if waiting:
                gg = gtok("G", w=0.5, h=0.26, state="wait", eyes=False).next_to(p, LEFT, buff=0.12)
                self.add(gg, msg(waiting, T.PINK, s=0.26, size=10).next_to(gg, UP, buff=0.04))
            if i == 4:
                self.add(msg("a", T.PINK, s=0.3, size=11).next_to(p, RIGHT, buff=0.15))
            self.add(txt(note, size=13, color=T.TEXT2, width=w - 3.3).move_to(P(x + 3.2, y - 0.68), aligned_edge=LEFT))
            y -= 1.1
        self.add(txt("head of the queue →", size=11, color=T.MUTED).move_to(P(x + 2.75, Y0 - 0.25), aligned_edge=LEFT))


class C6Sizing(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Unbuffered, size 1 or size N?"
    SUB = "A buffer changes timing and throughput, never correctness. Choose the size for a reason you can write down."

    def build(self):
        rows = [["Capacity", "What it guarantees", "Typical use"],
                ["0 (unbuffered)", "the receiver **has** the value when the send returns", "hand-off, request/reply, strict lock-step"],
                ["1", "one value can wait; the sender never blocks once", "a single result from a goroutine that may be abandoned (8.8 timeout)"],
                ["N (known)", "exactly N sends never block", "N workers each send one result; a semaphore of N slots (8.15)"],
                ["N (large)", "absorbs bursts while the consumer catches up", "smoothing a bursty producer; batching"]]
        tb = table(rows, [1.75, 2.85, 3.0], size=13)
        self.at(tb, X0, Y0)
        w1 = callout("warn", "A buffer does not fix a deadlock, it **postpones** it: if the receiver never comes, the "
                     "(N+1)th send blocks forever just like the first one would have.", width=tb.get_width(), size=14)
        self.at(w1, X0, tb.get_bottom()[1] - 0.25)
        tip = callout("tip", "Unbuffered is the default to reach for. Add a buffer when you can say **why**, and size it "
                      "from the design (\"one slot per worker\"), not from a guess like 100.", width=tb.get_width(), size=14)
        self.at(tip, X0, w1.get_bottom()[1] - 0.18)
        # measured chart
        x = tb.get_right()[0] + 0.55
        w = X1 - x
        self.at(section("COST PER VALUE (measured)", T.GO), x, Y0)
        data = [(int(c), float(v)) for c, v in re.findall(r"cap (\d+)\s+(\d+) ns", out("ch06_bufbench"))]
        vmax = max(v for _, v in data)
        y = Y0 - 0.7
        W = w - 1.6
        for c, v in data:
            self.add(txt(f"cap {c}", size=14, color=T.TEXT2, font=T.MONO).move_to(P(x + 0.95, y), aligned_edge=RIGHT))
            L = W * v / vmax
            bar = RoundedRectangle(width=L, height=0.32, corner_radius=0.05).set_fill(T.GO, 0.9).set_stroke(width=0)
            bar.move_to(P(x + 1.1 + L / 2, y))
            self.add(bar, txt(f"**{v:.0f} ns**", size=13, color=T.TEXT).next_to(bar, RIGHT, buff=0.08))
            y -= 0.5
        cap = txt("One producer sends 2,000,000 ints to one consumer (best of 3 runs, `examples/ch06_bufbench`).",
                  size=12, color=T.MUTED, width=w)
        self.at(cap, x, y + 0.05)
        expl = bullets(["Unbuffered: every value needs both goroutines to meet, so they wake each other constantly.",
                        "A small buffer lets the producer run ahead and the consumer drain in batches.",
                        f"Beyond ~64 slots it stops helping: the per-value cost of the lock and the copy remains."],
                       width=w, size=13, gap=0.06)
        self.at(expl, x, cap.get_bottom()[1] - 0.18)


class C6Close(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "close: no more values are coming"
    SUB = "After `close`, receivers still get every buffered value, then the zero value with ok == false. A `range` loop ends at exactly that point."

    def build(self):
        cd = code_ex("ch06_close_range", lines=(5, 20), size=12, hl=[(11, T.AMBER), 14, (18, T.TEAL)], marks={11: "1", 14: "2", 18: "3"})
        self.at(cd, X0, Y0)
        tm = terminal(out("ch06_close_range"), title="output", width=cd.get_width(), size=12)
        self.at(tm, X0, cd.get_bottom()[1] - 0.12)
        eq = code('''for v := range ch { use(v) }     // is shorthand for:
for { v, ok := <-ch; if !ok { break }; use(v) }''', size=12, numbers=False, width=cd.get_width())
        self.at(eq, X0, tm.get_bottom()[1] - 0.12)
        x = cd.get_right()[0] + 0.55
        w = X1 - x
        frames = [("before close", ["1", "4", "9"], False, "receive gets 1", "v=1 ok=true"),
                  ("closed, 2 left", ["4", "9"], True, "receive still gets 4, then 9", "v=4 ok=true"),
                  ("closed and empty", [], True, "every receive returns at once", "v=0 ok=false")]
        y = Y0
        for i, (t, items, closed, note, res) in enumerate(frames):
            self.add(txt(f"**{t}**", size=14, color=T.AMBER if closed else T.GREEN).move_to(P(x, y - 0.1), aligned_edge=LEFT))
            p = chan_pipe(3, items, cell=0.45, color=T.GREEN if not closed else T.AMBER).move_to(P(x + 1.0, y - 0.72))
            self.add(p)
            if closed:
                self.add(mono("closed", size=12, color=T.AMBER, weight="BOLD").next_to(p, LEFT, buff=0.1).shift(UP * 0.0))
                self.add(Line(p.get_left() + P(0.05, 0.3), p.get_left() + P(0.05, -0.3)).set_stroke(T.AMBER, 6))
            self.add(txt(note, size=13, color=T.TEXT2).move_to(P(x + 2.6, y - 0.6), aligned_edge=LEFT))
            self.add(mono(res, size=13, color=T.TEAL).move_to(P(x + 2.6, y - 0.9), aligned_edge=LEFT))
            y -= 1.3
        notes = bullets([(badge("1", T.YELLOW, r=0.11, size=11), "the **sender** closes, after its last send"),
                         (badge("2", T.YELLOW, r=0.11, size=11), "`range` keeps receiving until closed **and** drained"),
                         (badge("3", T.YELLOW, r=0.11, size=11), "after that, every receive succeeds instantly with ok == false")],
                        width=w, size=14, gap=0.06)
        self.at(notes, x, y + 0.05)
        k = callout("note", "Closing is a **signal**, not cleanup. An unreachable channel is garbage collected whether or "
                    "not it was closed; close only when receivers need to know the stream has ended.", width=w, size=13)
        self.at(k, x, notes.get_bottom()[1] - 0.15)


class C6Axioms(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "The channel axioms, verified by experiment"
    SUB = "examples/ch06_axioms tries every operation on every kind of channel (buffer size 1) and records whether it blocks, succeeds or panics."

    def build(self):
        ax = axioms()
        states = list(ax.keys())
        ops = ["send", "recv", "close"]
        colw = [2.55, 3.4, 3.4, 3.85]
        hdr = ["channel state", "send  `ch <- 1`", "receive  `v, ok := <-ch`", "close  `close(ch)`"]
        x = X0
        y = Y0
        hh = 0.55
        for j, (h, cw_) in enumerate(zip(hdr, colw)):
            b = Rectangle(width=cw_, height=hh).set_fill("#0E2A3A", 1).set_stroke(T.STROKE, 1.2)
            b.move_to(P(x + cw_ / 2, y - hh / 2))
            self.add(b, txt(f"**{h}**" if "`" not in h else h, size=15, color=T.GO).move_to(b))
            x += cw_
        y -= hh
        rh = 0.82
        for st in states:
            x = X0
            b = Rectangle(width=colw[0], height=rh).set_fill(T.PANEL2, 1).set_stroke(T.STROKE, 1.2)
            b.move_to(P(x + colw[0] / 2, y - rh / 2))
            self.add(b, txt(f"**{st}**", size=16, color=T.TEXT).move_to(b))
            x += colw[0]
            for op, cw_ in zip(ops, colw[1:]):
                r = ax[st][op]
                if r.startswith("panic"):
                    col, icon = T.RED, "!"
                elif r == "blocks":
                    col, icon = T.AMBER, "II"
                else:
                    col, icon = T.GREEN, "✓"
                c = Rectangle(width=cw_, height=rh).set_fill(col, 0.13).set_stroke(T.STROKE, 1.2)
                c.move_to(P(x + cw_ / 2, y - rh / 2))
                label = {"blocks": "blocks forever" if st == "nil" else "blocks (until a partner comes)"}.get(r, r)
                t = txt(label, size=14, color=col if col != T.GREEN else T.TEXT, font=T.MONO if r.startswith("v=") else T.SANS,
                        width=cw_ - 0.7, align="CENTER")
                ic = badge(icon, col, r=0.15, size=13).move_to(P(x + 0.3, y - rh / 2))
                t.move_to(P(x + cw_ / 2 + 0.15, y - rh / 2))
                self.add(c, ic, t)
                x += cw_
            y -= rh
        leg = legend_row([(badge("✓", T.GREEN, r=0.12, size=11), "completes"),
                          (badge("II", T.AMBER, r=0.12, size=10), "blocks"),
                          (badge("!", T.RED, r=0.12, size=11), "panics")], size=14, buff=0.5)
        self.at(leg, X0, y - 0.2)
        mem = callout("key", "Learn the three panics: **close(nil)**, **close twice**, **send after close**. "
                      "And the two forever-blocks on a **nil** channel, which `select` turns into a feature (8.8).",
                      width=CW - leg.get_width() - 0.4, size=14, inline=True)
        self.at(mem, X0 + leg.get_width() + 0.4, y - 0.12)


class C6Panics(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Why closing can panic"
    SUB = "A panic here is the runtime telling you that two goroutines disagree about who owns the channel."

    def build(self):
        w = (CW - 0.3) / 2
        a = code_ex("ch06_send_closed", size=15, width=w, hl=[(6, T.RED)])
        self.at(a, X0, Y0)
        ta = terminal(out("ch06_send_closed"), title="output", width=w, size=13)
        self.at(ta, X0, a.get_bottom()[1] - 0.12)
        b = code_ex("ch06_close_closed", size=15, width=w, hl=[(6, T.RED)])
        self.at(b, X0 + w + 0.3, Y0)
        tb = terminal(out("ch06_close_closed"), title="output", width=w, size=13)
        self.at(tb, X0 + w + 0.3, b.get_bottom()[1] - 0.12)
        y = min(ta.get_bottom()[1], tb.get_bottom()[1]) - 0.3
        why = bullets(["A **send after close** means a sender did not know the stream had ended: some other goroutine closed it.",
                       "A **double close** means two goroutines both believed they owned the channel.",
                       "There is no `isClosed(ch)` function on purpose: by the time it returned, the answer could be stale.",
                       "Recovering from these panics hides the real bug. Fix the ownership instead (next page)."],
                      width=CW - 4.4, size=15, gap=0.12, marker="cross", marker_color=T.RED)
        self.at(why, X0, y)
        g = gopher(1.15, mood="dead").move_to(P(X1 - 0.75, y - 0.65))
        bb = bubble("I closed it!  No, I closed it!", width=3.2, tail="right", tail_x=0.0, size=14)
        bb.next_to(g, LEFT, buff=0.3)
        self.add(g, bb)


class C6WhoCloses(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Who closes the channel?"
    SUB = "The rule: **the goroutine that sends closes**, and only when it is sure nobody else will send. Three topologies, three answers."

    def build(self):
        w = (CW - 0.5) / 3
        tops = [("1 sender → many receivers", T.GREEN, "The sender closes after its last send. Every receiver's `range` ends.", (1, 3)),
                ("many senders → 1 receiver", T.AMBER, "No sender may close alone. A **closer** goroutine waits for all of them (WaitGroup), then closes.", (3, 1)),
                ("many senders → many receivers", T.RED, "Do not close the data channel at all. Stop everyone with a separate signal: close a `done` channel or cancel a `context`.", (3, 3))]
        for i, (t, col, d, (ns, nr)) in enumerate(tops):
            x = X0 + i * (w + 0.25)
            bx = rbox(w, 2.75, color=col, fill=T.PANEL, radius=0.15, stroke_width=1.8)
            self.at(bx, x, Y0)
            self.at(txt(f"**{t}**", size=16, color=col), x + 0.18, Y0 - 0.15)
            cy = Y0 - 1.2
            pipe = chan_pipe(2, cell=0.38).move_to(P(x + w / 2, cy))
            ss = VGroup(*[gtok(f"S{k + 1}", w=0.55, h=0.27, eyes=False, size=10) for k in range(ns)]).arrange(DOWN, buff=0.08)
            ss.next_to(pipe, LEFT, buff=0.45)
            rr = VGroup(*[gtok(f"R{k + 1}", w=0.55, h=0.27, eyes=False, size=10, color=T.GO) for k in range(nr)]).arrange(DOWN, buff=0.08)
            rr.next_to(pipe, RIGHT, buff=0.45)
            self.add(pipe, ss, rr)
            for s_ in ss:
                self.add(arrow(s_.get_right(), pipe.get_left(), T.TEXT2, 1.4, 0.03))
            for r_ in rr:
                self.add(arrow(pipe.get_right(), r_.get_left(), T.TEXT2, 1.4, 0.03))
            if i == 0:
                self.add(pill("closes", T.GREEN, size=10).next_to(ss, UP, buff=0.08))
            elif i == 1:
                cl = gtok("closer", w=0.85, h=0.28, size=10, color=T.AMBER).next_to(pipe, UP, buff=0.32)
                self.add(cl, dashed_arrow(cl.get_bottom(), pipe.get_top(), T.AMBER, 1.6))
            else:
                dn = pill("done / ctx", T.RED, size=10, filled=False).next_to(pipe, UP, buff=0.32)
                self.add(dn)
            self.add(txt(d, size=13, color=T.TEXT2, width=w - 0.36).move_to(bx.get_corner(DL) + P(0.18, 0.15), aligned_edge=DL))
        cd = code_ex("ch06_multi_sender", lines=(11, 20), size=12, hl=[(17, T.AMBER), (18, T.AMBER), (19, T.AMBER), (20, T.AMBER)],
                     title="examples/ch06_multi_sender: the closer pattern")
        self.at(cd, X0, Y0 - 2.95)
        x = cd.get_right()[0] + 0.45
        tm = terminal(out("ch06_multi_sender"), title="output", width=X1 - x, size=12)
        self.at(tm, x, Y0 - 2.95)
        k = callout("rule", "Close from the sending side, exactly once, after the last send. "
                    "When ownership is unclear, signal with a separate channel instead.", width=X1 - x, size=13)
        self.at(k, x, tm.get_bottom()[1] - 0.15)


class C6Recap(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Recap and check yourself"
    SUB = "Buffers decouple timing; close ends a stream; range consumes it."

    def build(self):
        data = dict((int(c), float(v)) for c, v in re.findall(r"cap (\d+)\s+(\d+) ns", out("ch06_bufbench")))
        self.at(section("REMEMBER", T.GO), X0, Y0)
        rec = bullets([
            "A buffered channel is a bounded FIFO: send blocks when full, receive blocks when empty.",
            f"Buffers change speed, not correctness: {data[0]:.0f} ns per value unbuffered vs {data[64]:.0f} ns with 64 slots here.",
            "After `close`, buffered values are still delivered; then receives return zero, false.",
            "`for v := range ch` stops when the channel is closed and drained.",
            "Panics: close(nil), close twice, send after close. A nil channel blocks forever.",
            "The sender closes. Many senders: a closer goroutine. Many to many: a separate done signal.",
        ], width=6.0, size=15, marker="check", marker_color=T.GREEN, gap=0.14)
        self.at(rec, X0, Y0 - 0.5)
        x = 0.55
        self.at(section("CHECK YOURSELF", T.TEAL), x, Y0)
        qs = [("`ch := make(chan int, 2); ch <- 1; ch <- 2; close(ch)`. What do three receives return?",
               "1 true, 2 true, then 0 false."),
              ("Is `len(ch) == 0` a safe way to know a channel is drained?",
               "Only as a hint: another goroutine may send right after you look."),
              ("Five workers send results on `results`. Which goroutine should close it?",
               "None of the workers: a closer goroutine that waits for all five (WaitGroup), then closes."),
              ("Your program deadlocks; adding a buffer of 100 \"fixes\" it. Is it fixed?",
               "No. It deadlocks on the 101st value instead. Find the missing receiver.")]
        y = Y0 - 0.5
        for i, (q, a) in enumerate(qs):
            grp = vstack(txt(f"**Q{i + 1}.** {q}", size=15, color=T.TEXT, width=6.0),
                         txt(f"{{teal|**Answer.**}} {a}", size=14, color=T.TEXT2, width=6.0), buff=0.08)
            self.at(grp, x, y)
            y = grp.get_bottom()[1] - 0.28
