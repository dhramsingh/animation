"""Shared look and building blocks for the responsive-CSS ManimGL series.

Every scene file does `from rcss_kit import *`, which also re-exports manimlib.
Units: the ManimGL frame is 8 units tall and ~14.2 wide. Diagrams that show
CSS widths convert CSS px to scene units with an explicit scale per scene.
"""
from __future__ import annotations

import math
import re

import numpy as np
from manimlib import *  # noqa: F401,F403

# --------------------------------------------------------------------------
# Palette: one meaning per colour, used the same way in all three videos.
# --------------------------------------------------------------------------
BG = "#0B0F14"
INK = "#E9EEF4"       # primary labels
MUTED = "#8B98A8"     # secondary labels, body-text bars
FAINT = "#3A4555"     # grid lines, inactive things
PANEL = "#121821"     # panel / browser fill
PANEL_2 = "#1A2230"   # card fill
EDGE = "#2C3747"      # panel strokes

PX_C = "#FF7A6B"      # px, device-driven thinking
EM_C = "#3FD5C0"      # em, content-driven thinking
DEV_C = "#F6C453"     # physical devices
CONT_C = "#6CB8FF"    # content / layout
OK_C = "#7BD389"      # constraint satisfied
BAD_C = "#FF4D5E"     # constraint violated
WARN_C = "#FFA94D"    # soft (visual) failure
VIOLET = "#B48CFF"    # at-rules, zoom
PINK_C = "#F38BB5"    # text-measure constraint

SANS = "Inter"
MONO = "DejaVu Sans Mono"   # no ligatures, so ">=" stays ">="


# --------------------------------------------------------------------------
# Text
# --------------------------------------------------------------------------
def txt(s, size=28, color=INK, weight=NORMAL, font=SANS, t2c=None, **kw):
    m = Text(s, font=font, font_size=size, weight=weight, **kw)
    m.set_color(color)
    for key, col in (t2c or {}).items():
        m.set_parts_color(key, col)
    return m


def tex(s, size=40, color=INK, t2c=None, **kw):
    m = Tex(s, font_size=size, t2c=t2c or {}, **kw)
    m.set_color(color)
    for key, col in (t2c or {}).items():
        m.set_parts_color(key, col)
    return m


def mono(s, size=24, color=INK, t2c=None, **kw):
    return txt(s, size, color, font=MONO, t2c=t2c, **kw)


CSS_COLORS = [
    (re.compile(r"[a-z-]+(?=:)"), CONT_C),                     # property names
    (re.compile(r"\b(?:width|inline-size)\b"), CONT_C),         # range syntax
    (re.compile(r"-?\d+(?:\.\d+)?px"), PX_C),
    (re.compile(r"-?\d+(?:\.\d+)?(?:em|rem|ch|fr)\b"), EM_C),
    (re.compile(r"\d+(?:\.\d+)?%"), WARN_C),
    (re.compile(r"@media|@container"), VIOLET),
    (re.compile(r"/\*.*?\*/"), MUTED),
]


def code_panel(lines, size=24, pad=0.28, extra=None, stroke=EDGE, fill=PANEL):
    """A dark rounded panel holding syntax-coloured CSS."""
    if isinstance(lines, str):
        lines = [lines]
    t = Text("\n".join(lines), font=MONO, font_size=size, alignment="LEFT")
    t.set_color(INK)
    for pat, col in CSS_COLORS + list(extra or []):
        try:
            t.set_parts_color(pat, col)
        except Exception:
            pass
    bg = RoundedRectangle(t.get_width() + 2 * pad, t.get_height() + 2 * pad,
                          corner_radius=0.12)
    bg.set_fill(fill, 1).set_stroke(stroke, 1.5)
    bg.move_to(t)
    g = VGroup(bg, t)
    g.bg, g.code = bg, t
    return g


