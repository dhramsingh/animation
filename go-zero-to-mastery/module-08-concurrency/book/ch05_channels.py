from kit import *

CH, NAME = "8.5", "Channel Basics"


class C5Opener(Opener):
    NUM, NAME = CH, NAME
    TAGLINE = "A channel is a typed pipe between goroutines. Sending and receiving on it is how Go programs hand off work and synchronise."
    LEARN = ["Create channels, send, receive and use comma-ok",
             "Explain why an unbuffered send waits for a receiver",
             "Read and fix the runtime's deadlock error",
             "Restrict channels with direction types: `chan<-` and `<-chan`",
             "Use channels as values: in structs, as replies, as signals"]
    QUESTION = "If a send on an unbuffered channel blocks until someone receives, how can two goroutines ever exchange a value without both getting stuck?"

    def art(self):
        g = VGroup()
        a = gopher(1.45, look=(0.6, 0)).move_to(P(1.75, 0.2))
        b = gopher(1.45, look=(-0.6, 0)).move_to(P(5.95, 0.2))
        ring = chan_pipe(0, cell=0.6).move_to(P(3.85, 0.25))
        v = msg("v", T.PINK, s=0.5).move_to(ring)
        g.add(a, b, ring, v)
        g.add(arrow(a.get_right() + P(0.05, 0.05), ring.get_left() + P(-0.02, 0), T.GREEN, 3))
        g.add(arrow(ring.get_right() + P(0.02, 0), b.get_left() + P(-0.05, 0.05), T.GREEN, 3))
        g.add(mono("ch <- v", size=17, color=T.YELLOW).next_to(a, UP, buff=0.25))
        g.add(mono("v := <-ch", size=17, color=T.YELLOW).next_to(b, UP, buff=0.25))
        g.add(txt("**the hand-off**: both goroutines meet at the channel,\nthe value moves, then both continue",
                  size=15, color=T.TEXT2, align="CENTER").move_to(P(3.85, -1.7)))
        g.add(clock_icon(r=0.3, hour=3).move_to(P(3.85, 1.35)))
        return g


