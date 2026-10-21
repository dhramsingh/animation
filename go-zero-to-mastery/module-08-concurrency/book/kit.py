"""Page kit for the Module 8 graphic book, built on ManimGL.

Each book page is a ManimGL Scene (subclass of `Page`) rendered to one
still PNG. This module provides the building blocks: wrapped text with a
tiny inline markup, Go listings with line markers, terminals, tables,
callouts, and the book's icon set (gopher, G/M/P tokens, channels, locks).

Inline markup understood by `txt()`:
    **bold**        __italic__        `code`        {red|coloured text}
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

from manimlib import *  # noqa: F401,F403
from manimlib.mobject.svg.string_mobject import StringMobject
from manimlib.mobject.svg.svg_mobject import SVGMobject

import theme as T
from theme import *  # noqa: F401,F403

# ---------------------------------------------------------------------------
# Compatibility patches for manimgl 1.7.2 (the PyPI release).
# MarkupText calls two helpers that were renamed in that release. Markup is
# still validated inside markup_to_svg, so skipping the first is safe.
# ---------------------------------------------------------------------------
MarkupText.validate_markup_string = lambda self, s: None
StringMobject.get_file_path_by_content = (
    lambda self, content: self.get_svg_string_by_content(content))
SVGMobject.mobjects_from_file = (
    lambda self, svg_string: SVGMobject.mobjects_from_svg_string(self, svg_string))

FONT_FEATURES = {"font_features": "liga=0,dlig=0,clig=0,hlig=0,calt=0"}
BLOCK_COLOR = "#FE00FE"   # marker colour for hidden layout glyphs


class FastMarkup(MarkupText):
    """MarkupText without ManimGL's second 'labelled' render pass.
    Colours come straight from the markup; part selection is not needed."""

    def mobjects_from_svg_string(self, svg_string):
        subs = SVGMobject.mobjects_from_svg_string(self, svg_string)
        for sm in subs:
            sm.label = 0
        return subs


def _mk(body, **kw):
    kw.setdefault("fill_color", None)
    kw.setdefault("global_config", FONT_FEATURES)
    kw.setdefault("isolate", ())
    return FastMarkup(body, **kw)


FW, FH = FRAME_WIDTH, FRAME_HEIGHT
X0, X1 = -FW / 2 + 0.5, FW / 2 - 0.5     # content left / right
Y0, Y1 = 2.2, -3.52                      # content top / bottom
CW = X1 - X0                              # content width (about 13.2)
WRAP_K = 0.735                            # Pango wrap width correction

BOOK_DIR = Path(__file__).resolve().parent
EX_DIR = BOOK_DIR.parent / "examples"


def src(name, file="main.go", lines=None, drop_directive=True):
    """Source of an example program, optionally a 1-based inclusive line
    range (a, b). The //run: directive line is dropped."""
    text = (EX_DIR / name / file).read_text().rstrip("\n").expandtabs(4)
    ls = text.split("\n")
    if drop_directive and ls and ls[0].startswith("//run:"):
        ls = ls[1:]
    if lines:
        a, b = lines
        ls = ls[a - 1:b]
    return "\n".join(ls)


def nums(name, pattern, cast=float):
    """All regex captures (group 1) from an example's output, as numbers."""
    text = (EX_DIR / name / "output.txt").read_text()
    return [cast(m) for m in re.findall(pattern, text)]


def out(name, lines=None, first=None, drop=()):
    """Captured output of an example (first line is the command)."""
    ls = (EX_DIR / name / "output.txt").read_text().rstrip("\n").split("\n")
    if lines:
        a, b = lines
        ls = ls[a - 1:b]
    if first:
        ls = ls[:first]
    ls = [l for i, l in enumerate(ls) if i not in drop]
    return "\n".join(l.expandtabs(4) for l in ls)
_PAGES_FILE = BOOK_DIR / "pages.json"
PAGES = json.loads(_PAGES_FILE.read_text()) if _PAGES_FILE.exists() else {}


def P(x, y):
    return np.array([x, y, 0.0])


# ---------------------------------------------------------------------------
# Text
# ---------------------------------------------------------------------------
def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def md(s: str, code_color: str = T.INLINE_CODE) -> str:
    """Mini markdown -> Pango markup."""
    out = []
    for part in re.split(r"(`[^`]+`)", s):
        if len(part) >= 2 and part[0] == "`" and part[-1] == "`":
            out.append(
                f'<span font_family="{T.MONO}" foreground="{code_color}">'
                f"{esc(part[1:-1]).replace(' ', chr(160))}</span>")
            continue
        q = esc(part)
        q = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", q)
        q = re.sub(r"__(.+?)__", r"<i>\1</i>", q)
        q = re.sub(
            r"\{(#?\w+)\|(.+?)\}",
            lambda m: f'<span foreground="{T.NAMED.get(m.group(1), m.group(1))}">'
                      f"{m.group(2)}</span>",
            q)
        out.append(q)
    return "".join(out)


def txt(s, size=T.SIZE_BODY, color=T.TEXT, width=None, font=T.SANS,
        weight="NORMAL", lsh=None, align="LEFT", markup=True, mono=False,
        opacity=1.0):
    """Wrapped, left-aligned text. `width` is in frame units."""
    if mono:
        font = T.MONO
    body = md(s) if markup else esc(s)
    kw = {}
    if width is not None:
        kw["line_width"] = width * WRAP_K
    t = _mk(body, font=font, font_size=size, weight=weight,
            alignment=align, lsh=lsh, base_color=color, **kw)
    if opacity < 1:
        t.set_opacity(opacity)
    return t


def bold(s, size=T.SIZE_BODY, color=T.TEXT, **kw):
    return txt(s, size=size, color=color, weight="BOLD", **kw)


def heading(s, size=T.SIZE_H2, color=T.TEXT, **kw):
    return txt(s, size=size, color=color, weight="BOLD", **kw)


def caption(s, size=T.SIZE_TINY, color=T.MUTED, **kw):
    return txt(s, size=size, color=color, **kw)


def label(s, size=T.SIZE_SMALL, color=T.TEXT, weight="BOLD", **kw):
    return txt(s, size=size, color=color, weight=weight, align="CENTER", **kw)


def mono(s, size=T.SIZE_SMALL, color=T.TEXT, weight="NORMAL", **kw):
    return txt(s, size=size, color=color, font=T.MONO, weight=weight, markup=False, **kw)


def first_line_y(t, size):
    """y of the middle of the first line of a text block (for bullets)."""
    return t.get_top()[1] - 0.0047 * size


def bullets(items, width, size=T.SIZE_BODY, color=T.TEXT, marker_color=T.GO,
            gap=0.16, marker="dot", indent=0.34):
    """Bulleted list. marker: dot | num | check | cross | arrow | none.
    An item may be a (marker_color, text) tuple to colour one bullet."""
    rows = VGroup()
    for i, it in enumerate(items):
        mc = marker_color
        custom = None
        if isinstance(it, tuple):
            if isinstance(it[0], Mobject):
                custom, it = it
            else:
                mc, it = it
        t = txt(it, size=size, color=color, width=width - indent)
        y = first_line_y(t, size)
        if custom is not None:
            m = custom
        elif marker == "dot":
            m = Dot(radius=0.042 * size / 20, fill_color=mc)
        elif marker == "num":
            m = badge(str(i + 1), mc, r=0.13 * size / 20, size=size - 6)
        elif marker == "check":
            m = check_mark(mc, s=0.115 * size / 20)
        elif marker == "cross":
            m = cross_mark(mc, s=0.14 * size / 20)
        elif marker == "arrow":
            m = Triangle(fill_color=mc, fill_opacity=1, stroke_width=0)
            m.rotate(-PI / 2).set_height(0.12 * size / 20)
        else:
            m = VectorizedPoint()
        m.move_to(P(t.get_left()[0] - indent / 2 - 0.02, y))
        rows.add(VGroup(m, t))
    rows.arrange(DOWN, aligned_edge=LEFT, buff=gap)
    return rows


# ---------------------------------------------------------------------------
# Boxes, pills, badges
# ---------------------------------------------------------------------------
def rbox(w, h, color=T.STROKE, fill=T.PANEL, fill_opacity=1.0, radius=0.14,
         stroke_width=2.0, stroke_opacity=1.0):
    r = RoundedRectangle(width=w, height=h, corner_radius=min(radius, h / 2, w / 2))
    r.set_fill(fill, fill_opacity)
    r.set_stroke(color, stroke_width, stroke_opacity)
    return r


