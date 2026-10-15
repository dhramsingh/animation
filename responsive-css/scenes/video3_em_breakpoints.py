"""Video 3: Why media queries belong in em (or rem), not px.

Facts the video relies on:
  * Relative units in a media query resolve against the *initial* font-size,
    i.e. the browser's default font size f (16 px unless the reader changes it).
    They ignore `html { font-size: … }`, so em and rem behave identically there.
  * Page zoom changes the size of a CSS px: the viewport width in CSS px shrinks,
    f stays 16 CSS px, so px and em queries flip at the same zoom level.
  * Changing the default font size changes f only; w is untouched, so only
    em/rem queries (and rem-sized content) respond.
Running example (from Part 2): cards need 16em, gaps 1.5em, padding 1em,
  so n cards need W_n = (16n + 1.5(n-1) + 2) em: 18, 35.5, 53, 70.5 em.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rcss_kit import *  # noqa: E402,F401,F403

K = {1: 18.0, 2: 35.5, 3: 53.0, 4: 70.5}       # W_n in em
PXBP = {n: k * 16 for n, k in K.items()}          # the same breakpoints frozen in px


def cols_em(w, f):
    n = 1
    for k in (2, 3, 4):
        if w >= K[k] * f:
            n = k
    return n


def cols_px(w):
    n = 1
    for k in (2, 3, 4):
        if w >= PXBP[k]:
            n = k
    return n


def card_px(w, f, n):
    """Card width in CSS px for n columns when padding/gaps are rem-sized."""
    return (w - 2 * f - (n - 1) * 1.5 * f) / n


def site(w, f, n, S, h=3.0, url=None):
    """A browser `w` CSS px wide showing n rem-sized cards at font size f."""
    b = browser(w * S, h, url=url)
    tl, bw, bh = browser_content_box(b)
    pad, gap = f * S, 1.5 * f * S
    cw = card_px(w, f, n) * S
    ch = min(9.4 * f * S, bh - 0.55)
    need = 16 * f * S
    cards = VGroup(*(card(cw, ch, CONT_C, need_w=need) for _ in range(n))).arrange(RIGHT, buff=gap)
    hdr = RoundedRectangle(min(12 * f, w - 2 * f) * S, 0.9 * f * S, corner_radius=0.45 * f * S)
    hdr.set_fill(INK, 0.85).set_stroke(width=0)
    hdr.move_to(tl + np.array([pad + hdr.get_width() / 2, -pad - hdr.get_height() / 2, 0]))
    cards.move_to(tl + np.array([pad + cards.get_width() / 2, -pad * 2 - hdr.get_height() - ch / 2, 0]))
    g = VGroup(b, hdr, cards)
    g.broken = cw < need - 1e-6
    return g


def font_dial(f_tracker, size=0.9):
    """'Aa' whose size follows the reader's default font size, with a readout."""
    def make():
        f = f_tracker.get_value()
        aa = txt("Aa", 40, INK, weight=BOLD).set_height(size * f / 24)
        lab = VGroup(txt("default font size", 18, MUTED),
                     txt(f"{f:.0f} px", 30, EM_C, weight=BOLD)).arrange(DOWN, buff=0.06)
        return VGroup(aa, lab).arrange(RIGHT, buff=0.3, aligned_edge=DOWN)
    return make


# ==========================================================================
class V3S0_Title(RScene):
    def construct(self):
        card_ = title_card(self, 3, ["Why media queries", "belong in em"],
                           "breakpoints that scale with the reader, not the screen", EM_C, hold=1.0)
        self.play(card_.animate.shift(UP * 1.0), run_time=0.8)
        # foreshadow: a vertical px line versus a ray of em
        pl = Plot((0, 1600), (0, 32), 6.0, 2.6, x_ticks=(), y_ticks=())
        pl.move_to(DOWN * 2.0)
        vline = pl.vline(848, PX_C, 4, dashed=False)
        ray = Line(pl.c2p(0, 0), pl.c2p(1600, 1600 / 53)).set_stroke(EM_C, 5)
        lab_px = mono("848px", 20, PX_C).next_to(vline, UP, buff=0.08)
        lab_em = mono("53em", 20, EM_C).next_to(ray.get_end(), UP, buff=0.08)
        self.play(FadeIn(pl), ShowCreation(vline), FadeIn(lab_px), run_time=1)
        self.play(ShowCreation(ray), FadeIn(lab_em), run_time=1.2)
        self.wait(2)
        self.clear_all()


