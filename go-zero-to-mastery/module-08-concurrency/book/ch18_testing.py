from kit import *

CH, NAME = "8.18", "Testing Concurrent Code"


def _clock(lab, color=T.BLUE, r=0.32, hour=0, minute=0):
    c = clock_icon(color, r=r, hour=hour, minute=minute)
    return VGroup(c, txt(lab, size=12, color=color, font=T.MONO).next_to(c, DOWN, buff=0.06))


class C18Opener(Opener):
    NUM, NAME = CH, NAME
    TAGLINE = "Concurrent code is hard to test because timing changes from run to run. Go gives you a fake clock, a way to wait until goroutines settle, and a race detector that turns silent bugs into failures."
    LEARN = ["See why sleep-based tests are slow and flaky",
             "Test timeouts and expiry instantly with `testing/synctest`",
             "Use `synctest.Wait` to check state at exactly the right moment",
             "Let the bubble catch deadlocks and leaked goroutines",
             "Run `-race`, `-count` and `-cpu` to shake out rare bugs"]
    QUESTION = ("You must test a cache entry that expires after one hour. Do you make the test wait an hour, "
                "sprinkle `time.Sleep`, or is there something better?")

    def art(self):
        g = VGroup()
        bub = Circle(radius=2.0).set_fill(T.TEAL, 0.07).set_stroke(T.TEAL, 3).move_to(P(3.6, 0.3))
        g.add(bub, txt("**synctest bubble**", size=15, color=T.TEAL).next_to(bub, UP, buff=0.1))
        gs = VGroup(gopher(0.75, mood="happy"), gopher(0.75, mood="sleep"), gopher(0.75, mood="sleep")).arrange(RIGHT, buff=0.2)
        gs.move_to(P(3.6, -0.3))
        g.add(gs)
        c1 = _clock("00:00", T.BLUE, hour=12, minute=0).move_to(P(2.75, 1.2))
        c2 = _clock("01:00", T.GREEN, hour=1, minute=0).move_to(P(4.45, 1.2))
        g.add(c1, c2, arrow(c1[0].get_right(), c2[0].get_left(), T.YELLOW, 2.5, 0.08))
        g.add(txt("1 hour of fake time in 0.00 s", size=14, color=T.YELLOW, weight="BOLD").move_to(P(3.6, -2.0)))
        return g


