from kit import *

CH, NAME = "8.7", "Inside a Channel"

HCHAN_SRC = '''type hchan struct {
    qcount   uint           // values now in the buffer
    dataqsiz uint           // buffer capacity
    buf      unsafe.Pointer // the ring buffer
    elemsize uint16
    closed   uint32
    timer    *timer         // set for time.Timer channels
    elemtype *_type
    sendx    uint           // next slot to write
    recvx    uint           // next slot to read
    recvq    waitq          // parked receivers
    sendq    waitq          // parked senders
    bubble   *synctestBubble
    lock     mutex          // protects all of the above
}

type waitq struct {
    first *sudog
    last  *sudog
}'''


def peek_frames():
    fr = []
    for line in out("ch07_peek").split("\n")[1:]:
        m = re.match(r"(.+?)\s+qcount=(\d+) sendx=(\d+) recvx=(\d+) buf=\[(.*?)\] closed=(\d)", line)
        if m:
            fr.append((m.group(1).strip(), int(m.group(2)), int(m.group(3)), int(m.group(4)),
                       m.group(5).split(), int(m.group(6))))
    return fr


def mini_chan(vals, cap_, sendq=(), recvq=(), cell=0.42, color=T.GREEN, closed=False, label=True):
    """A compact hchan drawing: buffer cells on top, sendq/recvq along the bottom."""
    g = VGroup()
    bw = max(cap_ * (cell + 0.06) + 0.3, 2.9)
    body = rbox(bw, cell + 0.78, color=color, fill=color, fill_opacity=0.06, radius=0.12)
    g.add(body)
    cells = VGroup()
    for i in range(cap_):
        c = rbox(cell, cell, color=color, fill=T.BG, fill_opacity=0.5, radius=0.05, stroke_width=1.3)
        c.move_to(body.get_center() + P((i - (cap_ - 1) / 2) * (cell + 0.06), 0.17))
        cells.add(c)
        g.add(c)
        if i < len(vals) and vals[i]:
            g.add(msg(vals[i], T.PINK, s=cell - 0.1, size=11).move_to(c))
    if cap_ == 0:
        g.add(txt("no buffer", size=11, color=T.MUTED).move_to(body.get_center() + UP * 0.17))
    if closed:
        g.add(pill("closed", T.AMBER, size=9).move_to(body.get_corner(UR) + P(-0.38, -0.2)))
    sq = VGroup(txt("sendq", size=10, color=T.AMBER, weight="BOLD"),
                *[gtok(s_, w=0.42, h=0.22, state="wait", eyes=False, size=9) for s_ in sendq]).arrange(RIGHT, buff=0.06)
    rq = VGroup(txt("recvq", size=10, color=T.BLUE, weight="BOLD"),
                *[gtok(s_, w=0.42, h=0.22, state="wait", eyes=False, size=9) for s_ in recvq]).arrange(RIGHT, buff=0.06)
    sq.move_to(body.get_corner(DL) + P(0.12, 0.2), aligned_edge=LEFT)
    rq.move_to(body.get_corner(DR) + P(-0.12, 0.2), aligned_edge=RIGHT)
    if label:
        g.add(sq, rq)
    g.cells = cells
    g.body = body
    return g