def chapter_tag(n, title, color=EM_C):
    disk = Circle(radius=0.2).set_fill(color, 1).set_stroke(width=0)
    num = txt(str(n), 22, BG, weight=BOLD).move_to(disk)
    label = txt(title, 26, INK)
    g = VGroup(VGroup(disk, num), label).arrange(RIGHT, buff=0.2)
    g.to_corner(UL, buff=0.35)
    return g


def caption(s, size=26, color=MUTED, t2c=None):
    return txt(s, size, color, t2c=t2c).to_edge(DOWN, buff=0.35)


def pill(s, color, size=22, text_color=None, pad=0.14, opacity=0.18):
    t = txt(s, size, text_color or color, weight=BOLD)
    r = RoundedRectangle(t.get_width() + 2 * pad, t.get_height() + 1.3 * pad,
                         corner_radius=(t.get_height() + 1.3 * pad) / 2)
    r.set_fill(color, opacity).set_stroke(color, 1.5).move_to(t)
    return VGroup(r, t)


# --------------------------------------------------------------------------
# Marks
# --------------------------------------------------------------------------
def check_mark(size=0.35, color=OK_C, width=6):
    m = VMobject()
    m.set_points_as_corners([[-0.5, 0.0, 0], [-0.15, -0.38, 0], [0.55, 0.45, 0]])
    m.set_stroke(color, width).set_fill(opacity=0)
    return m.set_height(size)


def cross_mark(size=0.35, color=BAD_C, width=6):
    a = Line(UL, DR).set_stroke(color, width)
    b = Line(DL, UR).set_stroke(color, width)
    return VGroup(a, b).set_height(size)


def warn_sign(size=0.4, color=WARN_C):
    tri = Triangle().set_stroke(color, 3).set_fill(color, 0.15)
    bang = txt("!", 40, color, weight=BOLD).set_height(0.45).move_to(tri).shift(0.07 * DOWN)
    return VGroup(tri, bang).set_height(size)


def eye_icon(size=0.5, color=INK):
    up = ArcBetweenPoints(LEFT, RIGHT, angle=-PI / 2.2)
    down = ArcBetweenPoints(LEFT, RIGHT, angle=PI / 2.2)
    iris = Circle(radius=0.28).set_stroke(color, 3)
    pupil = Dot(radius=0.12, color=color)
    g = VGroup(up, down, iris, pupil)
    VGroup(up, down).set_stroke(color, 3)
    return g.set_width(size)


# --------------------------------------------------------------------------
# Devices (sizes are given directly in scene units)
# --------------------------------------------------------------------------
def tablet(w, h, color=DEV_C, fill=0.06, stroke=2.5):
    bez = 0.06 + 0.03 * min(w, h)
    body = RoundedRectangle(w + 2 * bez, h + 2 * bez,
                            corner_radius=0.08 + 0.06 * min(w, h))
    body.set_stroke(color, stroke).set_fill(color, fill)
    screen = Rectangle(w, h).set_stroke(color, 1, opacity=0.5).set_fill(BG, 1)
    cam = Dot(radius=0.018, fill_color=color).move_to(body.get_top() + bez / 2 * DOWN)
    g = VGroup(body, screen, cam)
    g.screen = screen
    return g


def phone(w, h, color=DEV_C, fill=0.06, stroke=2.5):
    bez = 0.05 + 0.02 * min(w, h)
    body = RoundedRectangle(w + 2 * bez, h + 2 * bez,
                            corner_radius=0.12 + 0.12 * min(w, h))
    body.set_stroke(color, stroke).set_fill(color, fill)
    screen = RoundedRectangle(w, h, corner_radius=0.06 + 0.1 * min(w, h))
    screen.set_stroke(color, 1, opacity=0.5).set_fill(BG, 1)
    notch = RoundedRectangle(w * 0.3, h * 0.035 + 0.02, corner_radius=0.02)
    notch.set_fill(color, 0.8).set_stroke(width=0).move_to(screen.get_top() + 0.04 * DOWN)
    g = VGroup(body, screen, notch)
    g.screen = screen
    return g