def box(w, h, color=T.STROKE, fill=T.PANEL, fill_opacity=1.0, stroke_width=2.0,
        stroke_opacity=1.0):
    r = Rectangle(width=w, height=h)
    r.set_fill(fill, fill_opacity)
    r.set_stroke(color, stroke_width, stroke_opacity)
    return r


def panel(mob, pad=0.25, color=T.STROKE, fill=T.PANEL, fill_opacity=1.0,
          radius=0.16, stroke_width=2.0, min_w=0, min_h=0, padx=None, pady=None):
    px = pad if padx is None else padx
    py = pad if pady is None else pady
    w = max(mob.get_width() + 2 * px, min_w)
    h = max(mob.get_height() + 2 * py, min_h)
    b = rbox(w, h, color=color, fill=fill, fill_opacity=fill_opacity,
             radius=radius, stroke_width=stroke_width)
    b.move_to(mob)
    return VGroup(b, mob)


def pill(s, color=T.GO, size=T.SIZE_TINY, filled=True, text_color=None,
         padx=0.16, pady=0.07, mono_font=False, weight="BOLD"):
    t = txt(s, size=size, color=text_color or (T.BG if filled else color),
            weight=weight, font=T.MONO if mono_font else T.SANS)
    h = t.get_height() + 2 * pady
    h = max(h, 0.0105 * size + 2 * pady)
    b = rbox(t.get_width() + 2 * padx, h, color=color,
             fill=color, fill_opacity=1.0 if filled else 0.12,
             radius=h / 2, stroke_width=1.5)
    t.move_to(b)
    return VGroup(b, t)


def badge(s, color=T.GO, r=0.16, size=None, text_color=None, filled=True):
    c = Circle(radius=r)
    c.set_fill(color, 1.0 if filled else 0.15).set_stroke(color, 2)
    t = txt(s, size=size or int(r * 95), color=text_color or (T.BG if filled else color),
            weight="BOLD", align="CENTER")
    t.move_to(c)
    return VGroup(c, t)


def check_mark(color=T.GREEN, s=0.16):
    m = VMobject().set_points_as_corners([P(-0.5, 0), P(-0.15, -0.38), P(0.55, 0.45)])
    m.set_stroke(color, 4).scale(s / 0.5)
    return m


def cross_mark(color=T.RED, s=0.14):
    a = Line(P(-1, -1), P(1, 1)).set_stroke(color, 4)
    b = Line(P(-1, 1), P(1, -1)).set_stroke(color, 4)
    return VGroup(a, b).scale(s / 2)


def hline(x0, x1, y, color=T.STROKE, width=1.5, opacity=1.0):
    return Line(P(x0, y), P(x1, y)).set_stroke(color, width, opacity)


def vline(x, y0, y1, color=T.STROKE, width=1.5, opacity=1.0):
    return Line(P(x, y0), P(x, y1)).set_stroke(color, width, opacity)


def dashed(a, b, color=T.TEXT2, width=2.0, dash=0.08, opacity=1.0):
    d = DashedLine(a, b, dash_length=dash)
    d.set_stroke(color, width, opacity)
    return d


# ---------------------------------------------------------------------------
# Arrows
# ---------------------------------------------------------------------------
def arrow(a, b, color=T.TEXT2, thick=3.0, buff=0.06, arc=0.0, tip=4.0):
    return Arrow(a, b, buff=buff, path_arc=arc, fill_color=color,
                 thickness=thick, tip_width_ratio=tip,
                 max_tip_length_to_length_ratio=0.35)


def darrow(a, b, color=T.TEXT2, thick=3.0, buff=0.06):
    """Double-headed arrow."""
    g = VGroup(arrow(a, b, color, thick, buff), arrow(b, a, color, thick, buff))
    return g


def dashed_arrow(a, b, color=T.TEXT2, width=2.5, dash=0.09, tip_len=0.16):
    a, b = np.array(a, dtype=float), np.array(b, dtype=float)
    d = b - a
    n = np.linalg.norm(d)
    u = d / n if n else RIGHT
    end = b - u * tip_len * 0.9
    line = dashed(a, end, color, width, dash)
    tip = Triangle(fill_color=color, fill_opacity=1, stroke_width=0)
    tip.set_height(tip_len).rotate(np.arctan2(u[1], u[0]) - PI / 2)
    tip.move_to(b - u * tip_len / 2)
    return VGroup(line, tip)


def arrow_label(arr, s, size=T.SIZE_TINY, color=T.TEXT2, side=UP, buff=0.08, **kw):
    t = txt(s, size=size, color=color, **kw)
    t.next_to(arr, side, buff=buff)
    return t


def elbow_arrow(points, color=T.TEXT2, width=3.0, tip_len=0.16):
    """Polyline through points ending in an arrow tip."""
    pts = [np.array(p, dtype=float) for p in points]
    last, prev = pts[-1], pts[-2]
    u = (last - prev) / max(np.linalg.norm(last - prev), 1e-6)
    pts2 = pts[:-1] + [last - u * tip_len * 0.9]
    line = VMobject().set_points_as_corners(pts2).set_stroke(color, width)
    tip = Triangle(fill_color=color, fill_opacity=1, stroke_width=0)
    tip.set_height(tip_len).rotate(np.arctan2(u[1], u[0]) - PI / 2)
    tip.move_to(last - u * tip_len / 2)
    return VGroup(line, tip)


# ---------------------------------------------------------------------------
# Callouts and bubbles
# ---------------------------------------------------------------------------
CALLOUTS = {
    "key": (T.GO, "KEY IDEA", "★"),
    "warn": (T.RED, "PITFALL", "!"),
    "tip": (T.GREEN, "PRO TIP", "✓"),
    "hood": (T.VIOLET, "UNDER THE HOOD", "⚙"),
    "version": (T.BLUE, "GO VERSION NOTE", "v"),
    "def": (T.AMBER, "DEFINITION", "≡"),
    "try": (T.PINK, "TRY IT", "▶"),
    "rule": (T.YELLOW, "RULE", "§"),
    "q": (T.TEAL, "THINK ABOUT IT", "?"),
    "note": (T.TEXT2, "NOTE", "i"),
}


def callout(kind, body, width=6.0, title=None, size=T.SIZE_SMALL, body_color=T.TEXT,
            inline=False):
    color, lab, glyph = CALLOUTS[kind]
    if inline:
        content = txt(f"{{{color}|**{title or lab}**}}   {body}", size=size, color=body_color,
                      width=width - 0.75)
        h = content.get_height() + 0.3
    else:
        head = txt(f"**{title or lab}**", size=size - 2, color=color)
        b = txt(body, size=size, color=body_color, width=width - 0.75)
        content = VGroup(head, b).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        h = content.get_height() + 0.36
    bx = rbox(width, h, color=color, fill=color, fill_opacity=0.08,
              radius=0.12, stroke_width=1.6)
    bx.set_stroke(color, 1.6, 0.55)
    bar = Rectangle(width=0.07, height=h - 0.02).set_fill(color, 1).set_stroke(width=0)
    bar.move_to(bx.get_left() + RIGHT * 0.035)
    ic = badge(glyph, color, r=0.15, size=15)
    if inline:
        content.move_to(bx.get_corner(UL) + P(0.62, -0.15), aligned_edge=UL)
        ic.move_to(P(bx.get_left()[0] + 0.36, first_line_y(content, size)))
    else:
        ic.move_to(bx.get_corner(UL) + P(0.36, -0.29))
        content.move_to(bx.get_corner(UL) + P(0.62, -0.18), aligned_edge=UL)
    return VGroup(bx, bar, ic, content)


def bubble(s, width=3.2, size=T.SIZE_SMALL, color=T.TEXT, fill=T.PANEL2,
           stroke=T.STROKE2, tail="down", tail_x=-0.5, tail_len=0.35, tail_dx=-0.2):
    """Speech bubble. tail: down | up | left | right; tail_x is the offset of
    the tail base from the centre of that edge; tail_dx skews the tip."""
    t = txt(s, size=size, color=color, width=width - 0.4)
    w, h = width, t.get_height() + 0.34
    b = rbox(w, h, color=stroke, fill=fill, radius=0.18)
    t.move_to(b)
    c = b.get_center()
    if tail in ("down", "up"):
        sgn = -1 if tail == "down" else 1
        y = c[1] + sgn * h / 2
        b1, b2 = P(c[0] + tail_x - 0.16, y), P(c[0] + tail_x + 0.16, y)
        tip = P(c[0] + tail_x + tail_dx, y + sgn * tail_len)
    else:
        sgn = -1 if tail == "left" else 1
        x = c[0] + sgn * w / 2
        b1, b2 = P(x, c[1] + tail_x - 0.14), P(x, c[1] + tail_x + 0.14)
        tip = P(x + sgn * tail_len, c[1] + tail_x + tail_dx)
    tri = Polygon(b1, b2, tip).set_fill(fill, 1).set_stroke(stroke, 2)
    cover = Line(b1 + (b2 - b1) * 0.06, b2 - (b2 - b1) * 0.06).set_stroke(fill, 5)
    return VGroup(tri, b, cover, t)


