from kit import *

CH, NAME = "8.9", "The Scheduler I: G, M and P"


class C9Opener(Opener):
    NUM, NAME = CH, NAME
    TAGLINE = "The Go runtime runs its own scheduler inside your process. Three letters explain it: G for goroutine, M for machine (an OS thread), P for processor."
    LEARN = ["Explain why Go schedules goroutines itself",
             "Describe G, M and P and the rule that binds them",
             "Read the big picture: run queues, idle lists, sysmon",
             "Set and reason about GOMAXPROCS, container-aware since Go 1.25",
             "Walk one turn of `schedule()` and `findRunnable()`"]
    QUESTION = "Your service runs 10,000 goroutines on 4 cores. How many OS threads does it use, and what decides which goroutine runs next?"

    def art(self):
        g = VGroup()
        G = gtok("G", w=1.5, h=0.75, size=30).move_to(P(1.8, 1.6))
        M = mthread("M", w=1.7, h=0.8, size=30).move_to(P(3.85, 1.6))
        Pp = pchip("P", s=1.05, size=34).move_to(P(5.9, 1.6))
        plus1 = txt("**+**", size=36, color=T.TEXT2).move_to(P(2.85, 1.6))
        plus2 = txt("**+**", size=36, color=T.TEXT2).move_to(P(4.85, 1.6))
        g.add(G, M, Pp, plus1, plus2)
        g.add(txt("goroutine", size=14, color=T.GO).next_to(G, DOWN, buff=0.18))
        g.add(txt("OS thread", size=14, color=T.AMBER).next_to(M, DOWN, buff=0.18))
        g.add(txt("processor", size=14, color=T.VIOLET).next_to(Pp, DOWN, buff=0.3))
        eq = txt("**an M holding a P runs a G**", size=20, color=T.TEXT).move_to(P(3.85, 0.15))
        g.add(eq)
        for i in range(4):
            gg = gopher(0.7, mood="run" if i == 0 else "happy").move_to(P(1.7 + i * 1.4, -1.45))
            g.add(gg)
        g.add(txt("thousands of Gs → a few Ms → GOMAXPROCS Ps", size=14, color=T.TEXT2).move_to(P(3.85, -2.45)))
        return g


