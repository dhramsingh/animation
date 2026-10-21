from kit import *

CH, NAME = "8.2", "Threads and Goroutines"


def _costs():
    c = {}
    c["t_create_us"] = nums("ch02_thread_cost_c", r"create\+join: ([\d.]+) us")[0]
    c["t_switch_us"] = nums("ch02_thread_cost_c", r"per switch|ping-pong\): ([\d.]+) us")[0] if False else \
        nums("ch02_thread_cost_c", r"pipe ping-pong\): ([\d.]+) us")[0]
    c["t_stack_kb"] = nums("ch02_thread_cost_c", r"\(virtual\): (\d+) KB")[0]
    c["g_create_ns"] = nums("ch02_switch_bench", r"create\+exit: (\d+) ns")[0]
    c["g_switch_ns"] = nums("ch02_switch_bench", r"ping-pong\): (\d+) ns")[0]
    c["g_stack_b"] = nums("ch02_goroutine_cost", r"\((\d+) bytes per goroutine\)")[0]
    c["g_total_b"] = nums("ch02_goroutine_cost", r"all runtime memory: [\d.]+ MB \((\d+) bytes")[0]
    c["g_alive"] = nums("ch02_goroutine_cost", r"alive: (\d+)", int)[0]
    return c


class C2Opener(Opener):
    NUM, NAME = CH, NAME
    TAGLINE = "Why can a Go program keep a million goroutines alive when a C program struggles with ten thousand threads? Follow the memory and the context switches."
    LEARN = ["Draw a process: its address space, its threads and what they share",
             "Measure what an OS thread costs to create, to switch and to keep",
             "Compare the 1:1, N:1 and M:N threading models",
             "Read the runtime's g structure and see why a switch is cheap",
             "Estimate how many goroutines a server can afford"]
    QUESTION = "A goroutine and a thread both run a function on their own stack. Where does the 40x difference in switching cost come from?"

    def art(self):
        c = _costs()
        g = VGroup()
        base = -3.0
        # an 8 MB thread stack column vs a 2 KB goroutine stack sliver
        th = rbox(1.6, 5.4, color=T.AMBER, fill=T.AMBER, fill_opacity=0.12, radius=0.1).move_to(P(2.4, base + 2.7))
        used = Rectangle(width=1.56, height=0.25).set_fill(T.AMBER, 0.7).set_stroke(width=0).move_to(th.get_bottom() + UP * 0.14)
        tl = txt(f"**{c['t_stack_kb'] / 1024:.0f} MB**", size=26, color=T.AMBER).move_to(th.get_center() + UP * 0.3)
        tl2 = txt("virtual stack\nreserved per\nOS thread", size=14, color=T.TEXT2, align="CENTER").next_to(tl, DOWN, buff=0.15)
        m = mthread("M", w=1.0, h=0.5).next_to(th, UP, buff=0.15)
        g.add(th, used, tl, tl2, m)
        gs = rbox(1.6, 0.06 * 1.0 + 0.04, color=T.GO, fill=T.GO, fill_opacity=0.9, radius=0.02).move_to(P(5.2, base + 0.05))
        gl = txt(f"**{c['g_stack_b'] / 1024:.0f} KB**", size=26, color=T.GO).next_to(gs, UP, buff=0.9)
        gl2 = txt("initial stack per\ngoroutine (grows\non demand)", size=14, color=T.TEXT2, align="CENTER").next_to(gl, DOWN, buff=0.1)
        gg = gopher(1.0).next_to(gl, UP, buff=0.2)
        arr = arrow(gl2.get_bottom() + DOWN * 0.05, gs.get_top() + UP * 0.03, T.GO, thick=2)
        g.add(gs, gl, gl2, gg, arr)
        g.add(hline(1.2, 6.5, base - 0.02, T.STROKE2, 2))
        g.add(txt("drawn to the same scale: the goroutine stack is 1/4096 of the thread's", size=13, color=T.MUTED)
              .move_to(P(3.85, base - 0.3)))
        return g


