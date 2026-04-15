import sys
import math
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from manim import (
    config,
    Scene,
    VGroup,
    RoundedRectangle,
    Arrow,
    Circle,
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
    ICON_SERVER,
    ICON_CHECK,
    ICON_DANGER,
    ICON_LOCK,
    ICON_SHIELD,
    ICON_LIGHTNING,
    ICON_CODE,
    ICON_STRUCTURE,
    ICON_BOOK,
    ICON_GRAPH,
    make_label,
    make_icon,
    make_icon_card,
    make_code_text,
    create_rect_glow,
)

config.background_color = "#0D1117"

# ── CQL color map ─────────────────────────────────────────────────────
CQL_T2C = {
    "CREATE": "#C586C0",
    "KEYSPACE": "#C586C0",
    "TABLE": "#C586C0",
    "WITH": "#C586C0",
    "ALTER": "#C586C0",
    "SELECT": "#C586C0",
    "INSERT": "#C586C0",
    "INTO": "#C586C0",
    "FROM": "#C586C0",
    "WHERE": "#C586C0",
    "VALUES": "#C586C0",
    "PRIMARY": "#C586C0",
    "ASC": "#C586C0",
    "DESC": "#C586C0",
    "ORDER": "#C586C0",
    "BY": "#C586C0",
    "CLUSTERING": "#C586C0",
    "QUORUM": "#4EC9B0",
    "ONE": "#4EC9B0",
    "TWO": "#4EC9B0",
    "ALL": "#4EC9B0",
    "ANY": "#4EC9B0",
    "CONSISTENCY": "#4EC9B0",
    "VARCHAR": "#4EC9B0",
    "INT": "#4EC9B0",
    "SimpleStrategy": "#CE9178",
    "bookstore": "#9CDCFE",
    "name": "#9CDCFE",
    "category": "#9CDCFE",
    "year": "#9CDCFE",
    "title": "#9CDCFE",
    "(": "#FFD700",
    ")": "#FFD700",
    ";": "#D4D4D4",
    ",": "#D4D4D4",
}


