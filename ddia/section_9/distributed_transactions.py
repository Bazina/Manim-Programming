import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from manim import (
    config,
    Scene,
    VGroup,
    Text,
    RoundedRectangle,
    Rectangle,
    Line,
    Arrow,
    DashedLine,
    DashedVMobject,
    Circle,
    ValueTracker,
    FadeIn,
    FadeOut,
    Create,
    Transform,
    GrowArrow,
    AddTextLetterByLetter,
    Circumscribe,
    Indicate,
    Wiggle,
    AnimationGroup,
    always_redraw,
    UP,
    DOWN,
    LEFT,
    RIGHT,
    UL,
    DR,
    WHITE,
    GREY_A,
    GREY_B,
    BLUE,
    GREEN,
    RED,
    ORANGE,
    TEAL,
    PURPLE,
    YELLOW,
    BOLD,
)

try:
    from manim_slides import Slide as BaseSlide
except Exception:
    BaseSlide = Scene

from libs.ddia_components import (
    DARK_BG,
    FONT,
    ICON_DATABASE,
    ICON_SERVER,
    ICON_STOPWATCH,
    ICON_CHECK,
    ICON_DANGER,
    ICON_BOMB,
    ICON_LOCK,
    ICON_USER,
    ICON_CHART,
    ICON_STRUCTURE,
    ICON_BOOK,
    ICON_SHIELD,
    create_rect_glow,
    make_code_text,
    make_icon,
)
from libs.slide_style import SlideStyleMixin
import libs.ddia_components as _ddia
import libs.slide_style as _slide_style

_raw_label = _ddia.make_label


def make_label(text, font_size=20, color=WHITE, weight=BOLD):
    """Pango spaces letters too widely at small font sizes, so text looks flat
    and stretched. Rendering 4x larger and scaling down keeps normal spacing."""
    return _raw_label(text, font_size=font_size * 4, color=color, weight=weight).scale(0.25)


# The shared helpers (_section_header, _icon_row_card, make_comparison_table)
# look make_label up in their own modules. Point them at the fix while this deck renders.
_ddia.make_label = make_label
_slide_style.make_label = make_label

ICON_KAFKA = "assets/icons/tech/kafka.svg"

DARK_BG_PAGE = "#0D1117"
config.background_color = DARK_BG_PAGE

# ── Timeline layout constants (same mapping as sheet 4) ────────────────
_TL_X0 = -5.0   # timeline x start
_TL_X1 = 6.2    # timeline x end
_T_MAX = 8.5    # total time units across the timeline
_LABEL_X = -6.3  # x-center for client letter circles
_ICN_X = -5.55  # x-center for sequence row icons

# ── Saga stage columns ─────────────────────────────────────────────────
_COLS = [-4.5, -1.3, 1.9]
_ORCH_POS = [-1.3, 2.35, 0]
_SVC_Y = 0.85
_TABLE_Y = -0.9

# ── Service colors ─────────────────────────────────────────────────────
C_BOOK = BLUE
C_PAY = ORANGE
C_ACC = PURPLE
C_COORD = TEAL
C_LOCK = YELLOW


def _tx(t):
    """Convert time unit to Manim x-coordinate."""
    return _TL_X0 + t * (_TL_X1 - _TL_X0) / _T_MAX


