from kit import *

CH, NAME = "8.16", "Concurrency Patterns II: Production"


def _db(h=0.9, w=0.8, color=T.BLUE):
    """A database cylinder."""
    body = Rectangle(width=w, height=h).set_fill(color, 0.18).set_stroke(color, 2)
    top = Ellipse(width=w, height=0.26).set_fill(color, 0.35).set_stroke(color, 2).move_to(body.get_top())
    bot = Arc(start_angle=PI, angle=PI, radius=w / 2).stretch(0.26 / w, 1).set_stroke(color, 2).move_to(body.get_bottom() + DOWN * 0.065)
    return VGroup(body, bot, top)


class C16Opener(Opener):
    NUM, NAME = CH, NAME
    TAGLINE = "Real services face bursts, slow dependencies, failures and restarts. A few more patterns keep a concurrent Go program polite to its neighbours and safe to stop."
    LEARN = ["Limit request rates with a token bucket",
             "Fan messages out to subscribers without one slow reader blocking all",
             "Shut down gracefully on SIGINT and SIGTERM",
             "Retry with exponential backoff and jitter",
             "Collapse duplicate work with singleflight; bound and cancel with errgroup"]
    QUESTION = ("A cache entry expires and 10,000 requests for it arrive in the same millisecond. Your database can "
                "handle 100 queries per second. What protects it?")

    def art(self):
        g = VGroup()
        crowd = VGroup(*[gopher(0.5, mood="run") for _ in range(12)]).arrange_in_grid(3, 4, buff=0.08)
        crowd.move_to(P(1.4, 0.6))
        g.add(crowd, txt("10,000 requests", size=14, color=T.TEXT2).next_to(crowd, DOWN, buff=0.15))
        f = Polygon(P(-0.7, 0.9), P(0.7, 0.9), P(0.15, -0.1), P(0.15, -0.6), P(-0.15, -0.6), P(-0.15, -0.1))
        f.set_fill(T.YELLOW, 0.15).set_stroke(T.YELLOW, 2.5).move_to(P(3.65, 0.6))
        g.add(f, txt("singleflight\n+ rate limit", size=13, color=T.YELLOW, weight="BOLD", align="CENTER").next_to(f, DOWN, buff=0.12))
        for i in range(5):
            g.add(arrow(P(2.6, 1.1 - i * 0.25), P(3.05, 1.0 - i * 0.12), T.MUTED, 1.5, 0.0))
        db = _db(1.1, 1.0).move_to(P(5.6, 0.55))
        g.add(arrow(P(3.85, 0.2), P(5.05, 0.5), T.GREEN, 2.6, 0.02), db)
        g.add(txt("1 query", size=14, color=T.GREEN, weight="BOLD").move_to(P(4.45, 0.75)))
        g.add(txt("database\nstays healthy", size=13, color=T.BLUE, align="CENTER").next_to(db, DOWN, buff=0.15))
        return g


