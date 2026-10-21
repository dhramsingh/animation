from kit import *

CH, NAME = "8.3", "Goroutines in Depth"


class C3Opener(Opener):
    NUM, NAME = CH, NAME
    TAGLINE = "One keyword starts a goroutine. Knowing exactly what it evaluates, when it dies and how its stack grows separates working code from flaky code."
    LEARN = ["Apply the evaluation rules of the `go` statement",
             "Explain why returning from `main` kills every goroutine",
             "Capture loop variables safely, before and after Go 1.22",
             "Trace a goroutine through the runtime's state machine",
             "Describe growable stacks, and why goroutines have no ID"]
    QUESTION = "A program starts a goroutine that prints three lines, yet none of them appear. Nothing crashed. Where did they go?"

    def art(self):
        g = VGroup()
        boss = gopher(1.6).move_to(P(2.2, 0.0))
        key = rbox(1.1, 0.55, color=T.GO, fill=T.GO, fill_opacity=0.95, radius=0.12).next_to(boss, DOWN, buff=0.15)
        kt = txt("**go**", size=22, color=T.BG, font=T.MONO).move_to(key)
        g.add(boss, key, kt)
        ys = [1.9, 0.3, -1.3]
        for i, y in enumerate(ys):
            t = gtok(f"G{i + 2}", w=1.0, h=0.46).move_to(P(5.6, y))
            a = arrow(boss.get_right() + P(0.1, 0), t.get_left(), T.GO, thick=2.5, arc=-0.2 + 0.2 * i)
            g.add(a, t)
        g.add(txt("main", size=14, color=T.TEXT2, weight="BOLD").next_to(boss, UP, buff=0.1))
        lab = txt("each `go` starts a new goroutine;\n`main` keeps going without waiting", size=14, color=T.TEXT2, align="CENTER")
        lab.move_to(P(3.9, -2.6))
        g.add(lab)
        return g