# ==========================================================================
class V3S1_TwoRulers(RScene):
    def construct(self):
        self.tag(1, "Two rulers", EM_C)
        S = 0.0088
        X0 = -6.2
        f = ValueTracker(16)

        def x(px):
            return X0 + px * S

        px_r = px_line(0, 1400, 1400 * S, y=1.4, step=50, labels=[0, 200, 400, 600, 800, 1000, 1200, 1400], label_size=16, unit="")
        px_r.shift(RIGHT * (X0 - px_r.to_x(0)))
        px_t = txt("CSS px (fixed)", 20, PX_C).next_to(px_r, UP, buff=0.15).align_to(px_r, LEFT)

        def em_ruler():
            fv = f.get_value()
            g = VGroup(Line([x(0), -0.3, 0], [x(1400), -0.3, 0]).set_stroke(EM_C, 2))
            k = 0
            while k * fv <= 1400:
                big = k % 10 == 0
                g.add(Line([x(k * fv), -0.3 - (0.12 if big else 0.06), 0], [x(k * fv), -0.3 + (0.12 if big else 0.06), 0])
                      .set_stroke(EM_C, 2 if big else 1))
                if big:
                    g.add(txt(f"{k}em", 16, EM_C).next_to([x(k * fv), -0.42, 0], DOWN, buff=0.06))
                k += 1
            return g

        em_r = always_redraw(em_ruler)
        em_t = always_redraw(lambda: txt(f"em  (1em = {f.get_value():.0f} px, the reader's default)", 20, EM_C)
                             .next_to([x(0), -0.3, 0], UP, buff=0.2, aligned_edge=LEFT))
        self.play(FadeIn(px_r), FadeIn(px_t), run_time=1)
        self.play(FadeIn(em_r), FadeIn(em_t), run_time=1)
        dial = always_redraw(lambda: font_dial(f)().to_corner(UR, buff=0.4).shift(DOWN * 0.3))
        self.play(FadeIn(dial))
        self.say("At the default 16 px, the two rulers line up: 50em = 800 px.", wait=1.5)

        # the content's real need: three cards = 53em
        need = always_redraw(lambda: VGroup(
            Rectangle(53 * f.get_value() * S, 0.36).set_fill(CONT_C, 0.35).set_stroke(CONT_C, 1.5)
            .move_to([x(53 * f.get_value() / 2), -1.55, 0]),
            txt("space three cards need (53em)", 18, CONT_C).move_to([x(53 * f.get_value() / 2), -1.55, 0])))
        pxm = VGroup(Line([x(848), 1.75, 0], [x(848), -2.4, 0]).set_stroke(PX_C, 4),
                     mono("min-width: 848px", 18, PX_C).next_to([x(848), -2.4, 0], DOWN, buff=0.08))
        emm = always_redraw(lambda: VGroup(
            DashedLine([x(53 * f.get_value()), -0.3, 0], [x(53 * f.get_value()), -2.4, 0], dash_length=0.08).set_stroke(EM_C, 4),
            mono("min-width: 53em", 18, EM_C).next_to([x(53 * f.get_value()), -2.75, 0], DOWN, buff=0.08)))
        self.play(FadeIn(need), run_time=1)
        self.play(ShowCreation(pxm[0]), FadeIn(pxm[1]), FadeIn(emm), run_time=1.2)
        self.say("Both breakpoints sit exactly where the cards stop fitting… at 16 px.", wait=2)
        for target, msg in ((20, "The reader picks 20 px. Every em grows by 25 %. The content needs 1060 px now."),
                            (24, "At 24 px the cards need 1272 px. The px breakpoint never moved."),
                            (12, "Smaller text, smaller need: 636 px. The em breakpoint follows it down too.")):
            self.play(f.animate.set_value(target), run_time=2.5)
            self.say(msg, wait=1.8)
        self.play(f.animate.set_value(16), run_time=2)
        eq = tex(r"53\,\text{em} = 53 \times f", 40, EM_C).move_to([1.2, 2.65, 0])
        self.play(Write(eq))
        self.say("An em breakpoint is measured in the same unit as the content it protects.", wait=3)
        self.clear_all()


