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
                box_h=0.44, ret_color=None):
        """DDIA-style operation box spanning [t_call, t_ret] at row y."""
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
        op_lbl.move_to(box.get_center())

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
        return VGroup(d1, d2, box, op_lbl), ret_lbl

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

        # Operations — timings chosen so operations overlap meaningfully
        # A: R.write(1)  t=0.4→3.2  (long write overlapping B's first read & C's write start)
        op_a1, ret_a1 = self._op_box(0.4, 3.2, "R.write(1)", "void", ROW_A, TEAL)
        # B: R.read() #1  t=0.8→1.9  (overlaps A's write → can legally read 1)
        op_b1, ret_b1 = self._op_box(0.8, 1.9, "R.read()", "1", ROW_B, BLUE, ret_color=GREEN)
        # C: R.write(2)  t=1.6→3.8  (overlaps end of A's write)
        op_c1, ret_c1 = self._op_box(1.6, 3.8, "R.write(2)", "void", ROW_C, ORANGE)
        # B: R.read() #2  t=2.6→4.3  (overlaps C's write → can still see 1 legally)
        op_b2, ret_b2 = self._op_box(2.6, 4.3, "R.read()", "1", ROW_B, BLUE, ret_color=GREEN)
        # A: Q.write(3)  t=4.9→6.9
        op_a2, ret_a2 = self._op_box(4.9, 6.9, "Q.write(3)", "void", ROW_A, TEAL)
        # C: R.read()  t=5.2→7.2  (sees 2 — C's own write has completed)
        op_c2, ret_c2 = self._op_box(5.2, 7.2, "R.read()", "2", ROW_C, ORANGE, ret_color=GREEN)

        all_ops = [
            (op_a1, ret_a1), (op_b1, ret_b1), (op_c1, ret_c1),
            (op_b2, ret_b2), (op_a2, ret_a2), (op_c2, ret_c2),
        ]
        for op, ret in all_ops:
            self.play(FadeIn(op), run_time=0.35)
            self.play(FadeIn(ret), run_time=0.25)
            self.wait(0.15)

        # Database state markers
        db0 = self._db_marker(0.0, "R=0", DB_Y, GREY_B)
        db1 = self._db_marker(3.2, "R=1", DB_Y, TEAL)
        db2 = self._db_marker(3.8, "R=2", DB_Y, ORANGE)
        for m in [db0, db1, db2]:
            self.play(FadeIn(m), run_time=0.3)
        self.wait(0.6)

        # Reasoning annotation
        reason = make_label(
            "B reads 1 during A's write → valid  |  "
            "B's 2nd read sees 1 → write(2) not yet linearized  |  "
            "C reads 2 after its own write ✓",
            font_size=9, color=GREY_A,
        )
        reason.to_edge(DOWN, buff=0.65)
        self.play(FadeIn(reason))

        badge = self._verdict_badge("YES — History H is Linearizable  ✓", GREEN, width=6.5)
        badge.to_edge(DOWN, buff=0.25)
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

        # Same timings — modified return values to break linearizability
        op_a1, ret_a1 = self._op_box(0.4, 3.2, "R.write(1)", "void", ROW_A, TEAL)
        # B's first read now claims to see 2 — before write(2) is complete
        op_b1, ret_b1 = self._op_box(0.8, 1.9, "R.read()", "2", ROW_B, BLUE, ret_color=ORANGE)
        op_c1, ret_c1 = self._op_box(1.6, 3.8, "R.write(2)", "void", ROW_C, ORANGE)
        op_b2, ret_b2 = self._op_box(2.6, 4.3, "R.read()", "2", ROW_B, BLUE, ret_color=ORANGE)
        op_a2, ret_a2 = self._op_box(4.9, 6.9, "Q.write(3)", "void", ROW_A, TEAL)
        # C's read now returns 1 after B already observed 2 — the violation
        op_c2, ret_c2 = self._op_box(5.2, 7.2, "R.read()", "1  ✗", ROW_C, ORANGE, ret_color=RED)

        for op, ret in [(op_a1, ret_a1), (op_c1, ret_c1), (op_b2, ret_b2),
                        (op_a2, ret_a2)]:
            self.play(FadeIn(op), run_time=0.3)
            self.play(FadeIn(ret), run_time=0.2)

        db0 = self._db_marker(0.0, "R=0", DB_Y, GREY_B)
        db1 = self._db_marker(3.2, "R=1", DB_Y, TEAL)
        db2 = self._db_marker(3.8, "R=2", DB_Y, ORANGE)
        for m in [db0, db1, db2]:
            self.play(FadeIn(m), run_time=0.25)

        # Show B's first read claiming 2 — this is the setup for the violation
        self.play(FadeIn(op_b1), run_time=0.35)
        self.play(FadeIn(ret_b1, shift=RIGHT * 0.1), run_time=0.3)
        self.play(Indicate(ret_b1, color=ORANGE, run_time=1.2))
        self.wait(0.4)

        # Reveal C's regression read with drama
        self.play(FadeIn(op_c2), run_time=0.4)
        self.play(FadeIn(ret_c2, shift=RIGHT * 0.1), run_time=0.4)
        self.play(Indicate(ret_c2, color=RED, run_time=1.5))
        self.wait(0.4)

        # Annotation connecting the two
        arrow_explain = make_label(
            "B already saw R=2  →  C cannot read R=1  (time cannot go backwards)",
            font_size=10, color=RED,
        )
        arrow_explain.to_edge(DOWN, buff=0.65)
        self.play(FadeIn(arrow_explain))

        badge = self._verdict_badge(
            "NOT Linearizable — once R=2 is observed, R=1 can never be returned  ✗",
            RED, width=8.5,
        )
        badge.to_edge(DOWN, buff=0.25)
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
        viols.move_to(RIGHT * 2.0 + DOWN * 1.6)
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
        header = make_label("Q5: Monotonic Reads — Timestamp Solution", font_size=24, color=GREEN)
        header.to_edge(UP, buff=0.35)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.4)

        problem = make_label(
            "Problem: sticky sessions pin client to one replica — fails on replica crash",
            font_size=12, color=RED,
        )
        problem.next_to(header, DOWN, buff=0.28)
        solution_lbl = make_label(
            "Solution: client tracks last-read version (timestamp), passes it as min_timestamp",
            font_size=12, color=GREEN,
        )
        solution_lbl.next_to(problem, DOWN, buff=0.1)
        self.play(FadeIn(problem, shift=UP * 0.1))
        self.play(FadeIn(solution_lbl, shift=UP * 0.1))
        self.wait(0.6)

        # 3-step flow
        steps = [
            (TEAL,   "Step 1",   "Client reads Replica A\ngets value at T=42\nstores T=42 locally"),
            (GREEN,  "Step 2",   "Next query sent\nwith { min_timestamp: 42 }\nto any replica"),
            (ORANGE, "Step 3",   "Replica checks own T:\n≥ 42 → serve read\n< 42 → block & wait"),
        ]
        step_cards = VGroup()
        for color, title, desc in steps:
            title_lbl = make_label(title, font_size=12, color=color)
            desc_lbl = make_label(desc, font_size=10, color=GREY_A)
            content = VGroup(title_lbl, desc_lbl).arrange(DOWN, buff=0.1)
            box = RoundedRectangle(
                corner_radius=0.1, width=3.1, height=1.7,
                fill_color=DARK_BG, fill_opacity=0.9,
                stroke_color=color, stroke_width=1.4,
            )
            content.move_to(box.get_center())
            step_cards.add(VGroup(box, content))

        step_cards.arrange(RIGHT, buff=0.65).move_to(DOWN * 0.4)

        arrows = VGroup()
        for i in range(len(step_cards) - 1):
            a = Arrow(
                step_cards[i].get_right(), step_cards[i + 1].get_left(),
                buff=0.1, stroke_width=2.0, color=GREY_A, tip_length=0.15,
            )
            arrows.add(a)

        for i, card in enumerate(step_cards):
            self.play(FadeIn(card, shift=UP * 0.15), run_time=0.5)
            if i < len(arrows):
                self.play(GrowArrow(arrows[i]), run_time=0.35)
            self.wait(0.3)

        # Advantage bullets
        advantages = VGroup(
            make_label("✓  Any replica can serve — no pinning", font_size=11, color=GREEN),
            make_label("✓  Failover transparent — just pick another replica", font_size=11, color=GREEN),
            make_label("⚠  High replication lag may cause brief blocking", font_size=11, color=ORANGE),
        ).arrange(DOWN, buff=0.12, aligned_edge=LEFT)
        advantages.to_edge(DOWN, buff=0.4)
        self.play(FadeIn(advantages, shift=UP * 0.1))
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
