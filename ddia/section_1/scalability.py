import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from manim import *

from libs.ddia_components import (
    DARK_BG,
    ICON_SCALE, ICON_SERVER, ICON_DATABASE, ICON_STOPWATCH,
    ICON_USER, ICON_LIGHTNING, ICON_MONITOR, ICON_SETTINGS,
    make_label, make_icon, make_icon_card,
)

config.background_color = "#0D1117"


class Scalability(Scene):
    def construct(self):
        self.scene_title()
        self.scene_describing_load()
        self.scene_describing_performance()
        self.scene_percentiles()
        self.scene_scale_up_vs_out()
        self.scene_elastic_vs_manual()
        self.scene_no_magic_sauce()
        self.scene_closing()

    # ─── Scene 1: Title ───────────────────────────────────────────────
    def scene_title(self):
        icon = make_icon(ICON_SCALE, color=ORANGE, height=1.2)
        title = make_label("Scalability", font_size=44, color=ORANGE)
        subtitle = make_label(
            "Designing Data-Intensive Applications — Ch. 1",
            font_size=20, color=GREY_B,
        )
        VGroup(icon, title, subtitle).arrange(DOWN, buff=0.4)

        self.play(FadeIn(icon, shift=DOWN * 0.3))
        self.wait(0.5)
        self.play(AddTextLetterByLetter(title, time_per_char=0.05))
        self.wait(0.5)
        self.play(FadeIn(subtitle, shift=UP * 0.2))
        self.wait(3)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 2: Describing Load ─────────────────────────────────────
    def scene_describing_load(self):
        header = make_label("Describing Load", font_size=30, color=BLUE)
        header.to_edge(UP, buff=0.5)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(1)

        quote = make_label(
            '"Load can be described with a few numbers\n'
            ' called load parameters."',
            font_size=20, color=YELLOW,
        )
        quote.next_to(header, DOWN, buff=0.5)
        self.play(FadeIn(quote, shift=UP * 0.2))
        self.wait(2)

        # Load parameter examples as icon cards
        params = [
            (ICON_LIGHTNING, ORANGE, "Requests/sec",
             "Web server throughput"),
            (ICON_DATABASE, BLUE, "Read/Write\nRatio",
             "DB workload shape"),
            (ICON_USER, GREEN, "Active Users",
             "Concurrent sessions"),
            (ICON_STOPWATCH, PURPLE, "Cache Hit\nRate",
             "% served from cache"),
        ]

        cards = VGroup()
        for icon_path, color, title, desc in params:
            ic = make_icon(icon_path, color=color, height=0.35)
            t = make_label(title, font_size=13, color=color, weight=BOLD)
            d = make_label(desc, font_size=10, color=GREY_A)
            content = VGroup(ic, t, d).arrange(DOWN, buff=0.1)
            box = RoundedRectangle(
                corner_radius=0.12, width=2.6, height=1.7,
                fill_color=DARK_BG, fill_opacity=0.9,
                stroke_color=color, stroke_width=1.5,
            )
            content.move_to(box.get_center())
            cards.add(VGroup(box, content))

        cards.arrange(RIGHT, buff=0.25).next_to(quote, DOWN, buff=0.5)

        self.play(
            AnimationGroup(
                *[FadeIn(c, shift=UP * 0.3) for c in cards],
                lag_ratio=0.15,
            )
        )
        self.wait(2)

        for c in cards:
            self.play(Indicate(c, color=YELLOW, scale_factor=1.05), run_time=0.4)
            self.wait(0.3)

        self.wait(1)

        bottom = make_label(
            "Choose the parameters that matter most for YOUR system",
            font_size=17, color=GREY_A,
        )
        bottom.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(bottom, shift=UP * 0.2))
        self.wait(3)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 3: Describing Performance ──────────────────────────────
    def scene_describing_performance(self):
        header = make_label("Describing Performance", font_size=30, color=GREEN)
        header.to_edge(UP, buff=0.5)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(1)

        # Two key questions
        q1 = make_label(
            "Load ↑, Resources same → What happens to performance?",
            font_size=16, color=YELLOW,
        )
        q2 = make_label(
            "Load ↑, Performance same → How many more resources?",
            font_size=16, color=YELLOW,
        )
        questions = VGroup(q1, q2).arrange(DOWN, buff=0.25)
        questions.next_to(header, DOWN, buff=0.5)
        self.play(FadeIn(q1, shift=UP * 0.2))
        self.wait(2)
        self.play(FadeIn(q2, shift=UP * 0.2))
        self.wait(2)

        # Two metric types side by side
        # Left: Throughput (batch)
        left_title = make_label("Batch Systems", font_size=18, color=BLUE)
        left_metric = make_label("Throughput", font_size=22, color=BLUE, weight=BOLD)
        left_desc = make_label("records/sec or\ntotal job time", font_size=12, color=GREY_A)
        left_icon = make_icon(ICON_DATABASE, color=BLUE, height=0.4)
        left_content = VGroup(left_icon, left_title, left_metric, left_desc).arrange(DOWN, buff=0.12)
        left_box = RoundedRectangle(
            corner_radius=0.15, width=4.0, height=2.8,
            fill_color=DARK_BG, fill_opacity=0.9, stroke_color=BLUE, stroke_width=1.5,
        )
        left_content.move_to(left_box.get_center())
        left_group = VGroup(left_box, left_content).move_to(LEFT * 3 + DOWN * 1.0)

        # Right: Response Time (online)
        right_title = make_label("Online Systems", font_size=18, color=ORANGE)
        right_metric = make_label("Response Time", font_size=22, color=ORANGE, weight=BOLD)
        right_desc = make_label("time from request\nto response", font_size=12, color=GREY_A)
        right_icon = make_icon(ICON_LIGHTNING, color=ORANGE, height=0.4)
        right_content = VGroup(right_icon, right_title, right_metric, right_desc).arrange(DOWN, buff=0.12)
        right_box = RoundedRectangle(
            corner_radius=0.15, width=4.0, height=2.8,
            fill_color=DARK_BG, fill_opacity=0.9, stroke_color=ORANGE, stroke_width=1.5,
        )
        right_content.move_to(right_box.get_center())
        right_group = VGroup(right_box, right_content).move_to(RIGHT * 3 + DOWN * 1.0)

        self.play(FadeIn(left_group, shift=RIGHT * 0.3))
        self.wait(1.5)
        self.play(FadeIn(right_group, shift=LEFT * 0.3))
        self.wait(3)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 4: Percentiles ─────────────────────────────────────────
    def scene_percentiles(self):
        header = make_label("Why Percentiles Matter", font_size=30, color=PURPLE)
        header.to_edge(UP, buff=0.5)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(1)

        # Visual: a bar chart representing response time distribution
        note = make_label(
            "Average hides outliers — use percentiles instead",
            font_size=18, color=YELLOW,
        )
        note.next_to(header, DOWN, buff=0.4)
        self.play(FadeIn(note, shift=UP * 0.2))
        self.wait(2)

        # Histogram bars (stylized)
        bar_heights = [0.3, 0.8, 1.8, 2.8, 3.2, 2.5, 1.4, 0.7, 0.35, 0.2, 0.12, 0.08]
        bar_colors = [GREEN] * 8 + [ORANGE] * 2 + [RED] * 2
        bars = VGroup()
        for i, (h, c) in enumerate(zip(bar_heights, bar_colors)):
            bar = Rectangle(
                width=0.45, height=h,
                fill_color=c, fill_opacity=0.7,
                stroke_color=c, stroke_width=1,
            )
            bars.add(bar)
        bars.arrange(RIGHT, buff=0.06, aligned_edge=DOWN)
        bars.move_to(LEFT * 0.5 + DOWN * 0.3)

        # X-axis labels
        x_label = make_label("Response Time →", font_size=12, color=GREY_A)
        x_label.next_to(bars, DOWN, buff=0.2)

        self.play(
            AnimationGroup(
                *[GrowFromEdge(b, DOWN) for b in bars],
                lag_ratio=0.06,
            )
        )
        self.play(FadeIn(x_label))
        self.wait(1.5)

        # Percentile markers
        # p50 at bar index ~4 (median), p95 at ~8, p99 at ~10
        p50_line = DashedLine(
            bars[4].get_top() + UP * 0.15, bars[4].get_bottom() + DOWN * 0.3,
            color=GREEN, stroke_width=2,
        )
        p50_label = make_label("p50\nMedian", font_size=11, color=GREEN)
        p50_label.next_to(p50_line, UP, buff=0.1)

        p95_line = DashedLine(
            bars[8].get_top() + UP * 0.15, bars[8].get_bottom() + DOWN * 0.3,
            color=ORANGE, stroke_width=2,
        )
        p95_label = make_label("p95", font_size=11, color=ORANGE)
        p95_label.next_to(p95_line, UP, buff=0.1)

        p99_line = DashedLine(
            bars[10].get_top() + UP * 0.15, bars[10].get_bottom() + DOWN * 0.3,
            color=RED, stroke_width=2,
        )
        p99_label = make_label("p99", font_size=11, color=RED)
        p99_label.next_to(p99_line, UP, buff=0.1)

        self.play(Create(p50_line), FadeIn(p50_label))
        self.wait(1)
        self.play(Create(p95_line), FadeIn(p95_label))
        self.wait(1)
        self.play(Create(p99_line), FadeIn(p99_label))
        self.wait(2)

        # Tail latency callout
        tail_box = RoundedRectangle(
            corner_radius=0.1, width=4.5, height=0.8,
            fill_color=DARK_BG, fill_opacity=0.95,
            stroke_color=RED, stroke_width=1.5,
        )
        tail_text = make_label(
            "Tail latencies (p99.9) affect\nyour most valuable customers",
            font_size=13, color=RED,
        )
        tail_text.move_to(tail_box.get_center())
        tail_group = VGroup(tail_box, tail_text)
        tail_group.to_edge(DOWN, buff=0.4)

        self.play(FadeIn(tail_group, shift=UP * 0.2))
        self.wait(3)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 5: Scale Up vs Scale Out ───────────────────────────────
    def scene_scale_up_vs_out(self):
        header = make_label("Coping with Load", font_size=30, color=ORANGE)
        header.to_edge(UP, buff=0.5)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(1)

        # ── Left: Scale Up (Vertical) ──
        left_title = make_label("Scale Up", font_size=20, color=BLUE, weight=BOLD)
        left_sub = make_label("(Vertical Scaling)", font_size=13, color=GREY_A)

        # One big server, growing
        big_server = make_icon_card(
            "BIG Machine", ICON_SERVER,
            color=BLUE, width=2.6, height=1.8, font_size=12,
        )
        up_arrow = Arrow(
            big_server.get_bottom() + DOWN * 0.1, big_server.get_top() + UP * 0.1,
            buff=0, stroke_width=3, color=BLUE, tip_length=0.15,
        ).next_to(big_server, LEFT, buff=0.15)
        up_label = make_label("More\nCPU/RAM", font_size=10, color=BLUE)
        up_label.next_to(up_arrow, LEFT, buff=0.1)

        left_group = VGroup(left_title, left_sub, big_server).arrange(DOWN, buff=0.15)
        up_arrow.next_to(big_server, LEFT, buff=0.15)
        up_label.next_to(up_arrow, LEFT, buff=0.1)
        left_all = VGroup(left_group, up_arrow, up_label).move_to(LEFT * 3.5 + DOWN * 0.5)

        # ── Right: Scale Out (Horizontal) ──
        right_title = make_label("Scale Out", font_size=20, color=GREEN, weight=BOLD)
        right_sub = make_label("(Horizontal Scaling)", font_size=13, color=GREY_A)

        small_servers = VGroup()
        for i in range(6):
            s = make_icon_card(
                f"Node {i + 1}", ICON_SERVER,
                color=GREEN, width=1.2, height=0.8, font_size=8,
            )
            small_servers.add(s)
        small_servers.arrange_in_grid(rows=2, cols=3, buff=0.12)

        right_group = VGroup(right_title, right_sub, small_servers).arrange(DOWN, buff=0.15)
        right_group.move_to(RIGHT * 3.2 + DOWN * 0.5)

        self.play(FadeIn(left_all, shift=RIGHT * 0.3))
        self.wait(1)
        self.play(GrowArrow(up_arrow), FadeIn(up_label))
        self.wait(2)

        self.play(FadeIn(right_group, shift=LEFT * 0.3))
        self.wait(2)

        # VS label
        vs = make_label("VS", font_size=26, color=ORANGE)
        vs.move_to(ORIGIN + DOWN * 0.5)
        self.play(FadeIn(vs, scale=1.5))
        self.wait(1)

        # Bottom insight
        insight = make_label(
            "In practice: a pragmatic mix of both approaches",
            font_size=18, color=YELLOW,
        )
        insight.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(insight, shift=UP * 0.2))
        self.wait(3)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 6: Elastic vs Manual Scaling ───────────────────────────
    def scene_elastic_vs_manual(self):
        header = make_label("Elastic vs Manual Scaling", font_size=30, color=TEAL)
        header.to_edge(UP, buff=0.5)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(1)

        # Left: Elastic
        elastic_icon = make_icon(ICON_LIGHTNING, color=GREEN, height=0.5)
        elastic_title = make_label("Elastic", font_size=20, color=GREEN, weight=BOLD)
        elastic_bullets = VGroup(
            make_label("• Auto-detects load increase", font_size=13, color=GREY_A),
            make_label("• Adds resources automatically", font_size=13, color=GREY_A),
            make_label("• Great for unpredictable load", font_size=13, color=GREY_A),
        ).arrange(DOWN, buff=0.1, aligned_edge=LEFT)
        elastic_content = VGroup(elastic_icon, elastic_title, elastic_bullets).arrange(DOWN, buff=0.15)
        elastic_box = RoundedRectangle(
            corner_radius=0.15, width=4.5, height=3.0,
            fill_color=DARK_BG, fill_opacity=0.9, stroke_color=GREEN, stroke_width=1.5,
        )
        elastic_content.move_to(elastic_box.get_center())
        elastic_group = VGroup(elastic_box, elastic_content).move_to(LEFT * 3 + DOWN * 0.3)

        # Right: Manual
        manual_icon = make_icon(ICON_SETTINGS, color=BLUE, height=0.5)
        manual_title = make_label("Manual", font_size=20, color=BLUE, weight=BOLD)
        manual_bullets = VGroup(
            make_label("• Human analyzes capacity", font_size=13, color=GREY_A),
            make_label("• Decides when to add nodes", font_size=13, color=GREY_A),
            make_label("• Simpler, fewer surprises", font_size=13, color=GREY_A),
        ).arrange(DOWN, buff=0.1, aligned_edge=LEFT)
        manual_content = VGroup(manual_icon, manual_title, manual_bullets).arrange(DOWN, buff=0.15)
        manual_box = RoundedRectangle(
            corner_radius=0.15, width=4.5, height=3.0,
            fill_color=DARK_BG, fill_opacity=0.9, stroke_color=BLUE, stroke_width=1.5,
        )
        manual_content.move_to(manual_box.get_center())
        manual_group = VGroup(manual_box, manual_content).move_to(RIGHT * 3 + DOWN * 0.3)

        self.play(FadeIn(elastic_group, shift=RIGHT * 0.3))
        self.wait(2)
        self.play(FadeIn(manual_group, shift=LEFT * 0.3))
        self.wait(2)

        # Highlight key tradeoff
        tradeoff = make_label(
            "Stateless services → easy to distribute.  Stateful data → much harder.",
            font_size=16, color=YELLOW,
        )
        tradeoff.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(tradeoff, shift=UP * 0.2))
        self.wait(3)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 7: No Magic Scaling Sauce ──────────────────────────────
    def scene_no_magic_sauce(self):
        header = make_label("No Magic Scaling Sauce", font_size=30, color=RED)
        header.to_edge(UP, buff=0.5)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(1)

        quote = make_label(
            "There is no one-size-fits-all\nscalable architecture.",
            font_size=20, color=YELLOW,
        )
        quote.next_to(header, DOWN, buff=0.4)
        self.play(FadeIn(quote, shift=UP * 0.2))
        self.wait(2)

        # The famous example: same throughput, very different design
        # Left: 100K req/s × 1 kB
        left_label = make_label("System A", font_size=16, color=BLUE, weight=BOLD)
        left_stat1 = make_label("100,000 req/s", font_size=20, color=BLUE)
        left_stat2 = make_label("× 1 kB each", font_size=14, color=GREY_A)
        left_content = VGroup(left_label, left_stat1, left_stat2).arrange(DOWN, buff=0.1)
        left_box = RoundedRectangle(
            corner_radius=0.12, width=3.8, height=2.2,
            fill_color=DARK_BG, fill_opacity=0.9, stroke_color=BLUE, stroke_width=1.5,
        )
        left_content.move_to(left_box.get_center())
        left_card = VGroup(left_box, left_content).move_to(LEFT * 3 + DOWN * 0.5)

        # Right: 3 req/min × 2 GB
        right_label = make_label("System B", font_size=16, color=ORANGE, weight=BOLD)
        right_stat1 = make_label("3 req/min", font_size=20, color=ORANGE)
        right_stat2 = make_label("× 2 GB each", font_size=14, color=GREY_A)
        right_content = VGroup(right_label, right_stat1, right_stat2).arrange(DOWN, buff=0.1)
        right_box = RoundedRectangle(
            corner_radius=0.12, width=3.8, height=2.2,
            fill_color=DARK_BG, fill_opacity=0.9, stroke_color=ORANGE, stroke_width=1.5,
        )
        right_content.move_to(right_box.get_center())
        right_card = VGroup(right_box, right_content).move_to(RIGHT * 3 + DOWN * 0.5)

        self.play(FadeIn(left_card, shift=RIGHT * 0.3))
        self.wait(1.5)
        self.play(FadeIn(right_card, shift=LEFT * 0.3))
        self.wait(2)

        # Same throughput badge in center
        same_badge = make_label("≈ Same data throughput!", font_size=16, color=GREEN)
        same_badge.move_to(ORIGIN + DOWN * 0.5)
        self.play(FadeIn(same_badge, scale=1.3))
        self.wait(1)

        # But...
        diff_label = make_label(
            "Completely different architectures",
            font_size=16, color=RED,
        )
        diff_label.next_to(same_badge, DOWN, buff=0.3)
        self.play(FadeIn(diff_label, shift=UP * 0.2))
        self.wait(2)

        # Bottom takeaway
        takeaway = make_label(
            "Architecture depends on which operations are common vs rare",
            font_size=17, color=GREY_A,
        )
        takeaway.to_edge(DOWN, buff=0.4)
        self.play(FadeIn(takeaway, shift=UP * 0.2))
        self.wait(3)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 8: Closing ─────────────────────────────────────────────
    def scene_closing(self):
        title = make_label("Scalability", font_size=40, color=ORANGE)
        title.move_to(UP * 1.5)
        self.play(AddTextLetterByLetter(title, time_per_char=0.05))
        self.wait(1)

        # Three key concepts as mini recap
        concepts = [
            (ICON_MONITOR, BLUE, "Describe\nLoad"),
            (ICON_STOPWATCH, GREEN, "Measure\nPerformance"),
            (ICON_SERVER, ORANGE, "Cope with\nGrowth"),
        ]
        icons_row = VGroup()
        for path, color, label_text in concepts:
            ic = make_icon(path, color=color, height=0.5)
            lbl = make_label(label_text, font_size=12, color=color)
            g = VGroup(ic, lbl).arrange(DOWN, buff=0.1)
            icons_row.add(g)
        icons_row.arrange(RIGHT, buff=1.0).move_to(ORIGIN)

        self.play(
            AnimationGroup(
                *[FadeIn(ic, shift=UP * 0.2) for ic in icons_row],
                lag_ratio=0.15,
            )
        )
        self.wait(2)

        takeaway = make_label(
            "Scalable architectures are built from\n"
            "general-purpose building blocks in familiar patterns",
            font_size=18, color=GREY_A,
        )
        takeaway.move_to(DOWN * 1.5)
        self.play(FadeIn(takeaway, shift=UP * 0.2))
        self.wait(4)
        self.play(FadeOut(*self.mobjects))
