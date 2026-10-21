# Go: Zero to Mastery · Module 8: The Concurrency Model

**Goroutines, channels and the scheduler, as a graphic book.** 193 illustrated pages for graduate and
postgraduate students, from the `go` keyword to the runtime's work-stealing scheduler, the memory model,
`context`, production patterns, debugging and testing. Every page is mostly picture: diagrams, timelines,
annotated code and real program output.

## Read it

- **`Module-08-Concurrency.pdf`**: the whole book, one 16:9 page per slide (2560×1440 images).
- **`index.html`**: a page viewer with a chapter list, keyboard navigation (← → Home End) and an
  overview grid (`g`). Open it from this folder so it can find `pages/`.
- **`pages/NNN-Name.png`**: the individual pages.

## Contents

| Chapter | Title | Pages |
|---|---|---|
| 8.1 | Concurrency vs Parallelism | 5–14 |
| 8.2 | Threads and Goroutines | 15–23 |
| 8.3 | Goroutines in Depth | 24–33 |
| 8.4 | Waiting for Goroutines | 34–41 |
| 8.5 | Channel Basics | 42–50 |
| 8.6 | Buffers, close and range | 51–58 |
| 8.7 | Inside a Channel | 59–67 |
| 8.8 | select and Timers | 68–77 |
| 8.9 | The Scheduler I: G, M and P | 78–84 |
| 8.10 | The Scheduler II: Queues, Syscalls and I/O | 85–92 |
| 8.11 | Preemption | 93–99 |
| 8.12 | Sharing Memory: sync and atomics | 100–114 |
| 8.13 | The Memory Model and the Race Detector | 115–128 |
| 8.14 | Cancellation with context | 129–139 |
| 8.15 | Concurrency Patterns I: Pipelines and Pools | 140–149 |
| 8.16 | Concurrency Patterns II: Production | 150–157 |
| 8.17 | Leaks, Deadlocks and Debugging | 158–166 |
| 8.18 | Testing Concurrent Code | 167–174 |
| 8.19 | Capstone: a Concurrent Web Crawler | 175–184 |
| — | Reference: cheat sheets, glossary, exercises, references | 185–193 |

Pages 1–4 are the cover, a guide to the visual language, the roadmap and the learning outcomes. Every
chapter opens with a question and closes with a recap and four check-yourself questions.

## Everything is real

- Every code listing is a complete program in `examples/` (Go 1.27.3, module `gozm/module08`).
- `tools/run_examples.py` runs them all and saves the output to `examples/*/output.txt`. The pages read
  those files, so outputs, benchmark numbers and the numbers quoted in the text always come from a real run.
- Measurements were taken on a 4-vCPU Intel Xeon 2.1 GHz Linux VM. Your numbers will differ.
- Runtime facts (queue sizes, timeouts, struct layouts, version history) were checked against the Go source
  of the version they describe.

## Rebuild

```bash
# system packages (Debian/Ubuntu)
sudo apt install fonts-inter fonts-jetbrains-mono libpango1.0-dev libcairo2-dev pkg-config \
                 xvfb pngquant ffmpeg
pip install manimgl==1.7.2 audioop-lts img2pdf

# Go 1.27.3 is fetched automatically by the go command
export GOTOOLCHAIN=go1.27.3

python3 tools/run_examples.py        # run every example, refresh outputs (about 1 minute)
python3 tools/build.py all           # render all pages, then the PDF and index.html
python3 tools/build.py render ch12   # or render one chapter (or ch12:ClassName for one page)
```

`build.py` renders headlessly under Xvfb, four scenes at a time, and prints `LAYOUT-WARN` for anything that
runs past the page edges.

## Layout

```
book/        one Python file per chapter; each page is a ManimGL Scene
  theme.py   colours, fonts and sizes
  kit.py     the drawing kit: text, code listings, callouts, gophers, G/M/P tokens, channels, charts
examples/    the Go programs behind every listing, with their captured output
pages/       rendered pages (PNG)
tools/       run_examples.py, build.py, viewer.html
```

## Note on the course prompt

The course instructions in `dataEdge/graphicbookproject/prompts/prompt-manimgl.md` could not be read when this
module was built (the repository was not accessible to this session). The book follows the request itself:
ManimGL, graphics-first pages, complete coverage. Share that file and the module can be adjusted to it.
