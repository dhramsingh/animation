from kit import *

REF = "REFERENCE"


def _pg(name):
    return PAGES.get("pages", {}).get(name, "?")


class RefOpener(Page):
    CH, CH_NAME = "", REF
    TITLE = ""

    def build(self):
        glow = Circle(radius=3.0).set_fill(T.PINK, 0.05).set_stroke(width=0).move_to(P(3.6, -0.2))
        self.add(glow)
        head = vstack(txt("**BACK MATTER**", size=18, color=T.PINK),
                      txt("**Reference**", size=72, color=T.TEXT),
                      txt("Keep these pages open while you code: the rules on one sheet, the words in one list, "
                          "and the exercises to make it stick.", size=T.SIZE_BODY, color=T.TEXT2, width=6.4),
                      buff=0.2)
        self.at(head, X0, 3.0)
        items = [("Cheat sheet: goroutines, channels, select", "CheatChannels", T.GREEN),
                 ("Cheat sheet: sync, atomic, context", "CheatSync", T.RED),
                 ("Cheat sheet: the runtime at a glance", "CheatRuntime", T.VIOLET),
                 ("Glossary", "Glossary", T.GO),
                 ("Exercises by chapter", "Exercises", T.AMBER),
                 ("References and further reading", "References", T.BLUE),
                 ("How this book was made", "Colophon", T.TEAL)]
        y = head.get_bottom()[1] - 0.45
        for t, cls, col in items:
            row = VGroup(Dot(radius=0.07, fill_color=col), txt(f"**{t}**", size=17, color=T.TEXT),
                         txt(f"p. {_pg(cls)}", size=15, color=col, weight="BOLD")).arrange(RIGHT, buff=0.2)
            self.at(row, X0, y)
            y -= 0.45
        books = VGroup()
        for i, col in enumerate((T.GREEN, T.RED, T.VIOLET, T.GO, T.AMBER)):
            b = rbox(0.55, 2.6 - (i % 2) * 0.3, color=col, fill=col, fill_opacity=0.25, radius=0.06)
            books.add(b)
        books.arrange(RIGHT, buff=0.08, aligned_edge=DOWN).move_to(P(3.2, -0.2))
        g = gopher(1.5, mood="happy").next_to(books, RIGHT, buff=0.3, aligned_edge=DOWN)
        self.add(books, g)


class CheatChannels(Page):
    CH, CH_NAME = "", REF
    TITLE = "Cheat sheet: goroutines, channels and select"
    SUB = "Everything about channel operations on one page. Chapters 8.3 to 8.8 explain each line."

    def build(self):
        tbl = table([["operation", "nil channel", "open, would block", "open, can proceed", "closed"],
                     ["`ch <- v`", "{red|blocks forever}", "blocks until a receiver or a free slot", "{green|sends}", "{red|panic}"],
                     ["`<-ch`", "{red|blocks forever}", "blocks until a value arrives", "{green|receives}",
                      "buffered values first, then zero value, ok = false"],
                     ["`close(ch)`", "{red|panic}", "{green|closes; wakes all receivers}", "{green|closes}", "{red|panic}"],
                     ["`len`, `cap`", "0, 0", "values waiting, capacity", "same", "values still buffered, capacity"]],
                    widths=[1.6, 2.0, 3.2, 2.2, CW - 9.0], size=13, center_cols=())
        self.at(tbl, X0, Y0)
        w = (CW - 0.4) / 3
        y = tbl.get_bottom()[1] - 0.3
        c1 = card("select", "Waits on several operations; runs **one** ready case, chosen **at random**. `default` "
                  "makes it non-blocking. A nil channel's case is never ready. `select {}` blocks forever. "
                  "Timeouts: `case <-time.After(d)` or a ctx.", w=w, color=T.YELLOW, size=13)
        c2 = card("Ownership rules", "The **sender** closes, and only one goroutine does it. Receivers never close. "
                  "Multiple senders: close from a separate goroutine after `wg.Wait()`. `for v := range ch` ends when "
                  "ch is closed and drained.", w=w, color=T.GREEN, size=13)
        c3 = card("Goroutines", "`go f(x)` evaluates f and x now, runs f later. main returning ends the program. "
                  "Wait with `WaitGroup`/`wg.Go`, errgroup, or a channel. Since Go 1.22 each loop iteration has its "
                  "own variable.", w=w, color=T.GO, size=13)
        for i, c in enumerate((c1, c2, c3)):
            self.at(c, X0 + i * (w + 0.2), y)
        y2 = min(c.get_bottom()[1] for c in (c1, c2, c3)) - 0.25
        idioms = table([["idiom", "code"],
                        ["signal / broadcast", "`done := make(chan struct{})` … `close(done)`"],
                        ["result with a timeout", "`ch := make(chan T, 1)`: the late send never leaks"],
                        ["semaphore of n", "`sem := make(chan struct{}, n)`; `sem <- struct{}{}`; `<-sem`"],
                        ["disable a select case", "set the channel variable to `nil`"]],
                       widths=[2.6, CW - 2.6], size=13)
        self.at(idioms, X0, y2)