class C16RateLimit(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Rate limiting with a token bucket"
    SUB = "Tokens drip into a bucket at a fixed rate; each request takes one. A full bucket allows a short burst, then the steady rate applies."

    def build(self):
        w = 6.4
        cd = code_ex("ch16_ratelimit", lines=(8, 32), size=13, width=w, hl=[10, 14, 20, 21, 28],
                     marks={10: "1", 14: "2", 20: "3", 28: "4"})
        self.at(cd, X0, Y0)
        ts = nums("ch16_ratelimit", r"at \+\s*(\d+)ms", int)
        tm = txt("**go run .** printed:  " + ",  ".join(f"r{i + 1} at +{t} ms" for i, t in enumerate(ts)),
                 size=13, color=T.GREEN, width=w)
        self.at(tm, X0, cd.get_bottom()[1] - 0.15)
        x = X0 + w + 0.45
        ww = X1 - x
        tick = node("ticker: +1 token / 100 ms", w=2.9, h=0.45, color=T.BLUE, size=12)
        self.at(tick, x, Y0)
        bucket = chan_pipe(2, ("T", "T"), cell=0.5, color=T.GREEN, item_color=T.YELLOW)
        bucket.next_to(tick, RIGHT, buff=0.6)
        self.add(bucket, arrow(tick.get_right(), bucket.get_left(), T.BLUE, 2.2, 0.04))
        self.add(txt("burst: cap 2", size=12, color=T.GREEN).next_to(bucket, DOWN, buff=0.06))
        times = nums("ch16_ratelimit", r"at \+\s*(\d+)ms", int)
        x0 = x + 1.1
        unit = (X1 - x0 - 0.2) / 400
        y = Y0 - 1.35
        self.add(txt("**tokens in**", size=12, color=T.BLUE).move_to(P(x0 - 0.12, y), aligned_edge=RIGHT))
        for t, lab in ((0, "2 (full)"), (100, "+1"), (200, "+1"), (300, "+1"), (400, "+1")):
            self.add(Dot(P(x0 + t * unit, y), radius=0.06, fill_color=T.BLUE))
            self.add(txt(lab, size=10, color=T.BLUE).next_to(P(x0 + t * unit, y), UP, buff=0.06))
        y2 = y - 0.6
        self.add(txt("**requests**", size=12, color=T.GO).move_to(P(x0 - 0.12, y2), aligned_edge=RIGHT))
        for i, t in enumerate(times):
            yy = y2 - (0.22 if i == 1 else 0)
            self.add(Dot(P(x0 + t * unit, yy), radius=0.07, fill_color=T.GO))
            self.add(txt(f"r{i + 1}", size=10, color=T.GO).next_to(P(x0 + t * unit, yy), RIGHT, buff=0.05))
        self.add(time_axis(x0, X1, y2 - 0.55, ticks=[(x0 + t * unit, str(t)) for t in (0, 100, 200, 300)], lab="ms"))
        st = num_steps([("Ticker", "sets the steady rate: 10 requests per second."),
                        ("Bucket", "a buffered channel holding up to 2 tokens: the allowed burst."),
                        ("Refill", "one token per tick; if the bucket is full the token is dropped."),
                        ("Take", "a request waits for a token before it proceeds.")],
                       width=ww, color=T.GREEN, size=12, gap=0.05)
        self.at(st, x, y2 - 1.15)
        k = callout("tip", "In production use `golang.org/x/time/rate`: `rate.NewLimiter(rate.Every(100*time.Millisecond), 2)`, "
                    "then `lim.Wait(ctx)` to block or `lim.Allow()` to reject. Same token bucket, no goroutine, ctx-aware.",
                    width=ww, size=12)
        self.at(k, x, st.get_bottom()[1] - 0.15)


class C16PubSub(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Publish/subscribe: one sender, many receivers"
    SUB = "A channel gives each value to one receiver. To broadcast, give every subscriber its own channel, and decide what to do when one is slow."

    def build(self):
        w = 6.4
        cd = code_ex("ch16_pubsub", lines=(8, 38), size=12, width=w, hl=[14, 25, 26, 27], marks={14: "1", 27: "2"})
        self.at(cd, X0, Y0)
        x = X0 + w + 0.45
        ww = X1 - x
        pub = node("Publish(msg)", w=1.7, h=0.5, color=T.GO, size=13)
        self.at(pub, x, Y0 - 0.9)
        subs = [("sub 1", ("m", "m"), T.GREEN, "keeps up"), ("sub 2", ("m",), T.GREEN, "keeps up"),
                ("sub 3", ("m", "m", "m", "m"), T.RED, "full: message dropped")]
        for i, (lab, items, col, note) in enumerate(subs):
            y = Y0 - 0.25 - i * 0.68
            p = chan_pipe(4, items, cell=0.34, color=col, item_color=T.PINK)
            p.move_to(P(x + 3.05, y))
            self.add(p, arrow(pub.get_right(), p.get_left(), col, 2, 0.05))
            g = gtok(lab, col if col != T.RED else T.GREY, w=0.85, h=0.36, size=11, state="run" if col != T.RED else "wait")
            g.next_to(p, RIGHT, buff=0.15)
            self.add(g, txt(note, size=10, color=col).next_to(p, DOWN, buff=0.03))
        tm = terminal(out("ch16_pubsub"), title="go run .", width=ww, size=12)
        self.at(tm, x, Y0 - 2.25)
        tbl = table([["when a subscriber is slow…", "trade-off"],
                     ["block (plain send)", "nobody loses data; one slow reader stalls all"],
                     ["drop (select + default)", "publisher never waits; slow readers miss events"],
                     ["drop oldest / disconnect", "more code; the fast path stays fast"]],
                    widths=[2.4, ww - 2.4], size=12)
        self.at(tbl, x, tm.get_bottom()[1] - 0.2)


class C16Shutdown(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Graceful shutdown: stop taking work, finish what's in hand"
    SUB = "On SIGINT or SIGTERM a service should stop accepting work, let in-flight work finish within a deadline, release resources and exit 0."

    def build(self):
        w = 6.4
        cd = code_ex("ch16_shutdown", lines=(29, 55), size=13, width=w, hl=[31, 32, 33, 48, 53],
                     marks={31: "1", 48: "2", 53: "4"})
        self.at(cd, X0, Y0)
        x = X0 + w + 0.45
        ww = X1 - x
        tm = terminal(out("ch16_shutdown"), title="go run . (workers: lines 13-27)", width=ww, size=11)
        self.at(tm, x, Y0)
        x0 = x + 1.0
        unit = (X1 - x0 - 0.1) / 200
        y = tm.get_bottom()[1] - 0.45
        lanes = {}
        for wk, j in re.findall(r"worker (\d+) finished job (\d+)", out("ch16_shutdown")):
            k = len(lanes.setdefault(int(wk), []))
            lanes[int(wk)].append((60 * k, 60 * (k + 1), f"job {j}"))
        lanes = dict(sorted(lanes.items()))
        for i, (wk, segs) in enumerate(lanes.items()):
            yy = y - i * 0.45
            self.add(txt(f"**worker {wk}**", size=11, color=T.GO).move_to(P(x0 - 0.1, yy), aligned_edge=RIGHT))
            for a, b, lab in segs:
                self.add(seg(x0 + a * unit, x0 + b * unit - 0.03, yy, T.GO if a < 120 else T.AMBER, h=0.32, lab=lab, size=10))
            self.add(txt("exit", size=10, color=T.GREEN, weight="BOLD").move_to(P(x0 + 186 * unit, yy)))
        xs = x0 + 150 * unit
        self.add(Line(P(xs, y + 0.3), P(xs, y - 0.75)).set_stroke(T.RED, 2.2))
        self.add(txt("SIGINT at 150 ms", size=11, color=T.RED, weight="BOLD").move_to(P(xs, y + 0.42)))
        self.add(time_axis(x0, X1, y - 0.8, ticks=[(x0 + t * unit, str(t)) for t in (0, 60, 120, 180)], lab="ms"))
        st = num_steps([("NotifyContext", "turns SIGINT/SIGTERM into a cancelled ctx."),
                        ("Stop dispatching:", "main's select sees ctx.Done() and stops sending jobs."),
                        ("Finish in-flight jobs", "(amber), then each worker sees ctx.Done() and returns."),
                        ("wg.Wait(),", "then flush, close, exit. HTTP servers: `srv.Shutdown(ctx)` closes listeners "
                         "and waits for active requests. Kubernetes allows 30 s after SIGTERM by default.")],
                       width=ww, color=T.RED, size=12, gap=0.04)
        self.at(st, x, y - 1.4)


class C16Retry(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Retries: exponential backoff with jitter"
    SUB = "Retrying at once, or on a fixed schedule, makes every failed client hit the recovering server at the same moment. Spread them out."

    def build(self):
        w = 6.4
        cd = code_ex("ch16_retry", lines=(21, 46), size=13, width=w, hl=[29, 32, 33, 34, 35], marks={29: "1", 34: "2"})
        self.at(cd, X0, Y0)
        x = X0 + w + 0.45
        ww = X1 - x
        self.at(section("WAIT BEFORE RETRY i: RANDOM IN [0, base·2^i)", T.YELLOW, size=14), x, Y0)
        waits = nums("ch16_retry", r"retry in (\d+)ms", int)
        x0 = x + 1.2
        unit = (X1 - x0 - 0.3) / 800
        for i in range(5):
            yy = Y0 - 0.6 - i * 0.42
            hi = 50 * 2 ** i
            self.add(txt(f"retry {i + 1}", size=12, color=T.TEXT2).move_to(P(x0 - 0.12, yy), aligned_edge=RIGHT))
            self.add(seg(x0, x0 + hi * unit, yy, T.YELLOW, h=0.26, outline=True))
            self.add(txt(f"< {hi} ms", size=10, color=T.YELLOW).next_to(P(x0 + hi * unit, yy), RIGHT, buff=0.06))
            if i < len(waits):
                self.add(Dot(P(x0 + waits[i] * unit, yy), radius=0.08, fill_color=T.GO))
        self.add(txt("● = the wait drawn in this run", size=11, color=T.GO).move_to(P(x0, Y0 - 2.75), aligned_edge=LEFT))
        rules = bullets(["**Exponential**: each failure doubles the window, so load falls off fast.",
                         "**Full jitter**: a random wait inside the window spreads clients apart.",
                         "**Cap** the window and the number of attempts; respect `ctx` while sleeping.",
                         "Retry only **idempotent** operations, and only errors that can heal (timeouts, 503).",
                         "`errors.Join` (Go 1.20) keeps both the last error and the ctx error."],
                        width=ww, size=12, marker="check", marker_color=T.GREEN, gap=0.05)
        self.at(rules, x, Y0 - 3.0)
        n = txt("Full jitter: Marc Brooker, \"Exponential Backoff And Jitter\", AWS Architecture Blog, 2015.",
                size=11, color=T.MUTED, width=ww)
        self.at(n, x, rules.get_bottom()[1] - 0.12)
        tm = terminal(out("ch16_retry"), title="go run .", width=ww, size=12)
        self.at(tm, x, n.get_bottom()[1] - 0.2)


class C16Singleflight(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "singleflight: one call for many identical requests"
    SUB = "When many goroutines ask for the same missing thing at once, let one of them fetch it and hand the result to all the others."

    def build(self):
        w = 6.4
        cd = code_ex("ch16_singleflight", lines=(12, 37), size=13, width=w, hl=[15, 21, 27], marks={27: "1"})
        self.at(cd, X0, Y0)
        tm = terminal(out("ch16_singleflight"), title="go run .", width=w, size=13)
        self.at(tm, X0, cd.get_bottom()[1] - 0.15)
        x = X0 + w + 0.45
        ww = X1 - x
        callers = VGroup(*[gtok(f"G{i}", T.GO if i == 1 else T.GREY, w=0.62, h=0.3, size=10,
                                state="run" if i == 1 else "wait") for i in range(1, 11)]).arrange_in_grid(5, 2, h_buff=0.12, v_buff=0.1)
        self.at(callers, x, Y0 - 0.1)
        do = node('g.Do("42", fn)', w=1.9, h=0.6, color=T.YELLOW, size=13)
        do.move_to(P(x + 2.6, callers.get_center()[1]))
        db = _db(0.8, 0.75).move_to(P(X1 - 0.5, callers.get_center()[1]))
        self.add(do, db)
        for c in callers:
            self.add(Line(c.get_right(), do.get_left()).set_stroke(T.MUTED, 1, 0.5))
        self.add(arrow(do.get_right(), db.get_left(), T.GREEN, 2.6, 0.06))
        self.add(txt("1 call", size=12, color=T.GREEN, weight="BOLD").move_to(P((do.get_right()[0] + db.get_left()[0]) / 2, do.get_center()[1] + 0.2)))
        self.add(txt("G1 runs fn; G2-G10 wait and get the same value and error", size=12, color=T.TEXT2, width=ww)
                 .move_to(P(x, callers.get_bottom()[1] - 0.2), aligned_edge=UL))
        tbl = table([["method", "what it does"],
                     ["`Do(key, fn)`", "run fn once per key at a time; return `(v, err, shared)`"],
                     ["`DoChan(key, fn)`", "the same, as a channel: select it against `ctx.Done()`"],
                     ["`Forget(key)`", "the next call runs fn again even if one is in flight"]],
                    widths=[1.9, ww - 1.9], size=12)
        self.at(tbl, x, callers.get_bottom()[1] - 0.7)
        k = callout("key", "Classic use: a **cache stampede**. The entry expires, thousands of requests miss at "
                    "once, and singleflight turns them into one database query. It lives in `golang.org/x/sync`.",
                    width=ww, size=12)
        self.at(k, x, tbl.get_bottom()[1] - 0.2)


class C16Errgroup(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "errgroup with a limit: bounded, cancellable fan-out"
    SUB = "SetLimit caps how many goroutines run; WithContext cancels the rest at the first error; Wait returns that error."

    def build(self):
        w = 6.4
        cd = code_ex("ch16_errgroup", lines=(12, 37), size=13, width=w, hl=[15, 16, 25, 26, 29, 36], marks={29: "1", 36: "2"})
        self.at(cd, X0, Y0)
        x = X0 + w + 0.45
        ww = X1 - x
        tm = terminal(out("ch16_errgroup"), title="go run .", width=ww, size=12)
        self.at(tm, x, Y0)
        # simulate the schedule: limit 3, page p takes 20p ms, page 4 fails
        slots, t_err, events = [0, 0, 0], None, []
        for p in range(1, 9):
            i = min(range(3), key=lambda k: slots[k])
            start = slots[i]
            end = start + 20 * p
            if t_err is not None and start >= t_err:
                end, kind = start, "cancel"
            elif t_err is not None and end > t_err:
                end, kind = t_err, "cancel"
            else:
                kind = "err" if p == 4 else "ok"
                if p == 4:
                    t_err = end
                    for e in events:
                        if e[3] > t_err:
                            e[3], e[4] = t_err, "cancel"
            slots[i] = end
            events.append([p, i, start, end, kind])
        x0 = x + 0.75
        unit = (X1 - x0 - 0.1) / 110
        y = tm.get_bottom()[1] - 0.45
        cols = {"ok": T.GREEN, "err": T.RED, "cancel": T.GREY}
        for s in range(3):
            self.add(txt(f"slot {s + 1}", size=11, color=T.TEXT2).move_to(P(x0 - 0.08, y - s * 0.42), aligned_edge=RIGHT))
        for p, i, a, b, kind in events:
            yy = y - i * 0.42
            if b - a < 3:
                self.add(cross_mark(T.GREY, 0.09).move_to(P(x0 + a * unit + 0.12 + (p - 7) * 0.22, yy)))
                continue
            self.add(seg(x0 + a * unit, x0 + b * unit - 0.03, yy, cols[kind], h=0.32, lab=f"p{p}", size=10,
                         outline=(kind == "cancel"), text_color=T.TEXT2 if kind == "cancel" else None))
        xe = x0 + t_err * unit
        self.add(Line(P(xe, y + 0.25), P(xe, y - 1.1)).set_stroke(T.RED, 2))
        self.add(txt("page 4 fails: ctx cancelled", size=10, color=T.RED, weight="BOLD").move_to(P(xe - 0.05, y - 1.25), aligned_edge=RIGHT))
        self.add(time_axis(x0, X1, y - 1.45, ticks=[(x0 + t * unit, str(t)) for t in (0, 20, 40, 60, 80, 100)], lab="ms"))
        st = bullets([(badge("1", T.YELLOW, r=0.12, size=11), "`g.Go` blocks while 3 are running: the loop itself is throttled"),
                      (badge("2", T.YELLOW, r=0.12, size=11), "`Wait` returns the **first** error; later ones are discarded"),
                      "Pages 5-8 return `context.Canceled` right away instead of doing work nobody will use."],
                     width=ww, size=12, gap=0.05, marker_color=T.GREY)
        self.at(st, x, y - 2.0)


class C16Recap(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Recap and check yourself"
    SUB = "Be polite to dependencies, be ready to stop, and never do the same expensive work twice at once."

    def build(self):
        self.at(section("REMEMBER", T.GO), X0, Y0)
        rec = bullets([
            "Token bucket = ticker (rate) + buffered channel (burst). In production: `x/time/rate`.",
            "Pub/sub: one channel per subscriber, and an explicit policy for slow ones.",
            "Graceful shutdown: `signal.NotifyContext`, stop intake, drain, `wg.Wait`, exit.",
            "Retries: exponential backoff, full jitter, a cap, ctx-aware sleeps, idempotent ops only.",
            "`singleflight` collapses identical concurrent calls into one.",
            "`errgroup` + `SetLimit` + `WithContext`: bounded fan-out that stops at the first error.",
        ], width=6.1, size=15, marker="check", marker_color=T.GREEN, gap=0.12)
        self.at(rec, X0, Y0 - 0.5)
        x = 0.55
        self.at(section("CHECK YOURSELF", T.TEAL), x, Y0)
        qs = [("Why add random jitter to exponential backoff?",
               "Without it, clients that failed together retry together, and overload the server again."),
              ("A publisher uses a plain send to each subscriber. What can one stuck subscriber do?",
               "Block the publisher, and with it every other subscriber."),
              ("Is singleflight a cache?",
               "No. It only merges calls that overlap in time; once fn returns, the next call runs fn again."),
              ("What does `g.Go` do when `SetLimit(3)` and 3 tasks are running?",
               "It blocks the caller until one finishes. `TryGo` returns false instead.")]
        y = Y0 - 0.5
        for i, (q, a_) in enumerate(qs):
            grp = vstack(txt(f"**Q{i + 1}.** {q}", size=15, color=T.TEXT, width=6.0),
                         txt(f"{{teal|**Answer.**}} {a_}", size=14, color=T.TEXT2, width=6.0), buff=0.08)
            self.at(grp, x, y)
            y = grp.get_bottom()[1] - 0.26