class C7Opener(Opener):
    NUM, NAME = CH, NAME
    TAGLINE = "Open the runtime: a channel is a 112-byte struct holding a lock, a ring buffer and two queues of parked goroutines."
    LEARN = ["Map every field of `runtime.hchan`",
             "Follow `chansend` and `chanrecv` case by case",
             "Explain sudogs, `gopark` and `goready`",
             "Trace a buffered channel through a full storyboard",
             "See why a direct send writes into another goroutine's stack"]
    QUESTION = "A sender finds a receiver already waiting. Why does the value skip the buffer entirely?"

    def art(self):
        g = VGroup()
        shell = rbox(5.3, 4.9, color=T.GREEN, fill=T.PANEL, fill_opacity=0.85, radius=0.25).move_to(P(3.85, 0.1))
        g.add(shell, txt("**runtime.hchan**", size=18, color=T.GREEN).move_to(shell.get_corner(UL) + P(0.25, -0.3), aligned_edge=LEFT))
        g.add(txt("112 bytes", size=13, color=T.MUTED).move_to(shell.get_corner(UR) + P(-0.25, -0.3), aligned_edge=RIGHT))
        # ring buffer
        cx, cy = 2.75, 0.75
        n = 6
        for i in range(n):
            a0 = PI / 2 - i * TAU / n
            sector = AnnularSector(inner_radius=0.55, outer_radius=1.05, angle=TAU / n - 0.08,
                                   start_angle=a0 - TAU / n + 0.04, arc_center=P(cx, cy))
            sector.set_fill(T.PINK if i in (1, 2, 3) else T.BG, 0.85 if i in (1, 2, 3) else 0.4).set_stroke(T.GREEN, 1.5)
            g.add(sector)
        g.add(txt("buf", size=14, color=T.GREEN, weight="BOLD").move_to(P(cx, cy)))
        g.add(txt("ring buffer", size=12, color=T.MUTED).move_to(P(cx, cy - 1.35)))
        lk = lock_icon(s=0.55).move_to(P(5.3, 1.05))
        g.add(lk, txt("lock", size=12, color=T.MUTED).next_to(lk, DOWN, buff=0.08))
        for j, (lab, col) in enumerate((("sendq", T.AMBER), ("recvq", T.BLUE))):
            y = -1.1 - 0.8 * j
            g.add(txt(f"**{lab}**", size=14, color=col).move_to(P(1.6, y), aligned_edge=LEFT))
            for k in range(2 - j):
                gg = gopher(0.55, mood="sleep").move_to(P(3.0 + 0.8 * k, y))
                g.add(gg)
        return g


