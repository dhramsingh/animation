/* ===================================================================
   Anim Kit: a small, dependency-free 2D canvas framework.
   - Logical stage is 1280 x 720; every scene draws in those units.
   - Math is typeset ON the canvas (AK.tex), so formulas are part of
     the picture and are captured in the exported video.
   - Playback: play/pause, scrub, scene chapters, keyboard shortcuts.
   - ?video=1 hides the UI for recording; window.Kit.seek(ms) renders
     any exact instant, which is how the MP4 files are produced.
   =================================================================== */
(function () {
  'use strict';

  const W = 1280, H = 720;

  /* ---------- palette & fonts ---------- */
  const C = {
    bg0: '#0a0f1f', bg1: '#131d38', panel: '#16213f', panel2: '#1e2b52',
    line: '#2b3b66', text: '#eef3ff', dim: '#a3b1d6', faint: '#63719a',
    q: '#4fa3ff',      // Query  (blue)
    k: '#ffb547',      // Key    (amber)
    v: '#5fd38d',      // Value  (green)
    hot: '#ff6b6b',    // negative / danger
    acc: '#b38cff',    // accent (violet)
    gold: '#ffd166', teal: '#2dd4bf', ink: '#0a0f1f'
  };
  const SANS = 'Inter, "Segoe UI", Helvetica, Arial, sans-serif';
  const MATH = '"STIX Two Math", "Latin Modern Math", "Cambria Math", Caladea, "Times New Roman", "Liberation Serif", FreeSerif, serif';
  const col = (n) => (n && C[n]) || n || C.text;

  /* ---------- numeric helpers ---------- */
  const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
  const lerp = (a, b, u) => a + (b - a) * u;
  const ease = (x) => { x = clamp(x); return x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; };
  const seg = (t, a, b) => clamp((t - a) / (b - a));     // linear 0..1 between ms a..b
  const sm = (t, a, b) => ease(seg(t, a, b));            // eased 0..1
  const sum = (a) => a.reduce((s, x) => s + x, 0);
  const vdot = (a, b) => sum(a.map((x, i) => x * b[i]));
  const matmul = (A, B) => A.map((r) => B[0].map((_, j) => sum(r.map((x, k) => x * B[k][j]))));
  const transpose = (A) => A[0].map((_, j) => A.map((r) => r[j]));
  const softmax = (a) => { const m = Math.max(...a); const e = a.map((x) => Math.exp(x - m)); const s = sum(e); return e.map((x) => x / s); };
  const mean = (a) => sum(a) / a.length;
  const std = (a) => { const m = mean(a); return Math.sqrt(mean(a.map((x) => (x - m) ** 2))); };
  const norm = (a) => Math.sqrt(vdot(a, a));
  const gpdf = (v, mu, sd) => Math.exp(-((v - mu) ** 2) / (2 * sd * sd)) / (sd * Math.sqrt(2 * Math.PI));

  // Deterministic PRNG (mulberry32) and Box-Muller normal samples.
  function rng(seed) {
    let s = seed >>> 0;
    return () => {
      s = (s + 0x6D2B79F5) >>> 0;
      let z = s;
      z = Math.imul(z ^ (z >>> 15), z | 1);
      z ^= z + Math.imul(z ^ (z >>> 7), z | 61);
      return ((z ^ (z >>> 14)) >>> 0) / 4294967296;
    };
  }
  function randn(r) { const u = Math.max(r(), 1e-12), v = r(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); }

  // Format a number with a true minus sign and no "-0.00".
  function fmt(x, d = 2) {
    const v = Number(x.toFixed(d));
    return (v === 0 ? (0).toFixed(d) : v.toFixed(d)).replace('-', '−');
  }
  function clock(ms) {
    const s = Math.floor(ms / 1000);
    return `${String(Math.floor(s / 60)).padStart(2, '0')}:${String(s % 60).padStart(2, '0')}`;
  }

  /* ---------- colour ---------- */
  function hex2(h) {
    h = h.replace('#', '');
    if (h.length === 3) h = h.split('').map((c) => c + c).join('');
    const n = parseInt(h, 16);
    return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
  }
  function mix(a, b, u) {
    const A = hex2(col(a)), B = hex2(col(b)); u = clamp(u);
    return `rgb(${Math.round(lerp(A[0], B[0], u))},${Math.round(lerp(A[1], B[1], u))},${Math.round(lerp(A[2], B[2], u))})`;
  }
  function alpha(hex, a) { const [r, g, b] = hex2(col(hex)); return `rgba(${r},${g},${b},${a})`; }
  // Signed colour map: negative -> neg colour, positive -> pos colour, 0 -> dark panel.
  function divMap(v, m, neg = C.q, pos = C.k) {
    const u = clamp(v / m, -1, 1);
    return u >= 0 ? mix('#1b2a52', pos, u) : mix('#1b2a52', neg, -u);
  }
  // Sequential map for 0..1: navy -> teal -> gold.
  function seqMap(u) { u = clamp(u); return u < 0.5 ? mix('#1b2a52', C.teal, u * 2) : mix(C.teal, C.gold, (u - 0.5) * 2); }
  const inkFor = (v, m) => (v / m > 0.45 ? C.ink : C.text);

  /* ---------- text ---------- */
  function font(size, o = {}) {
    return `${o.italic ? 'italic ' : ''}${o.bold ? '700 ' : '400 '}${size}px ${o.family || SANS}`;
  }
  const mctx = document.createElement('canvas').getContext('2d');
  function measure(s, size, o = {}) { mctx.font = font(size, o); return mctx.measureText(s).width; }

  function text(c, s, x, y, o = {}) {
    const size = o.size || 24;
    c.save();
    c.globalAlpha *= o.alpha ?? 1;
    c.font = font(size, o);
    c.fillStyle = col(o.color);
    c.textAlign = o.align || 'left';
    c.textBaseline = o.base || 'middle';
    c.fillText(s, x, y);
    c.restore();
  }
  function wrap(s, size, maxW, o = {}) {
    const lines = []; let line = '';
    for (const w of s.split(' ')) {
      const t = line ? line + ' ' + w : w;
      if (measure(t, size, o) > maxW && line) { lines.push(line); line = w; } else line = t;
    }
    if (line) lines.push(line);
    return lines;
  }
  /* Rich text: plain words plus $...$ segments, which are typeset as math.
     Math segments are atomic for wrapping. */
  function richTokens(s, size, o = {}) {
    const out = [];
    s.split('$').forEach((part, idx) => {
      if (idx % 2 === 1) { out.push({ m: true, s: part, w: texW(part, size) }); return; }
      part.split(/(\s+)/).forEach((tk) => {
        if (!tk) return;
        if (/^\s+$/.test(tk)) out.push({ sp: true, w: measure(' ', size, o) });
        else out.push({ s: tk, w: measure(tk, size, o) });
      });
    });
    return out;
  }
  function richLines(tokens, maxW) {
    const lines = []; let line = [], w = 0;
    for (const tk of tokens) {
      if (tk.sp) { if (line.length) { line.push(tk); w += tk.w; } continue; }
      if (line.length && w + tk.w > maxW) {
        while (line.length && line[line.length - 1].sp) w -= line.pop().w;
        lines.push(line); line = []; w = 0;
      }
      line.push(tk); w += tk.w;
    }
    while (line.length && line[line.length - 1].sp) line.pop();
    if (line.length) lines.push(line);
    return lines;
  }
  // Draw wrapped lines starting at x; yc is the vertical centre of the first line.
  function richDraw(c, lines, x, yc, lh, o = {}) {
    const size = o.size || 24;
    c.save();
    c.globalAlpha *= o.alpha ?? 1;
    lines.forEach((line, li) => {
      const yy = yc + li * lh;
      let xx = x;
      for (const tk of line) {
        if (!tk.sp) {
          if (tk.m) tex(c, tk.s, xx, yy, { size, color: o.color, anchor: 'mid' });
          else text(c, tk.s, xx, yy, { size, color: o.color, bold: o.bold });
        }
        xx += tk.w;
      }
    });
    c.restore();
  }
  // One line of rich text, left-aligned at x, centred on yc.
  function rich(c, s, x, yc, o = {}) {
    const size = o.size || 24;
    const lines = richLines(richTokens(s, size, o), 1e9);
    richDraw(c, lines, x, yc, 0, o);
    return lines.length ? lines[0].reduce((a, t) => a + t.w, 0) : 0;
  }
  function para(c, s, x, y, maxW, o = {}) {
    const size = o.size || 24, lh = o.lh || size * 1.35;
    const lines = richLines(richTokens(s, size, o), maxW);
    richDraw(c, lines, x, y + lh / 2, lh, o);
    return lines.length * lh;
  }

  /* ---------- mini TeX typesetter (drawn on canvas) ---------- */
  const SYM = {
    cdot: '·', odot: '⊙', times: '×', pm: '±', approx: '≈', propto: '∝', to: '→', rightarrow: '→', leftarrow: '←',
    leq: '≤', le: '≤', geq: '≥', ge: '≥', neq: '≠', infty: '∞', partial: '∂', in: '∈', ldots: '…', dots: '…',
    cdots: '⋯', mid: '∣', lVert: '‖', rVert: '‖', Vert: '‖', top: 'ᵀ', sim: '∼', equiv: '≡', nabla: '∇',
    prime: '′', circ: '∘', Rightarrow: '⇒', implies: '⇒', land: '∧', lor: '∨', ell: 'ℓ', hbar: 'ℏ', lnot: '¬',
    sum: '∑', prod: '∏', forall: '∀', exists: '∃', subset: '⊂', cup: '∪', cap: '∩', emptyset: '∅'
  };
  const GREEK = {
    alpha: 'α', beta: 'β', gamma: 'γ', delta: 'δ', epsilon: 'ε', varepsilon: 'ε', zeta: 'ζ', eta: 'η', theta: 'θ',
    iota: 'ι', kappa: 'κ', lambda: 'λ', mu: 'μ', nu: 'ν', xi: 'ξ', pi: 'π', rho: 'ρ', sigma: 'σ', tau: 'τ',
    phi: 'φ', varphi: 'φ', chi: 'χ', psi: 'ψ', omega: 'ω',
    Gamma: 'Γ', Delta: 'Δ', Theta: 'Θ', Lambda: 'Λ', Pi: 'Π', Sigma: 'Σ', Phi: 'Φ', Omega: 'Ω', Psi: 'Ψ'
  };
  const REL = new Set(['=', '+', '−', '<', '>', '≈', '≤', '≥', '≠', '∝', '→', '←', '±', '≡', '∼', '⇒']);
  const BIGOPS = new Set(['∑', '∏']);

  function texTokens(src) {
    const out = []; let i = 0;
    while (i < src.length) {
      const ch = src[i];
      if (ch === '\\') {
        let j = i + 1;
        if (/[a-zA-Z]/.test(src[j] || '')) {
          while (j < src.length && /[a-zA-Z]/.test(src[j])) j++;
          out.push({ t: 'cmd', v: src.slice(i + 1, j) });
        } else { out.push({ t: 'cmd', v: src[j] || '' }); j++; }
        i = j;
      } else if (ch === '{' || ch === '}' || ch === '_' || ch === '^') { out.push({ t: ch }); i++; }
      else { out.push({ t: 'ch', v: ch === '-' ? '−' : ch }); i++; }
    }
    return out;
  }

  function texParse(tokens) {
    let p = 0;
    const peek = () => tokens[p];
    // Raw text of a {...} argument (keeps spaces, used for \text, \mathrm, \textcolor names).
    function readRaw() {
      const tk = peek(); if (!tk) return '';
      if (tk.t !== '{') { p++; return tk.v ?? tk.t; }
      p++; let depth = 1, s = '';
      while (p < tokens.length) {
        const x = tokens[p++];
        if (x.t === '{') depth++;
        else if (x.t === '}') { depth--; if (depth === 0) break; }
        s += x.t === 'ch' ? x.v : x.t === 'cmd' ? (SYM[x.v] || GREEK[x.v] || x.v) : x.t;
      }
      return s;
    }
    function parseBase() {
      const tk = peek();
      if (!tk) return null;
      if (tk.t === '{') { p++; const c = parseSeq(); if (peek() && peek().t === '}') p++; return { k: 'g', c }; }
      if (tk.t === 'ch') {
        p++;
        if (tk.v === ' ') return null;                       // spaces are ignored in math mode
        return { k: 't', s: tk.v, it: /[A-Za-z]/.test(tk.v), rel: REL.has(tk.v) };
      }
      if (tk.t === 'cmd') {
        p++; const v = tk.v;
        if (v === 'frac' || v === 'dfrac') { const n = readArg(); const d = readArg(); return { k: 'frac', n, d }; }
        if (v === 'sqrt') return { k: 'sqrt', c: readArg() };
        if (v === 'textcolor' || v === 'color') { const name = readRaw(); const c = readArg(); return { k: 'col', name, c }; }
        if (v === 'mathrm' || v === 'text' || v === 'operatorname' || v === 'textrm') return { k: 't', s: readRaw(), it: false };
        if (v === 'mathbf' || v === 'textbf' || v === 'boldsymbol') return { k: 't', s: readRaw(), it: false, b: true };
        if (v === 'mathit') return { k: 't', s: readRaw(), it: true };
        if (v === 'mathbb') { const r = readRaw(); return { k: 't', s: r === 'E' ? '𝔼' : r, it: false }; }
        if (v === 'quad') return { k: 'sp', w: 1 };
        if (v === 'qquad') return { k: 'sp', w: 2 };
        if (v === ',') return { k: 'sp', w: 0.17 };
        if (v === ';') return { k: 'sp', w: 0.28 };
        if (v === '!') return { k: 'sp', w: -0.17 };
        if (['left', 'right', 'big', 'Big', 'bigl', 'bigr', 'displaystyle', 'limits', 'nolimits'].includes(v)) return null;
        if (v === 'sum' || v === 'prod') return { k: 'big', s: SYM[v] };
        if (GREEK[v]) return { k: 't', s: GREEK[v], it: true };
        if (SYM[v]) return { k: 't', s: SYM[v], it: false, rel: REL.has(SYM[v]) };
        return { k: 't', s: v, it: false };                   // \exp, \log, \max, \{ ...
      }
      if (tk.t === '}') return null;
      p++; return { k: 't', s: tk.t, it: false };
    }
    function readArg() {
      const tk = peek();
      if (!tk) return { k: 't', s: '', it: false };
      if (tk.t === '{') { p++; const c = parseSeq(); if (peek() && peek().t === '}') p++; return { k: 'g', c }; }
      return parseBase() || { k: 't', s: '', it: false };
    }
    function parseSeq() {
      const atoms = [];
      while (p < tokens.length && tokens[p].t !== '}') {
        const tk = tokens[p];
        if (tk.t === '_' || tk.t === '^') {               // script with no base
          const atom = { base: null };
          atoms.push(atom);
          while (p < tokens.length && (tokens[p].t === '_' || tokens[p].t === '^')) {
            const isSub = tokens[p].t === '_'; p++;
            const arg = readArg();
            if (isSub) atom.sub = arg; else atom.sup = arg;
          }
          continue;
        }
        const base = parseBase();
        if (!base) continue;
        const atom = { base };
        atoms.push(atom);
        while (p < tokens.length && (tokens[p].t === '_' || tokens[p].t === '^')) {
          const isSub = tokens[p].t === '_'; p++;
          const arg = readArg();
          if (isSub) atom.sub = arg; else atom.sup = arg;
        }
      }
      return atoms;
    }
    const out = [];
    while (p < tokens.length) { out.push(...parseSeq()); if (peek() && peek().t === '}') p++; }
    return out;
  }

  // Box model: w = width, asc/desc = extent above/below the baseline, draw(c, x, y) with y = baseline.
  function textBox(s, size, o) {
    const f = font(size, { italic: o.it, bold: o.b, family: MATH });
    mctx.font = f;
    const w = mctx.measureText(s).width;
    return {
      w, asc: size * 0.72, desc: size * 0.26,
      draw(c, x, y) { c.save(); c.font = f; c.fillStyle = col(o.color); c.textAlign = 'left'; c.textBaseline = 'alphabetic'; c.fillText(s, x, y); c.restore(); }
    };
  }
  function layoutSeq(atoms, size, st) {
    const parts = [];
    for (const a of atoms) {
      let box = a.base ? layout(a.base, size, st) : { w: 0, asc: 0, desc: 0, draw() {} };
      if (a.base && a.base.k === 'big' && (a.sup || a.sub)) box = limits(box, a, size, st);
      else if (a.sup || a.sub) box = scripts(box, a, size, st);
      const g = a.base && a.base.rel ? size * 0.28 : 0;
      parts.push({ box, g });
    }
    let x = 0, asc = 0, desc = 0; const placed = [];
    for (const pt of parts) {
      x += pt.g; placed.push([pt.box, x]); x += pt.box.w + pt.g;
      asc = Math.max(asc, pt.box.asc); desc = Math.max(desc, pt.box.desc);
    }
    return { w: x, asc, desc, draw(c, x0, y) { for (const [b, off] of placed) b.draw(c, x0 + off, y); } };
  }
  function scripts(bb, a, size, st) {
    const ss = size * 0.68, gap = size * 0.05, supY = size * 0.42, subY = size * 0.26;
    const sup = a.sup ? layout(a.sup, ss, st) : null;
    const sub = a.sub ? layout(a.sub, ss, st) : null;
    const sw = Math.max(sup ? sup.w : 0, sub ? sub.w : 0);
    return {
      w: bb.w + (sw ? sw + gap : 0),
      asc: Math.max(bb.asc, sup ? supY + sup.asc : 0),
      desc: Math.max(bb.desc, sub ? subY + sub.desc : 0),
      draw(c, x, y) {
        bb.draw(c, x, y);
        const sx = x + bb.w + gap * 0.5;
        if (sup) sup.draw(c, sx, y - supY);
        if (sub) sub.draw(c, sx, y + subY);
      }
    };
  }
  function limits(bb, a, size, st) {
    const ls = size * 0.7, gap = size * 0.06;
    const up = a.sup ? layout(a.sup, ls, st) : null;
    const lo = a.sub ? layout(a.sub, ls, st) : null;
    const w = Math.max(bb.w, up ? up.w : 0, lo ? lo.w : 0);
    const upY = -(bb.asc + gap + (up ? up.desc : 0));
    const loY = bb.desc + gap + (lo ? lo.asc : 0);
    return {
      w, asc: up ? -upY + up.asc : bb.asc, desc: lo ? loY + lo.desc : bb.desc,
      draw(c, x, y) {
        bb.draw(c, x + (w - bb.w) / 2, y);
        if (up) up.draw(c, x + (w - up.w) / 2, y + upY);
        if (lo) lo.draw(c, x + (w - lo.w) / 2, y + loY);
      }
    };
  }
  function layout(node, size, st) {
    switch (node.k) {
      case 't': return textBox(node.s, size, { it: node.it, b: node.b || st.b, color: st.color });
      case 'g': return layoutSeq(node.c, size, st);
      case 'sp': return { w: node.w * size, asc: 0, desc: 0, draw() {} };
      case 'big': return textBox(node.s, size * 1.45, { it: false, color: st.color });
      case 'col': return layout(node.c, size, { ...st, color: node.name });
      case 'frac': {
        const s2 = size * 0.86;
        const n = layout(node.n, s2, st), d = layout(node.d, s2, st);
        const pad = size * 0.16, axis = size * 0.31, gap = size * 0.1, lw = Math.max(1.5, size * 0.055);
        const w = Math.max(n.w, d.w) + pad * 2;
        const yN = -(axis + gap + n.desc), yD = d.asc + gap - axis;
        return {
          w, asc: -yN + n.asc, desc: yD + d.desc,
          draw(c, x, y) {
            n.draw(c, x + (w - n.w) / 2, y + yN);
            d.draw(c, x + (w - d.w) / 2, y + yD);
            c.save(); c.fillStyle = col(st.color); c.fillRect(x + pad * 0.2, y - axis - lw / 2, w - pad * 0.4, lw); c.restore();
          }
        };
      }
      case 'sqrt': {
        const b = layout(node.c, size, st);
        const sw = size * 0.6, pad = size * 0.08, top = b.asc + size * 0.14, lw = Math.max(1.5, size * 0.06);
        const w = sw + b.w + pad * 2;
        return {
          w, asc: top + lw, desc: Math.max(b.desc, size * 0.12),
          draw(c, x, y) {
            c.save(); c.strokeStyle = col(st.color); c.lineWidth = lw; c.lineJoin = 'miter';
            c.beginPath();
            c.moveTo(x + sw * 0.05, y - b.asc * 0.3);
            c.lineTo(x + sw * 0.3, y + Math.max(b.desc, size * 0.12) * 0.8);
            c.lineTo(x + sw * 0.62, y - top);
            c.lineTo(x + w, y - top);
            c.stroke(); c.restore();
            b.draw(c, x + sw + pad, y);
          }
        };
      }
      default: return { w: 0, asc: 0, desc: 0, draw() {} };
    }
  }
  const texCache = new Map();
  function texBox(src, size, color) {
    const key = src + '|' + size + '|' + (color || '');
    let b = texCache.get(key);
    if (!b) {
      b = layoutSeq(texParse(texTokens(src)), size, { color, b: false });
      if (texCache.size > 1200) texCache.clear();
      texCache.set(key, b);
    }
    return b;
  }
  // Draw a formula. (x, y) is the anchor point: align = left|center|right, anchor = mid|base.
  function tex(c, src, x, y, o = {}) {
    const size = o.size || 30;
    const b = texBox(src, size, o.color);
    let x0 = x;
    if (o.align === 'center') x0 = x - b.w / 2; else if (o.align === 'right') x0 = x - b.w;
    const base = o.anchor === 'base' ? y : y + (b.asc - b.desc) / 2;
    c.save(); c.globalAlpha *= o.alpha ?? 1; b.draw(c, x0, base); c.restore();
    return b.w;
  }
  const texW = (src, size = 30) => texBox(src, size).w;
  // Plain text or formula, chosen automatically.
  function lab(c, s, x, y, o = {}) {
    if (/[\\^_{]/.test(s)) return tex(c, s, x, y, { size: o.size || 22, align: o.align || 'center', color: o.color, alpha: o.alpha, anchor: 'mid' });
    return text(c, s, x, y, { size: o.size || 22, align: o.align || 'center', color: o.color, bold: o.bold, alpha: o.alpha });
  }

  /* ---------- shapes ---------- */
  function rrPath(c, x, y, w, h, r) {
    r = Math.max(0, Math.min(r, w / 2, h / 2));
    c.beginPath();
    c.moveTo(x + r, y);
    c.arcTo(x + w, y, x + w, y + h, r); c.arcTo(x + w, y + h, x, y + h, r);
    c.arcTo(x, y + h, x, y, r); c.arcTo(x, y, x + w, y, r);
    c.closePath();
  }
  function card(c, x, y, w, h, o = {}) {
    if (w <= 0 || h <= 0) return;
    c.save();
    c.globalAlpha *= o.alpha ?? 1;
    rrPath(c, x, y, w, h, o.r ?? 16);
    if (o.fill !== null) { c.fillStyle = col(o.fill || C.panel); c.fill(); }
    if (o.stroke) { c.strokeStyle = col(o.stroke); c.lineWidth = o.lw || 2; if (o.dash) c.setLineDash(o.dash); c.stroke(); }
    c.restore();
  }
  function arrow(c, x1, y1, x2, y2, o = {}) {
    const color = col(o.color || C.dim), lw = o.lw || 3, head = o.head ?? 14;
    const ang = Math.atan2(y2 - y1, x2 - x1);
    c.save();
    c.globalAlpha *= o.alpha ?? 1;
    c.strokeStyle = color; c.fillStyle = color; c.lineWidth = lw; c.lineCap = 'round';
    if (o.dash) c.setLineDash(o.dash);
    c.beginPath(); c.moveTo(x1, y1);
    c.lineTo(x2 - Math.cos(ang) * head * 0.6, y2 - Math.sin(ang) * head * 0.6);
    c.stroke(); c.setLineDash([]);
    if (head > 0) {
      c.beginPath(); c.moveTo(x2, y2);
      c.lineTo(x2 - head * Math.cos(ang - 0.42), y2 - head * Math.sin(ang - 0.42));
      c.lineTo(x2 - head * Math.cos(ang + 0.42), y2 - head * Math.sin(ang + 0.42));
      c.closePath(); c.fill();
    }
    c.restore();
  }
  function line(c, pts, o = {}) {
    if (pts.length < 2) return;
    c.save();
    c.globalAlpha *= o.alpha ?? 1;
    c.strokeStyle = col(o.color || C.acc); c.lineWidth = o.lw || 3; c.lineJoin = 'round'; c.lineCap = 'round';
    if (o.dash) c.setLineDash(o.dash);
    c.beginPath(); pts.forEach(([x, y], i) => (i ? c.lineTo(x, y) : c.moveTo(x, y)));
    c.stroke(); c.restore();
  }
  function pt(c, x, y, r, color = C.gold, a = 1) { c.save(); c.globalAlpha *= a; c.fillStyle = col(color); c.beginPath(); c.arc(x, y, r, 0, Math.PI * 2); c.fill(); c.restore(); }
  function glow(c, x, y, r, color = C.gold, a = 0.5) {
    const g = c.createRadialGradient(x, y, 0, x, y, r);
    g.addColorStop(0, alpha(color, a)); g.addColorStop(1, alpha(color, 0));
    c.save(); c.fillStyle = g; c.beginPath(); c.arc(x, y, r, 0, Math.PI * 2); c.fill(); c.restore();
  }
  // A dot travelling from (x1,y1) to (x2,y2); p in 0..1.
  function flowDot(c, x1, y1, x2, y2, p, color = C.gold, r = 7) {
    const x = lerp(x1, x2, p), y = lerp(y1, y2, p);
    glow(c, x, y, r * 4, color, 0.35); pt(c, x, y, r, color);
  }
  function pill(c, s, x, y, o = {}) {
    const size = o.size || 22, padX = o.padX ?? 20, h = o.h || Math.round(size * 1.9);
    const w = measure(s, size, { bold: o.bold }) + padX * 2;
    card(c, x - w / 2, y - h / 2, w, h, { fill: o.fill || C.panel2, stroke: o.stroke, lw: o.lw, r: h / 2, alpha: o.alpha });
    lab(c, s, x, y, { size, align: 'center', color: o.color || C.text, bold: o.bold, alpha: o.alpha });
    return w;
  }
  function block(c, x, y, w, h, title, o = {}) {
    card(c, x, y, w, h, { fill: o.fill || C.panel, stroke: o.stroke || C.line, lw: o.lw || 2.5, r: 16, alpha: o.alpha });
    if (o.bar) card(c, x, y + 10, 7, h - 20, { fill: o.bar, r: 4, alpha: o.alpha });
    const ty = o.sub ? y + h * 0.36 : y + h / 2;
    text(c, title, x + w / 2, ty, { size: o.size || 25, bold: true, align: 'center', color: o.color || C.text, alpha: o.alpha });
    if (o.sub) lab(c, o.sub, x + w / 2, y + h * 0.72, { size: o.ssize || 21, color: o.scolor || C.dim, alpha: o.alpha });
  }
  // Matrix brackets around a box.
  function bracket(c, x, y, w, h, o = {}) {
    const t = o.t || 9;
    c.save(); c.strokeStyle = col(o.color || C.dim); c.lineWidth = o.lw || 3;
    c.beginPath();
    c.moveTo(x + t, y); c.lineTo(x, y); c.lineTo(x, y + h); c.lineTo(x + t, y + h);
    c.moveTo(x + w - t, y); c.lineTo(x + w, y); c.lineTo(x + w, y + h); c.lineTo(x + w - t, y + h);
    c.stroke(); c.restore();
  }

  /* ---------- data displays ---------- */
  // Grid of numbers. M = rows of numbers, (x,y) = top-left, cw/ch = cell size.
  // o: {max, d, size, cmap(v,i,j)->fill, ink(v)->text colour, show(i,j)->0..1,
  //     hl:[[i,j,colour]], rows:[labels], cols:[labels], neg, pos}
  function grid(c, M, x, y, cw, ch, o = {}) {
    const R = M.length, Cn = M[0].length;
    const m = o.max ?? Math.max(...M.flat().map(Math.abs), 1e-9);
    const d = o.d ?? 2, size = o.size ?? Math.min(20, ch * 0.42, cw * 0.3);
    for (let i = 0; i < R; i++) for (let j = 0; j < Cn; j++) {
      const v = M[i][j], a = o.show ? o.show(i, j) : 1;
      const fx = x + j * cw + 2, fy = y + i * ch + 2, fw = cw - 4, fh = ch - 4;
      card(c, fx, fy, fw, fh, { fill: C.panel2, r: 7 });
      if (a > 0) {
        const fill = o.cmap ? o.cmap(v, i, j) : divMap(v, m, o.neg, o.pos);
        card(c, fx, fy, fw, fh, { fill, r: 7, alpha: a });
        const ink = o.ink ? o.ink(v) : inkFor(v, m);
        text(c, fmt(v, d), fx + fw / 2, fy + fh / 2, { size, align: 'center', color: ink, alpha: a });
      }
    }
    (o.hl || []).forEach(([i, j, color, lw]) => {
      c.save(); c.strokeStyle = col(color); c.lineWidth = lw || 4;
      rrPath(c, x + j * cw + 1, y + i * ch + 1, cw - 2, ch - 2, 8); c.stroke(); c.restore();
    });
    (o.rows || []).forEach((s, i) => lab(c, s, x - 14, y + i * ch + ch / 2, { size: o.lsize || 20, align: 'right', color: o.lcolor || C.dim }));
    (o.cols || []).forEach((s, j) => lab(c, s, x + j * cw + cw / 2, y - 16, { size: o.lsize || 20, color: o.lcolor || C.dim }));
  }
  // A vector drawn as a single row of cells.
  const vec = (c, v, x, y, cw, ch, o = {}) => grid(c, [v], x, y, cw, ch, o);

  // Vertical bars with a baseline at y.
  function bars(c, vals, x, y, w, h, o = {}) {
    const n = vals.length, gap = o.gap ?? 16, bw = (w - gap * (n - 1)) / n;
    const mx = o.max ?? Math.max(...vals, 1e-9);
    vals.forEach((v, i) => {
      const s = o.show ? o.show(i) : 1;
      const hh = clamp(v / mx, 0, 1) * h * s;
      const bx = x + i * (bw + gap);
      card(c, bx, y - hh, bw, hh, { fill: Array.isArray(o.colors) ? o.colors[i] : (o.color || C.q), r: 6, alpha: o.alpha ?? 1 });
      if (o.fmt && s > 0.5) text(c, o.fmt(v), bx + bw / 2, y - hh - 18, { size: o.vsize || 20, align: 'center', color: o.vcolor || C.text, alpha: s });
      if (o.labels) lab(c, o.labels[i], bx + bw / 2, y + 24, { size: o.lsize || 20, color: o.lcolor || C.dim });
    });
  }
  // Horizontal bars with labels on the left and values on the right.
  function hbars(c, vals, labels, x, y, w, rowH, o = {}) {
    const lw = o.labelW ?? 150, valW = o.valW ?? 96, bx = x + lw, bw = w - lw - valW;
    const mx = o.max ?? Math.max(...vals.map(Math.abs), 1e-9);
    vals.forEach((v, i) => {
      const yy = y + i * rowH + rowH / 2, s = o.show ? o.show(i) : 1;
      lab(c, labels[i], x + lw - 16, yy, { size: o.lsize || 22, align: 'right', color: (o.lcolors && o.lcolors[i]) || C.text, alpha: s });
      const len = clamp(Math.abs(v) / mx, 0, 1) * bw * s;
      card(c, bx, yy - rowH * 0.3, Math.max(len, 2), rowH * 0.6, { fill: (o.colors && o.colors[i]) || (v >= 0 ? C.q : C.hot), r: 6, alpha: s });
      if (s > 0.5) text(c, fmt(v, o.d ?? 2), bx + bw + 16, yy, { size: 22, color: C.text, alpha: s });
    });
  }
  // A 100% stacked bar.
  function stack(c, vals, colors, labels, x, y, w, h) {
    const tot = sum(vals); let xx = x;
    vals.forEach((v, i) => {
      const ww = (v / tot) * w;
      if (ww < 0.5) return;
      card(c, xx, y, ww, h, { fill: colors[i], r: 0 });
      if (labels && labels[i] && ww > 40) text(c, labels[i], xx + ww / 2, y + h / 2, { size: 18, align: 'center', color: C.ink, bold: true });
      xx += ww;
    });
  }
  // Cartesian plot frame with ticks. Returns {X, Y} mapping data -> pixels.
  function plot(c, bx, by, bw, bh, o = {}) {
    const x0 = o.xmin ?? 0, x1 = o.xmax ?? 1, y0 = o.ymin ?? 0, y1 = o.ymax ?? 1;
    const X = (v) => bx + ((v - x0) / (x1 - x0)) * bw;
    const Y = (v) => by + bh - ((v - y0) / (y1 - y0)) * bh;
    c.save();
    c.strokeStyle = C.line; c.lineWidth = 1;
    (o.xt || []).forEach((v) => { c.beginPath(); c.moveTo(X(v), by); c.lineTo(X(v), by + bh); c.stroke(); });
    (o.yt || []).forEach((v) => { c.beginPath(); c.moveTo(bx, Y(v)); c.lineTo(bx + bw, Y(v)); c.stroke(); });
    c.restore();
    c.save(); c.strokeStyle = C.dim; c.lineWidth = 2;
    c.beginPath(); c.moveTo(bx, by); c.lineTo(bx, by + bh); c.lineTo(bx + bw, by + bh); c.stroke(); c.restore();
    (o.xt || []).forEach((v) => lab(c, o.fx ? o.fx(v) : fmt(v, 1), X(v), by + bh + 22, { size: 19, color: C.dim }));
    (o.yt || []).forEach((v) => lab(c, o.fy ? o.fy(v) : fmt(v, 1), bx - 12, Y(v), { size: 19, align: 'right', color: C.dim }));
    if (o.xlabel) lab(c, o.xlabel, bx + bw, by + bh + 50, { size: 22, align: 'right', color: C.text });
    if (o.ylabel) lab(c, o.ylabel, bx, by - 24, { size: 22, align: 'left', color: C.text });
    return { X, Y };
  }
  // Histogram as density (area = 1). Optional normal curve overlay.
  function hist(c, data, bx, by, bw, bh, o = {}) {
    const lo = o.lo, hi = o.hi, nb = o.bins || 40, bwid = (hi - lo) / nb;
    const cnt = new Array(nb).fill(0);
    for (const v of data) { const i = Math.floor((v - lo) / bwid); if (i >= 0 && i < nb) cnt[i]++; }
    const dens = cnt.map((k) => k / (data.length * bwid));
    const dmax = o.dmax ?? Math.max(...dens, 1e-9) * 1.1;
    const X = (v) => bx + ((v - lo) / (hi - lo)) * bw;
    const Y = (d) => by + bh - (d / dmax) * bh;
    c.save(); c.globalAlpha *= o.alpha ?? 0.9; c.fillStyle = col(o.color || C.q);
    dens.forEach((d, i) => { const x0 = X(lo + i * bwid), x1 = X(lo + (i + 1) * bwid); c.fillRect(x0 + 1, Y(d), Math.max(1, x1 - x0 - 2), by + bh - Y(d)); });
    c.restore();
    if (o.normal) {
      const pts = [];
      for (let k = 0; k <= 200; k++) { const v = lo + ((hi - lo) * k) / 200; pts.push([X(v), Y(gpdf(v, o.normal.mu, o.normal.sd))]); }
      line(c, pts, { color: o.ncolor || C.gold, lw: 3.5 });
    }
    return { X, Y, dmax };
  }

  /* ---------- scene runner ---------- */
  // Chapter labels and the notes heading are plain text: turn $...$ titles into Unicode.
  function plainTitle(s) {
    return s.replace(/_k/g, '\u2096').replace(/\\sqrt\{([^}]*)\}/g, '\u221A$1').replace(/\\/g, '').replace(/\$/g, '');
  }
  function create(opts) {
    const scenes = opts.scenes;
    let acc = 0;
    scenes.forEach((s) => { s.start = acc; acc += s.dur; });
    const total = acc;
    const host = document.querySelector(opts.host);
    const videoMode = new URLSearchParams(location.search).get('video') === '1';
    host.classList.add('kit');
    if (videoMode) host.classList.add('video');
    host.innerHTML = `
      <div class="stage-wrap"><canvas class="stage" role="img" aria-label="${opts.title || 'Animation'}"></canvas></div>
      <div class="ctrl" aria-label="Playback controls">
        <button type="button" data-act="restart" title="Restart (R)">Restart</button>
        <button type="button" data-act="back" title="Previous scene (←)">◀ Prev</button>
        <button type="button" data-act="play" class="play" title="Play / pause (Space)">▶ Play</button>
        <button type="button" data-act="fwd" title="Next scene (→)">Next ▶</button>
        <input type="range" class="scrub" min="0" max="${total}" step="10" value="0" aria-label="Timeline">
        <span class="time">00:00 / ${clock(total)}</span>
        <select class="speed" aria-label="Playback speed">
          <option value="0.5">0.5×</option><option value="1" selected>1×</option><option value="1.5">1.5×</option><option value="2">2×</option>
        </select>
      </div>
      <nav class="chapters">${scenes.map((s, i) => `<button type="button" data-scene="${i}">${i + 1}. ${plainTitle(s.title)}</button>`).join('')}</nav>
      <section class="notes"><h2></h2><div class="n-body"></div></section>`;
    const canvas = host.querySelector('canvas');
    const ctx = canvas.getContext('2d');
    const playBtn = host.querySelector('[data-act="play"]');
    const scrub = host.querySelector('.scrub');
    const timeEl = host.querySelector('.time');
    const speedSel = host.querySelector('.speed');
    const chapterBtns = [...host.querySelectorAll('[data-scene]')];
    const notesTitle = host.querySelector('.notes h2');
    const notesBody = host.querySelector('.n-body');

    let T = 0, playing = false, last = 0, speed = 1, dragging = false, lastScene = -1;

    function fit() {
      const cssW = Math.min(canvas.parentElement.clientWidth, W);
      const dpr = Math.min(2, window.devicePixelRatio || 1);
      canvas.style.width = cssW + 'px';
      canvas.style.height = (cssW * H / W) + 'px';
      canvas.width = Math.round(cssW * dpr);
      canvas.height = Math.round(cssW * dpr * H / W);
    }
    function sceneIndex(t) { let i = 0; for (let k = 0; k < scenes.length; k++) if (scenes[k].start <= t) i = k; return i; }

    function paintBg(c) {
      const g = c.createLinearGradient(0, 0, 0, H);
      g.addColorStop(0, C.bg1); g.addColorStop(1, C.bg0);
      c.fillStyle = g; c.fillRect(0, 0, W, H);
      c.fillStyle = 'rgba(160,180,255,0.07)';
      for (let x = 40; x < W; x += 40) for (let y = 40; y < H; y += 40) c.fillRect(x, y, 2, 2);
    }
    function chrome(c, i, s, lt, t) {
      text(c, opts.part || '', 48, 24, { size: 17, color: C.faint, bold: true });
      text(c, `SCENE ${i + 1} / ${scenes.length}   ·   ${clock(t)} / ${clock(total)}`, W - 48, 24, { size: 17, color: C.dim, align: 'right' });
      card(c, 48, 42, W - 96, 4, { fill: C.line, r: 2 });
      card(c, 48, 42, (W - 96) * (t / total), 4, { fill: s.accent || C.acc, r: 2 });
      rich(c, s.title, 48, 84, { size: 36, bold: true });
      const cap = s.caption || '';
      const toks = richTokens(cap, 24);
      const shownN = Math.ceil(toks.length * clamp(lt / 1400));   // typewriter reveal, token by token
      const lines = richLines(toks.slice(0, shownN), W - 80 - 90);
      card(c, 40, 622, W - 80, 80, { fill: 'rgba(12,19,38,0.95)', stroke: C.line, lw: 1.5, r: 16 });
      card(c, 40, 622, 7, 80, { fill: s.accent || C.acc, r: 3 });
      richDraw(c, lines, 72, 662 - (lines.length - 1) * 16, 32, { size: 24, color: C.text });
    }
    function draw(t) {
      t = clamp(t, 0, total);
      const i = sceneIndex(t), s = scenes[i], lt = t - s.start;
      const k = canvas.width / W;
      ctx.setTransform(k, 0, 0, k, 0, 0);
      ctx.save();
      paintBg(ctx);
      ctx.save(); ctx.beginPath(); ctx.rect(0, 112, W, 500); ctx.clip();
      s.draw(ctx, lt, clamp(lt / s.dur));
      ctx.restore();
      chrome(ctx, i, s, lt, t);
      if (lt < 500) { ctx.fillStyle = `rgba(10,15,31,${1 - lt / 500})`; ctx.fillRect(0, 0, W, H); }
      ctx.restore();
      ui(i, t);
    }
    function ui(i, t) {
      if (videoMode) return;
      playBtn.textContent = playing ? '❚❚ Pause' : '▶ Play';
      if (!dragging) scrub.value = t;
      timeEl.textContent = `${clock(t)} / ${clock(total)}`;
      chapterBtns.forEach((b, k) => b.classList.toggle('on', k === i));
      if (i !== lastScene) {
        lastScene = i;
        notesTitle.textContent = `${i + 1}. ${plainTitle(scenes[i].title)}`;
        notesBody.innerHTML = scenes[i].notes || '';
      }
    }
    function loop(now) {
      if (!playing) return;
      T += (now - last) * speed; last = now;
      if (T >= total) { T = total; playing = false; }
      draw(T);
      if (playing) requestAnimationFrame(loop);
    }
    function setPlaying(v) {
      if (v === playing) return;
      if (v && T >= total) T = 0;
      playing = v; last = performance.now();
      if (v) requestAnimationFrame(loop); else draw(T);
    }
    function seek(t) { playing = false; T = clamp(t, 0, total); draw(T); }
    function step(dir) {
      const j = clamp(sceneIndex(T) + dir, 0, scenes.length - 1);
      seek(scenes[j].start);
    }

    host.querySelector('.ctrl').addEventListener('click', (e) => {
      const act = e.target.closest('[data-act]'); if (!act) return;
      const a = act.dataset.act;
      if (a === 'play') setPlaying(!playing);
      if (a === 'restart') seek(0);
      if (a === 'back') step(-1);
      if (a === 'fwd') step(1);
    });
    chapterBtns.forEach((b) => b.addEventListener('click', () => seek(scenes[+b.dataset.scene].start)));
    scrub.addEventListener('pointerdown', () => { dragging = true; });
    window.addEventListener('pointerup', () => { dragging = false; });
    scrub.addEventListener('input', () => seek(+scrub.value));
    speedSel.addEventListener('change', () => { speed = +speedSel.value; });
    window.addEventListener('keydown', (e) => {
      if (['INPUT', 'SELECT', 'BUTTON', 'TEXTAREA'].includes(e.target.tagName)) return;
      if (e.code === 'Space') { e.preventDefault(); setPlaying(!playing); }
      else if (e.key === 'ArrowRight') step(1);
      else if (e.key === 'ArrowLeft') step(-1);
      else if (e.key === 'r' || e.key === 'R') seek(0);
    });
    window.addEventListener('resize', () => { fit(); draw(T); });

    fit();
    draw(0);
    if (videoMode) setPlaying(true);
    // Exposed for the recorder: window.Kit.seek(ms) renders an exact instant.
    window.Kit = { seek, play: () => setPlaying(true), pause: () => setPlaying(false), total, scenes };
    return window.Kit;
  }

  /* ---------- public API ---------- */
  window.AK = {
    create, C, W, H, col, clamp, lerp, ease, seg, sm, sum, vdot, matmul, transpose, softmax, mean, std, norm,
    gpdf, rng, randn, fmt, clock, mix, alpha, font, measure, text, para, wrap, tex, texW, lab, card, arrow,
    rich, richTokens, richLines, richDraw,
    line, pt, glow, flowDot, pill, block, bracket, grid, vec, bars, hbars, stack, plot, hist, divMap, seqMap, inkFor
  };
})();
