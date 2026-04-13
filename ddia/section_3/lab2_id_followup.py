import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from manim import (
    config,
    Scene,
    VGroup,
    RoundedRectangle,
    Arrow,
    FadeIn,
    FadeOut,
    GrowArrow,
    AnimationGroup,
    AddTextLetterByLetter,
    ORIGIN,
    UP,
    DOWN,
    LEFT,
    RIGHT,
    BOLD,
    WHITE,
    GREY_A,
    GREY_B,
    BLUE,
    BLUE_B,
    GREEN,
    GREEN_B,
    RED,
    ORANGE,
    TEAL,
    PURPLE,
    YELLOW,
)

from libs.ddia_components import (
    DARK_BG,
    ICON_DATABASE,
    ICON_CHECK,
    ICON_CODE,
    ICON_STRUCTURE,
    ICON_DANGER,
    ICON_BOOK,
    make_label,
    make_icon,
    make_icon_card,
    make_code_text,
    create_rect_glow,
)

config.background_color = "#0D1117"

ICON_TECH_MYSQL = "assets/icons/tech/mysql.svg"

# ── MySQL DDL color map ───────────────────────────────────────────────
MYSQL_T2C = {
    "CREATE": "#C586C0",
    "TABLE": "#C586C0",
    "AUTO_INCREMENT": "#C586C0",
    "PRIMARY": "#C586C0",
    "KEY": "#C586C0",
    "UNIQUE": "#C586C0",
    "NOT": "#C586C0",
    "NULL": "#C586C0",
    "BIGINT": "#4EC9B0",
    "VARCHAR": "#4EC9B0",
    "TINYINT": "#4EC9B0",
    "TIMESTAMP": "#4EC9B0",
    "CHAR": "#4EC9B0",
    "ratings": "#9CDCFE",
    "id": "#9CDCFE",
    "user_id": "#9CDCFE",
    "movie_id": "#9CDCFE",
    "rating": "#9CDCFE",
    "uq_user_movie": "#CE9178",
    "idx_movie_id": "#CE9178",
    "CURRENT_TIMESTAMP": "#CE9178",
    "(": "#FFD700",
    ")": "#FFD700",
    ",": "#D4D4D4",
    ";": "#D4D4D4",
}


