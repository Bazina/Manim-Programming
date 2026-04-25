import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from manim import (
    config,
    Scene,
    VGroup,
    RoundedRectangle,
    Line,
    Arrow,
    DashedLine,
    Circle,
    FadeIn,
    FadeOut,
    GrowArrow,
    AddTextLetterByLetter,
    Circumscribe,
    Indicate,
    AnimationGroup,
    ORIGIN,
    UP,
    DOWN,
    LEFT,
    RIGHT,
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

from libs.ddia_components import (
    DARK_BG,
    ICON_DATABASE,
    ICON_SERVER,
    ICON_CHECK,
    ICON_CODE,
    ICON_LOCK,
    ICON_SHIELD,
    ICON_USER,
    make_label,
    make_icon,
)

config.background_color = "#0D1117"

# ── Timeline layout constants ──────────────────────────────────────────
_TL_X0 = -5.0   # timeline x start
_TL_X1 = 6.2    # timeline x end
_T_MAX = 8.5    # total time units across the timeline
_LABEL_X = -6.3  # x-center for client letter circles


def _tx(t):
    """Convert time unit to Manim x-coordinate."""
    return _TL_X0 + t * (_TL_X1 - _TL_X0) / _T_MAX


class Sheet4Consistency(Scene):

    def construct(self):
        self.scene_title()
        self.scene_q1_isolation()
        self.scene_q2_linearizable()
        self.scene_q2_non_linear()
        self.scene_q3_fifo()
        self.scene_q4_cap()
        self.scene_q5_monotonic()
        self.scene_closing()

    # ─── Shared helpers ───────────────────────────────────────────────

    def _make_op(self, text, x_center, y, color, width=1.9, height=0.40, font_size=10):
        box = RoundedRectangle(
            corner_radius=0.07,
            width=width,
            height=height,
            fill_color=DARK_BG,
            fill_opacity=0.92,
            stroke_color=color,
            stroke_width=1.4,
        )
        box.move_to([x_center, y, 0])
        lbl = make_label(text, font_size=font_size, color=color)
        lbl.move_to(box.get_center())
        return VGroup(box, lbl)

    def _client_row(self, letter, y, color):
        """Horizontal timeline row with client circle label on left."""
        circ = Circle(radius=0.21, stroke_color=color, stroke_width=1.5)
        circ.set_fill(DARK_BG, opacity=0.9)
        circ.move_to([_LABEL_X + 0.35, y, 0])
        ltr = make_label(letter, font_size=11, color=color)
        ltr.move_to(circ.get_center())
        client_lbl = make_label(f"Client {letter}", font_size=8, color=color)
        client_lbl.next_to(circ, LEFT, buff=0.07)
        tl = Line(
            [_TL_X0, y, 0], [_TL_X1, y, 0],
            stroke_color=color, stroke_width=1.0, stroke_opacity=0.35,
        )
        tip = Arrow(
            [_TL_X1 - 0.05, y, 0], [_TL_X1 + 0.25, y, 0],
            buff=0, stroke_width=1.5, color=color, tip_length=0.13,
        )
        return VGroup(client_lbl, circ, ltr, tl, tip)

    def _db_row(self, y):
        """Database timeline at bottom."""
        ic = make_icon(ICON_DATABASE, color=GREY_B, height=0.3)
        ic.move_to([_LABEL_X + 0.25, y, 0])
        lbl = make_label("Database", font_size=8, color=GREY_B)
        lbl.next_to(ic, LEFT, buff=0.06)
        tl = Line(
            [_TL_X0, y, 0], [_TL_X1, y, 0],
            stroke_color=GREY_B, stroke_width=2.0, stroke_opacity=0.7,
        )
        return VGroup(lbl, ic, tl)

    def _op_box(self, t_call, t_ret, op_text, ret_text, y, color,
                box_h=0.44, ret_color=None, tick_t=None):
        """DDIA-style operation box spanning [t_call, t_ret] at row y.
        tick_t: if given, draws a vertical line inside the box showing the linearization point."""
        x1 = _tx(t_call)
        x2 = _tx(t_ret)
        cx = (x1 + x2) / 2
        w = max(x2 - x1, 0.55)

        box = RoundedRectangle(
            corner_radius=0.07,
            width=w, height=box_h,
            fill_color=DARK_BG, fill_opacity=0.95,
            stroke_color=color, stroke_width=1.5,
        )
        box.move_to([cx, y, 0])
        op_lbl = make_label(op_text, font_size=9, color=color)
        # Shift label left when tick present to avoid overlap
        lbl_x = cx - w * 0.15 if tick_t is not None else cx
        op_lbl.move_to([lbl_x, y, 0])

        rc = ret_color or GREY_A
        ret_lbl = make_label(f"=> {ret_text}", font_size=9, color=rc)
        ret_lbl.next_to(box, RIGHT, buff=0.1)

        d1 = DashedLine(
            [x1, y + 0.55, 0], [x1, y - 0.55, 0],
            dash_length=0.07, color=GREY_B, stroke_width=0.7,
        )
        d2 = DashedLine(
            [x2, y + 0.55, 0], [x2, y - 0.55, 0],
            dash_length=0.07, color=GREY_B, stroke_width=0.7,
        )

        parts = [d1, d2, box, op_lbl]
        if tick_t is not None:
            xt = _tx(tick_t)
            tick = Line(
                [xt, y + box_h / 2 - 0.03, 0], [xt, y - box_h / 2 + 0.03, 0],
                stroke_color=color, stroke_width=2.5,
            )
            parts.append(tick)

        return VGroup(*parts), ret_lbl

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

    # ─── Scene 1: Title ───────────────────────────────────────────────
    def scene_title(self):
        icon = make_icon(ICON_LOCK, color=TEAL, height=1.1)
        title = make_label("Sheet 4: Consistency", font_size=36, color=TEAL)
        sub = make_label(
            "Isolation  ·  Linearizability  ·  FIFO Queues  ·  CAP  ·  Monotonic Reads",
            font_size=17, color=GREY_B,
        )
        VGroup(icon, title, sub).arrange(DOWN, buff=0.38)
        self.play(FadeIn(icon, shift=DOWN * 0.3))
        self.wait(0.4)
        self.play(AddTextLetterByLetter(title, time_per_char=0.04))
        self.wait(0.4)
        self.play(FadeIn(sub, shift=UP * 0.2))
        self.wait(3)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 2: Q1 — Isolation vs Ordering ─────────────────────────
    def scene_q1_isolation(self):
        header = make_label("Q1: Isolation vs. Ordering Guarantees", font_size=26, color=TEAL)
        header.to_edge(UP, buff=0.35)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.4)

        # Definition cards
        iso_box = RoundedRectangle(
            corner_radius=0.1, width=6.0, height=0.72,
            fill_color=DARK_BG, fill_opacity=0.9,
            stroke_color=BLUE, stroke_width=1.4,
        )
        iso_lbl = make_label(
            "Isolation — concurrent transactions hidden from each other",
            font_size=12, color=BLUE,
        )
        iso_lbl.move_to(iso_box.get_center())
        iso_card = VGroup(iso_box, iso_lbl)

        ord_box = RoundedRectangle(
            corner_radius=0.1, width=6.0, height=0.72,
            fill_color=DARK_BG, fill_opacity=0.9,
            stroke_color=ORANGE, stroke_width=1.4,
        )
        ord_lbl = make_label(
            "Ordering — all nodes agree on which op happened first",
            font_size=12, color=ORANGE,
        )
        ord_lbl.move_to(ord_box.get_center())
        ord_card = VGroup(ord_box, ord_lbl)

        VGroup(iso_card, ord_card).arrange(DOWN, buff=0.12).next_to(header, DOWN, buff=0.3)

        self.play(FadeIn(iso_card, shift=LEFT * 0.2))
        self.wait(0.2)
        self.play(FadeIn(ord_card, shift=LEFT * 0.2))
        self.wait(0.5)

        # ── Transaction diagrams ───────────────────────────────────────
        T1_Y = -1.15
        T2_Y = -2.05
        GOOD_X0, GOOD_X1 = -6.0, -0.6
        BAD_X0, BAD_X1 = 0.3, 6.2

        def _row_line(x0, x1, y, color):
            return Line([x0 + 0.9, y, 0], [x1, y, 0],
                        stroke_color=color, stroke_width=0.8, stroke_opacity=0.4)

        def _row_lbl(text, x, y, color):
            lbl = make_label(text, font_size=9, color=color)
            lbl.move_to([x, y, 0])
            return lbl

        # ── Good Isolation ─────────────────────────────────────────────
        g_hdr = make_label("Good Isolation  ✓", font_size=13, color=GREEN)
        g_hdr.move_to([(GOOD_X0 + GOOD_X1) / 2, -0.55, 0])

        g_t1_lbl = _row_lbl("T1:", GOOD_X0 + 0.45, T1_Y, BLUE)
        g_t2_lbl = _row_lbl("T2:", GOOD_X0 + 0.45, T2_Y, GREEN)
        g_t1_line = _row_line(GOOD_X0, GOOD_X1, T1_Y, BLUE)
        g_t2_line = _row_line(GOOD_X0, GOOD_X1, T2_Y, GREEN)

        # T1: Write A=2 at x=-4.3 to -2.5; Commit at x=-1.9 to -0.9
        g_t1_write = self._make_op("Write A=2", -3.4, T1_Y, BLUE, width=1.9)
        g_t1_commit = self._make_op("Commit", -1.4, T1_Y, BLUE, width=1.1, font_size=9)

        # T2: Read A at x=-4.8 to -3.5 (before T1 write range) → returns 1
        g_t2_read = self._make_op("Read A", -4.55, T2_Y, GREEN, width=1.3)
        g_t2_ret = make_label("= 1", font_size=12, color=GREEN)
        g_t2_ret.next_to(g_t2_read, RIGHT, buff=0.12)
        g_t2_commit = self._make_op("Commit", -1.4, T2_Y, GREEN, width=1.1, font_size=9)

        good_group = VGroup(
            g_hdr, g_t1_lbl, g_t2_lbl,
            g_t1_line, g_t2_line,
            g_t1_write, g_t1_commit,
            g_t2_read, g_t2_ret, g_t2_commit,
        )

        # ── Bad Isolation ──────────────────────────────────────────────
        b_hdr = make_label("Bad Isolation (Dirty Read)  ✗", font_size=13, color=RED)
        b_hdr.move_to([(BAD_X0 + BAD_X1) / 2, -0.55, 0])

        b_t1_lbl = _row_lbl("T1:", BAD_X0 + 0.45, T1_Y, BLUE)
        b_t2_lbl = _row_lbl("T2:", BAD_X0 + 0.45, T2_Y, RED)
        b_t1_line = _row_line(BAD_X0, BAD_X1, T1_Y, BLUE)
        b_t2_line = _row_line(BAD_X0, BAD_X1, T2_Y, RED)

        # T1: Write A=2 at center x=2.2; Commit at x=4.4
        b_t1_write = self._make_op("Write A=2", 2.2, T1_Y, BLUE, width=1.9)
        b_t1_commit = self._make_op("Commit", 4.5, T1_Y, BLUE, width=1.1, font_size=9)

        # T2: Read A at x=2.2 (overlaps with T1 write!) → returns 2
        b_t2_read = self._make_op("Read A", 2.2, T2_Y, RED, width=1.3)
        b_t2_ret = make_label("= 2  ✗", font_size=12, color=RED)
        b_t2_ret.next_to(b_t2_read, RIGHT, buff=0.12)
        b_t2_commit = self._make_op("Commit", 4.5, T2_Y, RED, width=1.1, font_size=9)

        bad_group = VGroup(
            b_hdr, b_t1_lbl, b_t2_lbl,
            b_t1_line, b_t2_line,
            b_t1_write, b_t1_commit,
            b_t2_read, b_t2_ret, b_t2_commit,
        )

        self.play(FadeIn(good_group, shift=UP * 0.15))
        self.wait(0.5)
        self.play(FadeIn(bad_group, shift=UP * 0.15))
        self.wait(0.5)
        self.play(Indicate(b_t2_ret, color=RED, run_time=1.2))

        note = make_label(
            "Isolation = transaction scope  |  Ordering = per-operation visibility across nodes",
            font_size=11, color=YELLOW,
        )
        note.to_edge(DOWN, buff=0.35)
        self.play(FadeIn(note, shift=UP * 0.1))
        self.wait(3.5)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 3: Q2 — History H (Linearizable) ──────────────────────
    def scene_q2_linearizable(self):
        header = make_label("Q2: Is History H Linearizable?", font_size=26, color=TEAL)
        header.to_edge(UP, buff=0.3)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.4)

        ROW_A = 1.7
        ROW_B = 0.45
        ROW_C = -0.8
        DB_Y = -2.1

        # Timeline frame
        row_a = self._client_row("A", ROW_A, TEAL)
        row_b = self._client_row("B", ROW_B, BLUE)
        row_c = self._client_row("C", ROW_C, ORANGE)
        db_row = self._db_row(DB_Y)

        time_lbl = make_label("time →", font_size=10, color=GREY_B)
        time_lbl.move_to([_TL_X1 + 0.35, 2.5, 0])

        self.play(
            AnimationGroup(
                FadeIn(row_a), FadeIn(row_b), FadeIn(row_c),
                FadeIn(db_row), FadeIn(time_lbl),
                lag_ratio=0.12,
            )
        )
        self.wait(0.4)

        # B: R.write(1) — linearizes SECOND at t=2.5; final state R=1
        op_b_w1, ret_b_w1 = self._op_box(0.5, 3.5, "R.write(1)", "void", ROW_B, BLUE, tick_t=2.5)
        # A: R.read() → 1 (write(1) tick at 2.5 falls within A's interval [1.0, 3.0])
        op_a_r, ret_a_r = self._op_box(1.0, 3.0, "R.read()", "1", ROW_A, TEAL, ret_color=GREEN)
        # C: R.write(2) — linearizes FIRST at t=1.8; then overwritten to 1 by B
        op_c_w2, ret_c_w2 = self._op_box(1.5, 4.2, "R.write(2)", "void", ROW_C, ORANGE, tick_t=1.8)
        # B: R.read() → 1 (after both writes; write(1) was last applied)
        op_b_r2, ret_b_r2 = self._op_box(4.5, 5.5, "R.read()", "1", ROW_B, BLUE, ret_color=GREEN)
        # A: Q.write(3)
        op_a_qw, ret_a_qw = self._op_box(6.0, 7.5, "Q.write(3)", "void", ROW_A, TEAL)
        # C: R.read() → 1 (latest state; write(1) overwritten write(2))
        op_c_r2, ret_c_r2 = self._op_box(6.3, 7.8, "R.read()", "1", ROW_C, ORANGE, ret_color=GREEN)

        all_ops = [
            (op_b_w1, ret_b_w1), (op_a_r, ret_a_r), (op_c_w2, ret_c_w2),
            (op_b_r2, ret_b_r2), (op_a_qw, ret_a_qw), (op_c_r2, ret_c_r2),
        ]
        for op, ret in all_ops:
            self.play(FadeIn(op), run_time=0.35)
            self.play(FadeIn(ret), run_time=0.25)
            self.wait(0.15)

        # DB: write(2) tick at t=1.8 → R=2, write(1) tick at t=2.5 → R=1 (overwrites)
        db0 = self._db_marker(0.0, "R=0", DB_Y, GREY_B)
        db2 = self._db_marker(1.8, "R=2", DB_Y, ORANGE)
        db1 = self._db_marker(2.5, "R=1", DB_Y, BLUE)
        for m in [db0, db2, db1]:
            self.play(FadeIn(m), run_time=0.3)
        self.wait(0.6)

        badge = self._verdict_badge("YES — History H is Linearizable  ✓", GREEN, width=6.5)
        badge.to_edge(DOWN, buff=0.2)
        reason = make_label(
            "write(2)→t=1.8 then write(1)→t=2.5 (final R=1)  |  A reads 1 ✓  |  B reads 1 ✓  |  C reads 1 ✓",
            font_size=9, color=GREY_A,
        )
        reason.next_to(badge, UP, buff=0.12)
        self.play(FadeIn(reason))
        self.play(FadeIn(badge, shift=UP * 0.15))
        self.play(Circumscribe(badge, color=GREEN, buff=0.05, run_time=1.5))
        self.wait(4)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 4: Q2 — Making H Non-Linearizable ─────────────────────
    def scene_q2_non_linear(self):
        header = make_label("Q2: Making H Non-Linearizable", font_size=26, color=RED)
        header.to_edge(UP, buff=0.3)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.4)

        ROW_A = 1.7
        ROW_B = 0.45
        ROW_C = -0.8
        DB_Y = -2.1

        row_a = self._client_row("A", ROW_A, TEAL)
        row_b = self._client_row("B", ROW_B, BLUE)
        row_c = self._client_row("C", ROW_C, ORANGE)
        db_row = self._db_row(DB_Y)
        time_lbl = make_label("time →", font_size=10, color=GREY_B)
        time_lbl.move_to([_TL_X1 + 0.35, 2.5, 0])

        self.play(
            AnimationGroup(
                FadeIn(row_a), FadeIn(row_b), FadeIn(row_c),
                FadeIn(db_row), FadeIn(time_lbl),
                lag_ratio=0.12,
            )
        )
        self.wait(0.3)

        # Same boxes & ticks as linearizable version
        op_b_w1, ret_b_w1 = self._op_box(0.5, 3.5, "R.write(1)", "void", ROW_B, BLUE, tick_t=2.5)
        op_a_r, ret_a_r = self._op_box(1.0, 3.0, "R.read()", "1", ROW_A, TEAL, ret_color=GREEN)
        op_c_w2, ret_c_w2 = self._op_box(1.5, 4.2, "R.write(2)", "void", ROW_C, ORANGE, tick_t=1.8)
        op_b_r2, ret_b_r2 = self._op_box(4.5, 5.5, "R.read()", "1", ROW_B, BLUE, ret_color=GREEN)
        op_a_qw, ret_a_qw = self._op_box(6.0, 7.5, "Q.write(3)", "void", ROW_A, TEAL)
        # Violation: C reads 2 after A and B both observed R=1
        op_c_r2, ret_c_r2 = self._op_box(6.3, 7.8, "R.read()", "2  ✗", ROW_C, ORANGE, ret_color=RED)

        for op, ret in [(op_b_w1, ret_b_w1), (op_a_r, ret_a_r), (op_c_w2, ret_c_w2),
                        (op_b_r2, ret_b_r2), (op_a_qw, ret_a_qw)]:
            self.play(FadeIn(op), run_time=0.3)
            self.play(FadeIn(ret), run_time=0.2)

        db0 = self._db_marker(0.0, "R=0", DB_Y, GREY_B)
        db2 = self._db_marker(1.8, "R=2", DB_Y, ORANGE)
        db1 = self._db_marker(2.5, "R=1", DB_Y, BLUE)
        for m in [db0, db2, db1]:
            self.play(FadeIn(m), run_time=0.25)

        # Highlight A and B both reading 1 — establishing the agreed-upon state
        self.play(Indicate(ret_a_r, color=GREEN, run_time=1.0))
        self.wait(0.2)
        self.play(Indicate(ret_b_r2, color=GREEN, run_time=1.0))
        self.wait(0.4)

        # Reveal C's regression read
        self.play(FadeIn(op_c_r2), run_time=0.4)
        self.play(FadeIn(ret_c_r2, shift=RIGHT * 0.1), run_time=0.4)
        self.play(Indicate(ret_c_r2, color=RED, run_time=1.5))
        self.wait(0.4)

        badge = self._verdict_badge(
            "NOT Linearizable — R=1 observed by A & B; C reading R=2 is a regression  ✗",
            RED, width=9.0,
        )
        badge.to_edge(DOWN, buff=0.2)
        reason = make_label(
            "write(1) was last applied (t=2.5) → final R=1  |  C reading R=2 = time going backwards ✗",
            font_size=9, color=RED,
        )
        reason.next_to(badge, UP, buff=0.12)
        self.play(FadeIn(reason))
        self.play(FadeIn(badge, shift=UP * 0.15))
        self.play(Circumscribe(badge, color=RED, buff=0.04, run_time=1.5))
        self.wait(4)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 5: Q3 — FIFO Queue ────────────────────────────────────
    def scene_q3_fifo(self):
        header = make_label("Q3: FIFO Queue — Linearizable?", font_size=26, color=ORANGE)
        header.to_edge(UP, buff=0.4)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.4)

        # History column (left)
        hist_hdr = make_label("History H:", font_size=13, color=GREY_A)
        hist_hdr.move_to(LEFT * 3.8 + UP * 1.5)

        ops_data = [
            ("A:  q.enq(x)", TEAL),
            ("B:  q.enq(y)", BLUE),
            ("A:  q: void", TEAL),
            ("B:  q: void", BLUE),
            ("A:  q.deq()  →  y", ORANGE),
            ("C:  q.deq()  →  y", RED),
        ]
        op_rows = VGroup()
        for text, color in ops_data:
            box = RoundedRectangle(
                corner_radius=0.06, width=3.6, height=0.42,
                fill_color=DARK_BG, fill_opacity=0.9,
                stroke_color=color, stroke_width=1.0,
            )
            lbl = make_label(text, font_size=11, color=color)
            lbl.move_to(box.get_center())
            op_rows.add(VGroup(box, lbl))

        op_rows.arrange(DOWN, buff=0.07).next_to(hist_hdr, DOWN, buff=0.2)
        op_rows.align_to(hist_hdr, LEFT)

        self.play(FadeIn(hist_hdr))
        for row in op_rows:
            self.play(FadeIn(row, shift=RIGHT * 0.1), run_time=0.28)
            self.wait(0.08)

        # Queue state visual (right)
        q_hdr = make_label("Queue State", font_size=13, color=GREY_A)
        q_hdr.move_to(RIGHT * 2.5 + UP * 1.5)
        self.play(FadeIn(q_hdr))

        q_x_box = RoundedRectangle(
            corner_radius=0.08, width=2.0, height=0.5,
            fill_color=DARK_BG, fill_opacity=0.9,
            stroke_color=TEAL, stroke_width=1.4,
        )
        q_x_lbl = make_label("x  (enqueued by A)", font_size=10, color=TEAL)
        q_x_lbl.move_to(q_x_box.get_center())
        q_x = VGroup(q_x_box, q_x_lbl)

        q_y_box = RoundedRectangle(
            corner_radius=0.08, width=2.0, height=0.5,
            fill_color=DARK_BG, fill_opacity=0.9,
            stroke_color=BLUE, stroke_width=1.4,
        )
        q_y_lbl = make_label("y  (enqueued by B)", font_size=10, color=BLUE)
        q_y_lbl.move_to(q_y_box.get_center())
        q_y = VGroup(q_y_box, q_y_lbl)

        q_stack = VGroup(q_x, q_y).arrange(DOWN, buff=0.06)
        q_stack.next_to(q_hdr, DOWN, buff=0.3)

        fifo_note = make_label("FIFO: x dequeued first, then y", font_size=10, color=GREY_A)
        fifo_note.next_to(q_stack, DOWN, buff=0.2)
        self.play(FadeIn(q_stack), FadeIn(fifo_note))
        self.wait(0.5)

        # Highlight the two dequeue violations
        self.play(Indicate(op_rows[4], color=RED, run_time=1.0))
        self.wait(0.2)
        self.play(Indicate(op_rows[5], color=RED, run_time=1.0))
        self.wait(0.3)

        # Violation list (right lower)
        viols = VGroup(
            make_label("✗  A dequeues y — x should come first (FIFO violated)", font_size=11, color=RED),
            make_label("✗  C dequeues y — y was enqueued only ONCE", font_size=11, color=RED),
            make_label("✗  x was never dequeued", font_size=11, color=ORANGE),
        ).arrange(DOWN, buff=0.16, aligned_edge=LEFT)
        viols.move_to(RIGHT * 4.0 + DOWN * 1.6)
        self.play(FadeIn(viols, shift=LEFT * 0.2))

        badge = self._verdict_badge(
            "NOT Linearizable — y dequeued twice violates FIFO queue semantics  ✗",
            RED, width=8.0,
        )
        badge.to_edge(DOWN, buff=0.3)
        self.play(FadeIn(badge, shift=UP * 0.15))
        self.wait(4)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 6: Q4 — CAP Trade-off ─────────────────────────────────
    def scene_q4_cap(self):
        header = make_label("Q4: Read-After-Write & CAP", font_size=26, color=PURPLE)
        header.to_edge(UP, buff=0.4)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.4)

        setup = make_label(
            "Solution: always read from the leader replica (guarantees read-your-writes)",
            font_size=12, color=GREY_A,
        )
        setup.next_to(header, DOWN, buff=0.25)
        self.play(FadeIn(setup, shift=UP * 0.1))
        self.wait(0.5)

        def _node_card(icon_path, label, color, w=2.3, h=1.3):
            ic = make_icon(icon_path, color=color, height=0.38)
            lbl = make_label(label, font_size=11, color=color)
            content = VGroup(ic, lbl).arrange(DOWN, buff=0.08)
            box = RoundedRectangle(
                corner_radius=0.1, width=w, height=h,
                fill_color=DARK_BG, fill_opacity=0.9,
                stroke_color=color, stroke_width=1.5,
            )
            content.move_to(box.get_center())
            return VGroup(box, content)

        client_card = _node_card(ICON_CODE, "Client", TEAL)
        leader_card = _node_card(ICON_SERVER, "Leader\nReplica", GREEN)
        follower_card = _node_card(ICON_SERVER, "Follower\nReplica", GREY_B)
        cards = VGroup(client_card, leader_card, follower_card)
        cards.arrange(RIGHT, buff=1.5).move_to(UP * 0.55)

        self.play(AnimationGroup(*[FadeIn(c, shift=DOWN * 0.15) for c in cards], lag_ratio=0.2))
        self.wait(0.4)

        # ── Normal flow: Client reads from leader ──────────────────────
        read_arrow = Arrow(
            client_card.get_right(), leader_card.get_left(),
            buff=0.1, stroke_width=2.0, color=GREEN, tip_length=0.15,
        )
        read_lbl = make_label("read", font_size=10, color=GREEN)
        read_lbl.next_to(read_arrow, UP, buff=0.08)
        ok_lbl = make_label("always fresh  ✓", font_size=10, color=GREEN)
        ok_lbl.next_to(leader_card, DOWN, buff=0.18)

        self.play(GrowArrow(read_arrow), FadeIn(read_lbl))
        self.play(FadeIn(ok_lbl))
        self.wait(1.2)

        # ── Leader crashes ─────────────────────────────────────────────
        self.play(FadeOut(read_arrow, read_lbl, ok_lbl))
        crash_x = make_label("✗", font_size=44, color=RED)
        crash_x.move_to(leader_card.get_center())
        leader_card.set_opacity(0.3)
        self.play(FadeIn(crash_x))

        fail_arrow = Arrow(
            client_card.get_right(), leader_card.get_left(),
            buff=0.1, stroke_width=2.0, color=RED, tip_length=0.15,
        )
        fail_lbl = make_label("read?", font_size=10, color=RED)
        fail_lbl.next_to(fail_arrow, UP, buff=0.08)
        fail_result = make_label("UNAVAILABLE", font_size=10, color=RED)
        fail_result.next_to(leader_card, DOWN, buff=0.18)

        self.play(GrowArrow(fail_arrow), FadeIn(fail_lbl))
        self.play(FadeIn(fail_result))
        self.wait(0.8)

        cap_summary = VGroup(
            make_label(
                "Lost: Availability  —  reads fail when leader unreachable",
                font_size=13, color=YELLOW,
            ),
            make_label(
                "P is always assumed — refusing reads IS the correct partition response (no stale data)",
                font_size=11, color=GREY_A,
            ),
            make_label(
                "Real trade-off: C vs A when partition fires  →  this system chooses C  →  CP",
                font_size=11, color=PURPLE,
            ),
        ).arrange(DOWN, buff=0.12)
        cap_summary.to_edge(DOWN, buff=0.35)
        self.play(FadeIn(cap_summary, shift=UP * 0.15))
        self.wait(4)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 7: Q5 — Monotonic Reads ───────────────────────────────
    def scene_q5_monotonic(self):
        header = make_label("Q5: Monotonic Reads — Timestamp Solution", font_size=22, color=GREEN)
        header.to_edge(UP, buff=0.3)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.3)

        # Five-row sequence diagram (DDIA Figure 5-4 style)
        ROW_U1 = 2.0    # User 1234
        ROW_L  = 0.85   # Leader
        ROW_F1 = -0.3   # Follower 1  (fresh)
        ROW_F2 = -1.45  # Follower 2  (stale)
        ROW_U2 = -2.6   # User 2345
        ICN_X  = -5.5

        def _row(icon_path, label_text, y, color):
            ic = make_icon(icon_path, color=color, height=0.36)
            ic.move_to([ICN_X, y, 0])
            lbl = make_label(label_text, font_size=9, color=color)
            lbl.next_to(ic, LEFT, buff=0.1)
            dash = DashedLine(
                [ICN_X + 0.25, y, 0], [_TL_X1 - 0.1, y, 0],
                dash_length=0.15, color=color, stroke_width=0.8, stroke_opacity=0.4,
            )
            return VGroup(lbl, ic, dash)

        def _arr(t0, y0, t1, y1, color):
            return Arrow(
                [_tx(t0), y0, 0], [_tx(t1), y1, 0],
                buff=0, stroke_width=1.7, color=color, tip_length=0.13,
            )

        def _msg(arr, text, offset, color, fs=8):
            lbl = make_label(text, font_size=fs, color=color)
            lbl.move_to(arr.get_center() + offset)
            return lbl

        # ── Phase 1: The Anomaly (Figure 5-4 style) ──────────────────
        sub = make_label(
            "User 2345 reads from a fresh replica, then a stale one — time appears to go backward  ✗",
            font_size=9, color=RED,
        )
        sub.next_to(header, DOWN, buff=0.18)

        rows = VGroup(
            _row(ICON_USER,     "User 1234",  ROW_U1, TEAL),
            _row(ICON_DATABASE, "Leader",     ROW_L,  BLUE),
            _row(ICON_DATABASE, "Follower 1", ROW_F1, GREEN),
            _row(ICON_DATABASE, "Follower 2", ROW_F2, ORANGE),
            _row(ICON_USER,     "User 2345",  ROW_U2, PURPLE),
        )
        time_lbl = make_label("time →", font_size=9, color=GREY_B)
        time_lbl.move_to([_TL_X1 + 0.2, ROW_U1 + 0.32, 0])

        self.play(FadeIn(sub), FadeIn(rows), FadeIn(time_lbl))
        self.wait(0.3)

        # User 1234 → Leader: INSERT
        ins_lbl = make_label(
            "insert into comments\n(author, reply_to, message)\nvalues(1234, 55555, 'Sounds good!')",
            font_size=7, color=TEAL,
        )
        ins_lbl.move_to([_tx(1.2), ROW_U1 + 0.5, 0])
        a_u1_l = _arr(1.5, ROW_U1, 2.3, ROW_L, TEAL)
        self.play(FadeIn(ins_lbl))
        self.play(GrowArrow(a_u1_l), run_time=0.5)

        # Leader → User 1234: "insert ok"
        a_l_u1 = _arr(2.3, ROW_L, 3.0, ROW_U1, BLUE)
        m_ok = _msg(a_l_u1, "insert ok", DOWN * 0.22, BLUE)
        self.play(GrowArrow(a_l_u1), run_time=0.4)
        self.play(FadeIn(m_ok))

        # Leader → Follower 1: fast replication
        a_l_f1 = _arr(2.3, ROW_L, 3.5, ROW_F1, GREEN)
        m_rep1 = _msg(a_l_f1, "insert into\ncomments...", UP * 0.27, GREEN, fs=7)
        self.play(GrowArrow(a_l_f1), run_time=0.5)
        self.play(FadeIn(m_rep1))

        # Leader → Follower 2: VERY SLOW — long diagonal, key visual element
        a_l_f2 = _arr(2.3, ROW_L, 7.6, ROW_F2, ORANGE)
        m_rep2 = make_label("insert into\ncomments...", font_size=7, color=ORANGE)
        m_rep2.move_to([_tx(7.3), ROW_F2 + 0.32, 0])
        self.play(GrowArrow(a_l_f2), run_time=1.2)
        self.play(FadeIn(m_rep2))
        self.wait(0.3)

        # User 2345 → Follower 1: Read ① (fresh → 1 result)
        q1 = make_label(
            "select * from comments\nwhere reply_to = 55555", font_size=7, color=PURPLE,
        )
        q1.move_to([_tx(3.9), ROW_U2 - 0.38, 0])
        a_u2_f1 = _arr(3.6, ROW_U2, 4.3, ROW_F1, PURPLE)
        self.play(FadeIn(q1), GrowArrow(a_u2_f1), run_time=0.5)

        a_f1_u2 = _arr(4.3, ROW_F1, 5.0, ROW_U2, GREEN)
        m_r1 = _msg(a_f1_u2, "1 result", RIGHT * 0.45 + UP * 0.2, GREEN, fs=9)
        self.play(GrowArrow(a_f1_u2), run_time=0.4)
        self.play(FadeIn(m_r1))
        self.wait(0.5)

        # User 2345 → Follower 2: Read ② (stale → no results!)
        q2 = make_label(
            "select * from comments\nwhere reply_to = 55555", font_size=7, color=PURPLE,
        )
        q2.move_to([_tx(6.0), ROW_U2 - 0.38, 0])
        a_u2_f2 = _arr(5.7, ROW_U2, 6.2, ROW_F2, PURPLE)
        self.play(FadeIn(q2), GrowArrow(a_u2_f2), run_time=0.4)

        a_f2_u2 = _arr(6.2, ROW_F2, 6.8, ROW_U2, RED)
        m_r2 = _msg(a_f2_u2, "no results!", RIGHT * 0.45 + UP * 0.2, RED, fs=9)
        self.play(GrowArrow(a_f2_u2), run_time=0.4)
        self.play(FadeIn(m_r2))
        self.play(Indicate(m_r2, color=RED, run_time=1.2))
        self.wait(0.3)

        badge1 = self._verdict_badge(
            "Time appears to go backward — Monotonic Reads violated  ✗", RED, width=8.2,
        )
        badge1.to_edge(DOWN, buff=0.3)
        note1 = make_label(
            "Follower 2 is stale — same query returns fewer results than Read ① saw",
            font_size=9, color=RED,
        )
        note1.next_to(badge1, UP, buff=0.12)
        self.play(FadeIn(note1), FadeIn(badge1, shift=UP * 0.1))
        self.wait(3.5)
        self.play(FadeOut(*self.mobjects))

        # ── Phase 2: Fix with min_timestamp ──────────────────────────
        header2 = make_label("Q5: Monotonic Reads — Timestamp Solution", font_size=22, color=GREEN)
        header2.to_edge(UP, buff=0.3)
        sub2 = make_label(
            "With min_timestamp: stale replica blocks — reads can never go backward  ✓",
            font_size=9, color=GREEN,
        )
        sub2.next_to(header2, DOWN, buff=0.18)

        rows2 = VGroup(
            _row(ICON_USER,     "User 1234",  ROW_U1, TEAL),
            _row(ICON_DATABASE, "Leader",     ROW_L,  BLUE),
            _row(ICON_DATABASE, "Follower 1", ROW_F1, GREEN),
            _row(ICON_DATABASE, "Follower 2", ROW_F2, ORANGE),
            _row(ICON_USER,     "User 2345",  ROW_U2, PURPLE),
        )
        time_lbl2 = make_label("time →", font_size=9, color=GREY_B)
        time_lbl2.move_to([_TL_X1 + 0.2, ROW_U1 + 0.32, 0])

        self.play(FadeIn(header2), FadeIn(sub2), FadeIn(rows2), FadeIn(time_lbl2))
        self.wait(0.3)

        # Same first half: User 1234 inserts, replication fans out
        ins_lbl2 = make_label(
            "insert into comments...\nvalues(1234, 55555, 'Sounds good!')",
            font_size=7, color=TEAL,
        )
        ins_lbl2.move_to([_tx(1.2), ROW_U1 + 0.4, 0])
        a2_u1_l = _arr(1.5, ROW_U1, 2.3, ROW_L,  TEAL)
        a2_l_u1 = _arr(2.3, ROW_L,  3.0, ROW_U1, BLUE)
        m2_ok   = _msg(a2_l_u1, "insert ok", DOWN * 0.22, BLUE)
        a2_l_f1 = _arr(2.3, ROW_L,  3.5, ROW_F1, GREEN)
        m2_rep1 = _msg(a2_l_f1, "insert into\ncomments...", UP * 0.27, GREEN, fs=7)
        a2_l_f2 = _arr(2.3, ROW_L,  7.6, ROW_F2, ORANGE)

        self.play(FadeIn(ins_lbl2), GrowArrow(a2_u1_l), run_time=0.5)
        self.play(GrowArrow(a2_l_u1), FadeIn(m2_ok),   run_time=0.4)
        self.play(GrowArrow(a2_l_f1), FadeIn(m2_rep1), run_time=0.4)
        self.play(GrowArrow(a2_l_f2), run_time=0.6)

        # User 2345 Read ①: same as anomaly, stores T=100
        q2_1 = make_label(
            "select * from comments\nwhere reply_to = 55555", font_size=7, color=PURPLE,
        )
        q2_1.move_to([_tx(3.9), ROW_U2 - 0.38, 0])
        a2_u2_f1 = _arr(3.6, ROW_U2, 4.3, ROW_F1, PURPLE)
        a2_f1_u2 = _arr(4.3, ROW_F1, 5.0, ROW_U2, GREEN)
        m2_r1    = _msg(a2_f1_u2, "1 result  (stores T=100)", RIGHT * 0.65 + UP * 0.2, GREEN, fs=8)
        self.play(FadeIn(q2_1), GrowArrow(a2_u2_f1), run_time=0.5)
        self.play(GrowArrow(a2_f1_u2), FadeIn(m2_r1), run_time=0.4)
        self.wait(0.4)

        # User 2345 Read ②: carries min_timestamp=100 → Follower 2 blocks
        q2_2 = make_label(
            "select * from comments\nwhere reply_to = 55555\n{ min_timestamp: 100 }",
            font_size=7, color=PURPLE,
        )
        q2_2.move_to([_tx(5.9), ROW_U2 - 0.48, 0])
        a2_u2_f2 = _arr(5.7, ROW_U2, 6.2, ROW_F2, PURPLE)
        self.play(FadeIn(q2_2), GrowArrow(a2_u2_f2), run_time=0.4)

        blk_x = make_label("✗", font_size=18, color=RED)
        blk_x.move_to([_tx(6.5), ROW_F2, 0])
        blk_note = make_label("T=80 < 100 → blocked", font_size=8, color=RED)
        blk_note.next_to(blk_x, DOWN, buff=0.08)
        self.play(FadeIn(blk_x), FadeIn(blk_note))
        self.wait(0.3)

        # Rerouted to Follower 1 → fresh "1 result"
        a2_rt = _arr(6.8, ROW_U2, 7.3, ROW_F1, TEAL)
        m2_rt = _msg(a2_rt, "retry → Follower 1", UP * 0.26, TEAL, fs=8)
        self.play(GrowArrow(a2_rt), run_time=0.4)
        self.play(FadeIn(m2_rt))

        a2_ok = _arr(7.3, ROW_F1, 7.8, ROW_U2, GREEN)
        m2_ok2 = _msg(a2_ok, "1 result  ✓", RIGHT * 0.4 + UP * 0.2, GREEN, fs=9)
        self.play(GrowArrow(a2_ok), run_time=0.4)
        self.play(FadeIn(m2_ok2))
        self.play(Indicate(m2_ok2, color=GREEN, run_time=1.2))
        self.wait(0.3)

        badge2 = self._verdict_badge(
            "Monotonic Reads guaranteed — T never goes backward  ✓", GREEN, width=7.8,
        )
        badge2.to_edge(DOWN, buff=0.3)
        bullets = VGroup(
            make_label("✓  Any replica can serve — no sticky sessions", font_size=10, color=GREEN),
            make_label("✓  Failover transparent — route to any fresh replica", font_size=10, color=GREEN),
            make_label("⚠  High replication lag may cause brief blocking at stale replica", font_size=10, color=ORANGE),
        ).arrange(DOWN, buff=0.09, aligned_edge=LEFT)
        bullets.next_to(badge2, UP, buff=0.13)
        self.play(FadeIn(bullets), FadeIn(badge2, shift=UP * 0.1))
        self.wait(4)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 8: Closing ─────────────────────────────────────────────
    def scene_closing(self):
        title = make_label("Sheet 4: Consistency", font_size=34, color=TEAL)
        title.move_to(UP * 1.8)
        self.play(AddTextLetterByLetter(title, time_per_char=0.05))
        self.wait(0.8)

        icon_data = [
            (ICON_LOCK,      TEAL),
            (ICON_DATABASE,  BLUE),
            (ICON_SERVER,    GREEN),
            (ICON_SHIELD,    ORANGE),
            (ICON_CHECK,     PURPLE),
        ]
        icons_row = (
            VGroup(*[make_icon(p, color=c, height=0.5) for p, c in icon_data])
            .arrange(RIGHT, buff=0.55)
            .move_to(ORIGIN)
        )
        self.play(
            AnimationGroup(*[FadeIn(ic, shift=UP * 0.2) for ic in icons_row], lag_ratio=0.1)
        )
        self.wait(1)

        themes = make_label(
            "Isolation  ·  Linearizability  ·  FIFO  ·  CAP Theorem  ·  Monotonic Reads",
            font_size=17, color=GREY_A,
        )
        themes.move_to(DOWN * 1.5)
        self.play(FadeIn(themes, shift=UP * 0.2))
        self.wait(4)
        self.play(FadeOut(*self.mobjects))
