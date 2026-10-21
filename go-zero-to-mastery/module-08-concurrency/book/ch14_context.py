from kit import *

CH, NAME = "8.14", "Cancellation with context"


def _ctxnode(lab, sub=None, color=T.GO, w=2.0, h=0.62, size=13, state="live"):
    """A context in a tree: live (outline), cancelled (red fill)."""
    col = T.RED if state == "dead" else color
    b = rbox(w, h, color=col, fill=col, fill_opacity=0.28 if state == "dead" else 0.1, radius=0.12, stroke_width=2)
    t = txt(f"**{lab}**", size=size, color=T.TEXT, font=T.MONO)
    g = VGroup(b, t)
    if sub:
        s = txt(sub, size=size - 3, color=T.TEXT2)
        VGroup(t, s).arrange(DOWN, buff=0.04).move_to(b)
        g.add(s)
    else:
        t.move_to(b)
    g.box = b
    return g


class C14Opener(Opener):
    NUM, NAME = CH, NAME
    TAGLINE = "Goroutines are cheap to start and easy to forget. A context.Context carries one message to every goroutine working on a request: stop now, and here is why."
    LEARN = ["Give work a deadline with `WithTimeout`, and always `cancel`",
             "Cancel whole trees of goroutines from one place",
             "Look inside: `cancelCtx`, `timerCtx`, `valueCtx`",
             "Make loops, channel code and library calls cancellable",
             "Use causes, `AfterFunc`, `WithoutCancel` and values well"]
    QUESTION = ("A user closes the browser tab. The handler has three goroutines running: a database query, a call "
                "to a pricing service and a cache lookup. How do all three find out, at once?")

    def art(self):
        g = VGroup()
        root = _ctxnode("Background()", color=T.GREY, w=2.4).move_to(P(3.6, 2.3))
        req = _ctxnode("r.Context()", "timeout 2 s", color=T.GO, w=2.4, state="dead").move_to(P(3.6, 1.15))
        g.add(root, req, arrow(root.get_bottom(), req.get_top(), T.MUTED, 2, 0.04))
        bolt = Polygon(P(0, 0.35), P(-0.18, 0.0), P(0.0, 0.02), P(-0.12, -0.35), P(0.2, 0.08), P(0.02, 0.06))
        bolt.set_fill(T.YELLOW, 1).set_stroke(width=0).scale(1.2).move_to(P(5.25, 1.3))
        g.add(bolt, txt("client gone:\ncancel()", size=13, color=T.YELLOW, weight="BOLD").next_to(bolt, RIGHT, buff=0.1))
        for i, lab in enumerate(("DB query", "pricing API", "cache")):
            x = 1.55 + i * 2.05
            c = _ctxnode(lab, color=T.GO, w=1.8, h=0.5, size=12, state="dead").move_to(P(x, -0.2))
            g.add(c, arrow(req.get_bottom(), c.get_top(), T.RED, 2.6, 0.06))
            gp = gopher(0.95, mood="blocked" if i == 1 else "sleep").move_to(P(x, -1.35))
            g.add(gp, txt("<-ctx.Done()", size=12, color=T.RED, font=T.MONO).next_to(gp, DOWN, buff=0.06))
        g.add(txt("one close, every goroutine wakes", size=15, color=T.TEXT2).move_to(P(3.6, -2.55)))
        return g