def laptop(w, h, color=DEV_C, fill=0.06, stroke=2.5):
    bez = 0.05 + 0.03 * h
    lid = RoundedRectangle(w + 2 * bez, h + 2 * bez, corner_radius=0.06)
    lid.set_stroke(color, stroke).set_fill(color, fill)
    screen = Rectangle(w, h).set_stroke(color, 1, opacity=0.5).set_fill(BG, 1)
    bw = w + 2 * bez
    base = Polygon(
        lid.get_corner(DL) + 0.12 * bw * LEFT,
        lid.get_corner(DR) + 0.12 * bw * RIGHT,
        lid.get_corner(DR) + 0.10 * bw * RIGHT + 0.07 * DOWN,
        lid.get_corner(DL) + 0.10 * bw * LEFT + 0.07 * DOWN,
    )
    base.set_stroke(color, stroke).set_fill(color, 0.25)
    g = VGroup(lid, screen, base)
    g.screen = screen
    return g


def monitor(w, h, color=DEV_C, fill=0.06, stroke=2.5):
    bez = 0.05 + 0.02 * h
    frame = RoundedRectangle(w + 2 * bez, h + 2 * bez, corner_radius=0.05)
    frame.set_stroke(color, stroke).set_fill(color, fill)
    screen = Rectangle(w, h).set_stroke(color, 1, opacity=0.5).set_fill(BG, 1)
    neck = Rectangle(0.1 * w, 0.18 * h).next_to(frame, DOWN, buff=0)
    foot = RoundedRectangle(0.35 * w, 0.04 * h + 0.03, corner_radius=0.02).next_to(neck, DOWN, buff=0)
    VGroup(neck, foot).set_stroke(color, stroke).set_fill(color, 0.25)
    g = VGroup(frame, screen, neck, foot)
    g.screen = screen
    return g


def browser(w, h, bar_h=0.26, stroke=EDGE, fill=PANEL, url=None):
    outer = RoundedRectangle(w, h, corner_radius=min(0.1, w / 8, h / 8))
    outer.set_fill(fill, 1).set_stroke(stroke, 2)
    sep = Line(outer.get_corner(UL) + bar_h * DOWN, outer.get_corner(UR) + bar_h * DOWN)
    sep.set_stroke(stroke, 1.5)
    dots = VGroup(*(Dot(radius=0.035, fill_color=c) for c in ("#FF5F57", "#FEBC2E", "#28C840")))
    dots.arrange(RIGHT, buff=0.06)
    dots.move_to(outer.get_corner(UL) + np.array([0.08 + dots.get_width() / 2, -bar_h / 2, 0]))
    g = VGroup(outer, sep, dots)
    if w > 1.6:
        addr = RoundedRectangle(min(w * 0.45, 3.0), bar_h * 0.55, corner_radius=bar_h * 0.27)
        addr.set_fill(BG, 1).set_stroke(width=0)
        addr.move_to(outer.get_top() + bar_h / 2 * DOWN)
        g.add(addr)
        if url:
            u = txt(url, 12, MUTED).set_height(bar_h * 0.28).move_to(addr)
            g.add(u)
    g.outer = outer
    g.bar_h = bar_h
    return g


def browser_content_box(b):
    """Top-left corner and size of the browser's viewport area."""
    o = b.outer
    tl = o.get_corner(UL) + b.bar_h * DOWN
    return tl, o.get_width(), o.get_height() - b.bar_h