# ---------------------------------------------------------------------------
# Code listings and terminals
# ---------------------------------------------------------------------------
_PKGS = {"fmt", "sync", "time", "context", "runtime", "os", "errors", "atomic",
         "http", "errgroup", "log", "rand", "strings", "io", "net", "signal",
         "pprof", "trace", "debug", "testing", "synctest", "semaphore",
         "strconv", "math", "sort", "bufio", "slices", "maps", "iter", "unsafe"}
_KW_EXTRA = {"chan", "go", "select", "defer", "func", "range"}


def _go_markup_lines(src, lang="go"):
    from pygments.lexers import get_lexer_by_name
    from pygments.token import Token
    toks = list(get_lexer_by_name(lang).get_tokens(src))
    lines, cur = [], []

    def col(i, tt, v):
        if v == "<-":
            return T.SYN["arrow"]
        if v in _KW_EXTRA:
            return T.SYN["keyword"]
        if tt in Token.Comment:
            return T.SYN["comment"]
        if tt in Token.Literal.String:
            return T.SYN["string"]
        if tt in Token.Literal.Number:
            return T.SYN["number"]
        if tt in Token.Keyword.Type:
            return T.SYN["type"]
        if tt in Token.Keyword:
            return T.SYN["keyword"]
        if tt in Token.Name.Builtin:
            return T.SYN["builtin"]
        if tt in Token.Name:
            nxt = toks[i + 1][1] if i + 1 < len(toks) else ""
            prv = toks[i - 1][1] if i > 0 else ""
            if v in _PKGS and nxt == ".":
                return T.SYN["package"]
            if nxt == "(" or nxt.startswith("("):
                return T.SYN["func"]
            if prv == "." and v[:1].isupper():
                return T.SYN["type"]
            return T.SYN["text"]
        return T.SYN["operator"]

    for i, (tt, v) in enumerate(toks):
        c = col(i, tt, v)
        pieces = v.split("\n")
        for k, piece in enumerate(pieces):
            if k > 0:
                lines.append(cur)
                cur = []
            if piece:
                cur.append((c, piece))
    if cur:
        lines.append(cur)
    return lines


def _plain_markup_lines(src, color_fn):
    out = []
    for line in src.split("\n"):
        out.append(color_fn(line))
    return out


def _term_color(line):
    if line.startswith("$ "):
        return [(T.GREEN, "$ "), (T.TEXT, line[2:])]
    low = line.lower()
    if low.startswith(("panic", "fatal error", "warning: data race", "==================")) \
            or "deadlock" in low or low.startswith("goroutine ") and "[" in low:
        return [(T.RED, line)]
    if line.startswith("#"):
        return [(T.MUTED, line)]
    return [(T.TEXT2, line)]


_ADV = {}


def mono_advance(size):
    """Exact advance width of one JetBrains Mono character at a font size."""
    if size not in _ADV:
        m = _mk(f'<span foreground="{BLOCK_COLOR}">\u2588</span>' + " " * 39 +
                f'<span foreground="{BLOCK_COLOR}">\u2588</span>', font=T.MONO, font_size=size,
                alignment="LEFT", base_color=T.TEXT)
        bl = sorted([sm for sm in m.submobjects], key=lambda b: b.get_left()[0])
        _ADV[size] = (bl[-1].get_left()[0] - bl[0].get_left()[0]) / 40
    return _ADV[size]


def _fit_size(src, size, width, numbers, marks, pad=0.22, min_size=9):
    """Largest font size <= size at which the longest line fits in width."""
    if not width:
        return size
    lines = src.expandtabs(4).strip("\n").split("\n")
    longest = max((len(l) for l in lines), default=1)
    n = len(lines)
    for sz in range(int(size), min_size - 1, -1):
        cw = mono_advance(sz)
        gutter = (len(str(n)) + 1.2) * cw if numbers else 0.0
        need = gutter + (longest + 1) * cw + (0.42 if marks else 0.0) + 2 * pad
        if need <= width + 1e-6:
            return sz
    print(f"LAYOUT-WARN listing too wide even at size {min_size}: {lines[0][:40]!r}", flush=True)
    return min_size


def _wrap_term(src, width, size, pad=0.22):
    cw = mono_advance(size)
    maxc = max(int((width - 2 * pad) / cw) - 1, 10)
    out_ = []
    for line in src.split("\n"):
        while len(line) > maxc:
            cut = line.rfind(" ", 0, maxc)
            if cut <= maxc // 3:
                cut = maxc
            out_.append(line[:cut])
            line = "    " + line[cut:].lstrip()
        out_.append(line)
    return "\n".join(out_)