class C9Why(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Why Go schedules goroutines itself"
    SUB = "The kernel schedules threads and knows nothing about goroutines. A scheduler inside the runtime can switch in user space and cooperate with channels, the GC and the network."

    def build(self):
        reasons = [("Cheap switches", "no system call, three registers (8.2)", T.GO),
                   ("Knows why a G waits", "channels park and ready Gs directly (8.7)", T.GREEN),
                   ("Cooperates with the GC", "stops Gs at safe points, schedules GC workers", T.VIOLET),
                   ("Integrates the network", "the netpoller turns I/O readiness into runnable Gs (8.10)", T.BLUE),
                   ("Keeps work local", "per-P queues and caches stay warm on one core", T.AMBER)]
        y = Y0
        for t, d, col in reasons:
            c = card(t, d, w=5.0, color=col, size=14)
            self.at(c, X0, y)
            y = c.get_bottom()[1] - 0.12
        # history timeline
        x = X0 + 5.5
        w = X1 - x
        self.at(section("A SHORT HISTORY OF THE SCHEDULER", T.GO), x, Y0)
        evs = [("2012", "Go 1.0", "G-M model: one global run queue behind one lock. Contention grows with cores."),
               ("2013", "Go 1.1", "Dmitry Vyukov's design adds **P**: per-processor run queues and work stealing."),
               ("2013", "Go 1.2", "Preemption at function entry: a long-running G can be stopped at a call."),
               ("2015", "Go 1.5", "GOMAXPROCS defaults to the number of CPUs (it used to be 1)."),
               ("2020", "Go 1.14", "Asynchronous preemption with signals: even tight loops can be stopped (8.11)."),
               ("2025", "Go 1.25", "Container-aware GOMAXPROCS, re-checked while the program runs.")]
        yy = Y0 - 0.55
        self.add(Line(P(x + 0.95, yy + 0.05), P(x + 0.95, yy - 0.64 * len(evs) + 0.3)).set_stroke(T.STROKE2, 3))
        for yr, ver, d in evs:
            self.add(Dot(P(x + 0.95, yy - 0.18), radius=0.08, fill_color=T.GO))
            self.add(txt(f"**{yr}**", size=13, color=T.MUTED).move_to(P(x + 0.75, yy - 0.18), aligned_edge=RIGHT))
            self.add(txt(f"**{ver}**", size=14, color=T.GO).move_to(P(x + 1.15, yy - 0.05), aligned_edge=LEFT))
            self.add(txt(d, size=13, color=T.TEXT2, width=w - 1.3).move_to(P(x + 1.15, yy - 0.26), aligned_edge=UL))
            yy -= 0.64
        bx = rbox(w, 1.4, color=T.STROKE2, fill=T.PANEL, radius=0.12)
        self.at(bx, x, Y1 + 1.42)
        bl = txt("**before Go 1.1**", size=13, color=T.RED).move_to(bx.get_corner(UL) + P(0.15, -0.2), aligned_edge=LEFT)
        q1 = slots_row(5, cell=0.3, color=T.RED, items=["", "", "", ""], item_fn=lambda s: gtok(s, w=0.26, h=0.16, eyes=False))
        q1.move_to(bx.get_left() + P(1.35, -0.15))
        l1 = lock_icon(s=0.22).next_to(q1, UP, buff=0.04)
        ms = VGroup(*[mthread("", w=0.36, h=0.22) for _ in range(3)]).arrange(DOWN, buff=0.05).next_to(q1, RIGHT, buff=0.35)
        self.add(bx, bl, q1, l1, ms)
        al = txt("**Go 1.1 and later**", size=13, color=T.GREEN).move_to(bx.get_center() + P(0.45, 0.58), aligned_edge=LEFT)
        self.add(al)
        for k in range(3):
            pp = pchip("", s=0.3).move_to(bx.get_center() + P(0.75 + 0.95 * k, -0.35))
            qq = VGroup(*[gtok("", w=0.22, h=0.14, eyes=False) for _ in range(2)]).arrange(DOWN, buff=0.03).next_to(pp, RIGHT, buff=0.07)
            self.add(pp, qq)


class C9GMP(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Meet G, M and P"
    SUB = "Three structs in runtime/runtime2.go. The whole scheduler is the dance between them."

    def build(self):
        w = (CW - 0.5) / 3
        cols = [
            ("G", "goroutine", T.GO, gtok("G", w=1.0, h=0.48, size=20),
             "A function running concurrently: its stack, saved registers and state.",
             "stack         [lo, hi)\nsched         gobuf (sp, pc, bp)\natomicstatus  _Grunnable ...\nwaitreason    \"chan receive\"\nm             running on",
             "**How many?** As many as you start: 100,000 is ordinary."),
            ("M", "machine = OS thread", T.AMBER, mthread("M", w=1.2, h=0.55, size=20),
             "A real kernel thread. It executes Gs, but only while it holds a P.",
             "g0       scheduling stack\ncurg     the G it runs now\np        the P it holds\nspinning looking for work\nlockedg  LockOSThread",
             "**How many?** Usually a few more than GOMAXPROCS; capped at 10,000 by default."),
            ("P", "processor (a scheduling context)", T.VIOLET, pchip("P", s=0.8, size=24),
             "The right to run Go code, plus the resources for it.",
             "runq     [256]guintptr\nrunnext  run this G next\nmcache   allocation cache\ntimers   this P's timers\ngFree    dead Gs to reuse",
             "**How many?** Exactly GOMAXPROCS."),
        ]
        for i, (letter, name, col, icon, d, fields, howmany) in enumerate(cols):
            x = X0 + i * (w + 0.25)
            bx = rbox(w, 4.65, color=col, fill=T.PANEL, radius=0.16, stroke_width=2)
            self.at(bx, x, Y0)
            icon.move_to(P(x + 0.75, Y0 - 0.55))
            self.add(icon, txt(f"**{name}**", size=16, color=col, width=w - 1.6).move_to(P(x + 1.5, Y0 - 0.55), aligned_edge=LEFT))
            self.add(txt(d, size=14, color=T.TEXT, width=w - 0.4).move_to(P(x + 0.2, Y0 - 1.05), aligned_edge=UL))
            f = code(fields, size=12, numbers=False, lang="text", width=w - 0.4)
            self.at(f, x + 0.2, Y0 - 1.75)
            self.add(txt(howmany, size=13, color=T.TEXT2, width=w - 0.4).move_to(P(x + 0.2, f.get_bottom()[1] - 0.15), aligned_edge=UL))
        rule = callout("rule", "**To run Go code, an M must hold a P.** The M runs one G at a time on that P. "
                       "An M in a blocking system call can give its P away, so GOMAXPROCS bounds Go code, not threads.",
                       width=CW, size=15)
        self.at(rule, X0, Y1 + rule.get_height() + 0.02)


class C9BigPicture(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "The big picture"
    SUB = "GOMAXPROCS = 3. Every P has a local run queue and a runnext slot; a global queue catches overflow. Ms come and go; sysmon watches over all of it."

    def build(self):
        gq = slots_row(8, cell=0.36, color=T.GREEN, items=["G9", "G10", "G11"], item_fn=lambda s: gtok(s, w=0.34, h=0.22, eyes=False, size=8))
        lab = txt("**global run queue** (sched.runq, one lock)", size=13, color=T.GREEN)
        self.at(lab, X0, Y0 - 0.15)
        gq.next_to(lab, RIGHT, buff=0.25)
        self.add(gq)
        sm = mthread("sysmon", w=1.35, h=0.48, size=13).move_to(P(5.7, Y0 - 0.28))
        self.add(sm, txt("an M with no P: preempts,\nretakes Ps, polls the network", size=11, color=T.MUTED, align="CENTER").next_to(sm, DOWN, buff=0.08))
        xs = [-5.05, -2.0, 1.05]
        y_g, y_p, y_m, y_c = Y0 - 1.35, Y0 - 2.25, Y0 - 3.15, Y0 - 4.0
        for i, x in enumerate(xs):
            curg = gtok(f"G{i + 1}", w=0.75, h=0.36, size=12).move_to(P(x, y_g))
            p = pchip(f"P{i}", s=0.62, size=16).move_to(P(x, y_p))
            m = mthread(f"M{i}", w=0.95, h=0.44, size=14).move_to(P(x, y_m))
            c = cpu_core(f"core {i}", w=1.0, h=0.5, size=11).move_to(P(x, y_c))
            self.add(Line(curg.get_bottom(), p.get_top()).set_stroke(T.STROKE2, 2), Line(p.get_bottom(), m.get_top()).set_stroke(T.STROKE2, 2),
                     dashed(m.get_bottom(), c.get_top(), T.STROKE2, 1.6))
            self.add(curg, p, m, c)
            rn = rbox(0.5, 0.4, color=T.YELLOW, fill=T.BG, fill_opacity=0.4, radius=0.06).move_to(P(x + 0.75, y_p + 0.05))
            self.add(rn, txt("runnext", size=9, color=T.YELLOW).next_to(rn, UP, buff=0.03))
            if i != 2:
                self.add(gtok(f"G{4 + i}", w=0.42, h=0.24, state="ready", eyes=False, size=8).move_to(rn))
            items = [["G7", "G8"], ["G12"], []][i]
            q = slots_row(4, cell=0.34, color=T.VIOLET, items=items, item_fn=lambda s: gtok(s, w=0.31, h=0.2, state="ready", eyes=False, size=7))
            q.next_to(rn, RIGHT, buff=0.12)
            self.add(q)
            if i == 0:
                self.add(txt("local run queue (256 slots)", size=10, color=T.VIOLET).next_to(q, UP, buff=0.05))
            if i == 2:
                self.add(txt("empty: will steal", size=11, color=T.VIOLET).next_to(q, DOWN, buff=0.06))
        mx = 4.45
        msys = mthread("M3", w=0.95, h=0.44, size=14).move_to(P(mx, y_m))
        gsys = gtok("G13", w=0.75, h=0.36, state="wait", size=11).move_to(P(mx, y_p))
        self.add(Line(gsys.get_bottom(), msys.get_top()).set_stroke(T.AMBER, 2), msys, gsys)
        self.add(txt("in a blocking syscall:\nno P needed (8.10)", size=11, color=T.AMBER).next_to(msys, RIGHT, buff=0.12))
        il = VGroup(VGroup(txt("**idle Ps**", size=12, color=T.VIOLET), pchip("", s=0.3)).arrange(RIGHT, buff=0.1),
                    VGroup(txt("**idle Ms**", size=12, color=T.AMBER), mthread("", w=0.4, h=0.24), mthread("", w=0.4, h=0.24)).arrange(RIGHT, buff=0.1)
                    ).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        il.move_to(P(mx - 0.4, y_g + 0.1), aligned_edge=LEFT)
        self.add(il)
        np_ = rbox(1.9, 0.62, color=T.BLUE, fill=T.BLUE, fill_opacity=0.12, radius=0.1).move_to(P(mx + 0.9, y_c))
        self.add(np_, txt("**netpoller**\nepoll / kqueue / IOCP", size=11, color=T.BLUE, align="CENTER").move_to(np_))
        self.add(kernel_band(CW, 0.32, "OS SCHEDULER: puts Ms (threads) on cores").move_to(P(0, Y1 + 0.18)))


class C9Gomaxprocs(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "GOMAXPROCS: how many Ps"
    SUB = "GOMAXPROCS is the number of Ps, so the number of goroutines that can execute Go code at the same instant."

    def build(self):
        cd = code_ex("ch09_gomaxprocs", lines=(8, 17), size=14, hl=[10, 12, 15])
        self.at(cd, X0, Y0)
        tm = terminal(out("ch09_gomaxprocs"), title="output (4 vCPUs, no CPU limit)", width=cd.get_width(), size=14)
        self.at(tm, X0, cd.get_bottom()[1] - 0.15)
        rules = bullets(["Default (Go 1.25+, Linux): the **smaller** of the CPUs this process may use (affinity mask) and the "
                         "container's **CPU limit** (cgroup quota ÷ period, rounded **up**, at least 2).",
                         "The runtime **re-checks** about once a second and adjusts if the limit changes.",
                         "Setting `GOMAXPROCS=n` in the environment, or calling `runtime.GOMAXPROCS(n)`, fixes the value and stops the updates.",
                         "`runtime.SetDefaultGOMAXPROCS()` returns to the automatic default.",
                         "Opt out with `GODEBUG=containermaxprocs=0` or `updatemaxprocs=0`."],
                        width=cd.get_width(), size=13, gap=0.08)
        self.at(rules, X0, tm.get_bottom()[1] - 0.25)
        x = cd.get_right()[0] + 0.6
        w = X1 - x
        # container illustration
        host = rbox(w, 2.65, color=T.STROKE2, fill=T.PANEL, radius=0.15)
        self.at(host, x, Y0)
        self.add(txt("**host: 8 CPUs**", size=14, color=T.TEXT2).move_to(host.get_corner(UL) + P(0.2, -0.22), aligned_edge=LEFT))
        cores = VGroup(*[cpu_core("", w=0.48, h=0.3) for _ in range(8)]).arrange(RIGHT, buff=0.12).move_to(host.get_center() + DOWN * 0.85)
        self.add(cores)
        ctr = rbox(w - 0.8, 1.35, color=T.BLUE, fill=T.BLUE, fill_opacity=0.08, radius=0.12).move_to(host.get_center() + UP * 0.2)
        self.add(ctr, txt("**container**  cpu.max = 250000 100000  →  2.5 CPUs", size=12, color=T.BLUE).move_to(ctr.get_top() + DOWN * 0.22))
        ps = VGroup(*[pchip(f"P{k}", s=0.4, size=11) for k in range(3)]).arrange(RIGHT, buff=0.25).move_to(ctr.get_center() + P(-0.9, -0.15))
        self.add(ps, txt("ceil(2.5) = 3\n\u2192 GOMAXPROCS = 3", size=12, color=T.VIOLET, weight="BOLD").next_to(ps, RIGHT, buff=0.3))
        tbl = table([["Setting", "Effect"],
                     ["too high (> real CPU)", "Ps compete for CPU time; the OS throttles the container; latency spikes"],
                     ["too low", "idle cores while goroutines wait in run queues"],
                     ["just right", "one P per CPU you are actually allowed to use"]],
                    [2.0, w - 2.0], size=12)
        self.at(tbl, x, host.get_bottom()[1] - 0.25)
        w3 = callout("note", "GOMAXPROCS does **not** limit threads. Goroutines blocked in system calls, or locked to threads "
                     "with `LockOSThread`, have Ms of their own (8.10).", width=w, size=13)
        self.at(w3, x, tbl.get_bottom()[1] - 0.2)


class C9Schedule(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "One turn of the scheduler: schedule() and findRunnable()"
    SUB = "Whenever a G stops running (it parks, yields, exits or is preempted) its M switches to its g0 stack and calls schedule(), which looks for the next G in this order."

    def build(self):
        steps = [("every 61st tick", "take 1 G from the **global** queue first, so it is never starved", T.GREEN),
                 ("local", "`runnext`, then the P's local run queue", T.VIOLET),
                 ("global", "take a batch from the global queue (up to 128, half a local queue)", T.GREEN),
                 ("network", "non-blocking netpoll: Gs whose sockets became ready", T.BLUE),
                 ("steal", "4 rounds over the other Ps in random order: take **half** of a victim's queue", T.AMBER),
                 ("GC", "if a GC is running, do background mark work", T.VIOLET),
                 ("sleep", "nothing anywhere: release the P; one M may block in netpoll, the rest park (`stopm`)", T.GREY)]
        y = Y0
        for i, (t, d, col) in enumerate(steps):
            b = badge(str(i + 1), col, r=0.17, size=14).move_to(P(X0 + 0.2, y - 0.25))
            n = node(t, w=1.85, h=0.5, color=col, size=13).move_to(P(X0 + 1.45, y - 0.25))
            dd = txt(d, size=13, color=T.TEXT2, width=4.6).move_to(P(X0 + 2.55, y - 0.25), aligned_edge=LEFT)
            self.add(b, n, dd)
            if i:
                self.add(arrow(P(X0 + 1.45, y + 0.12), P(X0 + 1.45, y + 0.0), T.MUTED, 1.4, 0))
            y -= 0.66
        ex = node("found G: `execute(gp)` → status _Grunning → `gogo(&gp.sched)` jumps to its saved PC and SP", w=6.9, h=0.62, color=T.GO, size=13)
        self.at(ex, X0, y - 0.1)
        x = X0 + 7.45
        w = X1 - x
        self.at(section("THE g0 SWITCH", T.VIOLET), x, Y0)
        stk_w = 1.5
        for k, (lab, col, fr) in enumerate((("G's stack", T.GO, ["main()", "worker()", "chansend()", "gopark()"]),
                                             ("g0 stack (M's)", T.VIOLET, ["mstart()", "schedule()", "findRunnable()"]))):
            sx = x + k * (stk_w + 0.9)
            self.add(txt(f"**{lab}**", size=12, color=col).move_to(P(sx + stk_w / 2, Y0 - 0.55)))
            for j, f in enumerate(fr):
                r = Rectangle(width=stk_w, height=0.36).set_fill(col, 0.25).set_stroke(col, 1.2).move_to(P(sx + stk_w / 2, Y0 - 0.9 - j * 0.38))
                self.add(r, txt(f, size=11, color=T.TEXT, font=T.MONO, markup=False).move_to(r))
        self.add(arrow(P(x + stk_w + 0.05, Y0 - 2.04), P(x + stk_w + 0.85, Y0 - 1.66), T.YELLOW, 2.2))
        self.add(txt("mcall", size=11, color=T.YELLOW, font=T.MONO).move_to(P(x + stk_w + 0.45, Y0 - 2.15)))
        expl = bullets(["Each M has a special goroutine **g0** whose stack runs scheduler code.",
                        "`mcall(park_m)` saves the G's registers into `g.sched` and switches to g0.",
                        "On g0, `schedule()` picks the next G and `gogo` switches to its stack.",
                        "So a switch is G → g0 → G': two cheap stack swaps, no kernel."],
                       width=w, size=13, gap=0.08)
        self.at(expl, x, Y0 - 2.55)
        k = callout("hood", "The 61 is from `pp.schedtick%61 == 0` in findRunnable: a prime, so it doesn't line up with "
                    "periodic patterns in your program.", width=w, size=12)
        self.at(k, x, expl.get_bottom()[1] - 0.2)


class C9Recap(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Recap and check yourself"
    SUB = "G is the work, M is the worker thread, P is the permission (and the queue) to run Go code."

    def build(self):
        self.at(section("REMEMBER", T.GO), X0, Y0)
        rec = bullets([
            "The runtime schedules Gs in user space: cheap switches that cooperate with channels, the GC and I/O.",
            "An M must hold a P to run Go code. #P = GOMAXPROCS; #M is whatever is needed (cap 10,000).",
            "Each P has a 256-slot run queue plus `runnext`; a global queue catches overflow.",
            "Go 1.25+: GOMAXPROCS respects the container CPU limit and is updated about once a second.",
            "findRunnable: global every 61 ticks, local, global batch, netpoll, steal half, GC work, sleep.",
            "A switch goes through g0: G → mcall → schedule() on g0 → gogo → G'.",
        ], width=6.0, size=15, marker="check", marker_color=T.GREEN, gap=0.14)
        self.at(rec, X0, Y0 - 0.5)
        x = 0.55
        self.at(section("CHECK YOURSELF", T.TEAL), x, Y0)
        qs = [("10,000 goroutines on 4 cores, all doing CPU work. How many run at any instant?",
               "At most GOMAXPROCS (4 by default here); the rest wait in run queues."),
              ("A container has a 1.2-CPU limit on a 64-core host. Default GOMAXPROCS in Go 1.27?",
               "ceil(1.2) = 2, and the minimum is 2 anyway: GOMAXPROCS = 2 (it was 64 before Go 1.25)."),
              ("Why does a P, not an M, own the run queue?",
               "Ms block in syscalls and come and go; a P stays, so its queue and caches survive the hand-off."),
              ("What stops two goroutines that keep re-spawning each other from starving the global queue?",
               "The every-61st-tick check of the global queue in findRunnable.")]
        y = Y0 - 0.5
        for i, (q, a_) in enumerate(qs):
            grp = vstack(txt(f"**Q{i + 1}.** {q}", size=15, color=T.TEXT, width=6.0),
                         txt(f"{{teal|**Answer.**}} {a_}", size=14, color=T.TEXT2, width=6.0), buff=0.08)
            self.at(grp, x, y)
            y = grp.get_bottom()[1] - 0.28