# --------------------------------------------------------------------------
# Cards and text
# --------------------------------------------------------------------------
def card(w, h, accent=CONT_C, need_w=None, show_img=True):
    """A product card. `need_w` is the min-content width of its contents (units).

    When the card is narrower than need_w its content keeps its width and spills
    over the right edge, drawn in red, which is what min-content overflow does.
    """
    broken = need_w is not None and need_w > w + 1e-6
    edge = BAD_C if broken else accent
    body = RoundedRectangle(w, h, corner_radius=min(0.07, w / 6, h / 6))
    body.set_fill(PANEL_2, 1).set_stroke(edge, 2)
    pad = min(0.07, w * 0.08)
    inner_w = max(w - 2 * pad, 0.02)
    cw = (need_w - 2 * pad) if need_w else inner_w
    parts = VGroup(body)
    left = body.get_left()[0] + pad
    top = body.get_top()[1] - pad
    if show_img:
        ih = h * 0.42
        img = Rectangle(inner_w, ih).set_fill(accent, 0.22).set_stroke(width=0)
        img.move_to([left + inner_w / 2, top - ih / 2, 0])
        sun = Dot(radius=min(ih, inner_w) * 0.09, fill_color=accent).set_opacity(0.8)
        sun.move_to(img.get_corner(UR) + np.array([-inner_w * 0.22, -ih * 0.28, 0]))
        mtn = Polygon(img.get_corner(DL), img.get_corner(DL) + np.array([inner_w * 0.38, ih * 0.62, 0]),
                      img.get_corner(DL) + np.array([inner_w * 0.7, 0, 0]))
        mtn.set_fill(accent, 0.55).set_stroke(width=0)
        parts.add(img, sun, mtn)
        top -= ih + h * 0.07
    col = BAD_C if broken else INK
    title = RoundedRectangle(cw * 0.85, h * 0.07, corner_radius=h * 0.035)
    title.set_fill(col, 0.9).set_stroke(width=0)
    title.move_to([left + cw * 0.85 / 2, top - h * 0.035, 0])
    top -= h * 0.13
    lines = VGroup()
    for frac in (1.0, 0.8):
        ln = RoundedRectangle(cw * frac, h * 0.045, corner_radius=h * 0.022)
        ln.set_fill(BAD_C if broken else MUTED, 0.85).set_stroke(width=0)
        ln.move_to([left + cw * frac / 2, top - h * 0.022, 0])
        top -= h * 0.085
        lines.add(ln)
    btn = RoundedRectangle(cw * 0.42, h * 0.1, corner_radius=h * 0.05)
    btn.set_fill(BAD_C if broken else accent, 0.9).set_stroke(width=0)
    btn.move_to([left + cw * 0.21, body.get_bottom()[1] + pad + h * 0.05, 0])
    parts.add(title, lines, btn)
    parts.broken = broken
    return parts


def card_row(n, viewport_w, card_h, pad, gap, need_w=None, accent=CONT_C):
    """n equal cards filling viewport_w with outer padding and gaps (all units)."""
    cw = (viewport_w - 2 * pad - (n - 1) * gap) / n
    cards = VGroup(*(card(cw, card_h, accent, need_w) for _ in range(n)))
    cards.arrange(RIGHT, buff=gap)
    return cards


# Word lengths (in characters) of a real paragraph, used for the text bars.
_PARAGRAPH = (
    "Responsive layouts adapt to the space they are given rather than to the "
    "device that happens to display them. A reader should never have to scroll "
    "sideways, squint at tiny text, or chase a line of prose across a screen so "
    "wide that the eye loses its place on the way back. Good breakpoints come "
    "from the content itself: the width at which a line grows too long, a row of "
    "cards gets too tight, or a navigation bar no longer fits on one line. "
    "Measure those widths, express them in ems, and the layout will follow the "
    "reader's own font size instead of guessing at hardware."
)
WORDS = [len(w) for w in _PARAGRAPH.split()]


def break_lines(word_lens, max_chars):
    lines, cur, used = [], [], 0
    for n in word_lens:
        need = n if not cur else used + 1 + n
        if cur and need > max_chars:
            lines.append(cur)
            cur, used = [n], n
        else:
            cur.append(n)
            used = need
    if cur:
        lines.append(cur)
    return lines


