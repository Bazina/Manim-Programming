import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from manim import (
    config,
    Scene,
    VGroup,
    RoundedRectangle,
    Rectangle,
    Square,
    Line,
    Arrow,
    DashedLine,
    DashedVMobject,
    Circle,
    VMobject,
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
)

try:
    from manim_slides import Slide as BaseSlide
except Exception:
    BaseSlide = Scene

from libs.ddia_components import (
    DARK_BG,
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
    make_comparison_table,
    make_code_text,
    make_label,
    make_icon,
)
from libs.slide_style import SlideStyleMixin

ICON_KAFKA = "assets/icons/tech/kafka.svg"

config.background_color = "#0D1117"

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

    def _header(self, text, color=TEAL):
        header = self._section_header(text, color=color)
        self.play(AddTextLetterByLetter(header, time_per_char=0.03))
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

    # ─── 2PC stage: coordinator + three participants + log ────────────
    def _twopc_stage(self):
        ys = [2.35, 1.45, 0.55, -0.35]
        rows = VGroup(
            self._row(ICON_STRUCTURE, "Coordinator", ys[0], C_COORD),
            self._row(ICON_DATABASE, "booking_db", ys[1], C_BOOK),
            self._row(ICON_DATABASE, "payment_db", ys[2], C_PAY),
            self._row(ICON_DATABASE, "accounting_db", ys[3], C_ACC),
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
                                  title="saga_log", tag_w=0.8)
            stage.add(log)
        self.play(FadeIn(stage, shift=UP * 0.1))
        return orch, svcs, tables, log

    def _call(self, orch, svc, color, dashed=False, shift=0.0):
        start = orch.get_bottom() + RIGHT * shift + DOWN * 0.05
        end = svc.get_top() + RIGHT * shift + UP * 0.05
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
            d = self._node(ICON_DATABASE, f"{name.lower()}_db", color, icon_h=0.4, font_size=9)
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

    def _schema_card(self, db_name, color, tables, x, top, height, width=4.2):
        """A card per database: table names, one row per column, tags right-aligned.

        tables: [(table_name, [(column, tag, tag_color, dim, enum), ...]), ...]
        Returns (card, refs) where refs maps a column name to its row.
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
            y -= 0.42 if t_i == 0 else 0.55
            tl = make_label(tname, font_size=12, color=WHITE)
            tl.move_to([left + tl.width / 2, y, 0])
            body.add(tl)
            for col, tag, tag_color, dim, enum in cols:
                y -= 0.33
                name = make_label(col, font_size=11, color=GREY_B if dim else GREY_A)
                name.move_to([left + 0.3 + name.width / 2, y, 0])
                row = VGroup(name)
                if tag:
                    tg = make_label(tag, font_size=10, color=GREY_B if dim else tag_color)
                    tg.move_to([right - tg.width / 2, y, 0])
                    row.add(tg)
                body.add(row)
                refs[col] = row
                if enum:
                    y -= 0.28
                    en = make_label(enum, font_size=9, color=GREY_B)
                    en.move_to([left + 0.6 + en.width / 2, y, 0])
                    body.add(en)
                    row.add(en)
        return VGroup(box, title, div, body), refs

    # ─── Scene 2: Schema ──────────────────────────────────────────────
    def scene_schema(self):
        self._header("Schema", color=TEAL)
        specs = [
            ("booking_db", C_BOOK, [
                ("rooms", [
                    ("room_id", "PK", C_BOOK, False, None),
                    ("booked_by", "Part 4", GREY_B, True, None),
                    ("fence_token", "Part 4", GREY_B, True, None),
                ]),
                ("bookings", [
                    ("id", "PK", C_BOOK, False, None),
                    ("room_id", "", None, False, None),
                    ("starts_at, ends_at", "", None, False, None),
                    ("user_id", "", None, False, None),
                    ("status", "", None, False, "PENDING · CONFIRMED · CANCELLED"),
                ]),
            ]),
            ("payment_db", C_PAY, [
                ("wallets", [
                    ("user_id", "PK", C_PAY, False, None),
                    ("balance", "CHECK >= 0", C_PAY, False, None),
                ]),
                ("payments", [
                    ("id", "PK", C_PAY, False, None),
                    ("booking_id", "UNIQUE", C_PAY, False, None),
                    ("amount", "", None, False, None),
                    ("status", "", None, False, "CHARGED · REFUNDED"),
                ]),
            ]),
            ("accounting_db", C_ACC, [
                ("ledger", [
                    ("id", "PK", C_ACC, False, None),
                    ("booking_id", "", None, False, None),
                    ("kind", "", None, False, "REVENUE · REVERSAL"),
                    ("amount", "", None, False, None),
                    ("(booking_id, kind)", "UNIQUE", C_ACC, False, None),
                ]),
            ]),
        ]
        xs = [-4.55, 0.0, 4.55]
        top, height = 2.85, 5.05
        cards, refs = [], []
        for (db, color, tables), x in zip(specs, xs):
            card, r = self._schema_card(db, color, tables, x, top, height)
            cards.append(card)
            refs.append(r)
        append_only = make_label("append only, never deletes", font_size=10, color=GREY_B)
        append_only.move_to([xs[2], top - height + 0.35, 0])
        cards[2].add(append_only)
        for card in cards:
            self.play(FadeIn(card, shift=UP * 0.15), run_time=0.5)
        self._next_slide(phase=True)

        y0 = top - height - 0.4
        notes = [
            (1, "balance", "Payment can say no", C_PAY, [xs[1], y0, 0]),
            (1, "booking_id", "a retry is a no-op", C_PAY, [xs[1], y0 - 0.5, 0]),
            (2, None, "undo = add a REVERSAL", C_ACC, [xs[2], y0, 0]),
        ]
        for idx, key, text, color, pos in notes:
            chip = self._chip(text, color, font_size=10).move_to(pos)
            target = refs[idx][key] if key else append_only
            self.play(Indicate(target, color=color, scale_factor=1.08), FadeIn(chip, shift=UP * 0.1))
            self.wait(0.4)

        later = self._chip("booked_by, fence_token come back in Part 4", GREY_B, font_size=10)
        later.move_to([xs[0], y0, 0])
        self.play(Indicate(refs[0]["booked_by"], color=GREY_A), Indicate(refs[0]["fence_token"], color=GREY_A),
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
            self._chip("Part 1  →  I  on one database", YELLOW, font_size=11),
            self._chip("Parts 2 and 3  →  A  across three databases", TEAL, font_size=11),
            self._chip("Part 4  →  locks across machines", C_LOCK, font_size=11),
        ).arrange(RIGHT, buff=0.3).move_to([0, -3.0, 0])
        self.play(AnimationGroup(*[FadeIn(r, shift=UP * 0.1) for r in roadmap], lag_ratio=0.25))
        self._end_scene()

    # ═════════════════════════════════════════════════════════════════
    # Part 1: One database first (p. 249–260)
    # ═════════════════════════════════════════════════════════════════

    # ─── Scene 3: Write skew ──────────────────────────────────────────
    def scene_write_skew(self):
        self._header("Write Skew: Double Booking", color=RED)
        sub = make_label("REPEATABLE READ (snapshot isolation) · room 101 · 12:00–13:00",
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
            "SELECT count(*) FROM bookings\n"
            " WHERE room_id = 101\n"
            "   AND end_time   > '12:00'\n"
            "   AND start_time < '13:00'\n"
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
        self._next_slide(phase=True)

        self.play(FadeOut(q), FadeOut(arrow), FadeOut(result), FadeOut(empty), FadeOut(nothing), FadeOut(cap))
        table = make_comparison_table(
            col_headers=["Fix", "Idea", "Note"],
            col_colors=[TEAL, GREY_A, GREY_A],
            col_x_positions=[-4.6, -0.6, 4.0],
            rows_data=[
                ("Materialize conflict", GREY_A, "lock the rooms row first", GREY_A,
                 "last resort, leaks into data model", GREY_B),
                ("SERIALIZABLE", GREY_A, "DB detects it, aborts one", GREY_A,
                 "in Postgres this is SSI, not 2PL", GREY_B),
                ("Exclusion constraint", GREEN, "DB rejects overlapping ranges", GREEN,
                 "EXCLUDE USING gist, prod answer", GREEN),
            ],
            header_font_size=13, row_font_size=11, note_font_size=10, row_spacing=0.6,
        )
        table.move_to([0, 0.3, 0])
        self.play(FadeIn(table[0]), Create(table[1]))
        for row in table[2]:
            self.play(FadeIn(row, shift=UP * 0.1), run_time=0.45)
            self.wait(0.3)
        self._play_glow(table[2][-1], GREEN, pad=0.3)
        self._end_scene()

    # ─── Scene 4b: Materializing conflicts ────────────────────────────
    def scene_materialize_conflicts(self):
        self._header("Materializing Conflicts", color=YELLOW)
        sub = make_label("No row to lock? Create rows whose only job is to be locked.", font_size=12, color=GREY_A)
        sub.move_to([0, 2.8, 0])
        self.play(FadeIn(sub))

        # room_slots grid: room 101, 11:00 → 14:00 in 15-minute rows
        times = [f"{11 + i // 4}:{(i % 4) * 15:02d}" for i in range(12)]
        cw, ch, gx0, gy = 0.9, 0.62, -5.4, 0.95
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
        name = make_label("room_slots · room 101", font_size=11, color=C_BOOK)
        name.next_to(cells, UP, buff=0.2).align_to(cells, LEFT)
        self.play(FadeIn(cells, lag_ratio=0.05), FadeIn(labels), FadeIn(name))
        note = make_label("one row per room per 15 minutes, created ahead for the next 6 months. it stores nothing.",
                          font_size=10, color=GREY_B)
        note.move_to([0, -0.35, 0])
        self.play(FadeIn(note))
        self._next_slide(phase=True)

        # T1 locks 12:00–13:00
        t1_sql = self._chip("T1 Alice:  SELECT * FROM room_slots WHERE room_id = 101"
                            "  AND slot >= '12:00' AND slot < '13:00'  FOR UPDATE", C_BOOK, font_size=9)
        t1_sql.move_to([0, -1.05, 0])
        self.play(FadeIn(t1_sql, shift=UP * 0.1))
        t1_idx = range(4, 8)
        t1_locks = VGroup(*[make_icon(ICON_LOCK, color=C_BOOK, height=0.24).move_to(cells[i]) for i in t1_idx])
        self.play(*[cells[i].animate.set_fill(C_BOOK, opacity=0.3).set_stroke(C_BOOK) for i in t1_idx],
                  FadeIn(t1_locks, scale=0.6))
        self._next_slide(phase=True)

        # T2 wants 12:30–13:30 and hits T1's rows
        t2_sql = self._chip("T2 Bob:  same query for 12:30 → 13:30", C_PAY, font_size=9)
        t2_sql.move_to([0, -1.6, 0])
        self.play(FadeIn(t2_sql, shift=UP * 0.1))
        t2_idx = range(6, 10)
        t2_frame = Rectangle(width=cw * 4 + 0.08, height=ch + 0.18, stroke_color=C_PAY, stroke_width=2)
        t2_frame.move_to(VGroup(*[cells[i] for i in t2_idx]).get_center())
        self.play(Create(t2_frame))
        clash = VGroup(*[cells[i] for i in (6, 7)])
        self.play(Indicate(clash, color=RED, scale_factor=1.06))
        wait = self._chip("T2 waits on 12:30 and 12:45", RED)
        wait.next_to(t2_frame, UP, buff=0.12)
        self.play(FadeIn(wait))
        self._next_slide(phase=True)

        # T1 commits, T2 wakes up and re-checks
        steps = VGroup(
            make_label("1. T1 checks bookings (0 overlaps), INSERTs Alice, COMMIT, locks released", font_size=10, color=C_BOOK),
            make_label("2. T2 gets its slot rows, checks bookings again: Alice's row is there", font_size=10, color=C_PAY),
            make_label("3. T2 tells Bob the room is taken. No double booking.", font_size=10, color=GREEN),
        ).arrange(DOWN, buff=0.16, aligned_edge=LEFT).move_to([0, -2.55, 0])
        self.play(FadeIn(steps[0]))
        self.play(FadeOut(t1_locks), *[cells[i].animate.set_fill("#161B22", opacity=1.0).set_stroke(GREY_B)
                                       for i in t1_idx], FadeOut(wait))
        t2_locks = VGroup(*[make_icon(ICON_LOCK, color=C_PAY, height=0.24).move_to(cells[i]) for i in t2_idx])
        self.play(FadeIn(steps[1]), FadeIn(t2_locks, scale=0.6),
                  *[cells[i].animate.set_fill(C_PAY, opacity=0.3).set_stroke(C_PAY) for i in t2_idx])
        self.play(FadeIn(steps[2]))
        rc = make_label("run it in READ COMMITTED, so T2's re-check sees the row T1 just committed",
                        font_size=9, color=YELLOW)
        rc.next_to(steps, DOWN, buff=0.2)
        self.play(FadeIn(rc))
        self._next_slide(phase=True)
        self._clear()

        # the trade-offs
        self._header("Materializing Conflicts: The Catch", color=YELLOW)
        cards = VGroup(
            self._card("Pick the lock size",
                       "One row per room (our rooms row) is simple, but every booking of room 101 waits,\n"
                       "even for a different day. 15-minute slots are precise, but that's 96 rows per room per day.",
                       C_BOOK, width=11.5),
            self._card("Concurrency leaks into the data model",
                       "room_slots holds no business data. It exists only because the database couldn't\n"
                       "lock a range for us. Every new kind of booking needs its own lock table.",
                       C_PAY, width=11.5),
            self._card("Hard to get right, so it's a last resort",
                       "Forget one code path that skips the slot lock and the double booking is back.\n"
                       "Prefer SERIALIZABLE, or an exclusion constraint that the database enforces.",
                       RED, width=11.5),
        ).arrange(DOWN, buff=0.3).move_to([0, -0.2, 0])
        for c in cards:
            self.play(FadeIn(c, shift=UP * 0.1), run_time=0.5)
            self.wait(0.4)
        self._end_scene()

    # ─── Scene 5: Two-phase locking ───────────────────────────────────
    def scene_two_phase_locking(self):
        self._header("Two-Phase Locking (2PL)", color=YELLOW)

        # Phase A: lock modes + compatibility
        s_card = self._card("Shared (S)", "many readers at once", GREEN, width=4.4)
        x_card = self._card("Exclusive (X)", "one writer, nobody else", RED, width=4.4)
        VGroup(s_card, x_card).arrange(DOWN, buff=0.4).move_to([-3.4, 0.4, 0])
        self.play(FadeIn(s_card, shift=RIGHT * 0.1))
        self.play(FadeIn(x_card, shift=RIGHT * 0.1))

        cell = 1.0
        gx, gy = 2.6, 1.0
        grid = VGroup()
        heads = [("held →", GREY_B), ("S", GREEN), ("X", RED)]
        for j, (t, c) in enumerate(heads):
            if j == 0:
                continue
            lbl = make_label(t, font_size=14, color=c)
            lbl.move_to([gx + j * cell, gy + cell, 0])
            grid.add(lbl)
        for i, (t, c) in enumerate([("S", GREEN), ("X", RED)]):
            lbl = make_label(t, font_size=14, color=c)
            lbl.move_to([gx, gy - i * cell, 0])
            grid.add(lbl)
            for j in range(2):
                ok = (i == 0 and j == 0)
                sq = Square(side_length=cell * 0.92, stroke_color=GREEN if ok else RED, stroke_width=1.4,
                            fill_color=GREEN if ok else RED, fill_opacity=0.12)
                sq.move_to([gx + (j + 1) * cell, gy - i * cell, 0])
                mark = make_label("ok" if ok else "wait", font_size=11, color=GREEN if ok else RED)
                mark.move_to(sq.get_center())
                grid.add(sq, mark)
        want = make_label("want ↓   held →", font_size=9, color=GREY_B)
        want.move_to([gx + 1.0, gy + 1.55, 0])
        self.play(FadeIn(grid), FadeIn(want))
        cap = self._caption("Writers block readers and readers block writers.", y=-2.6, font_size=12)
        self.play(FadeIn(cap))
        self._next_slide(phase=True)
        self.play(FadeOut(VGroup(s_card, x_card, grid, want, cap)))

        # Phase B: growing / shrinking chart
        ox, oy = -4.5, -1.8
        x_axis = Arrow([ox, oy, 0], [4.8, oy, 0], buff=0, stroke_width=1.6, color=GREY_B, tip_length=0.14)
        y_axis = Arrow([ox, oy, 0], [ox, 2.2, 0], buff=0, stroke_width=1.6, color=GREY_B, tip_length=0.14)
        x_lbl = make_label("time", font_size=10, color=GREY_B).next_to(x_axis, DOWN, buff=0.1).align_to(x_axis, RIGHT)
        y_lbl = make_label("locks held", font_size=10, color=GREY_B).next_to(y_axis, UP, buff=0.1)
        pts = [(0, 0), (1, 0), (1, 1), (2.2, 1), (2.2, 2), (3.4, 2), (3.4, 3), (4.6, 3), (4.6, 4), (6.8, 4), (6.8, 0), (8.6, 0)]
        sx, sy = 1.0, 0.85
        curve = VMobject(stroke_color=YELLOW, stroke_width=3)
        curve.set_points_as_corners([[ox + x * sx, oy + y * sy, 0] for x, y in pts])
        commit_x = ox + 6.8 * sx
        commit = DashedLine([commit_x, oy, 0], [commit_x, 2.0, 0], dash_length=0.1, color=GREEN, stroke_width=1.4)
        commit_lbl = make_label("COMMIT", font_size=11, color=GREEN).next_to(commit, UP, buff=0.08)
        grow_lbl = make_label("phase 1: growing\n(acquire while running)", font_size=10, color=YELLOW)
        grow_lbl.move_to([ox + 2.4, oy + 3.4 * sy + 0.9, 0])
        shrink_lbl = make_label("phase 2: shrinking\n(release all at the end)", font_size=10, color=GREEN)
        shrink_lbl.next_to(commit, RIGHT, buff=0.2).shift(DOWN * 0.8)
        self.play(GrowArrow(x_axis), GrowArrow(y_axis), FadeIn(x_lbl), FadeIn(y_lbl))
        self.play(Create(curve), run_time=2.2)
        self.play(FadeIn(grow_lbl))
        self.play(Create(commit), FadeIn(commit_lbl), FadeIn(shrink_lbl))
        self._next_slide(phase=True)
        self.play(FadeOut(VGroup(x_axis, y_axis, x_lbl, y_lbl, curve, commit, commit_lbl, grow_lbl, shrink_lbl)))

        # Phase C: predicate lock → index-range lock
        ly = 0.4
        tl = Line([-5.0, ly, 0], [5.0, ly, 0], stroke_color=GREY_B, stroke_width=2)
        room_lbl = make_label("room 101", font_size=12, color=C_BOOK).next_to(tl, LEFT, buff=0.2)
        ticks = VGroup()
        for i, h in enumerate(["10:00", "11:00", "12:00", "13:00", "14:00", "15:00"]):
            x = -5.0 + i * 2.0
            ticks.add(Line([x, ly - 0.1, 0], [x, ly + 0.1, 0], stroke_color=GREY_B, stroke_width=1.2))
            ticks.add(make_label(h, font_size=9, color=GREY_B).move_to([x, ly - 0.35, 0]))
        pred = Rectangle(width=2.0, height=0.5, fill_color=YELLOW, fill_opacity=0.25, stroke_color=YELLOW, stroke_width=1.2)
        pred.move_to([0.0, ly, 0])
        pred_lbl = make_label("T1 searched 12:00–13:00  →  shared predicate lock", font_size=10, color=YELLOW)
        pred_lbl.move_to([0, ly + 0.75, 0])
        self.play(Create(tl), FadeIn(room_lbl), FadeIn(ticks))
        self.play(FadeIn(pred), FadeIn(pred_lbl))

        ins = self._chip("T2 INSERT 12:30–13:30", C_PAY, font_size=10)
        ins.move_to([1.0, -1.6, 0])
        ins_arrow = Arrow(ins.get_top(), [1.0, ly - 0.3, 0], buff=0.05, stroke_width=2, color=C_PAY, tip_length=0.14)
        self.play(FadeIn(ins))
        self.play(GrowArrow(ins_arrow))
        stop = make_label("waits", font_size=11, color=RED).next_to(ins_arrow, RIGHT, buff=0.15)
        self.play(Wiggle(ins_arrow), FadeIn(stop))
        cap = self._caption("The lock covers rows that don't exist yet.", y=-2.6, font_size=12)
        self.play(FadeIn(cap))
        self._next_slide(phase=True)

        wide = Rectangle(width=10.0, height=0.5, fill_color=YELLOW, fill_opacity=0.18, stroke_color=YELLOW, stroke_width=1.2)
        wide.move_to([0, ly, 0])
        wide_lbl = make_label("index-range lock on room_id = 101  (all times)", font_size=10, color=YELLOW)
        wide_lbl.move_to(pred_lbl)
        cap2 = self._caption("Index-range lock: safe because it locks more, not less.", y=-2.6, font_size=12)
        self.play(Transform(pred, wide), Transform(pred_lbl, wide_lbl), Transform(cap, cap2))
        self._next_slide(phase=True)
        self.play(FadeOut(VGroup(tl, room_lbl, ticks, pred, pred_lbl, ins, ins_arrow, stop, cap)))

        # Phase D: deadlock
        t1 = self._flow_node("T1", C_BOOK, width=1.6, height=0.7).move_to([-3.0, 1.2, 0])
        t2 = self._flow_node("T2", C_PAY, width=1.6, height=0.7).move_to([3.0, 1.2, 0])
        ra = self._flow_node("row A", GREY_A, width=1.6, height=0.7).move_to([-3.0, -1.2, 0])
        rb = self._flow_node("row B", GREY_A, width=1.6, height=0.7).move_to([3.0, -1.2, 0])
        self.play(FadeIn(VGroup(t1, t2, ra, rb)))
        h1 = Arrow(t1.get_bottom(), ra.get_top(), buff=0.1, stroke_width=2, color=GREEN, tip_length=0.14)
        h2 = Arrow(t2.get_bottom(), rb.get_top(), buff=0.1, stroke_width=2, color=GREEN, tip_length=0.14)
        hl1 = make_label("holds", font_size=9, color=GREEN).next_to(h1, LEFT, buff=0.1)
        hl2 = make_label("holds", font_size=9, color=GREEN).next_to(h2, RIGHT, buff=0.1)
        self.play(GrowArrow(h1), GrowArrow(h2), FadeIn(hl1), FadeIn(hl2))
        w1 = self._dashed_arrow(t1.get_right() + DOWN * 0.1, rb.get_left() + UP * 0.1, RED)
        w2 = self._dashed_arrow(t2.get_left() + DOWN * 0.1, ra.get_right() + UP * 0.1, RED)
        wl = make_label("waits for", font_size=9, color=RED).move_to([0, 0.35, 0])
        self.play(Create(w1), Create(w2), FadeIn(wl))
        dl = make_label("deadlock", font_size=16, color=RED).move_to([0, -0.4, 0])
        self.play(FadeIn(dl, scale=0.8))
        self._next_slide(phase=True)
        abort = make_label("aborted, retry", font_size=11, color=RED).next_to(t2, UP, buff=0.15)
        self.play(t2[0].animate.set_stroke(RED), t2[1].animate.set_color(RED), FadeIn(abort), FadeOut(w2), FadeOut(h2), FadeOut(hl2))
        cap = self._caption("The database detects the cycle and aborts one transaction.", y=-2.4, font_size=12)
        self.play(FadeIn(cap))
        self._next_slide(phase=True)
        self.play(FadeOut(VGroup(t1, t2, ra, rb, h1, hl1, w1, wl, dl, abort, cap)))

        # Phase E: 2PL ≠ 2PC callout
        callout = self._card(
            "2PL ≠ 2PC",
            "2PL gives isolation on one database.\n2PC gives atomic commit across many.",
            TEAL, width=8.0, title_size=22, desc_size=13, align="center",
        )
        callout.move_to([0, 0.5, 0])
        glow = create_rect_glow(callout[0], color=TEAL, max_opacity=0.15)
        self.play(FadeIn(glow), FadeIn(callout, scale=0.95))
        line = make_label("Locks are held until commit.", font_size=18, color=YELLOW)
        line.move_to([0, -1.6, 0])
        self.play(AddTextLetterByLetter(line, time_per_char=0.04))
        self.play(Circumscribe(line, color=YELLOW))
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
            "  WHERE user_id = 'alice';",
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
        specs = [("booking_db", C_BOOK, "booking"), ("payment_db", C_PAY, "wallet · payment"),
                 ("accounting_db", C_ACC, "ledger")]
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
        specs = [("booking_db", C_BOOK), ("payment_db", C_PAY), ("accounting_db", C_ACC)]
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
        self._header("2PC: Happy Path", color=TEAL)
        rows, ys, log = self._twopc_stage()
        yc, yp = ys[0], ys[1:]

        begin = self._chip("begin gid=bk-7f2", C_COORD)
        begin.move_to([_tx(0.55), yc + 0.35, 0])
        self.play(FadeIn(begin))
        self._log(log, "COORD", "begin gid=bk-7f2", C_COORD)

        self._fan(0.3, yc, 1.2, yp, GREY_A)
        self._log(log, "BOOKING", "INSERT booking CONFIRMED", C_BOOK)
        self._log(log, "PAYMENT", "UPDATE wallet -120, INSERT payment", C_PAY)
        self._log(log, "ACCOUNT", "INSERT ledger REVENUE 120", C_ACC)
        bars = self._start_bars(1.2, yp, [C_BOOK, C_PAY, C_ACC])
        lock_lbl = make_label("locks held", font_size=10, color=GREY_A)
        lock_lbl.move_to([_tx(1.9), yp[-1] - 0.3, 0])
        self.play(*self._grow_bars(bars, 2.5), FadeIn(lock_lbl), run_time=0.6)
        self._next_slide(phase=True)

        # phase 1: prepare
        p1 = make_label("phase 1", font_size=9, color=C_COORD).move_to([_tx(3.0), yc + 0.62, 0])
        self.play(FadeIn(p1))
        self._fan(2.5, yc, 3.2, yp, C_COORD, label="prepare", extra=self._grow_bars(bars, 3.2))
        yes = VGroup(*[self._arr(3.5, y, 4.2, yc, GREEN) for y in yp])
        self.play(*[GrowArrow(a) for a in yes], *self._grow_bars(bars, 4.2), run_time=0.6)
        yes_lbl = make_label("yes ×3", font_size=10, color=GREEN).move_to([_tx(4.3), yc - 0.25, 0])
        self.play(FadeIn(yes_lbl))
        self._log(log, "ALL", "PREPARE TRANSACTION 'bk-7f2'  →  yes", GREEN)
        self._next_slide(phase=True)

        # commit point
        disk = make_icon(ICON_DATABASE, color=C_COORD, height=0.3)
        disk.move_to([_tx(4.7), yc, 0])
        cp = make_label("commit point", font_size=10, color=YELLOW).next_to(disk, UP, buff=0.3)
        self.play(FadeIn(disk, scale=0.6), *self._grow_bars(bars, 5.1))
        self._play_glow(disk, YELLOW, pad=0.25)
        self.play(FadeIn(cp))
        self._log(log, "COORD", "tx_log bk-7f2 = COMMIT   (fsync)", YELLOW, text_color=YELLOW)
        self._next_slide(phase=True)

        # phase 2: commit
        p2 = make_label("phase 2", font_size=9, color=GREEN).move_to([_tx(5.6), yc + 0.62, 0])
        self.play(FadeIn(p2))
        self._fan(5.1, yc, 6.0, yp, GREEN, label="commit", extra=self._grow_bars(bars, 6.0))
        self._log(log, "ALL", "COMMIT PREPARED 'bk-7f2'  →  locks released", GREEN)
        done = [make_icon(ICON_CHECK, color=GREEN, height=0.22).move_to([_tx(6.35), y, 0]) for y in yp]
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
        self._header("2PC: One Participant Says No", color=RED)
        rows, ys, log = self._twopc_stage()
        yc, yp = ys[0], ys[1:]
        self._log(log, "COORD", "begin gid=bk-8a1   (Bob, balance 50)", C_COORD)
        self._fan(0.3, yc, 1.2, yp, GREY_A)
        bars = self._start_bars(1.2, yp, [C_BOOK, C_PAY, C_ACC])
        self.play(*self._grow_bars(bars, 2.0), run_time=0.5)
        self._fan(2.0, yc, 2.8, yp, C_COORD, label="prepare", extra=self._grow_bars(bars, 2.8))
        replies = [
            self._arr(3.1, yp[0], 3.8, yc, GREEN),
            self._arr(3.1, yp[1], 3.8, yc, RED),
            self._arr(3.1, yp[2], 3.8, yc, GREEN),
        ]
        self.play(*[GrowArrow(a) for a in replies], *self._grow_bars(bars, 3.8), run_time=0.6)
        no = make_label("no", font_size=10, color=RED).move_to([_tx(3.2), yp[1] + 0.3, 0])
        self.play(FadeIn(no), Indicate(rows[2], color=RED))
        self._log(log, "BOOKING", "PREPARE  →  yes", C_BOOK)
        self._log(log, "PAYMENT", "CHECK violation, balance 50 < 120  →  no", RED, text_color=RED)
        self._log(log, "ACCOUNT", "PREPARE  →  yes", C_ACC)
        self._next_slide(phase=True)

        self._log(log, "COORD", "tx_log bk-8a1 = ABORT", RED, text_color=RED)
        self.play(*self._grow_bars(bars, 4.3), run_time=0.3)
        self._fan(4.3, yc, 5.1, yp, RED, label="abort", extra=self._grow_bars(bars, 5.1))
        self._log(log, "ALL", "ROLLBACK PREPARED 'bk-8a1'", RED)
        self.play(*[b.animate.set_fill(opacity=0.06) for b in bars])
        badge = self._verdict_badge("Nothing happened anywhere  ✓", GREEN, width=5.5)
        badge.move_to([_tx(7.0), 1.0, 0])
        self.play(FadeIn(badge, shift=UP * 0.1))
        cap = make_label("atomicity doing its job", font_size=10, color=GREY_B).next_to(badge, DOWN, buff=0.15)
        self.play(FadeIn(cap))
        self._end_scene()

    # ─── Scene 9: 2PC coordinator crash ───────────────────────────────
    def scene_2pc_coordinator_crash(self):
        self._header("2PC: The Coordinator Crashes", color=RED)
        rows, ys, log = self._twopc_stage()
        yc, yp = ys[0], ys[1:]
        colors = [C_BOOK, C_PAY, C_ACC]
        self._fan(0.2, yc, 0.9, yp, GREY_A)
        bars = self._start_bars(0.9, yp, colors)
        self.play(*self._grow_bars(bars, 1.4), run_time=0.5)
        self._fan(1.4, yc, 2.1, yp, C_COORD, label="prepare", extra=self._grow_bars(bars, 2.1))
        yes = VGroup(*[self._arr(2.4, y, 3.1, yc, GREEN) for y in yp])
        self.play(*[GrowArrow(a) for a in yes], *self._grow_bars(bars, 3.1), run_time=0.5)
        self._log(log, "ALL", "PREPARE TRANSACTION 'bk-9c4'  →  yes", GREEN)
        self._next_slide(phase=True)

        bomb = make_icon(ICON_BOMB, color=RED, height=0.42).move_to([_tx(3.6), yc, 0])
        self.play(FadeIn(bomb, scale=1.4), rows[0].animate.set_opacity(0.3), *self._grow_bars(bars, 3.6))
        self._log(log, "COORD", "crashed before writing a decision", RED, text_color=RED)

        chips = VGroup(*[self._chip("IN DOUBT", YELLOW).move_to([_tx(4.3), y + 0.3, 0]) for y in yp])
        self.play(*[FadeIn(c, scale=0.8) for c in chips])
        tracker = ValueTracker(0)
        clock_icon = make_icon(ICON_STOPWATCH, color=YELLOW, height=0.3).move_to([4.2, yc, 0])
        clock = always_redraw(lambda: make_label(
            f"in doubt  {int(tracker.get_value()) // 60:02d}:{int(tracker.get_value()) % 60:02d}",
            font_size=11, color=YELLOW,
        ).next_to(clock_icon, RIGHT, buff=0.15))
        self.add(clock_icon, clock)
        self.play(tracker.animate.set_value(1200), *self._grow_bars(bars, 8.3), run_time=3.0)
        self._next_slide(phase=True)

        # a new transaction blocks
        t2 = self._chip("T2: UPDATE wallets u1", GREY_A)
        t2.move_to([_tx(5.6), yp[1] - 0.42, 0])
        t2_arrow = Arrow(t2.get_top(), [_tx(5.6), yp[1] - 0.12, 0], buff=0.02, stroke_width=1.8,
                         color=RED, tip_length=0.12)
        blocked = make_label("blocked", font_size=9, color=RED).next_to(t2, RIGHT, buff=0.15)
        self.play(FadeIn(t2), GrowArrow(t2_arrow))
        self.play(Wiggle(t2_arrow), FadeIn(blocked))
        self._log(log, "PAYMENT", "T2 UPDATE wallets ... waiting for lock", C_PAY)
        self._log(log, "PAYMENT", "timeout? can't abort, can't commit, it doesn't know", YELLOW, text_color=YELLOW)
        self._next_slide(phase=True)

        # restart payment_db
        pay_icon = rows[2].icon
        self.play(pay_icon.animate.set_opacity(0.1), run_time=0.4)
        self.play(pay_icon.animate.set_opacity(1.0), run_time=0.4)
        self.play(Indicate(chips[1], color=YELLOW), Indicate(bars[1], color=C_PAY))
        self._log(log, "PAYMENT", "restarted, bk-9c4 still in pg_prepared_xacts, lock still held", C_PAY)
        self._next_slide(phase=True)

        self.play(FadeOut(log, *log.lines))
        l1 = make_label("Locks are held until commit.", font_size=16, color=YELLOW)
        l2 = make_label("… and commit is waiting on a dead coordinator.", font_size=16, color=RED)
        VGroup(l1, l2).arrange(DOWN, buff=0.25).move_to([0, -2.4, 0])
        self.play(FadeIn(l1))
        self.play(AddTextLetterByLetter(l2, time_per_char=0.03))
        self._end_scene()

    # ─── Scene 10: 2PC recovery + heuristic ───────────────────────────
    def scene_2pc_recovery(self):
        self._header("2PC: Recovery", color=TEAL)
        rows, ys, log = self._twopc_stage()
        yc, yp = ys[0], ys[1:]

        back = self._chip("coordinator back, reads tx_log", C_COORD)
        back.move_to([_tx(1.3), yc + 0.38, 0])
        self.play(FadeIn(back))

        # Case 1: no decision → abort
        self._log(log, "COORD", "case 1: tx_log has no decision for bk-9c4", C_COORD)
        case1 = self._fan(0.4, yc, 1.3, yp, RED, label="abort")
        self._log(log, "ALL", "ROLLBACK PREPARED 'bk-9c4'   (no record means abort)", RED)
        self._next_slide(phase=True)
        self.play(FadeOut(case1))

        # Case 2: COMMIT logged, only booking got it
        self._log(log, "COORD", "case 2: tx_log bk-7f2 = COMMIT, only booking got it", YELLOW, text_color=YELLOW)
        c_book = self._chip("CONFIRMED", GREEN).move_to([_tx(3.2), yp[0] + 0.3, 0])
        c_pay = self._chip("IN DOUBT", YELLOW).move_to([_tx(3.2), yp[1] + 0.3, 0])
        c_acc = self._chip("IN DOUBT", YELLOW).move_to([_tx(3.2), yp[2] + 0.3, 0])
        self.play(FadeIn(c_book), FadeIn(c_pay), FadeIn(c_acc))
        mid = self._chip("booking visible, payment not yet: atomic commit, not atomic visibility", YELLOW, font_size=9)
        mid.move_to([_tx(6.3), yc + 0.38, 0])
        self.play(FadeIn(mid, shift=DOWN * 0.1))
        self._next_slide(phase=True)
        self.play(FadeOut(mid))
        commits = VGroup(self._arr(4.4, yc, 5.2, yp[1], GREEN), self._arr(4.4, yc, 5.2, yp[2], GREEN))
        self.play(*[GrowArrow(a) for a in commits])
        self.play(Transform(c_pay, self._chip("CONFIRMED", GREEN).move_to(c_pay)),
                  Transform(c_acc, self._chip("CONFIRMED", GREEN).move_to(c_acc)))
        self._log(log, "ALL", "COMMIT PREPARED 'bk-7f2'   (the decision is final)", GREEN)
        self._next_slide(phase=True)
        self._clear()

        # Heuristic decision
        self._header("The Escape Hatch: Heuristic Decisions", color=RED)
        rows, ys, log = self._twopc_stage()
        yc, yp = ys[0], ys[1:]
        c_book = self._chip("committed", GREEN).move_to([_tx(0.8), yp[0] + 0.3, 0])
        c_pay = self._chip("IN DOUBT", YELLOW).move_to([_tx(0.8), yp[1] + 0.3, 0])
        c_acc = self._chip("IN DOUBT", YELLOW).move_to([_tx(0.8), yp[2] + 0.3, 0])
        self.play(FadeIn(c_book), FadeIn(c_pay), FadeIn(c_acc))

        admin = self._node(ICON_USER, "admin", GREY_A, icon_h=0.3, font_size=9)
        admin.move_to([_tx(2.4), (yp[1] + yp[2]) / 2 - 0.05, 0])
        self.play(FadeIn(admin))
        rb = self._chip("ROLLBACK PREPARED", RED).next_to(admin, RIGHT, buff=0.2)
        self.play(FadeIn(rb, shift=RIGHT * 0.1))
        self.play(Transform(c_pay, self._chip("rolled back", RED).move_to(c_pay)))
        self._log(log, "ADMIN", "payment_db: ROLLBACK PREPARED 'bk-7f2'   (by hand)", RED, text_color=RED)
        self._next_slide(phase=True)

        a = self._arr(4.6, yc, 5.4, yp[1], GREEN)
        back = self._arr(5.6, yp[1], 6.4, yc, RED)
        self.play(GrowArrow(a))
        self.play(GrowArrow(back))
        dne = make_label("does not exist", font_size=9, color=RED).move_to(back.get_center() + RIGHT * 0.75)
        self.play(FadeIn(dne))
        self._log(log, "COORD", "COMMIT PREPARED on payment_db  →  does not exist", RED, text_color=RED)
        self._next_slide(phase=True)

        self.play(FadeOut(log, *log.lines))
        end = VGroup(
            self._chip("booking CONFIRMED", GREEN, font_size=11),
            self._chip("ledger REVENUE", GREEN, font_size=11),
            self._chip("payment: none", RED, font_size=11),
        ).arrange(RIGHT, buff=0.35).move_to([0, -1.9, 0])
        self.play(AnimationGroup(*[FadeIn(c, shift=UP * 0.1) for c in end], lag_ratio=0.2))
        self.play(*[Indicate(c, color=RED) for c in end])
        cap = self._caption('"Heuristic" is a polite word for "probably broke atomicity".',
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
        foot = make_label("XA / JTA is the standard API for this: Postgres, MySQL, ActiveMQ … (remember the JMS lab)",
                          font_size=10, color=GREY_B)
        foot.move_to([0, -3.5, 0])
        self.play(FadeIn(foot))
        self._end_scene()

    # ═════════════════════════════════════════════════════════════════
    # Part 3: Saga
    # ═════════════════════════════════════════════════════════════════

    # ─── Scene 12: Saga intro ─────────────────────────────────────────
    def scene_saga_intro(self):
        self._header("Saga", color=ORANGE)
        orch, svcs, tables, log = self._saga_stage(with_log=True)
        cap = self._caption("Each service commits its own local transaction right away.",
                            y=-2.3, font_size=12)
        self.play(FadeIn(cap))
        self._log(log, "log", "one line per step", GREY_A)
        self._next_slide(phase=True)
        self._clear()

        self._header("Steps and Compensations", color=ORANGE)
        table = make_comparison_table(
            col_headers=["Step", "Service", "Action", "Compensation"],
            col_colors=[GREY_B, GREY_B, GREEN, RED],
            col_x_positions=[-5.4, -3.4, 0.0, 4.2],
            rows_data=[
                ("1", GREY_A, "Booking", C_BOOK, "INSERT booking PENDING", GREY_A, "set CANCELLED", GREY_A),
                ("2", GREY_A, "Payment", C_PAY, "charge $120", GREY_A, "refund, set REFUNDED", GREY_A),
                ("3", GREY_A, "Accounting", C_ACC, "ledger REVENUE", GREY_A, "ledger REVERSAL", GREY_A),
                ("4", GREY_A, "Booking", C_BOOK, "set CONFIRMED", GREY_A, "none, this is the end", GREY_B),
            ],
            header_font_size=13, row_font_size=12, note_font_size=12, row_spacing=0.6,
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

    def _saga_step(self, orch, svc, table, log, step, row_text, color, log_text=None):
        a = self._call(orch, svc, color)
        self._add_row(table, row_text, color)
        self._log(log, f"step {step}", log_text or "done", color)
        self.play(FadeOut(a), run_time=0.25)

    # ─── Scene 13: Saga happy path ────────────────────────────────────
    def scene_saga_happy_path(self):
        self._header("Saga: Happy Path", color=ORANGE)
        orch, svcs, tables, log = self._saga_stage()
        self._saga_step(orch, svcs[0], tables[0], log, 1, "bk-7f2 PENDING", YELLOW, "booking PENDING")
        self._saga_step(orch, svcs[1], tables[1], log, 2, "bk-7f2 CHARGED 120", C_PAY, "payment CHARGED")
        self._saga_step(orch, svcs[2], tables[2], log, 3, "bk-7f2 REVENUE 120", C_ACC, "ledger REVENUE")
        a = self._call(orch, svcs[0], GREEN, shift=0.3)
        self.play(self._swap_row(tables[0], 0, "bk-7f2 CONFIRMED", GREEN))
        self._log(log, "step 4", "booking CONFIRMED", GREEN)
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
        self._saga_step(orch, svcs[0], tables[0], log, 1, "bk-8a1 PENDING", YELLOW, "booking PENDING")
        a = self._call(orch, svcs[1], C_PAY)
        self._mark(svcs[1], ok=False)
        why = make_label("balance 50 < 120", font_size=9, color=RED).next_to(tables[1].div, DOWN, buff=0.15)
        self.play(FadeIn(why))
        self._log(log, "step 2", "FAILED, compensate", RED, text_color=RED)
        self.play(FadeOut(a))
        self._next_slide(phase=True)
        self._call(orch, svcs[0], RED, dashed=True, shift=-0.3)
        self.play(self._swap_row(tables[0], 0, "bk-8a1 CANCELLED", RED))
        self._log(log, "undo 1", "booking CANCELLED", RED)
        cap = self._caption("Final: booking CANCELLED, no payment, no ledger row.", y=-2.4, font_size=12)
        self.play(FadeIn(cap))
        self._next_slide(phase=True)
        self._clear()

        self._header("Saga: Accounting Is Down", color=RED)
        orch, svcs, tables, log = self._saga_stage(greyed="Accounting")
        down = make_label("unreachable", font_size=9, color=RED).next_to(svcs[2], DOWN, buff=0.08)
        self.play(FadeIn(down))
        self._saga_step(orch, svcs[0], tables[0], log, 1, "bk-5e0 PENDING", YELLOW, "booking PENDING")
        self._saga_step(orch, svcs[1], tables[1], log, 2, "bk-5e0 CHARGED 120", C_PAY, "payment CHARGED")
        a = self._call(orch, svcs[2], GREY_B)
        self._mark(svcs[2], ok=False)
        self._log(log, "step 3", "FAILED, compensate", RED, text_color=RED)
        self.play(FadeOut(a))
        self._next_slide(phase=True)
        self._call(orch, svcs[1], RED, dashed=True, shift=-0.3)
        self.play(self._swap_row(tables[1], 0, "bk-5e0 REFUNDED", RED))
        self._log(log, "undo 2", "payment REFUNDED", RED)
        self._call(orch, svcs[0], RED, dashed=True, shift=-0.3)
        self.play(self._swap_row(tables[0], 0, "bk-5e0 CANCELLED", RED))
        self._log(log, "undo 1", "booking CANCELLED", RED)
        cap = self._caption("Undo in reverse order.", color=ORANGE, y=-2.4, font_size=15)
        self.play(FadeIn(cap))
        self._end_scene()

    # ─── Scene 15: Saga crash + duplicate ─────────────────────────────
    def scene_saga_crash_and_retry(self):
        self._header("Saga: The Orchestrator Crashes", color=ORANGE)
        orch, svcs, tables, log = self._saga_stage()
        self._saga_step(orch, svcs[0], tables[0], log, 1, "bk-3d9 PENDING", YELLOW, "booking PENDING")
        self._saga_step(orch, svcs[1], tables[1], log, 2, "bk-3d9 CHARGED 120", C_PAY, "payment CHARGED")
        bomb = make_icon(ICON_BOMB, color=RED, height=0.4).next_to(orch, RIGHT, buff=0.2)
        self.play(FadeIn(bomb, scale=1.4), orch.animate.set_opacity(0.3))
        self._log(log, "crash", "orchestrator died", RED, text_color=RED)
        self._next_slide(phase=True)

        self.play(FadeOut(bomb), orch.animate.set_opacity(1.0))
        self._log(log, "resume", "last: step 2 done", C_COORD)
        self.play(Indicate(log.lines[-2], color=C_PAY), Indicate(log.lines[-1], color=C_COORD))
        self._saga_step(orch, svcs[2], tables[2], log, 3, "bk-3d9 REVENUE 120", C_ACC, "ledger REVENUE")
        a = self._call(orch, svcs[0], GREEN, shift=0.3)
        self.play(self._swap_row(tables[0], 0, "bk-3d9 CONFIRMED", GREEN))
        self._log(log, "step 4", "booking CONFIRMED", GREEN)
        self.play(FadeOut(a))
        cap = self._caption("The saga log is what lets us resume.", y=-2.4, font_size=13)
        self.play(FadeIn(cap))
        self._next_slide(phase=True)
        self.play(FadeOut(cap))

        # duplicate message
        dup_lbl = make_label("step 2 delivered again", font_size=9, color=C_PAY)
        dup_lbl.next_to(svcs[1], UP, buff=0.55).shift(RIGHT * 1.2)
        self._call(orch, svcs[1], C_PAY, shift=0.15)
        self.play(FadeIn(dup_lbl))
        bounce = self._dashed_arrow(svcs[1].get_top() + LEFT * 0.25 + UP * 0.05,
                                    orch.get_bottom() + LEFT * 0.25 + DOWN * 0.05, GREY_B)
        self.play(Create(bounce))
        uniq = make_label("booking_id UNIQUE", font_size=9, color=GREY_B).next_to(tables[1].rows[0], DOWN, buff=0.12)
        uniq.align_to(tables[1].rows[0], LEFT)
        self.play(FadeIn(uniq), Indicate(tables[1].rows[0], color=GREY_A))
        self._log(log, "step 2", "already charged, no-op", GREY_B)
        cap = self._caption("Every step and every compensation must be idempotent. (Idempotent Receiver, sheet 6)",
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

        for i, (txt, c) in enumerate([("bk-6b2 PENDING", YELLOW), ("bk-6b2 CHARGED 120", C_PAY),
                                      ("bk-6b2 REVENUE 120", C_ACC)]):
            a = self._call(orch, svcs[i], c)
            self._add_row(tables[i], txt, c)
            self.play(FadeOut(a), run_time=0.2)
        self._next_slide(phase=True)

        look = self._dashed_arrow(reader.get_left() + LEFT * 0.05, tables[2].get_right() + RIGHT * 0.05, GREY_A)
        self.play(Create(look))
        self.play(Transform(report, self._chip("revenue today: +$120", GREEN, font_size=10).move_to(report)))
        self._next_slide(phase=True)

        a = self._call(orch, svcs[0], RED, shift=0.3)
        fail = make_label("step 4 fails: room closed for maintenance", font_size=9, color=RED)
        fail.move_to([_COLS[0], 2.35, 0])
        self.play(FadeIn(fail), FadeOut(a))
        self._call(orch, svcs[2], RED, dashed=True, shift=-0.3)
        self._add_row(tables[2], "bk-6b2 REVERSAL -120", RED)
        self._call(orch, svcs[1], RED, dashed=True, shift=-0.3)
        self.play(self._swap_row(tables[1], 0, "bk-6b2 REFUNDED", RED))
        self._call(orch, svcs[0], RED, dashed=True, shift=-0.3)
        self.play(self._swap_row(tables[0], 0, "bk-6b2 CANCELLED", RED))
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
        self._add_row(tables[0], "Alice 101 PENDING", YELLOW)
        self.play(FadeOut(a))
        bob = self._node(ICON_USER, "Bob", GREY_A, icon_h=0.4)
        bob.move_to([-6.45, 0.85, 0])
        self.play(FadeIn(bob))
        try_arrow = Arrow(bob.get_right(), svcs[0].get_left(), buff=0.2, stroke_width=1.8,
                          color=GREY_A, tip_length=0.14)
        bob_req = make_label("room 101", font_size=9, color=GREY_A).next_to(try_arrow, UP, buff=0.08)
        self.play(GrowArrow(try_arrow), FadeIn(bob_req))
        rej = make_label("rejected: overlaps a PENDING booking", font_size=10, color=RED)
        rej.next_to(tables[0], DOWN, buff=0.15).align_to(tables[0], LEFT)
        self.play(Wiggle(try_arrow), try_arrow.animate.set_color(RED), FadeIn(rej))
        code = make_code_text(
            "EXCLUDE USING gist (\n  room_id WITH =,\n  tstzrange(starts_at, ends_at) WITH &&\n) WHERE (status <> 'CANCELLED')",
            font_size=10, language="sql", force_code_object=True, glow=False,
        )
        code.move_to([1.2, -2.6, 0])
        self.play(FadeIn(code))
        cap = make_label("PENDING acts as our lock.", font_size=14, color=GREEN)
        cap.next_to(code, RIGHT, buff=0.4)
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
        pm = make_label("Process Manager pattern (sheet 6)", font_size=9, color=GREY_B).move_to([-3.6, -0.75, 0])
        self.play(Create(div), FadeIn(lt))
        self.play(FadeIn(o), FadeIn(ls))
        self.play(*[GrowArrow(a) for a in la])
        self.play(FadeIn(pm))
        self._next_slide(phase=True)

        # right: choreography
        rt = make_label("Choreography", font_size=14, color=C_PAY).move_to([3.6, 2.5, 0])
        kafka = make_icon(ICON_KAFKA, color=WHITE, height=0.4).move_to([1.0, 1.35, 0])
        topic = RoundedRectangle(corner_radius=0.08, width=5.0, height=0.5, stroke_color=GREY_B,
                                 stroke_width=1.2, fill_color="#161B22", fill_opacity=0.95)
        topic.move_to([4.2, 1.35, 0])
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
        kl = make_label("events over Kafka (lab 4)", font_size=9, color=GREY_B).move_to([3.6, -0.75, 0])
        self.play(FadeIn(rt))
        self.play(FadeIn(kafka), FadeIn(topic), FadeIn(rs))
        self.play(AnimationGroup(*[FadeIn(e, shift=RIGHT * 0.1) for e in evs], lag_ratio=0.4), Create(ra))
        self.play(FadeIn(kl))
        self._next_slide(phase=True)

        table = make_comparison_table(
            col_headers=["", "Orchestration", "Choreography"],
            col_colors=[GREY_B, C_COORD, C_PAY],
            col_x_positions=[-3.8, 0.2, 3.9],
            rows_data=[
                ("where the flow lives", GREY_A, "one place", GREY_A, "spread across services", GREY_A),
                ("easy to follow", GREY_A, "yes", GREEN, "harder as steps grow", GREY_A),
                ("coupling", GREY_A, "services know the orchestrator", GREY_A, "services only know events", GREY_A),
            ],
            header_font_size=12, row_font_size=10, note_font_size=10, row_spacing=0.42,
        )
        table.move_to([0, -2.25, 0])
        self.play(FadeIn(table))
        foot = make_label("Messages that can't be retried go to a Dead Letter Channel (sheet 6).",
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
            self._row(ICON_SERVER, "instance A", ys[0], C_BOOK),
            self._row(ICON_LOCK, "lock service", ys[1], C_LOCK),
            self._row(ICON_SERVER, "instance B", ys[2], TEAL),
            self._row(ICON_DATABASE, "rooms row 101", ys[3], GREY_A),
        )
        time_lbl = make_label("time →", font_size=9, color=GREY_B)
        time_lbl.move_to([_TL_X1 + 0.2, ys[0] + 0.32, 0])
        self.play(FadeIn(rows), FadeIn(time_lbl))
        return rows, ys

    def _lock_story(self, rows, ys, fencing):
        yA, yL, yB, yS = ys
        tok_a = "ok, token 33" if fencing else "ok, lease 5s"
        tok_b = "ok, token 34" if fencing else "ok"

        a1 = self._arr(0.2, yA, 0.8, yL, C_BOOK)
        m1 = self._msg(a1, "acquire", LEFT * 0.55, C_BOOK)
        self.play(GrowArrow(a1), FadeIn(m1), run_time=0.5)
        a2 = self._arr(0.9, yL, 1.5, yA, C_LOCK)
        m2 = self._msg(a2, tok_a, RIGHT * 0.75, C_LOCK)
        self.play(GrowArrow(a2), FadeIn(m2), run_time=0.5)
        lease = self._start_bars(0.9, [yL], [C_LOCK], height=0.24)
        lease_lbl = make_label("A's lease (5s)", font_size=10, color=C_LOCK).move_to([_tx(2.3), yL - 0.3, 0])
        self.play(*self._grow_bars(lease, 1.8), FadeIn(lease_lbl), run_time=0.5)
        self._next_slide(phase=True)

        pause = self._start_bars(1.8, [yA], [GREY_B], height=0.34)
        pause_lbl = make_label("GC pause", font_size=11, color=GREY_A).move_to([_tx(2.9), yA, 0])
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
        w_b = "write, token 34" if fencing else "booked_by = B"
        m5 = self._msg(b3, w_b, RIGHT * 0.9, TEAL)
        self.play(GrowArrow(b3), FadeIn(m5), *self._grow_bars(pause, 5.8), run_time=0.5)
        state_b = "fence_token: 34, booked_by: B" if fencing else "booked_by: B"
        s1 = self._chip(state_b, TEAL).move_to([_tx(5.8), yS - 0.42, 0])
        self.play(FadeIn(s1))
        self._next_slide(phase=True)

        self.play(*self._grow_bars(pause, 6.3), run_time=0.4)
        self.play(rows[0].animate.set_opacity(1.0))
        think = self._chip('"I still have the lock"', C_BOOK).move_to([_tx(6.9), yA + 0.42, 0])
        self.play(FadeIn(think, shift=DOWN * 0.1))
        a3 = self._arr(6.6, yA, 7.4, yS, C_BOOK)
        w_a = "write, token 33" if fencing else "booked_by = A"
        m6 = self._msg(a3, w_a, RIGHT * 0.95 + UP * 0.35, C_BOOK)
        self.play(GrowArrow(a3), FadeIn(m6), run_time=0.7)
        return s1, a3

    # ─── Scene 18: Lock without fencing ───────────────────────────────
    def scene_lock_without_fencing(self):
        self._header("Distributed Lock: The Paused Client", color=YELLOW)
        why = make_label("Imagine the resource can't protect itself, like a file or an external system.",
                         font_size=10, color=GREY_B)
        why.move_to([0, 2.95, 0])
        self.play(FadeIn(why))
        rows, ys = self._lock_stage()
        self._lock_story(rows, ys, fencing=False)

        s2 = self._chip("booked_by: A", RED).move_to([_tx(7.4), ys[3] - 0.42, 0])
        self.play(FadeIn(s2))
        self.play(Indicate(s2, color=RED))
        badge = self._verdict_badge("B paid, the room says A. B's booking is lost  ✗", RED, width=8.0)
        badge.move_to([0, -2.3, 0])
        self.play(FadeIn(badge, shift=UP * 0.1))
        cap = self._caption("A node can't trust its own sense of time. The lease expired while it was paused.",
                            y=-3.1, font_size=11)
        self.play(FadeIn(cap))
        self._end_scene()

    # ─── Scene 19: Lock with fencing ──────────────────────────────────
    def scene_lock_with_fencing(self):
        self._header("Fencing Tokens", color=GREEN)
        rows, ys = self._lock_stage()
        _, a3 = self._lock_story(rows, ys, fencing=True)

        back = self._dashed_arrow([_tx(7.6), ys[3], 0], [_tx(8.2), ys[0], 0], RED)
        rej = make_label("33 < 34, rejected", font_size=10, color=RED).move_to([_tx(8.1), ys[1] + 0.1, 0])
        self.play(Create(back), FadeIn(rej))
        self.play(a3.animate.set_color(RED))
        self._next_slide(phase=True)

        code = make_code_text(
            "UPDATE rooms\n   SET booked_by = :who, fence_token = :t\n WHERE room_id = 101 AND fence_token < :t",
            font_size=10, language="sql", force_code_object=True, glow=False,
        )
        code.move_to([-2.2, -2.45, 0])
        chips = VGroup(self._chip("B, token 34  →  1 row", GREEN, font_size=10),
                       self._chip("A, token 33  →  0 rows", RED, font_size=10)).arrange(DOWN, buff=0.2)
        chips.next_to(code, RIGHT, buff=0.6)
        self.play(FadeIn(code))
        self.play(AnimationGroup(*[FadeIn(c, shift=LEFT * 0.1) for c in chips], lag_ratio=0.3))
        self._next_slide(phase=True)
        self._clear()

        self._header("Fencing Tokens: Two Rules", color=GREEN)
        c1 = self._card("The check lives in the storage, not the client",
                        "A honestly believes it still has the lock. Only the resource can say no.",
                        GREEN, width=11.0)
        c2 = self._card("Tokens only ever go up",
                        "Redis INCR is enough for the demo. Real systems use ZooKeeper (zxid)\n"
                        "or etcd (revision), which are linearizable and fault tolerant.",
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
        table = make_comparison_table(
            col_headers=["", "2PC", "Saga"],
            col_colors=[GREY_B, TEAL, ORANGE],
            col_x_positions=[-4.4, -0.4, 3.8],
            rows_data=[
                ("Atomicity", GREY_A, "all or nothing", GREY_A, "eventually, via compensations", GREY_A),
                ("Isolation", GREY_A, "yes, readers wait", GREEN, "none, readers see the middle", RED),
                ("Locks", GREY_A, "held until the decision", RED, "only inside each local step", GREEN),
                ("One node down", GREY_A, "everything blocks", RED, "that step retries or compensates", GREEN),
                ("Pick it when", GREY_A, "few nodes, short tx", GREY_A, "many services, long flows", GREY_A),
            ],
            header_font_size=16, row_font_size=12, note_font_size=12, row_spacing=0.62,
        )
        table.move_to([0, 0.0, 0])
        self.play(FadeIn(table[0]), Create(table[1]))
        for row in table[2]:
            self.play(FadeIn(row, shift=UP * 0.1), run_time=0.4)
            self.wait(0.3)
        self.play(Indicate(table[0][1], color=TEAL))
        self.play(Indicate(table[0][2], color=ORANGE))
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
        refs = make_label("DDIA p.249–251 · 257–260 · 301–304 · 353–364   ·   youtu.be/DOFflggE_0Q",
                          font_size=10, color=GREY_B)
        foot = VGroup(book, refs).arrange(RIGHT, buff=0.2).move_to([0, -2.8, 0])
        self.play(FadeIn(foot))
        self._end_scene(4)