class Listing(VGroup):
    """A code or terminal panel. Line numbers are 1-based.

    Useful members: .panel, .ys[i] (centre y of line i), .x_text (left x of
    code text), .cw (character width), .line_end(i), .right
    """

    def __init__(self, src, size=T.SIZE_CODE, title=None, lang="go",
                 numbers=True, hl=(), hl_color=T.YELLOW, marks=None,
                 width=None, dim=(), kind="code", lsh=None, pad=0.22,
                 title_color=T.MUTED, max_cols=None, start=1):
        super().__init__()
        if width and kind == "code":
            size = _fit_size(src, size, width, numbers, marks, pad)
        elif width and kind == "term":
            src = _wrap_term(src, width, size, pad)
        self.size = size
        self.start = start
        off = start - 1
        hl = [((h[0] - off, h[1]) if isinstance(h, tuple) else h - off) for h in hl]
        dim = [d - off for d in dim]
        if marks:
            marks = {k - off: v for k, v in marks.items()}
        src = src.expandtabs(4).rstrip("\n")
        if src.startswith("\n"):
            src = src[1:]
        raw_lines = src.split("\n")
        if lang in ("go", "c"):
            mlines = _go_markup_lines(src, lang)
            while len(mlines) < len(raw_lines):
                mlines.append([])
        else:
            mlines = _plain_markup_lines(src, _term_color if kind == "term" else
                                         (lambda l: [(T.TEXT, l)]))
        dim = set(dim)
        body_lines = []
        for i, ml in enumerate(mlines):
            if (i + 1) in dim:
                seg = "".join(f'<span foreground="{T.MUTED}">{esc(v)}</span>' for c, v in ml)
            else:
                seg = "".join(f'<span foreground="{c}">{esc(v)}</span>' for c, v in ml)
            body_lines.append(f'<span foreground="{BLOCK_COLOR}">█</span>' + seg)
        markup = "\n".join(body_lines)
        text = _mk(markup, font=T.MONO, font_size=size, alignment="LEFT", lsh=lsh,
                   base_color=T.TEXT)
        blocks = [sm for sm in text.submobjects
                  if color_to_hex(sm.get_fill_color()).upper() == BLOCK_COLOR]
        blocks.sort(key=lambda b: -b.get_center()[1])
        assert len(blocks) == len(raw_lines), (len(blocks), len(raw_lines))
        self.cw = mono_advance(size)
        self.ys = [None] + [b.get_center()[1] for b in blocks]
        self.pitch = (self.ys[1] - self.ys[-1]) / max(len(blocks) - 1, 1) \
            if len(blocks) > 1 else size * 0.0128
        for b in blocks:
            b.set_opacity(0)
        n = len(raw_lines)
        gutter = (len(str(n + off)) + 1.2) * self.cw if numbers else 0.0
        self.text = text
        # natural width
        longest = max(len(l) for l in raw_lines) if raw_lines else 1
        if max_cols:
            longest = max(longest, max_cols)
        inner_w = gutter + (longest + 1) * self.cw + (0.42 if marks else 0.0)
        w = width if width else inner_w + 2 * pad
        if title is not None and not width:
            w = max(w, 0.105 * len(title) + 2.1)
        bar_h = 0.36 if title is not None else 0.0
        h = len(blocks) * self.pitch + 2 * pad * 0.8 + bar_h
        fill = T.CODE_BG if kind == "code" else "#060A12"
        panel_ = rbox(w, h, color=T.STROKE, fill=fill, radius=0.14, stroke_width=1.6)
        self.panel = panel_
        # place text: first line centre at top - bar_h - pad*0.8 - pitch/2
        top = panel_.get_top()[1] - bar_h - pad * 0.8 - self.pitch / 2
        left = panel_.get_left()[0] + pad + gutter - self.cw  # block glyph width
        text.shift(P(left - blocks[0].get_left()[0], top - self.ys[1]))
        self.ys = [None] + [b.get_center()[1] for b in blocks]
        self.x_text = left + self.cw
        self.right = panel_.get_right()[0]
        self.raw_lines = raw_lines
        self.add(panel_)
        # title bar
        if title is not None:
            bar = RoundedRectangle(width=w - 0.02, height=bar_h, corner_radius=0.13)
            bar.set_fill(T.PANEL2, 1).set_stroke(width=0)
            bar.move_to(panel_.get_top() + DOWN * 0.01, aligned_edge=UP)
            sq = Rectangle(width=w - 0.02, height=bar_h / 2).set_fill(T.PANEL2, 1).set_stroke(width=0)
            sq.move_to(bar.get_bottom(), aligned_edge=DOWN)
            sep = hline(panel_.get_left()[0], panel_.get_right()[0], bar.get_bottom()[1], T.STROKE, 1.6)
            outline = panel_.copy().set_fill(opacity=0)
            cover = VGroup(sq, outline)
            dots = VGroup(*[Dot(radius=0.045, fill_color=c) for c in ("#FF5F57", "#FEBC2E", "#28C840")])
            dots.arrange(RIGHT, buff=0.09)
            ycen = panel_.get_top()[1] - bar_h / 2
            dots.move_to(P(panel_.get_left()[0] + 0.2, ycen), aligned_edge=LEFT)
            tt = txt(title, size=T.SIZE_TINY, color=title_color, font=T.MONO, markup=False)
            tt.move_to(P(dots.get_right()[0] + 0.2, ycen), aligned_edge=LEFT)
            self.add(bar, cover, sep, dots, tt)
            if kind == "code" and lang == "go":
                lp = pill("Go", T.GO_DARK, size=11, filled=True, text_color=T.TEXT,
                          padx=0.1, pady=0.04)
                lp.move_to(P(panel_.get_right()[0] - 0.2, ycen), aligned_edge=RIGHT)
                self.add(lp)
            elif kind == "term":
                lp = pill("terminal", T.STROKE2, size=11, filled=True, text_color=T.TEXT2,
                          padx=0.1, pady=0.04)
                lp.move_to(P(panel_.get_right()[0] - 0.2, ycen), aligned_edge=RIGHT)
                self.add(lp)
        # highlights
        for ln in hl:
            if isinstance(ln, tuple):
                ln, c = ln
            else:
                c = hl_color
            y = self.ys[ln]
            hb = Rectangle(width=w - 0.08, height=self.pitch * 1.02)
            hb.set_fill(c, 0.13).set_stroke(width=0)
            hb.move_to(P(panel_.get_center()[0], y))
            acc = Rectangle(width=0.05, height=self.pitch * 1.02).set_fill(c, 1).set_stroke(width=0)
            acc.move_to(P(panel_.get_left()[0] + 0.05, y))
            self.add(hb, acc)
        # line numbers
        if numbers:
            nums = VGroup()
            for i in range(1, n + 1):
                t = txt(str(i + off), size=size - 3, color=T.MUTED, font=T.MONO, markup=False)
                t.move_to(P(panel_.get_left()[0] + pad + gutter - 1.0 * self.cw, self.ys[i]),
                          aligned_edge=RIGHT)
                nums.add(t)
            self.add(nums)
        self.add(text)
        # markers: {line: "1"} or {line: ("1", color)}
        self.markers = {}
        if marks:
            for ln, m in marks.items():
                lab, c = (m if isinstance(m, tuple) else (m, T.YELLOW))
                bd = badge(lab, c, r=0.13, size=13)
                bd.move_to(P(self.right - 0.26, self.ys[ln]))
                self.add(bd)
                self.markers[ln] = bd

    def y(self, n):
        """centre y of file line n"""
        return self.ys[n - self.start + 1]

    def line_end(self, n):
        return self.x_text + len(self.raw_lines[n - self.start].rstrip()) * self.cw

    def line_point(self, n, col=None):
        x = self.line_end(n) if col is None else self.x_text + col * self.cw
        return P(x, self.y(n))

    def mark(self, n, lab, color=T.YELLOW, x=None):
        bd = badge(lab, color, r=0.13, size=13)
        bd.move_to(P(x if x is not None else self.line_end(n) + 0.3, self.y(n)))
        self.add(bd)
        return bd


def code(src, **kw):
    return Listing(src, **kw)


def code_ex(name, file="main.go", lines=None, **kw):
    """Listing of an example file; with lines=(a, b) shows real line numbers."""
    if lines:
        kw.setdefault("start", lines[0])
    kw.setdefault("title", f"examples/{name}/{file}")
    return Listing(src(name, file, lines), **kw)


def terminal(src, title="go run .", size=T.SIZE_CODE_SMALL, **kw):
    kw.setdefault("numbers", False)
    return Listing(src, size=size, title=title, lang="text", kind="term", **kw)


# ---------------------------------------------------------------------------
# Tables
# ---------------------------------------------------------------------------
def table(rows, widths, size=T.SIZE_SMALL, header=True, header_color=T.GO,
          pad=0.11, row_fill=(T.PANEL, T.PANEL2), col_colors=None, border=T.STROKE,
          header_fill="#0E2A3A", min_row_h=0.0, center_cols=()):
    """rows: list of rows of markup strings. widths: column widths."""
    g = VGroup()
    y = 0.0
    total_w = sum(widths)
    cells_all = []
    for r, row in enumerate(rows):
        is_h = header and r == 0
        cells = []
        for c, s in enumerate(row):
            col = (header_color if is_h else
                   (col_colors[c] if col_colors and col_colors[c] else T.TEXT))
            t = txt(f"**{s}**" if (is_h and s) else (s or " "), size=size - (1 if is_h else 0),
                    color=col, width=widths[c] - 2 * pad,
                    align="CENTER" if c in center_cols else "LEFT")
            cells.append(t)
        rh = max([t.get_height() for t in cells] + [min_row_h]) + 2 * pad
        fill = header_fill if is_h else row_fill[(r - (1 if header else 0)) % 2]
        bg = Rectangle(width=total_w, height=rh).set_fill(fill, 1).set_stroke(width=0)
        bg.move_to(P(total_w / 2, y - rh / 2))
        g.add(bg)
        x = 0.0
        for c, t in enumerate(cells):
            if c in center_cols:
                t.move_to(P(x + widths[c] / 2, y - rh / 2))
            else:
                t.move_to(P(x + pad, y - pad), aligned_edge=UL)
            x += widths[c]
        cells_all.append(cells)
        g.add(*cells)
        y -= rh
    # grid lines
    x = 0.0
    for c in range(1, len(widths)):
        x += widths[c - 1]
        g.add(vline(x, 0, y, border, 1.2))
    g.add(rbox(total_w, -y, color=border, fill=T.BG, fill_opacity=0.0, radius=0.06,
               stroke_width=1.6).move_to(P(total_w / 2, y / 2)))
    if header:
        hh = rows and cells_all[0][0]
    g.cells = cells_all
    return g