class C5Syntax(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Making, sending and receiving"
    SUB = "The arrow `<-` always points the way the data flows: into the channel for a send, out of it for a receive."

    def build(self):
        rows = [
            ("make", "ch := make(chan int)", "an unbuffered channel of int", T.GO),
            ("make", "ch := make(chan int, 8)", "buffered: room for 8 values (8.6)", T.GO),
            ("send", "ch <- v", "put v in; may block", T.GREEN),
            ("receive", "v := <-ch", "take a value out; may block", T.GREEN),
            ("receive", "v, ok := <-ch", "ok is false once ch is closed and empty", T.GREEN),
            ("receive", "<-ch", "wait and throw the value away", T.GREEN),
            ("close", "close(ch)", "no more values will be sent (8.6)", T.AMBER),
            ("inspect", "len(ch), cap(ch)", "queued values, buffer size", T.VIOLET),
            ("loop", "for v := range ch", "receive until closed and drained", T.PINK),
        ]
        y = Y0
        for kind, code_s, d, col in rows:
            k = pill(kind, col, size=12, filled=False, padx=0.12)
            k.move_to(P(X0 + 0.55, y - 0.24))
            c = mono(code_s, size=17, color=T.TEXT).move_to(P(X0 + 1.3, y - 0.24), aligned_edge=LEFT)
            dd = txt(d, size=14, color=T.TEXT2).move_to(P(X0 + 4.55, y - 0.24), aligned_edge=LEFT)
            self.add(k, c, dd)
            y -= 0.6
            self.add(hline(X0, X0 + 7.6, y + 0.06, T.STROKE, 1))
        # right: the arrow picture
        x = X0 + 8.0
        w = X1 - x
        self.at(section("READ THE ARROW", T.YELLOW), x, Y0)
        pipe1 = chan_pipe(3, cell=0.42).move_to(P(x + w / 2 + 0.45, Y0 - 1.0))
        v1 = msg("v", T.PINK, s=0.36).next_to(pipe1, LEFT, buff=0.55)
        a1 = arrow(v1.get_right(), pipe1.get_left(), T.GREEN, 3)
        l1 = mono("ch <- v", size=18, color=T.YELLOW).next_to(pipe1, DOWN, buff=0.15)
        self.add(pipe1, v1, a1, l1, txt("send", size=13, color=T.GREEN, weight="BOLD").next_to(v1, LEFT, buff=0.15))
        pipe2 = chan_pipe(3, ["v"], cell=0.42).move_to(P(x + w / 2 - 0.45, Y0 - 2.35))
        v2 = msg("v", T.PINK, s=0.36).next_to(pipe2, RIGHT, buff=0.55)
        a2 = arrow(pipe2.get_right(), v2.get_left(), T.GREEN, 3)
        l2 = mono("v := <-ch", size=18, color=T.YELLOW).next_to(pipe2, DOWN, buff=0.15)
        self.add(pipe2, v2, a2, l2, txt("receive", size=13, color=T.GREEN, weight="BOLD").next_to(v2, RIGHT, buff=0.15))
        facts = bullets(["The type is `chan T`; the zero value is **nil** (never ready).",
                         "A channel value is a **pointer** to a runtime struct (`hchan`, 8.7): copying it shares the same channel.",
                         "Channels are comparable: `ch1 == ch2` is true only for the same channel.",
                         "Any type can travel, including other channels and functions."],
                        width=w, size=14, gap=0.1)
        self.at(facts, x, Y0 - 3.2)


class C5Rendezvous(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "An unbuffered channel is a rendezvous"
    SUB = "A send completes only when a receiver takes the value, and a receive completes only when a sender provides one. Whoever arrives first waits."

    def build(self):
        cd = code_ex("ch05_handoff", lines=(8, 24), size=12, hl=[(14, T.PINK), (16, T.GREEN), (21, T.GREEN)],
                     marks={14: "1", 21: "2", 16: "3"})
        self.at(cd, X0, Y0)
        tm = terminal(out("ch05_handoff"), title="output", width=cd.get_width(), size=12)
        self.at(tm, X0, cd.get_bottom()[1] - 0.15)
        x = cd.get_right()[0] + 0.5
        w = X1 - x
        panels = [("1", "sender arrives first", "blocked", "ready? no one", T.AMBER),
                  ("2", "receiver arrives at t = 300 ms", "both ready", "", T.GO),
                  ("3", "value copied, both continue", "done", "", T.GREEN)]
        ph = 1.58
        for i, (n, title, state, extra, col) in enumerate(panels):
            yy = Y0 - i * (ph + 0.1)
            bx = rbox(w, ph, color=col, fill=T.PANEL, radius=0.14, stroke_width=1.6)
            self.at(bx, x, yy)
            self.add(badge(n, col, r=0.15, size=13).move_to(bx.get_corner(UL) + P(0.28, -0.27)))
            self.add(txt(f"**{title}**", size=15, color=T.TEXT).move_to(bx.get_corner(UL) + P(0.55, -0.27), aligned_edge=LEFT))
            cy = yy - ph / 2 - 0.15
            s = gopher(0.78, mood="blocked" if i == 0 else "happy", look=(0.6, 0)).move_to(P(x + 1.0, cy))
            ring = chan_pipe(0, cell=0.42).move_to(P(x + w / 2, cy))
            self.add(s, ring, txt("sender", size=11, color=T.MUTED).next_to(s, DOWN, buff=0.02))
            if i == 0:
                self.add(msg("hello", T.PINK, s=0.4, size=9).next_to(s, RIGHT, buff=0.1))
                self.add(txt("waiting for a receiver...", size=12, color=T.AMBER).move_to(P(x + w - 1.35, cy)))
            else:
                r = gopher(0.78, look=(-0.6, 0)).move_to(P(x + w - 1.0, cy))
                self.add(r, txt("receiver", size=11, color=T.MUTED).next_to(r, DOWN, buff=0.02))
                if i == 1:
                    self.add(msg("hello", T.PINK, s=0.4, size=9).move_to(ring))
                else:
                    self.add(msg("hello", T.PINK, s=0.4, size=9).next_to(r, LEFT, buff=0.1))
                    self.add(check_mark(T.GREEN, 0.18).move_to(P(x + w / 2, cy + 0.45)))
        k = callout("key", "Communication **and** synchronisation: when the send returns, the receiver has the value.",
                    width=cd.get_width(), size=13, inline=True)
        self.at(k, X0, tm.get_bottom()[1] - 0.12)


class C5PingPong(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Ping-pong: two goroutines, one channel"
    SUB = "One unbuffered channel can carry values in both directions. Each pass of the ball is a hand-off from one goroutine to the other."

    def build(self):
        cd = code_ex("ch05_pingpong", size=14, hl=[6, 12, (17, T.GO), 21, 22], marks={6: "1", 12: "2", 21: "3", 22: "4"})
        self.at(cd, X0, Y0)
        x = cd.get_right()[0] + 0.5
        w = X1 - x
        tm = terminal(out("ch05_pingpong"), title="output", width=w, size=14)
        self.at(tm, x, Y0)
        # table illustration
        y = tm.get_bottom()[1] - 1.05
        table_ = rbox(w - 2.4, 0.2, color=T.GREEN, fill=T.GREEN, fill_opacity=0.5, radius=0.05).move_to(P(x + w / 2, y - 0.25))
        net = Line(P(x + w / 2, y - 0.15), P(x + w / 2, y + 0.15)).set_stroke(T.TEXT2, 3)
        p1 = gopher(0.95, look=(0.6, 0.2)).move_to(P(x + 0.6, y))
        p2 = gopher(0.95, look=(-0.6, 0.2)).move_to(P(x + w - 0.6, y))
        ball = Circle(radius=0.1).set_fill(T.YELLOW, 1).set_stroke(width=0).move_to(P(x + w / 2 - 0.6, y + 0.55))
        arc = ArcBetweenPoints(P(x + 1.3, y + 0.15), P(x + w - 1.3, y + 0.15), angle=-0.9).set_stroke(T.YELLOW, 2, 0.6)
        self.add(table_, net, arc, p1, p2, ball)
        self.add(txt("**ping**", size=13, color=T.GO).next_to(p1, DOWN, buff=0.05), txt("**pong**", size=13, color=T.GO).next_to(p2, DOWN, buff=0.05))
        notes = bullets([(badge("1", T.YELLOW, r=0.11, size=11), "`range table` receives the ball (blocks until it is sent)"),
                         (badge("2", T.YELLOW, r=0.11, size=11), "`table <- ball + 1` sends it back; the other player is waiting in its range"),
                         (badge("3", T.YELLOW, r=0.11, size=11), "main serves the first ball: the two players start in any order"),
                         (badge("4", T.YELLOW, r=0.11, size=11), "main blocks on `<-done` until a player closes it")],
                        width=w, size=13, gap=0.06)
        self.at(notes, x, y - 0.75)
        q = callout("q", "Who prints first, ping or pong? Whoever's receive the runtime matches with main's serve. "
                    "Here it was pong; another run may differ.", width=w, size=13)
        self.at(q, x, notes.get_bottom()[1] - 0.15)


class C5Deadlock(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "fatal error: all goroutines are asleep - deadlock!"
    SUB = "If every goroutine is blocked and nothing (a timer, the network) can wake one, the runtime stops the program and prints every goroutine's stack."

    def build(self):
        cd = code_ex("ch05_deadlock", size=16, hl=[(7, T.RED)], marks={7: ("1", T.RED)})
        self.at(cd, X0, Y0)
        tm = terminal(out("ch05_deadlock"), title="output", width=cd.get_width(), size=14)
        self.at(tm, X0, cd.get_bottom()[1] - 0.15)
        ann = bullets([(badge("1", T.RED, r=0.11, size=11), "main sends, but no goroutine will ever receive; main is the only goroutine"),
                       "`[chan send]` in the trace is the wait reason of chapter 8.3's state machine"],
                      width=cd.get_width(), size=14, gap=0.08)
        self.at(ann, X0, tm.get_bottom()[1] - 0.15)
        x = cd.get_right()[0] + 0.5
        w = X1 - x
        g = gopher(1.2, mood="blocked").move_to(P(x + 0.8, Y0 - 0.95))
        pipe = chan_pipe(0, cell=0.5).move_to(P(x + 2.4, Y0 - 0.95))
        v = msg("42", T.PINK, s=0.4).move_to(pipe)
        empty = rbox(1.2, 1.2, color=T.STROKE2, fill=T.BG, fill_opacity=0.2, radius=0.2).move_to(P(x + 4.2, Y0 - 0.95))
        empty.set_stroke(T.STROKE2, 2, 0.8)
        qm = txt("**?**", size=40, color=T.MUTED).move_to(empty)
        self.add(g, pipe, v, empty, qm, arrow(g.get_right(), pipe.get_left(), T.RED, 2.5),
                 dashed_arrow(pipe.get_right(), empty.get_left(), T.MUTED, 2))
        self.add(txt("no receiver exists", size=13, color=T.MUTED).next_to(empty, DOWN, buff=0.08))
        self.at(section("HOW THE RUNTIME KNOWS", T.VIOLET), x, Y0 - 2.0)
        hood = txt("Whenever a thread goes idle, `checkdead()` counts the threads still able to run Go code. "
                   "If none is left and no timer is pending, nothing can ever happen again: the runtime throws "
                   "this fatal error. It cannot be recovered.", size=14, color=T.TEXT2, width=w)
        self.at(hood, x, Y0 - 2.48)
        w2 = callout("warn", "Detection is **global**. If any other goroutine is alive (an HTTP server, a ticker, a "
                     "goroutine in a syscall), a stuck goroutine just hangs silently: a **leak** (8.17).",
                     width=w, size=14)
        self.at(w2, x, hood.get_bottom()[1] - 0.2)
        causes = bullets(["send with no receiver (here)", "receive with no sender, or from a nil channel",
                          "`wg.Wait()` with a counter that never reaches 0", "two goroutines each waiting for the other (8.17)"],
                         width=w, size=13, gap=0.05, marker="cross", marker_color=T.RED)
        self.at(causes, x, w2.get_bottom()[1] - 0.2)


class C5Directions(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Channel directions: chan<- and <-chan"
    SUB = "A function can promise to only send, or only receive. The compiler enforces it, and the signature documents who owns which end."

    def build(self):
        types = [("chan T", "bidirectional", "send and receive", T.GREEN, True, True),
                 ("chan<- T", "send-only", "the arrow points INTO chan: data goes in", T.AMBER, True, False),
                 ("<-chan T", "receive-only", "the arrow comes OUT of chan: data comes out", T.BLUE, False, True)]
        y = Y0
        for t, name, d, col, can_s, can_r in types:
            bx = rbox(6.2, 1.05, color=col, fill=col, fill_opacity=0.07, radius=0.14, stroke_width=1.8)
            self.at(bx, X0, y)
            self.add(mono(t, size=22, color=col, weight="BOLD").move_to(P(X0 + 0.25, y - 0.32), aligned_edge=LEFT))
            self.add(txt(f"**{name}**", size=15, color=T.TEXT).move_to(P(X0 + 2.35, y - 0.32), aligned_edge=LEFT))
            self.add(txt(d, size=13, color=T.TEXT2).move_to(P(X0 + 0.25, y - 0.77), aligned_edge=LEFT))
            for j, (lab, ok) in enumerate((("send", can_s), ("recv", can_r))):
                mk = (check_mark(T.GREEN, 0.12) if ok else cross_mark(T.RED, 0.1))
                grp = VGroup(mk, txt(lab, size=13, color=T.TEXT2)).arrange(RIGHT, buff=0.08)
                grp.move_to(P(X0 + 4.5 + j * 0.85, y - 0.32), aligned_edge=LEFT)
                self.add(grp)
            y -= 1.2
        # producer / consumer picture
        pp = VGroup()
        prod = gtok("producer", w=1.5, h=0.42)
        pipe = chan_pipe(3, ["2", "1"], cell=0.4)
        cons = gtok("consumer", w=1.5, h=0.42)
        row = VGroup(prod, pipe, cons).arrange(RIGHT, buff=0.55)
        self.at(row, X0 + 0.1, y - 0.25)
        self.add(arrow(prod.get_right(), pipe.get_left(), T.AMBER, 2.5), arrow(pipe.get_right(), cons.get_left(), T.BLUE, 2.5))
        self.add(mono("out chan<- int", size=13, color=T.AMBER).next_to(prod, DOWN, buff=0.15))
        self.add(mono("in <-chan int", size=13, color=T.BLUE).next_to(cons, DOWN, buff=0.15))
        conv = callout("note", "A `chan T` converts **implicitly** to either direction (as in `go producer(ch)`). "
                       "The reverse conversion is not allowed.", width=6.2, size=14)
        self.at(conv, X0, y - 1.25)
        x = X0 + 6.55
        w = X1 - x
        cd = code_ex("ch05_direction_error", size=12, width=w, hl=[(5, T.RED), (9, T.RED)], marks={5: ("1", T.RED), 9: ("2", T.RED)})
        self.at(cd, x, Y0)
        tm = terminal(out("ch05_direction_error"), title="the compiler says no", width=w, size=11)
        self.at(tm, x, cd.get_bottom()[1] - 0.15)
        tip = callout("tip", "Return `<-chan T` from producers (8.15): callers cannot send or close by mistake.",
                      width=w, size=13, inline=True)
        self.at(tip, x, tm.get_bottom()[1] - 0.12)


class C5Values(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Channels are values: a channel of replies"
    SUB = "A channel can travel inside a struct or through another channel. Sending a request with its own reply channel gives you a tiny server."

    def build(self):
        cd = code_ex("ch05_reply", lines=(5, 26), size=12, hl=[7, (13, T.GREEN), 21, 22, 23], marks={7: "1", 13: "2", 22: "3", 23: "4"})
        self.at(cd, X0, Y0)
        tm = terminal(out("ch05_reply"), title="output", width=cd.get_width(), size=12)
        self.at(tm, X0, cd.get_bottom()[1] - 0.15)
        x = cd.get_right()[0] + 0.5
        w = X1 - x
        # diagram
        cy = Y0 - 1.25
        mainG = gopher(1.0).move_to(P(x + 0.65, cy))
        srv = gopher(1.0, look=(-0.6, 0)).move_to(P(X1 - 0.65, cy))
        reqs = chan_pipe(2, cell=0.4, lab="reqs").move_to(P(x + w / 2, cy + 0.45))
        reqmsg = VGroup(rbox(0.75, 0.34, color=T.PINK, fill=T.PINK, fill_opacity=0.9, radius=0.05),
                        txt("**n | reply**", size=10, color=T.BG))
        reqmsg[1].move_to(reqmsg[0])
        reqmsg.move_to(reqs.slots[1])
        rep = chan_pipe(1, ["9"], cell=0.4, lab="r.reply", item_color=T.GREEN).move_to(P(x + w / 2, cy - 0.85))
        self.add(mainG, srv, reqs, reqmsg, rep)
        self.add(arrow(mainG.get_right() + UP * 0.35, reqs.get_left(), T.PINK, 2.4))
        self.add(arrow(reqs.get_right(), srv.get_left() + UP * 0.35, T.PINK, 2.4))
        self.add(arrow(srv.get_left() + DOWN * 0.3, rep.get_right() + P(0, 0.05), T.GREEN, 2.4))
        self.add(arrow(rep.get_left() + P(0, 0.05), mainG.get_right() + DOWN * 0.3, T.GREEN, 2.4))
        self.add(txt("main", size=12, color=T.MUTED, weight="BOLD").next_to(mainG, DOWN, buff=0.03))
        self.add(txt("server", size=12, color=T.MUTED, weight="BOLD").next_to(srv, DOWN, buff=0.03))
        notes = bullets([(badge("1", T.YELLOW, r=0.11, size=11), "the request carries **its own reply channel**"),
                         (badge("2", T.YELLOW, r=0.11, size=11), "the server answers on exactly that channel"),
                         (badge("3", T.YELLOW, r=0.11, size=11), "send the request..."),
                         (badge("4", T.YELLOW, r=0.11, size=11), "...then block until the answer arrives")],
                        width=w, size=14, gap=0.06)
        self.at(notes, x, cy - 1.75)
        k = callout("key", "The server's state is touched by **one goroutine only**: no locks are needed. "
                    "This is the “share memory by communicating” idea from chapter 8.1, in code.",
                    width=w, size=14)
        self.at(k, x, notes.get_bottom()[1] - 0.2)


class C5Signals(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Signals: chan struct{} and the close broadcast"
    SUB = "Sometimes the message is the event itself. `struct{}` takes zero bytes, and closing a channel wakes every receiver at once."

    def build(self):
        cd = code_ex("ch05_signal", lines=(9, 27), size=13, hl=[(13, T.GO), (18, T.AMBER), (22, T.GREEN)],
                     marks={17: "1", 18: "2", 22: "3"})
        self.at(cd, X0, Y0)
        tm = terminal(out("ch05_signal"), title="output", width=cd.get_width(), size=13)
        self.at(tm, X0, cd.get_bottom()[1] - 0.15)
        x = cd.get_right()[0] + 0.5
        w = X1 - x
        bw = (w - 0.25) / 2
        for i, (title, col, n_recv, note) in enumerate(
                [("send: wakes ONE receiver", T.GREEN, 1, "`ch <- struct{}{}` is matched with exactly one waiting receiver."),
                 ("close: wakes ALL receivers", T.AMBER, 3, "`close(ch)` makes every current and future receive return at once.")]):
            bx = titled_box(title, bw, 2.5, color=col)
            self.at(bx, x + i * (bw + 0.25), Y0)
            cx = bx.box.get_center()[0]
            src_g = gtok("G0", w=0.7, h=0.32).move_to(P(cx - bw / 2 + 0.55, Y0 - 1.05))
            self.add(src_g)
            for k in range(3):
                rg = gtok(f"R{k + 1}", w=0.6, h=0.3, state="run" if k < n_recv else "wait").move_to(P(cx + bw / 2 - 0.5, Y0 - 0.65 - 0.42 * k))
                self.add(rg)
                if k < n_recv:
                    self.add(arrow(src_g.get_right(), rg.get_left(), col, 2.0, 0.04))
            self.add(txt(note, size=12, color=T.TEXT2, width=bw - 0.3).move_to(bx.box.get_bottom() + UP * 0.42))
        notes = bullets([(badge("1", T.YELLOW, r=0.11, size=11), "the writer stores the data **before** signalling"),
                         (badge("2", T.YELLOW, r=0.11, size=11), "`close(ready)` is synchronised before every receive that sees it closed"),
                         (badge("3", T.YELLOW, r=0.11, size=11), "so each reader is guaranteed to see `config == \"loaded\"`")],
                        width=w, size=14, gap=0.06)
        self.at(notes, x, Y0 - 2.75)
        mm = callout("rule", "Go memory model: **a send happens before the matching receive completes**, and "
                     "**a close happens before a receive that returns because the channel is closed**. "
                     "Chapter 8.13 builds on these rules.", width=w, size=14)
        self.at(mm, x, notes.get_bottom()[1] - 0.2)


class C5Recap(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Recap and check yourself"
    SUB = "Channels carry values and synchronise the goroutines at both ends."

    def build(self):
        self.at(section("REMEMBER", T.GO), X0, Y0)
        rec = bullets([
            "`make(chan T)` is unbuffered: a send waits for a receiver and vice versa (a rendezvous).",
            "The arrow `<-` shows the data flow. `v, ok := <-ch` tells you whether the channel is closed.",
            "All goroutines blocked = fatal deadlock; one goroutine blocked while others run = a silent leak.",
            "`chan<- T` is send-only, `<-chan T` is receive-only; `chan T` converts to either.",
            "Channels are values: put reply channels in requests, return `<-chan T` from producers.",
            "`chan struct{}` + `close` is a zero-byte broadcast signal with a memory-model guarantee.",
        ], width=6.0, size=15, marker="check", marker_color=T.GREEN, gap=0.14)
        self.at(rec, X0, Y0 - 0.5)
        x = 0.55
        self.at(section("CHECK YOURSELF", T.TEAL), x, Y0)
        qs = [("`ch := make(chan int); ch <- 1; fmt.Println(<-ch)` in main. What happens?",
               "Deadlock: the send blocks forever because main itself is the only possible receiver."),
              ("What does a receive from a nil channel do?", "It blocks forever (useful in select, 8.8)."),
              ("Can a function with parameter `in <-chan int` close `in`?",
               "No: closing a receive-only channel is a compile error. Only the sending side closes."),
              ("Why is `chan struct{}` preferred over `chan bool` for signals?",
               "It costs zero bytes per element and says clearly: the event matters, not a value.")]
        y = Y0 - 0.5
        for i, (q, a) in enumerate(qs):
            grp = vstack(txt(f"**Q{i + 1}.** {q}", size=15, color=T.TEXT, width=6.0),
                         txt(f"{{teal|**Answer.**}} {a}", size=14, color=T.TEXT2, width=6.0), buff=0.08)
            self.at(grp, x, y)
            y = grp.get_bottom()[1] - 0.28
        g = gopher(1.0).move_to(P(X0 + 0.9, -2.85))
        b = bubble("Don't wait for me... unless you're unbuffered.", width=3.7, tail="left", tail_x=-0.1)
        b.next_to(g, RIGHT, buff=0.35)
        self.add(g, b)