def text_bars(width, char_w, line_h, n_words=None, color=MUTED, bar_frac=0.55,
              max_lines=None, words=None):
    """Body text drawn as rounded word bars, greedily wrapped at `width`.

    Returns a VGroup whose top-left corner sits at the origin. `.lines` holds
    the per-line word counts, `.cpl` the characters per line available.
    """
    words = list(words or WORDS)[: n_words or len(words or WORDS)]
    max_chars = max(1, int(width / char_w + 1e-6))
    lines = break_lines(words, max_chars)
    if max_lines:
        lines = lines[:max_lines]
    bars = VGroup()
    bh = line_h * bar_frac
    for i, line in enumerate(lines):
        x = 0.0
        for n in line:
            wpx = n * char_w
            r = Rectangle(wpx - 0.25 * char_w, bh)
            r.set_fill(color, 0.85).set_stroke(width=0)
            r.move_to([x + (wpx - 0.25 * char_w) / 2, -i * line_h - bh / 2, 0])
            bars.add(r)
            x += (n + 1) * char_w
    bars.lines = lines
    bars.cpl = max_chars
    return bars


# --------------------------------------------------------------------------
# Axes and rulers
# --------------------------------------------------------------------------
def px_line(lo, hi, length, y=0, step=None, labels=None, color=MUTED, label_size=18,
            unit="", tick=0.08, label_color=None):
    """A horizontal number line from lo to hi (values), drawn `length` units wide,
    centred at x=0. Returns (group, value->x function)."""
    def to_x0(v):
        return (v - lo) / (hi - lo) * length - length / 2

    line = Line([to_x0(lo), y, 0], [to_x0(hi), y, 0]).set_stroke(color, 2)

    def to_x(v):
        # follows the line wherever the group has been moved
        a, b = line.get_start()[0], line.get_end()[0]
        return a + (v - lo) / (hi - lo) * (b - a)
    g = VGroup(line)
    ticks = VGroup()
    if step:
        v = math.ceil(lo / step) * step
        while v <= hi + 1e-9:
            ticks.add(Line([to_x(v), y - tick, 0], [to_x(v), y + tick, 0]).set_stroke(color, 1.5))
            v += step
    g.add(ticks)
    labs = VGroup()
    for v in (labels or []):
        lab = txt(f"{v:g}{unit}", label_size, label_color or MUTED)
        lab.next_to([to_x(v), y - tick, 0], DOWN, buff=0.1)
        labs.add(lab)
    g.add(labs)
    g.to_x = to_x
    g.line, g.ticks, g.labels = line, ticks, labs
    return g


def bracket_h(x0, x1, y, color=MUTED, h=0.12, width=2):
    """A ⊓-shaped dimension bracket from x0 to x1 at height y."""
    return VGroup(
        Line([x0, y, 0], [x1, y, 0]),
        Line([x0, y - h / 2, 0], [x0, y + h / 2, 0]),
        Line([x1, y - h / 2, 0], [x1, y + h / 2, 0]),
    ).set_stroke(color, width)


def dim_label(x0, x1, y, s, color=MUTED, size=20, above=True):
    br = bracket_h(x0, x1, y, color)
    lab = txt(s, size, color).next_to(br, UP if above else DOWN, buff=0.08)
    return VGroup(br, lab)


def glow_dot(point, color, radius=0.07):
    halo = Dot(point, radius=radius * 2.4, fill_color=color).set_opacity(0.18)
    core = Dot(point, radius=radius, fill_color=color)
    return VGroup(halo, core)


# --------------------------------------------------------------------------
# Scene base
# --------------------------------------------------------------------------
class RScene(Scene):
    """Common helpers: chapter tag swaps and clean exits."""

    def tag(self, n, title, color=EM_C):
        t = chapter_tag(n, title, color)
        old = getattr(self, "_tag", None)
        if old is not None:
            self.play(FadeOut(old, shift=0.2 * UP), FadeIn(t, shift=0.2 * UP), run_time=0.8)
        else:
            self.play(FadeIn(t, shift=0.2 * DOWN), run_time=0.8)
        self._tag = t
        return t

    def clear_all(self, run_time=0.8, keep=()):
        mobs = [m for m in self.mobjects if m not in keep and m is not self.frame]
        if mobs:
            self.play(*(FadeOut(m) for m in mobs), run_time=run_time)
        self._tag = None if getattr(self, "_tag", None) not in keep else self._tag
        # the caption is gone too; a later FadeOut of it would re-add it for a moment
        if getattr(self, "_cap", None) not in keep:
            self._cap = None

    def say(self, s, size=26, color=MUTED, t2c=None, wait=0.0, run_time=0.6):
        """Swap the bottom caption."""
        new = caption(s, size, color, t2c) if s else None
        old = getattr(self, "_cap", None)
        anims = []
        if old is not None:
            anims.append(FadeOut(old, shift=0.15 * DOWN))
        if new is not None:
            anims.append(FadeIn(new, shift=0.15 * UP))
        if anims:
            self.play(*anims, run_time=run_time)
        self._cap = new
        if wait:
            self.wait(wait)
        return new