# ==========================================================================
class V3S2_WhatEmMeans(RScene):
    def construct(self):
        self.tag(2, "What “em” means inside a media query", EM_C)

        def node(lines, col, w=3.6):
            t = VGroup(*(txt(l, 20, col) for l in lines)).arrange(DOWN, buff=0.08)
            r = RoundedRectangle(max(w, t.get_width() + 0.4), t.get_height() + 0.4, corner_radius=0.15)
            r.set_fill(PANEL, 1).set_stroke(col, 2)
            return VGroup(r, t.move_to(r))

        # browser settings mock
        sett = RoundedRectangle(3.8, 1.6, corner_radius=0.15).set_fill(PANEL, 1).set_stroke(EDGE, 2)
        sett.move_to([-4.6, 1.6, 0])
        st = txt("Browser settings", 20, MUTED).next_to(sett.get_top(), DOWN, buff=0.15)
        fs = txt("Font size", 20, INK).move_to(sett.get_center() + LEFT * 0.9 + DOWN * 0.2)
        dd = RoundedRectangle(1.5, 0.42, corner_radius=0.1).set_fill(BG, 1).set_stroke(EM_C, 1.5).move_to(sett.get_center() + RIGHT * 0.9 + DOWN * 0.2)
        dv = txt("Medium · 16 px", 15, EM_C).move_to(dd)
        settings = VGroup(sett, st, fs, dd, dv)
        init = node(["initial font-size", "f = 16 px"], EM_C).move_to([0, 1.6, 0])
        mq = node(["em / rem in", "@media queries"], EM_C).move_to([4.6, 1.6, 0])
        html = code_panel(["html { font-size: 62.5%; }"], 20).move_to([-4.6, -1.3, 0])
        rules = node(["rem in ordinary rules", "1rem = 10 px"], WARN_C).move_to([0, -1.3, 0])
        a1 = Arrow(sett.get_right(), init.get_left(), buff=0.1, thickness=3, fill_color=EM_C)
        a2 = Arrow(init.get_right(), mq.get_left(), buff=0.1, thickness=3, fill_color=EM_C)
        a3 = Arrow(html.get_right(), rules.get_left(), buff=0.1, thickness=3, fill_color=WARN_C)
        a4 = Arrow(init.get_bottom(), html.get_top() + RIGHT * 0.8, buff=0.1, thickness=2, fill_color=MUTED)
        blocked = Arrow(html.get_right() + UP * 0.2, mq.get_bottom() + LEFT * 0.4, buff=0.15, thickness=3, fill_color=PX_C)
        cross = cross_mark(0.5).move_to(blocked.get_center())
        self.play(FadeIn(settings), run_time=1)
        self.play(GrowArrow(a1), FadeIn(init), run_time=1)
        self.play(GrowArrow(a2), FadeIn(mq), run_time=1)
        res1 = tex(r"48\,\text{em} = 48 \times 16 = 768\ \text{px}", 30, EM_C).next_to(mq, UP, buff=0.25)
        self.play(FadeIn(res1))
        self.say("Inside a media query, 1em is the reader's default font size — before any CSS runs.", wait=2)
        self.play(FadeIn(html), GrowArrow(a4), run_time=1)
        self.play(GrowArrow(a3), FadeIn(rules), run_time=1)
        self.play(GrowArrow(blocked), run_time=0.8)
        self.play(ShowCreation(cross))
        self.say("Your stylesheet can change rem for the page. It cannot change em or rem inside @media.", wait=2.5)

        eqv = VGroup(mono("(width >= 48em)", 24, EM_C), tex(r"\equiv", 36, INK), mono("(width >= 48rem)", 24, EM_C),
                     tex(r"\equiv", 36, INK), tex(r"w \ge 48\,f", 36, EM_C)).arrange(RIGHT, buff=0.25)
        eqv.to_edge(DOWN, buff=1.1)
        self.play(FadeIn(eqv, shift=0.2 * UP))
        self.wait(1.5)
        # the 62.5% trap on a ruler
        self.clear_all()
        self.tag(2, "What “em” means inside a media query", EM_C)
        trap = code_panel(["html { font-size: 62.5%; }   /* 1rem = 10px */", "@media (width >= 48rem) { … }"], 24).to_edge(UP, buff=1.0)
        self.play(FadeIn(trap))
        nl = px_line(0, 1000, 11, y=-0.6, step=50, labels=[0, 200, 480, 768, 1000], label_size=18)
        exp = VGroup(Line([nl.to_x(480), -0.6, 0], [nl.to_x(480), 0.9, 0]).set_stroke(WARN_C, 4),
                     txt("expected: 48 × 10 = 480 px", 20, WARN_C).next_to([nl.to_x(480), 0.9, 0], UP, buff=0.08))
        real = VGroup(Line([nl.to_x(768), -0.6, 0], [nl.to_x(768), 0.9, 0]).set_stroke(EM_C, 4),
                      txt("actual: 48 × 16 = 768 px", 20, EM_C).next_to([nl.to_x(768), 0.9, 0], UP, buff=0.08))
        real[1].shift(DOWN * 0.45 + RIGHT * 1.2)
        self.play(FadeIn(nl))
        self.play(ShowCreation(exp[0]), FadeIn(exp[1]))
        self.play(ShowCreation(real[0]), FadeIn(real[1]))
        gap_ = Brace(Line([nl.to_x(480), -0.6, 0], [nl.to_x(768), -0.6, 0]), DOWN, buff=0.45)
        gl = txt("off by 288 px", 22, BAD_C).next_to(gap_, DOWN, buff=0.1)
        self.play(GrowFromCenter(gap_), FadeIn(gl))
        self.say("Classic trap: with the 62.5 % trick, 48rem in a query is still 768 px, not 480.", wait=3)
        self.clear_all()