class CheatSync(Page):
    CH, CH_NAME = "", REF
    TITLE = "Cheat sheet: sync, atomic and context"
    SUB = "All zero values below are ready to use; none of them may be copied after first use. Chapters 8.4, 8.12 and 8.14."

    def build(self):
        tbl = table([["type", "use it for", "key methods", "remember"],
                     ["`sync.Mutex`", "exclusive access to state", "`Lock`, `Unlock`, `TryLock`", "not re-entrant; `defer Unlock`"],
                     ["`sync.RWMutex`", "read-mostly state", "`RLock`, `RUnlock`, `Lock`", "a waiting writer blocks new readers"],
                     ["`sync.WaitGroup`", "wait for N goroutines", "`Go` (1.25), `Add`, `Done`, `Wait`", "Add before `go`; never negative"],
                     ["`sync.Once`", "one-time init", "`Do`, `OnceFunc`, `OnceValue(s)`", "callers wait for f to finish"],
                     ["`sync.Cond`", "wait for a condition", "`Wait`, `Signal`, `Broadcast`", "always wait in a `for` loop"],
                     ["`sync.Pool`", "reuse temporary objects", "`Get`, `Put`, `New`", "emptied by GC; reset objects"],
                     ["`sync.Map`", "write-once or disjoint keys", "`Load`, `Store`, `LoadOrStore`", "usually: map + Mutex"],
                     ["`atomic.Int64` etc.", "one counter, flag or pointer", "`Load`, `Store`, `Add`, `CompareAndSwap`", "sequentially consistent"],
                     ["`errgroup.Group`", "tasks that can fail", "`Go`, `Wait`, `SetLimit`, `WithContext`", "first error cancels ctx"],
                     ["`context.Context`", "cancel, deadline, values", "`Done`, `Err`, `Deadline`, `Value`", "first parameter; `defer cancel()`"]],
                    widths=[2.2, 2.9, 3.9, CW - 9.0], size=13, col_colors=[T.RED, None, None, T.TEXT2])
        self.at(tbl, X0, Y0)
        k = callout("key", "Pick by the job: hand off data → channel; protect state → Mutex; one word → atomic; wait for "
                    "a group → WaitGroup/errgroup; stop work → context.", width=CW, size=14, inline=True)
        self.at(k, X0, tbl.get_bottom()[1] - 0.3)


