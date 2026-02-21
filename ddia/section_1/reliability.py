import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from manim import *

from libs.ddia_components import (
    DARK_BG,
    ICON_SHIELD, ICON_BUG, ICON_SIREN,
    ICON_USER, ICON_BOMB, ICON_LOCK, ICON_CODE,
    ICON_SERVER, ICON_DATABASE, ICON_CHECK, ICON_DANGER,
    make_label, make_icon, make_icon_card,
)

config.background_color = "#0D1117"


class Reliability(Scene):
    def construct(self):
        self.scene_title()
        self.scene_what_is_reliability()
        self.scene_fault_vs_failure()
        self.scene_hardware_faults()
        self.scene_software_errors()
        self.scene_human_errors()
        self.scene_why_it_matters()
        self.scene_closing()

    # ─── Scene 1: Title ───────────────────────────────────────────────
    def scene_title(self):
        icon = make_icon(ICON_SHIELD, color=GREEN, height=1.2)
        title = make_label("Reliability", font_size=44, color=GREEN)
        subtitle = make_label(
            "Designing Data-Intensive Applications — Ch. 1",
            font_size=20, color=GREY_B,
        )
        group = VGroup(icon, title, subtitle).arrange(DOWN, buff=0.4)

        self.play(FadeIn(icon, shift=DOWN * 0.3))
        self.play(AddTextLetterByLetter(title, time_per_char=0.05))
        self.play(FadeIn(subtitle, shift=UP * 0.2))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 2: What is Reliability? ────────────────────────────────
    def scene_what_is_reliability(self):
        header = make_label("What Does Reliability Mean?", font_size=30, color=GREEN)
        header.to_edge(UP, buff=0.5)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))

        # Definition
        definition = make_label(
            '"Continuing to work correctly,\n even when things go wrong."',
            font_size=22, color=YELLOW,
        )
        definition.next_to(header, DOWN, buff=0.6)
        self.play(FadeIn(definition, shift=UP * 0.2))
        self.wait(1)

        # Four expectations as cards
        expectations = [
            (ICON_CHECK, BLUE, "Correct Function",
             "Does what the user expects"),
            (ICON_USER, ORANGE, "Tolerates Mistakes",
             "Handles unexpected usage"),
            (ICON_SERVER, GREEN, "Good Performance",
             "Fast under expected load"),
            (ICON_LOCK, PURPLE, "Prevents Abuse",
             "No unauthorized access"),
        ]

        cards = VGroup()
        for icon_path, color, title, desc in expectations:
            icon = make_icon(icon_path, color=color, height=0.35)
            t = make_label(title, font_size=15, color=color, weight=BOLD)
            d = make_label(desc, font_size=11, color=GREY_A)
            content = VGroup(icon, t, d).arrange(DOWN, buff=0.1)

            box = RoundedRectangle(
                corner_radius=0.12, width=2.6, height=1.5,
                fill_color=DARK_BG, fill_opacity=0.9,
                stroke_color=color, stroke_width=1.5,
            )
            content.move_to(box.get_center())
            cards.add(VGroup(box, content))

        cards.arrange(RIGHT, buff=0.25).next_to(definition, DOWN, buff=0.5)

        self.play(
            AnimationGroup(
                *[FadeIn(c, shift=UP * 0.3) for c in cards],
                lag_ratio=0.15,
            )
        )
        self.wait(2)

        # Bottom highlight
        bottom = make_label(
            'If all of these hold → the system is "working correctly"',
            font_size=18, color=GREY_A,
        )
        bottom.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(bottom, shift=UP * 0.2))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 3: Fault vs Failure ────────────────────────────────────
    def scene_fault_vs_failure(self):
        header = make_label("Fault ≠ Failure", font_size=32, color=ORANGE)
        header.to_edge(UP, buff=0.5)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))

        # Left card: Fault
        fault_icon = make_icon(ICON_BUG, color=YELLOW, height=0.6)
        fault_title = make_label("Fault", font_size=22, color=YELLOW)
        fault_desc = VGroup(
            make_label("One component deviates", font_size=14, color=GREY_A),
            make_label("from its spec", font_size=14, color=GREY_A),
        ).arrange(DOWN, buff=0.08)
        fault_example = make_label("e.g. a disk dies", font_size=12, color=GREY_B)

        fault_content = VGroup(fault_icon, fault_title, fault_desc, fault_example).arrange(DOWN, buff=0.2)
        fault_box = RoundedRectangle(
            corner_radius=0.15, width=4.0, height=3.2,
            fill_color=DARK_BG, fill_opacity=0.9, stroke_color=YELLOW, stroke_width=1.5,
        )
        fault_content.move_to(fault_box.get_center())
        fault_group = VGroup(fault_box, fault_content).move_to(LEFT * 3 + DOWN * 0.3)

        # Right card: Failure
        fail_icon = make_icon(ICON_DANGER, color=RED, height=0.6)
        fail_title = make_label("Failure", font_size=22, color=RED)
        fail_desc = VGroup(
            make_label("The whole system stops", font_size=14, color=GREY_A),
            make_label("serving users", font_size=14, color=GREY_A),
        ).arrange(DOWN, buff=0.08)
        fail_example = make_label("e.g. website is down", font_size=12, color=GREY_B)

        fail_content = VGroup(fail_icon, fail_title, fail_desc, fail_example).arrange(DOWN, buff=0.2)
        fail_box = RoundedRectangle(
            corner_radius=0.15, width=4.0, height=3.2,
            fill_color=DARK_BG, fill_opacity=0.9, stroke_color=RED, stroke_width=1.5,
        )
        fail_content.move_to(fail_box.get_center())
        fail_group = VGroup(fail_box, fail_content).move_to(RIGHT * 3 + DOWN * 0.3)

        self.play(FadeIn(fault_group, shift=RIGHT * 0.3))
        self.wait(0.5)
        self.play(FadeIn(fail_group, shift=LEFT * 0.3))
        self.wait(1)

        # Arrow with cross: Fault -/-> Failure (we prevent this!)
        arrow = Arrow(
            fault_group.get_right(), fail_group.get_left(),
            buff=0.2, stroke_width=3, color=WHITE, tip_length=0.15,
        )
        cross = Text("✗", font_size=28, color=RED, weight=BOLD, stroke_width=0)
        cross.move_to(arrow.get_center() + UP * 0.3)
        prevent_label = make_label("Fault Tolerance", font_size=14, color=GREEN)
        prevent_label.next_to(arrow, DOWN, buff=0.15)

        self.play(GrowArrow(arrow), FadeIn(cross), FadeIn(prevent_label))
        self.wait(1)

        # Bottom insight
        insight = make_label(
            "Goal: design fault-tolerance so faults don't become failures",
            font_size=18, color=GREEN,
        )
        insight.to_edge(DOWN, buff=0.5)
        self.play(AddTextLetterByLetter(insight, time_per_char=0.03))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 4: Hardware Faults ─────────────────────────────────────
    def scene_hardware_faults(self):
        header = make_label("1. Hardware Faults", font_size=30, color=RED)
        header.to_edge(UP, buff=0.5)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))

        # Server rack visualization — 6 servers, one goes red
        servers = VGroup()
        for i in range(6):
            s = make_icon_card(
                f"Server {i + 1}", ICON_SERVER,
                color=BLUE if i != 3 else BLUE,
                width=1.6, height=1.1, font_size=10,
            )
            servers.add(s)
        servers.arrange_in_grid(rows=2, cols=3, buff=0.25).move_to(UP * 0.2)

        self.play(
            AnimationGroup(
                *[FadeIn(s, shift=UP * 0.2) for s in servers],
                lag_ratio=0.08,
            )
        )
        self.wait(1)

        # Highlight one server failing (disk crash)
        failing = servers[3]
        fail_flash = SurroundingRectangle(
            failing, color=RED, buff=0.08, corner_radius=0.1, stroke_width=3,
        )
        fail_label = make_label("Disk crash!", font_size=14, color=RED)
        fail_label.next_to(failing, DOWN, buff=0.2)

        self.play(Create(fail_flash), FadeIn(fail_label))
        self.play(
            failing[0].animate.set_stroke(RED, width=2.5),
            Flash(failing, color=RED, line_length=0.3, flash_radius=0.8),
        )
        self.wait(1)

        # Show redundancy solution
        solution_title = make_label("Solution: Add Redundancy", font_size=20, color=GREEN)
        solution_title.to_edge(DOWN, buff=1.2)
        self.play(FadeIn(solution_title, shift=UP * 0.2))

        solutions = VGroup(
            make_label("• RAID disks", font_size=14, color=GREY_A),
            make_label("• Dual power supplies", font_size=14, color=GREY_A),
            make_label("• Hot-swappable CPUs", font_size=14, color=GREY_A),
            make_label("• Multi-machine redundancy", font_size=14, color=GREY_A),
        ).arrange(DOWN, buff=0.1, aligned_edge=LEFT)
        solutions.next_to(solution_title, DOWN, buff=0.2)
        self.play(FadeIn(solutions, shift=UP * 0.1))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 5: Software Errors ─────────────────────────────────────
    def scene_software_errors(self):
        header = make_label("2. Software Errors", font_size=30, color=PURPLE)
        header.to_edge(UP, buff=0.5)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))

        # Key difference
        diff_label = make_label(
            "Systematic — can cause many nodes to fail at once",
            font_size=18, color=YELLOW,
        )
        diff_label.next_to(header, DOWN, buff=0.4)
        self.play(FadeIn(diff_label, shift=UP * 0.2))
        self.wait(1)

        # Examples as icon cards
        examples = [
            (ICON_BUG, RED, "Kernel Bug",
             "A bug crashes every\nserver with bad input"),
            (ICON_CODE, ORANGE, "Runaway Process",
             "Uses all shared resources\n(CPU, memory, disk)"),
            (ICON_BOMB, PURPLE, "Cascading Failure",
             "One slow service\ntriggers chain reaction"),
            (ICON_SIREN, BLUE, "Leap Second",
             "2012: Linux kernel bug\ncrashed many servers"),
        ]

        cards = VGroup()
        for icon_path, color, title, desc in examples:
            icon = make_icon(icon_path, color=color, height=0.35)
            t = make_label(title, font_size=14, color=color, weight=BOLD)
            d = make_label(desc, font_size=10, color=GREY_A)
            content = VGroup(icon, t, d).arrange(DOWN, buff=0.1)
            box = RoundedRectangle(
                corner_radius=0.12, width=2.7, height=2.0,
                fill_color=DARK_BG, fill_opacity=0.9,
                stroke_color=color, stroke_width=1.5,
            )
            content.move_to(box.get_center())
            cards.add(VGroup(box, content))

        cards.arrange(RIGHT, buff=0.2).move_to(DOWN * 0.5)

        self.play(
            AnimationGroup(
                *[FadeIn(c, shift=UP * 0.3) for c in cards],
                lag_ratio=0.15,
            )
        )
        self.wait(1)

        # Indicate each
        for c in cards:
            self.play(Indicate(c, color=YELLOW, scale_factor=1.05), run_time=0.4)

        # Bottom
        bottom = make_label(
            "No quick fix — requires careful thinking, testing, monitoring",
            font_size=17, color=GREEN,
        )
        bottom.to_edge(DOWN, buff=0.4)
        self.play(FadeIn(bottom, shift=UP * 0.2))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 6: Human Errors ────────────────────────────────────────
    def scene_human_errors(self):
        header = make_label("3. Human Errors", font_size=30, color=ORANGE)
        header.to_edge(UP, buff=0.5)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))

        # Quote
        quote = make_label(
            "Humans are known to be unreliable",
            font_size=20, color=YELLOW,
        )
        quote.next_to(header, DOWN, buff=0.4)
        self.play(FadeIn(quote, shift=UP * 0.2))
        self.wait(1)

        # Approaches to reduce human errors — stacked rows
        approaches = [
            (ICON_CODE, BLUE, "Good Abstractions",
             "Design APIs that make it hard to do the wrong thing"),
            (ICON_DATABASE, GREEN, "Sandbox Environments",
             "Let people explore safely without affecting production"),
            (ICON_CHECK, ORANGE, "Testing at All Levels",
             "Unit tests → integration tests → manual QA"),
            (ICON_SHIELD, PURPLE, "Quick Recovery",
             "Easy rollback, gradual rollouts, tools to recompute"),
            (ICON_SIREN, RED, "Monitoring & Alerts",
             "Performance metrics, error rates, early warning signals"),
        ]

        rows = VGroup()
        for icon_path, color, title, desc in approaches:
            icon = make_icon(icon_path, color=color, height=0.3)
            t = make_label(title, font_size=15, color=color, weight=BOLD)
            d = make_label(desc, font_size=11, color=GREY_A)
            row_content = VGroup(icon, t, d).arrange(RIGHT, buff=0.15)
            box = RoundedRectangle(
                corner_radius=0.1, width=10.5, height=0.55,
                fill_color=DARK_BG, fill_opacity=0.9,
                stroke_color=color, stroke_width=1.2,
            )
            row_content.move_to(box.get_center())
            rows.add(VGroup(box, row_content))

        rows.arrange(DOWN, buff=0.12).next_to(quote, DOWN, buff=0.4)

        for row in rows:
            self.play(FadeIn(row, shift=LEFT * 0.3), run_time=0.5)
            self.wait(0.2)

        self.wait(2)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 7: Why Reliability Matters ─────────────────────────────
    def scene_why_it_matters(self):
        header = make_label("How Important Is Reliability?", font_size=30, color=RED)
        header.to_edge(UP, buff=0.5)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))

        # "Not just for nuclear power stations"
        note = make_label(
            "Not just for nuclear power stations!",
            font_size=22, color=YELLOW,
        )
        note.next_to(header, DOWN, buff=0.5)
        self.play(FadeIn(note, shift=UP * 0.2))
        self.wait(1)

        # Impact examples
        impacts = [
            ("Business Apps", "Lost productivity, legal risks\nfrom incorrect figures", BLUE),
            ("E-commerce", "Outages → lost revenue\n& reputation damage", ORANGE),
            ("Personal Data", "A parent's photos lost?\nCorrupted database?", RED),
        ]

        cards = VGroup()
        for title, desc, color in impacts:
            t = make_label(title, font_size=18, color=color, weight=BOLD)
            d = make_label(desc, font_size=13, color=GREY_A)
            content = VGroup(t, d).arrange(DOWN, buff=0.15)
            box = RoundedRectangle(
                corner_radius=0.12, width=3.4, height=2.0,
                fill_color=DARK_BG, fill_opacity=0.9,
                stroke_color=color, stroke_width=1.5,
            )
            content.move_to(box.get_center())
            cards.add(VGroup(box, content))

        cards.arrange(RIGHT, buff=0.3).move_to(DOWN * 0.3)

        self.play(
            AnimationGroup(
                *[FadeIn(c, shift=UP * 0.3) for c in cards],
                lag_ratio=0.15,
            )
        )
        self.wait(1)

        for c in cards:
            self.play(Indicate(c, color=YELLOW, scale_factor=1.05), run_time=0.5)

        # Bottom caveat
        caveat = make_label(
            "Sometimes we trade reliability for cost — but always consciously",
            font_size=17, color=GREY_A,
        )
        caveat.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(caveat, shift=UP * 0.2))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 8: Closing ─────────────────────────────────────────────
    def scene_closing(self):
        title = make_label("Reliability", font_size=40, color=GREEN)
        title.move_to(UP * 1.5)
        self.play(AddTextLetterByLetter(title, time_per_char=0.05))

        # Three fault types as mini recap
        fault_types = [
            (ICON_SERVER, RED, "Hardware\nFaults"),
            (ICON_BUG, PURPLE, "Software\nErrors"),
            (ICON_USER, ORANGE, "Human\nErrors"),
        ]
        icons_row = VGroup()
        for path, color, label_text in fault_types:
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
        self.wait(1)

        # Takeaway
        takeaway = make_label(
            "Build fault-tolerant systems from unreliable parts",
            font_size=20, color=GREY_A,
        )
        takeaway.move_to(DOWN * 1.5)
        self.play(FadeIn(takeaway, shift=UP * 0.2))
        self.wait(3)
        self.play(FadeOut(*self.mobjects))