class C18Problem(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Why concurrent tests flake"
    SUB = "A test that sleeps and hopes the background work is done passes on a fast laptop and fails on a busy CI machine."

    def build(self):
        w = 6.4
        x0 = X0 + 1.6
        unit = (X0 + w - x0) / 200
        for i, (lab, work, col) in enumerate((("laptop", 60, T.GREEN), ("busy CI", 130, T.RED))):
            y = Y0 - 0.35 - i * 1.2
            self.add(txt(f"**{lab}**", size=14, color=col).move_to(P(x0 - 0.12, y), aligned_edge=RIGHT))
            self.add(seg(x0, x0 + work * unit, y + 0.2, T.GO, h=0.3, lab=f"background work {work} ms", size=11))
            self.add(seg(x0, x0 + 100 * unit, y - 0.2, T.GREY, h=0.3, lab="test: time.Sleep(100ms)", size=11))
            xc = x0 + 100 * unit
            self.add(Line(P(xc, y + 0.45), P(xc, y - 0.45)).set_stroke(col, 2.4))
            self.add(txt("check: PASS" if col == T.GREEN else "check: FAIL", size=12, color=col, weight="BOLD")
                     .move_to(P(xc + 0.1, y - 0.2), aligned_edge=LEFT))
        self.add(time_axis(x0, X0 + w, Y0 - 2.3, ticks=[(x0 + t * unit, f"{t} ms" if t == 200 else str(t)) for t in (0, 50, 100, 150, 200)], lab=""))
        bad = bullets(["**Slow**: every sleep is real time, multiplied by every test, every run.",
                       "**Flaky**: no sleep is long enough under load, and longer sleeps make it slower.",
                       "**Blind**: you cannot test \"nothing happened yet\" without waiting."],
                      width=w, size=14, marker="cross", marker_color=T.RED, gap=0.1)
        self.at(bad, X0, Y0 - 2.85)
        x = X0 + w + 0.45
        ww = X1 - x
        self.at(section("BETTER, IN ORDER OF PREFERENCE", T.GREEN, size=16), x, Y0)
        good = num_steps([("Synchronize, don't sleep.", "Have the code under test signal completion: a channel, "
                           "a `WaitGroup`, a callback. Then the test waits for exactly that."),
                          ("Fake the clock.", "`testing/synctest` runs the test in a bubble whose `time` package is "
                           "fake: an hour passes instantly and deterministically."),
                          ("Wait for quiescence.", "`synctest.Wait()` returns when every other goroutine in the bubble "
                           "is blocked: the perfect moment to assert."),
                          ("Shake it.", "Run with `-race`, `-count=100` and `-cpu=1,2,4` to expose orderings a single "
                           "run never hits.")],
                         width=ww, color=T.GREEN, size=14, gap=0.14)
        self.at(good, x, Y0 - 0.5)


class C18Synctest(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "testing/synctest: a bubble with a fake clock"
    SUB = "Inside synctest.Test, time starts at midnight UTC on 2000-01-01 and jumps forward whenever every goroutine in the bubble is blocked."

    def build(self):
        w = 6.4
        a = code_ex("ch18_synctest", file="timeout.go", lines=(16, 25), size=13, width=w, hl=[20],
                    title="examples/ch18_synctest/timeout.go (code under test)")
        self.at(a, X0, Y0)
        b = code_ex("ch18_synctest", file="timeout_test.go", lines=(9, 24), size=13, width=w, hl=[10, 14, 18],
                    marks={10: "1", 14: "2", 18: "3"})
        self.at(b, X0, a.get_bottom()[1] - 0.15)
        x = X0 + w + 0.45
        ww = X1 - x
        tm = terminal(out("ch18_synctest"), title="go test -v . (real time: 0.00 s)", width=ww, size=12)
        self.at(tm, x, Y0)
        y = tm.get_bottom()[1] - 0.6
        x0 = x + 0.3
        stops = [("00:00", 0, T.BLUE, "Set(ttl 1h)"), ("00:59", 59, T.GO, "Get: ok"), ("01:00", 60, T.AMBER, "AfterFunc deletes"),
                 ("01:01", 61, T.GREEN, "Get: gone")]
        unit = (X1 - x0 - 0.5) / 61
        self.add(Line(P(x0, y), P(X1 - 0.3, y)).set_stroke(T.STROKE2, 3))
        for lab, t, col, ev in stops:
            px = {0: x0, 59: x0 + (X1 - x0) * 0.42, 60: x0 + (X1 - x0) * 0.62, 61: x0 + (X1 - x0) * 0.85}[t]
            self.add(Dot(P(px, y), radius=0.08, fill_color=col))
            self.add(txt(lab, size=12, color=col, font=T.MONO, weight="BOLD").next_to(P(px, y), UP, buff=0.1))
            self.add(txt(ev, size=11, color=T.TEXT2).next_to(P(px, y), DOWN, buff=0.1))
        self.add(txt("fake clock (each jump is instant)", size=11, color=T.MUTED).move_to(P(x0, y - 0.55), aligned_edge=LEFT))
        st = num_steps([("Test", "creates the bubble; goroutines and timers started inside belong to it."),
                        ("Sleep", "the fake clock jumps 59 min the moment nothing else can run, then waits for the bubble to settle."),
                        ("Past the TTL,", "the AfterFunc timer has fired and finished before `Sleep` returns.")],
                       width=ww, color=T.TEAL, size=12, gap=0.05)
        self.at(st, x, y - 0.85)
        v = callout("version", "Go 1.24: experiment (`synctest.Run`). Go 1.25: `synctest.Test` and `Wait`. "
                    "Go 1.27: `synctest.Sleep` = `time.Sleep` + `Wait`.", width=ww, size=12, inline=True)
        self.at(v, x, st.get_bottom()[1] - 0.15)


class C18Wait(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "synctest.Wait: assert when everything has settled"
    SUB = "Wait returns once every other goroutine in the bubble is durably blocked. Then the test can look at state without races and without guessing."

    def build(self):
        w = 6.4
        cd = code_ex("ch18_wait", file="afterfunc_test.go", lines=(9, 27), size=13, width=w, hl=[15, 21],
                     marks={15: "1", 21: "2"})
        self.at(cd, X0, Y0)
        tm = terminal(out("ch18_wait"), title="go test -v .", width=w, size=12)
        self.at(tm, X0, cd.get_bottom()[1] - 0.15)
        x = X0 + w + 0.45
        ww = X1 - x
        tbl = table([["durably blocking (time can advance)", "NOT durably blocking"],
                     ["send/receive on a channel made in the bubble", "locking a `sync.Mutex` or `RWMutex`"],
                     ["`select` whose cases are all bubble channels", "network or file I/O"],
                     ["`sync.Cond.Wait`", "system calls"],
                     ["`WaitGroup.Wait` (Add called in the bubble)", "channels made outside the bubble"],
                     ["`time.Sleep`", ""]],
                    widths=[ww * 0.55, ww * 0.45], size=12, col_colors=[T.GREEN, T.RED])
        self.at(tbl, x, Y0)
        k = callout("def", "**Durably blocked** = blocked on something only another goroutine **in the same bubble** "
                    "can release. A mutex could be unlocked from outside, so it does not count.",
                    width=ww, size=13)
        self.at(k, x, tbl.get_bottom()[1] - 0.2)
        rules = bullets(["When all are durably blocked: `Wait` returns if called; otherwise time jumps to the next "
                         "timer; otherwise the test fails with a deadlock.",
                         "`t.Context()` inside the bubble is cancelled when the test ends.",
                         "Avoid real network and external processes inside a bubble: use fakes."],
                        width=ww, size=12, marker="arrow", marker_color=T.YELLOW, gap=0.06)
        self.at(rules, x, k.get_bottom()[1] - 0.2)


class C18BubbleLeak(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "The bubble catches leaks and deadlocks"
    SUB = "synctest.Test waits for every goroutine it started. A goroutine stuck forever turns into a test failure with its exact line."

    def build(self):
        w = 6.4
        cd = code_ex("ch18_bubble_leak", file="leak_test.go", lines=(8, 16), size=15, width=w, hl=[(12, T.RED)], marks={12: "!"})
        self.at(cd, X0, Y0)
        k = callout("key", "Without the bubble this test passes and the goroutine leaks silently into the rest of the "
                    "test binary. With it, the leak is a red test pointing at line 12.", width=w, size=14)
        self.at(k, X0, cd.get_bottom()[1] - 0.25)
        steps = num_steps([("The test body returns.", "The root goroutine of the bubble exits."),
                           ("One goroutine is left,", "durably blocked on a bubble channel: nothing can ever release it."),
                           ("Test panics:", "\"deadlock: main bubble goroutine has exited but blocked goroutines remain\".")],
                          width=w, color=T.RED, size=14, gap=0.12)
        self.at(steps, X0, k.get_bottom()[1] - 0.3)
        x = X0 + w + 0.45
        ww = X1 - x
        lines = out("ch18_bubble_leak").split("\n")
        keep = [l for l in lines if l.startswith(("$", "===", "---", "panic:", "goroutine 2", "FAIL")) or "leak_test.go" in l]
        tm = terminal("\n".join(keep), title="go test -v . (abridged)", width=ww, size=12)
        self.at(tm, x, Y0)
        n = txt("The dump even marks the wait as **(durable)** and names the bubble.", size=13, color=T.TEXT2, width=ww)
        self.at(n, x, tm.get_bottom()[1] - 0.2)


class C18Race(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Run tests with -race, many times, on many Ps"
    SUB = "A race detector only sees races that happen. Make them happen: real concurrency in the test, repeated runs, different GOMAXPROCS."

    def build(self):
        w = 6.4
        a = code_ex("ch18_race_test", file="counter.go", lines=(3, 7), size=14, width=w, hl=[(6, T.RED)])
        self.at(a, X0, Y0)
        b = code_ex("ch18_race_test", file="counter_test.go", lines=(8, 20), size=14, width=w, hl=[11])
        self.at(b, X0, a.get_bottom()[1] - 0.15)
        x = X0 + w + 0.45
        ww = X1 - x
        lines = out("ch18_race_test").split("\n")
        keep = lines[:5] + ["  ...  (stacks and a second report)"] + [l for l in lines if "counter_test.go:19" in l or "race detected" in l
                                                                    or l.startswith(("--- FAIL", "FAIL"))]
        tm = terminal("\n".join(keep), title="go test -race -v . (abridged)", width=ww, size=12)
        self.at(tm, x, Y0)
        k = callout("warn", "The count printed **800**, the right answer, and the test still **failed**: with `-race` "
                    "any detected race fails the test. Without `-race` this test is green forever.",
                    width=ww, size=12)
        self.at(k, x, tm.get_bottom()[1] - 0.18)
        tbl = table([["flag", "why"],
                     ["`-race`", "fail on any data race"],
                     ["`-count=100`", "repeat (and skip the test cache)"],
                     ["`-cpu=1,2,4`", "run with different GOMAXPROCS"],
                     ["`-shuffle=on`", "random test order: finds shared state"],
                     ["`-timeout=30s`", "turn a hang into a failure with a dump"]],
                    widths=[1.9, ww - 1.9], size=12)
        self.at(tbl, x, k.get_bottom()[1] - 0.18)
        n = txt("`t.Parallel()` runs tests concurrently with each other; it does not make one test concurrent.",
                size=12, color=T.TEXT2, width=w)
        self.at(n, X0, b.get_bottom()[1] - 0.2)


class C18Design(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Designing concurrent code to be testable"
    SUB = "The easiest concurrent code to test is code whose goroutines can be started, observed and stopped by the caller."

    def build(self):
        cards = [("Return a way to stop", "Functions that start goroutines take a `ctx`, or return a stop/Close "
                  "method. Tests call it in `t.Cleanup`.", T.GREEN),
                 ("Signal completion", "Give callers something to wait on: a `done` channel, a `WaitGroup`, a result "
                  "channel. Tests wait on it instead of sleeping.", T.GO),
                 ("Keep goroutines local", "No package-level workers started in `init`. Each test builds its own "
                  "instance, so tests cannot interfere.", T.VIOLET),
                 ("Use the real clock, in a bubble", "With `synctest` you rarely need a fake clock interface: "
                  "`time.Now`, `time.After` and timers are already fake inside the bubble.", T.TEAL),
                 ("Make the core synchronous", "Put the logic in plain functions; keep the goroutine shell thin. "
                  "Test the logic without any concurrency at all.", T.AMBER),
                 ("Measure with RunParallel", "Benchmarks with `b.RunParallel` (8.12) show contention that a "
                  "single-goroutine benchmark hides.", T.BLUE)]
        cols, gap = 3, 0.22
        w = (CW - gap * 2) / cols
        for i, (t, b, col) in enumerate(cards):
            r, c = divmod(i, cols)
            cd = card(t, b, w=w, color=col, size=14, h=1.9)
            self.at(cd, X0 + c * (w + gap), Y0 - r * 2.12)
        k = callout("key", "If a test needs `time.Sleep`, the code is missing a signal. If a test hangs, run it with "
                    "`-timeout` and read the goroutine dump it prints.", width=CW, size=14, inline=True)
        self.at(k, X0, Y0 - 4.45)


class C18Recap(Page):
    CH, CH_NAME = CH, NAME
    TITLE = "Recap and check yourself"
    SUB = "Deterministic tests: synchronize instead of sleeping, fake the clock, and let -race and the bubble fail loudly."

    def build(self):
        self.at(section("REMEMBER", T.GO), X0, Y0)
        rec = bullets([
            "Sleep-based tests are slow and flaky; wait on a signal instead.",
            "`synctest.Test`: a bubble with a fake clock starting 2000-01-01 00:00 UTC.",
            "Time advances only when every bubble goroutine is durably blocked.",
            "`synctest.Wait` returns when everything else has settled; `Sleep` (1.27) = sleep + wait.",
            "Leftover blocked goroutines make the test fail: leaks become visible.",
            "`-race`, `-count`, `-cpu`, `-shuffle`, `-timeout`: make rare orderings happen.",
        ], width=6.1, size=15, marker="check", marker_color=T.GREEN, gap=0.12)
        self.at(rec, X0, Y0 - 0.5)
        x = 0.55
        self.at(section("CHECK YOURSELF", T.TEAL), x, Y0)
        qs = [("Inside a bubble, a goroutine waits on `mu.Lock()`. Can the fake clock advance?",
               "No. A mutex is not durably blocking: something outside could unlock it."),
              ("What is `time.Now()` at the start of every synctest bubble?",
               "Midnight UTC, January 1, 2000."),
              ("Your test passes 99 times in 100. Which flags help you find out why?",
               "`-race -count=1000 -cpu=1,2,4`, plus `-timeout` to get a dump if it hangs."),
              ("Why did `TestHitsConcurrent` fail although it printed 800?",
               "`-race` fails any test in which it detects a data race, whatever the result.")]
        y = Y0 - 0.5
        for i, (q, a_) in enumerate(qs):
            grp = vstack(txt(f"**Q{i + 1}.** {q}", size=15, color=T.TEXT, width=6.0),
                         txt(f"{{teal|**Answer.**}} {a_}", size=14, color=T.TEXT2, width=6.0), buff=0.08)
            self.at(grp, x, y)
            y = grp.get_bottom()[1] - 0.26