class CheatRuntime(Page):
    CH, CH_NAME = "", REF
    TITLE = "Cheat sheet: the runtime at a glance"
    SUB = "The numbers and knobs from chapters 8.3 and 8.9 to 8.11, all checked against the Go 1.27.3 runtime source."

    def build(self):
        w = (CW - 0.4) / 2
        nums_ = table([["what", "value"],
                       ["initial goroutine stack", "2 KB (`stackMin`), grows by copying"],
                       ["maximum stack", "1 GB on 64-bit (250 MB on 32-bit)"],
                       ["local run queue per P", "256 Gs + a `runnext` slot"],
                       ["global queue check", "every 61st schedule on a P"],
                       ["work stealing", "take half of a victim P's queue; 4 rounds over all Ps"],
                       ["sysmon sleep", "20 µs, backing off to 10 ms when idle"],
                       ["preemption", "a G running for more than 10 ms; SIGURG for async"],
                       ["blocking syscall hand-off", "P retaken after at least one sysmon tick (20 µs)"],
                       ["default GOMAXPROCS", "usable CPUs, also capped by the cgroup CPU limit"],
                       ["max OS threads", "10,000 (`debug.SetMaxThreads`)"]],
                      widths=[2.5, w - 2.5], size=13)
        self.at(nums_, X0, Y0)
        knobs = table([["GODEBUG / env", "effect"],
                       ["`GOMAXPROCS=n`", "number of Ps"],
                       ["`schedtrace=1000`", "print scheduler state every second"],
                       ["`scheddetail=1`", "with schedtrace: every G, M and P"],
                       ["`asyncpreemptoff=1`", "disable signal-based preemption"],
                       ["`containermaxprocs=0`", "ignore the cgroup CPU limit"],
                       ["`updatemaxprocs=0`", "do not adjust GOMAXPROCS at run time"],
                       ["`GOTRACEBACK=all`", "dump every goroutine on a crash"],
                       ["`GORACE=halt_on_error=1`", "stop at the first data race"]],
                      widths=[2.75, w - 2.75], size=13)
        self.at(knobs, X0 + w + 0.4, Y0)
        y = min(nums_.get_bottom()[1], knobs.get_bottom()[1]) - 0.35
        row = VGroup(gtok("G", T.GO), txt("goroutine: stack + state", size=13, color=T.TEXT2),
                     mthread("M"), txt("OS thread that runs Gs", size=13, color=T.TEXT2),
                     pchip("P", s=0.5), txt("processor: run queue + caches; GOMAXPROCS of them", size=13, color=T.TEXT2)
                     ).arrange(RIGHT, buff=0.18)
        self.at(row, X0, y)