class DistributedTransactions(SlideStyleMixin, BaseSlide):

    # Avoid reverse-video generation to prevent PyAV malloc failures on long renders.
    max_duration_before_split_reverse = 8.0

    def construct(self):
        # Part 0: setup
        self.scene_title()
        self.scene_story()
        self.scene_schema()
        self.scene_prerequisites()
        # Part 1: one database
        self.scene_write_skew()
        self.scene_phantom()
        self.scene_materialize_conflicts()
        self.scene_two_phase_locking()
        # Part 2: 2PC
        self.scene_single_db_baseline()
        self.scene_why_not_one_phase()
        self.scene_2pc_happy_path()
        self.scene_2pc_vote_no()
        self.scene_2pc_coordinator_crash()
        self.scene_2pc_recovery()
        self.scene_2pc_cost()
        # Part 3: Saga
        self.scene_saga_intro()
        self.scene_saga_happy_path()
        self.scene_saga_failures()
        self.scene_saga_crash_and_retry()
        self.scene_saga_no_isolation()
        self.scene_saga_orchestration_vs_choreography()
        # Part 4: distributed locks
        self.scene_lock_without_fencing()
        self.scene_lock_with_fencing()
        # Part 5: wrap up
        self.scene_compare()
        self.scene_closing()

    # ═════════════════════════════════════════════════════════════════
    # Style helpers
    # ═════════════════════════════════════════════════════════════════

    def _clear(self):
        self.play(FadeOut(*self.mobjects))

    def _end_scene(self, wait=2):
        self.wait(wait)
        self._next_slide()
        self._clear()

    def _header(self, text, color=TEAL, demo=None):
        header = self._section_header(text, color=color)
        self.play(AddTextLetterByLetter(header, time_per_char=0.03))
        if demo:
            tag = self._chip(f"demo/{demo}", GREY_B, font_size=9)
            tag.move_to([7.0 - tag.width / 2 - 0.15, 3.0, 0])
            self.play(FadeIn(tag), run_time=0.3)
        self.wait(0.3)
        return header

    def _card(self, title, desc, color, width=11.5, height=None, title_size=14,
              desc_size=12, align="left", pad=0.5):
        """Title + description card. Text sits at a fixed left padding (or centered)."""
        edge = {"aligned_edge": LEFT} if align == "left" else {}
        t = make_label(title, font_size=title_size, color=color)
        d = VGroup(*[make_label(line, font_size=desc_size, color=GREY_A) for line in desc.split("\n")])
        d.arrange(DOWN, buff=0.14, **edge)
        content = VGroup(t, d).arrange(DOWN, buff=0.22, **edge)
        box = RoundedRectangle(
            corner_radius=0.1,
            width=width,
            height=height or content.height + 0.7,
            fill_color=DARK_BG,
            fill_opacity=0.9,
            stroke_color=color,
            stroke_width=1.4,
        )
        content.move_to(box.get_center())
        if align == "left":
            content.align_to(box, LEFT).shift(RIGHT * pad)
        return VGroup(box, content)

    def _node(self, icon_path, label, color, icon_h=0.42, font_size=11):
        """Icon above label (arch_node from the weather project)."""
        ic = make_icon(icon_path, color=color, height=icon_h)
        lbl = make_label(label, font_size=font_size, color=color)
        return VGroup(ic, lbl).arrange(DOWN, buff=0.1)

    def _chip(self, text, color, font_size=10):
        if "\n" in text:
            lbl = VGroup(*[make_label(line, font_size=font_size, color=color) for line in text.split("\n")])
            lbl.arrange(DOWN, buff=0.12, aligned_edge=LEFT)
        else:
            lbl = make_label(text, font_size=font_size, color=color)
        box = RoundedRectangle(
            corner_radius=0.08,
            width=lbl.width + 0.26,
            height=lbl.height + 0.18,
            fill_color=DARK_BG,
            fill_opacity=0.95,
            stroke_color=color,
            stroke_width=1.2,
        )
        lbl.move_to(box.get_center())
        return VGroup(box, lbl)

    def _caption(self, text, color=GREY_A, y=-3.35, font_size=11):
        cap = make_label(text, font_size=font_size, color=color)
        cap.move_to([0, y, 0])
        return cap

    def _play_glow(self, mob, color, pad=0.2):
        """Glow behind an opaque box, then bring *mob* back on top."""
        box = RoundedRectangle(
            corner_radius=0.1,
            width=mob.width + pad,
            height=mob.height + pad,
            stroke_color=color,
            stroke_width=1.4,
            fill_color=DARK_BG,
            fill_opacity=1.0,
        )
        box.move_to(mob.get_center())
        glow = create_rect_glow(box, color=color, max_opacity=0.12)
        self.play(FadeIn(VGroup(glow, box)))
        self.bring_to_front(mob)
        return VGroup(glow, box)

    def _dashed_arrow(self, start, end, color, stroke_width=1.6):
        line = DashedLine(start, end, dash_length=0.1, color=color, stroke_width=stroke_width)
        line.add_tip(tip_length=0.13, tip_width=0.13)
        return line

    # ─── Sheet 4 timeline helpers ─────────────────────────────────────
    def _client_row(self, letter, name, y, color):
        """Horizontal timeline row with client circle label on left."""
        circ = Circle(radius=0.21, stroke_color=color, stroke_width=1.5)
        circ.set_fill(DARK_BG, opacity=0.9)
        circ.move_to([_LABEL_X + 0.35, y, 0])
        ltr = make_label(letter, font_size=11, color=color)
        ltr.move_to(circ.get_center())
        client_lbl = make_label(name, font_size=8, color=color)
        client_lbl.next_to(circ, UP, buff=0.07)
        tl = Line(
            [_TL_X0, y, 0], [_TL_X1, y, 0],
            stroke_color=color, stroke_width=1.0, stroke_opacity=0.35,
        )
        tip = Arrow(
            [_TL_X1 - 0.05, y, 0], [_TL_X1 + 0.25, y, 0],
            buff=0, stroke_width=1.5, color=color, tip_length=0.13,
        )
        return VGroup(client_lbl, circ, ltr, tl, tip)

    def _db_row(self, label, y):
        """Database timeline at bottom."""
        ic = make_icon(ICON_DATABASE, color=GREY_B, height=0.3)
        ic.move_to([_LABEL_X + 0.35, y, 0])
        lbl = make_label(label, font_size=8, color=GREY_B)
        lbl.next_to(ic, UP, buff=0.07)
        tl = Line(
            [_TL_X0, y, 0], [_TL_X1, y, 0],
            stroke_color=GREY_B, stroke_width=2.0, stroke_opacity=0.7,
        )
        return VGroup(lbl, ic, tl)

    def _op_box(self, t_call, t_ret, op_text, ret_text, y, color, box_h=0.44, ret_color=None):
        """DDIA-style operation box spanning [t_call, t_ret] at row y."""
        x1 = _tx(t_call)
        x2 = _tx(t_ret)
        w = max(x2 - x1, 0.55)
        box = RoundedRectangle(
            corner_radius=0.07,
            width=w, height=box_h,
            fill_color=DARK_BG, fill_opacity=0.95,
            stroke_color=color, stroke_width=1.5,
        )
        box.move_to([(x1 + x2) / 2, y, 0])
        op_lbl = make_label(op_text, font_size=9, color=color)
        op_lbl.move_to(box.get_center())
        ret_lbl = make_label(f"=> {ret_text}", font_size=9, color=ret_color or GREY_A)
        ret_lbl.next_to(box, RIGHT, buff=0.1)
        return VGroup(box, op_lbl), ret_lbl

    def _db_marker(self, t, state_text, y_db, color=WHITE):
        """State-change tick on the database timeline."""
        x = _tx(t)
        tick = Line(
            [x, y_db + 0.18, 0], [x, y_db - 0.18, 0],
            stroke_color=color, stroke_width=1.6,
        )
        lbl = make_label(state_text, font_size=9, color=color)
        lbl.next_to(tick, DOWN, buff=0.08)
        return VGroup(tick, lbl)

    def _verdict_badge(self, text, color, width=7.0):
        box = RoundedRectangle(
            corner_radius=0.1, width=width, height=0.56,
            fill_color=DARK_BG, fill_opacity=0.95,
            stroke_color=color, stroke_width=1.8,
        )
        lbl = make_label(text, font_size=13, color=color)
        lbl.move_to(box.get_center())
        return VGroup(box, lbl)

    # ─── Sequence rows (sheet 4, scene_q5_monotonic) ──────────────────
    def _row(self, icon_path, label_text, y, color):
        ic = make_icon(icon_path, color=color, height=0.34)
        ic.move_to([_ICN_X, y, 0])
        lbl = make_label(label_text, font_size=10, color=color)
        lbl.next_to(ic, LEFT, buff=0.1)
        dash = DashedLine(
            [_ICN_X + 0.25, y, 0], [_TL_X1 + 0.3, y, 0],
            dash_length=0.15, color=color, stroke_width=0.8, stroke_opacity=0.4,
        )
        row = VGroup(lbl, ic, dash)
        row.icon = ic
        row.y = y
        return row

    def _arr(self, t0, y0, t1, y1, color):
        return Arrow(
            [_tx(t0), y0, 0], [_tx(t1), y1, 0],
            buff=0, stroke_width=1.7, color=color, tip_length=0.13,
        )

    def _msg(self, arr, text, offset, color, fs=10):
        lbl = make_label(text, font_size=fs, color=color)
        lbl.move_to(arr.get_center() + offset)
        return lbl

    def _lock_bar(self, t0, t1, y, color, height=0.2):
        bar = Rectangle(
            width=_tx(t1) - _tx(t0), height=height,
            fill_color=color, fill_opacity=0.28, stroke_width=0,
        )
        bar.move_to([(_tx(t0) + _tx(t1)) / 2, y, 0])
        return bar

    def _start_bars(self, t0, ys, colors, height=0.2):
        """Zero-width bars at t0. _grow_bars stretches them as time passes."""
        bars = VGroup(*[self._lock_bar(t0, t0 + 0.02, y, c, height=height) for y, c in zip(ys, colors)])
        bars.t0, bars.ys, bars.colors, bars.h = t0, ys, colors, height
        self.add(bars)
        return bars

    def _grow_bars(self, bars, t1):
        """Animations that stretch every bar in *bars* up to time t1."""
        return [
            Transform(b, self._lock_bar(bars.t0, t1, y, c, height=bars.h).set_style(
                fill_opacity=b.get_fill_opacity()))
            for b, y, c in zip(bars, bars.ys, bars.colors)
        ]

    def _grow_all(self, groups, t1):
        return [a for g in groups for a in self._grow_bars(g, t1)]

    def _prepare(self, t, yc, y, color, groups, vote_yes=True):
        """Coordinator asks one participant to prepare. It writes, takes locks, and votes.

        Matches Coordinator.collectVotes: participants are asked one at a time.
        """
        ask = self._arr(t, yc, t + 0.5, y, C_COORD)
        self.play(GrowArrow(ask), *self._grow_all(groups, t + 0.5), run_time=0.45)
        bar = self._start_bars(t + 0.5, [y], [color])
        groups.append(bar)
        reply = self._arr(t + 0.7, y, t + 1.2, yc, GREEN if vote_yes else RED)
        self.play(GrowArrow(reply), *self._grow_all(groups, t + 1.2), run_time=0.45)
        return VGroup(ask, reply), bar

    # ─── 2PC stage: coordinator + three participants + log ────────────
    def _twopc_stage(self):
        ys = [2.35, 1.45, 0.55, -0.35]
        rows = VGroup(
            self._row(ICON_STRUCTURE, "Coordinator", ys[0], C_COORD),
            self._row(ICON_DATABASE, "bookingdb", ys[1], C_BOOK),
            self._row(ICON_DATABASE, "paymentdb", ys[2], C_PAY),
            self._row(ICON_DATABASE, "accountingdb", ys[3], C_ACC),
        )
        time_lbl = make_label("time →", font_size=9, color=GREY_B)
        time_lbl.move_to([_TL_X1 + 0.2, ys[0] + 0.32, 0])
        log = self._log_panel([0, -2.35, 0], width=13.2, height=2.3, title="log")
        self.play(FadeIn(rows), FadeIn(time_lbl), FadeIn(log))
        return rows, ys, log

    def _fan(self, t0, y0, t1, ys_to, color, label=None, label_offset=UP * 0.2, extra=()):
        arrows = VGroup(*[self._arr(t0, y0, t1, y, color) for y in ys_to])
        anims = [GrowArrow(a) for a in arrows]
        self.play(*anims, *extra, run_time=0.6)
        if label:
            lbl = make_label(label, font_size=10, color=color)
            lbl.move_to([_tx(t0) + 0.35, y0, 0] + label_offset)
            lbl.align_to([_tx(t0) + 0.1, 0, 0], LEFT)
            self.play(FadeIn(lbl), run_time=0.3)
            return VGroup(arrows, lbl)
        return arrows

    # ─── Log panel ────────────────────────────────────────────────────
    def _log_panel(self, center, width, height, title="log", tag_w=1.25):
        box = RoundedRectangle(
            corner_radius=0.1, width=width, height=height,
            fill_color="#161B22", fill_opacity=0.95,
            stroke_color=GREY_B, stroke_width=1.0,
        )
        box.move_to(center)
        ttl = make_label(title, font_size=10, color=GREY_B)
        ttl.next_to(box.get_corner(UL), DR, buff=0.12)
        panel = VGroup(box, ttl)
        panel.box = box
        panel.ttl = ttl
        panel.lines = VGroup()
        panel.line_h = 0.32
        panel.tag_w = tag_w
        panel.max_lines = max(1, int((height - 0.45) / panel.line_h))
        return panel

    def _log(self, panel, tag, text, color, text_color=GREY_A, run_time=0.35):
        anims = []
        n = len(panel.lines)
        if n >= panel.max_lines:
            old = panel.lines[0]
            panel.lines.remove(old)
            anims += [FadeOut(old)] + [ln.animate.shift(UP * panel.line_h) for ln in panel.lines]
            n -= 1
        x_left = panel.box.get_left()[0] + 0.25
        top = panel.ttl.get_bottom()[1] - 0.08
        y = top - panel.line_h * (n + 0.5)
        tag_lbl = make_label(tag, font_size=10, color=color)
        msg_lbl = make_label(text, font_size=10, color=text_color)
        room = panel.box.get_right()[0] - 0.2 - (x_left + panel.tag_w)
        if msg_lbl.width > room:
            msg_lbl.scale_to_fit_width(room)
        tag_lbl.move_to([x_left + tag_lbl.width / 2, y, 0])
        msg_lbl.move_to([x_left + panel.tag_w + msg_lbl.width / 2, y, 0])
        line = VGroup(tag_lbl, msg_lbl)
        panel.lines.add(line)
        self.play(*anims, FadeIn(line, shift=UP * 0.05), run_time=run_time)
        return line

    def _mono_row(self, cells, widths, font_size):
        """One table row as a single monospaced Text: every column padded to a fixed
        width, so columns line up exactly and all cells share one baseline.
        cells: [(text, color), ...]. row.cells[i] is the glyph group of column i."""
        line, t2c, pos, spans = "", {}, 0, []
        for i, ((text, color), width) in enumerate(zip(cells, widths)):
            if not text:
                text, color = ".", DARK_BG_PAGE   # Pango drops leading spaces, so keep a hidden glyph
            t2c[f"[{pos}:{pos + len(text)}]"] = color
            spans.append((pos, pos + len(text)))
            cell = text.ljust(width) if i < len(cells) - 1 else text
            line += cell
            pos += len(cell)
        row = Text(line, font=FONT, font_size=font_size * 4, weight=BOLD, t2c=t2c).scale(0.25)
        glyph_index = [sum(1 for ch in line[:k] if not ch.isspace()) for k in range(len(line) + 1)]
        row.cells = [VGroup(*row[glyph_index[a]:glyph_index[b]]) for a, b in spans]
        return row

    def _table(self, headers, header_colors, rows, font_size=12, max_width=12.8, row_gap=0.34, gap=4):
        """Left-aligned monospaced table. Returns VGroup(header, divider, rows) like
        make_comparison_table, with header.cells for highlighting single columns."""
        cols = len(headers)
        widths = [max(len(headers[c]), *(len(r[c * 2]) for r in rows)) + gap for c in range(cols)]
        chars = sum(widths) - gap
        font_size = min(font_size, max_width / (chars * 0.00825))
        header = self._mono_row(list(zip(headers, header_colors)), widths, font_size)
        body = VGroup(*[
            self._mono_row([(r[c * 2], r[c * 2 + 1]) for c in range(cols)], widths, font_size) for r in rows
        ])
        body.arrange(DOWN, buff=row_gap, aligned_edge=LEFT)
        body.next_to(header, DOWN, buff=row_gap + 0.12, aligned_edge=LEFT)
        div = Line(header.get_corner(DOWN + LEFT) + DOWN * 0.12, header.get_corner(DOWN + LEFT) + DOWN * 0.12
                   + RIGHT * max(header.width, body.width), stroke_color=GREY_B, stroke_width=0.8)
        return VGroup(header, div, body)

    # ─── Mini tables ──────────────────────────────────────────────────
    def _mini_table(self, title, color, center, width=2.9, height=1.4):
        box = RoundedRectangle(
            corner_radius=0.08, width=width, height=height,
            fill_color="#161B22", fill_opacity=0.95,
            stroke_color=color, stroke_width=1.0,
        )
        box.move_to(center)
        ttl = make_label(title, font_size=11, color=color)
        ttl.next_to(box.get_corner(UL), DR, buff=0.1)
        div = Line(
            [box.get_left()[0] + 0.1, ttl.get_bottom()[1] - 0.08, 0],
            [box.get_right()[0] - 0.1, ttl.get_bottom()[1] - 0.08, 0],
            stroke_color=color, stroke_width=0.8, stroke_opacity=0.5,
        )
        table = VGroup(box, ttl, div)
        table.box = box
        table.div = div
        table.rows = []
        return table

    def _row_label(self, table, i, text, color):
        lbl = make_label(text, font_size=10, color=color)
        y = table.div.get_y() - 0.22 - 0.3 * i
        lbl.move_to([table.box.get_left()[0] + 0.18 + lbl.width / 2, y, 0])
        return lbl

    def _add_row(self, table, text, color):
        lbl = self._row_label(table, len(table.rows), text, color)
        table.rows.append(lbl)
        self.play(FadeIn(lbl, shift=RIGHT * 0.15), run_time=0.35)
        return lbl

    def _swap_row(self, table, i, text, color):
        new = self._row_label(table, i, text, color)
        return Transform(table.rows[i], new)

    # ─── Saga stage: orchestrator + services + tables + saga_log ──────
    def _saga_stage(self, with_log=True, greyed=None):
        orch = self._node(ICON_STRUCTURE, "Orchestrator (booking svc)", C_COORD)
        orch.move_to(_ORCH_POS)
        specs = [
            (ICON_SERVER, "Booking", C_BOOK, "bookings"),
            (ICON_SERVER, "Payment", C_PAY, "payments"),
            (ICON_SERVER, "Accounting", C_ACC, "ledger"),
        ]
        svcs, tables = [], []
        for (icon, name, color, tname), x in zip(specs, _COLS):
            c = GREY_B if greyed == name else color
            n = self._node(icon, name, c)
            n.move_to([x, _SVC_Y, 0])
            svcs.append(n)
            tables.append(self._mini_table(tname, c, [x, _TABLE_Y, 0]))
        stage = VGroup(orch, *svcs, *tables)
        log = None
        if with_log:
            log = self._log_panel([5.25, 0.25, 0], width=3.5, height=4.3,
                                  title="saga_log", tag_w=1.15)
            stage.add(log)
        self.play(FadeIn(stage, shift=UP * 0.1))
        return orch, svcs, tables, log

    def _call(self, orch, svc, color, dashed=False, shift=0.0):
        """Arrow from the orchestrator to a service icon.

        It leaves from just under the orchestrator's label and points at the
        centre of the service icon, stopping a fixed gap short of it, so straight
        and diagonal arrows land the same way. shift slides it sideways
        (perpendicular to its direction) so a call and its compensation sit side by side.
        """
        start = orch.get_bottom() + DOWN * 0.1
        target = svc[0].get_center()
        d = target - start
        unit = d / np.linalg.norm(d)
        end = target - unit * (svc[0].height / 2 + 0.18)
        if shift:
            normal = np.array([unit[1], -unit[0], 0.0])
            start, end = start + normal * shift, end + normal * shift
        if dashed:
            a = self._dashed_arrow(start, end, color)
            self.play(Create(a), run_time=0.5)
        else:
            a = Arrow(start, end, buff=0, stroke_width=1.8, color=color, tip_length=0.14)
            self.play(GrowArrow(a), run_time=0.45)
        return a

    def _mark(self, svc, ok=True):
        icon = make_icon(ICON_CHECK if ok else ICON_DANGER, color=GREEN if ok else RED, height=0.26)
        icon.next_to(svc, RIGHT, buff=0.12)
        self.play(FadeIn(icon, scale=0.6), run_time=0.3)
        return icon

    # ═════════════════════════════════════════════════════════════════
    # Part 0: Setup
    # ═════════════════════════════════════════════════════════════════

    # ─── Scene 0: Title ───────────────────────────────────────────────
    def scene_title(self):
        icons = VGroup(
            make_icon(ICON_DATABASE, color=C_BOOK, height=0.7),
            make_icon(ICON_DATABASE, color=C_PAY, height=0.7),
            make_icon(ICON_DATABASE, color=C_ACC, height=0.7),
        ).arrange(RIGHT, buff=0.5)
        title = make_label("Distributed Transactions", font_size=38, color=TEAL)
        sub = make_label("One booking, three services, no shared commit.", font_size=17, color=GREY_A)
        cap = make_label("DDIA ch. 7 · 8 · 9", font_size=12, color=GREY_B)
        VGroup(icons, title, sub, cap).arrange(DOWN, buff=0.38)
        self.play(AnimationGroup(*[FadeIn(i, shift=DOWN * 0.3) for i in icons], lag_ratio=0.15))
        self.play(AddTextLetterByLetter(title, time_per_char=0.04))
        self.play(FadeIn(sub, shift=UP * 0.2))
        self.play(FadeIn(cap))
        self._end_scene(3)

    # ─── Scene 1: The story ───────────────────────────────────────────
    def scene_story(self):
        self._header("The Story", color=TEAL)

        user = self._node(ICON_USER, "Alice", GREY_A, icon_h=0.55)
        user.move_to([-5.6, 0.6, 0])
        ask = self._chip("Book room 101 for tonight", GREY_A, font_size=10)
        ask.next_to(user, UP, buff=0.25)
        self.play(FadeIn(user, shift=RIGHT * 0.2))
        self.play(FadeIn(ask, shift=UP * 0.1))
        self._next_slide(phase=True)

        xs = [-1.9, 1.4, 4.7]
        specs = [
            ("Booking", C_BOOK, "reserve room 101"),
            ("Payment", C_PAY, "take $120"),
            ("Accounting", C_ACC, "record revenue"),
        ]
        svcs, dbs, jobs = VGroup(), VGroup(), VGroup()
        for (name, color, job), x in zip(specs, xs):
            s = self._node(ICON_SERVER, name, color, icon_h=0.55, font_size=13)
            s.move_to([x, 0.6, 0])
            d = self._node(ICON_DATABASE, f"{name.lower()}db", color, icon_h=0.4, font_size=9)
            d.move_to([x, -0.9, 0])
            j = make_label(job, font_size=11, color=GREY_A)
            j.move_to([x, -1.85, 0])
            svcs.add(s)
            dbs.add(d)
            jobs.add(j)

        entry = Arrow(user.get_right(), svcs[0].get_left(), buff=0.2, stroke_width=2, color=GREY_A, tip_length=0.15)
        self.play(GrowArrow(entry))
        for s, d in zip(svcs, dbs):
            self.play(FadeIn(s, shift=UP * 0.1), FadeIn(d, shift=UP * 0.1), run_time=0.45)
        links = VGroup(*[
            Line(s.get_bottom(), d.get_top(), stroke_color=GREY_B, stroke_width=1.2, buff=0.08)
            for s, d in zip(svcs, dbs)
        ])
        self.play(Create(links), run_time=0.4)
        for j in jobs:
            self.play(FadeIn(j, shift=UP * 0.1), run_time=0.35)
        self._next_slide(phase=True)

        group = VGroup(svcs, dbs, jobs)
        frame = RoundedRectangle(
            corner_radius=0.2, width=group.width + 0.6, height=group.height + 0.5,
            stroke_color=TEAL, stroke_width=1.8,
        )
        frame.move_to(group.get_center())
        frame = DashedVMobject(frame, num_dashes=70)
        rule = make_label("All three, or none.", font_size=20, color=TEAL)
        rule.next_to(frame, DOWN, buff=0.3)
        self.play(Create(frame))
        self.play(AddTextLetterByLetter(rule, time_per_char=0.04))
        note = make_label("Each service owns its own database. There is no single COMMIT.",
                          font_size=11, color=GREY_B)
        note.next_to(rule, DOWN, buff=0.2)
        self.play(FadeIn(note))
        self._end_scene()

    def _schema_card(self, db_name, color, tables, x, top, height, width=4.2, row_h=0.3):
        """A card per database: table names, one row per column, tags right-aligned.

        tables: [(table_name, [(column, tag, tag_color, dim, enum), ...]), ...]
        Returns (card, refs) where refs maps a column name to its rows.
        """
        left = x - width / 2 + 0.3
        right = x + width / 2 - 0.3
        box = RoundedRectangle(
            corner_radius=0.12, width=width, height=height,
            fill_color="#161B22", fill_opacity=0.95,
            stroke_color=color, stroke_width=1.4,
        )
        box.move_to([x, top - height / 2, 0])
        title = make_label(db_name, font_size=14, color=color)
        title.move_to([x, top - 0.35, 0])
        div = Line([left, top - 0.65, 0], [right, top - 0.65, 0],
                   stroke_color=color, stroke_width=0.8, stroke_opacity=0.5)
        body = VGroup()
        refs = {}
        y = top - 0.65
        for t_i, (tname, cols) in enumerate(tables):
            y -= 0.42 if t_i == 0 else 0.45
            tl = make_label(tname, font_size=12, color=WHITE)
            tl.move_to([left + tl.width / 2, y, 0])
            body.add(tl)
            for col, tag, tag_color, dim, enum in cols:
                y -= row_h
                name = make_label(col, font_size=11, color=GREY_B if dim else GREY_A)
                name.move_to([left + 0.3 + name.width / 2, y, 0])
                row = VGroup(name)
                if tag:
                    tg = make_label(tag, font_size=10, color=GREY_B if dim else tag_color)
                    tg.move_to([right - tg.width / 2, y, 0])
                    row.add(tg)
                body.add(row)
                refs.setdefault(col, []).append(row)
                if enum:
                    y -= 0.25
                    en = make_label(enum, font_size=9, color=GREY_B)
                    en.move_to([left + 0.6 + en.width / 2, y, 0])
                    body.add(en)
                    row.add(en)
        return VGroup(box, title, div, body), refs

    # ─── Scene 2: Schema ──────────────────────────────────────────────
    def scene_schema(self):
        self._header("Schema", color=TEAL)
        where = make_label("MySQL · one server · three databases (demo/sql/00-schema.sql)",
                           font_size=10, color=GREY_B)
        where.move_to([0, 3.0, 0])
        self.play(FadeIn(where))
        specs = [
            ("bookingdb", C_BOOK, [
                ("rooms", [
                    ("room_id", "PK", C_BOOK, False, None),
                    ("name", "", None, False, None),
                    ("fence_token", "", GREY_B, True, None),
                ]),
                ("bookings", [
                    ("id", "PK", C_BOOK, False, None),
                    ("room_id, user_id", "", None, False, None),
                    ("starts_at, ends_at", "", None, False, None),
                    ("status", "", None, False, "PENDING · CONFIRMED · CANCELLED"),
                    ("transaction_id", "bk- / sg-", C_BOOK, False, None),
                    ("fence_token", "", GREY_B, True, None),
                ]),
            ]),
            ("paymentdb", C_PAY, [
                ("wallets", [
                    ("user_id", "PK", C_PAY, False, None),
                    ("balance", "CHECK >= 0", C_PAY, False, None),
                ]),
                ("payments", [
                    ("id", "PK", C_PAY, False, None),
                    ("booking_id", "UNIQUE", C_PAY, False, None),
                    ("transaction_id", "", None, False, None),
                    ("user_id, amount", "", None, False, None),
                    ("status", "", None, False, "CHARGED · REFUNDED"),
                ]),
            ]),
            ("accountingdb", C_ACC, [
                ("ledger", [
                    ("id", "PK", C_ACC, False, None),
                    ("booking_id", "", None, False, None),
                    ("transaction_id", "", None, False, None),
                    ("kind", "", None, False, "REVENUE · REVERSAL"),
                    ("amount", "", None, False, None),
                    ("(booking_id, kind)", "UNIQUE", C_ACC, False, None),
                ]),
            ]),
        ]
        xs = [-4.55, 0.0, 4.55]
        top, height = 2.65, 5.2
        cards, refs = [], []
        for (db, color, tables), x in zip(specs, xs):
            card, r = self._schema_card(db, color, tables, x, top, height)
            cards.append(card)
            refs.append(r)
        support = make_label("+ room_slot_lock · lock_lease\n+ tx_log · saga_log", font_size=9, color=GREY_B)
        support.move_to([xs[0], top - height + 0.38, 0])
        cards[0].add(support)
        append_only = make_label("append only, never deletes", font_size=10, color=GREY_B)
        append_only.move_to([xs[2], top - height + 0.3, 0])
        cards[2].add(append_only)
        for card in cards:
            self.play(FadeIn(card, shift=UP * 0.15), run_time=0.5)
        self._next_slide(phase=True)

        y0 = top - height - 0.4
        notes = [
            (1, "balance", "Payment can say no", C_PAY, [xs[1], y0, 0]),
            (1, "booking_id", "a retry is a no-op", C_PAY, [xs[1], y0 - 0.5, 0]),
            (2, None, "undo = add a REVERSAL", C_ACC, [xs[2], y0, 0]),
            (0, "transaction_id", "every row carries the global tx id", C_BOOK, [xs[0], y0, 0]),
        ]
        for idx, key, text, color, pos in notes:
            chip = self._chip(text, color, font_size=10).move_to(pos)
            target = VGroup(*refs[idx][key]) if key else append_only
            self.play(Indicate(target, color=color, scale_factor=1.08), FadeIn(chip, shift=UP * 0.1))
            self.wait(0.4)

        later = self._chip("fence_token + support tables: later", GREY_B, font_size=10)
        later.move_to([xs[0], y0 - 0.5, 0])
        self.play(Indicate(VGroup(*refs[0]["fence_token"]), color=GREY_A), Indicate(support, color=GREY_A),
                  FadeIn(later, shift=UP * 0.1))
        self._end_scene()

    # ─── Scene 2b: Prerequisites ──────────────────────────────────────
    def scene_prerequisites(self):
        self._header("Before We Start: ACID", color=TEAL)
        items = [
            (ICON_CHECK, TEAL, "Atomicity",
             "all the writes happen, or none of them. This is what we fight for across services."),
            (ICON_SHIELD, GREEN, "Consistency",
             "the rules hold before and after, like CHECK (balance >= 0)"),
            (ICON_LOCK, YELLOW, "Isolation",
             "two transactions running at once don't see each other's half-done work"),
            (ICON_DATABASE, BLUE, "Durability",
             "once COMMIT returns, the data survives a crash (the write-ahead log)"),
        ]
        cards = VGroup(*[self._icon_row_card(i, c, t, d) for i, c, t, d in items])
        cards.arrange(DOWN, buff=0.22, aligned_edge=LEFT).scale(1.1).move_to([0, 0.1, 0])
        for card in cards:
            self.play(FadeIn(card, shift=RIGHT * 0.12), run_time=0.45)
            self.wait(0.35)
        self._next_slide(phase=True)
        roadmap = VGroup(
            self._chip("Isolation on one database", YELLOW, font_size=11),
            self._chip("Atomicity across three databases", TEAL, font_size=11),
            self._chip("Locks across machines", C_LOCK, font_size=11),
        ).arrange(RIGHT, buff=0.3).move_to([0, -3.0, 0])
        self.play(AnimationGroup(*[FadeIn(r, shift=UP * 0.1) for r in roadmap], lag_ratio=0.25))
        self._end_scene()

    # ═════════════════════════════════════════════════════════════════
    # Part 1: One database first (p. 249–260)
    # ═════════════════════════════════════════════════════════════════

    # ─── Scene 3: Write skew ──────────────────────────────────────────
    def scene_write_skew(self):
        self._header("Write Skew: Double Booking", color=RED, demo="01-write-skew.sh")
        sub = make_label("InnoDB REPEATABLE READ (a snapshot for plain SELECTs) · room 101 · 12:00–13:00",
                         font_size=10, color=GREY_B)
        sub.move_to([0, 2.75, 0])

        Y1, Y2, YDB = 1.5, 0.1, -1.35
        r1 = self._client_row("A", "T1 Alice", Y1, C_BOOK)
        r2 = self._client_row("B", "T2 Bob", Y2, C_PAY)
        db = self._db_row("bookings", YDB)
        time_lbl = make_label("time →", font_size=9, color=GREY_B)
        time_lbl.move_to([_TL_X1 + 0.2, Y1 + 0.4, 0])
        self.play(FadeIn(sub), FadeIn(r1), FadeIn(r2), FadeIn(db), FadeIn(time_lbl))
        self._next_slide(phase=True)

        steps = [
            (0.1, 0.9, "BEGIN", None, Y1, C_BOOK),
            (0.5, 1.3, "BEGIN", None, Y2, C_PAY),
            (1.2, 2.9, "SELECT count(*)", "0", Y1, C_BOOK),
            (2.0, 3.7, "SELECT count(*)", "0", Y2, C_PAY),
            (4.1, 5.8, "INSERT · COMMIT", "ok", Y1, C_BOOK),
            (6.1, 7.8, "INSERT · COMMIT", "ok", Y2, C_PAY),
        ]
        markers = []
        for i, (t0, t1, op, ret, y, color) in enumerate(steps):
            box, ret_lbl = self._op_box(t0, t1, op, ret or "", y, color)
            self.play(FadeIn(box, shift=RIGHT * 0.1), run_time=0.4)
            if ret:
                self.play(FadeIn(ret_lbl), run_time=0.25)
            if i == 4:
                m = self._db_marker(t1, "rows: 1 (Alice)", YDB, color=C_BOOK)
                self.play(FadeIn(m))
                markers.append(m)
            if i == 5:
                m = self._db_marker(t1, "rows: 2", YDB, color=RED)
                self.play(FadeIn(m))
                markers.append(m)
            if i in (1, 3):
                self._next_slide(phase=True)

        badge = self._verdict_badge("Room 101 booked twice  ✗", RED, width=6.0)
        badge.move_to([0, -2.45, 0])
        self.play(*[Indicate(m, color=RED) for m in markers], FadeIn(badge, shift=UP * 0.1))
        cap = self._caption("Each transaction read, decided and wrote correctly. Together they broke the rule.",
                            y=-3.25, font_size=10)
        self.play(FadeIn(cap))
        self._next_slide(phase=True)

        self.play(FadeOut(badge), FadeOut(cap))
        flow = [
            self._flow_node("1  SELECT checks\na condition", TEAL, width=3.0, height=0.8),
            self._flow_node("2  app decides\nfrom the result", TEAL, width=3.0, height=0.8),
            self._flow_node("3  INSERT changes\nstep 1's answer", RED, width=3.0, height=0.8),
        ]
        VGroup(*flow).arrange(RIGHT, buff=0.6).move_to([0, -2.75, 0])
        arrows = [self._flow_arrow(flow[0], flow[1]), self._flow_arrow(flow[1], flow[2])]
        self.play(FadeIn(flow[0]))
        self.play(GrowArrow(arrows[0]), FadeIn(flow[1]))
        self.play(GrowArrow(arrows[1]), FadeIn(flow[2]))
        self._end_scene()

    # ─── Scene 4: Phantom ─────────────────────────────────────────────
    def scene_phantom(self):
        self._header("Why FOR UPDATE Doesn't Help", color=RED)
        q = make_code_text(
            "SELECT COUNT(*) FROM bookings\n"
            " WHERE room_id = 101\n"
            "   AND status <> 'CANCELLED'\n"
            "   AND starts_at < '13:00'\n"
            "   AND ends_at   > '12:00'\n"
            "   FOR UPDATE;",
            font_size=12, language="sql", force_code_object=True, glow=False,
        )
        q.move_to([-3.2, 0.9, 0])
        self.play(FadeIn(q, shift=UP * 0.1))

        result = self._mini_table("result: 0 rows", GREY_B, [3.2, 0.2, 0], width=3.4, height=1.6)
        empty = make_label("(empty)", font_size=10, color=GREY_B)
        empty.move_to(result.box.get_center() + DOWN * 0.15)
        arrow = Arrow(q.get_right(), result.get_left(), buff=0.25, stroke_width=2, color=GREY_A, tip_length=0.15)
        self.play(GrowArrow(arrow), FadeIn(result), FadeIn(empty))
        self._next_slide(phase=True)

        lock = make_icon(ICON_LOCK, color=C_LOCK, height=0.55)
        lock.move_to([3.2, 2.5, 0])
        self.play(FadeIn(lock, shift=DOWN * 0.2))
        self.play(lock.animate.move_to(result.box.get_center() + DOWN * 0.15), run_time=0.8)
        self.play(Wiggle(lock))
        nothing = make_label("nothing to attach to", font_size=11, color=RED)
        nothing.next_to(result, DOWN, buff=0.2)
        self.play(FadeOut(lock, shift=DOWN * 0.2), FadeIn(nothing))
        cap = self._caption("You can't lock a row that doesn't exist yet. That row is a phantom.",
                            color=GREY_A, y=-2.3, font_size=13)
        self.play(FadeIn(cap, shift=UP * 0.1))
        inno = make_label("MySQL is the exception: at REPEATABLE READ, InnoDB's FOR UPDATE also locks the index gap\n"
                          "(next-key lock). That is the same trick SERIALIZABLE uses in 03-serializable.sh.",
                          font_size=10, color=YELLOW)
        inno.move_to([0, -3.15, 0])
        self.play(FadeIn(inno))
        self._next_slide(phase=True)

        self.play(FadeOut(q), FadeOut(arrow), FadeOut(result), FadeOut(empty), FadeOut(nothing), FadeOut(cap),
                  FadeOut(inno))
        table = self._table(
            ["Fix", "Idea", "Note"],
            [TEAL, GREY_A, GREY_A],
            [
                ("Materialize conflict", GREY_A, "lock room_slot_lock rows first", GREY_A,
                 "02-materialized.sh, last resort", GREY_B),
                ("SERIALIZABLE", GREEN, "InnoDB locks the gap, one aborts", GREEN,
                 "03-serializable.sh", GREEN),
                ("Exclusion constraint", GREY_A, "DB rejects overlapping ranges", GREY_A,
                 "Postgres only, MySQL has none", GREY_B),
            ],
            font_size=14,
        )
        table.move_to([0, 0.3, 0])
        self.play(FadeIn(table[0]), Create(table[1]))
        for row in table[2]:
            self.play(FadeIn(row, shift=UP * 0.1), run_time=0.45)
            self.wait(0.3)
        self._play_glow(table[2][1], GREEN, pad=0.3)
        self._end_scene()

    # ─── Scene 4b: Materializing conflicts ────────────────────────────
    def scene_materialize_conflicts(self):
        self._header("Materializing Conflicts", color=YELLOW, demo="02-materialized.sh")
        sub = make_label("No row to lock? Create rows whose only job is to be locked.", font_size=12, color=GREY_A)
        sub.move_to([0, 2.8, 0])
        self.play(FadeIn(sub))

        # room_slots grid: room 101, 11:00 → 14:00 in 15-minute rows
        times = [f"{11 + i // 4}:{(i % 4) * 15:02d}" for i in range(12)]
        cw, ch, gx0, gy = 0.9, 0.62, -5.4, 1.15
        cells = VGroup()
        for i in range(12):
            r = Rectangle(width=cw * 0.94, height=ch, stroke_color=GREY_B, stroke_width=1.1,
                          fill_color="#161B22", fill_opacity=1.0)
            r.move_to([gx0 + i * cw + cw / 2, gy, 0])
            cells.add(r)
        labels = VGroup(*[
            make_label(t, font_size=9, color=GREY_B).next_to(c, DOWN, buff=0.1)
            for t, c in zip(times, cells)
        ])
        name = make_label("room_slot_lock · room 101", font_size=11, color=C_BOOK)
        name.next_to(cells, UP, buff=0.2).align_to(cells, LEFT)
        self.play(FadeIn(cells, lag_ratio=0.05), FadeIn(labels), FadeIn(name))
        note = make_label("one row per room per 15 minutes, seeded for today and tomorrow (192 rows). it stores nothing.",
                          font_size=12, color=GREY_B)
        note.move_to([0, -0.15, 0])
        self.play(FadeIn(note))
        self._next_slide(phase=True)

        # T1 locks 12:00–13:00
        t1_sql = self._chip("T1:  SELECT slot_start FROM room_slot_lock\n"
                            "     WHERE room_id = 101 AND slot_start >= '12:00' AND slot_start < '13:00'\n"
                            "     ORDER BY slot_start FOR UPDATE",
                            C_BOOK, font_size=11)
        t1_sql.move_to([0, -0.95, 0])
        self.play(FadeIn(t1_sql, shift=UP * 0.1))
        t1_idx = range(4, 8)
        t1_locks = VGroup(*[make_icon(ICON_LOCK, color=C_BOOK, height=0.24).move_to(cells[i]) for i in t1_idx])
        self.play(*[cells[i].animate.set_fill(C_BOOK, opacity=0.3).set_stroke(C_BOOK) for i in t1_idx],
                  FadeIn(t1_locks, scale=0.6))
        self._next_slide(phase=True)

        # T2 is the same request, sent at the same moment (the script fires both at once)
        t2_sql = self._chip("T2:  the same request, 12:00 → 13:00", C_PAY, font_size=11)
        t2_sql.move_to([0, -1.75, 0])
        self.play(FadeIn(t2_sql, shift=UP * 0.1))
        t2_idx = range(4, 8)
        t2_frame = Rectangle(width=cw * 4 + 0.08, height=ch + 0.18, stroke_color=C_PAY, stroke_width=2)
        t2_frame.move_to(VGroup(*[cells[i] for i in t2_idx]).get_center())
        self.play(Create(t2_frame))
        self.play(Indicate(cells[4], color=RED, scale_factor=1.1))
        wait = self._chip("T2 waits on the 12:00 row (ORDER BY keeps everyone in the same order)", RED)
        wait.move_to([0, 2.2, 0])
        self.play(FadeIn(wait))
        self._next_slide(phase=True)

        # T1 commits, T2 wakes up and re-checks
        steps = VGroup(
            make_label("1. T1 checks bookings (0 overlaps), INSERTs, COMMIT, locks released", font_size=10, color=C_BOOK),
            make_label("2. T2 gets the slot rows, checks bookings: T1's row is there", font_size=10, color=C_PAY),
            make_label("3. T2 answers \"room already booked\". One row in bookings.", font_size=10, color=GREEN),
        ).arrange(DOWN, buff=0.16, aligned_edge=LEFT).move_to([0, -2.65, 0])
        self.play(FadeIn(steps[0]))
        self.play(FadeOut(t1_locks), *[cells[i].animate.set_fill("#161B22", opacity=1.0).set_stroke(GREY_B)
                                       for i in t1_idx], FadeOut(wait))
        t2_locks = VGroup(*[make_icon(ICON_LOCK, color=C_PAY, height=0.24).move_to(cells[i]) for i in t2_idx])
        self.play(FadeIn(steps[1]), FadeIn(t2_locks, scale=0.6),
                  *[cells[i].animate.set_fill(C_PAY, opacity=0.3).set_stroke(C_PAY) for i in t2_idx])
        self.play(FadeIn(steps[2]))
        rc = make_label("InnoDB takes T2's snapshot at its first plain SELECT, after the wait, so the check sees T1's row",
                        font_size=9, color=YELLOW)
        rc.next_to(steps, DOWN, buff=0.2)
        self.play(FadeIn(rc))
        self._next_slide(phase=True)
        self._clear()

        # the trade-offs
        self._header("Materializing Conflicts: The Catch", color=YELLOW)
        cards = VGroup(
            self._card("Pick the lock size",
                       "One row per room is simple, but every booking of room 101 waits, even for another day.\n"
                       "The demo uses 15-minute slots: precise, but 96 rows per room per day to pre-create.",
                       C_BOOK, width=11.5),
            self._card("Concurrency leaks into the data model",
                       "room_slot_lock holds no business data. It exists only because the database couldn't\n"
                       "lock a range for us. Every new kind of booking needs its own lock table.",
                       C_PAY, width=11.5),
            self._card("Hard to get right, so it's a last resort",
                       "Forget one code path that skips the slot lock and the double booking is back.\n"
                       "Prefer SERIALIZABLE (03-serializable.sh), or in Postgres an exclusion constraint.",
                       RED, width=11.5),
        ).arrange(DOWN, buff=0.3).move_to([0, -0.2, 0])
        for c in cards:
            self.play(FadeIn(c, shift=UP * 0.1), run_time=0.5)
            self.wait(0.4)
        self._end_scene()

    # ─── Scene 5: 2PL is not 2PC ──────────────────────────────────────
    def scene_two_phase_locking(self):
        """One slide. 2PL is DDIA p.257 (isolation on one database). We only need two
        facts from it: it is not 2PC, and its locks are held until commit."""
        self._header("2PL ≠ 2PC", color=YELLOW)
        cards = VGroup(
            self._card("2PL: two-phase locking  (DDIA p.257)",
                       "Isolation on one database. Take locks while the transaction runs,\n"
                       "release them all at COMMIT. SERIALIZABLE in InnoDB works this way.",
                       YELLOW, width=10.5),
            self._card("2PC: two-phase commit  (DDIA p.354)",
                       "Atomic commit across many databases. Prepare everywhere,\n"
                       "then commit everywhere. That is the rest of this deck.",
                       TEAL, width=10.5),
        ).arrange(DOWN, buff=0.35).move_to([0, 0.6, 0])
        for c in cards:
            self.play(FadeIn(c, shift=UP * 0.1), run_time=0.5)
            self.wait(0.4)
        line = make_label("Locks are held until commit.", font_size=18, color=YELLOW)
        line.move_to([0, -2.1, 0])
        self.play(AddTextLetterByLetter(line, time_per_char=0.04))
        self.play(Circumscribe(line, color=YELLOW))
        hint = make_label("Remember this one. It comes back when the 2PC coordinator crashes.",
                          font_size=11, color=GREY_B)
        hint.next_to(line, DOWN, buff=0.3)
        self.play(FadeIn(hint))
        self._end_scene()

    # ═════════════════════════════════════════════════════════════════
    # Part 2: Two-phase commit (p. 353–364)
    # ═════════════════════════════════════════════════════════════════

    # ─── Scene 5b: The easy case, one database ────────────────────────
    def _wal_strip(self, records, x0, y, cell_w=1.55, h=0.5):
        """A row of write-ahead log records. records: [(text, color), ...]"""
        strip = VGroup()
        for i, (text, color) in enumerate(records):
            box = RoundedRectangle(corner_radius=0.06, width=cell_w - 0.1, height=h,
                                   fill_color="#161B22", fill_opacity=1.0,
                                   stroke_color=color, stroke_width=1.3)
            box.move_to([x0 + i * cell_w + cell_w / 2, y, 0])
            lbl = make_label(text, font_size=10, color=color).move_to(box)
            strip.add(VGroup(box, lbl))
        return strip

    def scene_single_db_baseline(self):
        self._header("The Easy Case: One Database", color=GREEN)
        sub = make_label("Same booking, but all four tables live in one database.", font_size=12, color=GREY_A)
        sub.move_to([0, 2.8, 0])
        self.play(FadeIn(sub))

        sql = self._code_box([
            "BEGIN;",
            "INSERT INTO bookings  ... 'CONFIRMED';",
            "UPDATE wallets SET balance = balance - 120",
            "  WHERE user_id = 1;",
            "INSERT INTO payments  ... 'CHARGED';",
            "INSERT INTO ledger    ... 'REVENUE';",
            "COMMIT;",
        ], "one transaction", GREEN, width=7.2, font_size=12, language="sql")
        sql.move_to([-2.7, 0.2, 0])
        db = self._node(ICON_DATABASE, "hotel_db", GREEN, icon_h=0.7, font_size=13)
        db.move_to([4.2, 1.0, 0])
        tables = VGroup(*[self._chip(t, c, font_size=10) for t, c in
                          [("bookings", C_BOOK), ("wallets", C_PAY), ("payments", C_PAY), ("ledger", C_ACC)]])
        tables.arrange(DOWN, buff=0.14).next_to(db, DOWN, buff=0.3)
        self.play(FadeIn(sql, shift=UP * 0.1))
        self.play(FadeIn(db), FadeIn(tables, lag_ratio=0.15))
        arrow = Arrow(sql.get_right(), tables.get_left(), buff=0.2, stroke_width=2, color=GREEN, tip_length=0.15)
        self.play(GrowArrow(arrow))
        cap = self._caption("If the CHECK on balance fails, the whole thing rolls back. Nobody sees half a booking.",
                            y=-3.2, font_size=11)
        self.play(FadeIn(cap))
        self._next_slide(phase=True)
        self.play(FadeOut(VGroup(sql, db, tables, arrow, cap)))

        # how one database makes it atomic: the write-ahead log
        wal_lbl = make_label("write-ahead log, on one disk", font_size=11, color=GREY_A)
        wal_lbl.move_to([-6.2, 1.75, 0], aligned_edge=LEFT)
        recs = [("booking", C_BOOK), ("wallet -120", C_PAY), ("payment", C_PAY), ("ledger", C_ACC), ("COMMIT", GREEN)]
        strip = self._wal_strip(recs, -6.2, 1.1)
        self.play(FadeIn(wal_lbl))
        for r in strip:
            self.play(FadeIn(r, shift=LEFT * 0.2), run_time=0.3)
        self._play_glow(strip[-1], YELLOW, pad=0.2)
        cp = make_label("commit point: the moment the disk finishes writing this one record",
                        font_size=10, color=YELLOW)
        cp.next_to(strip, DOWN, buff=0.25).align_to(strip, LEFT)
        self.play(FadeIn(cp))
        self._next_slide(phase=True)

        # crash before vs after the commit record
        c1_lbl = make_label("crash before COMMIT is on disk", font_size=11, color=RED)
        c1_lbl.move_to([-6.2, -0.35, 0], aligned_edge=LEFT)
        c1 = self._wal_strip(recs[:4], -6.2, -0.95)
        b1 = make_icon(ICON_BOMB, color=RED, height=0.42).move_to([-6.2 + 4 * 1.55 + 0.75, -0.95, 0])
        r1 = self._chip("restart: no commit record, undo all 4", RED, font_size=10)
        r1.next_to(b1, RIGHT, buff=0.3)
        self.play(FadeIn(c1_lbl), FadeIn(c1))
        self.play(FadeIn(b1, scale=1.4))
        self.play(FadeIn(r1), *[r.animate.set_opacity(0.3) for r in c1])

        c2_lbl = make_label("crash after COMMIT is on disk", font_size=11, color=GREEN)
        c2_lbl.move_to([-6.2, -1.85, 0], aligned_edge=LEFT)
        c2 = self._wal_strip(recs, -6.2, -2.45)
        b2 = make_icon(ICON_BOMB, color=RED, height=0.42).move_to([-6.2 + 5 * 1.55 + 0.4, -2.45, 0])
        r2 = self._chip("restart: commit record found, keep all 4", GREEN, font_size=10)
        r2.next_to(b2, RIGHT, buff=0.3)
        self.play(FadeIn(c2_lbl), FadeIn(c2))
        self.play(FadeIn(b2, scale=1.4))
        self.play(FadeIn(r2))
        cap = self._caption("One disk, one commit record, one decision.", color=GREEN, y=-3.35, font_size=14)
        self.play(FadeIn(cap))
        self._next_slide(phase=True)
        self._clear()

        # now split it
        self._header("Now Split It Into Three Services", color=RED)
        one = self._node(ICON_DATABASE, "hotel_db", GREEN, icon_h=0.8, font_size=13).move_to([0, 1.2, 0])
        self.play(FadeIn(one))
        xs = [-4.4, 0.0, 4.4]
        specs = [("bookingdb", C_BOOK, "booking"), ("paymentdb", C_PAY, "wallet · payment"),
                 ("accountingdb", C_ACC, "ledger")]
        parts, logs = VGroup(), VGroup()
        for (name, color, rec), x in zip(specs, xs):
            n = self._node(ICON_DATABASE, name, color, icon_h=0.6, font_size=12).move_to([x, 1.2, 0])
            parts.add(n)
            strip = self._wal_strip([(rec, color), ("COMMIT ?", YELLOW)], x - 1.9, -0.1, cell_w=1.9)
            logs.add(strip)
        self.play(*[Transform(one.copy(), p) for p in parts], FadeOut(one), run_time=1.0)
        self.add(parts)
        self.play(FadeIn(logs, lag_ratio=0.2))
        q = self._verdict_badge("Three disks, three commit records. Which one is the commit point?", YELLOW, width=11.0)
        q.move_to([0, -1.5, 0])
        self.play(FadeIn(q, shift=UP * 0.1))
        why = VGroup(
            make_label("each database can only commit its own part", font_size=11, color=GREY_A),
            make_label("one can say yes while another says no, or crashes", font_size=11, color=GREY_A),
            make_label("and nobody is in charge of the final answer", font_size=11, color=RED),
        ).arrange(DOWN, buff=0.14).move_to([0, -2.75, 0])
        self.play(AnimationGroup(*[FadeIn(w, shift=UP * 0.08) for w in why], lag_ratio=0.35))
        self._end_scene()

    # ─── Scene 6: Why not one phase ───────────────────────────────────
    def scene_why_not_one_phase(self):
        self._header("Why Not Just Send COMMIT?", color=TEAL)
        coord = self._node(ICON_STRUCTURE, "Coordinator", C_COORD, icon_h=0.5, font_size=12)
        coord.move_to([0, 2.0, 0])
        xs = [-4.0, 0.0, 4.0]
        specs = [("bookingdb", C_BOOK), ("paymentdb", C_PAY), ("accountingdb", C_ACC)]
        dbs = []
        for (name, color), x in zip(specs, xs):
            d = self._node(ICON_DATABASE, name, color, icon_h=0.5, font_size=11)
            d.move_to([x, -0.3, 0])
            dbs.append(d)
        self.play(FadeIn(coord), *[FadeIn(d) for d in dbs])

        arrows = [Arrow(coord.get_bottom(), d.get_top(), buff=0.15, stroke_width=2, color=C_COORD, tip_length=0.14)
                  for d in dbs]
        commit = make_label("COMMIT", font_size=10, color=C_COORD).next_to(coord, RIGHT, buff=0.3)
        self.play(*[GrowArrow(a) for a in arrows], FadeIn(commit))
        self._next_slide(phase=True)

        ok1 = make_icon(ICON_CHECK, color=GREEN, height=0.3).next_to(dbs[0], RIGHT, buff=0.15)
        ok3 = make_icon(ICON_CHECK, color=GREEN, height=0.3).next_to(dbs[2], RIGHT, buff=0.15)
        bad = make_icon(ICON_DANGER, color=RED, height=0.3).next_to(dbs[1], RIGHT, buff=0.15)
        why = make_label("CHECK violation:\nbalance < 0", font_size=9, color=RED).next_to(dbs[1], DOWN, buff=0.2)
        self.play(FadeIn(ok1), FadeIn(ok3))
        self.play(FadeIn(bad), FadeIn(why), dbs[1].animate.set_color(RED))
        strip = self._verdict_badge("room reserved · revenue recorded · no money taken  ✗", RED, width=9.0)
        strip.move_to([0, -2.0, 0])
        self.play(FadeIn(strip, shift=UP * 0.1))
        self._next_slide(phase=True)

        cap = self._caption("Once committed, a node can't take it back. Only commit once you're sure everyone will.",
                            y=-2.75, font_size=11)
        self.play(FadeIn(cap))
        chips = VGroup(
            self._chip("constraint violation on one node", RED),
            self._chip("commit request lost in the network", RED),
            self._chip("node crashes before its commit record", RED),
        ).arrange(RIGHT, buff=0.3).move_to([0, -3.4, 0])
        self.play(AnimationGroup(*[FadeIn(c, shift=UP * 0.1) for c in chips], lag_ratio=0.2))
        self._end_scene()

    # ─── Scene 7: 2PC happy path ──────────────────────────────────────
    def scene_2pc_happy_path(self):
        self._header("2PC: Happy Path", color=TEAL, demo="05-2pc.sh")
        rows, ys, log = self._twopc_stage()
        yc, yp = ys[0], ys[1:]

        begin = self._chip("bk-7f2 begin", C_COORD)
        begin.move_to([_tx(0.45), yc + 0.38, 0])
        self.play(FadeIn(begin))
        self._log(log, "COORD", "bk-7f2 begin, room 101 for user 1, amount 120.00", C_COORD)
        self._log(log, "COORD", "tx_log bk-7f2 = PREPARING", C_COORD)
        self._next_slide(phase=True)

        # phase 1: one participant at a time, each writes and votes
        p1 = make_label("phase 1: prepare, one by one", font_size=9, color=C_COORD)
        p1.move_to([_tx(2.3), yc + 0.62, 0])
        self.play(FadeIn(p1))
        groups = []
        self._prepare(0.4, yc, yp[0], C_BOOK, groups)
        lock_lbl = make_label("locks held", font_size=10, color=GREY_A)
        lock_lbl.move_to([_tx(1.5), yp[0] - 0.3, 0])
        self.play(FadeIn(lock_lbl), run_time=0.3)
        self._log(log, "BOOKING", "XA START · INSERT booking CONFIRMED · XA END · XA PREPARE → YES", C_BOOK)
        self._prepare(1.7, yc, yp[1], C_PAY, groups)
        self._log(log, "PAYMENT", "XA START · INSERT payment · wallet -120.00 · XA PREPARE → YES", C_PAY)
        self._prepare(3.0, yc, yp[2], C_ACC, groups)
        self._log(log, "ACCOUNT", "XA START · ledger REVENUE 120.00 · XA PREPARE → YES", C_ACC)
        self._next_slide(phase=True)

        # commit point: the decision row in tx_log
        disk = make_icon(ICON_DATABASE, color=C_COORD, height=0.3)
        disk.move_to([_tx(4.6), yc, 0])
        cp = make_label("commit point", font_size=10, color=YELLOW).next_to(disk, UP, buff=0.3)
        self.play(FadeIn(disk, scale=0.6), *self._grow_all(groups, 4.6))
        self._play_glow(disk, YELLOW, pad=0.25)
        self.play(FadeIn(cp))
        self._log(log, "COORD", "tx_log bk-7f2 = COMMIT, the decision is on disk, no going back", YELLOW,
                  text_color=YELLOW)
        self._next_slide(phase=True)

        # phase 2: commit
        p2 = make_label("phase 2", font_size=9, color=GREEN).move_to([_tx(5.6), yc + 0.62, 0])
        self.play(FadeIn(p2))
        self._fan(5.0, yc, 5.8, yp, GREEN, label="XA COMMIT", extra=self._grow_all(groups, 5.8))
        self._log(log, "ALL", "XA COMMIT 'bk-7f2' on booking, payment, accounting · locks released", GREEN)
        done = [make_icon(ICON_CHECK, color=GREEN, height=0.22).move_to([_tx(6.15), y, 0]) for y in yp]
        self.play(*[FadeIn(d, scale=0.6) for d in done])
        self._next_slide(phase=True)
        self._clear()

        # points of no return
        self._header("Two Points of No Return", color=TEAL)
        c1 = self._card("1. A participant votes yes",
                        "It gives up the right to abort. It must commit later if asked,\n"
                        "even after a crash. That's why it writes everything to disk first.",
                        C_PAY, width=10.5)
        c2 = self._card("2. The coordinator decides",
                        "The decision is final. If a commit request fails,\n"
                        "the coordinator retries forever.",
                        C_COORD, width=10.5)
        VGroup(c1, c2).arrange(DOWN, buff=0.4).move_to([0, 0.5, 0])
        self.play(FadeIn(c1, shift=UP * 0.1))
        self.play(FadeIn(c2, shift=UP * 0.1))
        wed = make_label('like a wedding: "I do" = yes vote, the minister = coordinator',
                         font_size=11, color=GREY_B)
        wed.move_to([0, -2.4, 0])
        self.play(FadeIn(wed))
        self._end_scene()

    # ─── Scene 8: 2PC vote no ─────────────────────────────────────────
    def scene_2pc_vote_no(self):
        self._header("2PC: One Participant Says No", color=RED, demo="05-2pc.sh")
        rows, ys, log = self._twopc_stage()
        yc, yp = ys[0], ys[1:]
        self._log(log, "COORD", "bk-8a1 begin, room 102 for user 2 (balance 50.00), amount 120.00", C_COORD)
        self._log(log, "COORD", "tx_log bk-8a1 = PREPARING", C_COORD)
        groups = []
        self._prepare(0.4, yc, yp[0], C_BOOK, groups)
        self._log(log, "BOOKING", "XA PREPARE → YES", C_BOOK)
        _, pay_bar = self._prepare(1.7, yc, yp[1], C_PAY, groups, vote_yes=False)
        groups.remove(pay_bar)
        no = make_label("NO", font_size=10, color=RED).move_to([_tx(2.3), yp[1] + 0.32, 0])
        self.play(FadeIn(no), Indicate(rows[2], color=RED), pay_bar[0].animate.set_fill(opacity=0.06))
        self._log(log, "PAYMENT", "CHECK chk_balance_non_negative fails: 50.00 - 120.00 < 0", RED, text_color=RED)
        self._log(log, "PAYMENT", "XA ROLLBACK of its own branch → vote NO", RED)
        never = self._chip("never asked", GREY_B).move_to([_tx(3.3), yp[2] + 0.3, 0])
        self.play(FadeIn(never))
        self._log(log, "COORD", "payment voted NO, so accounting is not asked at all", C_COORD)
        self._next_slide(phase=True)

        self._log(log, "COORD", "tx_log bk-8a1 = ABORT", RED, text_color=RED)
        abort = self._arr(3.4, yc, 4.0, yp[0], RED)
        abort_lbl = make_label("XA ROLLBACK", font_size=10, color=RED).move_to([_tx(3.9), yc + 0.22, 0])
        self.play(GrowArrow(abort), FadeIn(abort_lbl), *self._grow_all(groups, 4.0), run_time=0.6)
        self._log(log, "BOOKING", "XA ROLLBACK 'bk-8a1' · its locks are released", RED)
        self.play(*[g[0].animate.set_fill(opacity=0.06) for g in groups])
        badge = self._verdict_badge("Nothing for room 102 anywhere  ✓", GREEN, width=5.5)
        badge.move_to([_tx(6.7), 1.0, 0])
        self.play(FadeIn(badge, shift=UP * 0.1))
        cap = make_label("one NO aborts the whole thing", font_size=10, color=GREY_B).next_to(badge, DOWN, buff=0.15)
        self.play(FadeIn(cap))
        self._end_scene()

    # ─── Scene 9: 2PC coordinator crash ───────────────────────────────
    def scene_2pc_coordinator_crash(self):
        self._header("2PC: The Coordinator Crashes", color=RED, demo="06-2pc-in-doubt.sh")
        rows, ys, log = self._twopc_stage()
        yc, yp = ys[0], ys[1:]
        mode = self._chip("fail-mode = CRASH_AFTER_VOTES", RED)
        mode.move_to([_tx(1.2), yc + 0.38, 0])
        self.play(FadeIn(mode))
        self._log(log, "COORD", "tx_log bk-9c4 = PREPARING", C_COORD)
        groups = []
        for t, y, c in zip([0.3, 1.6, 2.9], yp, [C_BOOK, C_PAY, C_ACC]):
            self._prepare(t, yc, y, c, groups)
        self._log(log, "ALL", "XA PREPARE 'bk-9c4' → YES, YES, YES", GREEN)
        self._next_slide(phase=True)

        bomb = make_icon(ICON_BOMB, color=RED, height=0.42).move_to([_tx(4.5), yc, 0])
        self.play(FadeIn(bomb, scale=1.4), rows[0].animate.set_opacity(0.3), *self._grow_all(groups, 4.5))
        self._log(log, "COORD", "everyone voted yes and I am walking away (no decision written)", RED,
                  text_color=RED)

        chips = VGroup(*[self._chip("IN DOUBT", YELLOW).move_to([_tx(4.9), y + 0.3, 0]) for y in yp])
        self.play(*[FadeIn(c, scale=0.8) for c in chips])
        tracker = ValueTracker(0)
        clock_icon = make_icon(ICON_STOPWATCH, color=YELLOW, height=0.3).move_to([4.2, yc, 0])
        clock = always_redraw(lambda: make_label(
            f"in doubt  {int(tracker.get_value()) // 60:02d}:{int(tracker.get_value()) % 60:02d}",
            font_size=11, color=YELLOW,
        ).next_to(clock_icon, RIGHT, buff=0.15))
        self.add(clock_icon, clock)
        self.play(tracker.animate.set_value(1200), *self._grow_all(groups, 8.3), run_time=3.0)
        self._log(log, "MYSQL", "XA RECOVER lists bk-9c4 for booking, payment and accounting", YELLOW)
        self._next_slide(phase=True)

        # an unrelated write to the same wallet blocks
        t2 = self._chip("UPDATE wallets … user_id = 1", GREY_A, font_size=9)
        t2.move_to([_tx(7.0), yp[1] - 0.45, 0])
        t2_arrow = Arrow(t2.get_top(), [_tx(7.0), yp[1] - 0.12, 0], buff=0.02, stroke_width=1.8,
                         color=RED, tip_length=0.12)
        self.play(FadeIn(t2), GrowArrow(t2_arrow))
        self.play(Wiggle(t2_arrow))
        self._log(log, "PAYMENT", "other session, innodb_lock_wait_timeout = 5 ... waiting for the lock", C_PAY)
        self._log(log, "PAYMENT", "ERROR 1205 after 5s: Lock wait timeout exceeded", RED, text_color=RED)
        self._next_slide(phase=True)

        # restart paymentdb
        pay_icon = rows[2].icon
        self.play(pay_icon.animate.set_opacity(0.1), run_time=0.4)
        self.play(pay_icon.animate.set_opacity(1.0), run_time=0.4)
        self.play(Indicate(chips[1], color=YELLOW), Indicate(groups[1], color=C_PAY))
        self._log(log, "MYSQL", "after a restart XA RECOVER still lists bk-9c4, the locks are still held", C_PAY)
        self._next_slide(phase=True)

        self.play(FadeOut(log, *log.lines))
        l1 = make_label("Locks are held until commit.", font_size=16, color=YELLOW)
        l2 = make_label("… and commit is waiting on a dead coordinator.", font_size=16, color=RED)
        VGroup(l1, l2).arrange(DOWN, buff=0.25).move_to([0, -2.4, 0])
        self.play(FadeIn(l1))
        self.play(AddTextLetterByLetter(l2, time_per_char=0.03))
        self._end_scene()

    # ─── Scene 10: 2PC recovery + heuristic ───────────────────────────
    def _commit_lost_setup(self):
        """COMMIT_LOST_TO_PAYMENT: decision logged, booking and accounting committed,
        payment still prepared and holding its locks. Shared by recovery and heuristic."""
        rows, ys, log = self._twopc_stage()
        yc, yp = ys[0], ys[1:]
        mode = self._chip("fail-mode = COMMIT_LOST_TO_PAYMENT", RED).move_to([_tx(1.5), yc + 0.38, 0])
        prepared = VGroup(*[self._arr(0.3, yc, 0.8, y, C_COORD) for y in yp],
                          *[self._arr(1.0, y, 1.5, yc, GREEN) for y in yp])
        disk = make_icon(ICON_DATABASE, color=C_COORD, height=0.28).move_to([_tx(2.0), yc, 0])
        bars = self._start_bars(0.8, yp, [C_BOOK, C_PAY, C_ACC])
        self.play(FadeIn(mode), FadeIn(prepared), FadeIn(disk), *self._grow_bars(bars, 2.4))
        self._log(log, "COORD", "tx_log bk-7f2 = COMMIT, the decision is on disk", C_COORD)

        sent = VGroup(self._arr(2.4, yc, 3.0, yp[0], GREEN), self._arr(2.4, yc, 3.0, yp[2], GREEN))
        lost = self._dashed_arrow([_tx(2.4), yc, 0], [_tx(3.0), yp[1] + 0.15, 0], RED)
        lost_x = make_label("✗ lost", font_size=11, color=RED).next_to(lost.get_end(), RIGHT, buff=0.1)
        pay_bar = VGroup(bars[1])
        pay_bar.t0, pay_bar.ys, pay_bar.colors, pay_bar.h = 0.8, [yp[1]], [C_PAY], 0.2
        self.play(GrowArrow(sent[0]), GrowArrow(sent[1]), Create(lost), *self._grow_bars(bars, 3.0))
        self.play(FadeIn(lost_x), bars[0].animate.set_fill(opacity=0.06), bars[2].animate.set_fill(opacity=0.06))
        c_book = self._chip("CONFIRMED", GREEN).move_to([_tx(4.3), yp[0] + 0.3, 0])
        c_pay = self._chip("IN DOUBT", YELLOW).move_to([_tx(4.3), yp[1] + 0.3, 0])
        c_acc = self._chip("REVENUE committed", GREEN).move_to([_tx(4.3), yp[2] + 0.3, 0])
        self.play(FadeIn(c_book), FadeIn(c_pay), FadeIn(c_acc), *self._grow_bars(pay_bar, 4.2))
        self._log(log, "COORD", "the commit message to payment is lost. The decision still stands.", RED,
                  text_color=RED)
        return rows, ys, log, bars, pay_bar, c_pay

    def scene_2pc_recovery(self):
        self._header("2PC: Recovery", color=TEAL, demo="06-2pc-in-doubt.sh")
        rows, ys, log = self._twopc_stage()
        yc, yp = ys[0], ys[1:]
        colors = [C_BOOK, C_PAY, C_ACC]

        # Case 1 starts where scene 9 stopped: all prepared, no decision, locks held
        prepared = VGroup(*[self._arr(0.3, yc, 0.8, y, C_COORD) for y in yp],
                          *[self._arr(1.0, y, 1.5, yc, GREEN) for y in yp])
        bomb = make_icon(ICON_BOMB, color=RED, height=0.36).move_to([_tx(2.0), yc, 0])
        bars = self._start_bars(0.8, yp, colors)
        chips = VGroup(*[self._chip("IN DOUBT", YELLOW).move_to([_tx(2.6), y + 0.3, 0]) for y in yp])
        self.play(FadeIn(prepared), FadeIn(bomb), rows[0].animate.set_opacity(0.3),
                  *self._grow_bars(bars, 4.0), FadeIn(chips))
        self._log(log, "MYSQL", "where scene 9 stopped: XA RECOVER lists bk-9c4 on all three", YELLOW)
        self._next_slide(phase=True)

        back = self._chip("POST /admin/recover", C_COORD).move_to([_tx(3.4), yc + 0.38, 0])
        self.play(rows[0].animate.set_opacity(1.0), FadeIn(back), *self._grow_bars(bars, 4.5))
        self._log(log, "COORD", "reads tx_log: bk-9c4 = PREPARING, no decision was ever written", C_COORD)
        self._fan(4.5, yc, 5.3, yp, RED, label="XA ROLLBACK", extra=self._grow_bars(bars, 5.3))
        self.play(*[b.animate.set_fill(opacity=0.06) for b in bars],
                  *[Transform(c, self._chip("rolled back", GREY_B).move_to(c)) for c in chips])
        self._log(log, "COORD", "bk-9c4 recovering as ABORT · locks released", RED)
        self._log(log, "PAYMENT", "the blocked UPDATE wallets now finishes in milliseconds", C_PAY)
        self._next_slide(phase=True)
        self._clear()

        # Case 2: the decision was COMMIT, but the message to payment was lost
        self._header("2PC: Recovery, Commit Lost", color=TEAL)
        rows, ys, log, bars, pay_bar, c_pay = self._commit_lost_setup()
        yc, yp = ys[0], ys[1:]
        mid = self._verdict_badge("booking and ledger visible, payment not yet: atomic commit, not atomic visibility",
                                  YELLOW, width=12.0)
        mid.move_to([0, -1.05, 0])
        self.play(FadeIn(mid, shift=UP * 0.1))
        self._next_slide(phase=True)
        self.play(FadeOut(mid))

        back = self._chip("POST /admin/recover", C_COORD).move_to([_tx(4.9), yc + 0.38, 0])
        self.play(FadeIn(back), *self._grow_bars(pay_bar, 4.9))
        commit = self._arr(4.9, yc, 5.6, yp[1], GREEN)
        self.play(GrowArrow(commit), *self._grow_bars(pay_bar, 5.6))
        self.play(Transform(c_pay, self._chip("CHARGED", GREEN).move_to(c_pay)),
                  bars[1].animate.set_fill(opacity=0.06))
        self._log(log, "COORD", "recover replays XA COMMIT on all three, finished ones answer XAER_NOTA", GREEN)
        self._next_slide(phase=True)
        self._clear()

        # Heuristic decision: same starting state, but an admin acts before recovery
        self._header("The Escape Hatch: Heuristic Decisions", color=RED)
        rows, ys, log, bars, pay_bar, c_pay = self._commit_lost_setup()
        yc, yp = ys[0], ys[1:]
        self._next_slide(phase=True)

        admin = self._node(ICON_USER, "admin", GREY_A, icon_h=0.3, font_size=9)
        admin.move_to([_tx(5.3), (yp[1] + yp[2]) / 2 - 0.05, 0])
        rb = self._chip("mysql> XA ROLLBACK 'bk-7f2','payment'", RED).next_to(admin, RIGHT, buff=0.2)
        self.play(FadeIn(admin), *self._grow_bars(pay_bar, 5.3))
        self.play(FadeIn(rb, shift=RIGHT * 0.1))
        self.play(Transform(c_pay, self._chip("rolled back", RED).move_to(c_pay)),
                  bars[1].animate.set_fill(opacity=0.06))
        self._log(log, "ADMIN", "XA ROLLBACK 'bk-7f2','payment' typed by hand", RED, text_color=RED)
        self._next_slide(phase=True)

        a = self._arr(6.0, yc, 6.6, yp[1], GREEN)
        back = self._arr(6.8, yp[1], 7.4, yc, RED)
        self.play(GrowArrow(a))
        self.play(GrowArrow(back))
        dne = make_label("XAER_NOTA", font_size=10, color=RED).move_to(back.get_center() + RIGHT * 0.7)
        self.play(FadeIn(dne))
        self._log(log, "COORD", "recover: XA COMMIT on payment → XAER_NOTA, the code treats it as already done", RED,
                  text_color=RED)
        self._next_slide(phase=True)

        self.play(FadeOut(log, *log.lines))
        end = VGroup(
            self._chip("booking CONFIRMED", GREEN, font_size=11),
            self._chip("ledger REVENUE", GREEN, font_size=11),
            self._chip("payment: none", RED, font_size=11),
        ).arrange(RIGHT, buff=0.35).move_to([0, -1.9, 0])
        self.play(AnimationGroup(*[FadeIn(c, shift=UP * 0.1) for c in end], lag_ratio=0.2))
        self.play(*[Indicate(c, color=RED) for c in end])
        cap = self._caption('"Heuristic" is a polite word for "probably broke atomicity". The coordinator never notices.',
                            color=RED, y=-2.9, font_size=13)
        self.play(FadeIn(cap))
        self._end_scene()

    # ─── Scene 11: 2PC cost ───────────────────────────────────────────
    def scene_2pc_cost(self):
        self._header("What 2PC Costs", color=RED)
        items = [
            (ICON_DATABASE, C_COORD, "The coordinator is a database too",
             "its log is critical state, lose it and transactions stay in doubt"),
            (ICON_DANGER, RED, "Not replicated means single point of failure",
             "many coordinators aren't highly available by default"),
            (ICON_SERVER, C_BOOK, "App servers stop being stateless",
             "the coordinator's log lives on the app server's disk"),
            (ICON_STOPWATCH, YELLOW, "Extra fsyncs and round trips",
             "MySQL distributed transactions reported more than 10× slower"),
            (ICON_BOMB, RED, "It amplifies failures",
             "one participant down and the whole transaction fails"),
        ]
        cards = VGroup(*[self._icon_row_card(i, c, t, d) for i, c, t, d in items])
        cards.arrange(DOWN, buff=0.16, aligned_edge=LEFT).move_to([0, -0.15, 0])
        for card in cards:
            self.play(FadeIn(card, shift=RIGHT * 0.12), run_time=0.4)
            self.wait(0.35)
        foot = make_label("XA / JTA is the standard API for this: Postgres, MySQL, ActiveMQ …",
                          font_size=10, color=GREY_B)
        foot.move_to([0, -3.5, 0])
        self.play(FadeIn(foot))
        self._end_scene()

    # ═════════════════════════════════════════════════════════════════
    # Part 3: Saga
    # ═════════════════════════════════════════════════════════════════

    # ─── Scene 12: Saga intro ─────────────────────────────────────────
    def scene_saga_intro(self):
        self._header("Saga", color=ORANGE, demo="07-saga.sh")
        orch, svcs, tables, log = self._saga_stage(with_log=True)
        cap = self._caption("Each service commits its own local transaction right away.",
                            y=-2.3, font_size=12)
        self.play(FadeIn(cap))
        self._log(log, "sg-…", "one row per step", GREY_A)
        self._next_slide(phase=True)
        self._clear()

        self._header("Steps and Compensations", color=ORANGE)
        table = self._table(
            ["Step", "Service", "Action", "Compensation"],
            [GREY_B, GREY_B, GREEN, RED],
            [
                ("1 reserve", GREY_A, "Booking", C_BOOK, "lock slots, INSERT booking PENDING", GREY_A,
                 "set CANCELLED", GREY_A),
                ("2 charge", GREY_A, "Payment", C_PAY, "INSERT payment, wallet -120", GREY_A,
                 "refund, set REFUNDED", GREY_A),
                ("3 ledger", GREY_A, "Accounting", C_ACC, "ledger REVENUE", GREY_A, "ledger REVERSAL", GREY_A),
                ("4 confirm", GREY_A, "Booking", C_BOOK, "set CONFIRMED", GREY_A, "none, this is the end", GREY_B),
            ],
            font_size=14,
        )
        table.move_to([0, 0.4, 0])
        self.play(FadeIn(table[0]), Create(table[1]))
        for row in table[2]:
            self.play(FadeIn(row, shift=UP * 0.1), run_time=0.4)
            self.wait(0.25)
        cap = self._caption("A compensation is a new transaction, not a rollback.",
                            color=ORANGE, y=-2.4, font_size=15)
        self.play(FadeIn(cap, shift=UP * 0.1))
        self._end_scene()

    _STEP_NAMES = {1: "reserve", 2: "charge", 3: "ledger", 4: "confirm"}

    def _saga_step(self, orch, svc, table, log, step, row_text, color, log_text=None):
        """One saga step: the call, the committed row, the saga_log line."""
        a = self._call(orch, svc, color)
        self._add_row(table, row_text, color)
        self._log(log, f"{step} {self._STEP_NAMES[step]}", log_text or "DONE", color)
        self.play(FadeOut(a), run_time=0.25)

    # ─── Scene 13: Saga happy path ────────────────────────────────────
    def scene_saga_happy_path(self):
        self._header("Saga: Happy Path", color=ORANGE, demo="07-saga.sh")
        orch, svcs, tables, log = self._saga_stage()
        self._saga_step(orch, svcs[0], tables[0], log, 1, "booking 1 PENDING", YELLOW, "DONE, PENDING")
        self._saga_step(orch, svcs[1], tables[1], log, 2, "booking 1 CHARGED 120.00", C_PAY)
        self._saga_step(orch, svcs[2], tables[2], log, 3, "booking 1 REVENUE 120.00", C_ACC)
        a = self._call(orch, svcs[0], GREEN, shift=0.15)
        self.play(self._swap_row(tables[0], 0, "booking 1 CONFIRMED", GREEN))
        self._log(log, "4 confirm", "DONE, CONFIRMED", GREEN)
        self.play(FadeOut(a), run_time=0.25)
        self._next_slide(phase=True)
        cap = self._caption("Rows appear one by one, not together. No lock spans the whole flow.",
                            y=-2.4, font_size=12)
        self.play(FadeIn(cap))
        self._end_scene()

    # ─── Scene 14: Saga failures ──────────────────────────────────────
    def scene_saga_failures(self):
        self._header("Saga: Payment Fails", color=RED)
        orch, svcs, tables, log = self._saga_stage()
        self._saga_step(orch, svcs[0], tables[0], log, 1, "booking 1 PENDING", YELLOW, "DONE, PENDING")
        a = self._call(orch, svcs[1], C_PAY)
        self._mark(svcs[1], ok=False)
        why = make_label("user 2: CHECK, 50 < 120", font_size=9, color=RED)
        why.next_to(tables[1].div, DOWN, buff=0.15)
        self.play(FadeIn(why))
        self._log(log, "2 charge", "FAILED", RED, text_color=RED)
        self.play(FadeOut(a))
        self._next_slide(phase=True)
        self._call(orch, svcs[0], RED, dashed=True, shift=-0.15)
        self.play(self._swap_row(tables[0], 0, "booking 1 CANCELLED", RED))
        self._log(log, "1 reserve", "COMPENSATED", RED)
        cap = self._caption("Final: booking CANCELLED, no payment, no ledger row.", y=-2.4, font_size=12)
        self.play(FadeIn(cap))
        self._next_slide(phase=True)
        self._clear()

        self._header("Saga: Step 3 Fails", color=RED, demo="07-saga.sh · failAt=3")
        orch, svcs, tables, log = self._saga_stage()
        self._saga_step(orch, svcs[0], tables[0], log, 1, "booking 1 PENDING", YELLOW, "DONE, PENDING")
        self._saga_step(orch, svcs[1], tables[1], log, 2, "booking 1 CHARGED 120.00", C_PAY)
        a = self._call(orch, svcs[2], GREY_B)
        self._mark(svcs[2], ok=False)
        down = make_label("failAt=3, failing on purpose", font_size=9, color=RED).next_to(svcs[2], DOWN, buff=0.08)
        self.play(FadeIn(down))
        self._log(log, "3 ledger", "FAILED", RED, text_color=RED)
        self.play(FadeOut(a))
        self._next_slide(phase=True)
        self._call(orch, svcs[1], RED, dashed=True, shift=-0.15)
        self.play(self._swap_row(tables[1], 0, "booking 1 REFUNDED", RED))
        self._log(log, "2 charge", "COMPENSATED", RED)
        self._call(orch, svcs[0], RED, dashed=True, shift=-0.15)
        self.play(self._swap_row(tables[0], 0, "booking 1 CANCELLED", RED))
        self._log(log, "1 reserve", "COMPENSATED", RED)
        cap = self._caption("Undo in reverse order. The refund is a new state, not a deleted row.",
                            color=ORANGE, y=-2.4, font_size=14)
        self.play(FadeIn(cap))
        self._end_scene()

    # ─── Scene 15: Saga crash + duplicate ─────────────────────────────
    def scene_saga_crash_and_retry(self):
        self._header("Saga: The Orchestrator Crashes", color=ORANGE, demo="07-saga.sh · killAt=2")
        orch, svcs, tables, log = self._saga_stage()
        self._saga_step(orch, svcs[0], tables[0], log, 1, "booking 1 PENDING", YELLOW, "DONE, PENDING")
        self._saga_step(orch, svcs[1], tables[1], log, 2, "booking 1 CHARGED 50.00", C_PAY)
        bomb = make_icon(ICON_BOMB, color=RED, height=0.4).next_to(orch, RIGHT, buff=0.2)
        self.play(FadeIn(bomb, scale=1.4), orch.animate.set_opacity(0.3))
        self._log(log, "killAt=2", "dies, nothing compensated", RED, text_color=RED)
        mid = self._caption("The middle state: booking PENDING and the money already gone. 2PC never shows this.",
                            y=-2.4, font_size=11)
        self.play(FadeIn(mid))
        self._next_slide(phase=True)

        self.play(FadeOut(bomb), FadeOut(mid), orch.animate.set_opacity(1.0))
        self._log(log, "resume", "last DONE is step 2", C_COORD)
        self.play(Indicate(log.lines[-2], color=RED), Indicate(log.lines[-1], color=C_COORD))
        self._saga_step(orch, svcs[2], tables[2], log, 3, "booking 1 REVENUE 50.00", C_ACC)
        a = self._call(orch, svcs[0], GREEN, shift=0.15)
        self.play(self._swap_row(tables[0], 0, "booking 1 CONFIRMED", GREEN))
        self._log(log, "4 confirm", "DONE, CONFIRMED", GREEN)
        self.play(FadeOut(a))
        cap = self._caption("POST /saga/{id}/resume reads saga_log and carries on from step 3.", y=-2.4, font_size=13)
        self.play(FadeIn(cap))
        self._next_slide(phase=True)
        self.play(FadeOut(cap))

        # duplicate message
        dup_lbl = make_label("run 4: the same charge sent again", font_size=9, color=C_PAY)
        dup_lbl.next_to(svcs[1], RIGHT, buff=0.35).shift(UP * 0.55)
        self._call(orch, svcs[1], C_PAY, shift=0.15)
        self.play(FadeIn(dup_lbl))
        bounce = self._dashed_arrow(svcs[1].get_top() + LEFT * 0.25 + UP * 0.05,
                                    orch.get_bottom() + LEFT * 0.25 + DOWN * 0.05, GREY_B)
        self.play(Create(bounce))
        uniq = make_label("INSERT IGNORE: no-op", font_size=9, color=GREY_B)
        uniq.next_to(tables[1].rows[0], DOWN, buff=0.12)
        uniq.align_to(tables[1].rows[0], LEFT)
        self.play(FadeIn(uniq), Indicate(tables[1].rows[0], color=GREY_A))
        self._log(log, "payment", "already charged, no-op", GREY_B)
        cap = self._caption("Every step and every compensation must be idempotent.",
                            y=-2.4, font_size=11)
        self.play(FadeIn(cap))
        self._end_scene()

    # ─── Scene 16: Saga no isolation ──────────────────────────────────
    def scene_saga_no_isolation(self):
        self._header("Saga: No Isolation", color=RED)
        orch, svcs, tables, _ = self._saga_stage(with_log=False)
        reader = self._node(ICON_CHART, "daily report", GREY_A, icon_h=0.45)
        reader.move_to([5.3, 0.9, 0])
        report = self._chip("revenue today: $0", GREY_A, font_size=10).next_to(reader, DOWN, buff=0.25)
        self.play(FadeIn(reader), FadeIn(report))

        for i, (txt, c) in enumerate([("booking 1 PENDING", YELLOW), ("booking 1 CHARGED 120.00", C_PAY),
                                      ("booking 1 REVENUE 120.00", C_ACC)]):
            a = self._call(orch, svcs[i], c)
            self._add_row(tables[i], txt, c)
            self.play(FadeOut(a), run_time=0.2)
        self._next_slide(phase=True)

        look = self._dashed_arrow(reader.get_left() + LEFT * 0.05, tables[2].get_right() + RIGHT * 0.05, GREY_A)
        self.play(Create(look))
        self.play(Transform(report, self._chip("revenue today: +$120", GREEN, font_size=10).move_to(report)))
        self._next_slide(phase=True)

        a = self._call(orch, svcs[0], RED, shift=0.15)
        fail = make_label("step 4 fails (failAt=4)", font_size=9, color=RED)
        fail.move_to([_COLS[0], 2.35, 0])
        self.play(FadeIn(fail), FadeOut(a))
        self._call(orch, svcs[2], RED, dashed=True, shift=-0.15)
        self._add_row(tables[2], "booking 1 REVERSAL 120.00", RED)
        self._call(orch, svcs[1], RED, dashed=True, shift=-0.15)
        self.play(self._swap_row(tables[1], 0, "booking 1 REFUNDED", RED))
        self._call(orch, svcs[0], RED, dashed=True, shift=-0.15)
        self.play(self._swap_row(tables[0], 0, "booking 1 CANCELLED", RED))
        wrong = make_label("the report is now wrong", font_size=10, color=RED).next_to(report, DOWN, buff=0.15)
        self.play(Indicate(report, color=RED))
        self.play(report[0].animate.set_stroke(RED), report[1].animate.set_color(RED), FadeIn(wrong))
        cap = self._caption("Saga = ACD, no I. Other readers see the middle.", color=RED, y=-2.4, font_size=15)
        self.play(FadeIn(cap))
        self._next_slide(phase=True)
        self._clear()

        # countermeasure: semantic lock
        self._header("Countermeasure: Semantic Lock", color=GREEN)
        orch, svcs, tables, _ = self._saga_stage(with_log=False)
        a = self._call(orch, svcs[0], YELLOW)
        self._add_row(tables[0], "room 101 PENDING", YELLOW)
        self.play(FadeOut(a))
        bob = self._node(ICON_USER, "Bob", GREY_A, icon_h=0.4)
        bob.move_to([-6.45, 0.85, 0])
        self.play(FadeIn(bob))
        try_arrow = Arrow(bob.get_right(), svcs[0].get_left(), buff=0.2, stroke_width=1.8,
                          color=GREY_A, tip_length=0.14)
        bob_req = make_label("room 101", font_size=9, color=GREY_A).next_to(try_arrow, UP, buff=0.08)
        self.play(GrowArrow(try_arrow), FadeIn(bob_req))
        rej = make_label("rejected: room already booked", font_size=10, color=RED)
        rej.next_to(tables[0], DOWN, buff=0.15).align_to(tables[0], LEFT)
        self.play(Wiggle(try_arrow), try_arrow.animate.set_color(RED), FadeIn(rej))
        code = make_code_text(
            "-- step 1 reserve: lock slots, then\nSELECT COUNT(*) FROM bookings\n WHERE room_id = 101 AND status <> 'CANCELLED'\n"
            "   AND starts_at < :end AND ends_at > :start",
            font_size=10, language="sql", force_code_object=True, glow=False,
        )
        code.move_to([0.6, -2.5, 0])
        self.play(FadeIn(code))
        cap = make_label("status <> 'CANCELLED' counts PENDING, so PENDING acts as our lock.", font_size=12, color=GREEN)
        cap.next_to(code, DOWN, buff=0.2)
        self.play(FadeIn(cap))
        self._end_scene()

    # ─── Scene 17: Orchestration vs choreography ──────────────────────
    def scene_saga_orchestration_vs_choreography(self):
        self._header("Orchestration vs Choreography", color=ORANGE)
        div = DashedLine([0, 2.7, 0], [0, -0.9, 0], dash_length=0.12, color=GREY_B, stroke_width=0.9)

        # left: orchestration
        lt = make_label("Orchestration", font_size=14, color=C_COORD).move_to([-3.6, 2.5, 0])
        o = self._node(ICON_STRUCTURE, "orchestrator", C_COORD, icon_h=0.4, font_size=9).move_to([-3.6, 1.35, 0])
        ls = VGroup(*[
            self._node(ICON_SERVER, n, c, icon_h=0.32, font_size=9).move_to([x, -0.1, 0])
            for n, c, x in [("Booking", C_BOOK, -5.4), ("Payment", C_PAY, -3.6), ("Accounting", C_ACC, -1.8)]
        ])
        la = VGroup(*[Arrow(o.get_bottom(), s.get_top(), buff=0.1, stroke_width=1.6, color=C_COORD, tip_length=0.12)
                      for s in ls])
        pm = make_label("Process Manager pattern · what the demo uses", font_size=9, color=GREY_B)
        pm.move_to([-3.6, -0.75, 0])
        self.play(Create(div), FadeIn(lt))
        self.play(FadeIn(o), FadeIn(ls))
        self.play(*[GrowArrow(a) for a in la])
        self.play(FadeIn(pm))
        self._next_slide(phase=True)

        # right: choreography
        rt = make_label("Choreography", font_size=14, color=C_PAY).move_to([3.6, 2.5, 0])
        kafka = make_icon(ICON_KAFKA, color=WHITE, height=0.36).move_to([3.6, 1.95, 0])
        topic = RoundedRectangle(corner_radius=0.08, width=4.6, height=0.5, stroke_color=GREY_B,
                                 stroke_width=1.2, fill_color="#161B22", fill_opacity=0.95)
        topic.move_to([3.6, 1.3, 0])
        evs = VGroup(
            make_label("booking.created", font_size=9, color=C_BOOK),
            make_label("→ payment.charged", font_size=9, color=C_PAY),
            make_label("→ ledger.recorded", font_size=9, color=C_ACC),
        ).arrange(RIGHT, buff=0.12).move_to(topic)
        rs = VGroup(*[
            self._node(ICON_SERVER, n, c, icon_h=0.32, font_size=9).move_to([x, -0.1, 0])
            for n, c, x in [("Booking", C_BOOK, 1.8), ("Payment", C_PAY, 3.6), ("Accounting", C_ACC, 5.4)]
        ])
        ra = VGroup(*[
            DashedLine(s.get_top() + UP * 0.05, [s.get_x(), topic.get_bottom()[1] - 0.05, 0],
                       dash_length=0.08, color=s[0].get_color(), stroke_width=1.4)
            for s in rs
        ])
        kl = make_label("events over Kafka", font_size=9, color=GREY_B).move_to([3.6, -0.75, 0])
        self.play(FadeIn(rt))
        self.play(FadeIn(kafka), FadeIn(topic), FadeIn(rs))
        self.play(AnimationGroup(*[FadeIn(e, shift=RIGHT * 0.1) for e in evs], lag_ratio=0.4), Create(ra))
        self.play(FadeIn(kl))
        self._next_slide(phase=True)

        table = self._table(
            ["", "Orchestration", "Choreography"],
            [GREY_B, C_COORD, C_PAY],
            [
                ("where the flow lives", GREY_A, "one place", GREY_A, "spread across services", GREY_A),
                ("easy to follow", GREY_A, "yes", GREEN, "harder as steps grow", GREY_A),
                ("coupling", GREY_A, "services know the orchestrator", GREY_A, "services only know events", GREY_A),
            ],
            font_size=13,
        )
        table.move_to([0, -2.25, 0])
        self.play(FadeIn(table))
        foot = make_label("Messages that can't be retried go to a Dead Letter Channel.",
                          font_size=9, color=GREY_B)
        foot.move_to([0, -3.6, 0])
        self.play(FadeIn(foot))
        self._end_scene()

    # ═════════════════════════════════════════════════════════════════
    # Part 4: Distributed locks (p. 301–304)
    # ═════════════════════════════════════════════════════════════════

    def _lock_stage(self):
        ys = [2.3, 1.2, 0.1, -1.0]
        rows = VGroup(
            self._row(ICON_SERVER, "client 1", ys[0], C_BOOK),
            self._row(ICON_LOCK, "lock_lease", ys[1], C_LOCK),
            self._row(ICON_SERVER, "client 2", ys[2], TEAL),
            self._row(ICON_DATABASE, "bookingdb", ys[3], GREY_A),
        )
        time_lbl = make_label("time →", font_size=9, color=GREY_B)
        time_lbl.move_to([_TL_X1 + 0.2, ys[0] + 0.32, 0])
        self.play(FadeIn(rows), FadeIn(time_lbl))
        return rows, ys

    def _lock_story(self, rows, ys, fencing):
        yA, yL, yB, yS = ys
        tok_a = "ok, token 1, 3s" if fencing else "ok, lease 3s"
        tok_b = "ok, token 2" if fencing else "ok"

        a1 = self._arr(0.2, yA, 0.8, yL, C_BOOK)
        m1 = self._msg(a1, "acquire room:101", LEFT * 0.9, C_BOOK)
        self.play(GrowArrow(a1), FadeIn(m1), run_time=0.5)
        a2 = self._arr(0.9, yL, 1.5, yA, C_LOCK)
        m2 = self._msg(a2, tok_a, RIGHT * 0.75, C_LOCK)
        self.play(GrowArrow(a2), FadeIn(m2), run_time=0.5)
        lease = self._start_bars(0.9, [yL], [C_LOCK], height=0.24)
        lease_lbl = make_label("client 1's lease (3s)", font_size=10, color=C_LOCK).move_to([_tx(2.3), yL - 0.3, 0])
        self.play(*self._grow_bars(lease, 1.8), FadeIn(lease_lbl), run_time=0.5)
        self._next_slide(phase=True)

        pause = self._start_bars(1.8, [yA], [GREY_B], height=0.34)
        pause_lbl = make_label("5s pause", font_size=11, color=GREY_A).move_to([_tx(2.9), yA, 0])
        self.play(rows[0].animate.set_opacity(0.35), *self._grow_bars(pause, 3.7),
                  *self._grow_bars(lease, 3.7), run_time=1.6)
        self.play(FadeIn(pause_lbl))
        expired = make_label("expired", font_size=10, color=RED).move_to([_tx(3.95), yL + 0.28, 0])
        self.play(FadeIn(expired), lease[0].animate.set_fill(RED, opacity=0.25))
        self._next_slide(phase=True)

        b1 = self._arr(4.0, yB, 4.5, yL, TEAL)
        m3 = self._msg(b1, "acquire", LEFT * 0.55, TEAL)
        self.play(GrowArrow(b1), FadeIn(m3), *self._grow_bars(pause, 4.5), run_time=0.5)
        b2 = self._arr(4.6, yL, 5.1, yB, C_LOCK)
        m4 = self._msg(b2, tok_b, RIGHT * 0.75, C_LOCK)
        self.play(GrowArrow(b2), FadeIn(m4), *self._grow_bars(pause, 5.1), run_time=0.5)
        b3 = self._arr(5.3, yB, 5.8, yS, TEAL)
        w_b = "write, token 2" if fencing else "INSERT booking"
        m5 = self._msg(b3, w_b, RIGHT * 0.9, TEAL)
        self.play(GrowArrow(b3), FadeIn(m5), *self._grow_bars(pause, 5.8), run_time=0.5)
        state_b = "rooms.fence_token: 2 · booking for user 2" if fencing else "booking for user 2"
        s1 = self._chip(state_b, TEAL).move_to([_tx(5.8), yS - 0.42, 0])
        self.play(FadeIn(s1))
        self._next_slide(phase=True)

        self.play(*self._grow_bars(pause, 6.3), run_time=0.4)
        self.play(rows[0].animate.set_opacity(1.0))
        think = self._chip('"I still have the lock"', C_BOOK).move_to([_tx(6.9), yA + 0.42, 0])
        self.play(FadeIn(think, shift=DOWN * 0.1))
        a3 = self._arr(6.6, yA, 7.4, yS, C_BOOK)
        w_a = "write, token 1" if fencing else "INSERT booking"
        m6 = self._msg(a3, w_a, RIGHT * 0.95 + UP * 0.35, C_BOOK)
        self.play(GrowArrow(a3), FadeIn(m6), run_time=0.7)
        return s1, a3

    # ─── Scene 18: Lock without fencing ───────────────────────────────
    def scene_lock_without_fencing(self):
        self._header("Distributed Lock: The Paused Client", color=YELLOW)
        why = make_label("Without the token check, the write is a plain INSERT. Nothing in bookings stops a second one.",
                         font_size=10, color=GREY_B)
        why.move_to([0, 2.95, 0])
        self.play(FadeIn(why))
        rows, ys = self._lock_stage()
        self._lock_story(rows, ys, fencing=False)

        s2 = self._chip("booking for user 1", RED).move_to([_tx(7.4), ys[3] - 0.42, 0])
        self.play(FadeIn(s2))
        self.play(Indicate(s2, color=RED))
        badge = self._verdict_badge("Room 101 booked twice for 15:00–16:00  ✗", RED, width=8.0)
        badge.move_to([0, -2.3, 0])
        self.play(FadeIn(badge, shift=UP * 0.1))
        cap = self._caption("A node can't trust its own sense of time. The lease expired while it was paused.",
                            y=-3.1, font_size=11)
        self.play(FadeIn(cap))
        self._end_scene()

    # ─── Scene 19: Lock with fencing ──────────────────────────────────
    def scene_lock_with_fencing(self):
        self._header("Fencing Tokens", color=GREEN, demo="04-fencing.sh")
        rows, ys = self._lock_stage()
        _, a3 = self._lock_story(rows, ys, fencing=True)

        back = self._dashed_arrow([_tx(7.6), ys[3], 0], [_tx(8.2), ys[0], 0], RED)
        rej = make_label("stale fencing token 1", font_size=10, color=RED).move_to([_tx(8.1), ys[1] + 0.1, 0])
        self.play(Create(back), FadeIn(rej))
        self.play(a3.animate.set_color(RED))
        self._next_slide(phase=True)

        code = make_code_text(
            "UPDATE rooms SET fence_token = :t\n WHERE room_id = 101 AND fence_token < :t;\n"
            "-- 1 row: INSERT the booking   0 rows: reject",
            font_size=10, language="sql", force_code_object=True, glow=False,
        )
        code.move_to([-2.2, -2.45, 0])
        chips = VGroup(self._chip("client 2, token 2  →  1 row", GREEN, font_size=10),
                       self._chip("client 1, token 1  →  0 rows", RED, font_size=10)).arrange(DOWN, buff=0.2)
        chips.next_to(code, RIGHT, buff=0.6)
        self.play(FadeIn(code))
        self.play(AnimationGroup(*[FadeIn(c, shift=LEFT * 0.1) for c in chips], lag_ratio=0.3))
        self._next_slide(phase=True)
        self._clear()

        self._header("Fencing Tokens: Two Rules", color=GREEN)
        c1 = self._card("The check lives in the storage, not the client",
                        "Client 1 honestly believes it still has the lock. Only bookingdb can say no.",
                        GREEN, width=11.0)
        c2 = self._card("Tokens only ever go up",
                        "lock_lease does token = token + 1 on every grant and expiry never resets it.\n"
                        "Real systems use ZooKeeper (zxid) or etcd (revision): linearizable and fault tolerant.",
                        C_LOCK, width=11.0)
        VGroup(c1, c2).arrange(DOWN, buff=0.4).move_to([0, 0.4, 0])
        self.play(FadeIn(c1, shift=UP * 0.1))
        self.play(FadeIn(c2, shift=UP * 0.1))
        foot = make_label("Fencing protects against mistaken nodes, not lying ones (Byzantine faults are out of scope).",
                          font_size=10, color=GREY_B)
        foot.move_to([0, -2.5, 0])
        self.play(FadeIn(foot))
        self._end_scene()

    # ═════════════════════════════════════════════════════════════════
    # Part 5: Wrap up
    # ═════════════════════════════════════════════════════════════════

    # ─── Scene 20: 2PC vs Saga ────────────────────────────────────────
    def scene_compare(self):
        self._header("2PC vs Saga", color=TEAL)
        table = self._table(
            ["", "2PC", "Saga"],
            [GREY_B, TEAL, ORANGE],
            [
                ("Atomicity", GREY_A, "all or nothing", GREY_A, "eventually, via compensations", GREY_A),
                ("Isolation", GREY_A, "yes, readers wait", GREEN, "none, readers see the middle", RED),
                ("Locks", GREY_A, "held until the decision", RED, "only inside each local step", GREEN),
                ("One node down", GREY_A, "everything blocks", RED, "that step retries or compensates", GREEN),
                ("Pick it when", GREY_A, "few nodes, short tx", GREY_A, "many services, long flows", GREY_A),
            ],
            font_size=17,
        )
        table.move_to([0, 0.0, 0])
        self.play(FadeIn(table[0]), Create(table[1]))
        for row in table[2]:
            self.play(FadeIn(row, shift=UP * 0.1), run_time=0.4)
            self.wait(0.3)
        self.play(Indicate(table[0].cells[1], color=TEAL))
        self.play(Indicate(table[0].cells[2], color=ORANGE))
        self._end_scene()

    # ─── Scene 21: Closing ────────────────────────────────────────────
    def scene_closing(self):
        self._header("Takeaways", color=TEAL)
        cards = VGroup(
            self._icon_row_card(ICON_DATABASE, GREEN, "Keep it in one database if you can",
                                "constraints beat protocols"),
            self._icon_row_card(ICON_STRUCTURE, TEAL, "2PC gives you atomicity",
                                "and costs you availability"),
            self._icon_row_card(ICON_SERVER, ORANGE, "Sagas give you availability",
                                "and cost you isolation, so design compensations and idempotency up front"),
        ).arrange(DOWN, buff=0.3, aligned_edge=LEFT).scale(1.25).move_to([0, 0.3, 0])
        for c in cards:
            self.play(FadeIn(c, shift=RIGHT * 0.12), run_time=0.5)
            self.wait(0.6)
        book = make_icon(ICON_BOOK, color=GREY_B, height=0.3)
        refs = make_label("DDIA p.249–251 · 257–260 · 301–304 · 353–364  ·  distributed-transactions-demo/demo/01–07",
                          font_size=10, color=GREY_B)
        foot = VGroup(book, refs).arrange(RIGHT, buff=0.2).move_to([0, -2.8, 0])
        self.play(FadeIn(foot))
        self._end_scene(4)