class C2Process(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Inside a process"
    SUB = "A process owns an address space and kernel resources. Its threads share all of it, except their stacks and CPU registers."

    def build(self):
        x, top = X0, Y0
        w = 2.4
        regions = [("kernel space", T.BLUE, 0.5, "off-limits to user code"),
                   ("stack: thread 1", T.AMBER, 0.5, "grows down ↓"),
                   ("stack: thread 2", T.AMBER, 0.5, "one per thread"),
                   ("stack: thread 3", T.AMBER, 0.5, ""),
                   ("… free …", T.STROKE2, 0.85, "mmap, shared libraries"),
                   ("heap", T.PINK, 0.75, "grows up ↑ (make, new)"),
                   ("data / bss", T.VIOLET, 0.42, "global variables"),
                   ("text (code)", T.GO, 0.42, "machine code, read-only")]
        y = top - 0.35
        self.add(txt("**virtual address space**", size=14, color=T.TEXT2).move_to(P(x, top), aligned_edge=UL))
        self.add(txt("high", size=11, color=T.MUTED).move_to(P(x + w + 0.08, y - 0.08), aligned_edge=LEFT))
        for name, col, h, note in regions:
            r = Rectangle(width=w, height=h).set_fill(col, 0.18 if col != T.STROKE2 else 0.04).set_stroke(col, 1.5)
            r.move_to(P(x + w / 2, y - h / 2))
            t = txt(f"**{name}**", size=13, color=col if col != T.STROKE2 else T.MUTED).move_to(r)
            self.add(r, t)
            if note:
                self.add(txt(note, size=12, color=T.TEXT2, width=1.9).next_to(r, RIGHT, buff=0.12))
            y -= h
        self.add(txt("low", size=11, color=T.MUTED).move_to(P(x + w + 0.08, y + 0.08), aligned_edge=LEFT))
        tx = -1.85
        self.at(section("THREADS SHARE", T.GREEN), tx, Y0)
        shared = bullets(["code, globals and the **heap**", "open files and sockets (the fd table)",
                          "the address space and its page tables", "signal handlers, working directory, user id"],
                         width=3.9, size=15, marker="check", marker_color=T.GREEN, gap=0.08)
        self.at(shared, tx, Y0 - 0.5)
        self.at(section("EACH THREAD OWNS", T.AMBER), tx, shared.get_bottom()[1] - 0.3)
        own = bullets(["a **stack** (8 MB reserved by default on Linux)", "CPU **registers**: PC, SP, flags, vector registers",
                       "a thread ID, a signal mask, thread-local storage", "a **kernel** stack and task_struct (about 20 KB)"],
                      width=3.9, size=15, marker="dot", marker_color=T.AMBER, gap=0.08)
        self.at(own, tx, shared.get_bottom()[1] - 0.8)
        rx = 2.35
        k = callout("key", "Goroutines live **inside one process** and share its heap like threads do. "
                    "That is why they need channels or locks to cooperate safely.", width=X1 - rx, size=15)
        self.at(k, rx, Y0)
        hood = callout("hood", "On Linux a thread is a task made by `clone(CLONE_VM | CLONE_FILES | ...)`. "
                       "The kernel schedules tasks; a process is a group of tasks sharing one memory map.",
                       width=X1 - rx, size=14)
        self.at(hood, rx, k.get_bottom()[1] - 0.2)
        rows = [["", "Process", "Thread"],
                ["Address space", "its own", "shared with sibling threads"],
                ["Create", "`fork`/`exec`: copy page tables", "`clone`: share almost everything"],
                ["Talk to others", "pipes, sockets, shared mmap", "ordinary memory (needs synchronisation)"],
                ["A crash kills", "only itself", "the whole process"]]
        tb = table(rows, [1.9, 3.2, X1 - tx - 5.1], size=14)
        self.at(tb, tx, min(own.get_bottom()[1], hood.get_bottom()[1]) - 0.3)


class C2ThreadCost(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "What an OS thread really costs"
    SUB = "Every switch between threads goes through the kernel. We measured it with a small C program on this machine."

    def build(self):
        c = _costs()
        steps = [("user code running", "thread A on CPU", T.AMBER),
                 ("trap into the kernel", "timer interrupt, or a blocking syscall such as read()", T.BLUE),
                 ("save A's registers", "all general and vector registers, to A's kernel stack", T.BLUE),
                 ("run the scheduler", "pick the next runnable task (CFS / EEVDF)", T.BLUE),
                 ("restore B's registers", "and switch page tables if B is in another process", T.BLUE),
                 ("return to user mode", "thread B continues", T.AMBER)]
        y = Y0
        x = X0
        prev = None
        for i, (t, d, col) in enumerate(steps):
            n = node(f"{t}", w=2.6, h=0.5, color=col, size=14)
            n.move_to(P(x + 1.3, y - 0.25))
            dt = txt(d, size=13, color=T.TEXT2, width=3.0).next_to(n, RIGHT, buff=0.2)
            self.add(n, dt)
            if prev is not None:
                self.add(arrow(prev.get_bottom(), n.get_top(), T.MUTED, thick=2, buff=0.02))
            prev = n
            y -= 0.72
        indirect = callout("warn", "The hidden cost: after a switch the CPU caches and TLB hold the **other** "
                           "thread's data. The first microseconds run slowly while they refill.",
                           width=5.85, size=14, title="INDIRECT COST")
        self.at(indirect, X0, y - 0.05)

        x2 = 0.8
        cc = code(src("ch02_thread_cost_c", "threads.c", (15, 24)), size=13, start=15,
                  title="examples/ch02_thread_cost_c/threads.c", lang="c")
        self.at(cc, x2, Y0)
        tm = terminal(out("ch02_thread_cost_c"), title="measured on this machine", width=cc.get_width())
        self.at(tm, x2, cc.get_bottom()[1] - 0.2)
        cards = VGroup(
            stat(f"{c['t_create_us']:.0f} µs", "to create and join one thread", T.AMBER, w=1.85, size_v=30),
            stat(f"{c['t_switch_us']:.0f} µs", "per switch (pipe ping-pong, includes the syscalls)", T.AMBER, w=1.85, size_v=30),
            stat(f"{c['t_stack_kb'] / 1024:.0f} MB", "virtual stack reserved per thread", T.AMBER, w=1.85, size_v=30),
        ).arrange(RIGHT, buff=0.15, aligned_edge=UP)
        self.at(cards, x2, tm.get_bottom()[1] - 0.25)
        lim = callout("note", "Limits on this machine: `pid_max` = 32768, `threads-max` = 128594, and every thread "
                      "stack uses one of 65530 memory maps.", width=5.9, size=13, inline=True)
        self.at(lim, X0, Y1 + lim.get_height() + 0.02)


class C2GoroutineCost(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "What a goroutine costs (measured)"
    SUB = "Park 100,000 goroutines on a channel and ask the runtime how much memory they use."

    def build(self):
        c = _costs()
        cd = code_ex("ch02_goroutine_cost", lines=(9, 38), size=12, hl=[17, 18, 19, 20, 21, 22], marks={21: "1", 32: "2"})
        self.at(cd, X0, Y0)
        x = cd.get_right()[0] + 0.35
        tm = terminal(out("ch02_goroutine_cost"), title="output", size=13, width=X1 - x)
        self.at(tm, x, Y0)
        notes = bullets([(badge("1", T.YELLOW, r=0.12, size=12), "each goroutine parks on `<-block`: alive, but using no CPU"),
                         (badge("2", T.YELLOW, r=0.12, size=12), "`StackInuse` grows by exactly the new goroutines' stacks")],
                        width=X1 - x, size=14, gap=0.06)
        self.at(notes, x, tm.get_bottom()[1] - 0.15)
        sec = section("HOW MANY FIT IN 1 GiB OF RAM?", T.GO)
        self.at(sec, x, notes.get_bottom()[1] - 0.25)
        per_g = int(c["g_total_b"])
        n_g = (1 << 30) / per_g
        n_t_virtual = (1 << 30) / (c["t_stack_kb"] * 1024)
        n_t_kernel = (1 << 30) / (24 * 1024)
        data = [("goroutines", n_g, T.GO, f"{n_g:,.0f}", f"at {per_g:,} B each (measured)"),
                ("threads, if the 8 MB stacks were real", n_t_virtual, T.AMBER, f"{n_t_virtual:,.0f}", "virtual reservation"),
                ("threads, kernel memory only", n_t_kernel, T.AMBER, f"{n_t_kernel:,.0f}", "about 24 KB: kernel stack + task_struct")]
        y = sec.get_bottom()[1] - 0.28
        W = X1 - x - 0.1
        for lab, v, col, vs, note in data:
            L = max(W * v / n_g, 0.04)
            bar = RoundedRectangle(width=L, height=0.24, corner_radius=0.05).set_fill(col, 0.9).set_stroke(width=0)
            bar.move_to(P(x + L / 2, y - 0.36))
            t = txt(f"**{vs}**  {lab}", size=14, color=T.TEXT).move_to(P(x, y - 0.1), aligned_edge=LEFT)
            nt = txt(note, size=12, color=T.MUTED).move_to(P(x + L + 0.1, y - 0.36), aligned_edge=LEFT)
            if L > W - 2.5:
                nt.move_to(P(x + 0.1, y - 0.36), aligned_edge=LEFT).set_color(T.BG)
            self.add(bar, t, nt)
            y -= 0.6
        k = callout("key", "Goroutines are cheap because they are **just data** in the Go heap: a small growable "
                    "stack plus a few hundred bytes of bookkeeping. The kernel never sees them.",
                    width=X1 - x, size=13)
        self.at(k, x, y + 0.05)


class C2Models(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Three ways to map tasks onto OS threads"
    SUB = "Who schedules what? The answer decides how cheap a task is and whether tasks can use many cores."

    def build(self):
        w = 4.15
        cols = [
            ("1 : 1", "kernel threads", T.AMBER, "Every task is an OS thread. Simple and parallel, but each one costs kernel memory and a kernel switch.",
             "C pthreads, Java platform threads, Rust std::thread", (3, 3)),
            ("N : 1", "green threads", T.PINK, "Many user tasks share one OS thread. Very cheap switches, but no parallelism, and one blocking syscall stalls them all.",
             "early Java (1.1), GNU Pth, Python asyncio's loop", (5, 1)),
            ("M : N", "hybrid (Go)", T.GO, "M goroutines run on N threads chosen by a runtime scheduler. Cheap like green threads, parallel like 1:1.",
             "Go, Erlang/BEAM, Java 21 virtual threads, Tokio", (6, 3)),
        ]
        for i, (ratio, name, col, desc, who, (nt, nk)) in enumerate(cols):
            x = X0 + i * (w + 0.37)
            bx = rbox(w, 5.7, color=col, fill=T.PANEL, radius=0.16, stroke_width=1.8)
            self.at(bx, x, Y0)
            head = VGroup(txt(f"**{ratio}**", size=30, color=col), txt(f"**{name}**", size=16, color=T.TEXT)).arrange(RIGHT, buff=0.25)
            self.at(head, x + 0.2, Y0 - 0.15)
            cx = x + w / 2
            ty, ry, ky, cy = Y0 - 1.15, Y0 - 1.95, Y0 - 2.7, Y0 - 3.4
            tasks = VGroup(*[gtok("", w=0.36, h=0.26, color=col if col != T.AMBER else T.AMBER, eyes=False) for _ in range(nt)])
            tasks.arrange(RIGHT, buff=0.08).move_to(P(cx, ty))
            self.add(txt("tasks", size=11, color=T.MUTED).move_to(P(x + 0.35, ty + 0.3)))
            if i == 2:
                rt = rbox(w - 0.5, 0.36, color=T.VIOLET, fill=T.VIOLET, fill_opacity=0.15, radius=0.08).move_to(P(cx, ry))
                self.add(rt, txt("**Go scheduler**", size=12, color=T.VIOLET).move_to(rt))
            elif i == 1:
                rt = rbox(w - 0.5, 0.36, color=T.PINK, fill=T.PINK, fill_opacity=0.12, radius=0.08).move_to(P(cx, ry))
                self.add(rt, txt("**user-space scheduler**", size=12, color=T.PINK).move_to(rt))
            threads = VGroup(*[mthread("", w=0.55, h=0.34) for _ in range(nk)]).arrange(RIGHT, buff=0.3).move_to(P(cx, ky))
            kern = kernel_band(w - 0.4, 0.3, "kernel scheduler").move_to(P(cx, (ky + cy) / 2 - 0.05))
            cores = VGroup(*[cpu_core("", w=0.55, h=0.32) for _ in range(3)]).arrange(RIGHT, buff=0.3).move_to(P(cx, cy))
            self.add(tasks, threads, cores, kern)
            for j, tk in enumerate(tasks):
                tgt = threads[min(j * nk // nt, nk - 1)] if i != 0 else threads[j]
                mid = P(tk.get_center()[0], ry) if i else None
                if i == 0:
                    self.add(Line(tk.get_bottom(), tgt.get_top()).set_stroke(col, 1.5, 0.8))
                else:
                    self.add(Line(tk.get_bottom(), P(tk.get_center()[0], ry + 0.18)).set_stroke(col, 1.5, 0.8))
            if i:
                for th in threads:
                    self.add(Line(P(th.get_center()[0], ry - 0.18), th.get_top()).set_stroke(T.AMBER, 1.5, 0.8))
            dd = txt(desc, size=14, color=T.TEXT2, width=w - 0.4)
            self.at(dd, x + 0.2, cy - 0.45)
            ww = txt(f"{{muted|{who}}}", size=12, width=w - 0.4)
            self.at(ww, x + 0.2, dd.get_bottom()[1] - 0.12)


class C2Anatomy(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "What a goroutine is made of"
    SUB = "To the runtime a goroutine is a struct called g (in runtime/runtime2.go) plus a stack it owns. Here are the fields that matter."

    def build(self):
        fields = '''type g struct {
    stack       stack   // [lo, hi): this goroutine's stack
    stackguard0 uintptr // checked in every function prologue
    _panic      *_panic // innermost panic
    _defer      *_defer // innermost deferred call
    m           *m      // the OS thread running it (if any)
    sched       gobuf   // saved SP, PC, BP when not running
    atomicstatus atomic.Uint32 // _Grunnable, _Grunning, ...
    goid        uint64  // id shown in panics and traces
    waitreason  waitReason // "chan receive", "sleep", ...
    preempt     bool    // a request to yield soon
    lockedm     muintptr // set by runtime.LockOSThread
    parentGoid  uint64  // who started it
    startpc     uintptr // the function passed to go
    waiting     *sudog  // channel waits it is part of
    // ... about 60 more fields
}

type gobuf struct {
    sp, pc, bp uintptr // the whole "context" of a switch
    g    guintptr
    ctxt unsafe.Pointer
    lr   uintptr       // link register (ARM)
}'''
        cd = code(fields, size=13, title="runtime/runtime2.go (Go 1.27, abridged)", hl=[2, 7, 8, (20, T.GREEN)],
                  marks={2: "1", 7: "2", 8: "3"})
        self.at(cd, X0, Y0)
        x = cd.get_right()[0] + 0.5
        # drawing: g struct -> stack
        gbox = titled_box("g  (in the heap)", 2.4, 2.2, color=T.GO)
        self.at(gbox, x, Y0 - 0.1)
        rows = ["stack.lo / hi", "sched.sp", "sched.pc", "atomicstatus"]
        for i, r in enumerate(rows):
            self.add(txt(r, size=13, color=T.TEXT, font=T.MONO, markup=False).move_to(gbox.box.get_corner(UL) + P(0.2, -0.62 - 0.36 * i), aligned_edge=LEFT))
        sx = x + 3.5
        stack = VGroup()
        frames = [("main.main", T.STROKE2), ("worker()", T.GO_DARK), ("process()", T.GO_DARK), ("free", None)]
        sy = Y0 - 0.1
        for name, col in frames:
            h = 0.5 if col else 1.0
            r = Rectangle(width=2.0, height=h).set_fill(col or T.BG, 0.6 if col else 0.3).set_stroke(T.GO, 1.5)
            r.move_to(P(sx + 1.0, sy - h / 2))
            t = txt(name, size=12, color=T.TEXT if col else T.MUTED, font=T.MONO, markup=False).move_to(r)
            stack.add(r, t)
            sy -= h
        self.add(stack)
        self.add(txt("**stack: 2 KB, grows**", size=13, color=T.GO).next_to(stack, UP, buff=0.1))
        self.add(txt("hi", size=11, color=T.MUTED).next_to(stack, LEFT, buff=0.05).align_to(stack, UP))
        self.add(txt("lo", size=11, color=T.MUTED).next_to(stack, LEFT, buff=0.05).align_to(stack, DOWN))
        self.add(arrow(gbox.box.get_right() + UP * 0.48, stack[0].get_left() + UP * 0.1, T.GO, 2.2))
        self.add(arrow(gbox.box.get_right() + UP * 0.12, stack[4].get_left() + DOWN * 0.05, T.TEXT2, 2.2))
        notes = bullets([(badge("1", T.YELLOW, r=0.12, size=12), "`stack` bounds the goroutine's own stack; `stackguard0` sits a little above `lo` to detect overflow"),
                         (badge("2", T.YELLOW, r=0.12, size=12), "`sched` is where SP, PC and BP are saved when the goroutine stops running"),
                         (badge("3", T.YELLOW, r=0.12, size=12), "`atomicstatus` is the state machine of chapter 8.3")],
                        width=X1 - x, size=14, gap=0.1)
        self.at(notes, x, Y0 - 2.55)
        k = callout("key", "A goroutine switch saves **three registers** (SP, PC, BP) into `gobuf` and loads three others. "
                    "No kernel entry, no page-table change.", width=X1 - x, size=14)
        self.at(k, x, notes.get_bottom()[1] - 0.25)


class C2Switch(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Why a goroutine switch is cheap"
    SUB = "Both programs bounce a value between two workers. The goroutines never leave user space."

    def build(self):
        c = _costs()
        ratio = c["t_switch_us"] * 1000 / c["g_switch_ns"]
        # two lanes of steps
        def path(title, col, steps, y, kernel_idx=()):
            self.add(txt(f"**{title}**", size=17, color=col).move_to(P(X0, y), aligned_edge=LEFT))
            xx = X0
            yy = y - 0.62
            prev = None
            for i, s in enumerate(steps):
                cl = T.BLUE if i in kernel_idx else col
                n = node(s, w=1.92, h=0.62, color=cl, size=12)
                n.move_to(P(xx + 0.96, yy))
                self.add(n)
                if prev is not None:
                    self.add(arrow(prev.get_right(), n.get_left(), T.MUTED, 2, 0.02))
                prev = n
                xx += 2.13
            return prev
        path("OS thread switch", T.AMBER, ["thread A calls write()", "trap: user → kernel", "save all registers",
                                           "scheduler picks B", "restore B, return", "B runs"], Y0, kernel_idx=(1, 2, 3, 4))
        span = Rectangle(width=2.13 * 4 - 0.2, height=0.1).move_to(P(X0 + 2.13 * 3 - 0.1, Y0 - 1.0)).set_opacity(0)
        self.add(brace_label(span, "inside the kernel", DOWN, T.BLUE, 13))
        path("goroutine switch", T.GO, ["G1 does ch <- v", "gopark: save SP, PC, BP", "schedule() on g0",
                                         "pick G2 from run queue", "gogo: load G2's SP, PC", "G2 runs"], Y0 - 2.05)
        self.add(txt("everything stays in user space, on the same OS thread", size=13, color=T.GO)
                 .move_to(P(X0 + 2.13 * 3 - 0.1, Y0 - 3.05)))
        # measured bars
        y = Y0 - 3.55
        self.at(section("MEASURED ON THIS MACHINE (lower is better)", T.GO), X0, y)
        W = 6.6
        tv, gv = c["t_switch_us"] * 1000, c["g_switch_ns"]
        for i, (lab, v, col, s) in enumerate([("OS thread switch", tv, T.AMBER, f"{c['t_switch_us']:.2f} µs"),
                                              ("goroutine switch", gv, T.GO, f"{gv:.0f} ns")]):
            yy = y - 0.62 - i * 0.5
            self.add(txt(lab, size=14, color=T.TEXT2).move_to(P(X0 + 2.1, yy), aligned_edge=RIGHT))
            L = max(W * v / tv, 0.05)
            bar = RoundedRectangle(width=L, height=0.28, corner_radius=0.05).set_fill(col, 0.9).set_stroke(width=0)
            bar.move_to(P(X0 + 2.25 + L / 2, yy))
            self.add(bar, txt(f"**{s}**", size=14, color=T.TEXT).next_to(bar, RIGHT, buff=0.1))
        st = stat(f"{ratio:.0f}x", "cheaper to switch goroutines", T.GO, w=2.4, size_v=36)
        self.at(st, X1 - 2.4, y - 0.05)
        n = txt("Thread numbers come from `threads.c`, goroutine numbers from `examples/ch02_switch_bench` "
                "(`GOMAXPROCS=1`). The thread figure includes two syscalls per hop, which is what a real hand-off costs.",
                size=12, color=T.MUTED, width=CW - 2.6)
        self.at(n, X0, y - 1.62)


class C2Scale(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Putting it together: cost per unit of concurrency"
    SUB = "Each comparison has its own scale. Lower is better in every row."

    def build(self):
        c = _costs()
        rows = [("create and finish one", c["t_create_us"] * 1000, c["g_create_ns"], "ns", lambda v: f"{v / 1000:.1f} µs" if v >= 1000 else f"{v:.0f} ns"),
                ("switch between two", c["t_switch_us"] * 1000, c["g_switch_ns"], "ns", lambda v: f"{v / 1000:.2f} µs" if v >= 1000 else f"{v:.0f} ns"),
                ("stack reserved at start", c["t_stack_kb"] * 1024, c["g_stack_b"], "B", lambda v: f"{v / 1048576:.0f} MB" if v >= 1048576 else f"{v / 1024:.0f} KB"),
                ]
        y = Y0 - 0.1
        W = 5.2
        for lab, tv, gv, unit, fmt in rows:
            self.at(txt(f"**{lab}**", size=18, color=T.TEXT), X0, y)
            for j, (who, v, col) in enumerate((("OS thread", tv, T.AMBER), ("goroutine", gv, T.GO))):
                yy = y - 0.55 - j * 0.42
                self.add(txt(who, size=14, color=T.TEXT2).move_to(P(X0 + 1.55, yy), aligned_edge=RIGHT))
                L = max(W * v / tv, 0.05)
                bar = RoundedRectangle(width=L, height=0.26, corner_radius=0.05).set_fill(col, 0.9).set_stroke(width=0)
                bar.move_to(P(X0 + 1.7 + L / 2, yy))
                self.add(bar, txt(f"**{fmt(v)}**", size=14, color=T.TEXT).next_to(bar, RIGHT, buff=0.1))
            self.add(pill(f"{tv / gv:,.0f}x less for a goroutine", T.GO, size=12, filled=False).move_to(P(X0 + 3.6, y - 0.02), aligned_edge=LEFT))
            y -= 1.6
        x = 2.0
        rx = X1 - 4.7
        self.at(section("BACK-OF-THE-ENVELOPE", T.GREEN), rx, Y0)
        mem = int(c["g_total_b"])
        calc = txt(f"A chat server with **1,000,000** connections, one reader and one writer goroutine each:\n\n"
                   f"2,000,000 × {mem:,} B ≈ **{2e6 * mem / 1e9:.1f} GB**\n\n"
                   f"The same design with OS threads would need 2,000,000 threads, far beyond this machine's "
                   f"`pid_max` of 32,768, and 16 TB of reserved stack.", size=15, color=T.TEXT, width=4.7)
        self.at(calc, rx, Y0 - 0.5)
        warn = callout("warn", "Cheap is not free. A leaked goroutine holds its stack and everything it references "
                       "forever (chapter 8.17).", width=4.7, size=14)
        self.at(warn, rx, calc.get_bottom()[1] - 0.3)
        tip = callout("tip", "Goroutine stacks start small and **grow by copying**; deep recursion is fine (chapter 8.3).",
                      width=4.7, size=14)
        self.at(tip, rx, warn.get_bottom()[1] - 0.2)


class C2Recap(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Recap and check yourself"
    SUB = "Threads are the kernel's unit of execution; goroutines are the Go runtime's."

    def build(self):
        c = _costs()
        self.at(section("REMEMBER", T.GO), X0, Y0)
        rec = bullets([
            "Threads of a process share heap, globals and files; each has its own stack and registers.",
            f"An OS thread costs about {c['t_create_us']:.0f} µs to create and {c['t_switch_us']:.0f} µs per hand-off here, plus {c['t_stack_kb'] / 1024:.0f} MB of reserved stack.",
            f"A goroutine starts with a {c['g_stack_b'] / 1024:.0f} KB stack, costs about {int(c['g_total_b']):,} bytes in total and switches in about {c['g_switch_ns']:.0f} ns.",
            "Go uses **M:N** scheduling: many goroutines on a few threads, picked by the runtime.",
            "A goroutine is a `g` struct plus a stack; a switch saves SP, PC and BP into `g.sched`.",
        ], width=6.0, size=16, marker="check", marker_color=T.GREEN, gap=0.16)
        self.at(rec, X0, Y0 - 0.5)
        x = 0.55
        self.at(section("CHECK YOURSELF", T.TEAL), x, Y0)
        qs = [("Why can't an N:1 green-thread system use four cores?",
               "All its tasks share one OS thread, and the kernel only schedules threads."),
              ("Two goroutines in the same program write to the same slice. Are they isolated like processes?",
               "No. They share the heap exactly like threads; you need a channel or a lock."),
              ("Which three registers does a goroutine switch save?",
               "The stack pointer, the program counter and the frame pointer (gobuf.sp, pc, bp)."),
              ("Roughly how much memory do 50,000 idle goroutines need?",
               f"About 50,000 × {int(c['g_total_b']):,} B ≈ {5e4 * c['g_total_b'] / 1e6:.0f} MB.")]
        y = Y0 - 0.5
        for i, (q, a) in enumerate(qs):
            grp = vstack(txt(f"**Q{i + 1}.** {q}", size=16, color=T.TEXT, width=6.0),
                         txt(f"{{teal|**Answer.**}} {a}", size=15, color=T.TEXT2, width=6.0), buff=0.08)
            self.at(grp, x, y)
            y = grp.get_bottom()[1] - 0.3
        g = gopher(1.1).move_to(P(X0 + 0.9, -2.75))
        b = bubble("I'm just a struct and 2 KB of stack. Spawn away!", width=3.6, tail="left", tail_x=-0.1)
        b.next_to(g, RIGHT, buff=0.35).shift(UP * 0.2)
        self.add(g, b)
