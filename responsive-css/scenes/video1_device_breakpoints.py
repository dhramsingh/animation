"""Video 1: Why targeting device dimensions is a mathematically doomed strategy.

Render every chapter with ../render.sh, or one with
    manimgl scenes/video1_device_breakpoints.py V1S1_IPadRule -w --hd
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rcss_kit import *  # noqa: E402,F401,F403

# name, portrait CSS width, portrait CSS height, year released
IPADS = [
    ("mini 6", 744, 1133, 2021),
    ('9.7"', 768, 1024, 2010),
    ('10.2"', 810, 1080, 2019),
    ("Air", 820, 1180, 2020),
    ('Pro 11"', 834, 1194, 2018),
    ('Pro 12.9"', 1024, 1366, 2015),
]
# Chrome/Edge page-zoom presets from 50 % to 300 % (as fractions).
ZOOMS = [0.5, 0.67, 0.75, 0.8, 0.9, 1.0, 1.1, 1.25, 1.5, 1.75, 2.0, 2.5, 3.0]

RULE = 768  # the "iPad" breakpoint everyone copies


def mark_for(width):
    return check_mark(0.3) if width <= RULE else cross_mark(0.26)


# ==========================================================================
class V1S0_Title(RScene):
    def construct(self):
        card = title_card(self, 1, ["Why device breakpoints", "are mathematically doomed"],
                          "max-width: 768px  ≠  “iPad”", PX_C, hold=1.0)
        # foreshadow: one tidy dot, then the real cloud of widths
        nl = px_line(0, 2800, 12, y=-2.6, step=200, labels=[0, 768, 1400, 2800], unit="")
        dot = glow_dot([nl.to_x(768), -2.6, 0], DEV_C)
        lab = txt("iPad?", 20, DEV_C).next_to(dot, UP, buff=0.15)
        self.play(card.animate.shift(UP * 0.6), FadeIn(nl), run_time=1)
        self.play(FadeIn(dot, scale=0.5), FadeIn(lab), run_time=0.8)
        widths = sorted({round(w / z, 2) for _, a, b, _ in IPADS for w in (a, b) for z in ZOOMS})
        cloud = VGroup()
        stack = {}
        for w in widths:
            b = int(w // 70)
            k = stack.get(b, 0)
            stack[b] = k + 1
            cloud.add(Dot([nl.to_x(w), -2.45 + 0.11 * k, 0], radius=0.04, fill_color=DEV_C).set_opacity(0.85))
        self.play(FadeOut(lab), LaggedStartMap(FadeIn, cloud, shift=0.3 * DOWN, lag_ratio=0.01), run_time=2.5)
        self.say(f"{len(widths)} widths the same six iPads can report (2 orientations × 13 zoom levels)", wait=2.5)
        self.clear_all()


# ==========================================================================
class V1S1_IPadRule(RScene):
    def construct(self):
        self.tag(1, "The “iPad rule”", PX_C)
        code = code_panel(["@media (max-width: 768px) {", "  /* iPad layout */", "}"], size=30)
        code.to_edge(UP, buff=0.9)
        self.play(FadeIn(code.bg), Write(code.code), run_time=1.6)

        # --- one iPad, the 2010 mental model
        s = 0.0024
        ipad = tablet(768 * s, 1024 * s).move_to(DOWN * 0.9)
        wt = width_tag(ipad, "768 px", DEV_C, 22)
        name = txt('iPad 9.7"', 22, DEV_C).next_to(ipad, UP, buff=0.15)
        ok = check_mark(0.45).next_to(ipad, RIGHT, buff=0.4)
        self.play(DrawBorderThenFill(ipad), FadeIn(name), run_time=1.2)
        self.play(FadeIn(wt), run_time=0.6)
        self.play(ShowCreation(ok), Indicate(code.code[13:18], color=PX_C), run_time=0.8)
        self.say("One device, one width, one rule. That was the 2010 picture.", wait=1.5)

        # --- the iPad family, portrait, to scale
        s2 = 0.0019
        tabs = VGroup(*(tablet(w * s2, h * s2) for _, w, h, _ in IPADS))
        tabs.arrange(RIGHT, buff=0.42, aligned_edge=DOWN).move_to(DOWN * 0.95)
        names = VGroup(*(txt(n, 18, MUTED).next_to(t, DOWN, buff=0.14) for (n, *_), t in zip(IPADS, tabs)))
        wlabs = VGroup(*(txt(f"{w}", 24, DEV_C, weight=BOLD).next_to(nm, DOWN, buff=0.1)
                         for (_, w, _, _), nm in zip(IPADS, names)))
        marks = VGroup(*(mark_for(w).next_to(t, UP, buff=0.18) for (_, w, _, _), t in zip(IPADS, tabs)))
        self.play(
            ReplacementTransform(ipad, tabs[1]),
            FadeOut(VGroup(wt, name, ok)),
            LaggedStart(*(FadeIn(t, shift=0.3 * UP) for i, t in enumerate(tabs) if i != 1), lag_ratio=0.12),
            run_time=1.6,
        )
        self.play(LaggedStartMap(FadeIn, names, lag_ratio=0.08), LaggedStartMap(FadeIn, wlabs, lag_ratio=0.08), run_time=1.2)
        self.say("Six iPads in portrait. Same rule:", wait=0.3)
        self.play(LaggedStartMap(ShowCreation, marks, lag_ratio=0.15), run_time=1.5)
        self.say("Only 2 of 6 match, and one of them is a mini.", wait=2)

        # --- rotate: every one becomes wider than 768
        s3 = 0.00148
        land = VGroup(*(tablet(h * s3, w * s3) for _, w, h, _ in IPADS))
        land.arrange(RIGHT, buff=0.3, aligned_edge=DOWN).move_to(DOWN * 1.1)
        new_names = VGroup(*(txt(n, 18, MUTED).next_to(t, DOWN, buff=0.14) for (n, *_), t in zip(IPADS, land)))
        new_w = VGroup(*(txt(f"{h}", 24, DEV_C, weight=BOLD).next_to(nm, DOWN, buff=0.1)
                         for (_, _, h, _), nm in zip(IPADS, new_names)))
        new_marks = VGroup(*(cross_mark(0.26).next_to(t, UP, buff=0.18) for t in land))
        self.say("Rotate them.", wait=0.2)
        self.play(
            *(Transform(a, b, path_arc=PI / 2) for a, b in zip(tabs, land)),
            *(Transform(a, b) for a, b in zip(names, new_names)),
            FadeOut(marks),
            run_time=1.6,
        )
        self.play(*(Transform(a, b) for a, b in zip(wlabs, new_w)), run_time=0.8)
        self.play(LaggedStartMap(ShowCreation, new_marks, lag_ratio=0.12), run_time=1.2)
        self.say("Landscape: 0 of 6 match. Same devices, new widths.", wait=2)

        # --- Split View on the 12.9" Pro
        self.play(FadeOut(VGroup(*tabs[:5], *names, *wlabs, *new_marks)), FadeOut(self._cap), run_time=0.8)
        self._cap = None
        big_s = 0.0042
        big = tablet(1366 * big_s, 1024 * big_s).move_to(DOWN * 0.75)
        self.play(ReplacementTransform(tabs[5], big), run_time=1.2)
        scr = big.screen
        x0, top, bottom = scr.get_left()[0], scr.get_top()[1], scr.get_bottom()[1]
        split = ValueTracker(981)

        def windows():
            L = split.get_value()
            R = 1356 - L
            lw, rw = L * big_s, R * big_s
            h = top - bottom
            a = browser(lw - 0.04, h - 0.08, bar_h=0.24)
            a.move_to([x0 + 0.02 + (lw - 0.04) / 2, (top + bottom) / 2, 0])
            b = browser(rw - 0.04, h - 0.08, bar_h=0.24)
            b.move_to([x0 + lw + 10 * big_s + 0.02 + (rw - 0.04) / 2, (top + bottom) / 2, 0])
            handle = RoundedRectangle(0.05, 0.5, corner_radius=0.025).set_fill(MUTED, 1).set_stroke(width=0)
            handle.move_to([x0 + lw + 5 * big_s, (top + bottom) / 2, 0])
            g = VGroup(a, b, handle)
            for win, val in ((a, L), (b, R)):
                n = txt(f"{val:.0f} px", 30, DEV_C, weight=BOLD).move_to(win).shift(0.2 * UP)
                m = mark_for(val).set_height(0.32).next_to(n, DOWN, buff=0.2)
                g.add(n, m)
            return g

        wins = always_redraw(windows)
        sv = pill("Split View", VIOLET, 20).next_to(big, RIGHT, buff=0.3, aligned_edge=UP)
        self.play(FadeIn(wins), FadeIn(sv), run_time=1)
        self.say("Split View carves the same screen into app windows.", wait=1.5)
        self.play(split.animate.set_value(678), run_time=2.5)
        self.wait(1)
        so = browser(320 * big_s, (1024 - 60) * big_s * 0.92, bar_h=0.24)
        so.move_to(scr.get_right() + LEFT * (320 * big_s / 2 + 0.12)).set_z_index(5)
        so.outer.set_stroke(VIOLET, 3)
        so_lab = VGroup(txt("320 px", 26, DEV_C, weight=BOLD), check_mark(0.3)).arrange(DOWN).move_to(so).set_z_index(6)
        so_pill = pill("Slide Over", VIOLET, 20).next_to(sv, DOWN, buff=0.2, aligned_edge=LEFT)
        self.play(FadeIn(so, shift=LEFT), FadeIn(so_lab, shift=LEFT), FadeIn(so_pill), run_time=1.2)
        self.say("An iPad can show a phone-width window. The rule calls that “iPad”.", wait=2)

        # --- collapse everything into a scatter of widths
        wins.clear_updaters()
        allw = sorted({320, 375, 639, 678, 744, 768, 810, 820, 834, 981, 1024, 1080, 1133, 1180, 1194, 1366})
        NY = -1.0
        nl = px_line(250, 1450, 12, y=NY, step=50, labels=[320, 768, 1024, 1366])
        self.play(FadeOut(VGroup(big, wins, so, so_lab, sv, so_pill)), FadeOut(self._cap), run_time=1)
        self._cap = None
        zone = Rectangle(nl.to_x(RULE) - nl.to_x(250), 0.5).set_fill(PX_C, 0.18).set_stroke(PX_C, 1.5)
        zone.move_to([(nl.to_x(250) + nl.to_x(RULE)) / 2, NY + 0.3, 0])
        zl = mono("max-width: 768px", 20, PX_C).next_to(zone, UP, buff=0.1)
        self.play(FadeIn(nl), run_time=0.8)
        dots = VGroup(*(glow_dot([nl.to_x(w), NY, 0], DEV_C, 0.06) for w in allw))
        vals = VGroup(*(txt(f"{w}", 14, DEV_C).rotate(PI / 2).next_to(d, UP, buff=0.12) for w, d in zip(allw, dots)))
        self.play(LaggedStartMap(FadeIn, dots, scale=0.3, lag_ratio=0.08),
                  LaggedStartMap(FadeIn, vals, lag_ratio=0.08), run_time=2.2)
        big_label = txt("Every width an iPad can report (no zoom yet)", 30, DEV_C).move_to(UP * 0.9)
        self.play(FadeIn(big_label, shift=0.2 * DOWN))
        self.play(FadeIn(zone), FadeIn(zl), run_time=1)
        inside = [d for w, d in zip(allw, dots) if w <= RULE]
        self.play(*(d.animate.set_color(PX_C) for d in inside), run_time=0.8)
        caught = txt("caught: phone-size windows + a mini", 22, PX_C).next_to(nl, DOWN, buff=0.6).align_to(zone, LEFT)
        missed = txt("missed: every full-screen iPad but one", 22, DEV_C).next_to(nl, DOWN, buff=0.6).align_to(nl, RIGHT)
        self.play(FadeIn(caught), FadeIn(missed))
        self.say("“The iPad” is not a width. It is a scatter of widths, from 320 to 1366.", wait=3)
        self.clear_all()


# ==========================================================================
class V1S2_Continuum(RScene):
    def construct(self):
        self.tag(2, "Width is a continuum", PX_C)
        nl = px_line(300, 2000, 12.6, y=-1.6, step=100, labels=[320, 768, 1024, 1280, 1440, 1920])
        self.play(ShowCreation(nl.line), FadeIn(nl.ticks), FadeIn(nl.labels), run_time=1.2)
        groups = [
            ("phone", [320, 360, 375, 390, 393, 412, 414, 428, 430]),
            ("tablet", [744, 768, 800, 810, 820, 834, 1024]),
            ("laptop", [1280, 1366, 1440, 1536]),
            ("monitor", [1920]),
        ]
        dots = VGroup()
        icons = VGroup()
        for kind, ws in groups:
            row = VGroup(*(Dot([nl.to_x(w), -1.6, 0], radius=0.06, fill_color=DEV_C) for w in ws))
            dots.add(row)
            cx = np.mean([nl.to_x(w) for w in ws])
            ic = {"phone": lambda: phone(0.28, 0.56), "tablet": lambda: tablet(0.5, 0.66),
                  "laptop": lambda: laptop(0.8, 0.5), "monitor": lambda: monitor(0.8, 0.48)}[kind]()
            ic.set_stroke(width=2).move_to([cx, -0.75, 0])
            icons.add(ic)
        for row, ic in zip(dots, icons):
            self.play(LaggedStartMap(FadeIn, row, scale=0.3, lag_ratio=0.1), FadeIn(ic, shift=0.2 * DOWN), run_time=0.7)
        self.say("Common device widths: 21 tidy points.", wait=1.5)

        # a desktop browser window that the user drags: its right edge IS the dot
        w = ValueTracker(1440)
        LEFT_X = -6.75

        def win():
            right = nl.to_x(w.get_value())
            ww = right - LEFT_X
            b = browser(ww, 2.3, url="any.site")
            b.move_to([LEFT_X + ww / 2, 1.55, 0])
            tl, bw, bh = browser_content_box(b)
            hdr = Rectangle(bw - 0.3, 0.16).set_fill(CONT_C, 0.5).set_stroke(width=0)
            hdr.move_to(tl + np.array([bw / 2, -0.22, 0]))
            bars = text_bars(bw - 0.3, 0.075, 0.2, max_lines=7)
            bars.shift(tl + np.array([0.15, -0.45, 0]))
            grip = RoundedRectangle(0.06, 0.5, corner_radius=0.03).set_fill(CONT_C, 1).set_stroke(width=0)
            grip.move_to([right, 1.55, 0])
            return VGroup(b, hdr, bars, grip)

        window = always_redraw(win)
        readout = DecimalNumber(1440, num_decimal_places=0, font_size=34, color=CONT_C, group_with_commas=False)
        unit = txt("px", 26, CONT_C)
        ro = VGroup(txt("w =", 30, CONT_C), readout, unit)

        def place_ro(m):
            m.arrange(RIGHT, buff=0.12, aligned_edge=DOWN)
            x = nl.to_x(w.get_value())
            m.next_to([x, 3.0, 0], RIGHT if x < 3.5 else LEFT, buff=0.2)
            return m

        readout.add_updater(lambda d: d.set_value(w.get_value()))
        ro.add_updater(place_ro)
        cursor = always_redraw(lambda: glow_dot([nl.to_x(w.get_value()), -1.6, 0], CONT_C, 0.08))
        trail = VMobject().set_stroke(CONT_C, 8, opacity=0.7)
        lo_hi = [1440, 1440]

        def upd_trail(m):
            v = w.get_value()
            lo_hi[0], lo_hi[1] = min(lo_hi[0], v), max(lo_hi[1], v)
            m.set_points_as_corners([[nl.to_x(lo_hi[0]), -1.6, 0], [nl.to_x(lo_hi[1]), -1.6, 0]])

        trail.add_updater(upd_trail)
        drop = always_redraw(lambda: DashedLine([nl.to_x(w.get_value()), 0.35, 0], [nl.to_x(w.get_value()), -1.5, 0],
                                                dash_length=0.08).set_stroke(CONT_C, 1.5))
        self.play(FadeIn(window), FadeIn(ro), FadeIn(cursor), FadeIn(drop), run_time=1)
        self.add(trail)
        self.bring_to_front(dots, cursor)
        self.say("Now drag a desktop window.", wait=0.3)
        self.play(w.animate.set_value(420), run_time=4, rate_func=smooth)
        self.play(w.animate.set_value(1999), run_time=4, rate_func=smooth)
        self.play(w.animate.set_value(1000), run_time=2)
        self.say("Every width in between is reachable. The domain is an interval.", wait=1.5)

        # points versus interval
        for m in (trail, ro, readout):
            m.clear_updaters()
        f1 = tex(r"\text{devices: }\{320,\,375,\,768,\,1024,\,\dots\}", 34, DEV_C)
        f2 = tex(r"\text{users: }\; w \in [\,320,\ \infty)\subset\mathbb{R}", 34, CONT_C)
        fs = VGroup(f1, f2).arrange(DOWN, buff=0.3, aligned_edge=LEFT).move_to(UP * 2.0)
        self.play(FadeOut(window), FadeOut(ro), FadeOut(drop), FadeOut(cursor), run_time=0.6)
        self.play(Write(f1), run_time=1.2)
        self.play(Write(f2), run_time=1.2)
        self.wait(1)
        meas = tex(r"\lambda\big(\{w_1,\dots,w_n\}\big) = 0", 36, MUTED)
        meas_l = txt("any finite list of widths covers 0% of the line", 22, MUTED)
        meas.next_to(fs, DOWN, buff=0.35)
        meas_l.next_to(meas, DOWN, buff=0.15)
        self.play(FadeIn(meas, shift=0.2 * UP), FadeIn(meas_l), run_time=1)
        self.say("A device list tests a handful of points. Users live everywhere on the line.", wait=3)
        self.clear_all()


# ==========================================================================
class V1S3_PixelsAndZoom(RScene):
    def construct(self):
        self.tag(3, "Media queries measure CSS pixels", PX_C)
        # ---- device pixels vs CSS pixels
        n_c, n_r, cell = 12, 8, 0.32
        grid = VGroup(*(Square(cell).set_stroke(DEV_C, 1, opacity=0.6).set_fill(DEV_C, 0.08)
                        .move_to([(c - n_c / 2 + 0.5) * cell, (n_r / 2 - r - 0.5) * cell, 0])
                        for r in range(n_r) for c in range(n_c)))
        grid.move_to(LEFT * 3.3 + DOWN * 0.3)
        gl = txt("device pixels (hardware)", 22, DEV_C).next_to(grid, UP, buff=0.2)
        self.play(LaggedStartMap(FadeIn, grid, lag_ratio=0.004), FadeIn(gl), run_time=1.5)
        css = VGroup(*(Square(2 * cell).set_stroke(EM_C, 3).set_fill(EM_C, 0.0)
                       .move_to(grid.get_corner(UL) + np.array([(2 * c + 1) * cell, -(2 * r + 1) * cell, 0]))
                       for r in range(n_r // 2) for c in range(n_c // 2)))
        cl = txt("1 CSS pixel = 2 × 2 device pixels", 22, EM_C).next_to(grid, DOWN, buff=0.2)
        self.play(LaggedStartMap(ShowCreation, css, lag_ratio=0.02), FadeIn(cl), run_time=1.5)
        f = tex(r"w_{\text{css}} = \frac{W_{\text{device}}}{\text{DPR}}", 44, INK,
                t2c={r"w_{\text{css}}": EM_C, r"W_{\text{device}}": DEV_C})
        f.move_to(RIGHT * 3.3 + UP * 1.4)
        ex = tex(r"\text{iPad Air: } \frac{1640}{2} = 820", 36, MUTED).next_to(f, DOWN, buff=0.4)
        self.play(Write(f), run_time=1.2)
        self.play(FadeIn(ex, shift=0.2 * UP))
        self.say("Media queries never see hardware pixels — only CSS pixels.", wait=2)

        # ---- page zoom joins the formula
        f2 = tex(r"w_{\text{css}} = \frac{W_{\text{device}}}{\text{DPR}\cdot z}", 44, INK,
                 t2c={r"w_{\text{css}}": EM_C, r"W_{\text{device}}": DEV_C, "z": VIOLET}).move_to(f)
        zl = txt("z = browser zoom", 24, VIOLET).next_to(f2, DOWN, buff=0.4)
        self.play(TransformMatchingTex(f, f2), FadeOut(ex), run_time=1.2)
        self.play(FadeIn(zl))
        self.wait(1.5)
        self.play(FadeOut(VGroup(grid, css, gl, cl)), VGroup(f2, zl).animate.scale(0.75).to_corner(UR, buff=0.5).shift(DOWN * 0.5),
                  FadeOut(self._cap), run_time=1)
        self._cap = None

        # ---- a 1440 px desktop as the user zooms in
        axes = Plot((1, 2.6), (400, 1500), 5.6, 4.2, x_ticks=(1, 1.5, 2, 2.5), y_ticks=(600, 768, 1000, 1440),
                    x_fmt="{:.0%}", x_tick_color=VIOLET, x_label="zoom z", x_label_color=VIOLET,
                    y_label="w (CSS px)", y_label_color=EM_C)
        axes.move_to(RIGHT * 3.3 + DOWN * 0.7)
        axes.y_labels[1].set_color(PX_C)
        curve = axes.graph(lambda z: 1440 / z, color=EM_C)
        rule = axes.hline(RULE, PX_C)
        rl = mono("max-width: 768px", 16, PX_C).next_to(rule, UP, buff=0.06).align_to(rule, RIGHT)
        self.play(FadeIn(axes), run_time=1)

        z = ValueTracker(1.0)
        bsc = 0.0032

        def desk():
            zz = z.get_value()
            b = browser(1440 * bsc, 2.8, url="shop.example")
            b.move_to(LEFT * 3.6 + DOWN * 0.6)
            tl, bw, bh = browser_content_box(b)
            # content grows with zoom: fixed CSS sizes, bigger CSS px
            unit = bsc * zz
            wcss = 1440 / zz
            pad = 16 * unit
            ncol = 3 if wcss > RULE else 1
            gap = 24 * unit
            cw = (bw - 2 * pad - (ncol - 1) * gap) / ncol
            ch = min(300 * unit, bh - 2 * pad - 30 * unit - 0.05)
            cards = VGroup(*(card(cw, ch, CONT_C) for _ in range(ncol))).arrange(RIGHT, buff=gap)
            cards.move_to(tl + np.array([pad + cards.get_width() / 2, -pad - ch / 2 - 30 * unit, 0]))
            hdr = Rectangle(bw - 2 * pad, 18 * unit).set_fill(MUTED, 0.5).set_stroke(width=0)
            hdr.move_to(tl + np.array([bw / 2, -pad / 2 - 9 * unit, 0]))
            content = VGroup(hdr, cards)
            # clip to the viewport by dropping what falls below it
            keep = VGroup(*(m for m in content if m.get_bottom()[1] > tl[1] - bh - 0.01))
            return VGroup(b, keep)

        desktop = always_redraw(desk)
        cap_dev = txt("1440 device px · DPR 1", 20, DEV_C).move_to(LEFT * 3.6 + UP * 1.1)
        self.play(FadeIn(desktop), FadeIn(cap_dev), run_time=1)
        dot = always_redraw(lambda: glow_dot(axes.c2p(z.get_value(), 1440 / z.get_value()), EM_C, 0.07))
        zr = VGroup(txt("z =", 26, VIOLET), DecimalNumber(100, num_decimal_places=1, font_size=30, color=VIOLET),
                    txt("%", 24, VIOLET))
        wr = VGroup(txt("w =", 26, EM_C), DecimalNumber(1440, num_decimal_places=2, font_size=30, color=EM_C, group_with_commas=False),
                    txt("px", 24, EM_C))
        zr[1].add_updater(lambda d: d.set_value(z.get_value() * 100))
        wr[1].add_updater(lambda d: d.set_value(1440 / z.get_value()))
        for g in (zr, wr):
            g.add_updater(lambda m: m.arrange(RIGHT, buff=0.1, aligned_edge=DOWN))
        rd = VGroup(zr, wr)
        rd.add_updater(lambda m: m.arrange(RIGHT, buff=0.6).next_to(desktop[0], DOWN, buff=0.35))
        self.play(ShowCreation(curve), FadeIn(dot), FadeIn(rd), run_time=1.2)
        self.say("Same screen, same window. Only the zoom changes.", wait=0.5)
        for target in (1.1, 1.25, 1.5):
            self.play(z.animate.set_value(target), run_time=1.6)
            self.wait(0.6)
        self.play(ShowCreation(rule), FadeIn(rl), run_time=0.8)
        self.play(z.animate.set_value(1.875), run_time=2)
        hit = Circle(radius=0.22).set_stroke(PX_C, 4).move_to(axes.c2p(1.875, 768))
        self.play(ShowCreation(hit), Flash(axes.c2p(1.875, 768), color=PX_C))
        self.say("At 187.5 % zoom, a 1440 px desktop is “an iPad” to the media query.", wait=2)
        self.play(z.animate.set_value(2.5), FadeOut(hit), run_time=2)
        self.wait(1)
        frac = tex(r"110\%:\ \ \frac{1440}{1.1} = 1309.\overline{09}\ \text{px}", 34, INK).move_to(LEFT * 3.6 + UP * 2.2)
        self.play(z.animate.set_value(1.1), run_time=2)
        self.play(FadeIn(frac, shift=0.2 * DOWN))
        self.say("And widths are real numbers, not integers. Keep that in mind.", wait=2.5)
        for m in (zr[1], wr[1], zr, wr, rd):
            m.clear_updaters()
        self.clear_all()

        # ---- the map device -> width is not injective
        self.tag(4, "Width cannot identify a device", PX_C)
        target = glow_dot(RIGHT * 3.6 + DOWN * 0.2, PX_C, 0.11)
        tl = txt("w = 768", 34, PX_C, weight=BOLD).next_to(target, RIGHT, buff=0.3)
        sources = [
            (tablet(0.62, 0.82), 'iPad 9.7"  portrait', "768 / 1"),
            (laptop(1.0, 0.62), "1536 px laptop", "1536 / 200%"),
            (monitor(1.1, 0.62), "1920 px monitor", "1920 / 250%"),
            (browser(0.85, 0.6), "desktop window", "dragged to 768"),
            (VGroup(browser(1.1, 0.75), browser(0.6, 0.38).shift(0.1 * DOWN)), "page in an iframe", "<iframe width=768>"),
        ]
        rows = VGroup()
        for ic, nm, how in sources:
            ic.set_height(min(ic.get_height(), 0.8))
            label = VGroup(txt(nm, 20, INK), txt(how, 18, MUTED)).arrange(DOWN, aligned_edge=LEFT, buff=0.06)
            rows.add(VGroup(ic, label).arrange(RIGHT, buff=0.3))
        for r in rows:
            r[0].set_width(min(r[0].get_width(), 1.1))
        rows.arrange(DOWN, buff=0.3, aligned_edge=LEFT).move_to(LEFT * 3.6 + DOWN * 0.3)
        arrows = VGroup(*(Arrow(r.get_right(), target[1].get_center(), buff=0.15, thickness=2.5, fill_color=MUTED)
                          for r in rows))
        self.play(LaggedStartMap(FadeIn, rows, shift=0.2 * RIGHT, lag_ratio=0.15), run_time=1.6)
        self.play(LaggedStartMap(GrowArrow, arrows, lag_ratio=0.12), FadeIn(target), FadeIn(tl), run_time=1.6)
        fmap = tex(r"f:\ \text{device}\ \longmapsto\ w", 38, INK).to_edge(UP, buff=1.1)
        self.play(Write(fmap))
        self.say("Five very different situations, one width.", wait=1.5)
        back = VGroup(*(Arrow(target[1].get_center(), r.get_right(), buff=0.15, thickness=2.5, fill_color=PX_C)
                        for r in rows))
        qs = VGroup(*(txt("?", 30, PX_C, weight=BOLD).move_to(a.get_center() + 0.22 * UP) for a in back))
        inv = tex(r"f^{-1}(768) = \ ?", 38, PX_C).next_to(fmap, DOWN, buff=0.25)
        self.play(ReplacementTransform(arrows, back), FadeIn(qs, lag_ratio=0.1), Write(inv), run_time=1.6)
        self.say("f is not injective, so it has no inverse. A media query sees w, never the device.", wait=3)
        self.clear_all()


# ==========================================================================
def segment(nl, lo, hi, color, y, closed_lo=True, closed_hi=True, h=0.22, show_lo=True, show_hi=True):
    """A coloured interval on number line `nl` with open/closed end markers."""
    xa, xb = nl.to_x(lo), nl.to_x(hi)
    bar = Rectangle(max(xb - xa, 0.001), h).set_fill(color, 0.55).set_stroke(width=0)
    bar.move_to([(xa + xb) / 2, y, 0])
    g = VGroup(bar)
    for x, closed, show in ((xa, closed_lo, show_lo), (xb, closed_hi, show_hi)):
        if not show:
            continue
        c = Circle(radius=0.11).move_to([x, y, 0]).set_stroke(color, 3)
        c.set_fill(color if closed else BG, 1)
        g.add(c)
    return g


class V1S4_FractionalGap(RScene):
    def construct(self):
        self.tag(5, "Integer thinking, real-valued widths", PX_C)
        A_C, B_C = CONT_C, VIOLET
        codeA = code_panel(["@media (max-width: 767px) { /* phone  */ }"], 24)
        codeB = code_panel(["@media (min-width: 768px) { /* tablet */ }"], 24)
        codeA.bg.set_stroke(A_C, 2.5)
        codeB.bg.set_stroke(B_C, 2.5)
        codes = VGroup(codeA, codeB).arrange(DOWN, buff=0.18, aligned_edge=LEFT).to_edge(UP, buff=0.85)
        self.play(FadeIn(codeA, shift=0.2 * DOWN), run_time=0.8)
        self.play(FadeIn(codeB, shift=0.2 * DOWN), run_time=0.8)

        Y1 = 0.55
        nl = px_line(700, 840, 12, y=Y1, step=10, labels=[700, 720, 740, 767, 800, 820, 840])
        nl.labels[3].set_color(INK)
        a = segment(nl, 700, 767, A_C, Y1 + 0.3, show_lo=False)
        b = segment(nl, 768, 840, B_C, Y1 + 0.3, show_hi=False)
        self.play(FadeIn(nl), run_time=0.8)
        self.play(GrowFromEdge(a, LEFT), GrowFromEdge(b, RIGHT), run_time=1.2)
        self.say("At this scale the two rules look like a clean split.", wait=1.5)

        # magnifier: a lens on 766.5..768.5 opening into an inset line
        lo, hi = 766.6, 768.4
        lens = Rectangle(nl.to_x(hi) - nl.to_x(lo), 0.8).move_to([nl.to_x(767.5), Y1 + 0.2, 0])
        lens.set_stroke(INK, 2)
        Y2 = -2.0
        inset = px_line(lo, hi, 12, y=Y2, step=0.1, labels=[767, 767.5, 768], label_size=20)
        inset.labels.set_color(INK)
        frame_box = Rectangle(12.6, 1.6).move_to([0, Y2 + 0.25, 0]).set_stroke(INK, 2)
        con = VGroup(Line(lens.get_corner(DL), frame_box.get_corner(UL)),
                     Line(lens.get_corner(DR), frame_box.get_corner(UR))).set_stroke(INK, 1.5, opacity=0.5)
        self.play(ShowCreation(lens), FadeOut(self._cap), run_time=0.6)
        self._cap = None
        self.play(ShowCreation(con), ShowCreation(frame_box), FadeIn(inset), run_time=1.2)
        ia = segment(inset, lo, 767, A_C, Y2 + 0.3, show_lo=False)
        ib = segment(inset, 768, hi, B_C, Y2 + 0.3, show_hi=False)
        self.play(GrowFromEdge(ia, LEFT), GrowFromEdge(ib, RIGHT), run_time=1)
        gap = Rectangle(inset.to_x(768) - inset.to_x(767) - 0.25, 0.22).set_fill(BAD_C, 0.25).set_stroke(BAD_C, 2)
        gap.move_to([inset.to_x(767.5), Y2 + 0.3, 0])
        gl = txt("767 < w < 768: no rule applies", 22, BAD_C).next_to(frame_box, DOWN, buff=0.2)
        self.play(FadeIn(gap), Write(gl), run_time=1.2)
        self.wait(1)

        # a real viewport lands in the gap
        wv = 844 / 1.1
        vdot = glow_dot([inset.to_x(wv), Y2 + 0.3, 0], INK, 0.09)
        vlab = tex(r"\frac{844}{1.1} = 767.\overline{27}", 32, INK).next_to(vdot, UP, buff=0.35)
        vsrc = txt("844 px window at 110% zoom", 20, MUTED).next_to(vlab, UP, buff=0.1)
        self.play(FadeIn(vdot, scale=0.4), FadeIn(vlab), FadeIn(vsrc), run_time=1)
        self.play(Flash(vdot[1].get_center(), color=BAD_C, line_length=0.3), gap.animate.set_fill(BAD_C, 0.5))
        self.say("Neither query matches: the page falls back to its unstyled base layout.", wait=2.5)

        # the usual patch: 767.98
        codeA2 = code_panel(["@media (max-width: 767.98px) { /* phone  */ }"], 24).move_to(codeA, aligned_edge=LEFT)
        codeA2.bg.set_stroke(A_C, 2.5)
        ia2 = segment(inset, lo, 767.98, A_C, Y2 + 0.3, show_lo=False)
        gap2 = Rectangle(inset.to_x(768) - inset.to_x(767.98), 0.22).set_fill(BAD_C, 0.6).set_stroke(BAD_C, 1)
        gap2.move_to([inset.to_x(767.99), Y2 + 0.3, 0])
        gl2 = txt("the common .02 px patch shrinks the gap; it never closes it", 22, WARN_C).move_to(gl)
        self.play(FadeOut(vdot), FadeOut(vlab), FadeOut(vsrc), FadeOut(self._cap), run_time=0.5)
        self._cap = None
        self.play(FadeTransform(codeA, codeA2), Transform(ia, ia2), ReplacementTransform(gap, gap2),
                  FadeTransform(gl, gl2), run_time=1.5)
        self.wait(2)

        # the opposite mistake: both rules contain 768
        codeA3 = code_panel(["@media (max-width: 768px) { /* phone  */ }"], 24).move_to(codeA2, aligned_edge=LEFT)
        codeA3.bg.set_stroke(A_C, 2.5)
        ia3 = segment(inset, lo, 768, A_C, Y2 + 0.42, show_lo=False, h=0.16)
        ib3 = segment(inset, 768, hi, B_C, Y2 + 0.18, show_hi=False, h=0.16)
        both = Circle(radius=0.22).set_stroke(WARN_C, 4).move_to([inset.to_x(768), Y2 + 0.3, 0])
        gl3 = txt("max-width: 768px + min-width: 768px → at exactly 768 both apply", 22, WARN_C).move_to(gl)
        self.play(FadeTransform(codeA2, codeA3), Transform(ia, ia3), Transform(ib, ib3), FadeOut(gap2),
                  FadeTransform(gl2, gl3), run_time=1.5)
        self.play(ShowCreation(both), Flash(both.get_center(), color=WARN_C))
        self.wait(2)

        # the fix: half-open intervals with range syntax
        codeA4 = code_panel(["@media (width <  768px) { /* phone  */ }"], 24).move_to(codeA3, aligned_edge=LEFT)
        codeB4 = code_panel(["@media (width >= 768px) { /* tablet */ }"], 24).move_to(codeB, aligned_edge=LEFT)
        codeA4.bg.set_stroke(A_C, 2.5)
        codeB4.bg.set_stroke(B_C, 2.5)
        ia4 = segment(inset, lo, 768, A_C, Y2 + 0.3, closed_hi=False, show_lo=False)
        ib4 = segment(inset, 768, hi, B_C, Y2 + 0.3, show_hi=False)
        gl4 = tex(r"(-\infty,\,768)\ \cup\ [768,\,\infty) = \mathbb{R},\quad \text{disjoint}", 32, OK_C).move_to(gl)
        self.play(FadeTransform(codeA3, codeA4), FadeTransform(codeB, codeB4),
                  Transform(ia, ia4), Transform(ib, ib4), FadeOut(both), FadeOut(gl3), run_time=1.5)
        self.play(Write(gl4), run_time=1.2)
        lvl = VGroup(pill("Media Queries", OK_C, 18), pill("Level 4", OK_C, 18), pill("range syntax", OK_C, 18))
        lvl.arrange(DOWN, buff=0.08, aligned_edge=LEFT).next_to(codes, RIGHT, buff=0.3)
        self.play(FadeIn(lvl, shift=0.2 * LEFT))
        self.say("Half-open intervals partition the line exactly: every real w matches one rule.", wait=3)
        self.say("That fixes the boundary. It does not fix the choice of 768.", wait=2.5)
        self.clear_all()


# ==========================================================================
class V1S5_Explosion(RScene):
    def construct(self):
        self.tag(6, "A target that multiplies and moves", PX_C)
        # ---- the multiplication
        tabs = VGroup(*(tablet(w * 0.00062, h * 0.00062).set_stroke(width=1.5) for _, w, h, _ in IPADS))
        tabs.arrange(RIGHT, buff=0.08, aligned_edge=DOWN)
        rot = VGroup(tablet(0.4, 0.55), tablet(0.55, 0.4)).arrange(RIGHT, buff=0.1, aligned_edge=DOWN)
        zoom_ic = VGroup(Circle(radius=0.22).set_stroke(VIOLET, 3),
                         Line(ORIGIN, 0.22 * DR).set_stroke(VIOLET, 4).shift(0.18 * DR),
                         txt("%", 20, VIOLET, weight=BOLD))
        zoom_ic[2].move_to(zoom_ic[0])
        parts = [
            (tabs, "6 models"),
            (txt("×", 40, MUTED), None),
            (rot, "2 orientations"),
            (txt("×", 40, MUTED), None),
            (zoom_ic, "13 zoom levels"),
            (txt("=", 40, MUTED), None),
            (txt("156", 56, DEV_C, weight=BOLD), "combinations"),
        ]
        row = VGroup()
        for m, lab in parts:
            if lab:
                row.add(VGroup(m, txt(lab, 20, MUTED).next_to(m, DOWN, buff=0.15)))
            else:
                row.add(m)
        row.arrange(RIGHT, buff=0.45).move_to(UP * 1.9)
        for item in row:
            self.play(FadeIn(item, shift=0.2 * UP), run_time=0.45)
        self.wait(0.5)

        nl = px_line(0, 2800, 12.4, y=-2.3, step=200, labels=[0, 400, 768, 1200, 1600, 2000, 2400, 2800])
        nl.labels[2].set_color(PX_C)
        widths = sorted({round(w / z, 2) for _, a, b, _ in IPADS for w in (a, b) for z in ZOOMS})
        cloud = VGroup()
        stack = {}
        for wv in widths:
            k_bin = int(wv // 60)
            k = stack.get(k_bin, 0)
            stack[k_bin] = k + 1
            cloud.add(Dot([nl.to_x(wv), -2.15 + 0.12 * k, 0], radius=0.045, fill_color=DEV_C))
        self.play(FadeIn(nl), run_time=0.6)
        self.play(LaggedStart(*(FadeIn(d, shift=1.2 * DOWN) for d in cloud), lag_ratio=0.012), run_time=3)
        one = Line([nl.to_x(768), -2.4, 0], [nl.to_x(768), 0.15, 0]).set_stroke(PX_C, 4)
        one_l = mono("one rule: 768px", 20, PX_C).next_to(one, UP, buff=0.08)
        self.play(ShowCreation(one), FadeIn(one_l))
        self.say(f"{len(widths)} distinct widths from six iPads alone, spread from 248 px to 2732 px.", wait=2)
        more = VGroup(*(pill(s, VIOLET, 18) for s in ("Split View", "Slide Over", "iframes", "OS display scaling", "foldables")))
        more.arrange(RIGHT, buff=0.2).move_to(UP * 0.85 + RIGHT * 1.5)
        self.play(LaggedStartMap(FadeIn, more, shift=0.2 * DOWN, lag_ratio=0.15), run_time=1.2)
        self.say("…and every one of these multiplies the count again.", wait=2)
        self.clear_all()

        # ---- moving target: iPad widths over time
        self.tag(6, "A target that multiplies and moves", PX_C)
        pts = [(2010, 768), (2011, 768), (2012, 768), (2013, 768), (2014, 768), (2015, 768), (2015.3, 1024),
               (2016, 768), (2017, 768), (2017.3, 834), (2018, 834), (2019, 810), (2019.3, 834), (2020, 820),
               (2021, 744), (2022, 820), (2024, 1024), (2024.3, 1032)]
        pl = Plot((2009, 2025), (700, 1080), 11.0, 4.6, x_ticks=(2010, 2013, 2016, 2019, 2022, 2025),
                  y_ticks=(744, 768, 810, 834, 1024), x_label="year of release", y_label="portrait width (CSS px)",
                  y_label_color=DEV_C)
        pl.move_to(DOWN * 0.3)
        pl.y_labels[1].set_color(PX_C)
        self.play(FadeIn(pl), run_time=1)
        rule = pl.hline(768, PX_C, 3)
        rule_l = mono("written in 2010: max-width: 768px", 18, PX_C).next_to(rule, UP, buff=0.08).align_to(rule, LEFT).shift(RIGHT * 0.2)
        self.play(ShowCreation(rule), FadeIn(rule_l))
        year = ValueTracker(2009)
        yl = VGroup(txt("year", 22, MUTED), Integer(2009, font_size=40, color=INK, group_with_commas=False))
        yl.arrange(RIGHT, buff=0.15, aligned_edge=DOWN).to_corner(UR, buff=0.5).shift(DOWN * 0.4)
        yl[1].add_updater(lambda m: m.set_value(int(year.get_value())))
        self.add(yl)
        dots = VGroup()
        for x, wv in pts:
            col = PX_C if wv == 768 else DEV_C
            d = glow_dot(pl.c2p(x, wv), col, 0.08)
            dots.add(d)
        for (x, wv), d in zip(pts, dots):
            self.play(year.animate.set_value(x), FadeIn(d, scale=0.3), run_time=0.35)
        self.play(year.animate.set_value(2025), run_time=0.4)
        yl[1].clear_updaters()
        self.say("Since 2017, new iPads keep drifting off 768. The rule stayed where it was written.", wait=3)
        self.clear_all()


# ==========================================================================
M_CARD, GAP, PAD = 256, 24, 16   # card min width, grid gap, page padding (CSS px)


def device_cols(w):
    return 3 if w >= RULE else 1


def content_cols(w):
    n = 1
    while (n + 1) * M_CARD + n * GAP + 2 * PAD <= w and n < 4:
        n += 1
    return n


def card_w(w, n):
    return (w - 2 * PAD - (n - 1) * GAP) / n


class V1S6_WhereItBreaks(RScene):
    def construct(self):
        self.tag(7, "Where layouts actually break", PX_C)
        S = 0.0080            # scene units per CSS px (browser and plot share it)
        X0 = -6.6             # browser left edge
        pl = Plot((300, 1200), (0, 800), 900 * S, 2.75, x_ticks=(320, 568, 768, 848, 1024, 1128),
                  y_ticks=(256, 536), y_label="card width (px)", label_size=16)
        pl.shift(np.array([X0 + 300 * S, -2.95, 0]) - pl.ref.get_center())
        w_ax = txt("w", 22, INK).next_to(pl.x_axis, RIGHT, buff=0.12)
        pl.add(w_ax)
        pl.x_labels[2].set_color(PX_C)
        for i in (1, 3, 5):
            pl.x_labels[i].set_opacity(0)

        red = pl.band(300, 1200, BAD_C, 0.12, 0, 256)
        grn = pl.band(300, 1200, OK_C, 0.10, 256, 536)
        org = pl.band(300, 1200, WARN_C, 0.10, 536, 800)
        z_l = VGroup(
            txt("too narrow: overflows", 15, BAD_C).move_to(pl.c2p(1050, 128)),
            txt("fits", 15, OK_C).move_to(pl.c2p(1160, 400)),
            txt("too wide: room for another card", 15, WARN_C).move_to(pl.c2p(1010, 720)),
        )
        mode = {"fn": device_cols}
        w = ValueTracker(320)

        def page():
            wv = w.get_value()
            n = mode["fn"](wv)
            b = browser(wv * S, 2.2, url="shop.example")
            b.move_to([X0 + wv * S / 2, 2.0, 0])
            tl, bw, bh = browser_content_box(b)
            cw = card_w(wv, n) * S
            cards = VGroup(*(card(cw, 1.45, CONT_C, need_w=M_CARD * S) for _ in range(n))).arrange(RIGHT, buff=GAP * S)
            cards.move_to(tl + np.array([PAD * S + cards.get_width() / 2, -0.25 - 0.75, 0]))
            hdr = Rectangle(bw - 2 * PAD * S, 0.1).set_fill(MUTED, 0.5).set_stroke(width=0)
            hdr.move_to(tl + np.array([bw / 2, -0.13, 0]))
            return VGroup(b, hdr, cards)

        def curve_for(fn, color):
            segs = VGroup()
            edges = [300] + [x for x in (568, 768, 848, 1128) if fn(x) != fn(x - 0.01)] + [1200]
            for a, bnd in zip(edges[:-1], edges[1:]):
                n = fn((a + bnd) / 2)
                segs.add(pl.graph(lambda x, n=n: card_w(x, n), a, bnd - 0.01, n=40, color=color, width=4))
            return segs

        def state_color(c):
            return BAD_C if c < M_CARD else (WARN_C if c > 2 * M_CARD + GAP else OK_C)

        site = always_redraw(page)
        dot = always_redraw(lambda: glow_dot(pl.c2p(w.get_value(), card_w(w.get_value(), mode["fn"](w.get_value()))),
                                             state_color(card_w(w.get_value(), mode["fn"](w.get_value()))), 0.08))
        guide = always_redraw(lambda: DashedLine([X0 + w.get_value() * S, 0.9, 0], pl.c2p(w.get_value(), 0),
                                                 dash_length=0.07).set_stroke(MUTED, 1.2))
        RX = 5.15   # centre of the right-hand column
        code = code_panel(["@media (min-width: 768px) {", "  .grid { --cols: 3 }", "}"], 18)
        code.move_to([RX, 2.4, 0])
        self.play(FadeIn(pl), FadeIn(red), FadeIn(grn), FadeIn(org), FadeIn(z_l), run_time=1)
        self.play(FadeIn(site), FadeIn(code), run_time=1)
        need = VGroup(txt("each card needs", 20, INK), tex(r"m = 256\ \text{px}", 30, INK)).arrange(DOWN, buff=0.1)
        need.next_to(code, DOWN, buff=0.3)
        self.play(FadeIn(need))
        dev_curve = curve_for(device_cols, PX_C)
        self.add(guide, dot)
        self.say("Sweep the width with the device rule in place.", wait=0.2)
        self.play(w.animate.set_value(760), ShowCreation(dev_curve[0]), run_time=5, rate_func=linear)
        self.say("Above 568 px the single card is wider than two cards need.", run_time=0.5)
        self.play(w.animate.set_value(800), run_time=1.5)
        self.play(ShowCreation(dev_curve[1]), run_time=0.2)
        self.say("At 768 the rule jumps to 3 columns: each card gets 229 px < 256. Overflow.", wait=2.5)
        zone = pl.band(768, 848, BAD_C, 0.35, 0, 800)
        zone_l = txt("broken: 768–848", 18, BAD_C, weight=BOLD).next_to(zone, UP, buff=0.05)
        self.play(FadeIn(zone), FadeIn(zone_l))
        self.play(w.animate.set_value(1200), ShowCreation(dev_curve[2] if len(dev_curve) > 2 else VMobject()), run_time=3, rate_func=linear)
        self.wait(1)

        # ---- ask the content instead
        f = tex(r"W_n = n\,m + (n-1)\,g + 2p", 28, EM_C).next_to(code, DOWN, buff=0.3)
        vals = VGroup(*(tex(rf"W_{k} = {W_}", 28, EM_C) for k, W_ in ((2, 568), (3, 848), (4, 1128))))
        vals.arrange(DOWN, buff=0.12, aligned_edge=LEFT).next_to(f, DOWN, buff=0.2)
        pg = tex(r"m{=}256,\ g{=}24,\ p{=}16", 24, MUTED).next_to(vals, DOWN, buff=0.2)
        self.say("Now ask the content: how wide must the page be to fit n cards?", wait=0.5)
        self.play(FadeOut(need), Write(f), run_time=1.2)
        self.play(FadeIn(vals, shift=0.2 * DOWN), FadeIn(pg))
        code2 = code_panel(["@media (width >= 35.5em) {…}", "@media (width >= 53em)   {…}",
                            "@media (width >= 70.5em) {…}"], 17).move_to(code)
        cont_curve = curve_for(content_cols, EM_C)
        mode["fn"] = content_cols
        self.play(FadeOut(dev_curve), FadeOut(zone), FadeOut(zone_l), FadeTransform(code, code2), run_time=1)
        for i in (1, 3, 5):
            pl.x_labels[i].set_opacity(1).set_color(EM_C)
        bps = VGroup(*(pl.vline(x, EM_C, 2) for x in (568, 848, 1128)))
        self.play(FadeIn(bps), run_time=0.8)
        self.play(w.animate.set_value(320), run_time=1.5)
        self.play(w.animate.set_value(1200), ShowCreation(cont_curve), run_time=6, rate_func=linear)
        self.say("The curve never leaves the green band. 568, 848, 1128: numbers no device chose.", wait=3)
        self.say("848 px ÷ 16 = 53em. Part 2 is how to find these numbers; Part 3 is why em.", wait=3)
        self.clear_all()


# ==========================================================================
class V1S7_Summary(RScene):
    def construct(self):
        self.tag(8, "Why it is doomed, in four pictures", PX_C)
        panels = VGroup()
        for i in range(4):
            r = RoundedRectangle(6.4, 2.7, corner_radius=0.15).set_fill(PANEL, 1).set_stroke(EDGE, 2)
            panels.add(r)
        panels.arrange_in_grid(2, 2, buff=0.3).move_to(DOWN * 0.15)

        # 1 continuum
        p = panels[0]
        nl = px_line(300, 2000, 5.0, y=0)
        nl.move_to(p.get_center() + 0.1 * DOWN)
        band = Line(nl.line.get_start(), nl.line.get_end()).set_stroke(CONT_C, 8, opacity=0.6)
        ds = VGroup(*(Dot(nl.line.point_from_proportion((v - 300) / 1700), radius=0.06, fill_color=DEV_C) for v in (375, 768, 1024, 1440, 1920)))
        t1 = txt("widths form a continuum; devices are points", 20, INK).next_to(p.get_top(), DOWN, buff=0.25)
        g1 = VGroup(nl, band, ds, t1)

        # 2 not injective
        p = panels[1]
        tgt = glow_dot(p.get_center() + RIGHT * 1.6 + 0.2 * DOWN, PX_C, 0.08)
        srcs = VGroup(*(Dot(p.get_center() + LEFT * 1.8 + UP * (0.6 - 0.4 * k) + 0.2 * DOWN, radius=0.07, fill_color=DEV_C) for k in range(4)))
        arr = VGroup(*(Arrow(s.get_center(), tgt[1].get_center(), buff=0.12, thickness=2, fill_color=MUTED) for s in srcs))
        t2 = tex(r"f:\text{device}\mapsto w \ \text{ has no inverse}", 26, INK).next_to(p.get_top(), DOWN, buff=0.25)
        g2 = VGroup(srcs, arr, tgt, t2)

        # 3 gaps / overlaps
        p = panels[2]
        il = px_line(766.5, 768.5, 5.0, y=0, labels=[767, 768], label_size=16)
        il.move_to(p.get_center() + 0.25 * DOWN)
        sa = segment(il, 766.5, 767, CONT_C, il.line.get_y() + 0.25, show_lo=False, h=0.16)
        sb = segment(il, 768, 768.5, VIOLET, il.line.get_y() + 0.25, show_hi=False, h=0.16)
        gp = Rectangle(il.to_x(768) - il.to_x(767) - 0.2, 0.16).set_fill(BAD_C, 0.5).set_stroke(width=0)
        gp.move_to([il.to_x(767.5), il.line.get_y() + 0.25, 0])
        t3 = txt("integer edges leave gaps and overlaps", 20, INK).next_to(p.get_top(), DOWN, buff=0.25)
        g3 = VGroup(il, sa, sb, gp, t3)

        # 4 explosion
        p = panels[3]
        rng = np.random.default_rng(7)
        cl = VGroup(*(Dot(p.get_center() + np.array([np.clip(rng.normal(0, 1.1), -2.9, 2.9), np.clip(rng.normal(-0.2, 0.35), -1.0, 0.6), 0]),
                          radius=0.035, fill_color=DEV_C) for _ in range(140)))
        cl.set_opacity(0.85)
        t4 = txt("the device set multiplies and keeps moving", 20, INK).next_to(p.get_top(), DOWN, buff=0.25)
        g4 = VGroup(cl, t4)

        for pnl, g in zip(panels, (g1, g2, g3, g4)):
            self.play(FadeIn(pnl), FadeIn(g, lag_ratio=0.05), run_time=1.0)
            self.wait(1.2)
        out = VGroup(txt("So breakpoints must come from the", 30, INK), txt("content", 30, EM_C, weight=BOLD))
        out.arrange(RIGHT, buff=0.15).to_edge(DOWN, buff=0.3)
        self.play(FadeIn(out, shift=0.2 * UP))
        self.wait(1.5)
        nxt = txt("→ Part 2", 26, EM_C, weight=BOLD).next_to(out, RIGHT, buff=0.4)
        self.play(FadeIn(nxt, shift=0.2 * LEFT))
        self.wait(2.5)
        self.clear_all()