# ==========================================================================
class V3S3_Experiment(RScene):
    def construct(self):
        self.tag(3, "The experiment: same window, bigger text", EM_C)
        S = 0.0062
        W_ = 900
        f = ValueTracker(16)
        codeA = code_panel(["@media (width >= 568px) { 2 cols }", "@media (width >= 848px) { 3 cols }"], 17)
        codeB = code_panel(["@media (width >= 35.5em) { 2 cols }", "@media (width >= 53em)   { 3 cols }"], 17)
        codeA.bg.set_stroke(PX_C, 2)
        codeB.bg.set_stroke(EM_C, 2)
        LX, RX = -3.45, 3.45
        codeA.move_to([LX, 2.55, 0])
        codeB.move_to([RX, 2.55, 0])

        def side(which):
            fv = f.get_value()
            n = cols_px(W_) if which == "px" else cols_em(W_, fv)
            g = site(W_, fv, n, S, h=3.0)
            g.shift(np.array([LX if which == "px" else RX, 0.0, 0]) - g[0].get_center())
            cw = card_px(W_, fv, n)
            ok = cw >= 16 * fv - 1e-6
            info = VGroup(
                txt(f"{n} columns", 22, INK, weight=BOLD),
                txt(f"card {cw:.0f} px  {'≥' if ok else '<'}  needs {16 * fv:.0f} px", 20, OK_C if ok else BAD_C),
            ).arrange(DOWN, buff=0.08).next_to(g[0], DOWN, buff=0.2)
            return VGroup(g, info)

        left = always_redraw(lambda: side("px"))
        right = always_redraw(lambda: side("em"))
        self.play(FadeIn(codeA), FadeIn(codeB), run_time=1)
        self.play(FadeIn(left), FadeIn(right), run_time=1)
        dial = always_redraw(lambda: font_dial(f, 0.7)().move_to([0, 2.55, 0]))
        self.play(FadeIn(dial))
        self.say("Both windows are 900 px wide. Cards, gaps and text are all sized in rem.", wait=2)
        self.play(f.animate.set_value(20), run_time=3)
        self.say("At 20 px the px stylesheet still forces 3 columns: each card is 53 px too narrow.", wait=2.5)
        self.play(f.animate.set_value(24), run_time=3)
        self.say("At 24 px it is worse. The em stylesheet simply dropped to 2 columns at the right moment.", wait=3)
        self.play(f.animate.set_value(16), run_time=2)
        self.wait(1)
        self.clear_all()


# ==========================================================================
def phase_plot():
    pl = Plot((0, 1600), (0, 32), 8.6, 5.0, x_ticks=(0, 400, 848, 1200, 1600), y_ticks=(8, 16, 24, 32),
              y_label="default font size f (px)", y_label_color=EM_C, label_size=16)
    pl.x_labels[2].set_color(PX_C)
    pl.y_labels[1].set_color(INK)
    pl.add(VGroup(txt("w", 24, INK), txt("(CSS px)", 14, MUTED)).arrange(DOWN, buff=0.04).next_to(pl.x_axis, RIGHT, buff=0.15))
    return pl


def ray_pts(pl, k):
    """Origin to where w = k·f leaves the plot box."""
    f_end = min(32, 1600 / k)
    return pl.c2p(0, 0), pl.c2p(k * f_end, f_end)


