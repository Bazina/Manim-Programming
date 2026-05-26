import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from manim import (
    config,
    Scene,
    VGroup,
    RoundedRectangle,
    Line,
    Circle,
    Dot,
    FadeIn,
    FadeOut,
    AddTextLetterByLetter,
    Circumscribe,
    AnimationGroup,
    ORIGIN,
    UP,
    DOWN,
    LEFT,
    RIGHT,
    PI,
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
    GOLD,
)
import math

try:
    from manim_slides import Slide as BaseSlide
except Exception:
    BaseSlide = Scene

from libs.ddia_components import (
    DARK_BG,
    ICON_STRUCTURE,
    ICON_LAYERS,
    ICON_CHART,
    ICON_CHECK,
    ICON_DANGER,
    ICON_SETTINGS,
    ICON_CPU_BOLT,
    ICON_TRANSFER,
    ICON_LIGHTNING,
    make_label,
    make_icon,
    make_comparison_table,
    create_rect_glow,
)
from libs.slide_style import SlideStyleMixin

config.background_color = "#0D1117"


class Sheet3Partitioning(SlideStyleMixin, BaseSlide):

    max_duration_before_split_reverse = 8.0

    def construct(self):
        self.scene_title()
        self.scene_intro_diagram()
        self.scene_q1_hash_mod_n()
        self.scene_q1_fixed_partitions()
        self.scene_q1_dynamic_size()
        self.scene_q1_dynamic_nodes()
        self.scene_q1_consistent_hash()
        self.scene_q2_intro()
        self.scene_q2_theory()
        self.scene_q2_n4()
        self.scene_q2_n5()
        self.scene_q2_n6()
        self.scene_q2_general_formula()
        self.scene_q2_consistent_v_nodes()
        self.scene_q3_extra_capacity()
        self.scene_closing()

    # ─── Helpers ──────────────────────────────────────────────────────
    def _node_box(self, label, partitions, color, width=2.1, height=1.6):
        """Render a node card containing partition pills."""
        title = make_label(label, font_size=12, color=color)
        pills = VGroup()
        for p in partitions:
            pb = RoundedRectangle(
                corner_radius=0.06, width=1.55, height=0.34,
                fill_color=DARK_BG, fill_opacity=0.95,
                stroke_color=color, stroke_width=1.0,
            )
            pl = make_label(p, font_size=10, color=color)
            pl.move_to(pb.get_center())
            pills.add(VGroup(pb, pl))
        pills.arrange(DOWN, buff=0.08)
        content = VGroup(title, pills).arrange(DOWN, buff=0.15)
        box = RoundedRectangle(
            corner_radius=0.1, width=width,
            height=max(height, content.height + 0.35),
            fill_color=DARK_BG, fill_opacity=0.9,
            stroke_color=color, stroke_width=1.4,
        )
        content.move_to(box.get_center())
        return VGroup(box, content)

    def _fraction_label(self, num, denom, color=WHITE, font_size=22):
        n = make_label(str(num), font_size=font_size, color=color)
        d = make_label(str(denom), font_size=font_size, color=color)
        bar_w = max(n.width, d.width) + 0.08
        bar = Line(LEFT * bar_w / 2, RIGHT * bar_w / 2,
                   stroke_color=color, stroke_width=2.0)
        n.next_to(bar, UP, buff=0.05)
        d.next_to(bar, DOWN, buff=0.05)
        return VGroup(n, bar, d)

    def _verdict_badge(self, text, color, width=7.0):
        box = RoundedRectangle(
            corner_radius=0.1, width=width, height=0.56,
            fill_color=DARK_BG, fill_opacity=0.95,
            stroke_color=color, stroke_width=1.8,
        )
        lbl = make_label(text, font_size=13, color=color)
        lbl.move_to(box.get_center())
        return VGroup(box, lbl)

    def _table_cell(self, text, color, w=1.4, h=0.5, font_size=11, bold=False):
        box = RoundedRectangle(
            corner_radius=0.05, width=w, height=h,
            fill_color=DARK_BG, fill_opacity=0.9,
            stroke_color=color, stroke_width=1.0,
        )
        lbl = make_label(text, font_size=font_size, color=color)
        lbl.move_to(box.get_center())
        return VGroup(box, lbl)

    def _hash_ring(self, center, radius, servers, virtuals_per_server, color_map):
        """Draw hash ring with dots for virtual nodes around it."""
        ring = Circle(radius=radius, stroke_color=GREY_B, stroke_width=1.2)
        ring.move_to(center)
        items = VGroup(ring)
        total = sum(virtuals_per_server.get(s, 1) for s in servers)
        idx = 0
        for s in servers:
            n = virtuals_per_server.get(s, 1)
            color = color_map.get(s, TEAL)
            for k in range(n):
                ang = 2 * PI * idx / total
                x = center[0] + radius * math.cos(ang)
                y = center[1] + radius * math.sin(ang)
                d = Dot(point=[x, y, 0], color=color, radius=0.07)
                items.add(d)
                if k == 0:
                    lx = center[0] + (radius + 0.32) * math.cos(ang)
                    ly = center[1] + (radius + 0.32) * math.sin(ang)
                    lbl = make_label(s, font_size=10, color=color)
                    lbl.move_to([lx, ly, 0])
                    items.add(lbl)
                idx += 1
        return items

    # ─── Scene 1: Title ───────────────────────────────────────────────
    def scene_title(self):
        icon = make_icon(ICON_STRUCTURE, color=TEAL, height=1.1)
        title = make_label("Sheet 3: Partitioning", font_size=36, color=TEAL)
        sub = make_label(
            "Rebalancing  ·  Hash mod N  ·  Consistent Hashing  ·  Virtual Nodes",
            font_size=17, color=GREY_B,
        )
        VGroup(icon, title, sub).arrange(DOWN, buff=0.38)
        self.play(FadeIn(icon, shift=DOWN * 0.3))
        self.wait(0.3)
        self.play(AddTextLetterByLetter(title, time_per_char=0.04))
        self.wait(0.3)
        self.play(FadeIn(sub, shift=UP * 0.2))
        self.wait(3)
        self._next_slide()
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 2: Intro diagram — 4 nodes, 8 partitions ──────────────
    def scene_intro_diagram(self):
        header = self._section_header("Cluster: 4 Nodes × 2 Partitions Each", color=TEAL)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.3)

        sub = make_label(
            "Reference layout used throughout Sheet 3",
            font_size=12, color=GREY_A,
        )
        sub.next_to(header, DOWN, buff=0.2)
        self.play(FadeIn(sub, shift=UP * 0.1))

        node_colors = [TEAL, BLUE, GREEN, ORANGE]
        node_data = [
            ("Node 1", ["Partition 1", "Partition 2"]),
            ("Node 2", ["Partition 3", "Partition 4"]),
            ("Node 3", ["Partition 5", "Partition 6"]),
            ("Node 4", ["Partition 7", "Partition 8"]),
        ]
        cards = VGroup()
        for (lbl, parts), c in zip(node_data, node_colors):
            cards.add(self._node_box(lbl, parts, c, width=2.4, height=1.9))
        cards.arrange(RIGHT, buff=0.45).move_to(DOWN * 0.4)

        # Cluster bus line above nodes
        bus = Line(
            cards.get_left() + LEFT * 0.3 + UP * 1.4,
            cards.get_right() + RIGHT * 0.3 + UP * 1.4,
            stroke_color=GREY_B, stroke_width=1.5, stroke_opacity=0.5,
        )
        bus_lbl = make_label("Cluster", font_size=10, color=GREY_B)
        bus_lbl.next_to(bus, UP, buff=0.08)

        self.play(FadeIn(bus), FadeIn(bus_lbl))
        self.play(
            AnimationGroup(
                *[FadeIn(c, shift=UP * 0.15) for c in cards], lag_ratio=0.18,
            )
        )

        # Vertical connectors from bus to each node
        conns = VGroup()
        for c in cards:
            top_pt = c.get_top()
            conns.add(Line(
                [top_pt[0], bus.get_y(), 0], top_pt,
                stroke_color=GREY_B, stroke_width=1.0, stroke_opacity=0.5,
            ))
        self.play(FadeIn(conns))

        note = make_label(
            "8 partitions distributed evenly — rebalancing moves partitions, not individual keys",
            font_size=11, color=YELLOW,
        )
        note.to_edge(DOWN, buff=0.45)
        self.play(FadeIn(note, shift=UP * 0.1))
        self.wait(3.5)
        self._next_slide()
        self.play(FadeOut(*self.mobjects))

    # ─── Q1 — Hash mod N ─────────────────────────────────────────────
    def scene_q1_hash_mod_n(self):
        header = self._section_header("Q1: Hash mod N", color=BLUE)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.2)

        icon = make_icon(ICON_LIGHTNING, color=BLUE, height=0.5)
        icon.next_to(header, DOWN, buff=0.2)
        self.play(FadeIn(icon))

        adv = self._icon_row_card(
            ICON_CHECK, GREEN,
            "Advantage",
            "Easy to implement and very fast — single modulo operation per key",
        )
        dis = self._icon_row_card(
            ICON_DANGER, RED,
            "Disadvantage",
            "Scaling up/down requires FULL rehash — almost all keys move",
        )
        rows = VGroup(adv, dis).arrange(DOWN, buff=0.3)
        rows.next_to(icon, DOWN, buff=0.4)

        self.play(FadeIn(adv, shift=RIGHT * 0.2))
        self.wait(0.3)
        self._next_slide(phase=True)
        self.play(FadeIn(dis, shift=RIGHT * 0.2))
        glow = create_rect_glow(dis, color=RED, max_opacity=0.28, spread=0.32)
        self.add(glow)
        self.bring_to_back(glow)
        glow.set_opacity(0)
        self._play_glow_row(dis, glow, RED)

        verdict = self._verdict_badge(
            "Trade-off: simplicity vs. expensive rebalancing", RED, width=7.4,
        )
        verdict.to_edge(DOWN, buff=0.45)
        self.play(FadeIn(verdict, shift=UP * 0.1))
        self.wait(3)
        self._next_slide()
        self.play(FadeOut(*self.mobjects))

    # ─── Q1 — Fixed number of partitions ─────────────────────────────
    def scene_q1_fixed_partitions(self):
        header = self._section_header("Q1: Fixed Number of Partitions", color=GREEN)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.2)

        icon = make_icon(ICON_LAYERS, color=GREEN, height=0.5)
        icon.next_to(header, DOWN, buff=0.2)
        self.play(FadeIn(icon))

        adv = self._icon_row_card(
            ICON_CHECK, GREEN,
            "Advantage",
            "Less data moved on scaling · better utilization of powerful nodes (more partitions)",
        )
        dis = self._icon_row_card(
            ICON_DANGER, RED,
            "Disadvantage",
            "With variable data size, count is hard: too low → costly recovery; too high → metadata overhead",
        )
        rows = VGroup(adv, dis).arrange(DOWN, buff=0.3)
        rows.next_to(icon, DOWN, buff=0.4)

        self.play(FadeIn(adv, shift=RIGHT * 0.2))
        self.wait(0.3)
        self._next_slide(phase=True)
        self.play(FadeIn(dis, shift=RIGHT * 0.2))
        glow = create_rect_glow(dis, color=RED, max_opacity=0.28, spread=0.32)
        self.add(glow)
        self.bring_to_back(glow)
        glow.set_opacity(0)
        self._play_glow_row(dis, glow, RED)

        verdict = self._verdict_badge(
            "Trade-off: choosing the partition count is a sticky decision", RED, width=8.0,
        )
        verdict.to_edge(DOWN, buff=0.45)
        self.play(FadeIn(verdict, shift=UP * 0.1))
        self.wait(3)
        self._next_slide()
        self.play(FadeOut(*self.mobjects))

    # ─── Q1 — Dynamic w.r.t. data size ───────────────────────────────
    def scene_q1_dynamic_size(self):
        header = self._section_header("Q1: Dynamic Partitions (by Data Size)", color=ORANGE)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.2)

        icon = make_icon(ICON_CHART, color=ORANGE, height=0.5)
        icon.next_to(header, DOWN, buff=0.2)
        self.play(FadeIn(icon))

        adv = self._icon_row_card(
            ICON_CHECK, GREEN,
            "Advantage",
            "Scalable and ideal for key-range partitioning — split / merge follows actual data growth",
        )
        dis = self._icon_row_card(
            ICON_DANGER, RED,
            "Disadvantage",
            "Empty DB starts with 1 partition — all writes land there until the first split (idle nodes)",
        )
        rows = VGroup(adv, dis).arrange(DOWN, buff=0.3)
        rows.next_to(icon, DOWN, buff=0.4)

        self.play(FadeIn(adv, shift=RIGHT * 0.2))
        self.wait(0.3)
        self._next_slide(phase=True)
        self.play(FadeIn(dis, shift=RIGHT * 0.2))
        glow = create_rect_glow(dis, color=RED, max_opacity=0.28, spread=0.32)
        self.add(glow)
        self.bring_to_back(glow)
        glow.set_opacity(0)
        self._play_glow_row(dis, glow, RED)

        verdict = self._verdict_badge(
            "Trade-off: cold-start bottleneck on a fresh cluster", RED, width=7.6,
        )
        verdict.to_edge(DOWN, buff=0.45)
        self.play(FadeIn(verdict, shift=UP * 0.1))
        self.wait(3)
        self._next_slide()
        self.play(FadeOut(*self.mobjects))

    # ─── Q1 — Dynamic w.r.t. nodes count ─────────────────────────────
    def scene_q1_dynamic_nodes(self):
        header = self._section_header("Q1: Dynamic Partitions (by Node Count)", color=PURPLE)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.2)

        icon = make_icon(ICON_SETTINGS, color=PURPLE, height=0.5)
        icon.next_to(header, DOWN, buff=0.2)
        self.play(FadeIn(icon))

        adv = self._icon_row_card(
            ICON_CHECK, GREEN,
            "Advantage",
            "Scalable with a stable partition size — fixed work per partition",
        )
        dis = self._icon_row_card(
            ICON_DANGER, RED,
            "Disadvantage",
            "Splits can be unfair · incompatible with key-range partitioning (boundaries hash-arbitrary)",
        )
        rows = VGroup(adv, dis).arrange(DOWN, buff=0.3)
        rows.next_to(icon, DOWN, buff=0.4)

        self.play(FadeIn(adv, shift=RIGHT * 0.2))
        self.wait(0.3)
        self._next_slide(phase=True)
        self.play(FadeIn(dis, shift=RIGHT * 0.2))
        glow = create_rect_glow(dis, color=RED, max_opacity=0.28, spread=0.32)
        self.add(glow)
        self.bring_to_back(glow)
        glow.set_opacity(0)
        self._play_glow_row(dis, glow, RED)

        verdict = self._verdict_badge(
            "Trade-off: loses key-range queries", RED, width=6.8,
        )
        verdict.to_edge(DOWN, buff=0.45)
        self.play(FadeIn(verdict, shift=UP * 0.1))
        self.wait(3)
        self._next_slide()
        self.play(FadeOut(*self.mobjects))

    # ─── Q1 — Consistent Hashing (no v-nodes) ────────────────────────
    def scene_q1_consistent_hash(self):
        header = self._section_header("Q1: Consistent Hashing (no V-Nodes)", color=TEAL)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.2)

        icon = make_icon(ICON_TRANSFER, color=TEAL, height=0.5)
        icon.next_to(header, DOWN, buff=0.2)
        self.play(FadeIn(icon))

        adv = self._icon_row_card(
            ICON_CHECK, GREEN,
            "Advantage",
            "Less data movement on scaling — only neighbour on the ring is affected",
        )
        dis = self._icon_row_card(
            ICON_DANGER, RED,
            "Disadvantage",
            "Cascaded failure under load · uneven load when keys are skewed (hot spots on one server)",
        )
        rows = VGroup(adv, dis).arrange(DOWN, buff=0.3)
        rows.next_to(icon, DOWN, buff=0.4)

        self.play(FadeIn(adv, shift=RIGHT * 0.2))
        self.wait(0.3)
        self._next_slide(phase=True)
        self.play(FadeIn(dis, shift=RIGHT * 0.2))
        glow = create_rect_glow(dis, color=RED, max_opacity=0.28, spread=0.32)
        self.add(glow)
        self.bring_to_back(glow)
        glow.set_opacity(0)
        self._play_glow_row(dis, glow, RED)

        verdict = self._verdict_badge(
            "Trade-off: cascaded failure + skew → motivates virtual nodes", RED, width=8.4,
        )
        verdict.to_edge(DOWN, buff=0.45)
        self.play(FadeIn(verdict, shift=UP * 0.1))
        self.wait(3)
        self._next_slide()
        self.play(FadeOut(*self.mobjects))

    # ─── Q2 Intro ────────────────────────────────────────────────────
    def scene_q2_intro(self):
        header = self._section_header(
            "Q2: Hash mod N — Reassignment Fraction on ±1 Node", color=BLUE,
        )
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.2)

        setup = make_label(
            "Uniform hash function · LCM of consecutive integers = their product",
            font_size=13, color=GREY_A,
        )
        setup.next_to(header, DOWN, buff=0.3)
        self.play(FadeIn(setup, shift=UP * 0.1))

        # Show the core idea: key k goes to k mod N → k mod (N±1)
        formula = self._code_box(
            [
                "before: node(k) = k mod N",
                "after : node(k) = k mod (N ± 1)",
                "reassigned ⇔ before ≠ after",
            ],
            "Rule",
            BLUE,
            width=7.0,
            font_size=12,
            language="python",
        )
        formula.next_to(setup, DOWN, buff=0.4)
        self.play(FadeIn(formula, shift=UP * 0.15))

        plan = VGroup(
            make_label("Step 1: enumerate keys 0 .. LCM(N, N±1) − 1", font_size=12, color=GREY_A),
            make_label("Step 2: count those whose target changes", font_size=12, color=GREY_A),
            make_label("Step 3: divide by LCM = N · (N±1)", font_size=12, color=GREY_A),
        ).arrange(DOWN, buff=0.12, aligned_edge=LEFT)
        plan.next_to(formula, DOWN, buff=0.35)
        self.play(FadeIn(plan, shift=UP * 0.1))

        self.wait(3.5)
        self._next_slide()
        self.play(FadeOut(*self.mobjects))

    # ─── Q2 — N = 4 ──────────────────────────────────────────────────
    # ─── Q2 — Theory: why the formula works (CRT + LCM walkthrough) ──
    def scene_q2_theory(self):
        header = self._section_header(
            "Q2: Theory — Why Hash mod N Reassigns So Much",
            color=YELLOW,
        )
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.2)

        # ── Phase 1: Stay condition + CRT (text only, fades out next) ──
        cond = VGroup(
            make_label("A key k stays put when:", font_size=14, color=GREY_A),
            make_label("k mod N  ==  k mod (N ± 1)  ==  r", font_size=18, color=YELLOW),
        ).arrange(DOWN, buff=0.18)
        cond.next_to(header, DOWN, buff=0.4)
        self.play(FadeIn(cond[0]))
        self.play(FadeIn(cond[1], shift=UP * 0.1))
        self.wait(0.5)
        self._next_slide(phase=True)

        crt = VGroup(
            make_label("gcd(N, N ± 1)  =  1   →   N and N±1 are coprime",
                       font_size=14, color=GREEN),
            make_label("CRT: residues repeat every LCM(N, N±1) = N · (N±1)",
                       font_size=14, color=GREEN),
            make_label("Stay-count per LCM cycle  =  min(N, N±1)",
                       font_size=14, color=GOLD),
        ).arrange(DOWN, buff=0.18, aligned_edge=LEFT)
        crt.next_to(cond, DOWN, buff=0.5)
        for ln in crt:
            self.play(FadeIn(ln, shift=UP * 0.08), run_time=0.4)
            self.wait(0.2)
        self.wait(1.0)
        self._next_slide(phase=True)

        # Clear theory text — walkthrough needs full real estate
        self.play(FadeOut(cond), FadeOut(crt))

        # ── Phase 2: Walkthrough table — centered, full canvas ─────────
        walk_title = make_label(
            "Walkthrough — N = 4 → 5  (LCM = 20)",
            font_size=16, color=BLUE,
        )
        walk_title.next_to(header, DOWN, buff=0.4)

        sample = [(k, k % 4, k % 5) for k in [0, 1, 2, 3, 4, 5]] + [("…", "…", "…"), (19, 3, 4)]
        rows_data = []
        for k_, m4, m5 in sample:
            match = (m4 == m5) if isinstance(m4, int) else None
            c = GREEN if match else (RED if match is False else GREY_B)
            mark = "✓" if match else ("✗" if match is False else "…")
            rows_data.append(
                (str(k_), GREY_A, str(m4), BLUE, str(m5), ORANGE, mark, c)
            )

        table = make_comparison_table(
            col_headers     = ["k", "k mod 4", "k mod 5", "match?"],
            col_colors      = [GREY_A, BLUE, ORANGE, GREEN],
            col_x_positions = [-2.7, -0.9, 0.9, 2.7],
            rows_data       = rows_data,
            header_font_size = 13,
            row_font_size    = 12,
            note_font_size   = 13,
            row_spacing      = 0.34,
        )
        hdr_grp, div, body = table[0], table[1], table[2]
        # Center the entire table block under walk_title
        table.next_to(walk_title, DOWN, buff=0.25)
        table.set_x(0)

        self.play(FadeIn(walk_title, shift=UP * 0.1))
        self.play(FadeIn(hdr_grp, shift=UP * 0.08), FadeIn(div))
        for r in body:
            self.play(FadeIn(r, shift=RIGHT * 0.1), run_time=0.2)

        # GLOW the four matching rows (0..3)
        match_rows = VGroup(*body[:4])
        glow = create_rect_glow(match_rows, color=GREEN, max_opacity=0.32, spread=0.36)
        self.add(glow)
        self.bring_to_back(glow)
        glow.set_opacity(0)
        self._play_glow_row(match_rows, glow, GREEN)
        self.wait(0.4)
        self._next_slide(phase=True)

        # ── Phase 3: Verdict ───────────────────────────────────────────
        verdict = VGroup(
            make_label("4 stays / 20 in cycle  =  1/5 stay  →  4/5 reassigned",
                       font_size=15, color=GOLD),
            make_label("Generalize:  reassigned = (max − 1) / max   where max = max(N, N±1)",
                       font_size=13, color=GREY_A),
        ).arrange(DOWN, buff=0.14)
        verdict.to_edge(DOWN, buff=0.35)
        self.play(FadeIn(verdict, shift=UP * 0.1))
        self.wait(4)
        self._next_slide()
        self.play(FadeOut(*self.mobjects))

    def scene_q2_n4(self):
        self._q2_n_scene(
            n=4,
            add_num=16, add_den=20, add_simpl="4/5",
            rem_num=9,  rem_den=12, rem_simpl="3/4",
            color=GREEN,
        )

    # ─── Q2 — N = 5 ──────────────────────────────────────────────────
    def scene_q2_n5(self):
        self._q2_n_scene(
            n=5,
            add_num=25, add_den=30, add_simpl="5/6",
            rem_num=16, rem_den=20, rem_simpl="4/5",
            color=ORANGE,
        )

    # ─── Q2 — N = 6 ──────────────────────────────────────────────────
    def scene_q2_n6(self):
        self._q2_n_scene(
            n=6,
            add_num=36, add_den=42, add_simpl="6/7",
            rem_num=25, rem_den=30, rem_simpl="5/6",
            color=PURPLE,
        )

    def _q2_n_scene(self, n, add_num, add_den, add_simpl,
                    rem_num, rem_den, rem_simpl, color):
        header = self._section_header(f"Q2: N = {n} — Reassignment Fractions", color=color)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.2)

        # ── Phase 1: Centered key-table via make_comparison_table ─────
        lcm_add = n * (n + 1)
        sample_keys = list(range(0, min(lcm_add, 6)))
        rows_data = []
        for k in sample_keys:
            b = k % n
            a = k % (n + 1)
            chg = b != a
            mark = "✓ moved" if chg else "−  stay"
            mark_color = RED if chg else GREEN
            rows_data.append((str(k), WHITE, str(b), BLUE, str(a), GREEN, mark, mark_color))

        table = make_comparison_table(
            col_headers     = ["key k", f"k mod {n}", f"k mod {n + 1}", "moved?"],
            col_colors      = [GREY_A, BLUE, GREEN, color],
            col_x_positions = [-2.7, -0.9, 0.9, 2.9],
            rows_data       = rows_data,
            header_font_size = 13,
            row_font_size    = 12,
            note_font_size   = 12,
            row_spacing      = 0.34,
        )
        table.next_to(header, DOWN, buff=0.35)
        table.set_x(0)
        hdr_grp, div, body = table[0], table[1], table[2]
        self.play(FadeIn(hdr_grp), FadeIn(div))
        for r in body:
            self.play(FadeIn(r, shift=RIGHT * 0.1), run_time=0.2)
        self.wait(0.4)
        self._next_slide(phase=True)

        # ── Phase 2: Fractions side-by-side BELOW table ───────────────
        add_box = self._code_box(
            [
                f"Add ({n} → {n + 1}):",
                f"  LCM = {n} · {n + 1} = {lcm_add}",
                f"  reassigned = {add_num} / {add_den}",
                f"             = {add_simpl}",
            ],
            "Adding a server",
            GREEN, width=5.2, font_size=11, language="python",
        )
        rem_box = self._code_box(
            [
                f"Remove ({n} → {n - 1}):",
                f"  LCM = {n} · {n - 1} = {n * (n - 1)}",
                f"  reassigned = {rem_num} / {rem_den}",
                f"             = {rem_simpl}",
            ],
            "Removing a server",
            RED, width=5.2, font_size=11, language="python",
        )
        boxes = VGroup(add_box, rem_box).arrange(RIGHT, buff=0.5)
        boxes.next_to(table, DOWN, buff=0.35)
        boxes.set_x(0)

        self.play(FadeIn(add_box, shift=UP * 0.15))
        self.wait(0.3)
        self._next_slide(phase=True)
        self.play(FadeIn(rem_box, shift=UP * 0.15))
        self.wait(0.3)

        # GLOW the resulting fractions
        glow_a = create_rect_glow(add_box, color=GREEN, max_opacity=0.3, spread=0.35)
        glow_r = create_rect_glow(rem_box, color=RED, max_opacity=0.3, spread=0.35)
        self.add(glow_a, glow_r)
        self.bring_to_back(glow_a, glow_r)
        glow_a.set_opacity(0)
        glow_r.set_opacity(0)
        self._play_glow_row(add_box, glow_a, GREEN)
        self._play_glow_row(rem_box, glow_r, RED)

        verdict = self._verdict_badge(
            f"N={n}: add → {add_simpl} moved · remove → {rem_simpl} moved", color, width=8.6,
        )
        verdict.to_edge(DOWN, buff=0.3)
        self.play(FadeIn(verdict, shift=UP * 0.1))
        self.wait(3.5)
        self._next_slide()
        self.play(FadeOut(*self.mobjects))

    # ─── Q2 — General formula ────────────────────────────────────────
    def scene_q2_general_formula(self):
        header = self._section_header("Q2(d): General Formula", color=GOLD)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.2)

        intro = make_label(
            "Derivation: count keys whose hash-bucket stays vs. moves under k mod N",
            font_size=13, color=GREY_A,
        )
        intro.next_to(header, DOWN, buff=0.25)
        self.play(FadeIn(intro, shift=UP * 0.1))

        # ── Step-by-step derivation (addition path) ────────────────────
        steps_add = VGroup(
            make_label("1.  Old hash: k mod N    ·    New hash: k mod (N+1)",
                       font_size=12, color=GREY_A),
            make_label("2.  Residue patterns repeat every LCM(N, N+1) = N · (N+1) keys",
                       font_size=12, color=GREY_A),
            make_label("3.  Key k stays iff  k mod N  ==  k mod (N+1)",
                       font_size=12, color=GREY_A),
            make_label("4.  That happens for exactly N keys per LCM cycle (k = 0 .. N−1)",
                       font_size=12, color=GREY_A),
            make_label("5.  Moved = N(N+1) − N = N²    →    Fraction = N² / N(N+1)",
                       font_size=12, color=GREEN),
        ).arrange(DOWN, buff=0.12, aligned_edge=LEFT)
        steps_add.next_to(intro, DOWN, buff=0.3)
        for s in steps_add:
            self.play(FadeIn(s, shift=UP * 0.05), run_time=0.35)
            self.wait(0.15)
        self._next_slide(phase=True)

        add_box = self._code_box(
            [
                "N → N + 1 (add a server)",
                "",
                "    fraction reassigned",
                "       =  N / (N + 1)",
            ],
            "Addition",
            GREEN, width=5.8, font_size=14, language="python",
        )
        rem_box = self._code_box(
            [
                "N → N − 1 (remove a server)",
                "",
                "    fraction reassigned",
                "       =  (N − 1) / N",
            ],
            "Removal",
            RED, width=5.8, font_size=14, language="python",
        )
        boxes = VGroup(add_box, rem_box).arrange(RIGHT, buff=0.5)
        boxes.next_to(steps_add, DOWN, buff=0.3)
        self.play(FadeOut(steps_add))
        self.play(FadeIn(add_box, shift=UP * 0.15))
        self.play(FadeIn(rem_box, shift=UP * 0.15))

        # GLOW both with gold
        glow_a = create_rect_glow(add_box, color=GOLD, max_opacity=0.28, spread=0.35)
        glow_r = create_rect_glow(rem_box, color=GOLD, max_opacity=0.28, spread=0.35)
        self.add(glow_a, glow_r)
        self.bring_to_back(glow_a, glow_r)
        glow_a.set_opacity(0)
        glow_r.set_opacity(0)
        self._play_glow_row(add_box, glow_a, GOLD)
        self._play_glow_row(rem_box, glow_r, GOLD)

        # Verification row referencing earlier numbers
        check = VGroup(
            make_label("N=4 → 5:  16/20 = 4/5 reassigned  ✓",   font_size=11, color=GOLD),
            make_label("N=5 → 6:  25/30 = 5/6 reassigned  ✓",   font_size=11, color=GOLD),
            make_label("N=6 → 7:  36/42 = 6/7 reassigned  ✓",   font_size=11, color=GOLD),
            make_label("Symmetric:  N → N−1  uses  (N−1)/N",    font_size=11, color=GREY_A),
        ).arrange(DOWN, buff=0.1, aligned_edge=LEFT)
        check.to_edge(DOWN, buff=0.45)
        self.play(FadeIn(check, shift=UP * 0.1))

        self.wait(4)
        self._next_slide()
        self.play(FadeOut(*self.mobjects))

    # ─── Q2(e) — Consistent Hashing with V-Nodes ─────────────────────
    def scene_q2_consistent_v_nodes(self):
        header = self._section_header(
            "Q2(e): Consistent Hashing with V-Nodes", color=TEAL,
        )
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.2)

        setup = make_label(
            "Assume V = 10 virtual nodes per server · K = 500 total keys · share/node = K / (N · V)",
            font_size=12, color=GREY_A,
        )
        setup.next_to(header, DOWN, buff=0.2)
        self.play(FadeIn(setup, shift=UP * 0.1))

        # Use shared make_comparison_table for unified style
        rows_data = [
            ("3 → 4", WHITE, "3/4", BLUE, "1/4", TEAL),
            ("3 → 2", WHITE, "2/3", BLUE, "1/3", TEAL),
            ("4 → 5", WHITE, "4/5", BLUE, "1/5", TEAL),
            ("4 → 3", WHITE, "3/4", BLUE, "1/4", TEAL),
            ("5 → 6", WHITE, "5/6", BLUE, "1/6", TEAL),
            ("5 → 4", WHITE, "4/5", BLUE, "1/5", TEAL),
        ]
        table = make_comparison_table(
            col_headers     = ["Change", "Hash mod N", "Consistent + V-Nodes"],
            col_colors      = [GREY_A, BLUE, TEAL],
            col_x_positions = [-3.2, -0.3, 3.0],
            rows_data       = rows_data,
        )
        table.next_to(setup, DOWN, buff=0.35)
        hdr_grp, div, body_rows = table[0], table[1], table[2]

        self.play(FadeIn(hdr_grp), FadeIn(div))
        for r in body_rows:
            self.play(FadeIn(r, shift=RIGHT * 0.1), run_time=0.25)

        # GLOW the v-nodes column
        vn_col = VGroup(hdr_grp[2], *[r[2] for r in body_rows])
        glow = create_rect_glow(vn_col, color=TEAL, max_opacity=0.28, spread=0.3)
        self.add(glow)
        self.bring_to_back(glow)
        glow.set_opacity(0)
        self._play_glow_row(vn_col, glow, TEAL)

        formulas = VGroup(
            make_label("Add: 1 / (N + 1) of keys reassigned", font_size=12, color=GREEN),
            make_label("Remove: 1 / (N − 1) of keys reassigned", font_size=12, color=RED),
        ).arrange(DOWN, buff=0.12, aligned_edge=LEFT)
        formulas.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(formulas, shift=UP * 0.1))
        self.wait(4)
        self._next_slide()
        self.play(FadeOut(*self.mobjects))

    # ─── Q3 — Extra Capacity ─────────────────────────────────────────
    def scene_q3_extra_capacity(self):
        header = self._section_header(
            "Q3: Server with 2× Capacity — Doubled V-Nodes", color=GOLD,
        )
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.2)

        question = make_label(
            "How can one server receive 2× the objects of others?",
            font_size=13, color=GREY_A,
        )
        question.next_to(header, DOWN, buff=0.2)
        self.play(FadeIn(question, shift=UP * 0.1))

        # Left: two server cards, one labeled 2x
        normal = self._node_box("Node A", ["capacity 1×"], TEAL, width=2.2, height=1.2)
        big = self._node_box("Node B  (2×)", ["capacity 2×"], GOLD, width=2.4, height=1.2)
        servers = VGroup(normal, big).arrange(DOWN, buff=0.4)
        servers.to_edge(LEFT, buff=0.9).shift(DOWN * 0.2)
        self.play(FadeIn(normal, shift=RIGHT * 0.15))
        self.play(FadeIn(big, shift=RIGHT * 0.15))

        # Right: hash ring — Node A 3 v-nodes, Node B 6 v-nodes
        ring_center = [2.8, -0.4, 0]
        ring = self._hash_ring(
            center=ring_center,
            radius=1.7,
            servers=["A", "B"],
            virtuals_per_server={"A": 3, "B": 6},
            color_map={"A": TEAL, "B": GOLD},
        )
        self.play(FadeIn(ring, shift=UP * 0.1))

        # Highlight doubled v-nodes
        glow = create_rect_glow(ring, color=GOLD, max_opacity=0.25, spread=0.35)
        self.add(glow)
        self.bring_to_back(glow)
        glow.set_opacity(0)
        self._play_glow_row(ring, glow, GOLD)

        recipe = VGroup(
            make_label(
                "Recipe: assign 2× as many virtual nodes to Node B",
                font_size=13, color=GOLD,
            ),
            make_label(
                "→ Node B owns ~2× of the ring → naturally receives 2× the objects",
                font_size=12, color=GREY_A,
            ),
        ).arrange(DOWN, buff=0.12)
        recipe.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(recipe, shift=UP * 0.1))

        badge = self._verdict_badge(
            "Capacity-weighted v-nodes — no protocol change required  ✓",
            GOLD, width=8.4,
        )
        badge.next_to(recipe, UP, buff=0.2)
        self.play(FadeIn(badge, shift=UP * 0.1))
        self.play(Circumscribe(badge, color=GOLD, buff=0.05, run_time=1.4))

        self.wait(4)
        self._next_slide()
        self.play(FadeOut(*self.mobjects))

    # ─── Closing ─────────────────────────────────────────────────────
    def scene_closing(self):
        title = make_label("Sheet 3: Partitioning", font_size=34, color=TEAL)
        title.move_to(UP * 1.8)
        self.play(AddTextLetterByLetter(title, time_per_char=0.05))
        self.wait(0.6)

        icon_data = [
            (ICON_STRUCTURE, TEAL),
            (ICON_LAYERS, GREEN),
            (ICON_CHART, ORANGE),
            (ICON_TRANSFER, PURPLE),
            (ICON_CPU_BOLT, GOLD),
        ]
        icons_row = (
            VGroup(*[make_icon(p, color=c, height=0.5) for p, c in icon_data])
            .arrange(RIGHT, buff=0.55)
            .move_to(ORIGIN)
        )
        self.play(
            AnimationGroup(
                *[FadeIn(ic, shift=UP * 0.2) for ic in icons_row], lag_ratio=0.12,
            )
        )
        self.wait(0.8)

        themes = make_label(
            "Hash mod N  ·  Fixed Partitions  ·  Dynamic  ·  Consistent Hashing  ·  V-Nodes",
            font_size=16, color=GREY_A,
        )
        themes.move_to(DOWN * 1.5)
        self.play(FadeIn(themes, shift=UP * 0.2))
        self.wait(4)
        self._next_slide()
        self.play(FadeOut(*self.mobjects))
