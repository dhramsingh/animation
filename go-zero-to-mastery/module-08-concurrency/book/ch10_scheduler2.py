from kit import *

CH, NAME = "8.10", "The Scheduler II: Queues, Syscalls and I/O"


def runq_row(items, nxt=None, cap_=6, cell=0.4, label=True, color=T.VIOLET):
    g = VGroup()
    rn = rbox(cell + 0.12, cell + 0.08, color=T.YELLOW, fill=T.BG, fill_opacity=0.4, radius=0.06)
    g.add(rn)
    if nxt:
        g.add(gtok(nxt, w=cell, h=cell * 0.6, state="ready", eyes=False, size=9).move_to(rn))
    q = slots_row(cap_, cell=cell, color=color, items=items,
                  item_fn=lambda s: gtok(s, w=cell * 0.9, h=cell * 0.55, state="ready", eyes=False, size=9))
    q.next_to(rn, RIGHT, buff=0.15)
    g.add(q)
    if label:
        g.add(txt("runnext", size=10, color=T.YELLOW).next_to(rn, UP, buff=0.04))
        g.add(txt("local run queue", size=10, color=color).next_to(q, UP, buff=0.04))
    g.q = q
    g.rn = rn
    return g


class C10Opener(Opener):
    NUM, NAME = CH, NAME
    TAGLINE = "Where does a new goroutine go? What happens when one blocks in the kernel, or waits for a socket? The answers explain why Go servers need so few threads."
    LEARN = ["Trace a new goroutine through runnext, the local queue and the global queue",
             "Explain work stealing and spinning threads",
             "Follow a blocking system call: hand-off, retake, return",
             "Explain how the netpoller parks thousands of connections",
             "Read sysmon's duties and the `schedtrace` output"]
    QUESTION = "50 goroutines block in a system call, and 2,000 wait on idle network connections. Which of them need an OS thread of their own?"

    def art(self):
        g = VGroup()
        b1 = rbox(2.6, 3.7, color=T.AMBER, fill=T.PANEL, fill_opacity=0.85, radius=0.2).move_to(P(2.3, 0.1))
        g.add(b1, txt("**blocking syscall**", size=14, color=T.AMBER).move_to(b1.get_top() + DOWN * 0.3))
        for k in range(3):
            gg = gopher(0.62, mood="blocked").move_to(P(1.75, 1.0 - k * 0.95))
            m = mthread(f"M{k + 4}", w=0.9, h=0.4, size=11).next_to(gg, RIGHT, buff=0.15)
            g.add(gg, m)
        g.add(txt("one thread each", size=13, color=T.AMBER).move_to(b1.get_bottom() + UP * 0.3))
        b2 = rbox(2.9, 3.7, color=T.BLUE, fill=T.PANEL, fill_opacity=0.85, radius=0.2).move_to(P(5.3, 0.1))
        g.add(b2, txt("**network wait**", size=14, color=T.BLUE).move_to(b2.get_top() + DOWN * 0.3))
        for k in range(12):
            gg = gopher(0.42, mood="sleep").move_to(P(4.45 + (k % 4) * 0.58, 1.05 - (k // 4) * 0.62))
            g.add(gg)
        np_ = rbox(2.2, 0.45, color=T.BLUE, fill=T.BLUE, fill_opacity=0.18, radius=0.08).move_to(P(5.3, -1.05))
        g.add(np_, txt("**netpoller**: zero threads", size=12, color=T.BLUE).move_to(np_))
        g.add(txt("parked Gs, no threads", size=13, color=T.BLUE).move_to(b2.get_bottom() + UP * 0.3))
        return g


class C10Runq(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Where a new goroutine goes"
    SUB = "`go f()` puts the new G in the current P's runnext slot. Everything else in this page follows from that one decision (runqput in proc.go)."

    def build(self):
        frames = [("1. before", ["G2", "G3"], "G1", "P has G1 in runnext and G2, G3 queued."),
                  ("2. go f() creates G9", ["G2", "G3", "G1"], "G9", "G9 takes runnext; the old runnext G1 moves to the tail of the queue."),
                  ("3. queue full (256)", ["G2", "…", "G255", "G1"], "G9", "The next `go` finds no room: runqputslow moves **half** (128) plus the new G to the global queue, in one locked batch.")]
        y = Y0
        for t, items, nxt, d in frames:
            self.add(txt(f"**{t}**", size=15, color=T.YELLOW).move_to(P(X0, y - 0.1), aligned_edge=LEFT))
            r = runq_row(items, nxt, cap_=6, cell=0.42)
            self.at(r, X0 + 0.05, y - 0.35)
            if t.startswith("3"):
                gq = slots_row(4, cell=0.34, color=T.GREEN, items=["G2..", "G129", "G10"], item_fn=lambda s: gtok(s, w=0.32, h=0.2, eyes=False, size=7))
                gq.next_to(r, RIGHT, buff=0.75)
                self.add(gq, txt("global queue", size=10, color=T.GREEN).next_to(gq, UP, buff=0.04),
                         arrow(r.get_right() + P(0.05, -0.1), gq.get_left() + P(-0.03, -0.1), T.GREEN, 2.2))
            self.add(txt(d, size=13, color=T.TEXT2, width=6.2).move_to(P(X0, y - 1.25), aligned_edge=UL))
            y -= 1.95
        x = X0 + 7.2
        w = X1 - x
        self.at(section("WHY runnext?", T.YELLOW), x, Y0)
        why = txt("When G1 wakes G2 (by sending on a channel, say) and then blocks, G2 should run **immediately** "
                  "on the same P, with warm caches. runnext gives exactly that: the readied G runs next and "
                  "**inherits the rest of the current time slice**, so a ping-pong pair cannot hog the P forever.",
                  size=14, color=T.TEXT2, width=w)
        self.at(why, x, Y0 - 0.5)
        cd = code('''// runqput tries to put g on the local runnable queue.
// If next is true, runqput puts g in the pp.runnext slot.
// If the run queue is full, runnext puts g on the
// global queue.
func runqput(pp *p, gp *g, next bool)

// newproc: a new goroutine always goes to runnext
runqput(pp, newg, true)''', size=12, title="runtime/proc.go (Go 1.27, excerpts)", width=w, hl=[(8, T.YELLOW)], numbers=False)
        self.at(cd, x, why.get_bottom()[1] - 0.25)
        k = callout("key", "Local queues are lock-free rings (only the owner adds; others may steal). The global "
                    "queue needs `sched.lock`, which is why the runtime batches moves into and out of it.",
                    width=w, size=13)
        self.at(k, x, cd.get_bottom()[1] - 0.2)


class C10Steal(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Work stealing: idle Ps take half"
    SUB = "A P with nothing to run does not wait for work to be assigned. Its M spins, picks victims at random, and takes half of one's queue."

    def build(self):
        def p_row(name, items, x, y, nxt=None, col=T.VIOLET):
            pc = pchip(name, s=0.55, size=14).move_to(P(x, y))
            r = runq_row(items, nxt, cap_=6, cell=0.38, label=False, color=col).next_to(pc, RIGHT, buff=0.2)
            return VGroup(pc, r)
        y0 = Y0 - 0.4
        self.add(txt("**before**", size=16, color=T.TEXT).move_to(P(X0, y0 + 0.15), aligned_edge=LEFT))
        rows_b = [("P0", ["G2", "G3", "G4", "G5", "G6", "G7"], "G1"), ("P1", ["G9"], None), ("P2", [], None)]
        for i, (n, it, nx) in enumerate(rows_b):
            self.add(p_row(n, it, X0 + 0.4, y0 - 0.5 - i * 0.75, nx))
        sp = mthread("M2 spinning", w=1.8, h=0.4, size=11).move_to(P(X0 + 1.4, y0 - 2.6))
        self.add(sp, arrow(sp.get_top(), P(X0 + 0.4, y0 - 0.5 - 2 * 0.75 - 0.32), T.AMBER, 2))
        x1 = X0 + 4.6
        self.add(arrow(P(x1 - 0.3, y0 - 1.25), P(x1 + 0.2, y0 - 1.25), T.YELLOW, 3.5))
        xa = x1 + 0.55
        self.add(txt("**after P2 steals from P0**", size=16, color=T.TEXT).move_to(P(xa, y0 + 0.15), aligned_edge=LEFT))
        rows_a = [("P0", ["G5", "G6", "G7"], "G1"), ("P1", ["G9"], None), ("P2", ["G3", "G4"], "G2")]
        for i, (n, it, nx) in enumerate(rows_a):
            self.add(p_row(n, it, xa + 0.4, y0 - 0.5 - i * 0.75, nx))
        self.add(txt("P2 now runs G2 and has G3, G4 queued", size=12, color=T.VIOLET).move_to(P(xa, y0 - 2.6), aligned_edge=LEFT))
        rules = bullets(["**Victims in random order**, up to 4 passes over all Ps.",
                         "Take **half** of the victim's queue (`n - n/2`), oldest first.",
                         "Only on the last pass may a thief also take the victim's `runnext` (and its due timers).",
                         "At most **half the busy Ps** may have a spinning M: idle machines don't burn CPU.",
                         "A spinning M that finds work wakes another M, so work spreads quickly."],
                        width=6.1, size=14, gap=0.1)
        self.at(section("THE RULES (findRunnable, stealWork, runqgrab)", T.AMBER), X0, Y0 - 3.45)
        self.at(rules, X0, Y0 - 3.95)
        x = X0 + 6.8
        w = X1 - x
        k = callout("q", "Why half? Taking one G means stealing again soon; taking all moves the problem to the victim. "
                    "Half balances both queues in one step, and each G is moved at most a few times.",
                    width=w, size=14, title="WHY HALF?")
        self.at(k, x, Y0 - 3.45)


class C10Syscalls(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Blocking system calls: hand the P to someone else"
    SUB = "An M stuck in the kernel cannot run Go code, but its P (and the Gs queued on it) should not wait too. The runtime moves the P to another M."

    def build(self):
        frames = [
            ("1. G1 calls read()", "`entersyscall`: G1 → _Gsyscall. M0 keeps P0 loosely, for a fast return.", "P0", "M0", "G1", None),
            ("2. sysmon: still in syscall?", "After ≥ 1 sysmon tick (20 µs) with work waiting, `retake` + `handoffp`: P0 goes to M1, which runs G2.", "P0", "M1", "G2", "M0"),
            ("3. read() returns", "`exitsyscall`: P0 is taken. Grab any idle P; if none, put G1 on the global queue and park M0.", None, "M0", "G1", None),
        ]
        fw = (CW - 0.5) / 3
        for i, (t, d, pname, mname, gname, blocked) in enumerate(frames):
            x = X0 + i * (fw + 0.25)
            bx = rbox(fw, 3.0, color=T.STROKE2, fill=T.PANEL, radius=0.14)
            self.at(bx, x, Y0)
            self.add(txt(f"**{t}**", size=14, color=T.YELLOW).move_to(P(x + 0.18, Y0 - 0.22), aligned_edge=LEFT))
            cx = x + fw / 2
            kern = kernel_band(fw - 0.4, 0.32, "kernel").move_to(P(cx, Y0 - 2.55))
            self.add(kern)
            if i == 0:
                g1 = gtok("G1", w=0.7, h=0.32, state="wait", size=11).move_to(P(cx - 0.6, Y0 - 0.85))
                p0 = pchip("P0", s=0.45, size=12).move_to(P(cx + 0.6, Y0 - 1.0))
                m0 = mthread("M0", w=0.8, h=0.36, size=12).move_to(P(cx - 0.6, Y0 - 1.65))
                self.add(g1, p0, m0, Line(g1.get_bottom(), m0.get_top()).set_stroke(T.AMBER, 2),
                         dashed(m0.get_right(), p0.get_bottom(), T.VIOLET, 1.6), arrow(m0.get_bottom(), kern.get_top() + LEFT * 0.6, T.AMBER, 2))
            elif i == 1:
                g1 = gtok("G1", w=0.6, h=0.3, state="wait", size=10).move_to(P(cx - 0.95, Y0 - 0.85))
                m0 = mthread("M0", w=0.75, h=0.34, size=11).move_to(P(cx - 0.95, Y0 - 1.6))
                self.add(g1, m0, Line(g1.get_bottom(), m0.get_top()).set_stroke(T.AMBER, 2), arrow(m0.get_bottom(), kern.get_top() + LEFT * 0.95, T.AMBER, 2))
                g2 = gtok("G2", w=0.6, h=0.3, size=10).move_to(P(cx + 0.75, Y0 - 0.7))
                p0 = pchip("P0", s=0.42, size=11).move_to(P(cx + 0.75, Y0 - 1.25))
                m1 = mthread("M1", w=0.75, h=0.34, size=11).move_to(P(cx + 0.75, Y0 - 1.85))
                self.add(g2, p0, m1, Line(g2.get_bottom(), p0.get_top()).set_stroke(T.STROKE2, 2), Line(p0.get_bottom(), m1.get_top()).set_stroke(T.STROKE2, 2))
                sm = mthread("sysmon", w=0.95, h=0.3, size=9).move_to(P(cx, Y0 - 0.65))
                self.add(sm, dashed_arrow(sm.get_bottom(), p0.get_left(), T.AMBER, 1.6))
            else:
                g1 = gtok("G1", w=0.7, h=0.32, state="ready", size=11).move_to(P(cx - 0.6, Y0 - 0.9))
                gq = slots_row(3, cell=0.3, color=T.GREEN, items=["G1"], item_fn=lambda s: gtok(s, w=0.28, h=0.18, eyes=False, size=7)).move_to(P(cx + 0.7, Y0 - 0.9))
                m0 = mthread("M0", w=0.8, h=0.36, size=12, active=False).move_to(P(cx - 0.6, Y0 - 1.75))
                self.add(g1, gq, m0, txt("global q", size=10, color=T.GREEN).next_to(gq, DOWN, buff=0.04),
                         arrow(g1.get_right(), gq.get_left(), T.GREEN, 1.8), txt("idle", size=10, color=T.MUTED).next_to(m0, RIGHT, buff=0.08))
            self.add(txt(d, size=12, color=T.TEXT2, width=fw - 0.3).move_to(P(x + 0.15, Y0 - 3.15), aligned_edge=UL))
        cd = code_ex("ch10_syscall_threads", lines=(32, 37), size=12, width=6.5, title="examples/ch10_syscall_threads (main)", hl=[34, (36, T.AMBER)])
        self.at(cd, X0, Y0 - 4.05)
        tm = terminal(out("ch10_syscall_threads"), title="measured", width=X1 - cd.get_right()[0] - 0.3, size=12)
        self.at(tm, cd.get_right()[0] + 0.3, Y0 - 4.05)


class C10Netpoll(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "The netpoller: thousands of connections, few threads"
    SUB = "Go puts every socket in non-blocking mode. A read that would block parks the goroutine instead of the thread, and the OS tells the runtime when the socket is ready."

    def build(self):
        steps = num_steps([("Read", "`conn.Read` calls `read()`; the socket has no data: the kernel returns EAGAIN at once."),
                           ("Park", "the G parks with wait reason \"IO wait\"; the fd is already registered with epoll (kqueue, IOCP). The M is free."),
                           ("Ready", "data arrives; the kernel marks the fd ready."),
                           ("Poll", "`netpoll()` (called by findRunnable, by sysmon every 10 ms, or by an M blocked in epoll_wait) returns the ready Gs."),
                           ("Run", "`injectglist` makes them runnable; the read is retried and succeeds.")],
                          width=6.6, color=T.BLUE, size=14, gap=0.12)
        self.at(steps, X0, Y0)
        cd = code_ex("ch10_netpoll", lines=(27, 38), size=12, width=6.6, title="examples/ch10_netpoll: the server side",
                     hl=[(35, T.BLUE)])
        self.at(cd, X0, steps.get_bottom()[1] - 0.25)
        x = X0 + 7.1
        w = X1 - x
        # drawing: many gophers on netpoller
        box = rbox(w, 2.9, color=T.BLUE, fill=T.PANEL, radius=0.16)
        self.at(box, x, Y0)
        for k in range(18):
            gg = gopher(0.38, mood="sleep").move_to(P(x + 0.45 + (k % 9) * 0.6, Y0 - 0.55 - (k // 9) * 0.6))
            self.add(gg)
        self.add(txt("2,000 goroutines in `conn.Read`, status IO wait", size=12, color=T.TEXT2).move_to(P(x + w / 2, Y0 - 1.65)))
        np_ = rbox(w - 0.8, 0.5, color=T.BLUE, fill=T.BLUE, fill_opacity=0.18, radius=0.08).move_to(P(x + w / 2, Y0 - 2.2))
        self.add(np_, txt("**netpoller** (one epoll instance per process)", size=13, color=T.BLUE).move_to(np_))
        self.add(mthread("M", w=0.7, h=0.3, size=11).move_to(P(x + w - 0.6, Y0 - 2.65)))
        tm = terminal(out("ch10_netpoll"), title="measured", width=w, size=14)
        self.at(tm, x, Y0 - 3.15)
        thr = nums("ch10_netpoll", r"OS threads:\s+(\d+)", int)[0]
        sys_thr = nums("ch10_syscall_threads", r"OS threads = (\d+)", int)[-1]
        k = callout("key", f"2,000 open connections and 2,002 goroutines needed only **{thr} OS threads**. "
                    f"Compare 50 blocking syscalls → {sys_thr} threads on the previous page.", width=w, size=14)
        self.at(k, x, tm.get_bottom()[1] - 0.2)


class C10Sysmon(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "sysmon: the runtime's watchdog"
    SUB = "One dedicated M runs `sysmon` without a P, so it keeps working even when every P is busy. It wakes every 20 µs, backing off to 10 ms when the program is idle."

    def build(self):
        cx, cy, R = -2.6, -0.65, 2.0
        hub = mthread("sysmon", w=1.6, h=0.6, size=17).move_to(P(cx, cy))
        self.add(Circle(radius=R).move_to(P(cx, cy)).set_stroke(T.STROKE2, 2.5), hub)
        duties = [("retake", "a P stuck in a syscall > 20 µs\n→ hand it to another M", T.AMBER),
                  ("preempt", "a G running > 10 ms\n→ ask it to yield (8.11)", T.RED),
                  ("netpoll", "nobody polled for 10 ms\n→ poll, inject ready Gs", T.BLUE),
                  ("force GC", "no GC for 2 minutes\n→ start one", T.VIOLET),
                  ("scavenger", "return unused memory\nto the OS", T.GREEN),
                  ("GOMAXPROCS", "about once a second\n→ re-read CPU limits", T.GO)]
        for i, (t, d, col) in enumerate(duties):
            a = PI / 2 - i * TAU / len(duties)
            p = P(cx, cy) + R * np.array([np.cos(a), np.sin(a), 0])
            n = node(t, w=1.55, h=0.46, color=col, size=13).move_to(p)
            dd = txt(d, size=11, color=T.TEXT2, align="CENTER").next_to(n, UP if i == 0 else DOWN, buff=0.06)
            self.add(n, dd)
        x = 1.6
        w = X1 - x
        sl = table([["Situation", "sysmon sleeps"], ["busy: it just did something", "20 µs"], ["idle for 1 ms (50 rounds)", "doubles each round"],
                    ["idle for long", "at most 10 ms"]], [2.9, w - 2.9], size=13)
        self.at(sl, x, Y0)
        cdd = code('''const forcePreemptNS = 10 * 1000 * 1000 // 10ms
var forcegcperiod int64 = 2 * 60 * 1e9   // 2 minutes

// in sysmon's loop:
if idle == 0 {
    delay = 20 // start with 20us sleep...
} else if idle > 50 { // ...double after 1ms
    delay *= 2
}
if delay > 10*1000 { // up to 10ms
    delay = 10 * 1000
}''', size=12, title="runtime/proc.go (Go 1.27, excerpts)", width=w, hl=[1, 2])
        self.at(cdd, x, sl.get_bottom()[1] - 0.25)
        k = callout("note", "sysmon is also why a goroutine can't monopolise a P for long: it is the one that "
                    "notices the 10 ms and triggers preemption (8.11).", width=w, size=13)
        self.at(k, x, cdd.get_bottom()[1] - 0.2)


class C10Schedtrace(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Watching the scheduler: GODEBUG=schedtrace"
    SUB = "The runtime prints a one-line summary every N milliseconds. Here 12 CPU-bound goroutines run on 4 Ps for 250 ms, between two idle phases."

    def build(self):
        tm = terminal(out("ch10_schedtrace"), title="real output", width=CW, size=11)
        self.at(tm, X0, Y0)
        line = [l for l in out("ch10_schedtrace").split("\n") if "runqueue=" in l][1]
        fields = re.findall(r"(\w+)=(\[[^\]]*\]|\S+)", line)
        expl = {"gomaxprocs": "number of Ps", "idleprocs": "Ps with nothing to run", "threads": "Ms that exist",
                "spinningthreads": "Ms looking for work", "needspinning": "a spinning M was requested",
                "idlethreads": "Ms parked, ready for reuse", "runqueue": "Gs in the global queue",
                "schedticks": "scheduler calls per P"}
        self.at(section("READING ONE LINE", T.GO), X0, tm.get_bottom()[1] - 0.25)
        self.at(mono(line.split(" schedticks")[0], size=12, color=T.YELLOW), X0, tm.get_bottom()[1] - 0.7)
        rows = [["Field", "Value", "Meaning"]]
        for k, v in fields:
            if k in expl:
                rows.append([f"`{k}`", v, expl[k]])
        local = re.search(r"runqueue=\d+ (\[[^\]]*\])", line).group(1)
        rows.insert(len(rows) - 1, ["`[ ... ]`", local, "Gs in each P's local queue"])
        half = (len(rows) + 1) // 2
        t1 = table(rows[:half], [1.9, 0.8, 3.6], size=12)
        t2 = table([rows[0]] + rows[half:], [1.9, 1.5, 2.9], size=12)
        self.at(t1, X0, tm.get_bottom()[1] - 1.05)
        self.at(t2, X0 + t1.get_width() + 0.3, tm.get_bottom()[1] - 1.05)
        tip = callout("tip", "Add `scheddetail=1` for one line per P, M and G. For timelines of individual goroutines, "
                      "use `runtime/trace` and `go tool trace` (8.17).", width=CW, size=13, inline=True)
        self.at(tip, X0, Y1 + tip.get_height() + 0.02)


class C10Recap(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Recap and check yourself"
    SUB = "Queues keep work local; stealing spreads it; hand-offs and the netpoller keep threads few."

    def build(self):
        thr = nums("ch10_syscall_threads", r"OS threads = (\d+)", int)
        net = nums("ch10_netpoll", r"OS threads:\s+(\d+)", int)[0]
        self.at(section("REMEMBER", T.GO), X0, Y0)
        rec = bullets([
            "A new G goes to runnext; the old runnext moves to the queue; a full queue sends half to the global queue.",
            "Idle Ps steal half of a random victim's queue; spinning Ms are limited to half the busy Ps.",
            "A syscall longer than ~20 µs loses its P to another M; on return the G may go to the global queue.",
            f"Blocking syscalls cost threads ({thr[0]} → {thr[-1]} for 50 calls); network waits don't ({net} threads for 2,000 conns).",
            "sysmon: retake Ps, preempt after 10 ms, poll the network, force GC every 2 min, update GOMAXPROCS.",
            "`GODEBUG=schedtrace=1000` prints Ps, threads and queue lengths every second.",
        ], width=6.0, size=15, marker="check", marker_color=T.GREEN, gap=0.14)
        self.at(rec, X0, Y0 - 0.5)
        x = 0.55
        self.at(section("CHECK YOURSELF", T.TEAL), x, Y0)
        qs = [("A goroutine wakes another via a channel send and then blocks. Where does the woken one run?",
               "On the same P, from runnext, with the rest of the time slice."),
              ("Why does reading a file (not a socket) still create threads?",
               "Regular files are not pollable: read() blocks in the kernel, so the M is lost for the duration."),
              ("schedtrace shows runqueue=8 and idleprocs=0. What does it mean?",
               "All Ps are busy and 8 Gs wait in the global queue: CPU-bound saturation."),
              ("Which component would notice a P stuck in a 5-second syscall?", "sysmon, via retake.")]
        y = Y0 - 0.5
        for i, (q, a_) in enumerate(qs):
            grp = vstack(txt(f"**Q{i + 1}.** {q}", size=15, color=T.TEXT, width=6.0),
                         txt(f"{{teal|**Answer.**}} {a_}", size=14, color=T.TEXT2, width=6.0), buff=0.08)
            self.at(grp, x, y)
            y = grp.get_bottom()[1] - 0.28