GLOSSARY = [
    ("Amdahl's law", "the serial fraction of a program limits its speed-up on any number of cores (8.1)"),
    ("atomic operation", "a read-modify-write done by the hardware as one indivisible step (8.12)"),
    ("async preemption", "stopping a goroutine anywhere by signalling its thread with SIGURG (8.11)"),
    ("backpressure", "a slow consumer slowing the producer, e.g. through a full channel buffer (8.6)"),
    ("bubble", "synctest's isolated group of goroutines with a fake clock (8.18)"),
    ("buffered channel", "a channel with a queue of capacity > 0; sends block only when it is full (8.6)"),
    ("CAS", "compare-and-swap: write new only if the value is still old (8.12)"),
    ("cancellation", "telling goroutines to stop early, in Go through a context's Done channel (8.14)"),
    ("concurrency", "structuring a program as independently executing tasks (8.1)"),
    ("context", "a value carrying cancellation, a deadline and request-scoped values (8.14)"),
    ("critical section", "code that must run in at most one goroutine at a time (8.12)"),
    ("data race", "two unordered accesses to one location, at least one a non-atomic write (8.13)"),
    ("deadlock", "goroutines waiting for each other in a cycle; nobody can proceed (8.17)"),
    ("durably blocked", "blocked on something only another goroutine in the same bubble can release (8.18)"),
    ("fan-in / fan-out", "merging many channels into one / spreading one stream over many goroutines (8.15)"),
    ("G, M, P", "goroutine, OS thread (machine), logical processor: the scheduler's three structs (8.9)"),
    ("generator", "a function returning a channel that a goroutine fills (8.15)"),
    ("global run queue", "the scheduler's shared queue, checked every 61 schedules (8.10)"),
    ("goroutine", "a function running concurrently, scheduled by the Go runtime (8.3)"),
    ("goroutine leak", "a goroutine blocked forever; it and its memory are never freed (8.17)"),
    ("happens before", "the order Go guarantees: sequenced-before plus synchronized-before (8.13)"),
    ("hchan", "the runtime struct behind every channel: buffer, indexes, wait queues, lock (8.7)"),
]
GLOSSARY2 = [
    ("memory model", "the rules for when a write in one goroutine is visible to a read in another (8.13)"),
    ("mutex", "a lock that admits one goroutine at a time (8.12)"),
    ("netpoller", "the runtime's epoll/kqueue loop that parks goroutines waiting on sockets (8.10)"),
    ("nil channel", "a channel variable never made; operations block forever, close panics (8.6, 8.8)"),
    ("parallelism", "executing several computations at the same instant on several cores (8.1)"),
    ("park / ready", "taking a goroutine off the CPU to wait / putting it back on a run queue (8.7, 8.9)"),
    ("pipeline", "stages connected by channels, each running concurrently (8.15)"),
    ("preemption", "the runtime taking the CPU back from a running goroutine (8.11)"),
    ("race detector", "ThreadSanitizer-based tool enabled with -race (8.13)"),
    ("runnext", "a P's one-slot fast lane for the goroutine it just readied (8.10)"),
    ("select", "a statement that waits on several channel operations at once (8.8)"),
    ("semaphore", "a counter limiting how many goroutines do something at once (8.15)"),
    ("sequential consistency", "all operations appear in one global order that respects each goroutine's order (8.13)"),
    ("spinning thread", "an M actively looking for work before going to sleep (8.10)"),
    ("starvation mode", "the Mutex mode that hands the lock straight to the oldest waiter (8.12)"),
    ("sudog", "a waiting goroutine's entry in a channel or semaphore queue (8.7)"),
    ("sysmon", "a runtime thread without a P: preemption, netpoll, retaking Ps (8.10, 8.11)"),
    ("token bucket", "a rate limiter: tokens refill at a rate, requests spend them (8.16)"),
    ("unbuffered channel", "a channel of capacity 0: every send meets a receive (8.5)"),
    ("WaitGroup", "a counter that lets one goroutine wait for others to finish (8.4)"),
    ("work stealing", "an idle P taking half of another P's run queue (8.10)"),
    ("worker pool", "a fixed number of goroutines pulling jobs from one channel (8.15)"),
]


def _glossary(page, items):
    w = (CW - 0.5) / 2
    half = (len(items) + 1) // 2
    for c, chunk in enumerate((items[:half], items[half:])):
        y = Y0
        for term, d in chunk:
            t = txt(f"{{go|**{term}**}}  {d}", size=16, color=T.TEXT2, width=w)
            page.at(t, X0 + c * (w + 0.5), y)
            y = t.get_bottom()[1] - 0.2


class Glossary(Page):
    CH, CH_NAME = "", REF
    TITLE = "Glossary (A to H)"
    SUB = "The words of the module, with the chapter that explains each one."

    def build(self):
        _glossary(self, GLOSSARY)


class Glossary2(Page):
    CH, CH_NAME = "", REF
    TITLE = "Glossary (M to W)"
    SUB = "The words of the module, with the chapter that explains each one."

    def build(self):
        _glossary(self, GLOSSARY2)