class V3S4_PhaseDiagram(RScene):
    def construct(self):
        self.tag(4, "The (width, font size) plane", EM_C)
        pl = phase_plot().move_to(LEFT * 1.8 + DOWN * 0.4)
        self.play(FadeIn(pl), run_time=1)
        f16 = pl.hline(16, MUTED, 1.5)
        f16l = txt("browser default", 16, MUTED).next_to(f16, RIGHT, buff=0.1)
        self.play(ShowCreation(f16), FadeIn(f16l))
        self.say("Every reader is a point: their viewport width w and their default font size f.", wait=1.5)

        # where three cards physically fit
        fit = Polygon(pl.c2p(0, 0), pl.c2p(1600, 0), pl.c2p(1600, 1600 / 53)).set_fill(CONT_C, 0.16).set_stroke(width=0)
        fit_l = txt("3 cards fit", 20, CONT_C).move_to(pl.c2p(1300, 6))
        a, b = ray_pts(pl, 53)
        bound = Line(a, b).set_stroke(CONT_C, 3)
        bl = tex(r"w = 53\,f", 30, CONT_C).next_to(b, UP, buff=0.1).shift(LEFT * 0.3)
        self.play(FadeIn(fit), FadeIn(fit_l), ShowCreation(bound), FadeIn(bl), run_time=1.5)
        self.say("Cards are sized in rem, so the fit boundary w = 53 f is a ray through the origin.", wait=2.5)

        # px breakpoint: a vertical line
        vline = pl.vline(848, PX_C, 4, dashed=False)
        vl = mono("848px", 20, PX_C).next_to(vline, UP, buff=0.08)
        self.play(ShowCreation(vline), FadeIn(vl))
        over = Polygon(pl.c2p(848, 16), pl.c2p(848, 32), pl.c2p(1600, 32), pl.c2p(1600, 1600 / 53)).set_fill(BAD_C, 0.35).set_stroke(width=0)
        waste = Polygon(pl.c2p(0, 0), pl.c2p(848, 0), pl.c2p(848, 16)).set_fill(WARN_C, 0.3).set_stroke(width=0)
        ol = txt("3 columns forced,\ndon't fit: overflow", 18, BAD_C).move_to(pl.c2p(1130, 27))
        wl = txt("would fit, not used", 18, WARN_C).move_to(pl.c2p(640, 3.5))
        self.play(FadeIn(over), FadeIn(ol), run_time=1)
        self.play(FadeIn(waste), FadeIn(wl), run_time=1)
        self.say("A px breakpoint is a vertical line. It matches the true boundary only on the f = 16 row.", wait=2.5)

        # a reader moves up
        dot_f = ValueTracker(16)
        reader = always_redraw(lambda: glow_dot(pl.c2p(1000, dot_f.get_value()), INK, 0.1))
        self.play(FadeIn(reader, scale=0.3))
        self.play(dot_f.animate.set_value(24), run_time=3)
        self.say("A reader at 1000 px who picks 24 px lands in the red wedge.", wait=2)

        # em breakpoint: the ray itself
        ray = Line(a, b).set_stroke(EM_C, 6)
        rl = mono("53em", 20, EM_C).next_to(b, RIGHT, buff=0.1)
        self.play(ShowCreation(ray), FadeIn(rl), FadeOut(over), FadeOut(waste), FadeOut(ol), FadeOut(wl), run_time=1.5)
        self.say("An em breakpoint is the ray w = 53 f: it IS the fit boundary, for every f.", wait=2.5)
        inv = tex(r"\text{layout depends only on } \frac{w}{f}", 34, EM_C).to_corner(UR, buff=0.5).shift(DOWN * 0.6)
        self.play(Write(inv))
        self.wait(1)
        self.play(FadeOut(reader))

        # the whole fan
        fan = VGroup()
        verts = VGroup()
        labels = VGroup()
        for n in (1, 2, 3, 4):
            p0, p1 = ray_pts(pl, K[n])
            fan.add(Line(p0, p1).set_stroke(EM_C, 4))
            verts.add(pl.vline(PXBP[n], PX_C, 2))
            labels.add(mono(f"{K[n]:g}em", 16, EM_C).next_to(p1, UP if p1[1] > pl.c2p(0, 31)[1] else RIGHT, buff=0.06))
        cols_l = VGroup(*(txt(f"{n} col{'s' if n > 1 else ''}", 18, INK).move_to(pl.c2p(x_, 26))
                          for n, x_ in ((1, 690), (2, 1180), (3, 1520))))
        self.play(FadeOut(ray), FadeOut(rl), FadeOut(bound), FadeOut(bl), FadeOut(fit), FadeOut(fit_l), FadeOut(vline), FadeOut(vl),
                  run_time=0.8)
        self.play(LaggedStartMap(ShowCreation, verts, lag_ratio=0.2), run_time=1.2)
        self.play(LaggedStartMap(ShowCreation, fan, lag_ratio=0.2), FadeIn(labels), run_time=1.5)
        self.play(FadeIn(cols_l))
        pts = VGroup(*(Dot(pl.c2p(PXBP[n], 16), radius=0.08, fill_color=INK) for n in (2, 3, 4)))
        self.play(LaggedStartMap(FadeIn, pts, scale=0.3, lag_ratio=0.2))
        self.say("px breakpoints: a grid of vertical lines. em breakpoints: a fan of rays. They agree only at f = 16.", wait=3.5)
        self.clear_all()


