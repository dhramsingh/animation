from kit import *

CH, NAME = "8.19", "Capstone: a Concurrent Web Crawler"

WEB = {"/": ["/go", "/blog", "/docs"], "/go": ["/go/chan", "/go/select", "/"], "/blog": ["/blog/1", "/blog/2", "/go"],
       "/docs": ["/docs/mem", "/go/chan"], "/go/chan": ["/go/select"], "/go/select": [], "/blog/1": ["/blog/2"],
       "/blog/2": ["/missing"], "/docs/mem": ["/"]}
DEPTH = {"/": 0, "/go": 1, "/blog": 1, "/docs": 1, "/go/chan": 2, "/go/select": 2, "/blog/1": 2, "/blog/2": 2,
         "/docs/mem": 2, "/missing": 3}
DCOL = [T.GO, T.VIOLET, T.AMBER, T.RED]


def _arch(x, y, w):
    """Coordinator, task channel, worker pool, results channel: the crawler's architecture."""
    g = VGroup()
    coord = node("coordinator\nowns seen + queue", w=2.3, h=0.95, color=T.YELLOW, size=13)
    coord.move_to(P(x + 1.15, y - 1.2))
    pool = VGroup()
    for i in range(4):
        wk = gtok(f"worker {i + 1}", T.GO, w=1.55, h=0.38, size=11)
        wk.move_to(P(x + w - 0.8, y - 0.35 - i * 0.55))
        pool.add(wk)
    tasks = chan_pipe(0, cell=0.4, color=T.GREEN, lab="tasks")
    tasks.move_to(P(x + 3.35, y - 0.55))
    res = chan_pipe(0, cell=0.4, color=T.PINK, lab="results")
    res.move_to(P(x + 3.35, y - 1.9))
    g.add(coord, pool, tasks, res)
    g.add(arrow(coord.get_right() + UP * 0.25, tasks[0].get_left(), T.GREEN, 2.4, 0.05))
    for wk in pool:
        g.add(Line(tasks[0].get_right(), wk.get_left()).set_stroke(T.GREEN, 1.4, 0.7))
        g.add(Line(wk.get_left(), res[0].get_right()).set_stroke(T.PINK, 1.4, 0.7))
    g.add(arrow(res[0].get_left(), coord.get_right() + DOWN * 0.25, T.PINK, 2.4, 0.05))
    tick = node("ticker 5 ms", w=1.5, h=0.38, color=T.BLUE, size=11).move_to(P(x + w - 0.8, y - 2.65))
    ctxn = node("ctx (deadline)", w=1.75, h=0.38, color=T.RED, size=11).move_to(P(x + 1.15, y - 2.65))
    g.add(tick, ctxn, arrow(tick.get_top(), pool[-1].get_bottom(), T.BLUE, 1.8, 0.04))
    g.add(arrow(ctxn.get_top(), coord.get_bottom(), T.RED, 1.8, 0.04))
    return g


class C19Opener(Opener):
    NUM, NAME = CH, NAME
    TAGLINE = "One program that uses the whole module: a worker pool, channels as the only shared state, a select with a nil channel, a rate limit, a deadline, a clean shutdown, a race-free test with a fake clock."
    LEARN = ["Split a problem into an owner goroutine and a worker pool",
             "Coordinate with a select whose cases switch on and off",
             "Add a rate limit and a deadline without new locks",
             "Shut down without leaks, and prove it in a test",
             "Review concurrent code with a checklist"]
    QUESTION = ("Fetch every page of a site in parallel, never the same page twice, at most 200 fetches per "
                "second, and stop at a deadline. Which goroutine owns which data?")

    def art(self):
        g = VGroup()
        pos = {"/": (3.6, 2.0), "/go": (2.0, 0.85), "/blog": (3.6, 0.85), "/docs": (5.2, 0.85),
               "/go/chan": (1.3, -0.35), "/go/select": (2.6, -0.35), "/blog/1": (3.6, -0.35), "/blog/2": (4.6, -0.35),
               "/docs/mem": (5.8, -0.35), "/missing": (4.6, -1.5)}
        for a, ls in WEB.items():
            for b in ls:
                if b in pos:
                    g.add(Line(P(*pos[a]), P(*pos[b])).set_stroke(T.STROKE2, 1.5, 0.8))
        for k, (px, py) in pos.items():
            d = DEPTH[k]
            n = node(k, w=1.05 if len(k) < 8 else 1.2, h=0.4, color=DCOL[d], size=11, fill_opacity=0.25)
            g.add(n.move_to(P(px, py)))
        for i, (px, py) in enumerate(((1.0, 1.55), (6.2, 1.6), (6.4, -1.2))):
            g.add(gopher(0.6, mood="run").move_to(P(px, py)))
        g.add(txt("10 pages · 4 workers · 1 coordinator", size=14, color=T.TEXT2).move_to(P(3.6, -2.4)))
        return g


