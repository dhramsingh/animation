# Attention from scratch: four 2D animations

Four postgraduate-level animations on scaled dot-product attention, for a course on building an LLM from scratch. Each is an interactive page and an MP4 export. Everything on screen is drawn in 2D canvas, including the math, so every formula, chart and diagram is part of the picture.

| # | Animation | Length | Covers |
|---|-----------|--------|--------|
| 1 | The Query–Key dot product | 1:53 | Why Q·K scores affinity, the geometry of the dot product, a worked example, why S is asymmetric, softmax and the weighted sum of values |
| 2 | Why divide by √d_k? | 1:45 | Variance of a dot product (d_k), the unit-variance assumption, Monte-Carlo checks, the fix, and why magnitude matters for exp |
| 3 | Softmax saturation and vanishing gradients | 1:59 | Softmax as a soft argmax, sharpness versus scale, the Jacobian, backprop through softmax, the flat zero-gradient region, numerical stability |
| 4 | Scaled dot-product attention, end to end | 2:12 | Shapes at every step, scores, scaling, causal mask, row-wise softmax, output AV, a 15-line NumPy version, multi-head attention |

## Files

- `index.html`: gallery with links to the interactive pages and MP4s.
- `videos/*.html`: one self-contained page per animation.
- `exports/*.mp4`: 1280×720, 30 fps, H.264, no narration (on-screen captions only).
- `common/anim-kit.js`, `common/anim-kit.css`: the shared engine. It handles the timeline, the captions, and a small TeX typesetter that draws formulas on the canvas.
- `tools/export-video.js`: re-renders any page to MP4.

## Using the pages

- Open `index.html` or any file in `videos/` in a browser.
- Controls: **Space** play/pause, **←/→** previous/next scene, **R** restart. You can also drag the timeline, pick a chapter, or change the speed.
- `?video=1` hides the controls and plays full-screen, for recording.

## Re-exporting the MP4s

```bash
npm install playwright            # or use an existing Chromium via CHROME_PATH
node tools/export-video.js videos/01-query-key-dot-product.html exports/01-query-key-dot-product.mp4
```

The exporter needs `ffmpeg` on the PATH. It seeks each frame exactly, so timing is deterministic.

## About the numbers

- The worked examples use hand-picked toy vectors (5 tokens, d_k = d_v = 4). They are illustrative, not from a trained model. All the scores, weights and outputs are computed in code from these vectors, so they match the formulas on screen.
- The d_k experiments use fixed random seeds, so the histograms and Monte-Carlo values are reproducible.

## Status

The course spec `prompts/prompt-js-2d.md` in `dataEdge/animationproject` could not be read when these were built, so the format follows the brief in the request. Share that file and the animations can be adjusted to it.