# ==========================================================================
class V3S5_ZoomVsFontSize(RScene):
    def construct(self):
        self.tag(5, "Zoom versus font size", EM_C)
        pl = phase_plot().move_to(LEFT * 2.2 + DOWN * 0.4)
        a, b = ray_pts(pl, 53)
        ray = Line(a, b).set_stroke(EM_C, 5)
        vline = pl.vline(848, PX_C, 4, dashed=False)
        f16 = pl.hline(16, MUTED, 1.5)
        over = Polygon(pl.c2p(848, 16), pl.c2p(848, 32), pl.c2p(1600, 32), pl.c2p(1600, 1600 / 53)).set_fill(BAD_C, 0.25).set_stroke(width=0)
        self.play(FadeIn(pl), ShowCreation(ray), ShowCreation(vline), ShowCreation(f16), FadeIn(over), run_time=1.2)
        pos = {"w": 1000.0, "f": 16.0}
        wt, ft = ValueTracker(1000), ValueTracker(16)
        reader = always_redraw(lambda: glow_dot(pl.c2p(wt.get_value(), ft.get_value()), INK, 0.1))

        def status():
            w, fv = wt.get_value(), ft.get_value()
            n_px = 3 if w >= 848 else 2
            n_em = 3 if w >= 53 * fv else 2
            fits = lambda n: w >= (K[n] * fv)  # noqa: E731
            rows = VGroup()
            for name, n, col in (("px rule", n_px, PX_C), ("em rule", n_em, EM_C)):
                ok = fits(n)
                r = VGroup(txt(name, 22, col, weight=BOLD), txt(f"{n} cols", 22, INK),
                           (check_mark(0.3) if ok else cross_mark(0.26)))
                r.arrange(RIGHT, buff=0.25)
                rows.add(r)
            rows.arrange(DOWN, buff=0.25, aligned_edge=LEFT)
            vals = VGroup(txt(f"w = {w:.0f} px", 22, INK), txt(f"f = {fv:.1f} px", 22, EM_C)).arrange(DOWN, buff=0.12, aligned_edge=LEFT)
            g = VGroup(vals, rows).arrange(DOWN, buff=0.35, aligned_edge=LEFT)
            box = SurroundingRectangle(g, buff=0.25).set_fill(PANEL, 1).set_stroke(EDGE, 2)
            return VGroup(box, g).move_to([4.9, 0.2, 0])

        st = always_redraw(status)
        self.play(FadeIn(reader), FadeIn(st))
        # action 1: page zoom
        z1 = pill("Page zoom  (Ctrl +)", VIOLET, 22).move_to([4.9, 2.6, 0])
        self.play(FadeIn(z1))
        self.say("Page zoom makes CSS pixels bigger: w shrinks, f stays 16. The reader slides left.", wait=0.5)
        arr = Arrow(pl.c2p(1000, 16) + UP * 0.35, pl.c2p(640, 16) + UP * 0.35, buff=0, thickness=3, fill_color=VIOLET)
        self.play(GrowArrow(arr))
        self.play(wt.animate.set_value(640), run_time=3)
        self.say("Both rules flip at the same moment: on the f = 16 row the line and the ray meet.", wait=2.5)
        self.play(wt.animate.set_value(1000), FadeOut(arr), run_time=1.5)
        # action 2: default font size
        z2 = pill("Default font size", EM_C, 22).move_to(z1)
        self.play(FadeTransform(z1, z2))
        arr2 = Arrow(pl.c2p(1000, 16) + RIGHT * 0.35, pl.c2p(1000, 26) + RIGHT * 0.35, buff=0, thickness=3, fill_color=EM_C)
        self.say("Changing the default font size changes f only. The reader moves straight up.", wait=0.3)
        self.play(GrowArrow(arr2))
        self.play(ft.animate.set_value(1000 / 53), run_time=2)
        cross_pt = Circle(radius=0.18).set_stroke(EM_C, 3).move_to(pl.c2p(1000, 1000 / 53))
        self.play(ShowCreation(cross_pt))
        self.play(ft.animate.set_value(26), run_time=2.5)
        self.say("The em rule flips at f = 18.9 px. The px rule never notices and overflows.", wait=2.5)
        note = VGroup(txt("only if the text itself is in rem/em:", 18, MUTED),
                      txt("px font sizes ignore this setting entirely", 18, MUTED)).arrange(DOWN, buff=0.05)
        note.move_to([4.9, -2.55, 0])
        self.play(FadeIn(note))
        self.wait(2.5)
        self.clear_all()