class C7Hchan(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "runtime.hchan, field by field"
    SUB = "`make(chan T, n)` returns a pointer to this struct. Everything a channel does is a few operations on these fields, under one lock."

    def build(self):
        cd = code(HCHAN_SRC, size=13, title="runtime/chan.go (Go 1.27, comments shortened)",
                  hl=[(2, T.PINK), (3, T.PINK), (4, T.PINK), (9, T.PINK), (10, T.PINK), (11, T.BLUE), (12, T.AMBER), (15, T.RED)])
        self.at(cd, X0, Y0)
        x = cd.get_right()[0] + 0.55
        w = X1 - x
        # memory picture
        box = rbox(w, 3.5, color=T.GREEN, fill=T.PANEL, radius=0.15)
        self.at(box, x, Y0)
        self.add(txt("**hchan (112 bytes)**", size=14, color=T.GREEN).move_to(box.get_corner(UL) + P(0.2, -0.22), aligned_edge=LEFT))
        groups = [("queue", T.PINK, "qcount  dataqsiz  buf  sendx  recvx  elemsize  elemtype"),
                  ("waiters", T.BLUE, "recvq: first, last → sudog list\nsendq: first, last → sudog list"),
                  ("state", T.AMBER, "closed  timer  bubble"),
                  ("lock", T.RED, "one runtime mutex for all of it")]
        yy = Y0 - 0.5
        for name, col, d in groups:
            r = rbox(w - 0.4, 0.62 if "\n" not in d else 0.78, color=col, fill=col, fill_opacity=0.1, radius=0.08)
            self.at(r, x + 0.2, yy)
            self.add(txt(f"**{name}**", size=13, color=col).move_to(r.get_left() + P(0.15, 0), aligned_edge=LEFT))
            self.add(txt(d, size=12, color=T.TEXT2, font=T.MONO, markup=False).move_to(r.get_left() + P(1.1, 0), aligned_edge=LEFT))
            yy -= r.get_height() + 0.08
        self.at(section("WHERE make PUTS THE BUFFER", T.GO), x, Y0 - 3.75)
        rows = [["Element type", "Allocation"],
                ["size 0 (e.g. `struct{}`) or cap 0", "just the 112-byte hchan"],
                ["no pointers (int, [8]byte...)", "hchan and buffer in **one** block"],
                ["contains pointers", "hchan + a separate, GC-scanned buffer"]]
        tb = table(rows, [w * 0.47, w * 0.53], size=12)
        self.at(tb, x, Y0 - 4.2)
        self.add(txt("Sizes read from the DWARF debug info of a Go 1.27.3 binary: hchan 112 B, sudog 104 B, waitq 16 B.",
                     size=11, color=T.MUTED, width=cd.get_width()).move_to(P(X0, cd.get_bottom()[1] - 0.25), aligned_edge=UL))


class C7Ring(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "The ring buffer, observed live"
    SUB = "examples/ch07_peek reads the real hchan fields with unsafe after each operation. Watch sendx and recvx chase each other around a 3-slot ring."

    def build(self):
        fr = peek_frames()
        n = len(fr)
        x = X0
        colw = CW / 4
        for i, (op, qc, sx, rx, buf, closed) in enumerate(fr):
            cx = X0 + (i % 4) * colw + colw / 2
            cy = Y0 - 0.1 - (i // 4) * 1.95
            self.add(txt(f"**{i + 1}. {op}**", size=14, color=T.YELLOW, font=T.MONO).move_to(P(cx, cy)))
            cells = VGroup()
            for k in range(3):
                c = rbox(0.5, 0.5, color=T.GREEN, fill=T.BG, fill_opacity=0.5, radius=0.06, stroke_width=1.8)
                c.move_to(P(cx + (k - 1) * 0.6, cy - 0.78))
                cells.add(c)
                self.add(c, txt(str(k), size=10, color=T.MUTED).next_to(c, DOWN, buff=0.04))
                v = buf[k]
                live = (qc == 3) or (rx <= k < rx + qc) or (k < (rx + qc) - 3)
                if v != "0":
                    self.add(msg(v, T.PINK if live else "#475569", s=0.4, size=12).move_to(c))
            ra = arrow(cells[rx].get_top() + UP * 0.33, cells[rx].get_top() + UP * 0.03, T.BLUE, 2.4, 0)
            self.add(ra, txt("recvx", size=10, color=T.BLUE, weight="BOLD").next_to(ra, LEFT, buff=0.04))
            sa = arrow(cells[sx].get_bottom() + DOWN * 0.48, cells[sx].get_bottom() + DOWN * 0.2, T.GREEN, 2.4, 0)
            self.add(sa, txt("sendx", size=10, color=T.GREEN, weight="BOLD").next_to(sa, LEFT, buff=0.04))
            self.add(txt(f"qcount={qc}" + ("  closed=1" if closed else ""), size=11, color=T.TEXT2, font=T.MONO).move_to(P(cx, cy - 1.62)))
        # last cell: explanation
        cx = X0 + 3 * colw + 0.1
        cy = Y0 - 2.0
        expl = bullets(["**sendx** is where the next send writes; **recvx** where the next receive reads.",
                        "Both wrap to 0 at the end: frame 5 wrote 40 into slot 0.",
                        "A receive clears its slot (`typedmemclr`), so the GC never sees stale pointers.",
                        "Grey values are dead slots: the runtime ignores them."],
                       width=colw - 0.2, size=12, gap=0.06)
        self.at(expl, cx, cy)
        tm = terminal(out("ch07_peek"), title="examples/ch07_peek output (uses unsafe: for learning only)", width=CW, size=11)
        self.at(tm, X0, Y1 + tm.get_height() + 0.02)


class C7Send(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "chansend: four cases, in order"
    SUB = "What `ch <- v` compiles to: a call to runtime.chansend1, which checks these cases in this exact order (runtime/chan.go)."

    def build(self):
        def dn(s, col=T.YELLOW, w=2.5, h=0.85):
            return diamond(s, w=w, h=h, color=col, size=13)

        def nd(s, col, w=3.2, h=0.7):
            return node(s, w=w, h=h, color=col, size=13)
        x0 = X0 + 1.35
        y = Y0 - 0.4
        q0 = dn("ch == nil?").move_to(P(x0, y))
        r0 = nd("park forever: \"chan send (nil chan)\"", T.GREY).move_to(P(x0 + 3.9, y))
        lk = nd("lock(&c.lock)", T.RED, w=2.2, h=0.5).move_to(P(x0, y - 0.85))
        q1 = dn("closed?").move_to(P(x0, y - 1.7))
        r1 = nd("unlock; panic \"send on closed channel\"", T.RED).move_to(P(x0 + 3.9, y - 1.7))
        q2 = dn("receiver waiting in recvq?", w=2.6, h=1.0).move_to(P(x0, y - 2.85))
        r2 = nd("**direct send**: copy v to the receiver's stack, goready(receiver)", T.GREEN, w=3.6, h=0.85).move_to(P(x0 + 4.1, y - 2.85))
        q3 = dn("room in buffer?").move_to(P(x0, y - 4.0))
        r3 = nd("copy v into buf[sendx]; sendx++, qcount++", T.GO, w=3.6).move_to(P(x0 + 4.1, y - 4.0))
        r4 = nd("**park**: sudog on sendq, gopark", T.AMBER, w=2.6, h=0.6).move_to(P(x0, y - 4.95))
        for m in (q0, r0, lk, q1, r1, q2, r2, q3, r3, r4):
            self.add(m)

        def yes(a, b):
            ar = arrow(a.get_right(), b.get_left(), T.GREEN, 2.3)
            self.add(ar, txt("yes", size=12, color=T.GREEN, weight="BOLD").next_to(ar, UP, buff=0.03))

        def no(a, b):
            ar = arrow(a.get_bottom(), b.get_top(), T.RED, 2.3)
            self.add(ar, txt("no", size=12, color=T.RED, weight="BOLD").next_to(ar, LEFT, buff=0.05))
        yes(q0, r0)
        no(q0, lk)
        self.add(arrow(lk.get_bottom(), q1.get_top(), T.TEXT2, 2.3))
        yes(q1, r1)
        no(q1, q2)
        yes(q2, r2)
        no(q2, q3)
        yes(q3, r3)
        no(q3, r4)
        for i, r in enumerate((r2, r3)):
            self.add(badge(str(i + 1), T.YELLOW, r=0.13, size=12).move_to(r.get_corner(UR) + P(-0.05, -0.05)))
        self.add(badge("3", T.YELLOW, r=0.13, size=12).move_to(r4.get_corner(UR) + P(-0.05, -0.05)))
        x = x0 + 6.3
        w = X1 - x
        notes = bullets([(badge("1", T.YELLOW, r=0.12, size=11), "**fastest**: no buffer write at all; one copy, straight into the waiting goroutine's variable"),
                         (badge("2", T.YELLOW, r=0.12, size=11), "the common buffered case: a copy and two counter bumps"),
                         (badge("3", T.YELLOW, r=0.12, size=11), "slow path: the sender sleeps until a receiver takes its value, or the channel closes")],
                        width=w, size=14, gap=0.12)
        self.at(notes, x, Y0)
        hood = callout("hood", "When the parked sender wakes, it checks `sudog.success`. If it was woken by `close` "
                       "instead of a receiver, it panics with \"send on closed channel\" right there.",
                       width=w, size=13)
        self.at(hood, x, notes.get_bottom()[1] - 0.25)
        fast = callout("note", "A `select` with `default` first does a **lock-free** check: open and full means "
                       "\"would block\", so it returns false without touching the lock.", width=w, size=13)
        self.at(fast, x, hood.get_bottom()[1] - 0.18)


class C7Recv(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "chanrecv: the mirror image, with one twist"
    SUB = "`v, ok := <-ch` calls runtime.chanrecv2. The twist: when a sender is parked on a full buffer, the receiver takes the head and moves the sender's value to the tail."

    def build(self):
        def dn(s, w=2.5, h=0.85):
            return diamond(s, w=w, h=h, color=T.YELLOW, size=13)

        def nd(s, col, w=3.4, h=0.7):
            return node(s, w=w, h=h, color=col, size=13)
        x0 = X0 + 1.35
        y = Y0 - 0.4
        q0 = dn("ch == nil?").move_to(P(x0, y))
        r0 = nd("park forever: \"chan receive (nil chan)\"", T.GREY).move_to(P(x0 + 4.0, y))
        lk = nd("lock(&c.lock)", T.RED, w=2.2, h=0.5).move_to(P(x0, y - 0.85))
        q1 = dn("closed AND empty?", w=2.6, h=0.95).move_to(P(x0, y - 1.75))
        r1 = nd("return the zero value, ok = false", T.AMBER).move_to(P(x0 + 4.0, y - 1.75))
        q2 = dn("sender waiting in sendq?", w=2.6, h=1.0).move_to(P(x0, y - 2.9))
        r2 = nd("**recv**: unbuffered → copy from the sender; full buffer → take head, move sender's value to tail; goready(sender)",
                T.GREEN, w=3.9, h=1.1).move_to(P(x0 + 4.25, y - 2.9))
        q3 = dn("values in buffer?").move_to(P(x0, y - 4.05))
        r3 = nd("copy buf[recvx] out, clear it; recvx++, qcount--", T.GO).move_to(P(x0 + 4.0, y - 4.05))
        r4 = nd("**park**: sudog on recvq, gopark", T.BLUE, w=2.6, h=0.6).move_to(P(x0, y - 4.98))
        for m in (q0, r0, lk, q1, r1, q2, r2, q3, r3, r4):
            self.add(m)

        def yes(a, b):
            ar = arrow(a.get_right(), b.get_left(), T.GREEN, 2.3)
            self.add(ar, txt("yes", size=12, color=T.GREEN, weight="BOLD").next_to(ar, UP, buff=0.03))

        def no(a, b):
            ar = arrow(a.get_bottom(), b.get_top(), T.RED, 2.3)
            self.add(ar, txt("no", size=12, color=T.RED, weight="BOLD").next_to(ar, LEFT, buff=0.05))
        yes(q0, r0)
        no(q0, lk)
        self.add(arrow(lk.get_bottom(), q1.get_top(), T.TEXT2, 2.3))
        yes(q1, r1)
        no(q1, q2)
        yes(q2, r2)
        no(q2, q3)
        yes(q3, r3)
        no(q3, r4)
        x = x0 + 6.6
        w = X1 - x
        self.at(section("THE TWIST, DRAWN", T.GREEN), x, Y0)
        before = mini_chan(["1", "2", "3"], 3, sendq=["S"], cell=0.38)
        after = mini_chan(["4", "2", "3"], 3, cell=0.38)
        self.at(txt("before: full, sender S parked with 4", size=12, color=T.TEXT2), x, Y0 - 0.5)
        self.at(before, x, Y0 - 0.8)
        self.at(txt("after one receive", size=12, color=T.TEXT2), x, before.get_bottom()[1] - 0.2)
        self.at(after, x, before.get_bottom()[1] - 0.5)
        self.add(txt("got 1", size=13, color=T.TEAL, weight="BOLD").next_to(after, RIGHT, buff=0.15))
        expl = txt("Slot 0 held the oldest value (1), which goes to the receiver. Since the buffer was full, "
                   "slot 0 is also where the next send would write, so S's value 4 goes there directly and "
                   "S is woken. One copy in, one copy out, FIFO kept.", size=13, color=T.TEXT2, width=w)
        self.at(expl, x, after.get_bottom()[1] - 0.2)


class C7Sudog(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Parking: sudog, gopark and goready"
    SUB = "A goroutine that must wait wraps itself in a sudog (104 bytes), joins the channel's queue and parks. The partner that arrives later wakes it up."

    def build(self):
        su = code('''type sudog struct {
    g    *g                 // the parked goroutine
    next *sudog             // doubly linked
    prev *sudog             //   wait queue
    elem maybeTraceablePtr  // its variable: often ON ITS STACK
    isSelect bool           // part of a select? (8.8)
    success  bool           // woken by a partner, not by close
    c    maybeTraceableChan // which channel
    // + times, ticket, waitlink, parent, ...
}''', size=13, title="runtime/runtime2.go (abridged)", hl=[2, 5, 7])
        self.at(su, X0, Y0)
        steps = num_steps([("G1 receives", "`v := <-ch` finds the buffer empty: G1 fills a sudog with `elem = &v`, enqueues it on `recvq` and calls `gopark`. G1 is now _Gwaiting."),
                           ("G2 sends", "`ch <- 42`: chansend finds G1's sudog on `recvq` and dequeues it."),
                           ("sendDirect", "copies 42 straight into G1's `v`, **on G1's stack**. The buffer is never used."),
                           ("goready(G1)", "G1 becomes runnable, usually in G2's P's `runnext` slot, so it runs very soon.")],
                          width=su.get_width(), color=T.GO, size=14, gap=0.12)
        self.at(steps, X0, su.get_bottom()[1] - 0.3)
        x = su.get_right()[0] + 0.55
        w = X1 - x
        # drawing: channel with recvq -> sudog -> G1 stack
        ch = rbox(2.0, 1.1, color=T.GREEN, fill=T.GREEN, fill_opacity=0.08, radius=0.12)
        self.at(ch, x, Y0 - 0.2)
        self.add(txt("**hchan**", size=14, color=T.GREEN).move_to(ch.get_top() + DOWN * 0.22))
        rq = rbox(1.6, 0.36, color=T.BLUE, fill=T.BLUE, fill_opacity=0.15, radius=0.06).move_to(ch.get_center() + DOWN * 0.15)
        self.add(rq, txt("recvq.first", size=11, color=T.BLUE, font=T.MONO, markup=False).move_to(rq))
        sg = rbox(1.7, 1.1, color=T.VIOLET, fill=T.VIOLET, fill_opacity=0.12, radius=0.1)
        self.at(sg, x + 2.6, Y0 - 0.2)
        self.add(txt("**sudog**", size=13, color=T.VIOLET).move_to(sg.get_top() + DOWN * 0.2))
        self.add(txt("g    →\nelem →", size=12, color=T.TEXT, font=T.MONO, markup=False).move_to(sg.get_center() + DOWN * 0.15))
        self.add(arrow(rq.get_right(), sg.get_left(), T.BLUE, 2.2, 0.03))
        g1 = gopher(0.9, mood="sleep").move_to(P(x + w - 0.6, Y0 - 0.55))
        self.add(g1, txt("G1 (parked)", size=12, color=T.MUTED).next_to(g1, DOWN, buff=0.05))
        stk = VGroup()
        sy = Y0 - 2.05
        for i, (f, hlt) in enumerate((("main()", False), ("v int  = ?", True), ("...", False))):
            r = Rectangle(width=2.0, height=0.4).set_fill(T.PINK if hlt else T.GO_DARK, 0.5 if hlt else 0.35).set_stroke(T.GO, 1.2)
            r.move_to(P(x + w - 1.1, sy - i * 0.42))
            stk.add(r, txt(f, size=12, color=T.TEXT, font=T.MONO, markup=False).move_to(r))
        self.add(stk, txt("G1's stack", size=12, color=T.GO, weight="BOLD").next_to(stk, UP, buff=0.06))
        self.add(arrow(sg.get_right() + UP * 0.12, g1.get_left(), T.TEXT2, 2, 0.04))
        self.add(arrow(sg.get_right() + DOWN * 0.3, stk[2].get_left(), T.PINK, 2, 0.04))
        g2 = gtok("G2: ch <- 42", w=1.9, h=0.4, size=12).move_to(P(x + 1.0, Y0 - 2.45))
        self.add(g2, dashed_arrow(g2.get_right(), stk[2].get_left() + DOWN * 0.08, T.YELLOW, 2.4))
        self.add(txt("sendDirect writes 42 here", size=12, color=T.YELLOW).next_to(g2, DOWN, buff=0.12))
        k = callout("hood", "runtime/chan.go notes that `sendDirect` is **the only place in the runtime where one goroutine "
                    "writes to the stack of another**. It is safe because G1 is parked and the copy happens while "
                    "holding the channel lock, with no preemption point in between.", width=w, size=13)
        self.at(k, x, Y0 - 3.45)


class C7Story(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Storyboard: a fast producer meets a slow consumer"
    SUB = "`ch := make(chan int, 2)`. P sends 1, 2, 3 then closes; C receives slowly. Each panel shows the hchan and both goroutines."

    def build(self):
        panels = [
            ("1. make(chan int, 2)", [], [], [], "P", "run", "C", "run", "empty buffer, no waiters"),
            ("2. P: ch <- 1; ch <- 2", ["1", "2"], [], [], "P", "run", "C", "run", "buffered; P never blocked"),
            ("3. P: ch <- 3", ["1", "2"], ["P"], [], "P", "wait", "C", "run", "full: P parks on sendq with its 3"),
            ("4. C: <-ch gets 1", ["3", "2"], [], [], "P", "run", "C", "run", "head 1 out; P's 3 moved into slot 0; P woken"),
            ("5. C: <-ch, <-ch get 2, 3", [], [], [], "P", "run", "C", "run", "buffer empty again (FIFO kept)"),
            ("6. P: close(ch); C: <-ch", [], [], [], "P", "dead", "C", "run", "closed + empty: C gets 0, ok == false"),
        ]
        pw, ph = (CW - 0.5) / 3, 2.45
        for i, (t, vals, sq, rq, pn, ps, cn, cs, note) in enumerate(panels):
            x = X0 + (i % 3) * (pw + 0.25)
            y = Y0 - (i // 3) * (ph + 0.15)
            bx = rbox(pw, ph, color=T.STROKE2, fill=T.PANEL, radius=0.14)
            self.at(bx, x, y)
            self.add(txt(f"**{t}**", size=14, color=T.YELLOW, font=T.MONO).move_to(P(x + 0.18, y - 0.25), aligned_edge=LEFT))
            mc = mini_chan(vals, 2, sendq=sq, recvq=rq, cell=0.42, closed=(i == 5))
            mc.move_to(P(x + pw / 2, y - 1.15))
            self.add(mc)
            p = gtok(pn, w=0.6, h=0.3, state=ps, size=11).move_to(P(x + 0.45, y - 1.15))
            c = gtok(cn, w=0.6, h=0.3, state=cs, size=11).move_to(P(x + pw - 0.45, y - 1.15))
            self.add(p, c)
            self.add(txt(note, size=12, color=T.TEXT2, width=pw - 0.3, align="CENTER").move_to(P(x + pw / 2, y - ph + 0.32)))
        k = callout("key", "Every panel is a handful of field updates under `c.lock`. The scheduler only gets involved when "
                    "somebody parks (panel 3) or is woken (panel 4).", width=CW, size=14, inline=True)
        self.at(k, X0, Y1 + k.get_height() + 0.02)


class C7Close(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "closechan: wake everybody, then step back"
    SUB = "`close(ch)` flips one flag and releases every parked goroutine. Receivers get zero values; senders will panic when they run."

    def build(self):
        steps = num_steps([("Check", "`ch == nil` → panic \"close of nil channel\"; lock; already closed → unlock, panic \"close of closed channel\"."),
                           ("Mark", "`c.closed = 1`."),
                           ("Release receivers", "for each sudog on `recvq`: zero its `elem`, `success = false`, collect its G."),
                           ("Release senders", "for each sudog on `sendq`: `success = false`, collect its G (it will panic when it runs)."),
                           ("Unlock, then ready", "`unlock(&c.lock)`, then `goready` every collected G, outside the lock.")],
                          width=6.2, color=T.AMBER, size=15, gap=0.16)
        self.at(steps, X0, Y0)
        x = X0 + 6.7
        w = X1 - x
        before = mini_chan([], 2, recvq=["R1", "R2", "R3"], cell=0.42)
        self.at(txt("**before close**: three receivers parked on an empty channel", size=14, color=T.TEXT2), x, Y0)
        self.at(before, x, Y0 - 0.4)
        after = mini_chan([], 2, cell=0.42, closed=True)
        self.at(txt("**after close**: queues empty, all three runnable", size=14, color=T.TEXT2), x, before.get_bottom()[1] - 0.3)
        self.at(after, x, before.get_bottom()[1] - 0.7)
        rs = VGroup(*[gtok(f"R{k + 1}", w=0.65, h=0.3, size=11) for k in range(3)]).arrange(RIGHT, buff=0.12)
        rs.next_to(after, RIGHT, buff=0.3)
        self.add(rs)
        for r in rs:
            self.add(txt("0, false", size=10, color=T.TEAL, font=T.MONO).next_to(r, DOWN, buff=0.05))
        why = callout("q", "Why goready **after** unlocking? Readying a goroutine can involve the scheduler and other locks. "
                      "Holding the channel lock across that could deadlock with stack shrinking; the source says so.",
                      width=w, size=13)
        self.at(why, x, after.get_bottom()[1] - 0.45)
        k = callout("key", "This is why `close` works as a **broadcast** (chapter 8.5): one call wakes any number of waiters, "
                    "and every later receive returns immediately.", width=6.2, size=14)
        self.at(k, X0, steps.get_bottom()[1] - 0.35)


class C7Recap(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Recap and check yourself"
    SUB = "A channel is ordinary data plus a lock. Its cleverness is in the order of the checks."

    def build(self):
        self.at(section("REMEMBER", T.GO), X0, Y0)
        rec = bullets([
            "`hchan` = ring buffer (buf, sendx, recvx, qcount) + recvq/sendq of sudogs + closed + one lock.",
            "Send order: nil → closed (panic) → waiting receiver (direct) → buffer room → park.",
            "Receive order: nil → closed and empty (zero, false) → waiting sender → buffer → park.",
            "A direct send copies into the receiver's stack: the only cross-stack write in the runtime.",
            "Parked goroutines wait in sudogs; `goready` puts the partner back on a run queue.",
            "`close` marks the flag and readies every waiter: receivers get zero values, senders panic.",
        ], width=6.0, size=15, marker="check", marker_color=T.GREEN, gap=0.14)
        self.at(rec, X0, Y0 - 0.5)
        x = 0.55
        self.at(section("CHECK YOURSELF", T.TEAL), x, Y0)
        qs = [("Can a channel have values in its buffer and receivers parked on recvq at the same time?",
               "No. The runtime keeps the invariant: qcount > 0 implies recvq is empty."),
              ("Why is an unbuffered hand-off often faster than going through a buffer?",
               "One copy straight to the receiver, instead of a copy in and a copy out."),
              ("A sender is parked when the channel is closed. What happens?",
               "closechan readies it with success = false; when it runs it panics \"send on closed channel\"."),
              ("How much memory does `make(chan [64]byte, 4)` request?", "One block: 112 + 4 \u00D7 64 = 368 bytes, rounded up to the allocator's 384-byte size class.")]
        y = Y0 - 0.5
        for i, (q, a) in enumerate(qs):
            grp = vstack(txt(f"**Q{i + 1}.** {q}", size=15, color=T.TEXT, width=6.0),
                         txt(f"{{teal|**Answer.**}} {a}", size=14, color=T.TEXT2, width=6.0), buff=0.08)
            self.at(grp, x, y)
            y = grp.get_bottom()[1] - 0.28