# ---------------------------------------------------------------------------
# Icons
# ---------------------------------------------------------------------------
def gopher(h=1.0, color=T.GOPHER, mood="happy", look=(0.35, 0.0)):
    """The book's gopher mascot (a simplified drawing in the spirit of
    Renee French's Go gopher). mood: happy | sleep | blocked | dead | run | think"""
    s = h
    dark = "#0B1B2B"
    sw = 2.2 * h
    if mood in ("blocked", "dead"):
        color = "#8FA3B8" if mood == "blocked" else "#5C6B7E"
    g = VGroup()
    ear_l = Circle(radius=0.11 * s).set_fill(color, 1).set_stroke(dark, sw).move_to(P(-0.31 * s, 0.43 * s))
    ear_r = ear_l.copy().move_to(P(0.31 * s, 0.43 * s))
    feet = VGroup(*[Ellipse(width=0.24 * s, height=0.11 * s).set_fill(T.SNOUT, 1)
                    .set_stroke(dark, sw).move_to(P(x * s, -0.5 * s)) for x in (-0.2, 0.2)])
    body = RoundedRectangle(width=0.84 * s, height=1.0 * s, corner_radius=0.38 * s)
    body.set_fill(color, 1).set_stroke(dark, sw)
    belly = Ellipse(width=0.5 * s, height=0.42 * s).set_fill(WHITE, 0.10).set_stroke(width=0)
    belly.move_to(P(0, -0.22 * s))
    hands = VGroup(*[Ellipse(width=0.13 * s, height=0.21 * s).set_fill(T.SNOUT, 1)
                     .set_stroke(dark, sw).move_to(P(x * s, -0.1 * s)).rotate(-x * 0.9)
                     for x in (-0.44, 0.44)])
    g.add(ear_l, ear_r, feet, body, belly, hands)
    ex = 0.18
    if mood == "sleep":
        eyes = VGroup(*[Arc(start_angle=PI + 0.25, angle=PI - 0.5, radius=0.11 * s)
                        .set_stroke(dark, 3 * h).move_to(P(x * s, 0.2 * s)) for x in (-ex, ex)])
        g.add(eyes)
    elif mood == "dead":
        eyes = VGroup(*[cross_mark(dark, 0.08 * s).move_to(P(x * s, 0.2 * s)) for x in (-ex, ex)])
        g.add(eyes)
    else:
        whites = VGroup(*[Circle(radius=0.165 * s).set_fill(WHITE, 1).set_stroke(dark, sw)
                          .move_to(P(x * s, 0.2 * s)) for x in (-ex, ex)])
        lx, ly = look
        if mood == "blocked":
            lx, ly = 0.0, -0.45
        if mood == "think":
            lx, ly = 0.3, 0.45
        pupils = VGroup(*[Circle(radius=0.07 * s).set_fill(dark, 1).set_stroke(width=0)
                          .move_to(P((x + lx * 0.09) * s, (0.2 + ly * 0.09) * s)) for x in (-ex, ex)])
        shine = VGroup(*[Circle(radius=0.022 * s).set_fill(WHITE, 1).set_stroke(width=0)
                         .move_to(P((x + lx * 0.09 + 0.025) * s, (0.2 + ly * 0.09 + 0.03) * s))
                         for x in (-ex, ex)])
        g.add(whites, pupils, shine)
    snout = Ellipse(width=0.3 * s, height=0.17 * s).set_fill(T.SNOUT, 1).set_stroke(dark, sw * 0.8)
    snout.move_to(P(0, 0.0 * s))
    nose = Ellipse(width=0.12 * s, height=0.07 * s).set_fill(dark, 1).set_stroke(width=0)
    nose.move_to(P(0, 0.055 * s))
    teeth = Rectangle(width=0.1 * s, height=0.08 * s).set_fill(WHITE, 1).set_stroke(dark, sw * 0.6)
    teeth.move_to(P(0, -0.11 * s))
    g.add(teeth, snout, nose)
    if mood == "run":
        lines = VGroup(*[Line(P(-0.95 * s, y * s), P(-0.6 * s, y * s)).set_stroke(T.GO_LIGHT, 3 * h, 0.7)
                         for y in (0.15, 0.0, -0.15)])
        g.add(lines)
    if mood == "sleep":
        zz = VGroup(txt("z", size=int(22 * h), color=T.TEXT2, weight="BOLD"),
                    txt("z", size=int(16 * h), color=T.TEXT2, weight="BOLD"))
        zz[0].move_to(P(0.5 * s, 0.62 * s))
        zz[1].move_to(P(0.68 * s, 0.78 * s))
        g.add(zz)
    return g


def gtok(lab="G", color=T.GO, w=0.82, h=0.4, state="run", size=None, eyes=True):
    """Goroutine token. state: run (filled) | ready (outline) | wait (grey) | dead."""
    fill, fo, sc, tc = color, 1.0, color, T.BG
    if state == "ready":
        fo, tc = 0.16, color
    elif state == "wait":
        fill, sc, fo, tc = "#64748B", "#94A3B8", 0.9, "#0B1220"
    elif state == "dead":
        fill, sc, fo, tc = "#1E293B", "#475569", 1.0, "#64748B"
    b = rbox(w, h, color=sc, fill=fill, fill_opacity=fo, radius=h / 2, stroke_width=2)
    t = txt(lab, size=size or int(h * 40), color=tc, weight="BOLD", font=T.MONO, markup=False)
    g = VGroup(b, t)
    if eyes and state != "dead":
        ec = WHITE if state != "ready" else color
        e = VGroup(*[Dot(radius=h * 0.075, fill_color=ec) for _ in range(2)]).arrange(RIGHT, buff=h * 0.09)
        e.move_to(b.get_left() + RIGHT * (h * 0.42) + UP * h * 0.06)
        t.move_to(b.get_center() + RIGHT * h * 0.18)
        g.add(e)
    else:
        t.move_to(b)
    return g


def mthread(lab="M", w=1.05, h=0.52, color=T.AMBER, size=None, active=True):
    """OS thread (M): amber box with a thread squiggle."""
    b = rbox(w, h, color=color, fill=color, fill_opacity=0.16 if active else 0.05,
             radius=0.08, stroke_width=2.2)
    if not active:
        b.set_stroke(color, 2.2, 0.5)
    pts = [P(-0.16 + 0.04 * i, 0.07 * np.sin(i * 1.4)) for i in range(9)]
    sq = VMobject().set_points_smoothly(pts).set_stroke(color, 3)
    sq.move_to(b.get_left() + RIGHT * 0.25)
    t = txt(lab, size=size or int(h * 38), color=color, weight="BOLD", font=T.MONO, markup=False)
    t.move_to(b.get_center() + RIGHT * 0.12)
    return VGroup(b, sq, t)


def pchip(lab="P", s=0.66, color=T.VIOLET, size=None):
    """Logical processor (P): violet chip with pins."""
    b = rbox(s, s, color=color, fill=color, fill_opacity=0.18, radius=0.07, stroke_width=2.2)
    pins = VGroup()
    for k in range(3):
        off = (k - 1) * s * 0.26
        for d in (UP, DOWN, LEFT, RIGHT):
            perp = np.array([d[1], d[0], 0])
            pin = Line(ORIGIN, d * 0.08).set_stroke(color, 2.5)
            pin.move_to(b.get_center() + d * (s / 2 + 0.04) + perp * off)
            pins.add(pin)
    t = txt(lab, size=size or int(s * 36), color=color, weight="BOLD", font=T.MONO, markup=False)
    t.move_to(b)
    return VGroup(pins, b, t)


def cpu_core(lab="CPU 0", w=1.3, h=0.8, color=T.GREY, size=T.SIZE_TINY):
    b = rbox(w, h, color=color, fill="#1A2436", radius=0.08, stroke_width=2)
    inner = rbox(w * 0.55, h * 0.5, color=color, fill="#243049", radius=0.05, stroke_width=1.5)
    inner.move_to(b)
    pins = VGroup()
    for k in range(5):
        x = (k - 2) * w / 6
        for d in (UP, DOWN):
            pins.add(Line(ORIGIN, d * 0.07).set_stroke(color, 2).move_to(b.get_center() + P(x, d[1] * (h / 2 + 0.035))))
    t = txt(lab, size=size, color=T.TEXT2, weight="BOLD", align="CENTER")
    t.move_to(inner)
    return VGroup(pins, b, inner, t)


def lock_icon(color=T.RED, s=0.5, locked=True):
    body = rbox(s, s * 0.78, color=color, fill=color, fill_opacity=0.9, radius=s * 0.12, stroke_width=1)
    shackle = Arc(start_angle=0, angle=PI, radius=s * 0.3).set_stroke(color, 5 * s / 0.5)
    legs = VGroup(Line(P(-s * 0.3, 0), P(-s * 0.3, -s * 0.12)), Line(P(s * 0.3, 0), P(s * 0.3, -s * 0.12)))
    legs.set_stroke(color, 5 * s / 0.5)
    sh = VGroup(shackle, legs)
    sh.next_to(body, UP, buff=-s * 0.12)
    if not locked:
        sh.shift(UP * s * 0.18 + RIGHT * s * 0.0)
        sh.rotate(-0.35, about_point=sh.get_corner(DR))
    hole = VGroup(Circle(radius=s * 0.07).set_fill(T.BG, 1).set_stroke(width=0),
                  Rectangle(width=s * 0.05, height=s * 0.16).set_fill(T.BG, 1).set_stroke(width=0).shift(DOWN * s * 0.08))
    hole.move_to(body.get_center() + UP * s * 0.03)
    return VGroup(sh, body, hole)