class C3GoStatement(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "The go statement"
    SUB = "`go` + a function call. The call's arguments are evaluated now, in the current goroutine; the body runs later, in a new one."

    def build(self):
        forms = code('''go worker(id, jobs)      // a named function
go srv.handle(conn)      // a method value
go func(n int) {         // a function literal...
    fmt.Println("got", n)
}(42)                    // ...called on the spot
go fmt.Println("hi")     // any function at all
go close(done)           // ok: close, copy, panic, print

// go len(s)             // NOT allowed: len, cap, make...
// v := go f()           // NOT allowed: go is a statement''', size=14, title="the forms of go", numbers=False)
        self.at(forms, X0, Y0)
        rules = num_steps([("Evaluate", "the function value and every argument, right now, in the calling goroutine."),
                           ("Create", "a new goroutine (a g with a fresh stack) and put it on a run queue."),
                           ("Continue", "the caller immediately; it does not wait for the new goroutine."),
                           ("Discard", "the function's return values; use a channel to get results back.")],
                          width=forms.get_width(), color=T.GO, size=15, gap=0.14)
        self.at(rules, X0, forms.get_bottom()[1] - 0.3)

        x = forms.get_right()[0] + 0.5
        w = X1 - x
        cd = code_ex("ch03_args", lines=(8, 14), size=13, hl=[10, 11], marks={10: "1", 11: "2"})
        self.at(cd, x, Y0)
        tm = terminal(out("ch03_args"), title="one possible output", width=cd.get_width(), size=13)
        self.at(tm, x, cd.get_bottom()[1] - 0.12)
        y = tm.get_bottom()[1] - 0.32
        lanes = [("main", T.GO, [(0.0, 1.0, "x := 1"), (1.05, 2.2, "go Println(x)"), (2.25, 3.4, "go func(){}"), (3.45, 4.3, "x = 2"), (4.35, 6.2, "sleep")]),
                 ("G2", T.PINK, [(2.3, 4.6, "prints 1 (a copy)")]),
                 ("G3", T.AMBER, [(4.6, 6.2, "reads x: 2")])]
        unit = (w - 0.7) / 6.25
        for i, (lab, col, segs) in enumerate(lanes):
            yy = y - i * 0.4
            self.add(txt(f"**{lab}**", size=12, color=col).move_to(P(x + 0.5, yy), aligned_edge=RIGHT))
            for a, b, s in segs:
                self.add(seg(x + 0.65 + a * unit, x + 0.65 + b * unit - 0.03, yy, col, h=0.28, lab=s, size=11))
        self.add(arrow(P(x + 0.65 + 1.9 * unit, y - 0.14), P(x + 0.65 + 2.35 * unit, y - 0.4 + 0.14), T.TEXT2, 1.8, 0.0))
        self.add(arrow(P(x + 0.65 + 3.0 * unit, y - 0.14), P(x + 0.65 + 4.65 * unit, y - 0.8 + 0.14), T.TEXT2, 1.8, 0.0))
        notes = bullets([(badge("1", T.YELLOW, r=0.12, size=12), "`x` is an **argument**: copied at the `go` statement, so G2 prints 1"),
                         (badge("2", T.YELLOW, r=0.12, size=12), "the closure **captures the variable**; G3 reads it later and sees 2")],
                        width=w, size=14, gap=0.06)
        self.at(notes, x, y - 0.98)
        w2 = callout("warn", "The closure version is also a **data race**: main writes `x` while G3 reads it. "
                     "Pass values as arguments, or synchronise.", width=w, size=13, inline=True)
        self.at(w2, x, notes.get_bottom()[1] - 0.08)


class C3MainExits(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "When main returns, every goroutine dies"
    SUB = "A Go program ends the instant `main.main` returns. The runtime does not wait for other goroutines, and their deferred calls never run."

    def build(self):
        cd = code_ex("ch03_main_exits", size=15, hl=[12, 14], marks={12: "1", 14: "2"})
        self.at(cd, X0, Y0)
        tm = terminal(out("ch03_main_exits"), title="output", width=cd.get_width(), size=14)
        self.at(tm, X0, cd.get_bottom()[1] - 0.2)
        a = callout("q", "The three lines from `say` were never printed: the goroutine was still waiting "
                    "for a CPU when `main` returned and the process exited.", width=cd.get_width(), title="THE BIG QUESTION, ANSWERED", size=14)
        self.at(a, X0, tm.get_bottom()[1] - 0.14)

        x = cd.get_right()[0] + 0.6
        w = X1 - x
        self.at(section("WHAT HAPPENS", T.RED), x, Y0)
        y0 = Y0 - 0.8
        ml = lane("main", x + 0.9, X1 - 0.2, y0, T.GO, size=14, label_w=0.8)
        gl = lane("say", x + 0.9, X1 - 0.2, y0 - 0.8, T.PINK, size=14, label_w=0.8)
        self.add(ml, gl)
        x_go, x_end = x + 1.6, x + 3.6
        self.add(seg(x + 0.95, x_end, y0, T.GO, h=0.34, lab="go say(...)  Println  return", size=11))
        self.add(seg(x_go + 0.2, x_end, y0 - 0.8, T.PINK, h=0.34, lab="runnable", size=11, outline=True))
        self.add(arrow(P(x_go, y0 - 0.18), P(x_go + 0.25, y0 - 0.62), T.TEXT2, 2, 0))
        cut = DashedLine(P(x_end + 0.05, y0 + 0.4), P(x_end + 0.05, y0 - 1.2)).set_stroke(T.RED, 3)
        self.add(cut, txt("**exit(0)**", size=14, color=T.RED).next_to(cut, UP, buff=0.05))
        self.add(cross_mark(T.RED, 0.16).move_to(P(x_end + 0.45, y0 - 0.8)))
        self.add(txt("never printed", size=12, color=T.RED).move_to(P(x_end + 0.6, y0 - 1.15), aligned_edge=LEFT))
        notes = bullets([(badge("1", T.YELLOW, r=0.12, size=12), "`go say(...)` only **schedules** the goroutine"),
                         (badge("2", T.YELLOW, r=0.12, size=12), "`main` returns, the runtime calls `exit(0)`; all goroutines vanish mid-flight")],
                        width=w, size=15, gap=0.1)
        self.at(notes, x, y0 - 1.6)
        fix = callout("tip", "To wait, use a `sync.WaitGroup` or receive from a channel (chapter 8.4). "
                      "`time.Sleep` is a guess, not synchronisation: it fails on a slow or busy machine.", width=w, size=14)
        self.at(fix, x, notes.get_bottom()[1] - 0.3)
        hood = callout("hood", "`os.Exit` also ends the process without running defers. And `runtime.Goexit` in `main` "
                       "lets the others finish, then crashes with \"no goroutines (main called runtime.Goexit) - deadlock!\".",
                       width=w, size=13)
        self.at(hood, x, fix.get_bottom()[1] - 0.15)


class C3LoopVar(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Closures and the loop variable: Go 1.22 changed the rules"
    SUB = "Before Go 1.22 a `for` loop had one variable shared by all iterations. Since 1.22 each iteration gets its own. The `go` line in go.mod decides."

    def build(self):
        w = 6.45
        old = code_ex("ch03_loopvar_old", lines=(9, 20), size=13, width=w, hl=[(11, T.RED), (15, T.RED)],
                      title="ch03_loopvar_old/main.go   (go.mod: go 1.21)")
        self.at(old, X0, Y0)
        to = terminal(out("ch03_loopvar_old"), title="output", width=w, size=13)
        self.at(to, X0, old.get_bottom()[1] - 0.12)
        new = code_ex("ch03_loopvar", lines=(8, 15), size=13, width=w, hl=[(10, T.GREEN), (11, T.GREEN)],
                      title="ch03_loopvar/main.go   (go.mod: go 1.27)")
        self.at(new, X1 - w, Y0)
        tn = terminal(out("ch03_loopvar"), title="one possible output", width=w, size=13)
        self.at(tn, X1 - w, new.get_bottom()[1] - 0.12)
        y = min(to.get_bottom()[1], tn.get_bottom()[1]) - 0.25
        hgt = y - Y1 - 0.02
        lb = titled_box("Go ≤ 1.21: one i for the whole loop", w, hgt, color=T.RED)
        self.at(lb, X0, y)
        rb = titled_box("Go ≥ 1.22: a new i per iteration", w, hgt, color=T.GREEN)
        self.at(rb, X1 - w, y)
        cy = y - 0.4 - (hgt - 0.75) / 2
        var = VGroup(rbox(0.95, 0.55, color=T.PINK, fill=T.PINK, fill_opacity=0.2), txt("**i = 3**", size=15, color=T.PINK))
        var[1].move_to(var[0])
        var.move_to(P(X0 + w * 0.62, cy))
        self.add(var)
        gs = VGroup(*[gtok(f"G{k + 1}", w=0.66, h=0.3) for k in range(3)]).arrange(RIGHT, buff=0.15)
        gs.move_to(P(X0 + 1.55, cy))
        self.add(gs)
        for k, tk in enumerate(gs):
            self.add(arrow(tk.get_top(), var[0].get_top() + LEFT * (0.2 - 0.2 * k), T.RED, 1.8, 0.04, arc=-0.6))
        self.add(txt("all three closures read one variable, after the loop ended", size=12, color=T.TEXT2)
                 .move_to(P(X0 + w / 2, lb.box.get_bottom()[1] + 0.2)))
        for k in range(3):
            vx = X1 - w + 1.1 + k * 2.1
            v = VGroup(rbox(0.85, 0.45, color=T.PINK, fill=T.PINK, fill_opacity=0.2), txt(f"**i = {k}**", size=14, color=T.PINK))
            v[1].move_to(v[0])
            v.move_to(P(vx + 0.6, cy))
            tk = gtok(f"G{k + 1}", w=0.66, h=0.3).next_to(v, LEFT, buff=0.3)
            self.add(v, tk, arrow(tk.get_right(), v[0].get_left(), T.GREEN, 1.8, 0.04))
        self.add(txt("each closure captures its own copy; the order still varies", size=12, color=T.TEXT2)
                 .move_to(P(X1 - w / 2, rb.box.get_bottom()[1] + 0.2)))


class C3LoopVarFix(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Loop variables: rules you can rely on"
    SUB = "New code gets the safe behaviour automatically. Old modules, and code you copy from old blogs, still need care."

    def build(self):
        dd = do_dont('''// module says "go 1.21" or older
for i := 0; i < 3; i++ {
    go func() {
        fmt.Print(i) // shared i
    }()
}''', '''// works with ANY Go version
for i := 0; i < 3; i++ {
    go func(i int) { // a parameter
        fmt.Print(i)  // copied per call
    }(i)
}''', bad_note="Prints `3 3 3` (or `2 3 3`...): the goroutines run after the loop has moved on.",
                     good_note="Passing `i` as an argument copies it at the `go` statement (rule 1 of the go statement).",
                     width=8.0, bad_hl=[4], good_hl=[3, 5])
        self.at(dd, X0, Y0)
        x = dd.get_right()[0] + 0.45
        w = X1 - x
        rules = bullets(["The semantics come from the `go` line in **go.mod**, not from the compiler version.",
                         "Go 1.22+ applies it to `for i := ...` and `for k, v := range ...` loops.",
                         "The old fix `i := i` inside the body still works, but is no longer needed.",
                         "`go vet` (check **loopclosure**) flags the old pattern in old modules."],
                        width=w, size=15, gap=0.14)
        self.at(section("RULES", T.GO), x, Y0)
        self.at(rules, x, Y0 - 0.5)
        v = callout("version", "Go 1.22 (Feb 2024) made loop variables per-iteration. Go 1.22 also added `for i := range 10` "
                    "over integers, used throughout this book.", width=w, size=14)
        self.at(v, x, rules.get_bottom()[1] - 0.3)
        k = callout("key", "Even with per-iteration variables, **goroutines run in any order**. The output `0 2 1` is just one possibility.",
                    width=CW, size=15, inline=True)
        self.at(k, X0, min(dd.get_bottom()[1], v.get_bottom()[1]) - 0.35)


class C3Lifecycle(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "The life of a goroutine: the runtime's state machine"
    SUB = "Every goroutine is always in exactly one state, stored in g.atomicstatus. These names appear in the runtime source and its tracebacks."

    def build(self):
        def st(name, desc, col, w=2.25):
            b = rbox(w, 0.78, color=col, fill=col, fill_opacity=0.14, radius=0.14, stroke_width=2.2)
            n = txt(f"**{name}**", size=15, color=col, font=T.MONO)
            d = txt(desc, size=11, color=T.TEXT2, align="CENTER", width=w - 0.15)
            VGroup(n, d).arrange(DOWN, buff=0.05).move_to(b)
            g = VGroup(b, n, d)
            g.box = b
            return g
        S = {
            "idle": st("_Gidle", "just allocated", T.GREY),
            "dead": st("_Gdead", "unused, on a free list", "#64748B"),
            "runnable": st("_Grunnable", "in a run queue", T.GREEN),
            "running": st("_Grunning", "executing on an M + P", T.GO),
            "syscall": st("_Gsyscall", "in a system call", T.AMBER),
            "waiting": st("_Gwaiting", "parked: chan, lock, sleep...", T.BLUE),
            "preempted": st("_Gpreempted", "stopped for GC scan", T.VIOLET),
            "leaked": st("_Gleaked", "found by leak GC (1.27)", T.RED),
        }
        yt, yb = 1.1, -1.3
        pos = {"idle": (-5.4, yt), "runnable": (-1.75, yt), "running": (2.05, yt), "syscall": (5.45, yt),
               "dead": (-5.4, yb), "leaked": (-2.75, yb), "waiting": (0.0, yb), "preempted": (3.6, yb)}
        for k, (x, y) in pos.items():
            S[k].move_to(P(x, y))
            self.add(S[k])
        B = {k: S[k].box for k in S}

        def link(pa, pb, col, lab=None, lp=None, dash=False, arc=0.0, size=12):
            self.add(dashed_arrow(pa, pb, col, 2.2) if dash else arrow(pa, pb, col, 2.4, 0.04, arc))
            if lab:
                self.add(txt(lab, size=size, color=T.TEXT if col == T.TEXT2 else col, align="CENTER").move_to(P(*lp)))
        top, bot, rt, lf = (lambda k, dx=0: B[k].get_top() + RIGHT * dx), (lambda k, dx=0: B[k].get_bottom() + RIGHT * dx), \
            (lambda k, dy=0: B[k].get_right() + UP * dy), (lambda k, dy=0: B[k].get_left() + UP * dy)
        link(bot("idle"), top("dead"), T.TEXT2, "malg: allocate", (-4.55, -0.1))
        link(rt("dead", 0.2), lf("runnable", -0.2), T.GREEN, "newproc:\n`go f()`", (-3.05, 0.1))
        link(rt("runnable", 0.14), lf("running", 0.14), T.TEXT2, "execute", (0.15, yt + 0.37))
        link(lf("running", -0.14), rt("runnable", -0.14), T.TEXT2, "Gosched, preempted", (0.15, yt - 0.37))
        link(rt("running", 0.14), lf("syscall", 0.14), T.AMBER, "entersyscall", (3.75, yt + 0.37))
        link(lf("syscall", -0.14), rt("running", -0.14), T.AMBER, "exitsyscall", (3.75, yt - 0.37))
        link(bot("running", -0.55), top("waiting", 0.45), T.BLUE, "gopark", (1.45, -0.1))
        link(top("waiting", -0.45), bot("runnable", 0.55), T.GREEN, "goready", (-1.25, -0.1))
        link(bot("running", 0.55), top("preempted", -0.3), T.VIOLET, "suspendG", (3.45, -0.1))
        link(lf("preempted"), rt("waiting"), T.VIOLET, "taken over", (1.8, yb + 0.28))
        link(lf("waiting"), rt("leaked"), T.RED, None, dash=True)
        self.add(txt("blocked\nforever", size=11, color=T.RED, align="CENTER").move_to(P(-1.38, yb + 0.42)))
        link(top("syscall"), top("runnable"), T.AMBER, "exitsyscall, but no P is free: back to a run queue", (1.85, yt + 0.95), arc=0.45)
        path = elbow_arrow([rt("running", -0.25), P(6.85, yt - 0.25), P(6.85, -2.2), P(-5.4, -2.2), bot("dead")], T.MUTED, 2.2)
        self.add(path, txt("goexit: the function returned; the g goes back to a free list to be reused by a later `go`",
                           size=12, color=T.TEXT2).move_to(P(0.6, -2.42)))
        wr = ["chan receive", "chan send", "select", "sleep", "IO wait", "sync.Mutex.Lock", "sync.WaitGroup.Wait", "semacquire"]
        chips = VGroup(*[pill(w_, T.BLUE, size=12, filled=False, mono_font=True, weight="NORMAL") for w_ in wr]).arrange(RIGHT, buff=0.12)
        lab = txt("A goroutine in `_Gwaiting` **always carries a reason**, shown in tracebacks as `goroutine 7 [chan receive]`:", size=14, color=T.TEXT2)
        grp = vstack(lab, chips, buff=0.12)
        self.at(grp, X0, -2.72)
        self.add(txt("`_Gcopystack` (not drawn) is a brief state while a stack is moved.", size=12, color=T.MUTED)
                 .move_to(P(X1, -2.72), aligned_edge=UR))


class C3Stacks(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Growable stacks: start small, double, copy"
    SUB = "Every Go function starts by comparing the stack pointer with a guard. If the frame will not fit, the runtime moves the stack to a block twice as big."

    def build(self):
        asm = code('''TEXT main.depth(SB), ABIInternal, $80-8
    CMPQ  SP, 16(R14)  // R14 = g, 16(R14) = g.stackguard0
    JLS   76           // too close to the end? grow first
    PUSHQ BP
    MOVQ  SP, BP
    SUBQ  $72, SP      // now it is safe to claim the frame
    ...
76: MOVQ  AX, 8(SP)    // spill the argument
    CALL  runtime.morestack_noctxt(SB)
    MOVQ  8(SP), AX
    JMP   0            // start the function again''', size=13, lang="text",
                   title="go build -gcflags=-S  (real output, trimmed)", hl=[2, 3, (9, T.GREEN)], numbers=False)
        self.at(asm, X0, Y0)
        steps = num_steps([("Check", "the prologue compares SP with `g.stackguard0` (a little above `stack.lo`)."),
                           ("Grow", "`morestack` → `newstack` allocates a block **2x** the old size."),
                           ("Copy", "`copystack` copies every frame and rewrites pointers that point into the stack."),
                           ("Retry", "the old stack is freed and the function starts again on the new one.")],
                          width=asm.get_width(), color=T.GO, size=14, gap=0.1)
        self.at(steps, X0, asm.get_bottom()[1] - 0.25)
        x = asm.get_right()[0] + 0.55
        fh = 0.17

        def stack_col(x0, h, frames, label, full=False):
            g = VGroup()
            box = Rectangle(width=1.05, height=h).set_fill(T.BG, 0.3).set_stroke(T.GO, 2)
            box.move_to(P(x0 + 0.52, Y0 - 0.4 - h / 2))
            g.add(box)
            yy = box.get_top()[1]
            for i in range(frames):
                last = full and i == frames - 1
                fr = Rectangle(width=1.01, height=fh).set_fill(T.RED if last else T.GO, 0.5).set_stroke(T.GO, 1)
                fr.move_to(P(x0 + 0.52, yy - fh / 2 - 0.02))
                g.add(fr)
                yy -= fh + 0.02
            g.add(txt(f"**{label}**", size=14, color=T.GO).next_to(box, UP, buff=0.08))
            return g
        s1 = stack_col(x, 0.8, 4, "2 KB", full=True)
        s2 = stack_col(x + 1.7, 1.6, 4, "4 KB")
        s3 = stack_col(x + 3.4, 3.2, 9, "8 KB")
        self.add(s1, s2, s3)
        self.add(arrow(s1[0].get_right() + UP * 0.2, s2[0].get_left() + UP * 0.6, T.YELLOW, 2.5))
        self.add(arrow(s2[0].get_right() + UP * 0.4, s3[0].get_left() + UP * 1.4, T.YELLOW, 2.5))
        self.add(txt("copy", size=12, color=T.YELLOW).move_to(P(x + 1.38, Y0 - 0.45)))
        self.add(txt("copy", size=12, color=T.YELLOW).move_to(P(x + 3.08, Y0 - 0.55)))
        self.add(txt("the next frame\ndoes not fit", size=11, color=T.RED, align="CENTER").next_to(s1, DOWN, buff=0.1))
        self.add(txt("frames keep\ntheir order;\nfree space\nbelow", size=11, color=T.MUTED, align="CENTER").next_to(s2, DOWN, buff=0.1))
        gr = nums("ch03_stack_growth", r"stack in use\s+([\d.]+) MB")
        facts = bullets(["Max stack: **1 GB** on 64-bit (250 MB on 32-bit). Beyond it: `fatal error: stack overflow`.",
                         "The GC **shrinks** a stack to half when its goroutine uses less than a quarter.",
                         f"Measured: one goroutine recursing 1,000,000 deep held **{gr[-1]:.0f} MB** of stack, with no settings.",
                         "Since Go 1.19 new goroutines start at the **average** stack size seen so far (at least 2 KB)."],
                        width=X1 - x, size=13, gap=0.07)
        self.at(facts, x, s3.get_bottom()[1] - 0.2)
        hist = callout("version", "Go ≤ 1.2 used **segmented** stacks (linked chunks). A call right at a chunk edge "
                       "could allocate and free a chunk in a tight loop (\"hot split\"). Go 1.3 switched to copying.",
                       width=X1 - x, size=13)
        self.at(hist, x, Y1 + hist.get_height() + 0.02)


class C3NoIdentity(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "No name, no handle, no kill switch"
    SUB = "Thread libraries give you an ID, a join handle and a way to cancel. Goroutines offer none of these on purpose; you build them from channels and context."

    def build(self):
        rows = [["You want to...", "Threads (pthreads, Java)", "Go"],
                ["start a task", "`pthread_create`, `new Thread()`", "`go f()`"],
                ["wait for it to finish", "`pthread_join`, `t.join()`", "`sync.WaitGroup`, a done channel"],
                ["get its result", "join + a shared variable", "a result channel, `errgroup`"],
                ["stop it from outside", "`pthread_cancel`, `t.interrupt()`", "ask it to stop: close a channel, cancel a `context`"],
                ["know who it is", "thread ID, `currentThread()`", "no public ID; pass what you need"],
                ["store per-task data", "thread-local storage", "parameters, `context.Value`"],
                ["set a priority", "`pthread_setschedparam`", "not possible"]]
        tb = table(rows, [2.05, 3.0, 3.45], size=14, col_colors=[T.TEXT2, None, T.GO_LIGHT])
        self.at(tb, X0, Y0)
        why = callout("q", "A goroutine ID invites goroutine-local state, which hides data flow and breaks as soon as work moves "
                      "to another goroutine. Killing from outside would leave locks held and data half-written. "
                      "So Go makes cancellation **cooperative**: the goroutine checks a signal and exits cleanly.",
                      width=tb.get_width(), title="WHY SO MINIMAL?", size=14)
        self.at(why, X0, tb.get_bottom()[1] - 0.25)
        x = tb.get_right()[0] + 0.4
        w = X1 - x
        self.at(section("THE runtime PACKAGE", T.VIOLET), x, Y0)
        items = bullets(["`NumGoroutine()`: how many exist now",
                         "`Gosched()`: yield, stay runnable",
                         "`Goexit()`: end this goroutine (defers run)",
                         "`LockOSThread()`: pin to one OS thread"],
                        width=w, size=14, gap=0.06, marker_color=T.VIOLET)
        self.at(items, x, Y0 - 0.48)
        cd = code_ex("ch03_numgoroutine", lines=(9, 19), size=12, width=w, numbers=False, title="ch03_numgoroutine")
        self.at(cd, x, items.get_bottom()[1] - 0.2)
        tm = terminal(out("ch03_numgoroutine"), title="output", width=w, size=12)
        self.at(tm, x, cd.get_bottom()[1] - 0.1)


class C3Panics(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "A panic in any goroutine kills the whole program"
    SUB = "`recover` only works in the goroutine that is panicking. A panic that reaches the top of any goroutine's stack crashes the process."

    def build(self):
        cd = code_ex("ch03_panic", lines=(8, 20), size=14, hl=[(11, T.GREEN), (16, T.RED)], marks={11: ("1", T.GREEN), 16: ("2", T.RED)})
        self.at(cd, X0, Y0)
        tm = terminal(out("ch03_panic"), title="output", width=cd.get_width(), size=14)
        self.at(tm, X0, cd.get_bottom()[1] - 0.15)
        x = cd.get_right()[0] + 0.5
        w = X1 - x
        self.at(section("EACH GOROUTINE UNWINDS ITS OWN STACK", T.RED), x, Y0)

        def col(x0, title, frames, colr, note):
            g = VGroup()
            g.add(txt(f"**{title}**", size=14, color=colr).move_to(P(x0 + 1.1, Y0 - 0.6)))
            y = Y0 - 0.85
            for f, c in frames:
                r = rbox(2.2, 0.4, color=c, fill=c, fill_opacity=0.15, radius=0.06).move_to(P(x0 + 1.1, y - 0.2))
                g.add(r, txt(f, size=12, color=T.TEXT, font=T.MONO, markup=False).move_to(r))
                y -= 0.48
            g.add(txt(note, size=12, color=T.TEXT2, width=2.5, align="CENTER").move_to(P(x0 + 1.1, y - 0.22)))
            return g
        cw = (w - 0.3) / 2
        self.add(col(x, "main goroutine", [("main()", T.GO), ("deferred recover()", T.GREEN)], T.GO,
                     "(1) recover waits here, but nothing panics in main"))
        self.add(col(x + cw + 0.3, "worker goroutine", [("func2(): panic!", T.RED), ("top of its stack", T.RED)], T.RED,
                     "(2) unwinds to its top, finds no recover: crash"))
        self.add(dashed(P(x + cw + 0.15, Y0 - 0.5), P(x + cw + 0.15, Y0 - 2.3), T.STROKE2, 1.5))
        fix = code('''// recover INSIDE the goroutine
func safeGo(f func(), onPanic func(any)) {
    go func() {
        defer func() {
            if r := recover(); r != nil {
                onPanic(r) // log, count, restart
            }
        }()
        f()
    }()
}''', size=12, title="pattern: recover where the panic happens", width=w, hl=[(5, T.GREEN)])
        self.at(fix, x, Y0 - 2.5)
        k = callout("version", "`WaitGroup.Go` (Go 1.25) re-panics instead of calling `Done`, so a crashing task "
                    "can never make `Wait` return early.", width=w, size=13, inline=True)
        self.at(k, x, fix.get_bottom()[1] - 0.12)


class C3Recap(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Recap and check yourself"
    SUB = "The goroutine itself: how it starts, lives, grows and ends."

    def build(self):
        self.at(section("REMEMBER", T.GO), X0, Y0)
        rec = bullets([
            "`go f(x)` evaluates `f` and `x` **now**; the body runs later in a new goroutine; results are discarded.",
            "When `main` returns the process exits: wait with a WaitGroup or channel, never with `time.Sleep`.",
            "Go 1.22+ gives each loop iteration its own variable (controlled by go.mod's `go` line).",
            "States: runnable → running → waiting/syscall → runnable ... → dead (then reused).",
            "Stacks start at 2 KB (or the running average), double by copying, and can reach 1 GB.",
            "No IDs, no join, no kill: cancellation is cooperative. A panic anywhere kills everything.",
        ], width=6.0, size=15, marker="check", marker_color=T.GREEN, gap=0.14)
        self.at(rec, X0, Y0 - 0.5)
        x = 0.55
        self.at(section("CHECK YOURSELF", T.TEAL), x, Y0)
        qs = [("`x := 1; go fmt.Println(x); x = 2`. What does the goroutine print?",
               "1. Arguments are evaluated at the go statement."),
              ("Your program prints nothing from its goroutines on a CI server but works on your laptop. First suspect?",
               "main returns (or a Sleep-based wait expires) before they run."),
              ("Which state does a goroutine blocked in `<-ch` have, and which wait reason?",
               "_Gwaiting with reason \"chan receive\"."),
              ("Why can Go grow stacks by copying when C cannot?",
               "The runtime knows every pointer into the stack (from compiler metadata) and can fix them up.")]
        y = Y0 - 0.5
        for i, (q, a) in enumerate(qs):
            grp = vstack(txt(f"**Q{i + 1}.** {q}", size=15, color=T.TEXT, width=6.0),
                         txt(f"{{teal|**Answer.**}} {a}", size=14, color=T.TEXT2, width=6.0), buff=0.08)
            self.at(grp, x, y)
            y = grp.get_bottom()[1] - 0.28
        g = gopher(1.0, mood="run").move_to(P(X0 + 0.9, -2.85))
        b = bubble("Started by `go`, finished by return. Never by force.", width=3.8, tail="left", tail_x=-0.1)
        b.next_to(g, RIGHT, buff=0.35)
        self.add(g, b)