class Lab2IDFollowUp(Scene):
    def construct(self):
        self.scene_title()
        self.scene_the_question()
        self.scene_auto_increment()
        self.scene_composite_pk()
        self.scene_uuid()
        self.scene_atomicity()
        self.scene_comparison()
        self.scene_verdict()

    # ─── Helper ───────────────────────────────────────────────────────
    def _step_box(self, text, color, width=1.95, height=0.55):
        box = RoundedRectangle(
            corner_radius=0.08,
            width=width,
            height=height,
            fill_color=DARK_BG,
            fill_opacity=0.9,
            stroke_color=color,
            stroke_width=1.3,
        )
        lbl = make_label(text, font_size=10, color=color)
        lbl.move_to(box.get_center())
        return VGroup(box, lbl)

    # ─── Scene 1: Title ───────────────────────────────────────────────
    def scene_title(self):
        icon = make_icon(ICON_TECH_MYSQL, color=BLUE, height=1.1)
        title = make_label(
            "Lab 2 Follow-Up: Ratings ID Strategy",
            font_size=32,
            color=BLUE,
        )
        subtitle = make_label(
            "Auto-Increment  ·  Composite Key  ·  UUID",
            font_size=18,
            color=GREY_B,
        )
        VGroup(icon, title, subtitle).arrange(DOWN, buff=0.4)

        self.play(FadeIn(icon, shift=DOWN * 0.3))
        self.wait(0.4)
        self.play(AddTextLetterByLetter(title, time_per_char=0.04))
        self.wait(0.4)
        self.play(FadeIn(subtitle, shift=UP * 0.2))
        self.wait(3)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 2: The Question ────────────────────────────────────────
    def scene_the_question(self):
        header = make_label("The Design Question", font_size=30, color=ORANGE)
        header.to_edge(UP, buff=0.5)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.5)

        options = [
            (ICON_DATABASE, BLUE, "Auto-Increment ID", "BIGINT AUTO_INCREMENT PK"),
            (ICON_STRUCTURE, GREEN, "Composite PK", "PRIMARY KEY (user_id, movie_id)"),
            (ICON_CODE, PURPLE, "UUID", "CHAR(36) PRIMARY KEY"),
        ]
        cards = VGroup()
        for icon_path, color, title, sub in options:
            ic = make_icon(icon_path, color=color, height=0.4)
            t = make_label(title, font_size=13, color=color)
            s = make_label(sub, font_size=10, color=GREY_A)
            content = VGroup(ic, t, s).arrange(DOWN, buff=0.1)
            box = RoundedRectangle(
                corner_radius=0.12,
                width=3.6,
                height=1.9,
                fill_color=DARK_BG,
                fill_opacity=0.9,
                stroke_color=color,
                stroke_width=1.5,
            )
            content.move_to(box.get_center())
            cards.add(VGroup(box, content))

        cards.arrange(RIGHT, buff=0.5).move_to(DOWN * 0.2)

        for card in cards:
            self.play(FadeIn(card, shift=UP * 0.2), run_time=0.5)
            self.wait(0.4)

        question = make_label(
            "One user, one movie, one rating — which key enforces that?",
            font_size=16,
            color=YELLOW,
        )
        question.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(question, shift=UP * 0.2))
        self.wait(3)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 3: Option A — Auto-Increment ──────────────────────────
    def scene_auto_increment(self):
        header = make_label("Option A — Auto-Increment ID", font_size=28, color=BLUE)
        header.to_edge(UP, buff=0.5)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.5)

        sql = (
            "CREATE TABLE ratings (\n"
            "  id       BIGINT AUTO_INCREMENT\n"
            "             PRIMARY KEY,\n"
            "  user_id  VARCHAR(64) NOT NULL,\n"
            "  movie_id VARCHAR(32) NOT NULL,\n"
            "  rating   TINYINT NOT NULL,\n"
            "  UNIQUE KEY uq_user_movie\n"
            "    (user_id, movie_id)\n"
            ");"
        )
        code = make_code_text(sql, font_size=11, t2c=MYSQL_T2C)
        code.move_to(LEFT * 2.8 + DOWN * 0.3)
        self.play(FadeIn(code, shift=UP * 0.2))
        self.wait(0.8)

        pros = [
            (GREEN, "Compact PK — 8 bytes"),
            (GREEN, "ORM / JPA default — easy setup"),
            (GREEN, "Human-readable for debugging"),
        ]
        cons = [
            (RED, "ID unknown before write"),
            (RED, "Must add UNIQUE(user_id, movie_id)"),
            (RED, "Counter NOT rolled back → gaps"),
            (RED, "Conflicts in multi-master setups"),
        ]

        pros_title = make_label("Pros", font_size=13, color=GREEN)
        pros_items = VGroup(
            *[make_label("+ " + t, font_size=11, color=c) for c, t in pros]
        ).arrange(DOWN, buff=0.08, aligned_edge=LEFT)
        pros_group = VGroup(pros_title, pros_items).arrange(
            DOWN, buff=0.1, aligned_edge=LEFT
        )

        cons_title = make_label("Cons", font_size=13, color=RED)
        cons_items = VGroup(
            *[make_label("- " + t, font_size=11, color=c) for c, t in cons]
        ).arrange(DOWN, buff=0.08, aligned_edge=LEFT)
        cons_group = VGroup(cons_title, cons_items).arrange(
            DOWN, buff=0.1, aligned_edge=LEFT
        )

        VGroup(pros_group, cons_group).arrange(
            DOWN, buff=0.3, aligned_edge=LEFT
        ).move_to(RIGHT * 3.4 + DOWN * 0.3)

        self.play(FadeIn(pros_group, shift=LEFT * 0.2))
        self.wait(0.5)
        self.play(FadeIn(cons_group, shift=LEFT * 0.2))
        self.wait(3)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 4: Option B — Composite PK ────────────────────────────
    def scene_composite_pk(self):
        header = make_label(
            "Option B — Composite Primary Key", font_size=28, color=GREEN
        )
        header.to_edge(UP, buff=0.5)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.5)

        sql = (
            "CREATE TABLE ratings (\n"
            "  user_id  VARCHAR(64) NOT NULL,\n"
            "  movie_id VARCHAR(32) NOT NULL,\n"
            "  rating   TINYINT NOT NULL,\n"
            "  PRIMARY KEY (user_id, movie_id),\n"
            "  KEY idx_movie_id (movie_id)\n"
            ");"
        )
        code = make_code_text(sql, font_size=11, t2c=MYSQL_T2C)
        code.move_to(LEFT * 2.8 + DOWN * 0.3)
        glow = create_rect_glow(code.bg, color=GREEN)
        self.play(FadeIn(VGroup(glow, code), shift=UP * 0.2))
        self.wait(0.8)

        pros = [
            (GREEN, "Uniqueness enforced by PK itself"),
            (GREEN, "Direct O(1) PK lookup"),
            (GREEN, "Key is always known before write"),
            (GREEN, "Natural upsert: ON DUPLICATE KEY"),
        ]
        cons = [
            (ORANGE, "Wider PK — larger index entries"),
            (ORANGE, "Needs secondary idx on movie_id"),
        ]

        pros_title = make_label("Pros", font_size=13, color=GREEN)
        pros_items = VGroup(
            *[make_label("+ " + t, font_size=11, color=c) for c, t in pros]
        ).arrange(DOWN, buff=0.08, aligned_edge=LEFT)
        pros_group = VGroup(pros_title, pros_items).arrange(
            DOWN, buff=0.1, aligned_edge=LEFT
        )

        cons_title = make_label("Cons", font_size=13, color=ORANGE)
        cons_items = VGroup(
            *[make_label("- " + t, font_size=11, color=c) for c, t in cons]
        ).arrange(DOWN, buff=0.08, aligned_edge=LEFT)
        cons_group = VGroup(cons_title, cons_items).arrange(
            DOWN, buff=0.1, aligned_edge=LEFT
        )

        VGroup(pros_group, cons_group).arrange(
            DOWN, buff=0.3, aligned_edge=LEFT
        ).move_to(RIGHT * 3.4 + DOWN * 0.3)

        self.play(FadeIn(pros_group, shift=LEFT * 0.2))
        self.wait(0.5)
        self.play(FadeIn(cons_group, shift=LEFT * 0.2))

        badge = make_label("★  Recommended for this lab", font_size=14, color=GREEN)
        badge.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(badge, shift=UP * 0.2))
        self.wait(3)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 5: Option C — UUID ─────────────────────────────────────
    def scene_uuid(self):
        header = make_label("Option C — UUID Primary Key", font_size=28, color=PURPLE)
        header.to_edge(UP, buff=0.5)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.5)

        sql = (
            "CREATE TABLE ratings (\n"
            "  id       CHAR(36) PRIMARY KEY,\n"
            "  user_id  VARCHAR(64) NOT NULL,\n"
            "  movie_id VARCHAR(32) NOT NULL,\n"
            "  rating   TINYINT NOT NULL,\n"
            "  UNIQUE KEY uq_user_movie\n"
            "    (user_id, movie_id)\n"
            ");"
        )
        code = make_code_text(sql, font_size=11, t2c=MYSQL_T2C)
        code.move_to(LEFT * 2.8 + DOWN * 0.3)
        self.play(FadeIn(code, shift=UP * 0.2))
        self.wait(0.8)

        pros = [
            (GREEN, "ID pre-generated on client"),
            (GREEN, "Safe for distributed / multi-master"),
            (GREEN, "No server coordination needed"),
        ]
        cons = [
            (RED, "Largest PK — 36 bytes (CHAR)"),
            (RED, "Random UUIDs fragment B-tree index"),
            (RED, "Hard to read / debug in SQL"),
            (RED, "Still needs UNIQUE(user_id, movie_id)"),
        ]

        pros_title = make_label("Pros", font_size=13, color=GREEN)
        pros_items = VGroup(
            *[make_label("+ " + t, font_size=11, color=c) for c, t in pros]
        ).arrange(DOWN, buff=0.08, aligned_edge=LEFT)
        pros_group = VGroup(pros_title, pros_items).arrange(
            DOWN, buff=0.1, aligned_edge=LEFT
        )

        cons_title = make_label("Cons", font_size=13, color=RED)
        cons_items = VGroup(
            *[make_label("- " + t, font_size=11, color=c) for c, t in cons]
        ).arrange(DOWN, buff=0.08, aligned_edge=LEFT)
        cons_group = VGroup(cons_title, cons_items).arrange(
            DOWN, buff=0.1, aligned_edge=LEFT
        )

        VGroup(pros_group, cons_group).arrange(
            DOWN, buff=0.3, aligned_edge=LEFT
        ).move_to(RIGHT * 3.4 + DOWN * 0.3)

        self.play(FadeIn(pros_group, shift=LEFT * 0.2))
        self.wait(0.5)
        self.play(FadeIn(cons_group, shift=LEFT * 0.2))
        self.wait(3)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 6: Atomicity Deep-Dive ────────────────────────────────
    def scene_atomicity(self):
        header = make_label(
            "Atomicity: When Does the App Know the ID?",
            font_size=25,
            color=ORANGE,
        )
        header.to_edge(UP, buff=0.4)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.5)

        sub = make_label(
            "Critical for multi-table transactions — two round-trips vs one batch?",
            font_size=13,
            color=GREY_A,
        )
        sub.next_to(header, DOWN, buff=0.18)
        self.play(FadeIn(sub, shift=UP * 0.1))
        self.wait(0.4)

        # ── Lane 1: Auto-Increment ────────────────────────────────────
        ai_label = make_label("AUTO-INC", font_size=11, color=BLUE)
        s1 = self._step_box("INSERT\n(no id)", BLUE)
        s2 = self._step_box("DB: counter++\nallocate id", BLUE)
        s3 = self._step_box("Row\nwritten", GREY_B)
        s4 = self._step_box("LAST_INSERT\n_ID( )", BLUE)

        ai_steps = VGroup(s1, s2, s3, s4).arrange(RIGHT, buff=0.22)
        ai_a1 = Arrow(
            s1.get_right(),
            s2.get_left(),
            buff=0.05,
            stroke_width=2,
            color=BLUE,
            tip_length=0.1,
        )
        ai_a2 = Arrow(
            s2.get_right(),
            s3.get_left(),
            buff=0.05,
            stroke_width=2,
            color=BLUE,
            tip_length=0.1,
        )
        ai_a3 = Arrow(
            s3.get_right(),
            s4.get_left(),
            buff=0.05,
            stroke_width=2,
            color=BLUE,
            tip_length=0.1,
        )

        ai_known = make_label("ID known ▲", font_size=9, color=RED)
        ai_known.next_to(s4, DOWN, buff=0.05)
        ai_gap = make_label("⚠ rollback → gap in sequence", font_size=9, color=RED)
        ai_gap.next_to(s2, DOWN, buff=0.05)

        ai_lane = VGroup(ai_steps, ai_a1, ai_a2, ai_a3, ai_known, ai_gap)
        ai_label.next_to(ai_steps, LEFT, buff=0.2)
        ai_full = VGroup(ai_label, ai_lane)
        ai_full.move_to(UP * 1.0)

        # ── Lane 2: UUID ──────────────────────────────────────────────
        uuid_label = make_label("UUID", font_size=11, color=PURPLE)
        u1 = self._step_box("UUID =\ngen( )", PURPLE)
        u2 = self._step_box("INSERT\n(with id)", PURPLE)
        u3 = self._step_box("Row\nwritten", GREY_B)
        u4 = self._step_box("Done ✓", GREEN)

        uuid_steps = VGroup(u1, u2, u3, u4).arrange(RIGHT, buff=0.22)
        uuid_a1 = Arrow(
            u1.get_right(),
            u2.get_left(),
            buff=0.05,
            stroke_width=2,
            color=PURPLE,
            tip_length=0.1,
        )
        uuid_a2 = Arrow(
            u2.get_right(),
            u3.get_left(),
            buff=0.05,
            stroke_width=2,
            color=PURPLE,
            tip_length=0.1,
        )
        uuid_a3 = Arrow(
            u3.get_right(),
            u4.get_left(),
            buff=0.05,
            stroke_width=2,
            color=GREEN,
            tip_length=0.1,
        )

        uuid_known = make_label("ID known ▲", font_size=9, color=GREEN)
        uuid_known.next_to(u1, DOWN, buff=0.05)

        uuid_lane = VGroup(uuid_steps, uuid_a1, uuid_a2, uuid_a3, uuid_known)
        uuid_label.next_to(uuid_steps, LEFT, buff=0.2)
        uuid_full = VGroup(uuid_label, uuid_lane)
        uuid_full.move_to(DOWN * 0.3)

        # ── Lane 3: Composite PK ─────────────────────────────────────
        comp_label = make_label("COMPOSITE", font_size=11, color=GREEN)
        c1 = self._step_box("Key =\n(user, movie)", GREEN)
        c2 = self._step_box("INSERT\n(with key)", GREEN)
        c3 = self._step_box("Row\nwritten", GREY_B)
        c4 = self._step_box("Done ✓", GREEN)

        comp_steps = VGroup(c1, c2, c3, c4).arrange(RIGHT, buff=0.22)
        comp_a1 = Arrow(
            c1.get_right(),
            c2.get_left(),
            buff=0.05,
            stroke_width=2,
            color=GREEN,
            tip_length=0.1,
        )
        comp_a2 = Arrow(
            c2.get_right(),
            c3.get_left(),
            buff=0.05,
            stroke_width=2,
            color=GREEN,
            tip_length=0.1,
        )
        comp_a3 = Arrow(
            c3.get_right(),
            c4.get_left(),
            buff=0.05,
            stroke_width=2,
            color=GREEN,
            tip_length=0.1,
        )

        comp_known = make_label("Key IS the data ▲", font_size=9, color=GREEN)
        comp_known.next_to(c1, DOWN, buff=0.05)

        comp_lane = VGroup(comp_steps, comp_a1, comp_a2, comp_a3, comp_known)
        comp_label.next_to(comp_steps, LEFT, buff=0.2)
        comp_full = VGroup(comp_label, comp_lane)
        comp_full.move_to(DOWN * 1.6)

        # Animate row by row
        self.play(FadeIn(ai_full, shift=RIGHT * 0.2))
        self.wait(1.8)
        self.play(FadeIn(uuid_full, shift=RIGHT * 0.2))
        self.wait(1.8)
        self.play(FadeIn(comp_full, shift=RIGHT * 0.2))
        self.wait(1.5)

        insight = make_label(
            "Auto-increment: ID only known after write   |   UUID & Composite: ID pre-known → single atomic batch",
            font_size=12,
            color=YELLOW,
        )
        insight.to_edge(DOWN, buff=0.3)
        self.play(FadeIn(insight, shift=UP * 0.2))
        self.wait(4)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 7: Side-by-Side Comparison ────────────────────────────
    def scene_comparison(self):
        header = make_label("Side-by-Side Comparison", font_size=28, color=TEAL)
        header.to_edge(UP, buff=0.4)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.5)

        col_labels = ["Criterion", "Auto-Increment", "Composite PK", "UUID"]
        col_colors = [WHITE, BLUE, GREEN, PURPLE]
        col_widths = [3.5, 2.7, 2.7, 2.7]

        rows_data = [
            (
                "Enforces 1 rating / user-movie",
                "Extra UNIQUE needed",
                "By PRIMARY KEY ★",
                "Extra UNIQUE needed",
            ),
            (
                "Read: getUserRating(u, m)",
                "2-index lookup",
                "Direct PK lookup ★",
                "2-index lookup",
            ),
            (
                "Read: getTopRated(movie)",
                "idx_movie_id",
                "sec idx movie_id",
                "idx_movie_id",
            ),
            (
                "ID known before write?",
                "No — server-side",
                "Yes — it's the data ★",
                "Yes — client gen ★",
            ),
            ("PK storage size", "8 bytes ★", "~96 bytes", "36 bytes"),
            ("Rollback leaves gap?", "Yes ⚠", "No", "No"),
            ("Distributed / multi-master", "Conflicts possible", "Good", "Best ★"),
        ]

        # Header row
        header_cells = VGroup()
        for text, color, width in zip(col_labels, col_colors, col_widths):
            cell = RoundedRectangle(
                corner_radius=0.06,
                width=width,
                height=0.42,
                fill_color="#21262D",
                fill_opacity=1,
                stroke_color=color,
                stroke_width=1.2,
            )
            lbl = make_label(text, font_size=11, color=color)
            lbl.move_to(cell)
            header_cells.add(VGroup(cell, lbl))
        header_cells.arrange(RIGHT, buff=0.07).next_to(header, DOWN, buff=0.3)
        self.play(FadeIn(header_cells, shift=DOWN * 0.1))
        self.wait(0.2)

        all_rows = VGroup()
        for criterion, auto, comp, uuid in rows_data:
            row = VGroup()
            for text, color, width in zip(
                [criterion, auto, comp, uuid],
                [GREY_A, BLUE_B, GREEN_B, PURPLE],
                col_widths,
            ):
                cell = RoundedRectangle(
                    corner_radius=0.06,
                    width=width,
                    height=0.38,
                    fill_color=DARK_BG,
                    fill_opacity=0.9,
                    stroke_color=GREY_B,
                    stroke_width=0.6,
                )
                lbl = make_label(text, font_size=9, color=color)
                lbl.move_to(cell)
                row.add(VGroup(cell, lbl))
            row.arrange(RIGHT, buff=0.07)
            all_rows.add(row)

        all_rows.arrange(DOWN, buff=0.06).next_to(header_cells, DOWN, buff=0.07)
        for row in all_rows:
            self.play(FadeIn(row, shift=LEFT * 0.2), run_time=0.3)
            self.wait(0.15)
        self.wait(3)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 8: Verdict ────────────────────────────────────────────
    def scene_verdict(self):
        header = make_label("Recommendation", font_size=30, color=GREEN)
        header.to_edge(UP, buff=0.5)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.8)

        rec_icon = make_icon(ICON_STRUCTURE, color=GREEN, height=0.7)
        rec_title = make_label(
            "Composite PK  (user_id, movie_id)", font_size=20, color=GREEN
        )
        rec_content = VGroup(rec_icon, rec_title).arrange(DOWN, buff=0.15)
        rec_box = RoundedRectangle(
            corner_radius=0.15,
            width=5.0,
            height=2.0,
            fill_color=DARK_BG,
            fill_opacity=0.9,
            stroke_color=GREEN,
            stroke_width=1.8,
        )
        rec_content.move_to(rec_box.get_center())
        rec_glow = create_rect_glow(rec_box, color=GREEN)
        rec_card = VGroup(rec_glow, rec_box, rec_content)
        rec_card.move_to(UP * 0.5)
        self.play(FadeIn(rec_card, shift=DOWN * 0.2))
        self.wait(0.8)

        reason = make_label(
            "The business rule 'one user, one movie, one rating'\nis best expressed as the PRIMARY KEY itself.",
            font_size=15,
            color=GREY_A,
        )
        reason.next_to(rec_card, DOWN, buff=0.35)
        self.play(FadeIn(reason, shift=UP * 0.2))
        self.wait(1)

        warning = make_label(
            "Using a surrogate ID?  Always add  UNIQUE KEY (user_id, movie_id)  — missing it corrupts top-rated rankings.",
            font_size=12,
            color=YELLOW,
        )
        warning.to_edge(DOWN, buff=0.45)
        self.play(FadeIn(warning, shift=UP * 0.2))
        self.wait(4)
        self.play(FadeOut(*self.mobjects))
