import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from manim import *

from libs.ddia_components import (
    FONT, DARK_BG, CARD_BG, SQL_T2C,
    ICON_DATABASE, ICON_SERVER, ICON_SEARCH, ICON_STREAM,
    ICON_STOPWATCH, ICON_CPU_BOLT, ICON_CHECK, ICON_SCALE,
    ICON_TUNING, ICON_DANGER, ICON_HELP,
    make_label, make_card, make_icon, make_icon_card, make_code_text,
)

config.background_color = "#0D1117"


class DataIntensiveIntro(Scene):
    def construct(self):
        self.scene_title()
        self.scene_comparison()
        self.scene_data_challenges()
        self.scene_building_blocks()
        self.scene_architecture()
        self.scene_design_questions()
        self.scene_closing()

    # ─── Scene 1: Title ───────────────────────────────────────────────
    def scene_title(self):
        title = make_label("What is Data-Intensive?", font_size=42, color=BLUE)
        subtitle = make_label("Designing Data-Intensive Applications — Ch. 1", font_size=20, color=GREY_B)
        subtitle.next_to(title, DOWN, buff=0.4)

        icon = make_icon(ICON_DATABASE, color=BLUE, height=1.0)
        icon.next_to(title, UP, buff=0.5)

        self.play(FadeIn(icon, shift=DOWN * 0.3))
        self.wait(0.5)
        self.play(AddTextLetterByLetter(title, time_per_char=0.05))
        self.wait(0.5)
        self.play(FadeIn(subtitle, shift=UP * 0.2))
        self.wait(3)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 2: Data-Intensive vs Compute-Intensive ─────────────────
    def scene_comparison(self):
        header = make_label("Compute-Intensive vs Data-Intensive", font_size=30, color=ORANGE)
        header.to_edge(UP, buff=0.5)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(1)

        # ── Left: Compute-Intensive ──
        left_icon = make_icon(ICON_SERVER, color=GREY_A, height=0.6)
        left_title = make_label("Compute-Intensive", font_size=20, color=GREY_A)
        left_bullets = VGroup(
            make_label("• CPU-bound workloads", font_size=14, color=GREY_B),
            make_label("• HPC / simulations", font_size=14, color=GREY_B),
            make_label("• Raw processing power", font_size=14, color=GREY_B),
        ).arrange(DOWN, buff=0.12, aligned_edge=LEFT)

        left_content = VGroup(left_icon, left_title, left_bullets).arrange(DOWN, buff=0.2)
        left_box = RoundedRectangle(
            corner_radius=0.15, width=3.5, height=3.0,
            fill_color=DARK_BG, fill_opacity=0.9, stroke_color=GREY_B, stroke_width=1.5,
        )
        left_content.move_to(left_box.get_center())
        left_group = VGroup(left_box, left_content).move_to(LEFT * 3 + DOWN * 0.3)

        # ── Right: Data-Intensive ──
        right_icon = make_icon(ICON_DATABASE, color=BLUE, height=0.6)
        right_title = make_label("Data-Intensive", font_size=20, color=BLUE)
        right_bullets = VGroup(
            make_label("• Amount of data", font_size=14, color=BLUE_B),
            make_label("• Complexity of data", font_size=14, color=BLUE_B),
            make_label("• Speed of change", font_size=14, color=BLUE_B),
        ).arrange(DOWN, buff=0.12, aligned_edge=LEFT)

        right_content = VGroup(right_icon, right_title, right_bullets).arrange(DOWN, buff=0.2)
        right_box = RoundedRectangle(
            corner_radius=0.15, width=3.5, height=3.0,
            fill_color=DARK_BG, fill_opacity=0.9, stroke_color=BLUE, stroke_width=1.5,
        )
        right_content.move_to(right_box.get_center())
        right_group = VGroup(right_box, right_content).move_to(RIGHT * 3 + DOWN * 0.3)

        # Animate
        self.play(FadeIn(left_group, shift=RIGHT * 0.3))
        self.wait(1.5)
        self.play(FadeIn(right_group, shift=LEFT * 0.3))
        self.wait(2)

        # Emphasize data-intensive bullets one by one
        for bullet in right_bullets:
            self.play(Indicate(bullet, color=YELLOW, scale_factor=1.3))
            self.wait(0.5)

        # VS label
        vs_label = make_label("VS", font_size=28, color=ORANGE)
        vs_label.move_to(ORIGIN + DOWN * 0.3)
        self.play(FadeIn(vs_label, scale=1.5))
        self.wait(1)

        # Bottom highlight
        highlight = make_label("Most modern apps are data-intensive!", font_size=24, color=YELLOW)
        highlight.to_edge(DOWN, buff=0.6)
        self.play(AddTextLetterByLetter(highlight, time_per_char=0.03))
        self.wait(3)

        self.play(FadeOut(*self.mobjects))

    # ─── Scene 3: Data Challenges — visual diagrams ───────────────────
    def scene_data_challenges(self):
        header = make_label("Why Does This Matter?", font_size=30, color=YELLOW)
        header.to_edge(UP, buff=0.5)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(1)

        # ── Challenge 1: Too Many Requests ─────────────────────────────
        ch1_title = make_label("Too Many Requests", font_size=22, color=ORANGE)
        ch1_title.next_to(header, DOWN, buff=0.4)
        self.play(FadeIn(ch1_title, shift=UP * 0.2))
        self.wait(1)

        # Server on the right
        server = make_icon_card("Server", ICON_SERVER, color=BLUE, width=1.6, height=1.1, font_size=11)
        server.move_to(RIGHT * 2 + DOWN * 0.3)
        self.play(FadeIn(server, shift=UP * 0.2))
        self.wait(1)

        # Stats below the server (avoids arrow overlap)
        stats = VGroup(
            make_label("100K req/s", font_size=18, color=ORANGE),
            make_label("Peak hours = 10×", font_size=14, color=GREY_A),
        ).arrange(DOWN, buff=0.1)
        stats.next_to(server, DOWN, buff=0.4)
        self.play(FadeIn(stats, shift=UP * 0.2))
        self.wait(1)

        # User dots (static, on the left)
        user_positions = [
            LEFT * 5 + UP * 1.0,
            LEFT * 5 + UP * 0.2,
            LEFT * 5 + DOWN * 0.6,
            LEFT * 5 + DOWN * 1.4,
            LEFT * 4.0 + UP * 0.6,
            LEFT * 4.0 + DOWN * 0.2,
            LEFT * 4.0 + DOWN * 1.0,
        ]
        user_dots = VGroup(*[Dot(pos, radius=0.08, color=ORANGE) for pos in user_positions])
        self.play(FadeIn(user_dots))
        self.wait(0.5)

        # Loop: 3 waves of arrows hitting the server
        for wave in range(3):
            arrows = VGroup()
            for pos in user_positions:
                arr = Arrow(
                    pos, server.get_left(),
                    buff=0.15, stroke_width=1.5, color=ORANGE, tip_length=0.1,
                )
                arrows.add(arr)

            self.play(
                AnimationGroup(*[GrowArrow(a) for a in arrows], lag_ratio=0.04),
                run_time=0.6,
            )
            # Flash server on each hit
            self.play(
                Indicate(server, color=RED, scale_factor=1.08),
                run_time=0.4,
            )
            self.play(FadeOut(arrows), run_time=0.3)

        self.wait(2)

        # Transition out
        self.play(FadeOut(ch1_title, user_dots, server, stats))
        self.wait(1)

        # ── Challenge 2: Huge Responses ────────────────────────────────
        ch2_title = make_label("Huge Responses", font_size=22, color=GREEN)
        ch2_title.next_to(header, DOWN, buff=0.4)
        self.play(FadeIn(ch2_title, shift=UP * 0.2))
        self.wait(1)

        # Client on the left, Server on the right
        client_card = make_card("Client", width=1.8, height=1.1, fill_color=DARK_BG, label_color=WHITE, font_size=14)
        client_card.move_to(LEFT * 4 + DOWN * 0.5)
        server2 = make_icon_card("API Server", ICON_SERVER, color=BLUE, width=1.8, height=1.1, font_size=10)
        server2.move_to(RIGHT * 4 + DOWN * 0.5)

        self.play(FadeIn(client_card, shift=RIGHT * 0.2), FadeIn(server2, shift=LEFT * 0.2))
        self.wait(1)

        # Small request arrow (slightly above center)
        req_arrow = Arrow(
            client_card.get_right() + UP * 0.2, server2.get_left() + UP * 0.2,
            buff=0.15, stroke_width=2, color=GREY_A, tip_length=0.1,
        )
        req_label = make_label("GET /feed", font_size=11, color=GREY_A)
        req_label.next_to(req_arrow, UP, buff=0.08)
        self.play(GrowArrow(req_arrow), FadeIn(req_label))
        self.wait(1)

        # HUGE response arrow (slightly below center, thick)
        resp_arrow = Arrow(
            server2.get_left() + DOWN * 0.2, client_card.get_right() + DOWN * 0.2,
            buff=0.15, stroke_width=6, color=GREEN, tip_length=0.15,
        )
        resp_label = make_label("50 MB JSON", font_size=14, color=GREEN)
        resp_label.next_to(resp_arrow, DOWN, buff=0.08)

        # Growing rectangles to represent payload size
        payload_bars = VGroup()
        for i in range(8):
            bar = Rectangle(
                width=0.15, height=0.3 + i * 0.08,
                fill_color=GREEN, fill_opacity=0.6,
                stroke_width=0,
            )
            payload_bars.add(bar)
        payload_bars.arrange(RIGHT, buff=0.04).move_to(DOWN * 2.0)

        self.play(
            GrowArrow(resp_arrow), FadeIn(resp_label),
            AnimationGroup(*[GrowFromEdge(b, DOWN) for b in payload_bars], lag_ratio=0.08),
        )
        self.wait(3)

        self.play(FadeOut(ch2_title, client_card, server2, req_arrow, req_label,
                          resp_arrow, resp_label, payload_bars))
        self.wait(1)

        # ── Challenge 3: Huge Database ─────────────────────────────────
        ch3_title = make_label("Huge Database", font_size=22, color=PURPLE)
        ch3_title.next_to(header, DOWN, buff=0.4)
        self.play(FadeIn(ch3_title, shift=UP * 0.2))
        self.wait(1)

        # Stack of database layers growing
        db_layers = VGroup()
        layer_data = [
            ("Users", "2 TB", BLUE),
            ("Posts", "15 TB", ORANGE),
            ("Messages", "40 TB", GREEN),
            ("Media", "200 TB", PURPLE),
            ("Logs", "500 TB", RED),
        ]
        for name, size, color in layer_data:
            lbl = make_label(f"{name}  {size}", font_size=13, color=color)
            box = RoundedRectangle(
                corner_radius=0.08, width=4.0, height=0.5,
                fill_color=DARK_BG, fill_opacity=0.9,
                stroke_color=color, stroke_width=1.5,
            )
            lbl.move_to(box.get_center())
            db_layers.add(VGroup(box, lbl))

        db_layers.arrange(DOWN, buff=0.08).move_to(LEFT * 2.5 + DOWN * 0.5)

        # Animate layers stacking one by one
        for i, layer in enumerate(db_layers):
            self.play(FadeIn(layer, shift=UP * 0.2), run_time=0.4)
            self.wait(0.3)

        self.wait(1)

        # Total size callout
        total = make_label("Total: 757 TB", font_size=20, color=YELLOW)

        # Growth arrow on the right side
        growth_arrow = Arrow(
            RIGHT * 2 + DOWN * 2.2, RIGHT * 2 + UP * 1.5,
            buff=0, stroke_width=3, color=YELLOW, tip_length=0.15,
        )
        growth_label = make_label("Growing\nevery day", font_size=12, color=GREY_A)

        total.next_to(growth_arrow, LEFT, buff=0.8)
        growth_label.next_to(growth_arrow, RIGHT, buff=0.15)

        self.play(FadeIn(total, shift=LEFT * 0.2), GrowArrow(growth_arrow), FadeIn(growth_label))
        self.wait(3)

        # Bottom takeaway
        takeaway = make_label(
            "These challenges define data-intensive applications",
            font_size=18, color=YELLOW,
        )
        takeaway.to_edge(DOWN, buff=0.4)
        self.play(FadeIn(takeaway, shift=UP * 0.2))
        self.wait(3)

        self.play(FadeOut(*self.mobjects))

    # ─── Scene 4: The 5 Building Blocks ──────────────────────────────
    def scene_building_blocks(self):
        header = make_label("5 Standard Building Blocks", font_size=30, color=GREEN)
        header.to_edge(UP, buff=0.5)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(1)

        blocks = [
            ("Databases", ICON_DATABASE, BLUE),
            ("Caches", ICON_STOPWATCH, ORANGE),
            ("Search\nIndexes", ICON_SEARCH, GREEN),
            ("Stream\nProcessing", ICON_STREAM, PURPLE),
            ("Batch\nProcessing", ICON_CPU_BOLT, RED),
        ]

        descriptions = [
            "Store & retrieve",
            "Speed up reads",
            "Keyword search",
            "Async messaging",
            "Crunch data",
        ]

        cards = VGroup()
        for name, icon_path, color in blocks:
            card = make_icon_card(name, icon_path, color=color, width=2.0, height=1.6, font_size=13)
            cards.add(card)

        cards.arrange(RIGHT, buff=0.3).move_to(ORIGIN + UP * 0.2)

        # Scale down if too wide
        if cards.get_width() > 12:
            cards.scale_to_fit_width(12)

        # Stagger fade in
        self.play(
            AnimationGroup(
                *[FadeIn(card, shift=UP * 0.3) for card in cards],
                lag_ratio=0.15,
            )
        )
        self.wait(2)

        # Add descriptions below each card
        desc_labels = VGroup()
        for i, desc in enumerate(descriptions):
            d = make_label(desc, font_size=12, color=GREY_A)
            d.next_to(cards[i], DOWN, buff=0.15)
            desc_labels.add(d)

        self.play(
            AnimationGroup(
                *[FadeIn(d, shift=UP * 0.1) for d in desc_labels],
                lag_ratio=0.1,
            )
        )
        self.wait(3)

        # Highlight text
        bottom_text = make_label(
            "Applications compose these blocks to serve different needs",
            font_size=18, color=YELLOW,
        )
        bottom_text.to_edge(DOWN, buff=0.5)
        self.play(AddTextLetterByLetter(bottom_text, time_per_char=0.03))
        self.wait(3)

        self.play(FadeOut(*self.mobjects))

    # ─── Scene 5: Architecture Diagram ────────────────────────────────
    def scene_architecture(self):
        header = make_label("How They Fit Together", font_size=30, color=PURPLE)
        header.to_edge(UP, buff=0.5)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(1)

        # Client
        client_card = make_card("Client", width=1.8, height=0.7, fill_color=DARK_BG, label_color=WHITE, font_size=16)
        client_card.move_to(LEFT * 5.8)

        # Application box (central)
        app_rect = RoundedRectangle(
            corner_radius=0.2, width=2.5, height=1.2,
            fill_color="#1C2128", fill_opacity=0.9, stroke_color=PURPLE, stroke_width=2,
        )
        app_label = make_label("Application", font_size=18, color=PURPLE)
        app_label.move_to(app_rect.get_center())
        app_box = VGroup(app_rect, app_label).move_to(LEFT * 2.5)

        self.play(FadeIn(client_card, shift=RIGHT * 0.3))
        self.wait(0.5)
        self.play(FadeIn(app_box, shift=RIGHT * 0.3))
        self.wait(0.5)

        # Arrow: Client → Application
        client_arrow = Arrow(
            client_card.get_right(), app_box.get_left(),
            buff=0.15, stroke_width=3, color=WHITE, tip_length=0.15,
        )
        client_label = make_label("API", font_size=12, color=GREY_A)
        client_label.next_to(client_arrow, UP, buff=0.08)
        self.play(GrowArrow(client_arrow), FadeIn(client_label))
        self.wait(1)

        # Building block mini-cards — scattered in a vertical fan on the right
        block_data = [
            ("Database", ICON_DATABASE, BLUE),
            ("Cache", ICON_STOPWATCH, ORANGE),
            ("Search Index", ICON_SEARCH, GREEN),
            ("Stream Proc.", ICON_STREAM, PURPLE_B),
            ("Batch Proc.", ICON_CPU_BOLT, RED),
        ]

        arrow_labels = ["write", "read", "query", "publish", "schedule"]

        # Position each card at a distinct Y level with staggered X to avoid overlap
        positions = [
            RIGHT * 3.0 + UP * 2.2,  # Database — top
            RIGHT * 5.0 + UP * 1.1,  # Cache
            RIGHT * 3.0 + ORIGIN,  # Search Index — center
            RIGHT * 5.0 + DOWN * 1.1,  # Stream Proc.
            RIGHT * 3.0 + DOWN * 2.2,  # Batch Proc. — bottom
        ]

        mini_cards = VGroup()
        for i, (name, icon_path, color) in enumerate(block_data):
            mc = make_icon_card(name, icon_path, color=color, width=1.8, height=1.1, font_size=11)
            mc.move_to(positions[i])
            mini_cards.add(mc)

        self.play(
            AnimationGroup(
                *[FadeIn(mc, shift=LEFT * 0.3) for mc in mini_cards],
                lag_ratio=0.1,
            )
        )
        self.wait(1.5)

        # Arrows from application to each block
        arrows = VGroup()
        labels = VGroup()
        for i, mc in enumerate(mini_cards):
            arrow = Arrow(
                app_box.get_right(), mc.get_left(),
                buff=0.1, stroke_width=2, color=block_data[i][2], tip_length=0.12,
            )
            lbl = make_label(arrow_labels[i], font_size=10, color=GREY_A)
            lbl.next_to(arrow.get_center(), UP, buff=0.05)
            arrows.add(arrow)
            labels.add(lbl)

        self.play(
            AnimationGroup(
                *[GrowArrow(a) for a in arrows],
                lag_ratio=0.12,
            )
        )
        self.wait(0.5)
        self.play(
            AnimationGroup(
                *[FadeIn(l) for l in labels],
                lag_ratio=0.08,
            )
        )
        self.wait(2)

        # Combined result arrow back
        result_start = mini_cards[-1].get_left() + DOWN * 0.3
        result_end = app_box.get_right() + DOWN * 0.4
        result_arrow = Arrow(
            result_start, result_end,
            buff=0.1, stroke_width=2, color=GREEN, tip_length=0.12,
            path_arc=-0.3,
        )
        result_label = make_label("combined result", font_size=11, color=GREEN)
        result_label.next_to(result_arrow, DOWN, buff=0.08)
        self.play(GrowArrow(result_arrow), FadeIn(result_label))
        self.wait(2)

        # Bottom callout
        callout = make_label("One app — many data systems under the hood", font_size=20, color=YELLOW)
        callout.to_edge(DOWN, buff=0.5)
        self.play(AddTextLetterByLetter(callout, time_per_char=0.03))
        self.wait(3)

        self.play(FadeOut(*self.mobjects))

    # ─── Scene 6: Tricky Design Questions ─────────────────────────────
    def scene_design_questions(self):
        header = make_label("The Hard Questions", font_size=32, color=RED)
        header.to_edge(UP, buff=0.5)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(1)

        questions = [
            (ICON_CHECK, BLUE, "Reliability",
             "How to keep data correct when things fail?"),
            (ICON_SCALE, ORANGE, "Scalability",
             "How to handle growth in load?"),
            (ICON_STOPWATCH, GREEN, "Performance",
             "How to stay fast under degradation?"),
            (ICON_TUNING, PURPLE, "Maintainability",
             "What does a good API look like?"),
        ]

        q_groups = VGroup()
        for icon_path, color, title, desc in questions:
            icon = make_icon(icon_path, color=color, height=0.4)
            title_label = make_label(title, font_size=18, color=color, weight=BOLD)
            desc_label = make_label(desc, font_size=14, color=GREY_A)

            row_content = VGroup(icon, title_label, desc_label).arrange(RIGHT, buff=0.2)
            row_box = RoundedRectangle(
                corner_radius=0.12, width=10, height=0.7,
                fill_color=DARK_BG, fill_opacity=0.9, stroke_color=color, stroke_width=1.5,
            )
            row_content.move_to(row_box.get_center())
            q_groups.add(VGroup(row_box, row_content))

        q_groups.arrange(DOWN, buff=0.2).move_to(ORIGIN + DOWN * 0.2)

        # Stagger fade in
        for qg in q_groups:
            self.play(FadeIn(qg, shift=LEFT * 0.3), run_time=0.6)
            self.wait(0.5)

        self.wait(2)

        # Indicate each row
        for qg in q_groups:
            self.play(Indicate(qg, color=YELLOW, scale_factor=1.05), run_time=0.5)
            self.wait(0.5)

        self.wait(1)

        # Bottom text
        bottom = make_label("These are the core themes of this book.", font_size=20, color=GREY_A)
        bottom.to_edge(DOWN, buff=0.5)
        self.play(AddTextLetterByLetter(bottom, time_per_char=0.03))
        self.wait(3)

        self.play(FadeOut(*self.mobjects))

    # ─── Scene 7: Closing ─────────────────────────────────────────────
    def scene_closing(self):
        title = make_label("Data-Intensive Applications", font_size=36, color=BLUE)
        title.move_to(UP * 1.0)
        self.play(AddTextLetterByLetter(title, time_per_char=0.05))
        self.wait(1)

        # Mini icons row as visual recap
        icon_data = [
            (ICON_DATABASE, BLUE),
            (ICON_STOPWATCH, ORANGE),
            (ICON_SEARCH, GREEN),
            (ICON_STREAM, PURPLE),
            (ICON_CPU_BOLT, RED),
        ]
        icons_row = VGroup()
        for path, color in icon_data:
            ic = make_icon(path, color=color, height=0.5)
            icons_row.add(ic)
        icons_row.arrange(RIGHT, buff=0.5).move_to(ORIGIN)

        self.play(
            AnimationGroup(
                *[FadeIn(ic, shift=UP * 0.2) for ic in icons_row],
                lag_ratio=0.1,
            )
        )
        self.wait(2)

        themes = make_label(
            "Reliability · Scalability · Performance · Maintainability",
            font_size=20, color=GREY_A,
        )
        themes.move_to(DOWN * 1.2)
        self.play(FadeIn(themes, shift=UP * 0.2))
        self.wait(4)

        self.play(FadeOut(*self.mobjects))
