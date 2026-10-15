"""Video 2: What a content-driven breakpoint is, and how to find its exact value.

Numbers used throughout (all CSS px at the default 16 px font size):
  card grid  : min card width m = 256 (16em), gap g = 24 (1.5em), page padding p = 16 (1em)
               W_n = n*m + (n-1)*g + 2p  ->  288, 568, 848, 1128  (18, 35.5, 53, 70.5 em)
  navigation : logo 120 + gap 24 + items 64+96+80+60+84 + 4 gaps of 16 + padding 32 = 624 (39em)
  body text  : ~0.5em per character -> 8 px/char; 75 characters need 600 px + 32 padding = 632 (39.5em)
  sidebar    : 66ch text (528) + 32 gap + 240 sidebar + 32 padding = 832 (52em)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rcss_kit import *  # noqa: E402,F401,F403

M_CARD, GAP, PAD = 256, 24, 16
CHAR = 8                      # average glyph advance at 16 px (≈ 0.5em)
NAV_ITEMS = [("Home", 64), ("Products", 96), ("Pricing", 80), ("Docs", 60), ("Contact", 84)]
LOGO_W, NAV_GAP, LOGO_GAP = 120, 16, 24
ITEMS_W = sum(w for _, w in NAV_ITEMS) + NAV_GAP * (len(NAV_ITEMS) - 1)   # 448
NAV_MIN = LOGO_W + LOGO_GAP + ITEMS_W + 2 * PAD                             # 624


def W(n):
    return n * M_CARD + (n - 1) * GAP + 2 * PAD


def cols(w):
    n = 1
    while W(n + 1) <= w and n < 4:
        n += 1
    return n


def card_w(w, n):
    return (w - 2 * PAD - (n - 1) * GAP) / n


def cpl(width_px):
    return int(width_px / CHAR)


def nav_bar(w_px, S, labels, mode="inline", h=0.34):
    """Logo + links (or a hamburger) for a page `w_px` wide, left edge at x=0.

    mode: "inline" draws the links right-aligned and lets them collide with the
    logo when there is not enough room (that collision is drawn red);
    "burger" swaps the links for a menu button.
    """
    g = VGroup()
    logo = RoundedRectangle(LOGO_W * S, h, corner_radius=h / 2).set_fill(EM_C, 0.25).set_stroke(EM_C, 1.5)
    logo.move_to([PAD * S + LOGO_W * S / 2, 0, 0])
    mark = Dot(radius=h * 0.22, fill_color=EM_C).move_to(logo.get_left() + RIGHT * h * 0.5)
    g.add(logo, mark)
    right = (w_px - PAD) * S
    if mode == "burger":
        bars = VGroup(*(Line(LEFT * h * 0.45, RIGHT * h * 0.45).set_stroke(INK, 3) for _ in range(3)))
        bars.arrange(DOWN, buff=h * 0.16).move_to([right - h * 0.45, 0, 0])
        g.add(bars)
        return g
    x = right - ITEMS_W * S
    logo_end = logo.get_right()[0]
    for (name, iw), lab in zip(NAV_ITEMS, labels):
        clash = x < logo_end + 1e-6
        col = BAD_C if clash else INK
        pillr = RoundedRectangle(iw * S, h * 0.8, corner_radius=h * 0.4)
        pillr.set_fill(col, 0.12 if not clash else 0.35).set_stroke(col, 1.2)
        pillr.move_to([x + iw * S / 2, 0, 0])
        t = lab.copy().set_color(col)
        t.set_height(min(h * 0.38, t.get_height()))
        if t.get_width() > iw * S * 0.85:
            t.set_width(iw * S * 0.85)
        t.move_to(pillr)
        g.add(pillr, t)
        x += (iw + NAV_GAP) * S
    return g


def nav_labels(size=20):
    return [txt(n, size, INK) for n, _ in NAV_ITEMS]


# ==========================================================================
class V2S0_Title(RScene):
    def construct(self):
        card_ = title_card(self, 2, ["Content-driven breakpoints"],
                           "break where the content breaks, not where a device sits", EM_C, hold=1.0)
        # tiny demo: a paragraph stretches until its lines get too long
        S = 0.0072
        w = ValueTracker(360)
        X0 = -5.0

        def demo():
            wv = w.get_value()
            b = browser(wv * S, 1.7)
            b.move_to([X0 + wv * S / 2, -2.0, 0])
            tl, bw, bh = browser_content_box(b)
            n = cpl(wv - 2 * PAD)
            col = OK_C if n <= 75 else BAD_C
            bars = text_bars((wv - 2 * PAD) * S, CHAR * S, 0.17, color=col, max_lines=6)
            bars.shift(tl + np.array([PAD * S, -0.15, 0]))
            return VGroup(b, bars)

        d = always_redraw(demo)
        self.play(card_.animate.shift(UP * 0.8), FadeIn(d), run_time=1)
        self.play(w.animate.set_value(632), run_time=2.5)
        mk = Line([X0 + 632 * S, -0.9, 0], [X0 + 632 * S, -3.0, 0]).set_stroke(EM_C, 4)
        ml = txt("75 characters per line: the text says “break here”", 22, EM_C).next_to(mk, RIGHT, buff=0.2).shift(UP * 0.7)
        self.play(ShowCreation(mk), FadeIn(ml))
        self.play(w.animate.set_value(1300), run_time=2)
        self.wait(1.5)
        self.clear_all()


# ==========================================================================
class V2S1_Definition(RScene):
    def construct(self):
        self.tag(1, "A definition you can compute", EM_C)
        pl = Plot((300, 1200), (-450, 450), 7.9, 4.1, x_ticks=(320, 624, 632, 848, 1200),
                  y_ticks=(-400, 0, 400), x_label="viewport width w (CSS px)",
                  y_label="slack g(w) = available − required (px)", label_size=16)
        pl.move_to(LEFT * 2.35 + DOWN * 0.85)
        for i in (1, 2, 3):
            pl.x_labels[i].set_opacity(0)
        pos = pl.band(300, 1200, OK_C, 0.08, 0, 450)
        neg = pl.band(300, 1200, BAD_C, 0.08, -450, 0)
        pl_l = VGroup(txt("constraint holds", 16, OK_C).move_to(pl.c2p(1110, 400)),
                      txt("constraint violated", 16, BAD_C).move_to(pl.c2p(1100, -400)))
        zero = pl.hline(0, INK, 1.5, dashed=False)
        self.play(FadeIn(pl), FadeIn(pos), FadeIn(neg), FadeIn(pl_l), ShowCreation(zero), run_time=1.2)

        def legend_row(icon, formula, color, y):
            sw = Line(LEFT * 0.2, RIGHT * 0.2).set_stroke(color, 5)
            icon.set_height(min(icon.get_height(), 0.32))
            icon.set_width(min(icon.get_width(), 0.65))
            row = VGroup(sw, icon, formula).arrange(RIGHT, buff=0.15)
            row.move_to([2.55, y, 0], aligned_edge=LEFT)
            return row

        # constraint 1: three cards fit
        g1 = pl.graph(lambda w: w - W(3), W(3) - 450, 1200, color=CONT_C)
        r1l = legend_row(card_row(3, 1.0, 0.45, 0.03, 0.05), tex(r"g_{\text{cards}} = w - 848", 28, CONT_C), CONT_C, 0.9)
        self.play(ShowCreation(g1), FadeIn(r1l), run_time=1.5)
        r1 = glow_dot(pl.c2p(848, 0), EM_C, 0.09)
        self.play(FadeIn(r1, scale=0.3), Flash(pl.c2p(848, 0), color=EM_C))
        pl.x_labels[3].set_opacity(1).set_color(CONT_C)
        self.say("Where the slack crosses zero, the layout stops working. That root is the breakpoint.", wait=2.5)

        # constraints 2 and 3
        g2 = pl.graph(lambda w: w - NAV_MIN, 300, NAV_MIN + 450, color=VIOLET)
        ic2 = VGroup(*(RoundedRectangle(0.2, 0.12, corner_radius=0.06).set_stroke(VIOLET, 1.5) for _ in range(4))).arrange(RIGHT, buff=0.04)
        r2l = legend_row(ic2, tex(r"g_{\text{nav}} = w - 624", 28, VIOLET), VIOLET, 0.1)
        g3 = pl.graph(lambda w: (632 - w), 300, 632 + 450, color=PINK_C)
        ic3 = text_bars(0.9, 0.03, 0.08, color=PINK_C, max_lines=3, n_words=30)
        r3l = legend_row(ic3, tex(r"g_{\text{measure}} = 632 - w", 28, PINK_C), PINK_C, -0.7)
        self.play(ShowCreation(g2), FadeIn(r2l), run_time=1.2)
        r2 = glow_dot(pl.c2p(624, 0), EM_C, 0.09)
        self.play(FadeIn(r2, scale=0.3))
        self.play(ShowCreation(g3), FadeIn(r3l), run_time=1.2)
        r3 = glow_dot(pl.c2p(632, 0), EM_C, 0.09)
        self.play(FadeIn(r3, scale=0.3))
        lab = VGroup(txt("624", 16, VIOLET), txt("632", 16, PINK_C)).arrange(RIGHT, buff=0.15)
        lab.next_to(pl.c2p(628, -450), DOWN, buff=0.12)
        self.play(FadeIn(lab))
        self.say("Each constraint of the content has its own root: nav fits, text not too long, cards fit.", wait=2.5)

        defn = VGroup(
            txt("Content-driven breakpoint", 30, EM_C, weight=BOLD),
            tex(r"b^{*}\ \text{ such that }\ g_i(b^{*}) = 0", 36, INK),
        ).arrange(RIGHT, buff=0.5).to_edge(UP, buff=0.9)
        self.play(FadeIn(defn[0], shift=0.2 * DOWN), Write(defn[1]), run_time=1.5)
        deps = VGroup(*(pill(s, CONT_C, 18) for s in ("font size", "text length", "item count", "min widths", "gaps")))
        deps.arrange(RIGHT, buff=0.15).next_to(defn, DOWN, buff=0.2)
        nod = pill("no device anywhere", PX_C, 18).next_to(deps, RIGHT, buff=0.25)
        VGroup(deps, nod).match_x(defn)
        self.play(LaggedStartMap(FadeIn, deps, lag_ratio=0.1), run_time=1)
        self.play(FadeIn(nod, scale=0.8))
        self.say("g depends only on the content. Change the content and the breakpoint moves with it.", wait=3)
        self.clear_all()


# ==========================================================================
class V2S2_StretchTest(RScene):
    def construct(self):
        self.tag(2, "Method 1: the stretch test", EM_C)
        S = 0.0094
        X0 = -6.6
        w = ValueTracker(320)
        state = {"cap": False, "sidebar": False}
        labels = nav_labels()

        def page():
            wv = w.get_value()
            b = browser(wv * S, 3.3, url="blog.example/article")
            b.move_to([X0 + wv * S / 2, 1.45, 0])
            tl, bw, bh = browser_content_box(b)
            nav = nav_bar(wv, S, labels, "burger" if wv < NAV_MIN else "inline", h=0.26)
            nav.shift(tl + np.array([0, -0.22, 0]))
            avail = wv - 2 * PAD
            side = state["sidebar"] and wv >= 832
            if side:
                avail = wv - 2 * PAD - 32 - 240
            text_w = min(avail, 66 * CHAR) if state["cap"] else avail
            n = cpl(text_w)
            col = WARN_C if n < 45 else (OK_C if n <= 75 else BAD_C)
            x_text = PAD * S
            if state["cap"] and not side:
                x_text = (wv * S - text_w * S) / 2
            h1 = RoundedRectangle(min(text_w * 0.7, 420) * S, 0.17, corner_radius=0.08).set_fill(INK, 0.9).set_stroke(width=0)
            h1.move_to(tl + np.array([x_text + h1.get_width() / 2, -0.62, 0]))
            bars = text_bars(text_w * S, CHAR * S, 0.2, color=MUTED, max_lines=9)
            bars.shift(tl + np.array([x_text, -0.9, 0]))
            g = VGroup(b, nav, h1, bars)
            if len(bars.lines) > 1:
                line1 = VGroup(*bars[: len(bars.lines[0])])
                hl = SurroundingRectangle(line1, buff=0.03).set_stroke(width=0).set_fill(col, 0.22)
                start2 = bars[len(bars.lines[0])]
                sweep = CurvedArrow(line1.get_right() + 0.05 * RIGHT, start2.get_left() + 0.05 * LEFT, angle=-0.35)
                sweep.set_color(col)
                g.add(hl, sweep)
            if side:
                sb = RoundedRectangle(240 * S, 2.0, corner_radius=0.06).set_fill(EM_C, 0.12).set_stroke(EM_C, 1.5)
                sb.move_to(tl + np.array([wv * S - PAD * S - 120 * S, -0.62 - 1.0, 0]))
                sbt = RoundedRectangle(150 * S, 0.12, corner_radius=0.06).set_fill(EM_C, 0.8).set_stroke(width=0)
                sbt.move_to(sb.get_corner(UL) + np.array([0.12 + 75 * S, -0.18, 0]))
                sbb = text_bars(200 * S, CHAR * S, 0.2, color=EM_C, max_lines=6, n_words=30).set_opacity(0.6)
                sbb.shift(sb.get_corner(UL) + np.array([0.12, -0.38, 0]))
                g.add(sb, sbt, sbb)
            return g

        site = always_redraw(page)

        # characters-per-line gauge
        GX0, GX1, GY = -6.2, -0.4, -1.55
        lo, hi = 20, 120

        def gx(v):
            return GX0 + (v - lo) / (hi - lo) * (GX1 - GX0)

        zones = VGroup(
            Rectangle(gx(45) - gx(lo), 0.22).set_fill(WARN_C, 0.5).move_to([(gx(lo) + gx(45)) / 2, GY, 0]),
            Rectangle(gx(75) - gx(45), 0.22).set_fill(OK_C, 0.6).move_to([(gx(45) + gx(75)) / 2, GY, 0]),
            Rectangle(gx(hi) - gx(75), 0.22).set_fill(BAD_C, 0.5).move_to([(gx(75) + gx(hi)) / 2, GY, 0]),
        ).set_stroke(width=0)
        zl = VGroup(*(txt(s, 16, MUTED).next_to([gx(v), GY - 0.11, 0], DOWN, buff=0.08) for s, v in (("45", 45), ("75", 75))))
        gt = txt("characters per line", 18, MUTED).next_to(zones, UP, buff=0.12).align_to(zones, LEFT)

        def needle_val():
            wv = w.get_value()
            avail = wv - 2 * PAD - (32 + 240 if state["sidebar"] and wv >= 832 else 0)
            return cpl(min(avail, 66 * CHAR) if state["cap"] else avail)

        needle = always_redraw(lambda: Triangle().set_fill(INK, 1).set_stroke(width=0).set_height(0.16).rotate(PI)
                               .move_to([gx(min(max(needle_val(), lo), hi)), GY + 0.24, 0]))
        cpl_num = Integer(36, font_size=34, color=INK)
        cpl_num.add_updater(lambda m: m.set_value(needle_val()))
        cpl_num.add_updater(lambda m: m.next_to(zones, RIGHT, buff=0.3))

        # width axis shares the browser scale, so the browser's edge sits over w
        nl = px_line(0, 1350, 1350 * S, y=-2.75, step=50, labels=[320, 632, 832, 1200], label_size=16)
        nl.shift(RIGHT * (X0 - nl.to_x(0)))
        to_x = lambda v: X0 + v * S  # noqa: E731
        cur = always_redraw(lambda: glow_dot([to_x(w.get_value()), -2.75, 0], INK, 0.07))
        wl = always_redraw(lambda: txt(f"w = {w.get_value():.0f} px", 20, INK).next_to([to_x(w.get_value()), -2.75, 0], UP, buff=0.18))

        eye = eye_icon(0.5).move_to([1.5, -1.45, 0])
        eye_t = VGroup(txt("arrow = the eye's", 16, MUTED), txt("return sweep", 16, MUTED)).arrange(DOWN, buff=0.05, aligned_edge=LEFT)
        eye_t.next_to(eye, RIGHT, buff=0.15)
        self.play(FadeIn(site), run_time=1)
        self.play(FadeIn(zones), FadeIn(zl), FadeIn(gt), FadeIn(needle), FadeIn(cpl_num), FadeIn(nl), FadeIn(cur), FadeIn(wl),
                  FadeIn(eye), FadeIn(eye_t), run_time=1)
        self.say("Start at the narrowest width (mobile first). Widen slowly. Watch the content.", wait=1)
        self.play(w.animate.set_value(392), run_time=2.5, rate_func=linear)
        self.say("Below 45 characters, lines are choppy. From 392 px the text reads well.", wait=1)
        self.play(w.animate.set_value(624), run_time=4, rate_func=linear)
        self.say("624 px: the links fit in one row, so the menu button can go.", wait=1.5)
        self.play(w.animate.set_value(632), run_time=1, rate_func=linear)
        mark = Line([to_x(632), -2.6, 0], [to_x(632), -0.3, 0]).set_stroke(EM_C, 3)
        mk_l = txt("632 px: 75 characters", 20, EM_C, weight=BOLD).next_to(mark.get_top(), DL, buff=0.08).shift(DOWN * 0.1)
        self.play(ShowCreation(mark), FadeIn(mk_l))
        self.say("At 632 px each line holds 75 characters: the measure is at its limit.", wait=1)
        self.play(w.animate.set_value(900), run_time=3, rate_func=linear)
        self.say("Keep going and lines run to 100+ characters: the eye's return sweep gets lost.", wait=2.5)

        # two ways to respond
        opt = VGroup(
            VGroup(txt("A  absorb it", 18, OK_C, weight=BOLD), code_panel(["article { max-width: 66ch; }"], 13, pad=0.2)).arrange(DOWN, buff=0.08, aligned_edge=LEFT),
            VGroup(txt("B  break here", 18, EM_C, weight=BOLD), code_panel(["@media (width >= 39.5em) {…}"], 13, pad=0.2)).arrange(DOWN, buff=0.08, aligned_edge=LEFT),
        ).arrange(RIGHT, buff=0.2, aligned_edge=UP)
        opt.move_to([3.95, -1.5, 0])
        self.play(FadeOut(eye), FadeOut(eye_t), FadeIn(opt[0], shift=0.2 * LEFT), run_time=0.8)
        self.play(FadeIn(opt[1], shift=0.2 * LEFT), run_time=0.8)
        self.say("Two answers: let intrinsic CSS absorb it, or add a breakpoint at that width.", wait=2)
        state["cap"] = True
        self.play(Indicate(opt[0], color=OK_C, scale_factor=1.05), opt[1].animate.set_opacity(0.3), run_time=1)
        self.say("Capping the measure fixes it with no breakpoint at all. The margins take the extra room.", wait=2)
        self.play(w.animate.set_value(832), run_time=2, rate_func=linear)
        self.say("Now the empty margins are the problem. At 832 px a 15em sidebar fits beside 66ch of text.", wait=1.5)
        state["sidebar"] = True
        mark2 = Line([to_x(832), -2.6, 0], [to_x(832), -0.3, 0]).set_stroke(EM_C, 3)
        mk2_l = txt("832 px = 52em: sidebar fits", 20, EM_C, weight=BOLD).next_to(mark2.get_top(), DR, buff=0.08).shift(DOWN * 0.1)
        self.play(ShowCreation(mark2), FadeIn(mk2_l))
        self.play(w.animate.set_value(1200), run_time=3, rate_func=linear)
        self.say("Each breakpoint was found by watching content, not by looking up a device.", wait=3)
        cpl_num.clear_updaters()
        self.clear_all()


# ==========================================================================
def mini(title, test, color, build):
    """A mini browser illustration with a title and a measurable test."""
    b = browser(2.9, 1.6, bar_h=0.18)
    tl, bw, bh = browser_content_box(b)
    content = build(tl, bw, bh)
    t = txt(title, 22, color, weight=BOLD).next_to(b, UP, buff=0.12)
    m = mono(test, 16, MUTED).next_to(b, DOWN, buff=0.12)
    g = VGroup(t, b, content, m)
    g.frame_ = b
    return g


def _overflow(tl, bw, bh):
    g = VGroup()
    wide = Rectangle(bw * 1.12, 0.55).set_fill(BAD_C, 0.25).set_stroke(BAD_C, 2)
    wide.move_to(tl + np.array([0.1 + wide.get_width() / 2, -0.45, 0]))
    bars = text_bars(bw - 0.2, 0.05, 0.13, max_lines=2, n_words=30).shift(tl + np.array([0.1, -0.85, 0]))
    sb = RoundedRectangle(bw * 0.6, 0.06, corner_radius=0.03).set_fill(MUTED, 0.9).set_stroke(width=0)
    sb.move_to(tl + np.array([0.1 + bw * 0.3, -bh + 0.07, 0]))
    arrow = Arrow(LEFT * 0.25, RIGHT * 0.25, buff=0, thickness=2, fill_color=BAD_C).next_to(wide, UP, buff=0.04).align_to(wide, RIGHT)
    return g.add(wide, bars, sb, arrow)


def _collision(tl, bw, bh):
    S = bw / 520
    nav = nav_bar(520, S, nav_labels(14), "inline", h=0.22).shift(tl + np.array([0, -0.2, 0]))
    bars = text_bars(bw - 0.2, 0.05, 0.13, max_lines=4, n_words=40).shift(tl + np.array([0.1, -0.5, 0]))
    return VGroup(nav, bars)


def _clip(tl, bw, bh):
    g = VGroup()
    for i in range(3):
        c = RoundedRectangle(bw / 3 - 0.08, bh - 0.2, corner_radius=0.05).set_fill(PANEL_2, 1).set_stroke(CONT_C, 1.2)
        c.move_to(tl + np.array([0.04 + (i + 0.5) * bw / 3, -bh / 2, 0]))
        btn = RoundedRectangle(bw / 3 - 0.16, 0.2, corner_radius=0.1).set_fill(CONT_C, 0.8).set_stroke(width=0)
        btn.move_to(c.get_bottom() + UP * 0.2)
        lab = txt("Add to ca…", 12, BG, weight=BOLD).move_to(btn)
        lab.set_width(min(lab.get_width(), btn.get_width() * 0.9))
        g.add(c, btn, lab)
    g.add(SurroundingRectangle(g[-2:], buff=0.04).set_stroke(BAD_C, 2))
    return g


def _orphan(tl, bw, bh):
    g = VGroup()
    items = [0.5, 0.75, 0.6, 0.45]
    x = 0.1
    for k, iw in enumerate(items):
        p = RoundedRectangle(iw, 0.16, corner_radius=0.08).set_stroke(INK, 1.2).set_fill(INK, 0.1)
        p.move_to(tl + np.array([x + iw / 2, -0.18, 0]))
        x += iw + 0.08
        g.add(p)
    lone = RoundedRectangle(0.62, 0.16, corner_radius=0.08).set_stroke(BAD_C, 2).set_fill(BAD_C, 0.2)
    lone.move_to(tl + np.array([0.1 + 0.31, -0.42, 0]))
    bars = text_bars(bw - 0.2, 0.05, 0.13, max_lines=4, n_words=40).shift(tl + np.array([0.1, -0.65, 0]))
    return g.add(lone, bars)


def _long(tl, bw, bh):
    bars = text_bars(bw - 0.1, 0.022, 0.12, max_lines=8, color=MUTED).shift(tl + np.array([0.05, -0.15, 0]))
    sweep = CurvedArrow(bars[0].get_left() + (bw - 0.15) * RIGHT, tl + np.array([0.05, -0.27, 0]), angle=-0.25).set_color(WARN_C)
    return VGroup(bars, sweep)


def _whitespace(tl, bw, bh):
    col = RoundedRectangle(0.75, bh - 0.2, corner_radius=0.04).set_fill(PANEL_2, 1).set_stroke(EDGE, 1)
    col.move_to(tl + np.array([bw / 2, -bh / 2, 0]))
    bars = text_bars(0.62, 0.03, 0.12, max_lines=8, n_words=40).shift(col.get_corner(UL) + np.array([0.06, -0.08, 0]))
    l = double_arrow(tl + np.array([0.08, -bh / 2, 0]), col.get_left() + LEFT * 0.05, WARN_C, 1.5)
    r = double_arrow(col.get_right() + RIGHT * 0.05, tl + np.array([bw - 0.08, -bh / 2, 0]), WARN_C, 1.5)
    return VGroup(col, bars, l, r)


def _upscaled(tl, bw, bh):
    g = VGroup()
    rng = np.random.default_rng(3)
    n_c, n_r = 10, 4
    cw, ch = (bw - 0.2) / n_c, (bh - 0.25) / n_r
    for r in range(n_r):
        for c in range(n_c):
            sq = Rectangle(cw, ch).set_stroke(width=0)
            sq.set_fill(interpolate_color(CONT_C, WARN_C, rng.random() * 0.6), 0.35 + 0.4 * rng.random())
            sq.move_to(tl + np.array([0.1 + (c + 0.5) * cw, -0.12 - (r + 0.5) * ch, 0]))
            g.add(sq)
    return g


def _awkward(tl, bw, bh):
    c = RoundedRectangle(bw - 0.2, bh - 0.2, corner_radius=0.05).set_fill(PANEL_2, 1).set_stroke(WARN_C, 1.5)
    c.move_to(tl + np.array([bw / 2, -bh / 2, 0]))
    img = Rectangle(bw - 0.3, 0.4).set_fill(CONT_C, 0.3).set_stroke(width=0).move_to(c.get_top() + DOWN * 0.27)
    t = RoundedRectangle(0.5, 0.08, corner_radius=0.04).set_fill(INK, 0.8).set_stroke(width=0).move_to(c.get_left() + RIGHT * 0.37 + DOWN * 0.05)
    btn = RoundedRectangle(bw - 0.4, 0.16, corner_radius=0.08).set_fill(CONT_C, 0.8).set_stroke(width=0).move_to(c.get_bottom() + UP * 0.2)
    return VGroup(c, img, t, btn)


class V2S3_StructuralVsVisual(RScene):
    def construct(self):
        self.tag(3, "Two ways a layout breaks", EM_C)
        hdr_s = txt("STRUCTURAL: the layout fails", 26, BAD_C, weight=BOLD)
        hdr_v = txt("VISUAL: the layout degrades", 26, WARN_C, weight=BOLD)
        structural = [
            ("Overflow", "scrollWidth > clientWidth", _overflow),
            ("Collision", "Σ item widths > w", _collision),
            ("Clipping", "min-content > box", _clip),
            ("Orphan wrap", "rows(nav) > 1", _orphan),
        ]
        visual = [
            ("Line too long", "chars per line > 75", _long),
            ("Wasted space", "content / w < ½", _whitespace),
            ("Upscaled image", "drawn width > intrinsic", _upscaled),
            ("Stretched card", "aspect ratio off", _awkward),
        ]
        row1 = VGroup(*(mini(t, test, BAD_C, f) for t, test, f in structural))
        row2 = VGroup(*(mini(t, test, WARN_C, f) for t, test, f in visual))
        for row, y in ((row1, 1.45), (row2, -1.55)):
            for k, m in enumerate(row):
                m.shift(np.array([-5.3 + 3.55 * k, y, 0]) - m.frame_.get_center())
        hdr_s.move_to(UP * 2.95)
        hdr_v.move_to(UP * 0.05)
        self.play(FadeIn(hdr_s, shift=0.2 * DOWN))
        for m in row1:
            self.play(FadeIn(m, lag_ratio=0.05), run_time=0.9)
            self.wait(0.5)
        self.say("Structural breaks are objective: something overflows, collides, clips or wraps.", wait=1.5)
        self.play(FadeIn(hdr_v, shift=0.2 * DOWN))
        for m in row2:
            self.play(FadeIn(m, lag_ratio=0.05), run_time=0.9)
            self.wait(0.5)
        self.say("Visual breaks are softer, but still measurable against a threshold.", wait=2)
        self.play(*(Indicate(m[3], color=INK, scale_factor=1.08) for m in (*row1, *row2)), run_time=1.2)
        self.say("Either way, each failure is an inequality in w, and its boundary is a breakpoint.", wait=3)
        self.clear_all()


# ==========================================================================
class V2S4_Analytic(RScene):
    def construct(self):
        self.tag(4, "Method 2: compute it from the content", EM_C)
        # ---- the card grid as a ruler
        S = 0.0122
        segs = [("p", PAD, MUTED), ("m", M_CARD, CONT_C), ("g", GAP, FAINT), ("m", M_CARD, CONT_C), ("g", GAP, FAINT),
                ("m", M_CARD, CONT_C), ("p", PAD, MUTED)]
        x = -W(3) * S / 2
        strip = VGroup()
        labs = VGroup()
        Y = 1.6
        for name, px, col in segs:
            r = Rectangle(px * S, 0.5).set_fill(col, 0.35 if col != FAINT else 0.8).set_stroke(col if col != FAINT else MUTED, 1.5)
            r.move_to([x + px * S / 2, Y, 0])
            strip.add(r)
            if name == "m":
                labs.add(tex(rf"m = {px}", 28, CONT_C).next_to(r, UP, buff=0.12))
            else:
                labs.add(txt(f"{name}={px}", 14, MUTED).next_to(r, UP, buff=0.12))
            x += px * S
        cards = VGroup(*(card(r.get_width() - 0.06, 1.25, CONT_C) for r in strip[1::2]))
        for c_, r in zip(cards, strip[1::2]):
            c_.next_to(r, DOWN, buff=0.15)
        total = Brace(strip, DOWN, buff=0.15 + 1.45)
        tot_l = tex(r"W_3 = 3\cdot 256 + 2\cdot 24 + 2\cdot 16 = 848\ \text{px}", 34, EM_C).next_to(total, DOWN, buff=0.15)
        self.play(LaggedStartMap(GrowFromEdge, strip, edge=LEFT, lag_ratio=0.15), run_time=1.5)
        self.play(FadeIn(labs, lag_ratio=0.1), LaggedStartMap(FadeIn, cards, shift=0.2 * UP, lag_ratio=0.2), run_time=1.2)
        self.play(GrowFromCenter(total), Write(tot_l), run_time=1.5)
        gen = tex(r"W_n = n\,m + (n-1)\,g + 2p", 40, INK).to_edge(UP, buff=1.0).shift(RIGHT * 2.5)
        self.play(Write(gen))
        self.say("A grid of n cards needs n minimum widths, n−1 gaps and the page padding.", wait=2)

        # table of thresholds
        rows = [("n", r"W_n\ (\text{px})", r"W_n / 16"), ("1", "288", "18em"), ("2", "568", "35.5em"),
                ("3", "848", "53em"), ("4", "1128", "70.5em")]
        tbl = VGroup()
        for i, (a, b_, c_) in enumerate(rows):
            col = MUTED if i == 0 else INK
            r = VGroup(tex(a, 34, col), tex(b_, 34, col if i == 0 else CONT_C), tex(c_.replace("em", r"\,\text{em}"), 34, col if i == 0 else EM_C))
            for k, m in enumerate(r):
                m.move_to([k * 2.2, -i * 0.58, 0])
            tbl.add(r)
        tbl.move_to(DOWN * 1.25)
        line = Line(LEFT * 1.2, RIGHT * 5).set_stroke(EDGE, 1.5).next_to(tbl[0], DOWN, buff=0.12)
        line.match_x(tbl)
        self.play(FadeOut(VGroup(total, tot_l, cards)), FadeOut(self._cap), run_time=1)
        self._cap = None
        self.play(FadeIn(tbl[0]), ShowCreation(line))
        self.play(LaggedStartMap(FadeIn, tbl[1:], shift=0.2 * DOWN, lag_ratio=0.25), run_time=1.6)
        self.play(Indicate(tbl[3], color=EM_C))
        self.say("Every row is a candidate breakpoint, derived from three content measurements.", wait=2.5)
        self.clear_all()

        # ---- the nav bar
        self.tag(4, "Method 2: compute it from the content", EM_C)
        S = 0.0145
        labels = nav_labels(22)
        nv = nav_bar(NAV_MIN, S, labels, "inline", h=0.5)
        nv.move_to(UP * 1.4)
        frame_ = Rectangle(NAV_MIN * S, 0.8).set_stroke(EDGE, 2).move_to(nv).align_to(nv, LEFT).shift(LEFT * 0.0)
        frame_.set_x(nv.get_x())
        frame_.stretch_to_fit_width(NAV_MIN * S).move_to([nv[0].get_left()[0] - PAD * S + NAV_MIN * S / 2, nv.get_y(), 0])
        self.play(FadeIn(frame_), FadeIn(nv, lag_ratio=0.1), run_time=1.2)
        x = frame_.get_left()[0]
        dims = VGroup()
        pieces = [("p", PAD), ("logo", LOGO_W), ("≥gap", LOGO_GAP)]
        for (nm, iw) in NAV_ITEMS:
            pieces += [(nm, iw), ("g", NAV_GAP)]
        pieces = pieces[:-1] + [("p", PAD)]
        for nm, px in pieces:
            d = dim_label(x, x + px * S - 0.02, nv.get_bottom()[1] - 0.3, str(px), MUTED, 14, above=False)
            dims.add(d)
            x += px * S
        self.play(LaggedStartMap(FadeIn, dims, lag_ratio=0.06), run_time=2)
        sum_t = tex(r"16 + 120 + 24 + (64+96+80+60+84) + 4\cdot 16 + 16 = 624\ \text{px} = 39\,\text{em}", 32, VIOLET)
        sum_t.next_to(dims, DOWN, buff=0.45)
        self.play(Write(sum_t), run_time=2)
        self.say("Measure each item's intrinsic width once. Their sum is the nav's breakpoint.", wait=2)

        # squeeze it to see the break happen
        w = ValueTracker(NAV_MIN + 120)
        S2 = 0.0118

        def squeeze():
            wv = w.get_value()
            b = browser(wv * S2, 1.1)
            b.move_to([-5.6 + wv * S2 / 2, -2.2, 0])
            tl, bw, bh = browser_content_box(b)
            n = nav_bar(wv, S2, labels, "inline", h=0.36).shift(tl + np.array([0, -0.35, 0]))
            r = txt(f"{wv:.0f} px", 22, BAD_C if wv < NAV_MIN else INK).next_to(b, RIGHT, buff=0.3)
            return VGroup(b, n, r)

        sq = always_redraw(squeeze)
        self.play(FadeOut(dims), FadeOut(frame_), nv.animate.set_opacity(0.4), FadeIn(sq), run_time=1)
        self.play(w.animate.set_value(NAV_MIN), run_time=2.5)
        self.wait(0.8)
        self.play(w.animate.set_value(540), run_time=2.5)
        self.say("Below 624 px the links run into the logo: a structural break, exactly where predicted.", wait=2.5)
        self.clear_all()

        # ---- the measure
        self.tag(4, "Method 2: compute it from the content", EM_C)
        f = tex(r"\text{chars per line} \approx \frac{w - 2p}{0.5\,\text{em}}", 40, INK).move_to(UP * 2.35)
        self.play(Write(f), run_time=1.5)
        S = 0.0172
        x0 = -632 * S / 2
        Y = 0.55
        padl = Rectangle(PAD * S, 0.55).set_fill(MUTED, 0.35).set_stroke(MUTED, 1).move_to([x0 + PAD * S / 2, Y, 0])
        glyphs = VGroup(*(Rectangle(CHAR * S, 0.55).set_stroke(PINK_C, 0.8).set_fill(PINK_C, 0.12 + 0.1 * (k % 2))
                          .move_to([x0 + (PAD + CHAR * (k + 0.5)) * S, Y, 0]) for k in range(75)))
        padr = padl.copy().move_to([x0 + (632 - PAD / 2) * S, Y, 0])
        self.play(FadeIn(padl), LaggedStartMap(FadeIn, glyphs, lag_ratio=0.02), FadeIn(padr), run_time=2)
        b1 = Brace(glyphs, UP, buff=0.08)
        b1l = tex(r"75 \times 8\ \text{px} = 600\ \text{px}", 30, PINK_C).next_to(b1, UP, buff=0.08)
        b2 = Brace(VGroup(padl, padr), DOWN, buff=0.12)
        b2l = tex(r"600 + 2\cdot 16 = 632\ \text{px} = 39.5\,\text{em}", 34, EM_C).next_to(b2, DOWN, buff=0.12)
        gl = txt("one cell = one average glyph ≈ 0.5em = 8 px at a 16 px font", 20, MUTED).next_to(b2l, DOWN, buff=0.35)
        self.play(GrowFromCenter(b1), FadeIn(b1l), run_time=1)
        self.play(GrowFromCenter(b2), Write(b2l), FadeIn(gl), run_time=1.5)
        self.say("Same idea for text: the measure limit gives the width directly.", wait=2.5)
        self.clear_all()


# ==========================================================================
def thumb(n_cards, burger, wpx, S=0.0042, h=1.05):
    b = browser(wpx * S, h, bar_h=0.12)
    tl, bw, bh = browser_content_box(b)
    nav = nav_bar(wpx, S, nav_labels(10), "burger" if burger else "inline", h=0.12).shift(tl + np.array([0, -0.1, 0]))
    cw = card_w(wpx, n_cards) * S
    cs = VGroup(*(card(cw, 0.55, CONT_C, show_img=True) for _ in range(n_cards))).arrange(RIGHT, buff=GAP * S)
    cs.move_to(tl + np.array([PAD * S + cs.get_width() / 2, -0.25 - 0.28, 0]))
    return VGroup(b, nav, cs)


class V2S5_ConstraintMap(RScene):
    def construct(self):
        self.tag(5, "The constraint map", EM_C)
        lo, hi = 300, 1300
        L = 10.6
        X0 = -4.2

        def x(v):
            return X0 + (v - lo) / (hi - lo) * L

        rows = [
            ("nav fits in one row", lambda v: v >= NAV_MIN, VIOLET),
            ("2 cards fit", lambda v: v >= W(2), CONT_C),
            ("3 cards fit", lambda v: v >= W(3), CONT_C),
            ("4 cards fit", lambda v: v >= W(4), CONT_C),
            ("text ≥ 45 ch", lambda v: v >= 392, PINK_C),
            ("text ≤ 75 ch", lambda v: v <= 632, PINK_C),
        ]
        Y0, DY = 2.3, 0.55
        grid = VGroup()
        bars = VGroup()
        for i, (name, ok, col) in enumerate(rows):
            y = Y0 - i * DY
            lab = txt(name, 20, col).move_to([X0 - 0.2, y, 0], aligned_edge=RIGHT)
            # find the transition
            edges = [lo] + [v for v in (392, 568, 624, 632, 848, 1128) if ok(v) != ok(v - 0.5)] + [hi]
            segs = VGroup()
            for a, bnd in zip(edges[:-1], edges[1:]):
                good = ok((a + bnd) / 2)
                r = Rectangle(x(bnd) - x(a), 0.36).set_fill(OK_C if good else BAD_C, 0.55 if good else 0.35).set_stroke(BG, 1)
                r.move_to([(x(a) + x(bnd)) / 2, y, 0])
                segs.add(r)
            grid.add(lab)
            bars.add(segs)
        nl = px_line(lo, hi, L, y=Y0 - len(rows) * DY + 0.05, step=50, labels=[320, 568, 624, 848, 1128], label_size=15)
        nl.shift(RIGHT * (X0 + L / 2))
        for i, (name, ok, col) in enumerate(rows):
            self.play(FadeIn(grid[i]), LaggedStartMap(GrowFromEdge, bars[i], edge=LEFT, lag_ratio=0.3), run_time=0.7)
        self.play(FadeIn(nl))
        self.say("Each constraint is green where it holds and red where it fails.", wait=2)

        # the text-too-long row is absorbed by max-width: 66ch
        fix = code_panel(["max-width: 66ch"], 16).next_to(bars[5], RIGHT, buff=0.1)
        fix.move_to([x(1050), Y0 - 5 * DY, 0])
        self.play(FadeIn(fix))
        self.play(*(s.animate.set_fill(OK_C, 0.55) for s in bars[5]), run_time=1)
        self.say("A constraint that intrinsic CSS can absorb needs no breakpoint.", wait=1.5)
        self.play(FadeOut(fix))

        cuts = [W(2), NAV_MIN, W(3), W(4)]
        vls = VGroup(*(DashedLine([x(v), Y0 + 0.35, 0], [x(v), nl.get_y() - 0.1, 0], dash_length=0.08).set_stroke(EM_C, 2.5) for v in cuts))
        self.play(LaggedStartMap(ShowCreation, vls, lag_ratio=0.2), run_time=1.5)
        self.say("Breakpoints are the vertical lines where any row changes colour.", wait=1.5)

        # one layout per interval, shown in an even row and linked to its interval
        spans = [(320, W(2), 1, True, 440), (W(2), NAV_MIN, 2, True, 596), (NAV_MIN, W(3), 2, False, 736),
                 (W(3), W(4), 3, False, 988), (W(4), 1300, 4, False, 1214)]
        thumbs = VGroup()
        links = VGroup()
        tx = [-5.6, -2.85, -0.1, 2.65, 5.4]
        for (a, bnd, n, burger, rep_w), cx in zip(spans, tx):
            t = thumb(n, burger, rep_w, S=2.4 / rep_w, h=1.15)
            t.move_to([cx, -2.45, 0])
            rng_l = txt(f"{a}–{bnd - 1 if bnd < 1300 else '∞'}", 16, MUTED).next_to(t, UP, buff=0.08)
            thumbs.add(VGroup(t, rng_l))
            links.add(Line([(x(a) + x(bnd)) / 2, nl.get_y() - 0.35, 0], rng_l.get_top() + UP * 0.05).set_stroke(EDGE, 1.5))
        self.play(LaggedStartMap(ShowCreation, links, lag_ratio=0.15), LaggedStartMap(FadeIn, thumbs, shift=0.2 * UP, lag_ratio=0.2), run_time=2)
        self.say("Between breakpoints, one layout satisfies every row.", wait=2)
        css = code_panel([
            "@media (width >= 35.5em) { .grid { --cols: 2 } }",
            "@media (width >= 39em)   { .nav  { display: flex } }",
            "@media (width >= 53em)   { .grid { --cols: 3 } }",
            "@media (width >= 70.5em) { .grid { --cols: 4 } }",
        ], 18)
        css.move_to([0, -2.4, 0])
        self.play(FadeOut(thumbs), FadeOut(links), FadeOut(self._cap), run_time=0.8)
        self._cap = None
        self.play(FadeIn(css, shift=0.2 * UP), run_time=1)
        self.say("Four breakpoints, every one traceable to a measurement of the content.", wait=3)
        self.clear_all()


# ==========================================================================
class V2S6_Procedure(RScene):
    def construct(self):
        self.tag(6, "The procedure", EM_C)

        def box(s_, col=INK, w=2.6, h=0.75, size=20):
            r = RoundedRectangle(w, h, corner_radius=0.15).set_fill(PANEL, 1).set_stroke(col, 2)
            t = txt(s_, size, col)
            if t.get_width() > w - 0.25:
                t.set_width(w - 0.25)
            return VGroup(r, t.move_to(r))

        def diamond(s_, col=WARN_C, w=3.2, h=1.3):
            d = Polygon(UP * h / 2, RIGHT * w / 2, DOWN * h / 2, LEFT * w / 2).set_fill(PANEL, 1).set_stroke(col, 2)
            t = txt(s_, 18, col)
            if t.get_width() > w * 0.6:
                t.set_width(w * 0.6)
            return VGroup(d, t.move_to(d))

        def elbow(points, col):
            pts = [np.array(p_, dtype=float) for p_ in points]
            path = VMobject().set_points_as_corners(pts[:-1]).set_stroke(col, 3)
            tip = Arrow(pts[-2], pts[-1], buff=0, thickness=3, fill_color=col)
            return VGroup(path, tip)

        Y1, Y2, Y3 = 1.5, -0.45, -2.05
        start = box("start at 320 px", MUTED, 2.3).move_to([-5.7, Y1, 0])
        widen = box("widen w", INK, 1.9).move_to([-2.85, Y1, 0])
        q1 = diamond("a constraint fails?").move_to([0.45, Y1, 0])
        rec = box("record w*", EM_C, 2.0).move_to([3.75, Y1, 0])
        q2 = diamond("intrinsic CSS can absorb it?", WARN_C, 3.6, 1.35).move_to([3.75, Y2, 0])
        fixb = box("fix: max-width · minmax() · clamp()", OK_C, 4.0, size=18).move_to([-1.0, Y2, 0])
        addb = box("@media (width >= w*÷16 em)", EM_C, 3.9, size=18).move_to([3.75, Y3, 0])
        chart = VGroup(start, widen, q1, rec, q2, fixb, addb)

        def arr(a_, b_, col=MUTED):
            return Arrow(a_, b_, buff=0.06, thickness=3, fill_color=col)

        a1 = arr(start.get_right(), widen.get_left())
        a2 = arr(widen.get_right(), q1[0].get_left())
        a3 = arr(q1[0].get_right(), rec.get_left(), EM_C)
        a4 = arr(rec.get_bottom(), q2[0].get_top(), EM_C)
        a5 = arr(q2[0].get_left(), fixb.get_right(), OK_C)
        a6 = arr(q2[0].get_bottom(), addb.get_top(), EM_C)
        loop_no = elbow([q1[0].get_top(), [0.45, 2.6, 0], [-2.85, 2.6, 0], widen.get_top()], MUTED)
        back_fix = elbow([fixb.get_left(), [-2.6, Y2, 0], [-2.6, widen.get_bottom()[1], 0]], OK_C)
        back_add = elbow([addb.get_left(), [-3.1, Y3, 0], [-3.1, widen.get_bottom()[1], 0]], EM_C)
        lbls = VGroup(txt("no", 18, MUTED).next_to(loop_no, UP, buff=0.05),
                      txt("yes", 18, EM_C).next_to(a3, UP, buff=0.05),
                      txt("yes", 18, OK_C).next_to(a5, UP, buff=0.05),
                      txt("no", 18, EM_C).next_to(a6, RIGHT, buff=0.08))
        arrows = VGroup(a1, a2, a3, a4, a5, a6, loop_no, back_fix, back_add)
        self.play(LaggedStartMap(FadeIn, chart, lag_ratio=0.12), run_time=2)
        self.play(LaggedStartMap(ShowCreation, arrows, lag_ratio=0.1), FadeIn(lbls), run_time=2)

        # breakpoints found accumulate on a ruler
        nl = px_line(300, 1300, 5.6, y=-3.0, step=100, labels=[320, 1300], label_size=14)
        nl.shift(LEFT * 3.6)
        nl_t = txt("breakpoints found", 18, EM_C).next_to(nl, RIGHT, buff=0.3)
        self.play(FadeIn(nl), FadeIn(nl_t))
        token = glow_dot(start.get_center(), INK, 0.1)
        self.play(FadeIn(token, scale=0.3))

        def travel(*mobs, rt=0.45):
            for m in mobs:
                self.play(token.animate.move_to(m.get_center()), run_time=rt)

        found = [(568, "add"), (624, "add"), (632, "fix"), (848, "add"), (1128, "add")]
        travel(widen, q1)
        for v, kind in found:
            travel(rec, q2)
            travel(addb if kind == "add" else fixb)
            col = EM_C if kind == "add" else OK_C
            dot = glow_dot([nl.to_x(v), -3.0, 0], col, 0.07)
            lab = txt(str(v), 14, col).next_to(dot, UP if kind == "fix" else DOWN, buff=0.06)
            self.play(FadeIn(dot, scale=0.3), FadeIn(lab), run_time=0.4)
            travel(widen, q1, rt=0.35)
        self.say("Mobile-first, one constraint at a time, until the widest screen you support.", wait=3)
        self.clear_all()


# ==========================================================================
class V2S7_Intrinsic(RScene):
    def construct(self):
        self.tag(7, "Let the browser solve it, then go per-component", EM_C)
        code = code_panel([".grid {", "  display: grid;", "  gap: 1.5rem;",
                           "  grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr));", "}"], 20)
        code.to_edge(UP, buff=0.9)
        self.play(FadeIn(code), run_time=1)
        f = tex(r"n(w) = \left\lfloor \frac{w - 2p + g}{m + g} \right\rfloor", 40, INK).next_to(code, DOWN, buff=0.35).shift(LEFT * 3.4)
        f2 = tex(r"n(w) \ge k \iff w \ge k\,m + (k-1)\,g + 2p = W_k", 32, EM_C).next_to(f, RIGHT, buff=0.6)
        self.play(Write(f), run_time=1.5)
        self.play(Write(f2), run_time=1.5)
        pl = Plot((300, 1300), (0, 4.6), 10.0, 2.4, x_ticks=(320, 568, 848, 1128), y_ticks=(1, 2, 3, 4),
                  y_label="columns", label_size=16)
        pl.add(txt("w", 22, INK).next_to(pl.x_axis, RIGHT, buff=0.12))
        pl.move_to(DOWN * 2.0)
        self.play(FadeIn(pl))

        def n_auto(w_):
            return max(1, int((w_ - 2 * PAD + GAP) // (M_CARD + GAP)))

        steps = VGroup()
        for k in range(1, 5):
            a = max(300, W(k))
            bnd = min(1300, W(k + 1)) if k < 4 else 1300
            steps.add(Line(pl.c2p(a, k), pl.c2p(bnd, k)).set_stroke(EM_C, 5))
        vls = VGroup(*(pl.vline(W(k), CONT_C, 2) for k in (2, 3, 4)))
        self.play(LaggedStartMap(ShowCreation, steps, lag_ratio=0.3), run_time=2)
        self.play(FadeIn(vls))
        self.say("The step edges land exactly on W₂, W₃, W₄: the browser finds the content breakpoints itself.", wait=3)
        self.clear_all()

        # ---- container queries: the same component in two different containers
        self.tag(7, "Let the browser solve it, then go per-component", EM_C)
        S = 0.0072
        page_w = 1280
        b = browser(page_w * S, 4.7, url="shop.example")
        b.move_to(DOWN * 0.35)
        tl, bw, bh = browser_content_box(b)
        main_w, side_w = 880, 320
        main = Rectangle(main_w * S, bh - 0.4).set_stroke(EDGE, 2).move_to(tl + np.array([0.2 + main_w * S / 2, -bh / 2, 0]))
        side = Rectangle(side_w * S, bh - 0.4).set_stroke(EDGE, 2).next_to(main, RIGHT, buff=(page_w - main_w - side_w - 0.2 / S * 2) * S / 1.0)
        side.align_to(main, UP).set_x(tl[0] + bw - 0.2 - side_w * S / 2)
        ml = txt("main · 880 px", 16, MUTED).next_to(main, UP, buff=0.05).align_to(main, LEFT)
        sl = txt("sidebar · 320 px", 16, MUTED).next_to(side, UP, buff=0.05).align_to(side, LEFT)
        self.play(FadeIn(b), FadeIn(main), FadeIn(side), FadeIn(ml), FadeIn(sl), run_time=1)

        def grid_in(box, cols_, ok=True):
            inner = box.get_width() - 2 * PAD * S
            cw = (inner - (cols_ - 1) * GAP * S) / cols_
            need = M_CARD * S
            cs = VGroup(*(card(cw, 1.5, CONT_C, need_w=need) for _ in range(cols_))).arrange(RIGHT, buff=GAP * S)
            cs.move_to(box.get_top() + DOWN * (0.2 + 0.75) + RIGHT * 0.0)
            cs.align_to(box, LEFT).shift(RIGHT * PAD * S)
            return cs

        mq = code_panel(["@media (width >= 53em) { .grid { --cols: 3 } }"], 18).to_corner(UR, buff=0.3).shift(DOWN * 0.25)
        mq.bg.set_stroke(PX_C, 2)
        g_main = grid_in(main, 3)
        g_side = grid_in(side, 3)
        self.play(FadeIn(mq), FadeIn(g_main), FadeIn(g_side), run_time=1)
        bad = txt("viewport is 1280 px, so the sidebar copy gets 3 columns too", 20, BAD_C).next_to(b, DOWN, buff=0.15)
        self.play(FadeIn(bad))
        self.wait(2)
        cq = code_panel([".shelf { container-type: inline-size; }",
                         "@container (width >= 35.5em) { .grid { --cols: 2 } }",
                         "@container (width >= 53em)   { .grid { --cols: 3 } }"], 18).to_corner(UR, buff=0.3).shift(DOWN * 0.25)
        cq.bg.set_stroke(EM_C, 2)
        g_side2 = grid_in(side, 1)
        good = txt("each copy reads its own container's width", 20, OK_C).move_to(bad)
        self.play(FadeTransform(mq, cq), ReplacementTransform(g_side, g_side2), FadeTransform(bad, good), run_time=1.5)
        self.say("Content breakpoints belong to components. Container queries let each component carry its own.", wait=3)
        self.clear_all()


# ==========================================================================
class V2S8_Summary(RScene):
    def construct(self):
        self.tag(8, "The recipe", EM_C)
        steps = [
            ("1", "Name the content's constraints", "fits · measure · min widths · no overlap"),
            ("2", "Find where each one changes sign", "stretch test, or arithmetic: g(b*) = 0"),
            ("3", "Absorb what intrinsic CSS can", "max-width: 66ch · minmax() · clamp() · wrap"),
            ("4", "Break at the rest, in em", "848 px ÷ 16 = 53em"),
        ]
        rows = VGroup()
        for n, a, b_ in steps:
            disk = Circle(radius=0.3).set_fill(EM_C, 1).set_stroke(width=0)
            num = txt(n, 28, BG, weight=BOLD).move_to(disk)
            t = VGroup(txt(a, 30, INK, weight=BOLD), txt(b_, 22, MUTED)).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
            rows.add(VGroup(VGroup(disk, num), t).arrange(RIGHT, buff=0.35))
        rows.arrange(DOWN, buff=0.45, aligned_edge=LEFT).move_to(LEFT * 1.8 + UP * 0.1)
        # a small picture for each step
        ic1 = VGroup(card_row(3, 0.9, 0.38, 0.02, 0.04),
                     VGroup(*(RoundedRectangle(0.18, 0.1, corner_radius=0.05).set_stroke(VIOLET, 1.5) for _ in range(4))).arrange(RIGHT, buff=0.03),
                     text_bars(0.7, 0.025, 0.07, color=PINK_C, max_lines=3, n_words=24)).arrange(RIGHT, buff=0.2)
        ax = Line(LEFT * 0.9, RIGHT * 0.9).set_stroke(MUTED, 1.5)
        sl = Line(LEFT * 0.8 + DOWN * 0.3, RIGHT * 0.8 + UP * 0.3).set_stroke(CONT_C, 3)
        ic2 = VGroup(ax, sl, glow_dot(ORIGIN, EM_C, 0.06))
        colb = Rectangle(0.7, 0.45).set_stroke(EDGE, 1.5)
        ic3 = VGroup(Rectangle(1.8, 0.55).set_stroke(EDGE, 1.5), colb,
                     text_bars(0.6, 0.025, 0.07, color=OK_C, max_lines=5, n_words=40).move_to(colb),
                     double_arrow(LEFT * 0.88, LEFT * 0.37, OK_C, 1.5), double_arrow(RIGHT * 0.37, RIGHT * 0.88, OK_C, 1.5))
        nl4 = Line(LEFT * 0.9, RIGHT * 0.9).set_stroke(MUTED, 1.5)
        ic4 = VGroup(nl4, Line(UP * 0.18, DOWN * 0.18).set_stroke(EM_C, 4).move_to(RIGHT * 0.25),
                     mono("53em", 16, EM_C).next_to(RIGHT * 0.25, UP, buff=0.22))
        icons = VGroup(ic1, ic2, ic3, ic4)
        for ic, r in zip(icons, rows):
            ic.move_to([4.6, r.get_y(), 0])
        for r, ic in zip(rows, icons):
            self.play(FadeIn(r, shift=0.2 * RIGHT), FadeIn(ic, shift=0.2 * LEFT), run_time=0.8)
            self.wait(1.4)
        q = VGroup(txt("Why “in em”?", 30, EM_C, weight=BOLD), txt("→ Part 3", 26, EM_C)).arrange(RIGHT, buff=0.3)
        q.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(q, shift=0.2 * UP))
        self.wait(3)
        self.clear_all()