def clock_icon(color=T.BLUE, r=0.25, hour=2, minute=0):
    c = Circle(radius=r).set_fill(color, 0.12).set_stroke(color, 2.5)
    ticks = VGroup(*[Line(ORIGIN, UP * r * 0.18).set_stroke(color, 2)
                     .move_to(c.get_center() + r * 0.8 * np.array([np.sin(a), np.cos(a), 0]))
                     .rotate(-a) for a in np.linspace(0, TAU, 12, endpoint=False)])
    ha = TAU * (hour % 12) / 12 + TAU * minute / 720
    ma = TAU * minute / 60
    hh = Line(ORIGIN, r * 0.5 * np.array([np.sin(ha), np.cos(ha), 0])).set_stroke(color, 3)
    mh = Line(ORIGIN, r * 0.75 * np.array([np.sin(ma), np.cos(ma), 0])).set_stroke(color, 2.5)
    return VGroup(c, ticks, hh, mh)


def gear_icon(color=T.VIOLET, r=0.25, teeth=8):
    pts = []
    for i in range(teeth * 2):
        a = i * PI / teeth
        rr = r if i % 2 == 0 else r * 0.78
        pts.append(rr * np.array([np.cos(a), np.sin(a), 0]))
        a2 = (i + 0.5) * PI / teeth
        pts.append(rr * np.array([np.cos(a2), np.sin(a2), 0]))
    g = Polygon(*pts).set_fill(color, 0.25).set_stroke(color, 2.5)
    hole = Circle(radius=r * 0.3).set_fill(T.BG, 1).set_stroke(color, 2)
    return VGroup(g, hole)


def msg(lab="v", color=T.PINK, s=0.36, size=None, filled=True):
    """A value travelling through a channel."""
    b = rbox(s, s, color=color, fill=color, fill_opacity=0.95 if filled else 0.15,
             radius=0.06, stroke_width=1.5)
    t = txt(lab, size=size or int(s * 44), color=T.BG if filled else color,
            weight="BOLD", font=T.MONO, markup=False)
    t.move_to(b)
    return VGroup(b, t)


def chan_pipe(cap=3, items=(), cell=0.5, color=T.GREEN, lab=None, item_color=T.PINK,
              show_idx=False, size=T.SIZE_TINY):
    """A channel drawn as a tube with `cap` slots (items fill from the right,
    the head of the queue is on the right)."""
    if cap == 0:
        ring = rbox(0.6, cell + 0.1, color=color, fill=color, fill_opacity=0.08,
                    radius=0.12, stroke_width=3)
        g = VGroup(ring)
        if lab:
            l = txt(lab, size=size, color=color, weight="BOLD", font=T.MONO, markup=False)
            l.next_to(ring, DOWN, buff=0.1)
            g.add(l)
        g.slots = []
        return g
    w = cap * cell + 0.16
    tube = rbox(w, cell + 0.16, color=color, fill=color, fill_opacity=0.08,
                radius=0.14, stroke_width=3)
    g = VGroup(tube)
    slots = []
    for i in range(cap):
        x = tube.get_left()[0] + 0.08 + cell * (i + 0.5)
        sl = rbox(cell - 0.08, cell - 0.08, color=color, fill=T.BG, fill_opacity=0.6,
                  radius=0.05, stroke_width=1.2)
        sl.set_stroke(color, 1.2, 0.5)
        sl.move_to(P(x, tube.get_center()[1]))
        slots.append(sl)
        g.add(sl)
        if show_idx:
            it = txt(str(i), size=11, color=T.MUTED, font=T.MONO, markup=False)
            it.next_to(sl, DOWN, buff=0.12)
            g.add(it)
    # items fill from the right (oldest on the right, next to leave)
    for k, v in enumerate(items):
        idx = cap - 1 - k
        if idx < 0:
            break
        m = msg(v, item_color, s=cell - 0.16)
        m.move_to(slots[idx])
        g.add(m)
    if lab:
        l = txt(lab, size=size, color=color, weight="BOLD", font=T.MONO, markup=False)
        l.next_to(tube, DOWN, buff=0.1 + (0.2 if show_idx else 0))
        g.add(l)
    g.slots = slots
    g.tube = tube
    return g


def slots_row(n, cell=0.42, color=T.VIOLET, items=(), item_fn=None, gap=0.04):
    """Generic row of queue cells; items is a list of mobjects or labels."""
    g = VGroup()
    cells = []
    for i in range(n):
        c = rbox(cell, cell, color=color, fill=T.BG, fill_opacity=0.5, radius=0.05, stroke_width=1.4)
        c.set_stroke(color, 1.4, 0.6)
        c.move_to(P(i * (cell + gap), 0))
        cells.append(c)
        g.add(c)
    for i, it in enumerate(items):
        if i >= n:
            break
        m = it if isinstance(it, Mobject) else (item_fn(it) if item_fn else gtok(it, w=cell * 0.9, h=cell * 0.6, eyes=False))
        m.move_to(cells[i])
        g.add(m)
    g.cells = cells
    return g


def kernel_band(w, h=0.6, lab="OS KERNEL", color=T.BLUE):
    b = rbox(w, h, color=color, fill=color, fill_opacity=0.12, radius=0.1, stroke_width=2)
    t = txt(lab, size=T.SIZE_TINY, color=color, weight="BOLD")
    t.move_to(b)
    return VGroup(b, t)


def titled_box(title, w, h, color=T.GO, fill=T.PANEL, size=T.SIZE_SMALL, title_color=None,
               fill_opacity=1.0, radius=0.14):
    """Box with a coloured title tab in the top-left corner."""
    b = rbox(w, h, color=color, fill=fill, fill_opacity=fill_opacity, radius=radius, stroke_width=2)
    t = txt(f"**{title}**", size=size, color=title_color or color)
    t.move_to(b.get_corner(UL) + P(0.18, -0.14), aligned_edge=UL)
    g = VGroup(b, t)
    g.box = b
    g.title = t
    return g


def card(title, body, w=4.0, color=T.GO, size=T.SIZE_SMALL, title_size=None, icon=None,
         fill=T.PANEL, h=None, body_color=T.TEXT2, gap=0.12):
    """Card: coloured title, wrapped body, optional icon on the right of the title."""
    tt = txt(f"**{title}**", size=title_size or size + 3, color=color, width=w - 0.4 - (0.6 if icon else 0))
    bb = txt(body, size=size, color=body_color, width=w - 0.4)
    content = VGroup(tt, bb).arrange(DOWN, aligned_edge=LEFT, buff=gap)
    hh = h if h else content.get_height() + 0.4
    b = rbox(w, hh, color=color, fill=fill, radius=0.14, stroke_width=1.8)
    b.set_stroke(color, 1.8, 0.7)
    content.move_to(b.get_corner(UL) + P(0.2, -0.2), aligned_edge=UL)
    g = VGroup(b, content)
    if icon is not None:
        icon.move_to(b.get_corner(UR) + P(-0.38, -0.36))
        g.add(icon)
    g.box = b
    return g


def stat(value, lab, color=T.GO, w=2.4, size_v=40, size_l=T.SIZE_TINY):
    v = txt(f"**{value}**", size=size_v, color=color, align="CENTER")
    l = txt(lab, size=size_l, color=T.TEXT2, width=w - 0.3, align="CENTER")
    c = VGroup(v, l).arrange(DOWN, buff=0.1)
    b = rbox(w, c.get_height() + 0.35, color=color, fill=T.PANEL, stroke_width=1.6)
    b.set_stroke(color, 1.6, 0.6)
    c.move_to(b)
    return VGroup(b, c)


def num_steps(steps, width, color=T.GO, size=T.SIZE_SMALL, gap=0.18):
    """Numbered steps: list of (title, body)."""
    rows = VGroup()
    for i, (t, b) in enumerate(steps):
        bd = badge(str(i + 1), color, r=0.17, size=15)
        tt = txt(f"**{t}**" + (f"  {b}" if b else ""), size=size, width=width - 0.55)
        tt.next_to(bd, RIGHT, buff=0.18, aligned_edge=UP).shift(UP * 0.02)
        bd.move_to(P(bd.get_center()[0], first_line_y(tt, size)))
        rows.add(VGroup(bd, tt))
    rows.arrange(DOWN, aligned_edge=LEFT, buff=gap)
    return rows


