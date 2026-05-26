import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from manim import (
    config,
    Scene,
    VGroup,
    RoundedRectangle,
    Arrow,
    Line,
    FadeIn,
    FadeOut,
    GrowArrow,
    AddTextLetterByLetter,
    AnimationGroup,
    ORIGIN,
    UP,
    DOWN,
    LEFT,
    RIGHT,
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

from libs.slide_controls import slide_checkpoint  # noqa: F401
from libs.slide_style import SlideStyleMixin
from libs.ddia_components import (
    DARK_BG,
    ICON_DATABASE,
    ICON_SERVER,
    ICON_LIGHTNING,
    ICON_STOPWATCH,
    ICON_CHART,
    ICON_LAYERS,
    ICON_TRANSFER,
    ICON_CPU_BOLT,
    ICON_USER,
    ICON_FILE,
    ICON_SETTINGS,
    ICON_MONITOR,
    create_rect_glow,
    make_label,
    make_icon,
)

config.background_color = "#0D1117"


class Sheet1Hardware(SlideStyleMixin, BaseSlide):

    # Avoid reverse-video generation to prevent PyAV malloc failures on long renders.
    max_duration_before_split_reverse = 8.0

    def construct(self):
        self.scene_title()
        self.scene_latency_numbers()
        self.scene_q1_intro()
        self.scene_q1_service_time()
        self.scene_q1_disks_per_day()
        self.scene_q1_p90()
        self.scene_q1_scale_10x()
        self.scene_q1_optimized_disks()
        self.scene_q2_intro()
        self.scene_q2_causes()
        self.scene_q2_architectural()
        self.scene_q2_partition_customers()
        self.scene_q3_intro()
        self.scene_q3_storage_size()
        self.scene_q3_storage_types()
        self.scene_q3_service_time()
        self.scene_q3_scale_machines()
        self.scene_closing()

    # ─── Local helper: formatted math line (replaces code blocks) ─────
    def _calc_line(self, parts, font_size=16, buff=0.12):
        """parts: list of (text, color) tuples → returns VGroup arranged RIGHT."""
        row = VGroup(*[make_label(t, font_size=font_size, color=c) for t, c in parts])
        row.arrange(RIGHT, buff=buff)
        return row

    def _calc_block(self, lines, font_size=16, buff=0.18):
        """lines: list of parts-lists → returns VGroup stacked DOWN, left-aligned."""
        rows = VGroup(*[self._calc_line(parts, font_size=font_size) for parts in lines])
        rows.arrange(DOWN, buff=buff, aligned_edge=LEFT)
        return rows

    # ─── Local style helper: animated reveal of icon-row cards w/ glow ──
    def _reveal_rows(self, rows, glow_indices=None, glow_color=YELLOW):
        """Fade in a stack of icon_row_cards, with phase stops + optional glow."""
        glow_indices = set(glow_indices or [])
        glow_map = {}
        for i in glow_indices:
            g = create_rect_glow(rows[i], color=glow_color, max_opacity=0.28, spread=0.3)
            self.add(g)
            self.bring_to_back(g)
            g.set_opacity(0)
            glow_map[i] = g
        for i, row in enumerate(rows):
            self.play(FadeIn(row, shift=RIGHT * 0.1), run_time=0.32)
            if i in glow_map:
                self._play_glow_row(row, glow_map[i], glow_color)
            if i < len(rows) - 1:
                self._next_slide(phase=True)

    # ─── Scene 1: Title ───────────────────────────────────────────────
    def scene_title(self):
        icon = make_icon(ICON_CPU_BOLT, color=TEAL, height=1.1)
        title = make_label("Sheet 1: Hardware & System Sizing", font_size=34, color=TEAL)
        sub = make_label(
            "Storage Notes  ·  Twitter Tweets  ·  Cell Tower Heartbeats",
            font_size=17, color=GREY_B,
        )
        VGroup(icon, title, sub).arrange(DOWN, buff=0.38)
        self.play(FadeIn(icon, shift=DOWN * 0.3))
        self.wait(0.4)
        self.play(AddTextLetterByLetter(title, time_per_char=0.04))
        self.wait(0.4)
        self.play(FadeIn(sub, shift=UP * 0.2))
        self.wait(3)
        self._next_slide()
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 1b: Reference Latency Numbers ─────────────────────────
    def scene_latency_numbers(self):
        header = self._section_header(
            "Latency Numbers Every Engineer Should Know",
            color=YELLOW,
        )
        self.play(AddTextLetterByLetter(header, time_per_char=0.03))
        self.wait(0.3)

        attribution = make_label(
            "Source — colin-scott.github.io/personal_website/research/interactive_latency.html",
            font_size=11, color=GREY_B,
        )
        attribution.next_to(header, DOWN, buff=0.18)
        self.play(FadeIn(attribution, shift=UP * 0.1))
        self.wait(0.3)

        # 2-column compact table — fits everything on screen
        entries = [
            (ICON_CPU_BOLT,   TEAL,   "L1 cache reference",            "~ 1 ns"),
            (ICON_CPU_BOLT,   BLUE,   "L2 cache reference",            "~ 4 ns"),
            (ICON_LIGHTNING,  GREEN,  "Main memory",                   "~ 100 ns"),
            (ICON_DATABASE,   ORANGE, "SSD random read (4 KB)",        "~ 16 us"),
            (ICON_TRANSFER,   PURPLE, "RTT — same datacenter",         "~ 500 us"),
            (ICON_DATABASE,   RED,    "Read 1 MB seq (SSD)",           "~ 1 ms"),
            (ICON_DATABASE,   RED,    "HDD disk seek",                 "~ 3 ms"),
            (ICON_TRANSFER,   GREY_B, "RTT — CA → Netherlands",        "~ 150 ms"),
        ]

        def _entry(icon_path, color, title, val):
            ic = make_icon(icon_path, color=color, height=0.26)
            t = make_label(title, font_size=11, color=color)
            v = make_label(val, font_size=12, color=color)
            text_col = VGroup(t, v).arrange(DOWN, buff=0.03, aligned_edge=LEFT)
            content = VGroup(ic, text_col).arrange(RIGHT, buff=0.18)
            box = RoundedRectangle(
                corner_radius=0.08, width=5.6, height=content.height + 0.2,
                fill_color=DARK_BG, fill_opacity=0.9,
                stroke_color=color, stroke_width=1.0,
            )
            content.move_to(box.get_center())
            return VGroup(box, content)

        cards = [_entry(*e) for e in entries]
        left_col = VGroup(*cards[0::2]).arrange(DOWN, buff=0.12, aligned_edge=LEFT)
        right_col = VGroup(*cards[1::2]).arrange(DOWN, buff=0.12, aligned_edge=LEFT)
        grid = VGroup(left_col, right_col).arrange(RIGHT, buff=0.3, aligned_edge=UP)
        grid.next_to(attribution, DOWN, buff=0.25)

        # Glow the two numbers actually used downstream: 16 us + 1 ms
        glow_targets = [cards[3], cards[5]]
        glow_colors = [ORANGE, RED]
        glows = []
        for card, color in zip(glow_targets, glow_colors):
            g = create_rect_glow(card, color=color, max_opacity=0.3, spread=0.3)
            self.add(g)
            self.bring_to_back(g)
            g.set_opacity(0)
            glows.append((card, g, color))

        # Reveal column-pair by column-pair
        for i in range(len(cards) // 2):
            self.play(
                FadeIn(left_col[i], shift=RIGHT * 0.1),
                FadeIn(right_col[i], shift=LEFT * 0.1),
                run_time=0.32,
            )
            if i < len(cards) // 2 - 1:
                self._next_slide(phase=True)

        self._next_slide(phase=True)
        for card, g, color in glows:
            self._play_glow_row(card, g, color)

        note = make_label(
            "SSD 4 KB ≈ 16 us drives Q3 hot-path · 1 MB seq ≈ 1 ms drives Q1 write math",
            font_size=11, color=GREEN,
        )
        note.to_edge(DOWN, buff=0.3)
        self.play(FadeIn(note, shift=UP * 0.1))
        self.wait(2.5)
        self._next_slide()
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 2: Q1 Intro ────────────────────────────────────────────
    def scene_q1_intro(self):
        header = self._section_header("Q1: Storage System for User Notes", color=TEAL)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.4)

        spec_rows = VGroup(
            self._icon_row_card(
                ICON_USER, TEAL,
                "Request rate",
                "1,000 requests / second",
            ),
            self._icon_row_card(
                ICON_FILE, BLUE,
                "Payload size",
                "~300 KB per note",
            ),
            self._icon_row_card(
                ICON_DATABASE, ORANGE,
                "Disk capacity",
                "128 MB each",
            ),
            self._icon_row_card(
                ICON_LIGHTNING, GREEN,
                "Disk write speed",
                "300 MB / second",
            ),
            self._icon_row_card(
                ICON_SERVER, PURPLE,
                "Compute",
                "1 machine · 1 core",
            ),
        ).arrange(DOWN, buff=0.14).next_to(header, DOWN, buff=0.35)

        self._reveal_rows(spec_rows, glow_indices={1, 3}, glow_color=BLUE)

        note = make_label(
            "State assumptions clearly — interview gold",
            font_size=12, color=YELLOW,
        )
        note.to_edge(DOWN, buff=0.4)
        self.play(FadeIn(note, shift=UP * 0.1))
        self.wait(3)
        self._next_slide()
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 3: Q1a — Service Time ──────────────────────────────────
    def scene_q1_service_time(self):
        header = self._section_header("Q1a: Request Service Time", color=BLUE)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.4)

        assume = self._icon_row_card(
            ICON_SETTINGS, GREY_A,
            "Assumption",
            "Service time = write-to-disk only (ignore CPU, network, queues)",
        )
        assume.next_to(header, DOWN, buff=0.3)
        self.play(FadeIn(assume, shift=UP * 0.1))
        self.wait(0.4)
        self._next_slide(phase=True)

        l1 = self._calc_line([
            ("data_size ", GREY_A), ("= ", GREY_A), ("300 KB", YELLOW),
        ], font_size=18)
        l2 = self._calc_line([
            ("write_speed ", GREY_A), ("= ", GREY_A), ("300 MB/s", YELLOW), ("  (SSD)", GREY_B),
        ], font_size=18)
        l3 = self._calc_line([
            ("service_time ", GREY_A), ("= ", GREY_A),
            ("data_size", YELLOW), (" / ", GREY_A), ("write_speed", YELLOW),
        ], font_size=18)
        l4 = self._calc_line([
            ("             = ", GREY_A),
            ("300 KB", YELLOW), (" / ", GREY_A), ("300,000 KB/s", YELLOW),
            ("  =  ", GREY_A), ("0.001 s", GREEN),
            ("  =  ", GREY_A), ("1 ms", GREEN),
        ], font_size=18)
        calc = VGroup(l1, l2, l3, l4).arrange(DOWN, buff=0.18, aligned_edge=LEFT)
        calc.next_to(assume, DOWN, buff=0.4)
        self.play(FadeIn(l1, shift=UP * 0.1)); self.wait(0.2)
        self.play(FadeIn(l2, shift=UP * 0.1)); self.wait(0.2)
        self._next_slide(phase=True)
        self.play(FadeIn(l3, shift=UP * 0.1)); self.wait(0.2)
        self.play(FadeIn(l4, shift=UP * 0.1))
        self.wait(0.5)
        self._next_slide(phase=True)

        answer_box = RoundedRectangle(
            corner_radius=0.12, width=4.5, height=0.9,
            fill_color=DARK_BG, fill_opacity=0.95,
            stroke_color=GREEN, stroke_width=2.0,
        )
        answer_lbl = make_label("Service time = 1 ms", font_size=22, color=GREEN)
        answer_lbl.move_to(answer_box.get_center())
        answer = VGroup(answer_box, answer_lbl).to_edge(DOWN, buff=0.45)
        glow = create_rect_glow(answer, color=GREEN, max_opacity=0.32, spread=0.4)
        self.add(glow)
        self.bring_to_back(glow)
        glow.set_opacity(0)
        self.play(FadeIn(answer, shift=UP * 0.15))
        self._play_glow_row(answer, glow, GREEN)
        self.wait(3)
        self._next_slide()
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 4: Q1b — Disks per Day ─────────────────────────────────
    def scene_q1_disks_per_day(self):
        header = self._section_header("Q1b: Disks for 1 Full Day (No Splitting)", color=ORANGE)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.4)

        assume = self._icon_row_card(
            ICON_SETTINGS, GREY_A,
            "Assumption",
            "A single 300 KB note must fit fully on one disk (no fragmentation)",
        )
        assume.next_to(header, DOWN, buff=0.25)
        self.play(FadeIn(assume, shift=UP * 0.1))
        self.wait(0.3)
        self._next_slide(phase=True)

        l1 = self._calc_line([
            ("Requests/day ", GREY_A),
            ("1000 r/s", YELLOW), (" × ", GREY_A), ("86,400 s", YELLOW),
            (" = ", GREY_A), ("86,400,000", YELLOW),
        ], font_size=18)
        l2 = self._calc_line([
            ("Notes/disk ", GREY_A),
            ("⌊", YELLOW), ("128 MB", YELLOW), (" / ", GREY_A), ("300 KB", YELLOW), ("⌋", YELLOW),
            (" = ", GREY_A), ("426", YELLOW),
        ], font_size=18)
        l3 = self._calc_line([
            ("Disks ", GREY_A),
            ("⌈", ORANGE), ("86.4M", ORANGE), (" / ", GREY_A), ("426", ORANGE), ("⌉", ORANGE),
            (" = ", GREY_A),
            ("202,817 disks", ORANGE),
        ], font_size=18)
        calc = VGroup(l1, l2, l3).arrange(DOWN, buff=0.2, aligned_edge=LEFT)
        calc.next_to(assume, DOWN, buff=0.35)
        self.play(FadeIn(l1, shift=UP * 0.1)); self.wait(0.3)
        self._next_slide(phase=True)
        self.play(FadeIn(l2, shift=UP * 0.1)); self.wait(0.3)
        self._next_slide(phase=True)
        self.play(FadeIn(l3, shift=UP * 0.1))
        self.wait(0.4)
        self._next_slide(phase=True)

        # Answer banner
        ans_box = RoundedRectangle(
            corner_radius=0.12, width=5.5, height=0.85,
            fill_color=DARK_BG, fill_opacity=0.95,
            stroke_color=ORANGE, stroke_width=2.0,
        )
        ans_lbl = make_label("202,817 disks / day", font_size=22, color=ORANGE)
        ans_lbl.move_to(ans_box.get_center())
        ans = VGroup(ans_box, ans_lbl)
        ans.next_to(calc, DOWN, buff=0.25)
        glow = create_rect_glow(ans, color=ORANGE, max_opacity=0.32, spread=0.35)
        self.add(glow)
        self.bring_to_back(glow)
        glow.set_opacity(0)
        self.play(FadeIn(ans, shift=UP * 0.1))
        self._play_glow_row(ans, glow, ORANGE)
        self.wait(0.4)
        self._next_slide(phase=True)

        # Cost callout — image-style formatted math
        cost_title = make_label("Cost Reality Check (~25 TB / day on GCP)", font_size=16, color=RED)
        cost_lines = VGroup(
            self._calc_line([("1 month retention  →  ", GREY_A), ("$4,250 / month", YELLOW)], font_size=16),
            self._calc_line([("15 days            →  ", GREY_A), ("$64,000", YELLOW)], font_size=16),
            self._calc_line([("1 year             →  ", GREY_A), ("$1,530,000", RED), (" !!!", RED)], font_size=16),
        ).arrange(DOWN, buff=0.15, aligned_edge=LEFT)
        cost = VGroup(cost_title, cost_lines).arrange(DOWN, buff=0.22, aligned_edge=LEFT)
        cost.to_edge(DOWN, buff=0.4)
        cost_glow = create_rect_glow(cost, color=RED, max_opacity=0.28, spread=0.35)
        self.add(cost_glow)
        self.bring_to_back(cost_glow)
        cost_glow.set_opacity(0)
        self.play(FadeOut(assume, calc))
        self.play(FadeIn(cost, shift=UP * 0.15))
        self._play_glow_row(cost, cost_glow, RED)
        self.wait(3.5)
        self._next_slide()
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 5: Q1c — P90 ───────────────────────────────────────────
    def scene_q1_p90(self):
        header = self._section_header("Q1c: 90th Percentile Service Time", color=GREEN)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.4)

        rows = VGroup(
            self._icon_row_card(
                ICON_LAYERS, BLUE,
                "Disks pre-allocated",
                "No cost of requesting resources at runtime",
            ),
            self._icon_row_card(
                ICON_LIGHTNING, ORANGE,
                "Fragmentation allowed",
                "Writes proceed without delay",
            ),
            self._icon_row_card(
                ICON_SETTINGS, GREY_A,
                "Software queues ignored",
                "Negligible processing & data-structure updates",
            ),
            self._icon_row_card(
                ICON_STOPWATCH, GREEN,
                "p90 = 1 ms (stable)",
                "No queueing => tail latency tracks the mean",
            ),
        ).arrange(DOWN, buff=0.14).next_to(header, DOWN, buff=0.35)

        self._reveal_rows(rows, glow_indices={3}, glow_color=GREEN)

        self.wait(3.5)
        self._next_slide()
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 6: Q1d — 10x Load ──────────────────────────────────────
    def scene_q1_scale_10x(self):
        header = self._section_header("Q1d: Scaling to 10,000 r/s", color=PURPLE)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.4)

        sub = make_label(
            "Queueing appears once 1 core saturates — pick one:",
            font_size=13, color=GREY_A,
        )
        sub.next_to(header, DOWN, buff=0.2)
        self.play(FadeIn(sub))
        self.wait(0.3)

        opts = VGroup(
            self._icon_row_card(
                ICON_CPU_BOLT, BLUE,
                "Vertical scale",
                "Bigger machine: more cores + more memory",
            ),
            self._icon_row_card(
                ICON_SERVER, GREEN,
                "Horizontal scale",
                ">10 servers behind a load balancer (same disks)",
            ),
            self._icon_row_card(
                ICON_LIGHTNING, ORANGE,
                "Faster disks",
                "10x faster tier => single request gets quicker too",
            ),
        ).arrange(DOWN, buff=0.14).next_to(sub, DOWN, buff=0.25)

        self._reveal_rows(opts, glow_indices={1}, glow_color=GREEN)

        # Mini diagram: LB → 11 servers
        lb_box = RoundedRectangle(
            corner_radius=0.1, width=2.4, height=0.55,
            fill_color=DARK_BG, fill_opacity=0.92,
            stroke_color=GREEN, stroke_width=1.5,
        )
        lb_lbl = make_label("Load Balancer", font_size=11, color=GREEN)
        lb_lbl.move_to(lb_box.get_center())
        lb = VGroup(lb_box, lb_lbl)

        servers = VGroup()
        for i, txt in enumerate(["Server 1", "Server 2", "...", "Server 11"]):
            sb = RoundedRectangle(
                corner_radius=0.08, width=1.4, height=0.45,
                fill_color=DARK_BG, fill_opacity=0.92,
                stroke_color=BLUE, stroke_width=1.2,
            )
            sl = make_label(txt, font_size=10, color=BLUE)
            sl.move_to(sb.get_center())
            servers.add(VGroup(sb, sl))
        servers.arrange(RIGHT, buff=0.2)

        diagram = VGroup(lb, servers).arrange(DOWN, buff=0.5)
        diagram.to_edge(DOWN, buff=0.3)

        arrows = VGroup()
        for s in servers:
            arrows.add(Arrow(
                lb.get_bottom(), s.get_top(),
                buff=0.05, stroke_width=1.4, color=GREY_A, tip_length=0.12,
            ))

        self._next_slide(phase=True)
        self.play(FadeIn(diagram, shift=UP * 0.15))
        self.play(AnimationGroup(*[GrowArrow(a) for a in arrows], lag_ratio=0.12))
        self.wait(3)
        self._next_slide()
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 7: Q1e — Optimized Disks ───────────────────────────────
    def scene_q1_optimized_disks(self):
        header = self._section_header("Q1e: Optimized Disk Count (Splitting OK)", color=TEAL)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.4)

        assume = make_label(
            "Allow splitting a 300 KB note across 2 disks",
            font_size=15, color=GREY_A,
        )
        assume.next_to(header, DOWN, buff=0.3)
        self.play(FadeIn(assume, shift=UP * 0.1))
        self.wait(0.3)
        self._next_slide(phase=True)

        # Image-style colored math rows
        line1 = self._calc_line([
            ("Requests/disk ", GREY_A),
            ("128 MB", YELLOW), (" / ", GREY_A), ("300 KB", YELLOW),
            (" ≈ ", GREY_A), ("426.67", YELLOW),
        ], font_size=18)
        line2 = self._calc_line([
            ("Without split ", GREY_A),
            ("⌈", YELLOW), ("86.4M", YELLOW), (" / ", GREY_A), ("426", YELLOW), ("⌉", YELLOW),
            (" = ", GREY_A),
            ("202,817 disks", YELLOW),
        ], font_size=18)
        line3 = self._calc_line([
            ("With split ", GREY_A),
            ("⌈", GREEN), ("86.4M", GREEN), (" / ", GREY_A), ("426.67", GREEN), ("⌉", GREEN),
            (" = ", GREY_A),
            ("202,500 disks", GREEN),
        ], font_size=18)

        calc = VGroup(line1, line2, line3).arrange(DOWN, buff=0.2, aligned_edge=LEFT)
        calc.next_to(assume, DOWN, buff=0.5)

        self.play(FadeIn(line1, shift=UP * 0.1))
        self.wait(0.4)
        self._next_slide(phase=True)
        self.play(FadeIn(line2, shift=UP * 0.1))
        self.wait(0.4)
        self._next_slide(phase=True)
        self.play(FadeIn(line3, shift=UP * 0.1))
        self.wait(0.4)
        self._next_slide(phase=True)

        # Divider under the math
        divider = Line(
            calc.get_left() + DOWN * 0.18 + RIGHT * 0.5,
            calc.get_right() + DOWN * 0.18 - RIGHT * 0.5,
            stroke_color=GREY_B, stroke_width=1.2,
        )
        divider.next_to(line3, DOWN, buff=0.15, aligned_edge=LEFT)
        self.play(FadeIn(divider))

        saved = self._calc_line([
            ("Saved ", GREY_A),
            ("317 disks", YELLOW),
            ("   ≈   ", GREY_A),
            ("$6.89 / day", GREEN),
        ], font_size=20)
        saved.next_to(divider, DOWN, buff=0.25, aligned_edge=LEFT)

        glow = create_rect_glow(saved, color=TEAL, max_opacity=0.3, spread=0.35)
        self.add(glow)
        self.bring_to_back(glow)
        glow.set_opacity(0)
        self.play(FadeIn(saved, shift=UP * 0.1))
        self._play_glow_row(saved, glow, TEAL)
        self.wait(3)
        self._next_slide()
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 8: Q2 Intro ────────────────────────────────────────────
    def scene_q2_intro(self):
        header = self._section_header("Q2: Twitter — Slow Tweet Submission", color=BLUE)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.4)

        ctx = VGroup(
            self._icon_row_card(
                ICON_USER, RED,
                "Symptom",
                "Users complain about delay between submit & timeline display",
            ),
            self._icon_row_card(
                ICON_STOPWATCH, ORANGE,
                "Measured p90",
                "300 ms for submit-tweet request",
            ),
            self._icon_row_card(
                ICON_CHART, BLUE,
                "Target",
                "Lower p90 to 300 us (1000x faster) — tweet size = 8 KB",
            ),
        ).arrange(DOWN, buff=0.14).next_to(header, DOWN, buff=0.35)

        self._reveal_rows(ctx, glow_indices={2}, glow_color=BLUE)

        self.wait(3)
        self._next_slide()
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 9: Q2a — Causes ────────────────────────────────────────
    def scene_q2_causes(self):
        header = self._section_header("Q2a: 4 Possible Causes of Slow p90", color=ORANGE)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.4)

        framing = make_label(
            "Complaining users likely high-profile: famous bloggers, news channels, etc.",
            font_size=12, color=YELLOW,
        )
        framing.next_to(header, DOWN, buff=0.2)
        self.play(FadeIn(framing))
        self.wait(0.3)

        rows = VGroup(
            self._icon_row_card(
                ICON_MONITOR, BLUE,
                "1. Network congestion",
                "Queueing at internal switches / routers",
            ),
            self._icon_row_card(
                ICON_LAYERS, ORANGE,
                "2. Software queueing",
                "Rush-hour spikes overload thread pools",
            ),
            self._icon_row_card(
                ICON_DATABASE, PURPLE,
                "3. Disk defragmentation",
                "Background defrag process steals I/O bandwidth",
            ),
            self._icon_row_card(
                ICON_LIGHTNING, RED,
                "4. GC pressure",
                "Garbage collection pauses block the request",
            ),
        ).arrange(DOWN, buff=0.14).next_to(framing, DOWN, buff=0.25)

        self._reveal_rows(rows, glow_indices={0, 1, 2, 3}, glow_color=ORANGE)
        self.wait(3)
        self._next_slide()
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 10: Q2b — Architectural Change ─────────────────────────
    def scene_q2_architectural(self):
        header = self._section_header("Q2b: Architectural Change => 300 us", color=GREEN)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.4)

        intro = self._icon_row_card(
            ICON_CPU_BOLT, YELLOW,
            "Order-of-magnitude wins",
            "Need major architectural change — not micro-optimization",
        )
        intro.next_to(header, DOWN, buff=0.25)
        self.play(FadeIn(intro, shift=UP * 0.1))
        self.wait(0.3)
        self._next_slide(phase=True)

        l1 = self._calc_line([
            ("tweet_size ", GREY_A), ("= ", GREY_A), ("8 KB", YELLOW),
        ], font_size=18)
        l2 = self._calc_line([
            ("SSD: ", GREY_A), ("4 KB", YELLOW), (" takes ", GREY_A), ("150 us", YELLOW),
        ], font_size=18)
        l3 = self._calc_line([
            ("service_time ", GREY_A), ("= ", GREY_A),
            ("(8 KB / 4 KB)", YELLOW), (" × ", GREY_A), ("150 us", YELLOW),
        ], font_size=18)
        l4 = self._calc_line([
            ("             = ", GREY_A),
            ("2", YELLOW), (" × ", GREY_A), ("150 us", YELLOW),
            ("  =  ", GREY_A), ("300 us", GREEN), ("  ✓", GREEN),
        ], font_size=18)
        calc = VGroup(l1, l2, l3, l4).arrange(DOWN, buff=0.18, aligned_edge=LEFT)
        calc.next_to(intro, DOWN, buff=0.4)
        for ln in [l1, l2, l3, l4]:
            self.play(FadeIn(ln, shift=UP * 0.1)); self.wait(0.2)
        self.wait(0.4)
        self._next_slide(phase=True)

        ans_box = RoundedRectangle(
            corner_radius=0.12, width=5.0, height=0.85,
            fill_color=DARK_BG, fill_opacity=0.95,
            stroke_color=GREEN, stroke_width=2.0,
        )
        ans_lbl = make_label("SSD => p90 = 300 us", font_size=22, color=GREEN)
        ans_lbl.move_to(ans_box.get_center())
        ans = VGroup(ans_box, ans_lbl).to_edge(DOWN, buff=0.45)
        glow = create_rect_glow(ans, color=GREEN, max_opacity=0.32, spread=0.35)
        self.add(glow)
        self.bring_to_back(glow)
        glow.set_opacity(0)
        self.play(FadeIn(ans, shift=UP * 0.1))
        self._play_glow_row(ans, glow, GREEN)
        self.wait(3)
        self._next_slide()
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 11: Q2c — Partition by Customer Tier ───────────────────
    def scene_q2_partition_customers(self):
        header = self._section_header("Q2c: Cost-Aware Tiering by Customer", color=PURPLE)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.4)

        problem = self._icon_row_card(
            ICON_SETTINGS, RED,
            "Problem with universal SSD",
            "Paying for SSD across 1,110,100 users — most are not complaining",
        )
        problem.next_to(header, DOWN, buff=0.22)
        self.play(FadeIn(problem, shift=UP * 0.1))
        self.wait(0.3)
        self._next_slide(phase=True)

        # Tier table: 4 rows × 3 cols (followers, count, storage)
        tier_rows_data = [
            ("1M+ followers",            "100",        "nVME — 30 us",                              TEAL),
            ("< 100K followers",         "10,000",     "SSD — 300 us",                              GREEN),
            ("< 10K followers",          "100,000",    "Disk — 30 ms",                              ORANGE),
            ("< 1K followers",           "1,000,000",  "Disk + heavy compression — 30 ms+",         RED),
        ]
        col_w = [2.4, 1.7, 4.2]
        col_x = [-3.6, -1.05, 1.85]

        def _cell(text, x, y, w, color, fs=11):
            box = RoundedRectangle(
                corner_radius=0.06, width=w, height=0.5,
                fill_color=DARK_BG, fill_opacity=0.9,
                stroke_color=color, stroke_width=1.0,
            )
            box.move_to([x, y, 0])
            lbl = make_label(text, font_size=fs, color=color)
            lbl.move_to(box.get_center())
            return VGroup(box, lbl)

        # Header row
        hdr_y = -0.4
        hdr_cells = VGroup(
            _cell("Customer Tier", col_x[0], hdr_y, col_w[0], GREY_A, fs=11),
            _cell("Count",         col_x[1], hdr_y, col_w[1], GREY_A, fs=11),
            _cell("Storage Layer", col_x[2], hdr_y, col_w[2], GREY_A, fs=11),
        )
        self.play(FadeIn(hdr_cells))
        self.wait(0.2)

        table_rows = []
        for i, (tier, cnt, store, color) in enumerate(tier_rows_data):
            y = hdr_y - 0.55 * (i + 1)
            row = VGroup(
                _cell(tier,  col_x[0], y, col_w[0], color),
                _cell(cnt,   col_x[1], y, col_w[1], color),
                _cell(store, col_x[2], y, col_w[2], color),
            )
            table_rows.append(row)

        # Reveal with glow on the 1M+ premium tier (where complaints come from)
        glow_idx = {0}
        glow_map = {}
        for i in glow_idx:
            g = create_rect_glow(table_rows[i], color=TEAL, max_opacity=0.28, spread=0.3)
            self.add(g)
            self.bring_to_back(g)
            g.set_opacity(0)
            glow_map[i] = g

        for i, row in enumerate(table_rows):
            self.play(FadeIn(row, shift=LEFT * 0.1), run_time=0.32)
            if i in glow_map:
                self._play_glow_row(row, glow_map[i], TEAL)
            if i < len(table_rows) - 1:
                self._next_slide(phase=True)

        note = make_label(
            "Premium users get nVME · majority on cheap disks + compression — both sides happy",
            font_size=11, color=YELLOW,
        )
        note.to_edge(DOWN, buff=0.35)
        self.play(FadeIn(note, shift=UP * 0.1))
        self.wait(4)
        self._next_slide()
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 12: Q3 Intro ───────────────────────────────────────────
    def scene_q3_intro(self):
        header = self._section_header("Q3: Cell Tower Heartbeat Monitoring", color=ORANGE)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.4)

        ctx = VGroup(
            self._icon_row_card(
                ICON_SERVER, BLUE,
                "Compute",
                "1 machine · 1 core (handles exactly the given load)",
            ),
            self._icon_row_card(
                ICON_LIGHTNING, ORANGE,
                "Load",
                "1,000,000 heartbeats / minute from 100 towers",
            ),
            self._icon_row_card(
                ICON_MONITOR, GREEN,
                "Live dashboard",
                "10x10 grid — green if last 10 heartbeats on time, red otherwise",
            ),
            self._icon_row_card(
                ICON_CHART, PURPLE,
                "History view",
                "Per-tower history for last 30 days",
            ),
        ).arrange(DOWN, buff=0.14).next_to(header, DOWN, buff=0.3)

        self._reveal_rows(ctx, glow_indices={1}, glow_color=ORANGE)
        self.wait(3)
        self._next_slide()
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 13: Q3a — Storage Size ─────────────────────────────────
    def scene_q3_storage_size(self):
        header = self._section_header("Q3a: Storage Size — 30 Days × 100 Towers", color=BLUE)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.4)

        schema_title = make_label("Heartbeat message schema", font_size=14, color=BLUE)
        s1 = self._calc_line([("tower_id   ", GREY_A), ("7 bits  ≈ 1 byte", YELLOW)], font_size=15)
        s2 = self._calc_line([("timestamp  ", GREY_A), ("long    = 8 bytes", YELLOW)], font_size=15)
        s3 = self._calc_line([("total      ", GREY_A), ("= 9 bytes", GREEN)], font_size=15)
        msg_format = VGroup(schema_title, s1, s2, s3).arrange(DOWN, buff=0.1, aligned_edge=LEFT)
        msg_format.next_to(header, DOWN, buff=0.3)
        self.play(FadeIn(msg_format))
        self.wait(0.3)
        self._next_slide(phase=True)

        c1 = self._calc_line([
            ("Per-tower rate ", GREY_A),
            ("1,000,000", YELLOW), (" / ", GREY_A), ("100", YELLOW),
            (" = ", GREY_A), ("10,000 msg / min", YELLOW),
        ], font_size=16)
        c2 = self._calc_line([
            ("Minutes in 30 days ", GREY_A),
            ("1440", YELLOW), (" × ", GREY_A), ("30", YELLOW),
            (" = ", GREY_A), ("43,200 min", YELLOW),
        ], font_size=16)
        c3 = self._calc_line([
            ("Messages ", GREY_A),
            ("100", YELLOW), (" × ", GREY_A), ("10,000", YELLOW), (" × ", GREY_A), ("43,200", YELLOW),
            (" = ", GREY_A), ("43.2 B", YELLOW),
        ], font_size=16)
        c4 = self._calc_line([
            ("Storage ", GREY_A),
            ("43.2 B", YELLOW), (" × ", GREY_A), ("9 bytes", YELLOW),
            ("  ≈  ", GREY_A), ("432 GB", GREEN),
        ], font_size=16)
        calc = VGroup(c1, c2, c3, c4).arrange(DOWN, buff=0.16, aligned_edge=LEFT)
        calc.next_to(msg_format, DOWN, buff=0.35, aligned_edge=LEFT)
        for ln in [c1, c2, c3, c4]:
            self.play(FadeIn(ln, shift=UP * 0.1))
            self.wait(0.2)
        self._next_slide(phase=True)

        ans_box = RoundedRectangle(
            corner_radius=0.12, width=4.5, height=0.85,
            fill_color=DARK_BG, fill_opacity=0.95,
            stroke_color=GREEN, stroke_width=2.0,
        )
        ans_lbl = make_label("~432 GB total", font_size=22, color=GREEN)
        ans_lbl.move_to(ans_box.get_center())
        ans = VGroup(ans_box, ans_lbl).to_edge(DOWN, buff=0.4)
        glow = create_rect_glow(ans, color=GREEN, max_opacity=0.32, spread=0.35)
        self.add(glow)
        self.bring_to_back(glow)
        glow.set_opacity(0)
        self.play(FadeIn(ans, shift=UP * 0.1))
        self._play_glow_row(ans, glow, GREEN)
        self.wait(3)
        self._next_slide()
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 14: Q3b — Hot / Cold Storage Types ─────────────────────
    def scene_q3_storage_types(self):
        header = self._section_header("Q3b: Storage Types — Hot vs Cold", color=PURPLE)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.4)

        hot = self._icon_row_card(
            ICON_LIGHTNING, RED,
            "HOT  — last 10 messages / tower",
            "SSD + in-memory cache  =>  drives the 10x10 live grid",
        )
        cold = self._icon_row_card(
            ICON_LAYERS, BLUE,
            "COLD — last 30 days of history",
            "HDD or SSD  =>  per-tower history view (less frequent)",
        )
        stack = VGroup(hot, cold).arrange(DOWN, buff=0.2).next_to(header, DOWN, buff=0.35)

        self._reveal_rows(stack, glow_indices={0, 1}, glow_color=PURPLE)

        mapping = self._code_box(
            [
                "Functionality            ->  Storage",
                "  live 10x10 grid        ->  HOT  (SSD / cache)",
                "  30-day tower history   ->  COLD (HDD or SSD)",
            ],
            "Mapping",
            YELLOW,
            width=7.0,
        )
        mapping.to_edge(DOWN, buff=0.4)
        self.play(FadeIn(mapping, shift=UP * 0.1))
        self.wait(3.5)
        self._next_slide()
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 15: Q3c — Request Service Time ─────────────────────────
    def scene_q3_service_time(self):
        header = self._section_header("Q3c: View-Tower Request Service Time", color=TEAL)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.4)

        hot_title = make_label("HOT path — last 10 messages", font_size=15, color=GREEN)
        h1 = self._calc_line([("read_size  ", GREY_A), ("10 × 9 bytes", YELLOW), (" = ", GREY_A), ("90 bytes", YELLOW)], font_size=14)
        h2 = self._calc_line([("fits in ", GREY_A), ("1 page", YELLOW), ("  →  ", GREY_A), ("1 read", YELLOW)], font_size=14)
        h3 = self._calc_line([("SSD read ", GREY_A), ("= ", GREY_A), ("16 us", GREEN)], font_size=14)
        hot_calc = VGroup(hot_title, h1, h2, h3).arrange(DOWN, buff=0.12, aligned_edge=LEFT)

        cold_title = make_label("COLD path — last 30 days", font_size=15, color=ORANGE)
        c1 = self._calc_line([("read_size  ", GREY_A), ("30 days", YELLOW), (" = ", GREY_A), ("4.32 GB", YELLOW)], font_size=14)
        c2 = self._calc_line([("page_size ", GREY_A), ("1 MB", YELLOW), ("  →  ", GREY_A), ("4,320 pages", YELLOW)], font_size=14)
        c3 = self._calc_line([("random read ", GREY_A), ("250 us / page", YELLOW)], font_size=14)
        c4 = self._calc_line([("service_time ", GREY_A), ("4,320", YELLOW), (" × ", GREY_A), ("250 us", YELLOW), ("  =  ", GREY_A), ("1.08 s", ORANGE)], font_size=14)
        cold_calc = VGroup(cold_title, c1, c2, c3, c4).arrange(DOWN, buff=0.12, aligned_edge=LEFT)

        cols = VGroup(hot_calc, cold_calc).arrange(RIGHT, buff=0.6, aligned_edge=UP)
        cols.next_to(header, DOWN, buff=0.4)

        self.play(FadeIn(hot_calc, shift=RIGHT * 0.15))
        self.wait(0.3)
        self._next_slide(phase=True)
        self.play(FadeIn(cold_calc, shift=LEFT * 0.15))
        self.wait(0.3)
        self._next_slide(phase=True)

        # Final answer banner
        ans_box = RoundedRectangle(
            corner_radius=0.12, width=8.5, height=0.85,
            fill_color=DARK_BG, fill_opacity=0.95,
            stroke_color=TEAL, stroke_width=2.0,
        )
        ans_lbl = make_label("hot = 16 us   ·   cold = 1.08 s", font_size=20, color=TEAL)
        ans_lbl.move_to(ans_box.get_center())
        ans = VGroup(ans_box, ans_lbl).to_edge(DOWN, buff=0.4)
        glow = create_rect_glow(ans, color=TEAL, max_opacity=0.32, spread=0.35)
        self.add(glow)
        self.bring_to_back(glow)
        glow.set_opacity(0)
        self.play(FadeIn(ans, shift=UP * 0.1))
        self._play_glow_row(ans, glow, TEAL)
        self.wait(3)
        self._next_slide()
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 16: Q3d — Scaling Machines ─────────────────────────────
    def scene_q3_scale_machines(self):
        header = self._section_header("Q3d: Scale to 10M Heartbeats / sec", color=RED)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.4)

        # Image-style framing: 1M/min ≈ 16.7K/s → 600× more load
        cur = self._calc_line([
            ("Current: ", GREY_A),
            ("1M/min", YELLOW), (" ≈ ", GREY_A), ("16.7K/s", YELLOW),
            (" on 1 machine.", GREY_A),
        ], font_size=20)
        tgt = self._calc_line([
            ("Target: ", GREY_A),
            ("10M/s", YELLOW), ("  →  ", GREY_A),
            ("~600× more load", RED),
        ], font_size=20)
        framing = VGroup(cur, tgt).arrange(DOWN, buff=0.2, aligned_edge=LEFT)
        framing.next_to(header, DOWN, buff=0.45)

        framing_glow = create_rect_glow(tgt, color=RED, max_opacity=0.32, spread=0.35)
        self.add(framing_glow)
        self.bring_to_back(framing_glow)
        framing_glow.set_opacity(0)

        self.play(FadeIn(cur, shift=UP * 0.1))
        self.wait(0.4)
        self._next_slide(phase=True)
        self.play(FadeIn(tgt, shift=UP * 0.1))
        self._play_glow_row(tgt, framing_glow, RED)
        self.wait(0.4)
        self._next_slide(phase=True)

        # Plan rows
        plan = VGroup(
            self._icon_row_card(
                ICON_TRANSFER, GREEN,
                "Load balancer in front",
                "Fans 10M/s evenly across the worker pool",
            ),
            self._icon_row_card(
                ICON_SERVER, BLUE,
                "~600 worker machines",
                "Each handles ≈ 1M/min (same as today's single box)",
            ),
        ).arrange(DOWN, buff=0.14).next_to(framing, DOWN, buff=0.4)
        self._reveal_rows(plan, glow_indices={1}, glow_color=BLUE)

        # Mini LB → N servers diagram
        lb_box = RoundedRectangle(
            corner_radius=0.1, width=2.6, height=0.5,
            fill_color=DARK_BG, fill_opacity=0.92,
            stroke_color=GREEN, stroke_width=1.5,
        )
        lb_lbl = make_label("Load Balancer", font_size=11, color=GREEN)
        lb_lbl.move_to(lb_box.get_center())
        lb = VGroup(lb_box, lb_lbl)

        servers = VGroup()
        for txt in ["Worker 1", "Worker 2", "...", "Worker ~600"]:
            sb = RoundedRectangle(
                corner_radius=0.08, width=1.5, height=0.4,
                fill_color=DARK_BG, fill_opacity=0.92,
                stroke_color=BLUE, stroke_width=1.2,
            )
            sl = make_label(txt, font_size=9, color=BLUE)
            sl.move_to(sb.get_center())
            servers.add(VGroup(sb, sl))
        servers.arrange(RIGHT, buff=0.18)

        diagram = VGroup(lb, servers).arrange(DOWN, buff=0.4)
        diagram.to_edge(DOWN, buff=0.35)

        arrows = VGroup()
        for s in servers:
            arrows.add(Arrow(
                lb.get_bottom(), s.get_top(),
                buff=0.05, stroke_width=1.4, color=GREY_A, tip_length=0.12,
            ))

        self.play(FadeIn(diagram, shift=UP * 0.15))
        self.play(AnimationGroup(*[GrowArrow(a) for a in arrows], lag_ratio=0.12))
        self.wait(3)
        self._next_slide()
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 17: Closing ────────────────────────────────────────────
    def scene_closing(self):
        title = make_label("Sheet 1: Hardware & System Sizing", font_size=32, color=TEAL)
        title.move_to(UP * 1.8)
        self.play(AddTextLetterByLetter(title, time_per_char=0.05))
        self.wait(0.8)

        icon_data = [
            (ICON_CPU_BOLT,  TEAL),
            (ICON_DATABASE,  BLUE),
            (ICON_LIGHTNING, ORANGE),
            (ICON_STOPWATCH, GREEN),
            (ICON_CHART,     PURPLE),
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
            "Service Time  ·  Disk Sizing  ·  p90  ·  Scaling  ·  Tiering",
            font_size=17, color=GREY_A,
        )
        themes.move_to(DOWN * 1.5)
        self.play(FadeIn(themes, shift=UP * 0.2))
        self.wait(4)
        self._next_slide()
        self.play(FadeOut(*self.mobjects))