EXERCISES = [
    ("8.1", "★", "Run ch01_speedup with GOMAXPROCS 1 to 8 on your machine. Fit Amdahl's law: what serial fraction p explains your curve?"),
    ("8.2", "★", "With ch02_goroutine_cost, estimate how many idle goroutines fit in 1 GB. How many threads would?"),
    ("8.3", "★★", "Write a recursive function that grows a goroutine's stack to 1 MB. Measure StackInuse before and after."),
    ("8.4", "★", "Rewrite a WaitGroup program with wg.Go. Then make one task fail and switch to errgroup."),
    ("8.5", "★", "Pass a token around a ring of 5 goroutines 1,000 times with unbuffered channels. Time one hop."),
    ("8.6", "★★", "Three senders, one channel, one receiver ranging over it. Close it safely without a panic."),
    ("8.7", "★★★", "In runtime/chan.go find where a receiver copies straight from a waiting sender's stack. Why is it safe?"),
    ("8.8", "★★", "Merge two channels with select; set each to nil when it closes; stop when both are nil."),
    ("8.9", "★", "Run a CPU-bound program with GODEBUG=schedtrace=500 and explain every field of one line."),
    ("8.10", "★★", "Start 100 goroutines doing a blocking syscall. Count OS threads, then repeat with network waits."),
    ("8.11", "★", "Reproduce the pre-1.14 hang with asyncpreemptoff=1. Add one function call to the loop. What changes?"),
    ("8.12", "★★", "Fix the racy counter with a Mutex, an atomic and a channel. Benchmark all three with RunParallel."),
    ("8.13", "★★★", "Change the litmus test so only one goroutine uses atomics. Can 0, 0 still happen? Explain."),
    ("8.14", "★★", "Thread a ctx through three layers, cancel with a cause at the top, and log Cause at the bottom."),
    ("8.15", "★★", "Build gen → square → print with cancellation, then fan out square to 4 workers keeping order."),
    ("8.16", "★★", "Add graceful shutdown with signal.NotifyContext and http.Server.Shutdown to a small HTTP server."),
    ("8.17", "★★", "Write an ABBA deadlock, read its dump, fix it with a lock order. Then leak a goroutine and find it with goroutineleak."),
    ("8.18", "★★", "Turn a time.Sleep-based test for a 1-minute cache expiry into a synctest test that runs in 0 s."),
    ("8.19", "★★★", "Do the six crawler exercises; keep the synctest + -race test green after each."),
]


class Exercises(Page):
    CH, CH_NAME = "", REF
    TITLE = "Exercises by chapter"
    SUB = "★ check your understanding  ·  ★★ apply it  ·  ★★★ dig into the runtime. Every exercise starts from an example in examples/."

    def build(self):
        w = (CW - 0.5) / 2
        half = (len(EXERCISES) + 1) // 2
        for c, chunk in enumerate((EXERCISES[:half], EXERCISES[half:])):
            y = Y0
            for ch, stars, t in chunk:
                b = pill(ch, T.GO, size=12)
                s = txt(stars, size=12, color=T.YELLOW, weight="BOLD")
                tt = txt(t, size=13, color=T.TEXT2, width=w - 1.45)
                b.move_to(P(X0 + c * (w + 0.5), y), aligned_edge=UL)
                s.move_to(P(X0 + c * (w + 0.5) + 0.75, y - 0.02), aligned_edge=UL)
                tt.move_to(P(X0 + c * (w + 0.5) + 1.4, y), aligned_edge=UL)
                self.add(b, s, tt)
                y = min(tt.get_bottom()[1], b.get_bottom()[1]) - 0.16