def brace(mob, direction=DOWN, color=T.TEXT2, buff=0.08, depth=0.16, width=2.2):
    """A curly brace along one side of mob, drawn without LaTeX."""
    d = np.array(direction, dtype=float)
    horiz = abs(d[1]) > 0.5
    if horiz:
        a, b = mob.get_left()[0], mob.get_right()[0]
        edge = (mob.get_bottom() if d[1] < 0 else mob.get_top())[1]
        L = b - a
    else:
        a, b = mob.get_bottom()[1], mob.get_top()[1]
        edge = (mob.get_left() if d[0] < 0 else mob.get_right())[0]
        L = b - a
    h = depth
    r = min(h / 2, L / 6)
    pts = [(0, 0), (r * 0.3, h * 0.35), (r, h / 2), (L / 2 - r, h / 2), (L / 2 - r * 0.3, h * 0.65), (L / 2, h),
           (L / 2 + r * 0.3, h * 0.65), (L / 2 + r, h / 2), (L - r, h / 2), (L - r * 0.3, h * 0.35), (L, 0)]
    v = VMobject().set_points_smoothly([P(x, y) for x, y in pts]) if False else VMobject()
    v.set_points_as_corners([P(x, y) for x, y in pts])
    v.set_stroke(color, width)
    sgn = -1 if (d[1] < 0 or d[0] < 0) else 1
    if horiz:
        v.stretch(sgn, 1, about_point=ORIGIN)
        v.shift(P(a, edge + sgn * buff))
    else:
        v.rotate(PI / 2, about_point=ORIGIN)
        v.stretch(-sgn, 0, about_point=ORIGIN)
        v.shift(P(edge + sgn * buff, a))
    return v


def brace_label(mob, s, direction=DOWN, color=T.TEXT2, size=T.SIZE_TINY, buff=0.08, width=None):
    br = brace(mob, direction, color, buff)
    t = txt(s, size=size, color=color, width=width, align="CENTER")
    t.next_to(br, direction, buff=0.08)
    return VGroup(br, t)


def time_axis(x0, x1, y, ticks=(), color=T.MUTED, lab="time", size=T.SIZE_TINY):
    ax = arrow(P(x0, y), P(x1, y), color, thick=2.0, buff=0)
    g = VGroup(ax)
    for x, s in ticks:
        g.add(Line(P(x, y - 0.06), P(x, y + 0.06)).set_stroke(color, 1.5))
        if s:
            g.add(txt(s, size=size - 2, color=color).next_to(P(x, y), DOWN, buff=0.1))
    if lab:
        g.add(txt(lab, size=size, color=color).next_to(P(x1, y), DOWN, buff=0.1).shift(LEFT * 0.2))
    return g


def seg(x0, x1, y, color, h=0.32, lab=None, size=T.SIZE_TINY, opacity=0.9, text_color=None,
        outline=False):
    """Segment of a timeline lane."""
    r = rbox(max(x1 - x0, 0.02), h, color=color, fill=color,
             fill_opacity=0.15 if outline else opacity, radius=0.05, stroke_width=1.4)
    r.move_to(P((x0 + x1) / 2, y))
    g = VGroup(r)
    if lab:
        t = txt(lab, size=size, color=text_color or (color if outline else T.BG), weight="BOLD", font=T.SANS)
        if t.get_width() > (x1 - x0) - 0.08:
            t.scale((x1 - x0 - 0.08) / t.get_width())
        t.move_to(r)
        g.add(t)
    return g


def hbars(data, x0, y0, bar_w_max, row_h=0.42, color=T.GO, size=T.SIZE_SMALL,
          label_w=2.6, fmt="{:.0f}", unit="", vmax=None, colors=None, value_color=T.TEXT):
    """Horizontal bar chart: data = [(label, value)]. Labels left, values at bar end."""
    vmax = vmax or max(v for _, v in data)
    g = VGroup()
    for i, (lab, v) in enumerate(data):
        y = y0 - i * row_h
        c = colors[i] if colors else color
        t = txt(lab, size=size, color=T.TEXT2, width=label_w)
        t.move_to(P(x0 + label_w - 0.1, y), aligned_edge=RIGHT)
        L = max(bar_w_max * v / vmax, 0.03)
        b = Rectangle(width=L, height=row_h * 0.62).set_fill(c, 1).set_stroke(width=0)
        b.move_to(P(x0 + label_w + L / 2, y))
        vt = txt(fmt.format(v) + unit, size=size - 1, color=value_color, weight="BOLD")
        vt.next_to(b, RIGHT, buff=0.1)
        g.add(t, b, vt)
    return g


# ---------------------------------------------------------------------------
# Page base class
# ---------------------------------------------------------------------------
BOOK_TITLE = "GO: ZERO TO MASTERY"
MODULE_TITLE = "MODULE 8  ·  THE CONCURRENCY MODEL"


class Page(Scene):
    """One page of the book. Subclasses set the class attributes and
    implement build()."""
    CH = ""            # e.g. "8.3"
    CH_NAME = ""       # e.g. "Goroutines"
    TITLE = ""
    SUB = ""
    CHROME = True

    def construct(self):
        bg = Rectangle(width=FW + 0.2, height=FH + 0.2).set_fill(T.BG, 1).set_stroke(width=0)
        self.add(bg)
        if self.CHROME:
            self.chrome()
        n0 = len(self.mobjects)
        self.build()
        self.check_layout(self.mobjects[n0:])

    def check_layout(self, mobs):
        """Report elements that cross the footer rule or the page edges."""
        if not self.CHROME:
            return
        bottom, top = -FH / 2 + 0.47, FH / 2 - 0.47
        left, right = -FW / 2 + 0.25, FW / 2 - 0.25
        for m in mobs:
            if m.get_width() == 0 and m.get_height() == 0:
                continue
            b, t_ = m.get_bottom()[1], m.get_top()[1]
            l, r = m.get_left()[0], m.get_right()[0]
            issues = []
            if b < bottom - 0.01:
                issues.append(f"below footer by {bottom - b:.2f}")
            if t_ > top + 0.01:
                issues.append(f"above header by {t_ - top:.2f}")
            if l < left - 0.01:
                issues.append(f"past left edge by {left - l:.2f}")
            if r > right + 0.01:
                issues.append(f"past right edge by {r - right:.2f}")
            if issues:
                print(f"LAYOUT-WARN {type(self).__name__}: {type(m).__name__} at "
                      f"({m.get_center()[0]:.1f},{m.get_center()[1]:.1f}) " + "; ".join(issues), flush=True)

    # -- chrome --------------------------------------------------------------
    def page_number(self):
        return PAGES.get("pages", {}).get(type(self).__name__, "")

    def chrome(self):
        y_h = FH / 2 - 0.24
        left = txt(f"**{BOOK_TITLE}**   {MODULE_TITLE}", size=12, color=T.MUTED)
        left.move_to(P(X0, y_h), aligned_edge=LEFT)
        right_s = f"CHAPTER {self.CH}  ·  {self.CH_NAME.upper()}" if self.CH else self.CH_NAME.upper()
        right = txt(right_s, size=12, color=T.MUTED, weight="BOLD")
        right.move_to(P(X1, y_h), aligned_edge=RIGHT)
        top_line = hline(X0, X1, FH / 2 - 0.45, T.STROKE, 1.4)
        self.add(left, right, top_line)
        # accent bar in the go colour
        acc = Rectangle(width=1.2, height=0.05).set_fill(T.GO, 1).set_stroke(width=0)
        acc.move_to(P(X0 + 0.6, FH / 2 - 0.45))
        self.add(acc)
        if self.TITLE:
            ty = FH / 2 - 0.98
            items = []
            if self.CH:
                tag = pill(self.CH, T.GO, size=20, padx=0.16, pady=0.08)
                tag.move_to(P(X0, ty), aligned_edge=LEFT)
                items.append(tag)
            t = txt(f"**{self.TITLE}**", size=T.SIZE_H1, color=T.TEXT)
            t.move_to(P((items[0].get_right()[0] + 0.25) if items else X0, ty), aligned_edge=LEFT)
            self.add(*items, t)
            if self.SUB:
                s = txt(self.SUB, size=T.SIZE_BODY - 1, color=T.TEXT2, width=CW)
                s.move_to(P(X0, ty - 0.52), aligned_edge=LEFT)
                self.add(s)
        # footer
        y_f = -FH / 2 + 0.24
        self.add(hline(X0, X1, -FH / 2 + 0.44, T.STROKE, 1.2))
        n = self.page_number()
        if n != "":
            pn = txt(f"**{n}**", size=14, color=T.TEXT2)
            pn.move_to(P(X1, y_f), aligned_edge=RIGHT)
            self.add(pn)
        foot = txt("Goroutines · Channels · The Scheduler", size=11, color=T.MUTED)
        foot.move_to(P(X0, y_f), aligned_edge=LEFT)
        self.add(foot)

    def build(self):
        pass

    # -- helpers ---------------------------------------------------------------
    def at(self, mob, x, y, edge=UL):
        mob.move_to(P(x, y), aligned_edge=edge)
        self.add(mob)
        return mob

    def put(self, *mobs):
        self.add(*mobs)
        return mobs[0] if len(mobs) == 1 else mobs