class C19Design(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "The design: one owner, many workers"
    SUB = "Shared state (seen pages, the queue) lives in exactly one goroutine. Workers own nothing; they get a URL and send back a page."

    def build(self):
        w = 6.6
        self.add(_arch(X0, Y0, w))
        x = X0 + w + 0.45
        ww = X1 - x
        tbl = table([["thing", "owner", "how others reach it"],
                     ["`seen` map, `queue`", "coordinator", "nobody else: no lock needed"],
                     ["`tasks` channel", "coordinator (sends, closes)", "workers range over it"],
                     ["`results` channel", "workers (send)", "coordinator receives"],
                     ["`inflight` count", "coordinator", "\"how many tasks are out?\""],
                     ["rate limit", "the ticker", "each worker takes a tick before fetching"],
                     ["deadline", "`ctx`", "fetch and the coordinator select on Done"]],
                    widths=[1.95, 1.9, ww - 3.85], size=12)
        self.at(tbl, x, Y0)
        k = callout("key", "\"Share memory by communicating\" in practice: the map that would need a mutex is touched by "
                    "one goroutine only, and every other goroutine talks to it through channels.",
                    width=ww, size=13)
        self.at(k, x, tbl.get_bottom()[1] - 0.2)
        n = bullets(["`tasks` and `results` are unbuffered: every hand-off is a synchronisation point.",
                     "The coordinator never blocks on one channel only; it always selects (next pages)."],
                    width=w, size=13, marker="arrow", marker_color=T.YELLOW, gap=0.08)
        self.at(n, X0, Y0 - 3.35)


class C19Fetch(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "The fake web and the fetcher"
    SUB = "To keep the example self-contained, the \"web\" is a map and every fetch takes 20 ms. The crawler cannot tell the difference."

    def build(self):
        w = 6.4
        a = code_ex("ch19_crawler", file="crawl.go", lines=(10, 21), size=13, width=w)
        self.at(a, X0, Y0)
        b = code_ex("ch19_crawler", file="crawl.go", lines=(35, 46), size=13, width=w, hl=[36, 37, 38, 39], marks={38: "1"})
        self.at(b, X0, a.get_bottom()[1] - 0.15)
        x = X0 + w + 0.45
        ww = X1 - x
        cols = {0: [], 1: [], 2: [], 3: []}
        for k, d in DEPTH.items():
            cols[d].append(k)
        pos = {}
        for d, ks in cols.items():
            for i, k in enumerate(ks):
                pos[k] = (x + 0.75 + d * 1.6, Y0 - 0.35 - i * 0.62 - (0.9 if d in (0, 3) else 0))
        for s_, ls in WEB.items():
            for t_ in ls:
                pa, pb = P(*pos[s_]), P(*pos[t_])
                back = DEPTH[t_] <= DEPTH[s_]
                if back:
                    self.add(dashed(pa, pb, T.MUTED, 1.0, 0.05, opacity=0.6))
                else:
                    self.add(Line(pa, pb).set_stroke(DCOL[DEPTH[t_]], 1.6, 0.8))
        for k, (px, py) in pos.items():
            self.add(node(k, w=1.25, h=0.4, color=DCOL[DEPTH[k]], size=11, fill_opacity=0.25).move_to(P(px, py)))
        for d in range(4):
            self.add(txt(f"depth {d}", size=12, color=DCOL[d], weight="BOLD").move_to(P(x + 0.75 + d * 1.6, Y0 + 0.02)))
        self.add(txt("dashed = link to a page at the same or a lower depth (already seen)", size=11, color=T.MUTED)
                 .move_to(P(x, Y0 - 3.65), aligned_edge=LEFT))
        k = callout("note", "① `fetch` honours `ctx` like any real HTTP call would (`http.NewRequestWithContext`). "
                    "`/missing` is linked but absent: a 404 to show error handling.", width=ww, size=12)
        self.at(k, x, Y0 - 3.95)


class C19Workers(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "The worker pool: rate-limited, cancellable"
    SUB = "Four workers range over tasks. Before each fetch a worker takes a tick from the shared ticker, so the whole pool makes at most 200 fetches a second."

    def build(self):
        w = 6.4
        cd = code_ex("ch19_crawler", file="crawl.go", lines=(48, 67), size=13, width=w, hl=[52, 58, 60, 61, 63, 64],
                     marks={52: "1", 58: "2", 60: "3", 64: "4"})
        self.at(cd, X0, Y0)
        x = X0 + w + 0.45
        ww = X1 - x
        st = num_steps([("One ticker for the pool:", "a tick every 5 ms is a global rate of 200/s, however many workers."),
                        ("range over tasks:", "the worker exits when the coordinator closes `tasks`."),
                        ("Take a tick or give up:", "if ctx is done, skip waiting; fetch will fail fast anyway."),
                        ("Always send a result,", "even an error: the coordinator counts every task it handed out.")],
                       width=ww, color=T.GO, size=13, gap=0.12)
        self.at(st, x, Y0)
        k = callout("warn", "Why must a worker report a failed fetch? The coordinator's `inflight` counter only goes "
                    "down on a result. A worker that silently dropped a task would make the coordinator wait forever.",
                    width=ww, size=13, title="EVERY TASK GETS AN ANSWER")
        self.at(k, x, st.get_bottom()[1] - 0.25)
        n = txt("A shared `time.Ticker` channel is safe for many receivers: each tick goes to exactly one worker, "
                "and ticks nobody takes are dropped.", size=13, color=T.TEXT2, width=w)
        self.at(n, X0, cd.get_bottom()[1] - 0.2)


class C19Coordinator(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "The coordinator: a select that switches cases on and off"
    SUB = "One loop, three cases. A nil channel disables a case (8.8), so the same select can stop sending when there is nothing to send, or after a cancel."

    def build(self):
        w = 6.6
        cd = code_ex("ch19_crawler", file="crawl.go", lines=(70, 103), size=11, width=w,
                     hl=[74, 75, 78, 81, 84, 91, 96, 97, 100, 101],
                     marks={74: "1", 75: "2", 81: "3", 84: "4", 96: "5", 100: "6"})
        self.at(cd, X0, Y0)
        x = X0 + w + 0.45
        ww = X1 - x
        st = num_steps([("Loop", "while there is work queued **or** tasks are still out."),
                        ("send = nil", "unless the queue has a URL: an empty queue disables the send case."),
                        ("Send a task:", "pop the queue, `inflight++`."),
                        ("Receive a result:", "`inflight--`, record it, queue unseen links one level deeper."),
                        ("Cancelled:", "drop the queue and set `done = nil` so this case never fires again; keep "
                         "receiving until every task in flight has answered."),
                        ("Shut down:", "`close(tasks)` ends the workers' range loops; `wg.Wait()` makes sure they exited.")],
                       width=ww, color=T.YELLOW, size=12, gap=0.08)
        self.at(st, x, Y0)
        k = callout("key", "No goroutine is ever left blocked: workers always have a receiver for their result, and "
                    "the coordinator stops only when `inflight` is zero. That is why the leak test passes.",
                    width=ww, size=12)
        self.at(k, x, st.get_bottom()[1] - 0.2)


class C19Run(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Running it: with a budget, and with a tight deadline"
    SUB = "The same Crawl, two contexts. With 2 s it finishes; with 50 ms the deadline cuts it short, and it still returns cleanly."

    def build(self):
        w = 6.4
        cd = code_ex("ch19_crawler", file="main.go", lines=(9, 29), size=13, width=w, hl=[10, 13])
        self.at(cd, X0, Y0)
        lines = out("ch19_crawler").split("\n")
        ok = [l for l in lines if "=>" in l]
        npages = nums("ch19_crawler", r"=> (\d+) pages", int)
        x = X0 + w + 0.45
        ww = X1 - x
        tm = terminal("\n".join(lines), title="go run .", width=ww, size=11)
        self.at(tm, x, Y0)
        # depth timeline for the 2 s run
        y = cd.get_bottom()[1] - 0.45
        x0 = X0 + 1.1
        unit = (X0 + w - x0) / 110
        self.add(txt("**2 s run: fetch waves (20 ms each)**", size=13, color=T.TEXT).move_to(P(X0, y + 0.05), aligned_edge=LEFT))
        waves = [(0, "/", 0), (25, "3 pages", 1), (50, "5 pages", 2), (80, "/missing", 3)]
        for i, (t0, lab, d) in enumerate(waves):
            yy = y - 0.4 - i * 0.32
            self.add(txt(f"depth {d}", size=11, color=DCOL[d]).move_to(P(x0 - 0.1, yy), aligned_edge=RIGHT))
            self.add(seg(x0 + t0 * unit, x0 + (t0 + 20) * unit, yy, DCOL[d], h=0.28, lab=lab, size=10))
        self.add(time_axis(x0, X0 + w, y - 1.75, ticks=[(x0 + t * unit, str(t)) for t in (0, 25, 50, 75, 100)], lab="ms"))
        self.add(txt(f"{npages[0]} pages at depths 0-3 need 4 sequential waves: about 4 × 20 ms plus rate-limit ticks. "
                     f"With 50 ms only {npages[1]} pages come back, the rest report the deadline.", size=12,
                     color=T.TEXT2, width=ww).move_to(P(x, tm.get_bottom()[1] - 0.2), aligned_edge=UL))


class C19Test(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Proving it: a race-free, leak-free test in fake time"
    SUB = "The crawler's own test runs in a synctest bubble under -race. A leaked worker or coordinator would fail it."

    def build(self):
        w = 6.4
        cd = code_ex("ch19_crawltest", file="crawl_test.go", lines=(10, 31), size=13, width=w, hl=[11, 12, 15, 25, 28])
        self.at(cd, X0, Y0)
        x = X0 + w + 0.45
        ww = X1 - x
        tm = terminal(out("ch19_crawltest"), title="go test -v -race .", width=ww, size=12)
        self.at(tm, x, Y0)
        checks = bullets(["**Fast:** 2 s budgets and 20 ms fetches run in fake time.",
                          "**Race-free:** `-race` watched every access: no report.",
                          "**Leak-free:** the bubble fails the test if any goroutine is left blocked.",
                          "**Deadline-safe:** with 30 ms, Crawl returns at exactly 30 ms of fake time."],
                         width=ww, size=13, marker="check", marker_color=T.GREEN, gap=0.1)
        self.at(checks, x, tm.get_bottom()[1] - 0.25)
        n = callout("note", "Fake time is deterministic, but `select` still picks randomly among ready cases, so the "
                    "total can differ by one 5 ms tick between runs (100 or 105 ms). Assert on outcomes, not on exact "
                    "schedules.", width=ww, size=12)
        self.at(n, x, checks.get_bottom()[1] - 0.2)


class C19Review(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "A review checklist for any concurrent Go code"
    SUB = "Ask these questions of every pull request that starts a goroutine, makes a channel or adds a lock. Here are the crawler's answers."

    def build(self):
        rows = [["question", "the crawler's answer"],
                ["How does every goroutine **end**?", "workers: `tasks` closed; coordinator: queue empty and inflight 0"],
                ["Who **closes** each channel, exactly once?", "coordinator closes `tasks`; `results` is never closed, nobody ranges over it"],
                ["Which goroutine **owns** each piece of shared state?", "coordinator owns `seen`, `queue`, `pages`; no mutex"],
                ["What happens on **cancel** or deadline?", "stop dispatching, drain in-flight results, close, wait"],
                ["What **bounds** concurrency and rate?", "4 workers; one 5 ms ticker = 200 fetches/s"],
                ["Can a send or receive block **forever**?", "no: every task gets a result; the coordinator always receives"],
                ["Do **errors** reach a decision point?", "each Page carries Err; 404s and deadline errors are reported"],
                ["Is it **tested** under `-race`, fast and leak-checked?", "synctest bubble + `-race`, two tests, about 1 s"]]
        tbl = table(rows, widths=[5.3, CW - 5.3], size=14, col_colors=[T.YELLOW, None])
        self.at(tbl, X0, Y0)
        k = callout("key", "Most concurrency bugs are a \"no\" or a \"not sure\" to one of these eight questions. Answer "
                    "them in the design, not in production.", width=CW, size=14, inline=True)
        self.at(k, X0, tbl.get_bottom()[1] - 0.3)


class C19Exercises(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Extend the crawler: exercises"
    SUB = "Each exercise uses a technique from this module. Try them in order; keep every one race-free and leak-free under the synctest test."

    def build(self):
        ex = [("Per-host limits", "Give each host its own ticker or `x/time/rate` limiter, so one slow site does not "
               "starve the others.", "8.16", T.GO),
              ("Retries", "Retry 5xx and timeouts with exponential backoff and full jitter, inside the worker, "
               "honouring ctx.", "8.16", T.AMBER),
              ("errgroup version", "Rewrite the pool with `errgroup.WithContext` and `SetLimit`. What changes about "
               "error handling?", "8.4, 8.16", T.VIOLET),
              ("Streaming results", "Return `<-chan Page` instead of a slice, so callers process pages as they "
               "arrive. Who closes it?", "8.15", T.GREEN),
              ("Real HTTP", "Fetch with `http.NewRequestWithContext`, parse links with `golang.org/x/net/html`, "
               "and test against `httptest.Server`.", "8.14", T.BLUE),
              ("Metrics", "Count fetches, errors and in-flight tasks with `atomic.Int64`, and expose them while it "
               "runs. Is a mutex needed?", "8.12", T.TEAL)]
        cols, gap = 3, 0.22
        w = (CW - gap * 2) / cols
        for i, (t, b, ch, col) in enumerate(ex):
            r, c = divmod(i, cols)
            cd = card(f"{i + 1}. {t}", b + f"\n\n{{muted|see {ch}}}", w=w, color=col, size=14, h=2.3)
            self.at(cd, X0 + c * (w + gap), Y0 - r * 2.5)
        k = callout("try", "Stretch goal: make `Crawl` resumable. Persist `seen` and `queue` when the deadline hits, "
                    "and continue from them in the next run.", width=CW, size=14, inline=True)
        self.at(k, X0, Y0 - 5.15)


class C19Recap(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Recap: the whole module in one program"
    SUB = "Every line of the crawler maps to a chapter. If you can explain each one, you know Go's concurrency model."

    def build(self):
        rows = [["in the crawler", "concept", "chapter"],
                ["`wg.Go(func() { for t := range tasks {…} })`", "goroutines, WaitGroup.Go, range over a channel", "8.3, 8.4, 8.6"],
                ["`tasks`, `results` (unbuffered)", "synchronous hand-off, happens-before", "8.5, 8.13"],
                ["`var send chan task // nil`", "nil channels disable select cases", "8.8"],
                ["`limiter := time.NewTicker(…)`", "timers and tickers, rate limiting", "8.8, 8.16"],
                ["`case <-ctx.Done():`", "cancellation and deadlines", "8.14"],
                ["coordinator owns `seen`", "share memory by communicating", "8.12, 8.15"],
                ["4 workers", "worker pool, the scheduler's Ps", "8.10, 8.15"],
                ["`close(tasks); wg.Wait()`", "clean shutdown, no leaks", "8.16, 8.17"],
                ["`synctest.Test` + `-race`", "testing concurrent code", "8.13, 8.18"]]
        tbl = table(rows, widths=[5.0, 5.7, CW - 10.7], size=14, col_colors=[None, T.TEXT2, T.GO])
        self.at(tbl, X0, Y0)
        q = quote("Concurrency is about dealing with lots of things at once. Parallelism is about doing lots of "
                  "things at once.", "Rob Pike, \"Concurrency is not Parallelism\", 2012", width=CW, size=16)
        self.at(q, X0 + 0.2, tbl.get_bottom()[1] - 0.35)