# ==========================================================================
class V3S6_Measure(RScene):
    def construct(self):
        self.tag(6, "Characters per line survive scaling", EM_C)
        S = 0.0082
        fonts = (16, 20, 24)
        col_px = 348            # a two-column article's text column at 768px, in px
        col_em = col_px / 16    # the same column written in em: 21.75em
        xs = (-3.6, 0.35, 4.65)
        rows = {"px": 2.35, "em": -0.2}
        lab_px = VGroup(pill("px", PX_C, 22), txt("column = 348px", 16, PX_C)).arrange(DOWN, buff=0.08).move_to([-6.3, rows["px"] - 0.7, 0])
        lab_em = VGroup(pill("em", EM_C, 22), txt("column = 21.75em", 16, EM_C)).arrange(DOWN, buff=0.08).move_to([-6.3, rows["em"] - 0.6, 0])
        heads = VGroup(*(txt(f"f = {fv} px", 22, INK, weight=BOLD).move_to([x_, 2.75, 0]) for fv, x_ in zip(fonts, xs)))
        self.play(FadeIn(heads), FadeIn(lab_px), FadeIn(lab_em))
        panels = {}
        for kind in ("px", "em"):
            for fv, x_ in zip(fonts, xs):
                width = (col_px if kind == "px" else col_em * fv) * S
                bars = text_bars(width, 0.5 * fv * S, 1.5 * fv * S, n_words=34, color=MUTED)
                box = Rectangle(width + 0.12, max(bars.get_height(), 0.3) + 0.12).set_stroke(EDGE, 1.5)
                grp = VGroup(box, bars)
                bars.move_to(box)
                grp.move_to([x_, rows[kind], 0], aligned_edge=UP)
                ncpl = bars.cpl
                col = OK_C if 40 <= ncpl <= 75 else (WARN_C if ncpl >= 30 else BAD_C)
                info = txt(f"{ncpl} ch/line · {len(bars.lines)} lines", 18, col).next_to(grp, DOWN, buff=0.1)
                panels[(kind, fv)] = VGroup(grp, info)
        for kind in ("px", "em"):
            self.play(LaggedStart(*(FadeIn(panels[(kind, fv)]) for fv in fonts), lag_ratio=0.3), run_time=1.8)
            self.wait(0.8)
        self.say("px column: bigger text, same width, fewer characters per line. Choppy, more return sweeps.", wait=2.5)
        f1 = tex(r"\text{px: } \ \frac{348}{0.5\,f} = 43.5,\ 34.8,\ 29", 30, PX_C)
        f2 = tex(r"\text{em: } \ \frac{21.75\,f}{0.5\,f} = 43.5 \ \text{ for every } f", 30, EM_C)
        fg = VGroup(f1, f2).arrange(RIGHT, buff=0.8).move_to(DOWN * 2.7)
        self.play(Write(f1), run_time=1.2)
        self.play(Write(f2), run_time=1.2)
        self.wait(1)
        # similarity: the 24px em layout is the 16px one, scaled
        ghost = panels[("em", 24)][0].copy()
        target = panels[("em", 16)][0]
        self.play(ghost.animate.scale(16 / 24).move_to(target, aligned_edge=UL).set_color(EM_C), run_time=2)
        self.play(Flash(target.get_center(), color=EM_C, flash_radius=1.2), run_time=1)
        self.say("Scale the 24 px em layout down by 2/3: it lands exactly on the 16 px one. Same lines, same breaks.", wait=3)
        self.clear_all()


# ==========================================================================
class V3S7_Psychology(RScene):
    def construct(self):
        self.tag(7, "The psychology: what the number makes you think", EM_C)
        # mental models
        left = VGroup(mono("768px", 40, PX_C))
        bubble_l = RoundedRectangle(4.2, 2.2, corner_radius=0.5).set_stroke(PX_C, 2).set_fill(PANEL, 1)
        ip = tablet(0.75, 1.0)
        lt = txt("“an iPad”", 22, PX_C)
        VGroup(ip, lt).arrange(RIGHT, buff=0.3).move_to(bubble_l)
        left.next_to(bubble_l, UP, buff=0.3)
        L = VGroup(bubble_l, ip, lt, left).move_to([-3.6, 1.2, 0])
        bubble_r = RoundedRectangle(4.2, 2.2, corner_radius=0.5).set_stroke(EM_C, 2).set_fill(PANEL, 1)
        cells = VGroup(*(Rectangle(0.07, 0.3).set_fill(EM_C, 0.25 + 0.25 * (k % 2)).set_stroke(width=0) for k in range(48))).arrange(RIGHT, buff=0)
        rt = txt("“room for ~96 characters”", 22, EM_C)
        VGroup(cells, rt).arrange(DOWN, buff=0.25).move_to(bubble_r)
        right = mono("48em", 40, EM_C).next_to(bubble_r, UP, buff=0.3)
        R = VGroup(bubble_r, cells, rt, right).move_to([3.6, 1.2, 0])
        self.play(FadeIn(L, shift=0.2 * RIGHT), run_time=1)
        self.say("A px number invites device thinking: you picture hardware.", wait=1.5)
        self.play(FadeIn(R, shift=0.2 * LEFT), run_time=1)
        self.say("An em number is a quantity of text: you picture the content it must hold.", wait=2)
        self.play(FadeOut(self._cap))
        self._cap = None

        # one knob drives every size
        f = ValueTracker(16)
        knob = Circle(radius=0.55).set_fill(PANEL, 1).set_stroke(EM_C, 4).move_to([0, -1.9, 0])
        kl = always_redraw(lambda: txt(f"f = {f.get_value():.0f}", 22, EM_C, weight=BOLD).move_to(knob))
        targets = [("text", -5.2), ("gaps", -2.6), ("card widths", 2.6), ("breakpoints", 5.2)]
        boxes = VGroup()
        wires = VGroup()
        for name, x_ in targets:
            bx = pill(name, EM_C, 20).move_to([x_, -1.9, 0])
            boxes.add(bx)
            wires.add(Line(knob.get_center(), bx.get_center()).set_stroke(EM_C, 2, opacity=0.6))
        self.bring_to_front(knob)
        self.play(ShowCreation(wires), FadeIn(boxes), FadeIn(knob), FadeIn(kl), run_time=1.2)
        self.bring_to_front(knob, kl)
        kt = txt("one number the reader chose drives every decision", 22, INK).next_to(knob, DOWN, buff=0.3)
        self.play(FadeIn(kt))
        self.wait(1.5)
        cut = cross_mark(0.35).move_to(wires[3].point_from_proportion(0.55))
        pxb = pill("breakpoints in px", PX_C, 20).move_to(boxes[3])
        self.play(FadeTransform(boxes[3], pxb), wires[3].animate.set_stroke(PX_C, opacity=0.4), ShowCreation(cut))
        self.say("With px breakpoints, one wire is cut: the layout ignores the reader's choice.", wait=2.5)
        self.clear_all()

        # accessibility demo: 200% text, em layout reflows, px layout breaks
        self.tag(7, "The psychology: what the number makes you think", EM_C)
        badges = VGroup(pill("WCAG 1.4.4  Resize text to 200%", OK_C, 20),
                        pill("WCAG 1.4.10  Reflow, no 2-D scrolling", OK_C, 20)).arrange(RIGHT, buff=0.4).to_edge(UP, buff=0.95)
        self.play(FadeIn(badges, lag_ratio=0.3))
        S = 0.0066
        W_ = 1280
        f2 = ValueTracker(16)

        def pair():
            fv = f2.get_value()
            a = site(W_, fv, cols_px(W_), S, h=2.1)
            b = site(W_, fv, cols_em(W_, fv), S, h=2.1)
            a.shift(np.array([-2.35, 0.95, 0]) - a[0].get_center())
            b.shift(np.array([-2.35, -1.75, 0]) - b[0].get_center())
            out = VGroup(a, b)
            for frame_, name, col, broken in ((a[0], "px breakpoints", PX_C, a.broken), (b[0], "em breakpoints", EM_C, b.broken)):
                lab = VGroup(txt(name, 20, col, weight=BOLD),
                             txt(f"{cols_px(W_) if col == PX_C else cols_em(W_, fv)} cols · " + ("overflows" if broken else "fits"),
                                 20, BAD_C if broken else OK_C)).arrange(RIGHT, buff=0.3)
                lab.next_to(frame_, UP, buff=0.1).align_to(frame_, LEFT)
                out.add(lab)
            return out

        pr = always_redraw(pair)
        dial = always_redraw(lambda: font_dial(f2, 0.7)().move_to([4.6, -1.75, 0]))
        self.play(FadeIn(pr), FadeIn(dial))
        self.play(f2.animate.set_value(32), run_time=5, rate_func=linear)
        self.say("Text at 200 %: the em layout reflows 4 → 3 → 2 columns; the px layout overflows.", wait=3)
        self.clear_all()