def width_tag(mob, s, color=DEV_C, size=20, buff=0.12, ref=None):
    """Dimension bracket + label under a mobject (or its .screen)."""
    r = ref if ref is not None else getattr(mob, "screen", mob)
    y = mob.get_bottom()[1] - buff
    br = bracket_h(r.get_left()[0], r.get_right()[0], y, color, h=0.1)
    lab = txt(s, size, color).next_to(br, DOWN, buff=0.08)
    return VGroup(br, lab)


def title_card(scene, part, lines, subtitle, accent=EM_C, hold=2.5):
    kicker = txt(f"RESPONSIVE CSS  ·  PART {part}", 22, accent, weight=BOLD)
    title = VGroup(*(txt(l, 52, INK, weight=BOLD) for l in lines)).arrange(DOWN, buff=0.18)
    sub = txt(subtitle, 26, MUTED)
    rule = Line(LEFT * 1.2, RIGHT * 1.2).set_stroke(accent, 3)
    g = VGroup(kicker, rule, title, sub).arrange(DOWN, buff=0.3)
    g.move_to(UP * 0.4)
    scene.play(FadeIn(kicker, shift=0.2 * DOWN), ShowCreation(rule), run_time=0.8)
    scene.play(LaggedStartMap(FadeIn, title, shift=0.2 * UP, lag_ratio=0.25), run_time=1.2)
    scene.play(FadeIn(sub), run_time=0.8)
    scene.wait(hold)
    return VGroup(kicker, rule, title, sub)