class ConsistencyLab(Scene):
    def construct(self):
        self.scene_title()
        self.scene_lab_overview()
        self.scene_cluster_architecture()
        self.scene_data_model()
        self.scene_consistency_levels()
        self.scene_quorum_formula()
        self.scene_rf1_experiment()
        self.scene_rf2_experiment()
        self.scene_rf3_experiment()
        self.scene_tips()
        self.scene_closing()

    # ─── Helpers ──────────────────────────────────────────────────────
    def _node_card(self, label, color=BLUE, glow=True):
        ic = make_icon(ICON_SERVER, color=color, height=0.35)
        lbl = make_label(label, font_size=10, color=color)
        content = VGroup(ic, lbl).arrange(DOWN, buff=0.06)
        box = RoundedRectangle(
            corner_radius=0.1,
            width=2.1,
            height=1.15,
            fill_color=DARK_BG,
            fill_opacity=0.9,
            stroke_color=color,
            stroke_width=1.4,
        )
        content.move_to(box.get_center())
        if glow:
            g = create_rect_glow(box, color=color)
            return VGroup(g, box, content)
        return VGroup(box, content)

    def _fail_overlay(self, card):
        x = make_label("✗", font_size=38, color=RED)
        x.move_to(card.get_center())
        return x

    def _quorum_badge(self, text, success=True):
        color = GREEN if success else RED
        box = RoundedRectangle(
            corner_radius=0.1,
            width=8.5,
            height=0.58,
            fill_color=DARK_BG,
            fill_opacity=0.95,
            stroke_color=color,
            stroke_width=1.5,
        )
        lbl = make_label(text, font_size=12, color=color)
        lbl.move_to(box.get_center())
        return VGroup(box, lbl)

    # ─── Scene 1: Title ───────────────────────────────────────────────
    def scene_title(self):
        icon = make_icon(ICON_DATABASE, color=TEAL, height=1.1)
        title = make_label("Lab 3: Consistency", font_size=36, color=TEAL)
        sub = make_label(
            "Replication  ·  Quorum  ·  Tunable Consistency",
            font_size=18,
            color=GREY_B,
        )
        VGroup(icon, title, sub).arrange(DOWN, buff=0.4)
        self.play(FadeIn(icon, shift=DOWN * 0.3))
        self.wait(0.4)
        self.play(AddTextLetterByLetter(title, time_per_char=0.04))
        self.wait(0.4)
        self.play(FadeIn(sub, shift=UP * 0.2))
        self.wait(3)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 2: Lab Overview ────────────────────────────────────────
    def scene_lab_overview(self):
        header = make_label("What Will You Do?", font_size=30, color=GREEN)
        header.to_edge(UP, buff=0.5)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.8)

        steps = [
            (
                ICON_SERVER,
                BLUE,
                "A) RF = 1",
                "Create cluster, insert data, pause nodes one by one",
            ),
            (
                ICON_DATABASE,
                TEAL,
                "B) RF = 2",
                "Alter keyspace to RF=2 — test QUORUM with a node down",
            ),
            (
                ICON_SHIELD,
                ORANGE,
                "C) RF = 3",
                "Alter to RF=3 — repeat node-down experiments",
            ),
            (
                ICON_BOOK,
                PURPLE,
                "D & E) Matrices",
                "Record Success / Failure for every scenario",
            ),
            (
                ICON_GRAPH,
                GREEN,
                "F) Report",
                "Explain your results and answer discussion questions",
            ),
        ]

        rows = VGroup()
        for icon_path, color, title, desc in steps:
            ic = make_icon(icon_path, color=color, height=0.28)
            t = make_label(title, font_size=13, color=color)
            d = make_label(desc, font_size=11, color=GREY_A)
            content = VGroup(ic, t, d).arrange(RIGHT, buff=0.18)
            box = RoundedRectangle(
                corner_radius=0.1,
                width=content.width + 0.5,
                height=content.height + 0.25,
                fill_color=DARK_BG,
                fill_opacity=0.9,
                stroke_color=color,
                stroke_width=1.1,
            )
            content.move_to(box.get_center())
            rows.add(VGroup(box, content))

        rows.arrange(DOWN, buff=0.1).next_to(header, DOWN, buff=0.4)
        for row in rows:
            self.play(FadeIn(row, shift=LEFT * 0.3), run_time=0.5)
            self.wait(0.55)

        note = make_label(
            "Groups of 3 — each student changes a column value between inserts!",
            font_size=18,
            color=YELLOW,
        )
        note.to_edge(DOWN, buff=0.4)
        self.play(FadeIn(note, shift=UP * 0.2))
        self.wait(3)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 3: Cluster Architecture ───────────────────────────────
    def scene_cluster_architecture(self):
        header = make_label("3-Node Cassandra Ring", font_size=30, color=TEAL)
        header.to_edge(UP, buff=0.4)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.5)

        ring = Circle(
            radius=2.1, stroke_color=GREY_B, stroke_width=1.0, stroke_opacity=0.45
        )
        ring_center = DOWN * 0.25
        ring.move_to(ring_center)
        self.play(FadeIn(ring))

        angles = [90, 210, 330]
        colors = [BLUE, GREEN, ORANGE]
        node_labels = ["Node 1\n(seed)", "Node 2", "Node 3"]
        node_cards = []

        for angle, color, label in zip(angles, colors, node_labels):
            pos = ring_center + np.array(
                [
                    2.1 * math.cos(math.radians(angle)),
                    2.1 * math.sin(math.radians(angle)),
                    0,
                ]
            )
            card = self._node_card(label, color=color, glow=True)
            card.move_to(pos)
            node_cards.append(card)
            self.play(FadeIn(card, shift=(ring_center - pos) * 0.15), run_time=0.5)
            self.wait(0.2)

        # Gossip arrows between adjacent nodes — use edge points so arrows
        # don't overlap the card boxes.
        for i in range(3):
            j = (i + 1) % 3
            direction = node_cards[j].get_center() - node_cards[i].get_center()
            direction /= np.linalg.norm(direction)
            start = node_cards[i].get_edge_center(direction)
            end = node_cards[j].get_edge_center(-direction)
            a = Arrow(
                start,
                end,
                buff=0.06,
                stroke_width=1.4,
                color=GREY_A,
                tip_length=0.09,
            )
            self.play(GrowArrow(a), run_time=0.35)

        gossip = make_label(
            "gossip protocol keeps every node in sync", font_size=15, color=GREY_A
        )
        gossip.to_edge(DOWN, buff=1.05)
        token = make_label(
            "Consistent hashing: partition key  →  token  →  replica node(s)",
            font_size=17,
            color=YELLOW,
        )
        token.to_edge(DOWN, buff=0.45)
        self.play(FadeIn(gossip, shift=UP * 0.1))
        self.wait(0.5)
        self.play(FadeIn(token, shift=UP * 0.1))
        self.wait(3)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 4: Cassandra Data Model ───────────────────────────────
    def scene_data_model(self):
        header = make_label("Primary Key Anatomy", font_size=30, color=BLUE)
        header.to_edge(UP, buff=0.4)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.5)

        # Partition key brick
        pk_lbl = make_label("PARTITION KEY", font_size=10, color=BLUE)
        pk_val = make_label("name", font_size=16, color=BLUE)
        pk_box = RoundedRectangle(
            corner_radius=0.1,
            width=3.0,
            height=1.0,
            fill_color=DARK_BG,
            fill_opacity=0.9,
            stroke_color=BLUE,
            stroke_width=2.0,
        )
        pk_glow = create_rect_glow(pk_box, color=BLUE)
        VGroup(pk_lbl, pk_val).arrange(DOWN, buff=0.06).move_to(pk_box.get_center())
        pk_group = VGroup(pk_glow, pk_box, pk_lbl, pk_val)

        # Clustering column bricks
        cl_cols = [("category", TEAL), ("year", PURPLE), ("title", ORANGE)]
        cl_bricks = VGroup()
        for col, color in cl_cols:
            cl_lbl = make_label("CLUSTERING", font_size=9, color=color)
            cl_val = make_label(col, font_size=14, color=color)
            cl_box = RoundedRectangle(
                corner_radius=0.1,
                width=2.4,
                height=1.0,
                fill_color=DARK_BG,
                fill_opacity=0.9,
                stroke_color=color,
                stroke_width=1.5,
            )
            VGroup(cl_lbl, cl_val).arrange(DOWN, buff=0.06).move_to(cl_box.get_center())
            cl_bricks.add(VGroup(cl_box, cl_lbl, cl_val))

        key_strip = VGroup(pk_group, *cl_bricks).arrange(RIGHT, buff=0.08)
        key_strip.move_to(UP * 0.6)

        self.play(FadeIn(pk_group, shift=DOWN * 0.2))
        for brick in cl_bricks:
            self.play(FadeIn(brick, shift=DOWN * 0.2), run_time=0.4)

        note_pk = make_label(
            "Partition key → hashed to token → determines which node(s) store this row",
            font_size=12,
            color=BLUE,
        )
        note_cl = make_label(
            "Clustering columns → sort rows within a partition on disk",
            font_size=12,
            color=TEAL,
        )
        VGroup(note_pk, note_cl).arrange(DOWN, buff=0.14).move_to(DOWN * 0.7)
        self.play(FadeIn(note_pk, shift=UP * 0.1))
        self.wait(0.5)
        self.play(FadeIn(note_cl, shift=UP * 0.1))
        self.wait(0.8)

        cql = (
            "CREATE TABLE bookstore.books (\n"
            "  name VARCHAR, category VARCHAR,\n"
            "  year INT,  title VARCHAR,\n"
            "  PRIMARY KEY ((name), category, year, title)\n"
            ") WITH CLUSTERING ORDER BY\n"
            "  (category ASC, year DESC, title ASC);"
        )
        code = make_code_text(cql, font_size=11, t2c=CQL_T2C)
        code.to_edge(DOWN, buff=0.25)
        self.play(FadeIn(code, shift=UP * 0.2))
        self.wait(3)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 5: Consistency Levels ─────────────────────────────────
    def scene_consistency_levels(self):
        header = make_label("Cassandra Consistency Levels", font_size=28, color=TEAL)
        header.to_edge(UP, buff=0.4)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.5)

        levels = [
            (GREEN, "ONE", "1 replica must ack", "Fastest — may return stale data"),
            (TEAL, "TWO", "2 replicas must ack", "Middle ground"),
            (
                ORANGE,
                "QUORUM",
                "⌊RF/2⌋ + 1 must ack",
                "Strong (R + W > RF) — lab default",
            ),
            (RED, "ALL", "All RF replicas must ack", "Slowest — 1 down = unavailable"),
            (
                GREY_A,
                "ANY (W only)",
                "1 node or hinted handoff",
                "Highest availability, weakest durability",
            ),
        ]

        rows = VGroup()
        for color, level, req, tradeoff in levels:
            level_l = make_label(level, font_size=13, color=color)
            req_l = make_label(req, font_size=11, color=WHITE)
            tradeoff_l = make_label(tradeoff, font_size=11, color=GREY_A)
            content = VGroup(level_l, req_l, tradeoff_l).arrange(RIGHT, buff=0.55)
            box = RoundedRectangle(
                corner_radius=0.1,
                width=content.width + 0.6,
                height=content.height + 0.25,
                fill_color=DARK_BG,
                fill_opacity=0.9,
                stroke_color=color,
                stroke_width=1.1,
            )
            content.move_to(box.get_center())
            rows.add(VGroup(box, content))

        rows.arrange(DOWN, buff=0.1).next_to(header, DOWN, buff=0.35)
        for row in rows:
            self.play(FadeIn(row, shift=LEFT * 0.2), run_time=0.4)
            self.wait(0.45)

        speed = make_label(
            "Speed  ←————————————————————→  Safety", font_size=18, color=YELLOW
        )
        speed.to_edge(DOWN, buff=0.4)
        self.play(FadeIn(speed, shift=UP * 0.2))
        self.wait(3)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 6: Quorum Formula ──────────────────────────────────────
    def scene_quorum_formula(self):
        header = make_label("The Quorum Formula", font_size=30, color=ORANGE)
        header.to_edge(UP, buff=0.4)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.5)

        # Large R + W > RF
        r_l = make_label("R", font_size=56, color=TEAL)
        plus = make_label("+", font_size=56, color=WHITE)
        w_l = make_label("W", font_size=56, color=ORANGE)
        gt = make_label(">", font_size=56, color=WHITE)
        rf_l = make_label("RF", font_size=56, color=PURPLE)
        formula = VGroup(r_l, plus, w_l, gt, rf_l).arrange(RIGHT, buff=0.28)
        formula.move_to(UP * 0.9)
        self.play(
            AnimationGroup(
                *[FadeIn(m, shift=DOWN * 0.15) for m in formula],
                lag_ratio=0.15,
            )
        )
        self.wait(0.5)

        notes = (
            VGroup(
                make_label("R = read CL", font_size=14, color=TEAL),
                make_label("W = write CL", font_size=14, color=ORANGE),
                make_label("RF = replication factor", font_size=14, color=PURPLE),
            )
            .arrange(RIGHT, buff=0.7)
            .next_to(formula, DOWN, buff=0.3)
        )
        self.play(FadeIn(notes))
        self.wait(0.6)

        # Three RF example cards
        ex_data = [
            (GREY_B, "RF = 1", "Q = 1", "0 failures tolerated"),
            (ORANGE, "RF = 2", "Q = 2 (ALL!)", "0 failures tolerated"),
            (GREEN, "RF = 3 ★", "Q = 2", "1 failure tolerated"),
        ]
        ex_cards = VGroup()
        for color, rf, q, note in ex_data:
            rf_l = make_label(rf, font_size=13, color=color)
            q_l = make_label(q, font_size=12, color=WHITE)
            n_l = make_label(note, font_size=11, color=color)
            content = VGroup(rf_l, q_l, n_l).arrange(DOWN, buff=0.1)
            box = RoundedRectangle(
                corner_radius=0.12,
                width=3.3,
                height=1.5,
                fill_color=DARK_BG,
                fill_opacity=0.9,
                stroke_color=color,
                stroke_width=1.5,
            )
            content.move_to(box.get_center())
            if color == GREEN:
                g = create_rect_glow(box, color=GREEN)
                ex_cards.add(VGroup(g, box, content))
            else:
                ex_cards.add(VGroup(box, content))

        ex_cards.arrange(RIGHT, buff=0.4).next_to(notes, DOWN, buff=0.4)
        self.play(
            AnimationGroup(
                *[FadeIn(c, shift=UP * 0.2) for c in ex_cards], lag_ratio=0.2
            )
        )
        self.wait(1.5)

        take = make_label(
            "RF=3 + QUORUM  →  2 + 2 = 4 > 3  ✓  Best production default",
            font_size=18,
            color=YELLOW,
        )
        take.to_edge(DOWN, buff=0.4)
        self.play(FadeIn(take, shift=UP * 0.2))
        self.wait(3)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 7: RF = 1 Experiments ─────────────────────────────────
    def scene_rf1_experiment(self):
        header = make_label("RF = 1  —  Single Copy", font_size=28, color=GREY_B)
        header.to_edge(UP, buff=0.4)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.5)

        n1 = self._node_card("Node 1\n(replica)", color=BLUE, glow=True)
        n2 = self._node_card("Node 2", color=GREY_B, glow=False)
        n3 = self._node_card("Node 3", color=GREY_B, glow=False)
        nodes = VGroup(n1, n2, n3).arrange(RIGHT, buff=0.9).move_to(UP * 0.7)

        note = make_label(
            "With RF=1, exactly 1 node holds the partition.",
            font_size=13,
            color=GREY_A,
        )
        note.next_to(nodes, DOWN, buff=0.4)
        self.play(FadeIn(nodes, shift=DOWN * 0.1))
        self.play(FadeIn(note))
        self.wait(1)

        # Pause Node 1 (the owner) — FAIL
        fail1 = self._fail_overlay(n1)
        self.play(FadeIn(fail1))
        n1.set_opacity(0.3)
        r1 = self._quorum_badge(
            "Node 1 down: no replica available  ✗  FAIL  — no CL can help",
            success=False,
        )
        r1.next_to(note, DOWN, buff=0.3)
        self.play(FadeIn(r1, shift=UP * 0.1))
        self.wait(1.5)

        # Restore, pause Node 2 (non-owner) — SUCCESS
        self.play(FadeOut(fail1, r1))
        n1.set_opacity(1.0)
        fail2 = self._fail_overlay(n2)
        self.play(FadeIn(fail2))
        n2.set_opacity(0.3)
        r2 = self._quorum_badge(
            "Node 2 down: replica on Node 1 still up  ✓  SUCCESS", success=True
        )
        r2.next_to(note, DOWN, buff=0.3)
        self.play(FadeIn(r2, shift=UP * 0.1))
        self.wait(2)

        tip = make_label(
            "RF=1 means zero fault tolerance — avoid in production.",
            font_size=17,
            color=ORANGE,
        )
        tip.to_edge(DOWN, buff=0.4)
        self.play(FadeIn(tip))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 8: RF = 2 Experiments ─────────────────────────────────
    def scene_rf2_experiment(self):
        header = make_label("RF = 2  —  Two Copies", font_size=28, color=ORANGE)
        header.to_edge(UP, buff=0.4)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.5)

        n1 = self._node_card("Node 1\n(replica)", color=ORANGE, glow=True)
        n2 = self._node_card("Node 2\n(replica)", color=ORANGE, glow=True)
        n3 = self._node_card("Node 3", color=GREY_B, glow=False)
        nodes = VGroup(n1, n2, n3).arrange(RIGHT, buff=0.9).move_to(UP * 0.9)

        qnote = make_label(
            "QUORUM with RF=2  →  ⌊2/2⌋+1 = 2  (both replicas must respond = ALL)",
            font_size=13,
            color=ORANGE,
        )
        qnote.next_to(nodes, DOWN, buff=0.35)
        self.play(FadeIn(nodes, shift=DOWN * 0.1))
        self.play(FadeIn(qnote))
        self.wait(0.8)

        # Down Node 1 (replica) → FAIL
        fail1 = self._fail_overlay(n1)
        self.play(FadeIn(fail1))
        n1.set_opacity(0.3)
        r1 = self._quorum_badge(
            "Node 1 down: QUORUM needs 2 — only 1 available  ✗  FAIL", success=False
        )
        r1.next_to(qnote, DOWN, buff=0.3)
        self.play(FadeIn(r1))
        self.wait(0.8)
        cl_tip = make_label(
            "Lower to CL ONE → succeeds (1 replica still available)",
            font_size=12,
            color=GREEN,
        )
        cl_tip.next_to(r1, DOWN, buff=0.18)
        self.play(FadeIn(cl_tip))
        self.wait(1.5)

        # Restore; down Node 3 (non-replica) → SUCCESS
        self.play(FadeOut(fail1, r1, cl_tip))
        n1.set_opacity(1.0)
        fail3 = self._fail_overlay(n3)
        self.play(FadeIn(fail3))
        n3.set_opacity(0.3)
        r3 = self._quorum_badge(
            "Node 3 down (no replica): both replicas up  ✓  SUCCESS", success=True
        )
        r3.next_to(qnote, DOWN, buff=0.3)
        self.play(FadeIn(r3))
        self.wait(3)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 9: RF = 3 Experiments ─────────────────────────────────
    def scene_rf3_experiment(self):
        header = make_label("RF = 3  —  Full Replication", font_size=28, color=GREEN)
        header.to_edge(UP, buff=0.4)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.5)

        n1 = self._node_card("Node 1\n(replica)", color=GREEN, glow=True)
        n2 = self._node_card("Node 2\n(replica)", color=GREEN, glow=True)
        n3 = self._node_card("Node 3\n(replica)", color=GREEN, glow=True)
        nodes = VGroup(n1, n2, n3).arrange(RIGHT, buff=0.9).move_to(UP * 0.95)

        qnote = make_label(
            "QUORUM with RF=3  →  ⌊3/2⌋+1 = 2  (tolerates 1 node failure)",
            font_size=13,
            color=GREEN,
        )
        qnote.next_to(nodes, DOWN, buff=0.3)
        self.play(FadeIn(nodes, shift=DOWN * 0.1))
        self.play(FadeIn(qnote))
        self.wait(0.8)

        # Down 1 node → still OK
        fail1 = self._fail_overlay(n1)
        self.play(FadeIn(fail1))
        n1.set_opacity(0.3)
        r1 = self._quorum_badge(
            "1 node down: QUORUM needs 2 — 2 available  ✓  SUCCESS", success=True
        )
        r1.next_to(qnote, DOWN, buff=0.3)
        self.play(FadeIn(r1))
        self.wait(1.5)

        # Down 2nd node → FAIL
        fail2 = self._fail_overlay(n2)
        self.play(FadeIn(fail2))
        n2.set_opacity(0.3)
        r2 = self._quorum_badge(
            "2 nodes down: QUORUM needs 2 — only 1 available  ✗  FAIL", success=False
        )
        r2.next_to(r1, DOWN, buff=0.12)
        self.play(FadeIn(r2))
        self.wait(1)

        cl_tip = make_label(
            "CL ONE with 2 nodes down may still work if Node 3 holds the partition.",
            font_size=16,
            color=ORANGE,
        )
        cl_tip.to_edge(DOWN, buff=0.4)
        self.play(FadeIn(cl_tip))
        self.wait(3)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 10: Tips & Tricks ──────────────────────────────────────
    def scene_tips(self):
        header = make_label("Cassandra Tips & Tricks", font_size=28, color=ORANGE)
        header.to_edge(UP, buff=0.4)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.5)

        tips = [
            (
                ICON_SERVER,
                TEAL,
                "nodetool status / ring",
                "Check which nodes are Up/Down and who owns which tokens",
            ),
            (
                ICON_CODE,
                BLUE,
                "TRACING ON",
                "Reveals per-replica latency and coordinator decisions for any query",
            ),
            (
                ICON_STRUCTURE,
                GREEN,
                "Read Repair",
                "Cassandra auto-heals stale replicas during QUORUM+ reads",
            ),
            (
                ICON_SHIELD,
                ORANGE,
                "Hinted Handoff",
                "Writes to a down node are cached as hints — replayed on recovery",
            ),
            (
                ICON_DANGER,
                RED,
                "Avoid ALLOW FILTERING",
                "Forces a full cluster scan — O(all data) — never in production",
            ),
            (
                ICON_DATABASE,
                PURPLE,
                "Run nodetool repair after ALTER KEYSPACE",
                "New replicas may be empty without an explicit repair pass",
            ),
        ]

        rows = VGroup()
        for icon_path, color, title, desc in tips:
            ic = make_icon(icon_path, color=color, height=0.27)
            t = make_label(title, font_size=12, color=color)
            d = make_label(desc, font_size=10, color=GREY_A)
            content = VGroup(ic, t, d).arrange(RIGHT, buff=0.15)
            box = RoundedRectangle(
                corner_radius=0.08,
                width=content.width + 0.5,
                height=content.height + 0.25,
                fill_color=DARK_BG,
                fill_opacity=0.9,
                stroke_color=color,
                stroke_width=1.0,
            )
            content.move_to(box.get_center())
            rows.add(VGroup(box, content))

        rows.arrange(DOWN, buff=0.1).next_to(header, DOWN, buff=0.35)
        for row in rows:
            self.play(FadeIn(row, shift=LEFT * 0.2), run_time=0.4)
            self.wait(0.45)

        self.wait(2)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 12: Closing ────────────────────────────────────────────
    def scene_closing(self):
        title = make_label("Lab 3: Consistency", font_size=34, color=TEAL)
        title.move_to(UP * 1.5)
        self.play(AddTextLetterByLetter(title, time_per_char=0.05))
        self.wait(0.8)

        icon_data = [
            (ICON_DATABASE, TEAL),
            (ICON_SERVER, BLUE),
            (ICON_SHIELD, GREEN),
            (ICON_LIGHTNING, ORANGE),
            (ICON_LOCK, PURPLE),
        ]
        icons_row = (
            VGroup(
                *[make_icon(path, color=color, height=0.5) for path, color in icon_data]
            )
            .arrange(RIGHT, buff=0.55)
            .move_to(ORIGIN)
        )
        self.play(
            AnimationGroup(
                *[FadeIn(ic, shift=UP * 0.2) for ic in icons_row], lag_ratio=0.1
            )
        )
        self.wait(1)

        themes = make_label(
            "Cassandra  ·  Replication  ·  Quorum  ·  CAP Theorem  ·  Docker",
            font_size=18,
            color=GREY_A,
        )
        themes.move_to(DOWN * 1.5)
        self.play(FadeIn(themes, shift=UP * 0.2))
        self.wait(4)
        self.play(FadeOut(*self.mobjects))
