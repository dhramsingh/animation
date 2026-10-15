# Responsive CSS breakpoints: three ManimGL animations

Three graduate-level animations on choosing media-query breakpoints, built with [ManimGL](https://github.com/3b1b/manim) (the 3Blue1Brown engine). They are designed to be watched without narration. Diagrams, graphs and animated layouts carry the argument, and short captions only point at what to look at.

| # | Video | Length | Question it answers |
|---|-------|--------|---------------------|
| 1 | [Why device breakpoints are mathematically doomed](exports/01-device-breakpoints-are-doomed.mp4) | 4:26 | Why is `max-width: 768px` "for the iPad" a losing strategy? |
| 2 | [Content-driven breakpoints](exports/02-content-driven-breakpoints.mp4) | 4:06 | What is a content-driven breakpoint, and how do you find its exact value? |
| 3 | [Why media queries belong in em](exports/03-em-media-queries.mp4) | 3:54 | What do `em`/`rem` breakpoints buy you, and how do they protect readers who enlarge their default font size? |

All three are 1920×1080 at 30 fps, H.264, with no audio.

## What each video shows

### 1 · Why device breakpoints are mathematically doomed
1. **The "iPad rule"**: six iPads drawn to scale (744, 768, 810, 820, 834 and 1024 CSS px wide). `max-width: 768px` matches 2 of 6 in portrait and 0 of 6 in landscape. Split View (981 | 375, 678 | 678) and Slide Over (320) put phone-sized windows on the same screen. "The iPad" turns out to be a scatter of 16 widths.
2. **Width is a continuum**: 21 common device widths sit as dots on a number line, then a dragged desktop window sweeps the whole interval. A finite list of widths has measure zero.
3. **Media queries measure CSS pixels**: device pixels group into CSS pixels (DPR), and page zoom adds one more division: `w = W / (DPR · z)`. The hyperbola `1440 / z` shows a desktop becoming "an iPad" at 187.5 % zoom, and widths come out as real numbers (110 % → 1309.09 px).
4. **Width cannot identify a device**: five different situations map to `w = 768`, so `f: device ↦ w` is not injective and has no inverse.
5. **Integer thinking, real-valued widths**: a zoom inset shows the gap `767 < w < 768` that `max-width: 767px` / `min-width: 768px` leaves uncovered (a 844 px window at 110 % lands at 767.27). The common `.98` patch shrinks the gap but never closes it, and the overlap version double-matches at exactly 768. Range syntax `(width < 768px)` / `(width >= 768px)` partitions the line exactly.
6. **A target that multiplies and moves**: 6 models × 2 orientations × 13 zoom levels gives 156 combinations and 139 distinct widths (248 to 2732 px). A timeline shows new iPads drifting off 768 since 2017.
7. **Where layouts actually break**: a live card grid sweeps from 320 to 1200 px, synced to a plot of card width. The device rule overflows between 768 and 848 px. The content rule (`W_n = n·m + (n−1)·g + 2p` → 568, 848, 1128) never leaves the "fits" band.
8. **Summary** in four pictures.

### 2 · Content-driven breakpoints
1. **A definition you can compute**: each content constraint has a slack `g(w) = available − required`. A content-driven breakpoint is a root `g(b*) = 0`. Cards (848), navigation (624) and text measure (632) are plotted together, and no device appears in the definition.
2. **Method 1, the stretch test**: an article widens from 320 px with a live characters-per-line gauge and the eye's return sweep. The nav fits at 624 and the measure hits 75 characters at 632. `max-width: 66ch` absorbs that with no breakpoint, and a 15em sidebar fits at 832 px = 52em.
3. **Two ways a layout breaks**: structural failures (overflow, collision, clipping, orphan wrap) and visual ones (line too long, wasted space, upscaled image, stretched card), each with a measurable test.
4. **Method 2, compute it**: a ruler of padding, card and gap segments gives `W_3 = 848 px`, with a table of `W_n` in px and em. Each nav item's intrinsic width sums to 624 px = 39em, and squeezing the nav shows the collision exactly there. A glyph ruler gives 75 × 8 + 32 = 632 px = 39.5em.
5. **The constraint map**: every constraint becomes a green/red bar over w. Breakpoints are the colour changes, one layout fits each interval, and four `@media` rules in em come out.
6. **The procedure**: a flowchart (widen → constraint fails? → can intrinsic CSS absorb it? → fix it or add `@media (width >= w*/16 em)`) with a token tracing the run and the breakpoints accumulating on a ruler.
7. **Let the browser solve it**: `repeat(auto-fit, minmax(16rem, 1fr))` gives `n(w) = ⌊(w − 2p + g)/(m + g)⌋`, whose steps land exactly on `W_n`. Container queries then let the same component break per container: a main column versus a sidebar.
8. **The recipe**, step by step with pictures.

### 3 · Why media queries belong in em
1. **Two rulers**: a fixed CSS-px ruler above an em ruler that stretches as the reader's default font size goes 16 → 20 → 24 → 12. The `53em` breakpoint follows the space three cards need (848 → 1060 → 1272 → 636 px), and `848px` stays put.
2. **What em means inside a media query**: browser setting → initial font-size → `@media`. `html { font-size: 62.5% }` changes rem for rules but not inside queries, so `em ≡ rem ≡ f` there. The classic trap: `48rem` in a query is 768 px, not 480.
3. **The experiment**: two 900 px windows, one stylesheet in px and one in em, with rem-sized content. At 20 px the px version forces 3 columns of 267 px cards that need 320 (overflow), while the em version drops to 2 columns of 415 px.
4. **The (width, font size) plane**: with rem content, the fit boundary is the ray `w = 53f`. A px breakpoint is a vertical line that matches it only on the `f = 16` row, leaving an overflow wedge above and a wasted-space wedge below. An em breakpoint is the ray itself. Layout depends only on `w/f`, which gives a fan of rays against a grid of lines.
5. **Zoom versus font size**: page zoom moves the reader horizontally, and both rules flip together. The font-size setting moves them vertically, and only em responds (at f = 18.9 px for a 1000 px window).
6. **Characters per line survive scaling**: a 348px column drops to 43 → 34 → 29 characters per line as text grows, while a 21.75em column stays at 43. The 24 px em layout scaled by 2/3 lands exactly on the 16 px one.
7. **The psychology**: "768px" evokes hardware, while "48em" is a quantity of text (~96 characters). One reader-chosen number drives text, gaps, card widths and breakpoints, and px breakpoints cut that wire. A WCAG 1.4.4 / 1.4.10 demo at 200 % text has em reflowing 4 → 3 → 2 columns while px overflows.
8. **Summary** with the phase diagram and final CSS.

## Numbers and assumptions

- CSS widths of iPads (portrait × landscape): mini 6 744×1133, 9.7″ 768×1024, 10.2″ 810×1080, Air 820×1180, Pro 11″ 834×1194, Pro 12.9″ 1024×1366, Pro 13″ (2024) 1032×1376. Split View sizes are Apple's 12.9″ figures.
- The browser zoom presets are the 13 Chrome/Edge steps from 50 % to 300 % (50, 67, 75, 80, 90, 100, 110, 125, 150, 175, 200, 250, 300). Firefox uses slightly different steps; the conclusion does not change.
- The card grid uses a 16em minimum card width, 1.5em gaps and 1em page padding, so `W_n` = 18, 35.5, 53 and 70.5em.
- The nav items' intrinsic widths (64, 96, 80, 60, 84 px) and logo (120 px) are illustrative measurements.
- Characters per line assume an average glyph of 0.5em, a common rule of thumb for Latin text. The 45–75 character band is the usual typographic guideline.
- Every number on screen is computed in the scene code from these inputs, so the graphics and the formulas agree.

## Rendering

```bash
pip install manimgl audioop-lts      # audioop-lts is needed on Python 3.13+
# system: ffmpeg, LaTeX + dvisvgm, Pango/Cairo dev headers, fonts Inter + DejaVu Sans Mono
./render.sh            # all three videos at 1080p into exports/
./render.sh 2 -l       # one video at 480p for a quick look
```

`render.sh` renders every chapter scene (`V<n>S<k>_*`) with ManimGL, wrapping it in `xvfb-run` on a headless machine, then joins the chapters with ffmpeg. To iterate on one chapter:

```bash
manimgl scenes/video3_em_breakpoints.py V3S4_PhaseDiagram        # live preview window
manimgl scenes/video3_em_breakpoints.py V3S4_PhaseDiagram -w -l   # write a 480p file to build/
```

`custom_config.yml` selects ManimGL's `basic` TeX template (no `dsfont` needed), the dark background and the default fonts. `scenes/rcss_kit.py` holds the shared palette and drawing helpers: devices, browser frames, cards, word-bar paragraphs that reflow, number lines, plots and code panels.

## Status

The project brief at `dataEdge/animationproject/prompts/prompt-manimgl.md` was not reachable from the session that built these (the repository was not attached and access was denied). The videos follow ManimGL and 3Blue1Brown conventions; share the brief and the scenes can be adjusted to it.