class Plot(VGroup):
    """Axes along the bottom and left edges of a box (ManimGL's Axes draw
    through the origin, which is off-screen for ranges like 300..1500)."""

    def __init__(self, x_range, y_range, width, height, x_ticks=(), y_ticks=(),
                 x_fmt="{:g}", y_fmt="{:g}", color=MUTED, label_size=16,
                 x_label=None, y_label=None, x_label_color=MUTED, y_label_color=MUTED,
                 x_tick_color=None, y_tick_color=None, grid=False):
        super().__init__()
        self.x0, self.x1 = x_range
        self.y0, self.y1 = y_range
        self.w, self.h = width, height
        self.ref = Dot(ORIGIN, radius=0.001).set_opacity(0)
        self.add(self.ref)
        self.x_axis = Line(self.c2p(self.x0, self.y0), self.c2p(self.x1, self.y0)).set_stroke(color, 2)
        self.y_axis = Line(self.c2p(self.x0, self.y0), self.c2p(self.x0, self.y1)).set_stroke(color, 2)
        self.add(self.x_axis, self.y_axis)
        self.x_labels, self.y_labels, self.grid_lines = VGroup(), VGroup(), VGroup()
        for v in x_ticks:
            p = self.c2p(v, self.y0)
            self.add(Line(p + 0.06 * DOWN, p + 0.06 * UP).set_stroke(color, 1.5))
            lab = txt(x_fmt.format(v), label_size, x_tick_color or color).next_to(p, DOWN, buff=0.12)
            self.x_labels.add(lab)
            if grid:
                self.grid_lines.add(Line(p, self.c2p(v, self.y1)).set_stroke(FAINT, 1))
        for v in y_ticks:
            p = self.c2p(self.x0, v)
            self.add(Line(p + 0.06 * LEFT, p + 0.06 * RIGHT).set_stroke(color, 1.5))
            lab = txt(y_fmt.format(v), label_size, y_tick_color or color).next_to(p, LEFT, buff=0.12)
            self.y_labels.add(lab)
            if grid:
                self.grid_lines.add(Line(p, self.c2p(self.x1, v)).set_stroke(FAINT, 1))
        self.add(self.grid_lines, self.x_labels, self.y_labels)
        if x_label:
            self.x_title = txt(x_label, label_size + 4, x_label_color)
            self.x_title.next_to(self.x_axis, DOWN, buff=0.45)
            self.add(self.x_title)
        if y_label:
            self.y_title = txt(y_label, label_size + 4, y_label_color)
            self.y_title.next_to(self.y_axis, UP, buff=0.15)
            self.y_title.align_to(self.y_axis, LEFT).shift(LEFT * 0.3)
            self.add(self.y_title)

    def c2p(self, x, y):
        o = self.ref.get_center()
        return o + np.array([(x - self.x0) / (self.x1 - self.x0) * self.w,
                             (y - self.y0) / (self.y1 - self.y0) * self.h, 0])

    def x2p(self, x):
        return self.c2p(x, self.y0)[0]

    def graph(self, f, x_min=None, x_max=None, n=240, color=EM_C, width=4):
        xs = np.linspace(self.x0 if x_min is None else x_min, self.x1 if x_max is None else x_max, n)
        pts = [self.c2p(x, f(x)) for x in xs]
        return VMobject().set_points_as_corners(pts).set_stroke(color, width).set_fill(opacity=0)

    def hline(self, y, color=MUTED, width=2, dashed=True, x_min=None, x_max=None):
        a = self.c2p(self.x0 if x_min is None else x_min, y)
        b = self.c2p(self.x1 if x_max is None else x_max, y)
        ln = DashedLine(a, b, dash_length=0.1) if dashed else Line(a, b)
        return ln.set_stroke(color, width)

    def vline(self, x, color=MUTED, width=2, dashed=True, y_min=None, y_max=None):
        a = self.c2p(x, self.y0 if y_min is None else y_min)
        b = self.c2p(x, self.y1 if y_max is None else y_max)
        ln = DashedLine(a, b, dash_length=0.1) if dashed else Line(a, b)
        return ln.set_stroke(color, width)

    def band(self, x_a, x_b, color, opacity=0.15, y_a=None, y_b=None):
        a = self.c2p(x_a, self.y0 if y_a is None else y_a)
        b = self.c2p(x_b, self.y1 if y_b is None else y_b)
        r = Rectangle(abs(b[0] - a[0]), abs(b[1] - a[1])).set_fill(color, opacity).set_stroke(width=0)
        return r.move_to((a + b) / 2)


def double_arrow(a, b, color=MUTED, thickness=2):
    a, b = np.array(a, dtype=float), np.array(b, dtype=float)
    mid = (a + b) / 2
    return VGroup(Arrow(mid, a, buff=0, thickness=thickness, fill_color=color),
                  Arrow(mid, b, buff=0, thickness=thickness, fill_color=color))


# --------------------------------------------------------------------------
# Render speed: ManimGL draws every filled VMobject into an offscreen float
# texture at 2x the output size in each dimension (4x supersampling), then
# composites it. On a GPU that is cheap; on software GL (llvmpipe, i.e. any
# headless render box) it dominates the frame time. Fill edges also get an
# anti-aliased border pass, so a 1x canvas looks the same at 1080p and renders
# several times faster. Set RCSS_FILL_SS=2 to restore ManimGL's default.
# --------------------------------------------------------------------------
def _install_fill_canvas(scale):
    import os as _os
    from functools import lru_cache as _lru

    import moderngl as _mgl
    import manimlib.shader_wrapper as _sw
    from manimlib.config import manim_config as _cfg

    src = _sw.VShaderWrapper.get_fill_canvas
    orig = getattr(src, "__wrapped__", src)

    @_lru
    def get_fill_canvas(ctx):
        size = _cfg.camera.resolution
        tsize = (int(scale * size[0]), int(scale * size[1]))
        fill_texture = ctx.texture(size=tsize, components=4, dtype='f2')
        depth_texture = ctx.texture(size=size, components=1, dtype='f4')
        fill_fbo = ctx.framebuffer(fill_texture)
        depth_fbo = ctx.framebuffer(depth_texture)
        # reuse ManimGL's own compositing program and quad
        _, quad_vao, _ = orig(ctx)
        return (fill_fbo, quad_vao, depth_fbo)

    if scale != 2:
        _sw.VShaderWrapper.get_fill_canvas = staticmethod(get_fill_canvas)