# ==========================================================================
class V3S8_Summary(RScene):
    def construct(self):
        self.tag(8, "Summary", EM_C)
        pl = Plot((0, 1600), (0, 32), 4.6, 2.9, x_ticks=(), y_ticks=(16,), x_label="w", y_label="f", label_size=14)
        pl.move_to([-4.2, 0.6, 0])
        a, b = ray_pts(pl, 53)
        vis = VGroup(pl, pl.vline(848, PX_C, 4, dashed=False), Line(a, b).set_stroke(EM_C, 5),
                     Polygon(pl.c2p(848, 16), pl.c2p(848, 32), pl.c2p(1600, 32), pl.c2p(1600, 1600 / 53)).set_fill(BAD_C, 0.3).set_stroke(width=0))
        pts = [
            (PX_C, "px breakpoint = vertical line: right only when f = 16"),
            (EM_C, "em breakpoint = ray w = k·f: right for every reader"),
            (INK, "in @media, em = rem = the browser's default font size"),
            (INK, "html { font-size } never changes a media query"),
            (INK, "page zoom: both agree · font-size setting: only em responds"),
            (EM_C, "em keeps characters per line, so reading stays comfortable"),
        ]
        items = VGroup()
        for col, s in pts:
            d = Dot(radius=0.06, fill_color=col)
            items.add(VGroup(d, txt(s, 22, INK)).arrange(RIGHT, buff=0.2))
        items.arrange(DOWN, buff=0.28, aligned_edge=LEFT).move_to([2.6, 0.75, 0])
        self.play(FadeIn(vis), run_time=1)
        for it in items:
            self.play(FadeIn(it, shift=0.2 * RIGHT), run_time=0.6)
            self.wait(0.7)
        code = code_panel([
            "/* content says: 3 cards need 3·16em + 2·1.5em + 2·1em */",
            "@media (width >= 53em) { .grid { --cols: 3 } }",
        ], 22).to_edge(DOWN, buff=0.6)
        self.play(FadeIn(code, shift=0.2 * UP))
        self.wait(3)
        recap = VGroup(
            pill("1  devices are a moving cloud", PX_C, 18),
            pill("2  content sets the width", CONT_C, 18),
            pill("3  em lets it scale with the reader", EM_C, 18),
        ).arrange(RIGHT, buff=0.3).next_to(code, UP, buff=0.3)
        self.play(LaggedStartMap(FadeIn, recap, lag_ratio=0.3))
        self.wait(3)
        self.clear_all()