REFS = [
    ("Specifications and source", [
        "The Go Programming Language Specification: go statements, channel types, select (go.dev/ref/spec)",
        "The Go Memory Model, version of June 6, 2022 (go.dev/ref/mem)",
        "Go 1.27.3 source: runtime/proc.go, runtime2.go, chan.go, select.go, sema.go, preempt.go, signal_unix.go, mgc.go; "
        "internal/sync/mutex.go; sync; context; testing/synctest",
    ]),
    ("Design documents and proposals", [
        "Dmitry Vyukov, \"Scalable Go Scheduler Design Doc\", 2012",
        "Austin Clements, \"Proposal: Non-cooperative goroutine preemption\", golang/go#24543, 2018",
        "Russ Cox, \"Hardware Memory Models\", \"Programming Language Memory Models\", \"Updating the Go Memory Model\", 2021",
    ]),
    ("Go blog and talks", [
        "Andrew Gerrand, \"Share Memory By Communicating\", 2010  ·  Rob Pike, \"Go Concurrency Patterns\", Google I/O 2012",
        "Rob Pike, \"Concurrency is not Parallelism\", 2012  ·  Sameer Ajmani, \"Advanced Go Concurrency Patterns\", 2013",
        "Dmitry Vyukov and Andrew Gerrand, \"Introducing the Go Race Detector\", 2013",
        "Sameer Ajmani, \"Go Concurrency Patterns: Context\" and \"Pipelines and cancellation\", 2014",
        "Damien Neil, \"Testing concurrent code with testing/synctest\", 2025",
    ]),
    ("Papers and books", [
        "C. A. R. Hoare, \"Communicating Sequential Processes\", CACM 21(8), 1978",
        "Leslie Lamport, \"How to Make a Multiprocessor Computer That Correctly Executes Multiprocess Programs\", 1979",
        "Hans-J. Boehm and Sarita V. Adve, \"Foundations of the C++ Concurrency Memory Model\", PLDI 2008",
        "Konstantin Serebryany and Timur Iskhodzhanov, \"ThreadSanitizer: data race detection in practice\", 2009",
        "Marc Brooker, \"Exponential Backoff And Jitter\", AWS Architecture Blog, 2015",
        "Alan Donovan and Brian Kernighan, The Go Programming Language, chapters 8-9, 2015  ·  Katherine Cox-Buday, Concurrency in Go, 2017",
    ]),
]


class References(Page):
    CH, CH_NAME = "", REF
    TITLE = "References and further reading"
    SUB = "Primary sources first. Every runtime number in this module was checked against the Go 1.27.3 source code."

    def build(self):
        y = Y0
        cols = [T.GO, T.VIOLET, T.GREEN, T.AMBER]
        for (head, items), col in zip(REFS, cols):
            s = section(head, col, size=15)
            self.at(s, X0, y)
            b = bullets(items, width=CW, size=13, marker="dot", marker_color=col, gap=0.05)
            self.at(b, X0, s.get_bottom()[1] - 0.12)
            y = b.get_bottom()[1] - 0.25


class Colophon(Page):
    CH, CH_NAME = "", REF
    TITLE = "How this book was made"
    SUB = "Every page is a ManimGL scene; every listing is a real program; every output was captured, not typed."

    def build(self):
        w = (CW - 0.4) / 2
        steps = num_steps([("Write the programs.", "Each listing is a file in `examples/`. `tools/run_examples.py` runs "
                            "them all with Go 1.27.3 and saves the real output, including the races and the deadlocks."),
                           ("Measure on real hardware.", "Timings come from a 4-vCPU Intel Xeon 2.1 GHz Linux VM. "
                            "Pages read the numbers from the saved output, so the text always matches the run."),
                           ("Draw with ManimGL.", "Each page is a `Scene` built from a small kit of shapes: gophers, "
                            "G/M/P tokens, channel tubes, lanes and code panels. One theme file sets every colour."),
                           ("Render and check.", "`tools/build.py all` renders every page at 2560×1440, warns about "
                            "anything that overflows, then builds the PDF and the HTML viewer.")],
                          width=w, color=T.TEAL, size=14, gap=0.16)
        self.at(steps, X0, Y0)
        x = X0 + w + 0.4
        tm = code("python3 tools/run_examples.py   # run every example\n"
                 "python3 tools/build.py all      # render, PDF, viewer\n"
                 "# pages/*.png  Module-08-Concurrency.pdf  index.html",
                 size=14, lang="text", title="rebuild everything", width=w, numbers=False)
        self.at(tm, x, Y0)
        v = callout("note", "Your numbers will differ: other CPUs, other loads, other Go versions. That is the point of "
                    "the \"measured\" pages: run them yourself and compare.", width=w, size=14)
        self.at(v, x, tm.get_bottom()[1] - 0.25)
        g = gopher(1.4, mood="happy").move_to(P(x + w / 2, v.get_bottom()[1] - 1.0))
        self.add(g, txt("Happy concurrent coding.", size=18, color=T.GO, weight="BOLD").next_to(g, DOWN, buff=0.15))