class C14Why(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "The problem: work that outlives its purpose"
    SUB = "A request spawns goroutines. If the client leaves or a deadline passes, nothing in Go stops them unless you pass a signal down."

    def build(self):
        w = 6.6
        x0 = X0 + 1.45
        x1 = X0 + w
        unit = (x1 - x0) / 5

        def lanes(y, title, stop_at, col):
            self.add(txt(f"**{title}**", size=15, color=col).move_to(P(X0, y + 0.5), aligned_edge=LEFT))
            rows = [("client", T.BLUE, [(0, 1, "waiting", T.BLUE)]),
                    ("handler", T.GO, [(0, 1, "", T.GO)]),
                    ("DB query", T.GO, [(0.1, stop_at, "", T.GO)]),
                    ("API call", T.GO, [(0.15, stop_at + 0.3 if stop_at > 2 else stop_at, "", T.GO)])]
            for i, (lab, c, segs) in enumerate(rows):
                yy = y - 0.15 - i * 0.37
                self.add(txt(lab, size=12, color=T.TEXT2).move_to(P(x0 - 0.12, yy), aligned_edge=RIGHT))
                for a, b, sl, sc in segs:
                    if b > 1 and i >= 2:
                        self.add(seg(x0 + a * unit, x0 + 1 * unit, yy, sc, h=0.28, size=11))
                        self.add(seg(x0 + 1 * unit, x0 + b * unit, yy, T.RED, h=0.28, lab="wasted", size=11, outline=True))
                    else:
                        self.add(seg(x0 + a * unit, x0 + min(b, 1) * unit, yy, sc, h=0.28, lab=sl, size=11))
            xl = x0 + unit
            self.add(Line(P(xl, y + 0.1), P(xl, y - 1.4)).set_stroke(T.YELLOW, 1.8))
            self.add(txt("client disconnects", size=11, color=T.YELLOW).move_to(P(xl + 0.08, y + 0.2), aligned_edge=LEFT))
            return y - 1.6

        y = lanes(Y0 - 0.62, "Without a context: goroutines keep running", 4.3, T.RED)
        y = lanes(y - 0.45, "With a context: one cancel stops them all", 1.0, T.GREEN)
        self.add(time_axis(x0, x1, y + 0.05, lab="time"))
        k = callout("key", "Go has **no way to kill a goroutine** from outside. Stopping is cooperative: you pass a "
                    "signal down, each goroutine checks it and returns. `context` is that signal.",
                    width=w, size=13)
        self.at(k, X0, y - 0.45)
        x = X0 + w + 0.45
        ww = X1 - x
        iface = code('''type Context interface {
    Deadline() (deadline time.Time, ok bool)
    Done() <-chan struct{}
    Err() error
    Value(key any) any
}''', size=14, title="context.Context (package context)", width=ww, numbers=False, hl=[3])
        self.at(iface, x, Y0)
        rows = [["method", "answers"],
                ["`Done()`", "a channel that is **closed** when the work should stop"],
                ["`Err()`", "nil, then `Canceled` or `DeadlineExceeded`"],
                ["`Deadline()`", "when it will be cancelled automatically, if ever"],
                ["`Value(key)`", "request-scoped data: request ID, user, trace span"]]
        tbl = table(rows, widths=[1.6, ww - 1.6], size=13)
        self.at(tbl, x, iface.get_bottom()[1] - 0.25)
        v = callout("version", "Added to the standard library in Go 1.7 (2016), from golang.org/x/net/context. "
                    "Now it is the first parameter of almost every blocking API.", width=ww, size=13, inline=False)
        self.at(v, x, tbl.get_bottom()[1] - 0.2)


class C14Timeout(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "WithTimeout: a time budget for everything below"
    SUB = "A deadline is a budget for the whole operation, not for one call. Every function that receives the context shares what is left."

    def build(self):
        w = 6.4
        cd = code_ex("ch14_timeout", lines=(9, 30), size=13, width=w, hl=[11, 14, 15, 20, 21],
                     marks={14: "1", 20: "2", 21: "3"})
        self.at(cd, X0, Y0)
        tm = terminal(out("ch14_timeout"), title="go run .", width=w, size=13)
        self.at(tm, X0, cd.get_bottom()[1] - 0.15)
        x = X0 + w + 0.45
        ww = X1 - x
        x0 = x + 1.2
        unit = (X1 - x0) / 560
        y = Y0 - 0.45
        self.add(txt("**timeline (ms)**", size=14, color=T.TEXT).move_to(P(x, Y0), aligned_edge=UL))
        self.add(txt("fast", size=12, color=T.TEXT2).move_to(P(x0 - 0.12, y), aligned_edge=RIGHT))
        self.add(seg(x0, x0 + 30 * unit, y, T.GREEN, h=0.32))
        self.add(txt("\"rows\" at 30", size=11, color=T.GREEN).move_to(P(x0 + 30 * unit + 0.1, y), aligned_edge=LEFT))
        y2 = y - 0.5
        self.add(txt("slow", size=12, color=T.TEXT2).move_to(P(x0 - 0.12, y2), aligned_edge=RIGHT))
        self.add(seg(x0 + 30 * unit, x0 + 100 * unit, y2, T.AMBER, h=0.32))
        self.add(seg(x0 + 100 * unit, x0 + 530 * unit, y2, T.GREY, h=0.32, lab="would have run until 530 ms", size=11, outline=True, text_color=T.TEXT2))
        xd = x0 + 100 * unit
        self.add(Line(P(xd, y + 0.35), P(xd, y2 - 0.35)).set_stroke(T.RED, 2.5))
        self.add(txt("deadline 100 ms:\nDone() closes", size=11, color=T.RED, weight="BOLD").move_to(P(xd + 0.08, y2 - 0.6), aligned_edge=LEFT))
        self.add(time_axis(x0, X1, y2 - 1.05, ticks=[(x0, "0"), (xd, "100"), (x0 + 530 * unit, "530")], lab=""))
        steps = num_steps([("select", "on the work and on `ctx.Done()`: whichever happens first wins."),
                           ("WithTimeout", "= WithDeadline(now + d). It starts a timer that cancels the context."),
                           ("defer cancel()", "releases the timer and the parent's reference **now**, not at the "
                            "deadline. Always call it, even on success.")],
                          width=ww, color=T.GO, size=13, gap=0.1)
        self.at(steps, x, y2 - 1.75)
        vt = terminal(out("ch14_lostcancel"), title="go vet catches a discarded cancel (lostcancel)", width=ww, size=12)
        self.at(vt, x, steps.get_bottom()[1] - 0.2)


class C14Tree(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "The context tree: cancellation flows down"
    SUB = "Every derived context is a child of its parent. Cancelling a node cancels its whole subtree, and nothing above it."

    def build(self):
        w = 6.4
        cd = code_ex("ch14_tree", lines=(10, 35), size=12, width=w, hl=[17, 18, 19, 20, 31, 34], marks={31: "1", 34: "2"})
        self.at(cd, X0, Y0)
        tm = terminal(out("ch14_tree"), title="go run .", width=w, size=12)
        self.at(tm, X0, cd.get_bottom()[1] - 0.12)
        x = X0 + w + 0.45
        ww = X1 - x
        cx = x + ww / 2
        bg = _ctxnode("Background", color=T.GREY, w=1.9).move_to(P(cx, Y0 - 0.3))
        root = _ctxnode("root", color=T.GO, w=1.6).move_to(P(cx, Y0 - 1.2))
        a = _ctxnode("a", color=T.GO, w=1.3).move_to(P(cx - 1.5, Y0 - 2.15))
        b = _ctxnode("b", color=T.GO, w=1.3).move_to(P(cx + 1.5, Y0 - 2.15))
        a1 = _ctxnode("a1", color=T.GO, w=1.3).move_to(P(cx - 1.5, Y0 - 3.1))
        for p_, c_ in ((bg, root), (root, a), (root, b), (a, a1)):
            self.add(arrow(p_.get_bottom(), c_.get_top(), T.MUTED, 2, 0.04))
        self.add(bg, root, a, b, a1)
        for n_, lab, col in ((a, "1", T.RED), (a1, "1", T.RED), (root, "2", T.AMBER), (b, "2", T.AMBER)):
            n_.box.set_stroke(col, 2.5)
            self.add(badge(lab, col, r=0.15, size=12).move_to(n_.get_corner(UR) + P(0.0, 0.0)))
        self.add(txt("(1) cancelA(): a and a1", size=13, color=T.RED, weight="BOLD").move_to(P(cx + 0.4, Y0 - 2.95), aligned_edge=LEFT))
        self.add(txt("(2) cancelRoot(): root and b", size=13, color=T.AMBER, weight="BOLD").move_to(P(cx + 0.4, Y0 - 3.3), aligned_edge=LEFT))
        rules = bullets(["Cancel flows **down** only: cancelling a never touches root or b.",
                         "A child's deadline can only be **earlier**. Asking for a later one than the parent's just "
                         "returns a plain `WithCancel` child (context.go).",
                         "Each `With...` call returns a new node; the parent is never modified."],
                        width=ww, size=13, marker="arrow", marker_color=T.YELLOW, gap=0.08)
        self.at(rules, x, Y0 - 3.7)


class C14Inside(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Inside package context: three small structs"
    SUB = "A context is a linked list of nodes pointing at their parents. Cancellation is a mutex, a closed channel and a set of children."

    def build(self):
        w = 6.4
        cd = code('''type cancelCtx struct {
    Context                  // the parent
    mu       sync.Mutex
    done     atomic.Value    // chan struct{}, made lazily
    children map[canceler]struct{}
    err      atomic.Value    // set by the first cancel
    cause    error
}

type timerCtx struct {
    cancelCtx
    timer    *time.Timer     // fires cancel(DeadlineExceeded)
    deadline time.Time
}

type valueCtx struct {
    Context                  // the parent
    key, val any
}''', size=13, title="context/context.go (abridged)", width=w, hl=[4, 5, 12])
        self.at(cd, X0, Y0)
        x = X0 + w + 0.45
        ww = X1 - x
        self.at(section("cancel(err, cause), once", T.RED, size=16), x, Y0)
        st = num_steps([("Lock", "`mu`; if `err` is already set, return: cancel is idempotent."),
                        ("Record", "`err` and `cause`."),
                        ("Close", "`done` (or store a shared, already-closed channel if nobody asked for Done yet)."),
                        ("Recurse", "into every child, then drop the children map."),
                        ("Detach", "from the parent's children map.")],
                       width=ww, color=T.RED, size=13, gap=0.05)
        self.at(st, x, Y0 - 0.45)
        self.at(section("How a child links to its parent", T.VIOLET, size=16), x, st.get_bottom()[1] - 0.25)
        paths = table([["parent is…", "the child…"],
                       ["never cancelled (`Background`)", "links nothing"],
                       ["a `cancelCtx` (the usual case)", "joins its `children` map"],
                       ["a custom type with `AfterFunc`", "registers a callback"],
                       ["any other custom Context", "costs a goroutine that waits on both"]],
                      widths=[3.1, ww - 3.1], size=12)
        self.at(paths, x, st.get_bottom()[1] - 0.65)
        k = callout("key", "`Done()` is just a channel that gets **closed**: the close broadcast from 8.5. That is why one "
                    "cancel wakes any number of goroutines, and why selecting on it is cheap.",
                    width=ww, size=13)
        self.at(k, x, paths.get_bottom()[1] - 0.2)


class C14Listen(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Making code cancellable: three shapes"
    SUB = "A context only asks. Your code has to look: in loops, in every blocking channel operation, and by passing ctx to library calls."

    def build(self):
        w = 6.4
        a = code_ex("ch14_loop", lines=(10, 21), size=13, width=w, hl=[13, 14, 15], marks={14: "1"})
        self.at(a, X0, Y0)
        b = code_ex("ch14_loop", lines=(24, 34), size=13, width=w, hl=[28, 30, 31], marks={30: "2"})
        self.at(b, X0, a.get_bottom()[1] - 0.15)
        x = X0 + w + 0.45
        ww = X1 - x
        tm = terminal(out("ch14_loop"), title="go run .", width=ww, size=12)
        self.at(tm, x, Y0)
        rows = [["code that…", "becomes cancellable by…"],
                ["① computes in a loop", "checking `ctx.Err()` every N steps (cheap: one atomic load)"],
                ["② blocks on a channel", "a `select` with `case <-ctx.Done():`"],
                ["③ calls a library", "passing ctx: `http.NewRequestWithContext`, `db.QueryContext`, "
                 "`exec.CommandContext`, `(*net.Dialer).DialContext`"],
                ["sleeps", "`select` on a timer and `ctx.Done()`, not `time.Sleep`"]]
        tbl = table(rows, widths=[2.1, ww - 2.1], size=12)
        self.at(tbl, x, tm.get_bottom()[1] - 0.25)
        k = callout("tip", "Return `ctx.Err()` (or wrap it with `%w`) so callers can test `errors.Is(err, "
                    "context.DeadlineExceeded)`.", width=ww, size=13)
        self.at(k, x, tbl.get_bottom()[1] - 0.2)


class C14Cause(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Saying why: WithCancelCause and Cause"
    SUB = "Err tells you that a context ended and how. Since Go 1.20 a cause can tell you why, without changing what Err returns."

    def build(self):
        w = 6.4
        cd = code_ex("ch14_cause", lines=(10, 24), size=13, width=w, hl=[13, 14, 16, 18, 19, 23])
        self.at(cd, X0, Y0)
        tm = terminal(out("ch14_cause"), title="go run .", width=w, size=13)
        self.at(tm, X0, cd.get_bottom()[1] - 0.15)
        x = X0 + w + 0.45
        ww = X1 - x
        bw = (ww - 0.3) / 2
        e = card("ctx.Err()", "**What** happened: only `Canceled` or `DeadlineExceeded`. A fixed set, safe for "
                 "control flow and `errors.Is`.", w=bw, color=T.GO, size=13)
        c = card("context.Cause(ctx)", "**Why**: the error you passed to cancel. Made for logs, metrics and error "
                 "messages. Without a cause it equals `Err()`.", w=bw, color=T.YELLOW, size=13)
        self.at(e, x, Y0)
        self.at(c, x + bw + 0.3, Y0)
        y = min(e.get_bottom()[1], c.get_bottom()[1]) - 0.3
        tbl = table([["plain (Go 1.7)", "with a cause"],
                     ["`WithCancel`", "`WithCancelCause` (1.20)"],
                     ["`WithDeadline`", "`WithDeadlineCause` (1.21)"],
                     ["`WithTimeout`", "`WithTimeoutCause` (1.21)"]],
                    widths=[ww / 2, ww / 2], size=13)
        self.at(tbl, x, y)
        k = callout("key", "The cause travels down the tree with the cancellation: every descendant reports the "
                    "same `Cause`. The **first** cancellation wins; later calls change nothing.",
                    width=ww, size=13)
        self.at(k, x, tbl.get_bottom()[1] - 0.2)


class C14AfterFunc(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "AfterFunc and WithoutCancel (Go 1.21)"
    SUB = "Two tools for the edges of a request: run cleanup when a context ends, and keep working after it ends."

    def build(self):
        w = (CW - 0.4) / 2
        a = code_ex("ch14_afterfunc", lines=(10, 26), size=13, width=w, hl=[13, 14, 15, 24], marks={13: "1", 24: "2"})
        self.at(a, X0, Y0)
        ta = terminal(out("ch14_afterfunc"), title="go run .", width=w, size=13)
        self.at(ta, X0, a.get_bottom()[1] - 0.12)
        na = bullets(["`AfterFunc(ctx, f)` runs f **in its own goroutine** once ctx is done.",
                      "`stop()` unregisters f; it returns true if f had not started."],
                     width=w, size=13, marker="num", marker_color=T.YELLOW, gap=0.06)
        self.at(na, X0, ta.get_bottom()[1] - 0.18)
        x = X0 + w + 0.4
        b = code_ex("ch14_withoutcancel", lines=(11, 26), size=13, width=w, hl=[14, 15])
        self.at(b, x, Y0)
        tb = terminal(out("ch14_withoutcancel"), title="go run .", width=w, size=13)
        self.at(tb, x, b.get_bottom()[1] - 0.12)
        nb = bullets(["`WithoutCancel(ctx)` keeps the **values** but drops cancellation and deadline.",
                      "Use it for work that must outlive the request: audit logs, async cleanup."],
                     width=w, size=13, marker="arrow", marker_color=T.GREEN, gap=0.06)
        self.at(nb, x, tb.get_bottom()[1] - 0.18)


class C14Values(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Context values: request-scoped data only"
    SUB = "WithValue adds one key/value node to the chain. Value(key) walks up the chain until it finds the key."

    def build(self):
        w = 6.4
        cd = code_ex("ch14_value", lines=(8, 33), size=13, width=w, hl=[9, 11, 14, 18], marks={9: "1", 18: "2"})
        self.at(cd, X0, Y0)
        x = X0 + w + 0.45
        ww = X1 - x
        chain = [("valueCtx", "traceKey = span", T.VIOLET),
                 ("valueCtx", "requestIDKey = 7f3a", T.VIOLET), ("Background", "", T.GREY)]
        prev = None
        y = Y0 - 0.1
        nodes = []
        for i, (lab, sub, col) in enumerate(chain):
            n = _ctxnode(lab, sub or None, color=col, w=2.6, h=0.6 if sub else 0.45, size=12)
            self.at(n, x, y)
            nodes.append(n)
            if prev is not None:
                self.add(arrow(prev.get_bottom(), n.get_top(), T.MUTED, 2, 0.03))
            prev = n
            y = n.get_bottom()[1] - 0.2
        lk = txt("Value(requestIDKey):\nasks each node, child to parent,\nuntil a key matches.\nO(depth) per lookup.",
                 size=12, color=T.YELLOW, weight="BOLD")
        self.at(lk, x + 2.95, Y0 - 0.3)
        for n in nodes[:2]:
            self.add(Dot(n.get_right() + RIGHT * 0.12, radius=0.05, fill_color=T.YELLOW))
        dd = do_dont("ctx = WithValue(ctx, \"db\", pool)\nctx = WithValue(ctx, \"verbose\", true)",
                     "ctx = WithRequestID(ctx, id)\nid, ok := RequestID(ctx)", width=ww, size=12,
                     bad_note="dependencies and optional parameters; string keys collide",
                     good_note="request-scoped data, typed accessors, unexported key type")
        self.at(dd, x, y - 0.1)
        tm = terminal(out("ch14_value"), title="go run .", width=ww, size=12)
        self.at(tm, x, dd.get_bottom()[1] - 0.2)


class C14Rules(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Rules of the road, and where context already lives"
    SUB = "The package documentation states the conventions; the standard library follows them everywhere."

    def build(self):
        w = 6.3
        self.at(section("THE CONVENTIONS (package context docs)", T.GO, size=16), X0, Y0)
        rules = bullets([
            "Pass a Context **explicitly, as the first parameter**, named `ctx`.",
            "Do **not store** Contexts inside a struct type.",
            "Never pass a **nil** Context. If unsure, pass `context.TODO()`.",
            "Use Values only for request-scoped data that crosses processes and APIs.",
            "One Context may be used by many goroutines at once: it is safe.",
            "Always call the `CancelFunc`: `go vet` reports a discarded one.",
            "`Background()` at the top (main, init, tests); `TODO()` as a placeholder.",
        ], width=w, size=14, marker="check", marker_color=T.GREEN, gap=0.1)
        self.at(rules, X0, Y0 - 0.5)
        x = X0 + w + 0.45
        ww = X1 - x
        self.at(section("IN THE STANDARD LIBRARY", T.VIOLET, size=16), x, Y0)
        tbl = table([["package", "what takes or gives a ctx"],
                     ["`net/http`", "`r.Context()`: cancelled when the client disconnects or ServeHTTP returns; "
                                    "`NewRequestWithContext` for clients"],
                     ["`database/sql`", "`QueryContext`, `ExecContext`, `BeginTx`"],
                     ["`os/exec`", "`CommandContext`: kills the process on cancel"],
                     ["`net`", "`Dialer.DialContext`, `Resolver` lookups"],
                     ["`os/signal`", "`NotifyContext` (1.16): cancelled on Ctrl-C"],
                     ["`testing`", "`t.Context()` (1.24): cancelled when the test ends"],
                     ["`x/sync/errgroup`", "`WithContext`: cancelled on the first error (8.4)"]],
                    widths=[1.95, ww - 1.95], size=12)
        self.at(tbl, x, Y0 - 0.5)
        k = callout("key", "Context answers \"should this work continue?\". It does not stop anything by force: a "
                    "goroutine that never checks `ctx.Done()` or `ctx.Err()` runs on.",
                    width=w, size=14)
        self.at(k, X0, rules.get_bottom()[1] - 0.3)


class C14Recap(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Recap and check yourself"
    SUB = "One tree of contexts per request; cancel at the top, listen at every blocking point."

    def build(self):
        self.at(section("REMEMBER", T.GO), X0, Y0)
        rec = bullets([
            "`Done()` is a channel closed on cancel: one close wakes every listener.",
            "`WithTimeout`/`WithDeadline` set a budget for everything below; `defer cancel()` always.",
            "Cancellation flows down the tree; children can only shorten deadlines.",
            "Inside: `cancelCtx` (mutex, lazy done channel, children map), `timerCtx`, `valueCtx`.",
            "Listen in loops (`ctx.Err()`), in selects (`<-ctx.Done()`), and pass ctx to every call.",
            "`Cause` explains why; `AfterFunc` cleans up; `WithoutCancel` outlives the request.",
            "Values: request-scoped only, unexported key types, typed accessors.",
        ], width=6.1, size=15, marker="check", marker_color=T.GREEN, gap=0.12)
        self.at(rec, X0, Y0 - 0.5)
        x = 0.55
        self.at(section("CHECK YOURSELF", T.TEAL), x, Y0)
        qs = [("A parent has a 1 s deadline; you call `WithTimeout(parent, 5*time.Second)`. When does the child expire?",
               "After at most 1 s: a child can never outlive its parent's deadline."),
              ("Your goroutine does `time.Sleep(10 * time.Second)` and the context is cancelled. What happens?",
               "Nothing until the sleep ends. Select on a timer and `ctx.Done()` instead."),
              ("Why is it safe to call a `CancelFunc` twice?",
               "cancel checks `err` under the mutex and returns if it is already set."),
              ("Where should a database handle go: in ctx, or a parameter/field?",
               "A parameter or struct field. Context values are for request-scoped data.")]
        y = Y0 - 0.5
        for i, (q, a_) in enumerate(qs):
            grp = vstack(txt(f"**Q{i + 1}.** {q}", size=15, color=T.TEXT, width=6.0),
                         txt(f"{{teal|**Answer.**}} {a_}", size=14, color=T.TEXT2, width=6.0), buff=0.08)
            self.at(grp, x, y)
            y = grp.get_bottom()[1] - 0.26