# ---------------------------------------------------------------------------
# Layout and diagram helpers
# ---------------------------------------------------------------------------
def vstack(*mobs, buff=0.25, aligned=LEFT):
    g = VGroup(*mobs)
    g.arrange(DOWN, aligned_edge=aligned, buff=buff)
    return g


def hstack(*mobs, buff=0.25, aligned=UP):
    g = VGroup(*mobs)
    g.arrange(RIGHT, aligned_edge=aligned, buff=buff)
    return g


def section(s, color=T.GO, size=T.SIZE_H3, width=None):
    """Small section heading with a coloured bar on the left."""
    t = txt(f"**{s}**", size=size, color=T.TEXT, width=width)
    bar = Rectangle(width=0.06, height=t.get_height() + 0.08).set_fill(color, 1).set_stroke(width=0)
    bar.next_to(t, LEFT, buff=0.14)
    return VGroup(bar, t)


def node(s, w=2.2, h=0.62, color=T.GO, size=T.SIZE_SMALL, fill_opacity=0.12, text_color=None,
         radius=0.12, weight="BOLD", stroke_width=2.0):
    """Flowchart box with centred text."""
    b = rbox(w, h, color=color, fill=color, fill_opacity=fill_opacity, radius=radius,
             stroke_width=stroke_width)
    t = txt(s, size=size, color=text_color or T.TEXT, width=w - 0.2, align="CENTER", weight=weight)
    t.move_to(b)
    g = VGroup(b, t)
    g.box = b
    return g


def diamond(s, w=2.2, h=1.0, color=T.YELLOW, size=T.SIZE_SMALL):
    d = Polygon(P(0, h / 2), P(w / 2, 0), P(0, -h / 2), P(-w / 2, 0))
    d.set_fill(color, 0.12).set_stroke(color, 2)
    t = txt(s, size=size, color=T.TEXT, width=w * 0.62, align="CENTER", weight="BOLD")
    t.move_to(d)
    g = VGroup(d, t)
    g.box = d
    return g


def connect(a, b, color=T.TEXT2, thick=2.6, buff=0.06, side_a=None, side_b=None, arc=0.0):
    """Arrow from the edge of mobject a to the edge of mobject b."""
    pa = a.get_edge_center(side_a) if side_a is not None else None
    pb = b.get_edge_center(side_b) if side_b is not None else None
    if pa is None or pb is None:
        ca, cb = a.get_center(), b.get_center()
        d = cb - ca
        if abs(d[0]) * (a.get_height() + b.get_height()) > abs(d[1]) * (a.get_width() + b.get_width()):
            sa, sb = (RIGHT, LEFT) if d[0] > 0 else (LEFT, RIGHT)
        else:
            sa, sb = (UP, DOWN) if d[1] > 0 else (DOWN, UP)
        pa = pa if pa is not None else a.get_edge_center(sa)
        pb = pb if pb is not None else b.get_edge_center(sb)
    return arrow(pa, pb, color, thick, buff, arc)


def quote(s, who, width=6.0, size=T.SIZE_H3, color=T.TEXT, accent=T.GO):
    mark = txt("“", size=90, color=accent, weight="BOLD")
    q = txt(f"__{s}__", size=size, color=color, width=width - 0.8)
    a = txt(f"— {who}", size=T.SIZE_SMALL, color=T.TEXT2, width=width - 0.8)
    body = vstack(q, a, buff=0.16)
    mark.next_to(body, LEFT, buff=0.15, aligned_edge=UP).shift(UP * 0.12)
    return VGroup(mark, body)


def do_dont(bad_src, good_src, bad_note="", good_note="", width=6.4, size=T.SIZE_CODE_SMALL,
            bad_title="DON'T", good_title="DO", bad_hl=(), good_hl=(), vertical=False, gap=0.3):
    """Side-by-side (or stacked) wrong/right code panels."""
    w = width if vertical else (width - gap) / 2

    def one(src, note, title, color, hl, mark):
        head = VGroup(mark, txt(f"**{title}**", size=T.SIZE_SMALL, color=color)).arrange(RIGHT, buff=0.12)
        c = code(src, size=size, width=w, numbers=False, hl=[(l, color) for l in hl])
        c.set_stroke(color, 1.6, 0.0)
        c.panel.set_stroke(color, 1.8, 0.8)
        parts = [head, c]
        if note:
            parts.append(txt(note, size=T.SIZE_SMALL - 1, color=T.TEXT2, width=w))
        return vstack(*parts, buff=0.12)

    a = one(bad_src, bad_note, bad_title, T.RED, bad_hl, cross_mark(T.RED, 0.12))
    b = one(good_src, good_note, good_title, T.GREEN, good_hl, check_mark(T.GREEN, 0.14))
    return vstack(a, b, buff=gap) if vertical else hstack(a, b, buff=gap)


def legend_row(items, size=T.SIZE_TINY, buff=0.35):
    """items: list of (mobject, label)"""
    g = VGroup()
    for m, s in items:
        g.add(VGroup(m, txt(s, size=size, color=T.TEXT2)).arrange(RIGHT, buff=0.12))
    g.arrange(RIGHT, buff=buff)
    return g


def lane(label_s, x0, x1, y, color=T.GO, size=T.SIZE_SMALL, label_w=1.6, line=True):
    """A horizontal swim lane with a label on the left; returns group."""
    l = txt(f"**{label_s}**", size=size, color=color, width=label_w)
    l.move_to(P(x0 - 0.15, y), aligned_edge=RIGHT)
    g = VGroup(l)
    if line:
        g.add(dashed(P(x0, y), P(x1, y), T.STROKE2, 1.2, 0.06))
    return g


# ---------------------------------------------------------------------------
# Chapter opener template
# ---------------------------------------------------------------------------
class Opener(Page):
    """Chapter opener: big number, title, tagline, outcomes, illustration."""
    NUM = "8.1"
    NAME = ""
    TAGLINE = ""
    LEARN = []
    QUESTION = ""
    CHROME = True

    def chrome(self):
        # Only header strip and footer; no page title.
        t, self.TITLE = self.TITLE, ""
        self.CH, self.CH_NAME = self.NUM, self.NAME
        super().chrome()
        self.TITLE = t

    def build(self):
        glow = Circle(radius=3.2).set_fill(T.GO, 0.05).set_stroke(width=0).move_to(P(3.6, -0.2))
        glow2 = Circle(radius=2.3).set_fill(T.GO, 0.05).set_stroke(width=0).move_to(P(3.6, -0.2))
        self.add(glow, glow2)
        lab = txt("**CHAPTER**", size=18, color=T.GO)
        num = txt(f"**{self.NUM}**", size=120, color=T.GO)
        name = txt(f"**{self.NAME}**", size=46, color=T.TEXT, width=6.6, lsh=0.9)
        tag = txt(self.TAGLINE, size=T.SIZE_BODY, color=T.TEXT2, width=6.4)
        head = vstack(lab, num, name, tag, buff=0.16)
        self.at(head, X0, 3.1)
        y = head.get_bottom()[1] - 0.3
        if self.LEARN:
            sec = txt("**IN THIS CHAPTER YOU WILL**", size=14, color=T.MUTED)
            bl = bullets(self.LEARN, width=6.4, size=T.SIZE_SMALL, marker="check", marker_color=T.GREEN, gap=0.12)
            g = vstack(sec, bl, buff=0.16)
            self.at(g, X0, y)
            y = g.get_bottom()[1] - 0.25
        if self.QUESTION:
            q = callout("q", self.QUESTION, width=6.4, title="THE BIG QUESTION")
            self.at(q, X0, y)
        art = self.art()
        if art is not None:
            self.add(art)

    def art(self):
        return None