_install_fill_canvas(float(__import__("os").environ.get("RCSS_FILL_SS", "1")))


def _install_scissored_fill():
    """Limit each fill pass (clear, draw, composite) to the object's own
    screen box instead of the whole frame. Valid because no scene in this
    series moves the camera frame. Disable with RCSS_SCISSOR=0."""
    import moderngl as _mgl
    import OpenGL.GL as gl
    import manimlib.shader_wrapper as _sw
    from manimlib.config import manim_config as _cfg
    from manimlib.constants import FRAME_WIDTH as _FW, FRAME_HEIGHT as _FH

    def render_fill(self):
        if self.fill_vao is None:
            return
        W, H = _cfg.camera.resolution
        pts = self.vert_data["point"]
        if len(pts) == 0:
            return
        pad = 6
        x0 = int(max(0, np.floor((pts[:, 0].min() / _FW + 0.5) * W) - pad))
        x1 = int(min(W, np.ceil((pts[:, 0].max() / _FW + 0.5) * W) + pad))
        y0 = int(max(0, np.floor((pts[:, 1].min() / _FH + 0.5) * H) - pad))
        y1 = int(min(H, np.ceil((pts[:, 1].max() / _FH + 0.5) * H) + pad))
        if x1 <= x0 or y1 <= y0:
            return
        box = (x0, y0, x1 - x0, y1 - y0)

        original_fbo = self.ctx.fbo
        fill_tx_fbo, fill_tx_vao, depth_tx_fbo = self.fill_canvas
        old_scissor = original_fbo.scissor
        fill_tx_fbo.scissor = box
        fill_tx_fbo.use()
        fill_tx_fbo.clear(viewport=box)

        apply_depth_test = bool(gl.glGetBooleanv(gl.GL_DEPTH_TEST))
        self.ctx.disable(_mgl.DEPTH_TEST)
        gl.glBlendFuncSeparate(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA,
                               gl.GL_ONE_MINUS_DST_ALPHA, gl.GL_ONE)
        self.fill_vao.render()
        if apply_depth_test:
            self.ctx.enable(_mgl.DEPTH_TEST)
            depth_tx_fbo.clear(1.0)
            depth_tx_fbo.use()
            gl.glBlendFunc(gl.GL_ONE, gl.GL_ONE)
            gl.glBlendEquation(gl.GL_MIN)
            self.fill_depth_vao.render()
        gl.glBlendFunc(gl.GL_ONE, gl.GL_ONE)
        gl.glBlendEquation(gl.GL_MAX)
        self.fill_border_vao.render()

        original_fbo.scissor = box
        original_fbo.use()
        gl.glBlendFunc(gl.GL_ONE, gl.GL_ONE_MINUS_SRC_ALPHA)
        gl.glBlendEquation(gl.GL_FUNC_ADD)
        fill_tx_vao.render()
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        original_fbo.scissor = old_scissor
        original_fbo.use()
        fill_tx_fbo.scissor = None

    _sw.VShaderWrapper.render_fill = render_fill


if __import__("os").environ.get("RCSS_SCISSOR", "1") != "0" and float(__import__("os").environ.get("RCSS_FILL_SS", "1")) == 1:
    _install_scissored_fill()
