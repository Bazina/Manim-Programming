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
    AddTextLetterByLetter,
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
    ICON_DANGER,
    ICON_LIGHTNING,
    ICON_CODE,
    ICON_GRAPH,
    ICON_LOCK,
    ICON_SHIELD,
    make_label,
    make_icon,
)

config.background_color = "#0D1117"

ICON_STREAMING = "assets/icons/devices/LightningBold.svg"


class Sheet5Streaming(Scene):

    def construct(self):
        self.scene_title()
        self.scene_q1_overview()
        self.scene_q1_drop()
        self.scene_q1_buffer()
        self.scene_q1_backpressure()
        self.scene_q2_overview()
        self.scene_q2_merge_sweep()
        self.scene_q2_global_sequence()
        self.scene_q3_tools()
        self.scene_closing()

    # ─── Helpers ──────────────────────────────────────────────────────

    def _card(self, title, desc, color, width=11.5, height=None, title_size=13, desc_size=11):
        t = make_label(title, font_size=title_size, color=color)
        d = make_label(desc, font_size=desc_size, color=GREY_A)
        content = VGroup(t, d).arrange(DOWN, buff=0.1, aligned_edge=LEFT)
        h = height or content.height + 0.38
        box = RoundedRectangle(
            corner_radius=0.09,
            width=width, height=h,
            fill_color=DARK_BG, fill_opacity=0.9,
            stroke_color=color, stroke_width=1.3,
        )
        content.move_to(box.get_center())
        return VGroup(box, content)

    def _icon_row_card(self, icon_path, color, title, desc, row_w=11.5):
        ic = make_icon(icon_path, color=color, height=0.28)
        t = make_label(title, font_size=13, color=color)
        d = make_label(desc, font_size=11, color=GREY_A)
        content = VGroup(ic, t, d).arrange(RIGHT, buff=0.18)
        box = RoundedRectangle(
            corner_radius=0.09,
            width=row_w, height=content.height + 0.3,
            fill_color=DARK_BG, fill_opacity=0.9,
            stroke_color=color, stroke_width=1.1,
        )
        content.move_to(box.get_center())
        return VGroup(box, content)

    def _flow_node(self, label, color, width=2.0, height=0.9):
        box = RoundedRectangle(
            corner_radius=0.1, width=width, height=height,
            fill_color=DARK_BG, fill_opacity=0.9,
            stroke_color=color, stroke_width=1.5,
        )
        lbl = make_label(label, font_size=10, color=color)
        lbl.move_to(box.get_center())
        return VGroup(box, lbl)

    def _flow_arrow(self, left_node, right_node, color=GREY_A, label=None):
        a = Arrow(
            left_node.get_right(), right_node.get_left(),
            buff=0.1, stroke_width=2.0, color=color, tip_length=0.15,
        )
        if label:
            lbl = make_label(label, font_size=9, color=color)
            lbl.next_to(a, UP, buff=0.07)
            return VGroup(a, lbl)
        return a

    def _verdict(self, text, color, width=9.5):
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
        icon = make_icon(ICON_LIGHTNING, color=TEAL, height=1.1)
        title = make_label("Sheet 5: Streaming", font_size=36, color=TEAL)
        sub = make_label(
            "Overload Strategies  ·  Topic-Level Ordering  ·  Streaming Tools",
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

    # ─── Scene 2: Q1 Overview ─────────────────────────────────────────
    def scene_q1_overview(self):
        header = make_label(
            "Q1: Producer Faster Than Consumer — 3 Strategies",
            font_size=24, color=ORANGE,
        )
        header.to_edge(UP, buff=0.4)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.4)

        # Producer → [overload] → Consumer flow
        prod = self._flow_node("Producer\n(fast)", ORANGE, width=2.2)
        queue = self._flow_node("???", RED, width=1.6, height=0.9)
        cons = self._flow_node("Consumer\n(slow)", BLUE, width=2.2)

        flow = VGroup(prod, queue, cons).arrange(RIGHT, buff=1.2).move_to(UP * 0.9)
        a1 = self._flow_arrow(prod, queue, ORANGE)
        a2 = self._flow_arrow(queue, cons, BLUE)

        self.play(AnimationGroup(*[FadeIn(n, shift=DOWN * 0.1) for n in [prod, queue, cons]], lag_ratio=0.2))
        self.play(GrowArrow(a1[0] if isinstance(a1, VGroup) else a1),
                  GrowArrow(a2[0] if isinstance(a2, VGroup) else a2))
        self.wait(0.4)

        overload_lbl = make_label("overload!", font_size=11, color=RED)
        overload_lbl.next_to(queue, UP, buff=0.15)
        self.play(FadeIn(overload_lbl))
        self.play(Indicate(queue, color=RED, run_time=1.2))
        self.wait(0.5)

        strategies = [
            (RED,    "Drop Messages",      "Discard excess — simplest, no memory cost"),
            (BLUE,   "Buffer Messages",    "Queue excess — absorbs bursts, risk of overflow"),
            (GREEN,  "Backpressure",       "Throttle producer — zero data loss, requires protocol support"),
        ]
        rows = VGroup()
        for color, title, desc in strategies:
            rows.add(self._icon_row_card(ICON_LIGHTNING, color, title, desc))
        rows.arrange(DOWN, buff=0.1).next_to(flow, DOWN, buff=0.55)

        for row in rows:
            self.play(FadeIn(row, shift=LEFT * 0.3), run_time=0.45)
            self.wait(0.35)

        self.wait(2.5)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 3: Drop Messages ───────────────────────────────────────
    def scene_q1_drop(self):
        header = make_label("Q1A: Drop Messages", font_size=28, color=RED)
        header.to_edge(UP, buff=0.4)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.4)

        when_lbl = make_label("Use when dropped messages are acceptable:", font_size=14, color=GREY_A)
        when_lbl.next_to(header, DOWN, buff=0.35)
        self.play(FadeIn(when_lbl, shift=UP * 0.1))
        self.wait(0.3)

        cases = [
            (ICON_CODE,      TEAL,   "Client can retry",
             "Producer resends on next cycle — no permanent loss"),
            (ICON_GRAPH,     BLUE,   "Logging / monitoring",
             "Missing a few log lines or metrics is tolerable"),
            (ICON_LIGHTNING, ORANGE, "Heartbeat messages",
             "Purpose is 'I'm alive' — stale heartbeats carry no value"),
        ]
        rows = VGroup()
        for icon_path, color, title, desc in cases:
            rows.add(self._icon_row_card(icon_path, color, title, desc))
        rows.arrange(DOWN, buff=0.1).next_to(when_lbl, DOWN, buff=0.3)

        for row in rows:
            self.play(FadeIn(row, shift=LEFT * 0.3), run_time=0.45)
            self.wait(0.4)

        tradeoff = VGroup(
            make_label("✓  Zero memory overhead — simplest implementation", font_size=12, color=GREEN),
            make_label("✗  Permanent data loss — only safe when message value is low", font_size=12, color=RED),
        ).arrange(DOWN, buff=0.12, aligned_edge=LEFT)
        tradeoff.to_edge(DOWN, buff=0.45)
        self.play(FadeIn(tradeoff, shift=UP * 0.1))
        self.wait(3.5)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 4: Buffer Messages ─────────────────────────────────────
    def scene_q1_buffer(self):
        header = make_label("Q1B: Buffer / Queue Messages", font_size=28, color=BLUE)
        header.to_edge(UP, buff=0.4)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.4)

        when_lbl = make_label("Use when the client cannot retry:", font_size=14, color=GREY_A)
        when_lbl.next_to(header, DOWN, buff=0.35)
        self.play(FadeIn(when_lbl, shift=UP * 0.1))
        self.wait(0.3)

        cases = [
            (ICON_DANGER,    RED,    "Client under high pressure",
             "Cannot afford to hold messages in memory and resend — fire-and-forget"),
            (ICON_SERVER,    ORANGE, "IoT sensor readings",
             "Embedded device may not have memory or CPU for a resend queue"),
            (ICON_DATABASE,  BLUE,   "One-shot event producers",
             "Lambda / serverless function — exits after emit, cannot retry"),
        ]
        rows = VGroup()
        for icon_path, color, title, desc in cases:
            rows.add(self._icon_row_card(icon_path, color, title, desc))
        rows.arrange(DOWN, buff=0.1).next_to(when_lbl, DOWN, buff=0.3)

        for row in rows:
            self.play(FadeIn(row, shift=LEFT * 0.3), run_time=0.45)
            self.wait(0.4)

        # Buffer overflow warning
        overflow = make_label(
            "⚠  Buffer overflow risk — must define eviction: drop oldest, drop newest, or block",
            font_size=12, color=YELLOW,
        )
        overflow.to_edge(DOWN, buff=0.6)
        tradeoff = VGroup(
            make_label("✓  Absorbs bursts — producer is unaffected while buffer has space", font_size=12, color=GREEN),
            make_label("✗  If consumer is permanently slower, buffer eventually overflows", font_size=12, color=RED),
        ).arrange(DOWN, buff=0.1, aligned_edge=LEFT)
        tradeoff.to_edge(DOWN, buff=0.25)

        self.play(FadeIn(overflow, shift=UP * 0.1))
        self.play(FadeIn(tradeoff, shift=UP * 0.1))
        self.wait(3.5)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 5: Backpressure ────────────────────────────────────────
    def scene_q1_backpressure(self):
        header = make_label("Q1C: Backpressure", font_size=28, color=GREEN)
        header.to_edge(UP, buff=0.4)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.4)

        when_lbl = make_label("Use when NO message can be dropped:", font_size=14, color=GREY_A)
        when_lbl.next_to(header, DOWN, buff=0.35)
        self.play(FadeIn(when_lbl, shift=UP * 0.1))
        self.wait(0.3)

        cases = [
            (ICON_LOCK,  YELLOW, "Transactional systems (ATM)",
             "Every event is a financial operation — loss is unacceptable"),
            (ICON_SHIELD, PURPLE, "Payment / trading pipelines",
             "Missing a trade or payment event causes data integrity failure"),
        ]
        rows = VGroup()
        for icon_path, color, title, desc in cases:
            rows.add(self._icon_row_card(icon_path, color, title, desc, row_w=11.0))
        rows.arrange(DOWN, buff=0.1).next_to(when_lbl, DOWN, buff=0.3)

        for row in rows:
            self.play(FadeIn(row, shift=LEFT * 0.3), run_time=0.45)
            self.wait(0.4)

        # Flow diagram: consumer throttles producer
        prod_bp = self._flow_node("Producer", GREEN, width=2.0)
        cons_bp = self._flow_node("Consumer", GREEN, width=2.0)
        bp_row = VGroup(prod_bp, cons_bp).arrange(RIGHT, buff=3.5).move_to(DOWN * 0.5)

        fwd_arrow = Arrow(
            prod_bp.get_right(), cons_bp.get_left(),
            buff=0.1, stroke_width=2.0, color=GREEN, tip_length=0.15,
        )
        fwd_lbl = make_label("messages", font_size=9, color=GREEN)
        fwd_lbl.next_to(fwd_arrow, UP, buff=0.08)

        back_arrow = Arrow(
            cons_bp.get_left(), prod_bp.get_right(),
            buff=0.1, stroke_width=2.0, color=ORANGE, tip_length=0.15,
        )
        back_lbl = make_label("SLOW DOWN signal", font_size=9, color=ORANGE)
        back_lbl.next_to(back_arrow, DOWN, buff=0.08)

        self.play(AnimationGroup(FadeIn(prod_bp), FadeIn(cons_bp), lag_ratio=0.2))
        self.play(GrowArrow(fwd_arrow), FadeIn(fwd_lbl))
        self.play(GrowArrow(back_arrow), FadeIn(back_lbl))
        self.wait(0.5)

        tradeoff = VGroup(
            make_label("✓  Zero data loss — strongest guarantee", font_size=12, color=GREEN),
            make_label("✗  Producer must support throttle  |  latency increases under load", font_size=12, color=RED),
        ).arrange(DOWN, buff=0.1, aligned_edge=LEFT)
        tradeoff.to_edge(DOWN, buff=0.35)
        self.play(FadeIn(tradeoff, shift=UP * 0.1))
        self.wait(3.5)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 6: Q2 Overview ─────────────────────────────────────────
    def scene_q2_overview(self):
        header = make_label("Q2: Topic-Level Ordering Guarantee", font_size=26, color=TEAL)
        header.to_edge(UP, buff=0.4)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.4)

        context = make_label(
            "Kafka today: ordering guaranteed per partition — NOT across partitions in same topic",
            font_size=13, color=GREY_A,
        )
        context.next_to(header, DOWN, buff=0.3)
        question = make_label(
            "Goal: impose ordering across ALL partitions of a topic",
            font_size=13, color=YELLOW,
        )
        question.next_to(context, DOWN, buff=0.1)
        self.play(FadeIn(context, shift=UP * 0.1))
        self.play(FadeIn(question, shift=UP * 0.1))
        self.wait(0.6)

        # Show current state: 3 partitions, unordered across them
        P1 = self._flow_node("Partition 1\n[1, 4, 7]", BLUE, width=2.4)
        P2 = self._flow_node("Partition 2\n[2, 5, 8]", ORANGE, width=2.4)
        P3 = self._flow_node("Partition 3\n[3, 6, 9]", PURPLE, width=2.4)
        parts = VGroup(P1, P2, P3).arrange(RIGHT, buff=0.6).move_to(DOWN * 0.2)

        topic_lbl = make_label("Topic", font_size=11, color=GREY_B)
        topic_lbl.next_to(parts, UP, buff=0.2)

        cross_note = make_label(
            "Reading across partitions gives: 1,4,7,2,5,8,3,6,9 — NOT ordered",
            font_size=12, color=RED,
        )
        cross_note.next_to(parts, DOWN, buff=0.3)

        self.play(FadeIn(topic_lbl))
        for p in parts:
            self.play(FadeIn(p, shift=UP * 0.15), run_time=0.4)
        self.play(FadeIn(cross_note, shift=UP * 0.1))
        self.play(Indicate(cross_note, color=RED, run_time=1.2))
        self.wait(0.5)

        approach_lbl = make_label(
            "Two approaches to fix this →",
            font_size=14, color=GREEN,
        )
        approach_lbl.to_edge(DOWN, buff=0.4)
        self.play(FadeIn(approach_lbl, shift=UP * 0.15))
        self.wait(3)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 7: Approach 1 — Merge Sweep ───────────────────────────
    def scene_q2_merge_sweep(self):
        header = make_label("Q2 — Approach 1: Merge Sweep", font_size=26, color=BLUE)
        header.to_edge(UP, buff=0.4)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.4)

        idea = make_label(
            "Each producer writes to its own temporary partition → periodic merge into one main ordered partition",
            font_size=12, color=GREY_A,
        )
        idea.next_to(header, DOWN, buff=0.28)
        self.play(FadeIn(idea, shift=UP * 0.1))
        self.wait(0.4)

        # Flow diagram: temp partitions → merge → main
        tA = self._flow_node("Temp A\n(producer A)", TEAL, width=2.1, height=0.85)
        tB = self._flow_node("Temp B\n(producer B)", TEAL, width=2.1, height=0.85)
        tC = self._flow_node("Temp C\n(producer C)", TEAL, width=2.1, height=0.85)
        temps = VGroup(tA, tB, tC).arrange(DOWN, buff=0.2)

        merge_box = self._flow_node("Merge Sweep\n(by timestamp)", ORANGE, width=2.4, height=1.1)
        main_part = self._flow_node("Main Partition\n(ordered)", BLUE, width=2.4, height=1.1)

        diagram = VGroup(temps, merge_box, main_part).arrange(RIGHT, buff=1.2).move_to(DOWN * 0.1)

        aA = Arrow(tA.get_right(), merge_box.get_left(), buff=0.1, stroke_width=1.5, color=TEAL, tip_length=0.12)
        aB = Arrow(tB.get_right(), merge_box.get_left(), buff=0.1, stroke_width=1.5, color=TEAL, tip_length=0.12)
        aC = Arrow(tC.get_right(), merge_box.get_left(), buff=0.1, stroke_width=1.5, color=TEAL, tip_length=0.12)
        aM = Arrow(merge_box.get_right(), main_part.get_left(), buff=0.1, stroke_width=2.0, color=BLUE, tip_length=0.15)

        self.play(
            AnimationGroup(FadeIn(temps), FadeIn(merge_box), FadeIn(main_part), lag_ratio=0.2)
        )
        self.play(GrowArrow(aA), GrowArrow(aB), GrowArrow(aC))
        self.play(GrowArrow(aM))
        self.wait(0.6)

        pros_title = make_label("Advantages", font_size=13, color=GREEN)
        pros = VGroup(
            make_label("✓  No connection switching between partition machines during writes", font_size=11, color=GREEN),
            make_label("✓  No inner-partition data shuffling to satisfy ordering", font_size=11, color=GREEN),
            make_label("✓  Reads from main partition are inherently ordered", font_size=11, color=GREEN),
        ).arrange(DOWN, buff=0.08, aligned_edge=LEFT)
        pros_group = VGroup(pros_title, pros).arrange(DOWN, buff=0.08, aligned_edge=LEFT)

        cons_title = make_label("Disadvantages", font_size=13, color=RED)
        cons = VGroup(
            make_label("✗  Single point of failure — all data funnels into one main partition", font_size=11, color=RED),
            make_label("✗  Merge latency — ordering is eventual, not real-time", font_size=11, color=ORANGE),
        ).arrange(DOWN, buff=0.08, aligned_edge=LEFT)
        cons_group = VGroup(cons_title, cons).arrange(DOWN, buff=0.08, aligned_edge=LEFT)

        VGroup(pros_group, cons_group).arrange(DOWN, buff=0.18, aligned_edge=LEFT).to_edge(DOWN, buff=0.3)

        self.play(FadeIn(pros_group, shift=UP * 0.1))
        self.wait(0.4)
        self.play(FadeIn(cons_group, shift=UP * 0.1))
        self.play(Indicate(cons[0], color=RED, run_time=1.2))
        self.wait(3.5)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 8: Approach 2 — Global Sequence ────────────────────────
    def scene_q2_global_sequence(self):
        header = make_label("Q2 — Approach 2: Global Sequence Number", font_size=25, color=ORANGE)
        header.to_edge(UP, buff=0.4)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.4)

        idea = make_label(
            "Write to any partition as before — each message gets a global monotonic sequence number",
            font_size=12, color=GREY_A,
        )
        idea.next_to(header, DOWN, buff=0.28)
        self.play(FadeIn(idea, shift=UP * 0.1))
        self.wait(0.4)

        # Diagram: producers → partitions (with seq#) → consumer sorts
        p1 = self._flow_node("Partition 1\nseq: 1,4,7", BLUE, width=2.2, height=0.85)
        p2 = self._flow_node("Partition 2\nseq: 2,5,8", ORANGE, width=2.2, height=0.85)
        p3 = self._flow_node("Partition 3\nseq: 3,6,9", PURPLE, width=2.2, height=0.85)
        parts = VGroup(p1, p2, p3).arrange(DOWN, buff=0.2)

        seq_box = self._flow_node("Global\nSequencer", YELLOW, width=2.0, height=1.1)
        consumer = self._flow_node("Consumer\n(sort by seq)", GREEN, width=2.2, height=1.1)

        diagram = VGroup(parts, consumer).arrange(RIGHT, buff=2.8).move_to(DOWN * 0.1)
        seq_box.move_to(diagram.get_center() + UP * 0.0)

        a1 = Arrow(p1.get_right(), consumer.get_left(), buff=0.1, stroke_width=1.3, color=BLUE, tip_length=0.12)
        a2 = Arrow(p2.get_right(), consumer.get_left(), buff=0.1, stroke_width=1.3, color=ORANGE, tip_length=0.12)
        a3 = Arrow(p3.get_right(), consumer.get_left(), buff=0.1, stroke_width=1.3, color=PURPLE, tip_length=0.12)

        self.play(
            AnimationGroup(FadeIn(parts), FadeIn(consumer), lag_ratio=0.2)
        )
        self.play(GrowArrow(a1), GrowArrow(a2), GrowArrow(a3))
        self.wait(0.6)

        ordered_lbl = make_label(
            "Consumer reads from all partitions → sorts by seq → 1,2,3,4,5,6,7,8,9  ✓",
            font_size=11, color=GREEN,
        )
        ordered_lbl.next_to(consumer, DOWN, buff=0.2)
        self.play(FadeIn(ordered_lbl))
        self.wait(0.5)

        pros_title = make_label("Advantages", font_size=13, color=GREEN)
        pros = VGroup(
            make_label("✓  Minimal write-path change — same old code, new sequencing layer", font_size=11, color=GREEN),
            make_label("✓  All partitions remain active — no dormant partitions", font_size=11, color=GREEN),
        ).arrange(DOWN, buff=0.08, aligned_edge=LEFT)
        pros_group = VGroup(pros_title, pros).arrange(DOWN, buff=0.08, aligned_edge=LEFT)

        cons_title = make_label("Disadvantages", font_size=13, color=RED)
        cons = VGroup(
            make_label("✗  Shuffle on read — consumer must merge and sort across all partitions", font_size=11, color=RED),
            make_label("✗  Global counter = coordination bottleneck → performance hit at high throughput", font_size=11, color=RED),
        ).arrange(DOWN, buff=0.08, aligned_edge=LEFT)
        cons_group = VGroup(cons_title, cons).arrange(DOWN, buff=0.08, aligned_edge=LEFT)

        VGroup(pros_group, cons_group).arrange(DOWN, buff=0.18, aligned_edge=LEFT).to_edge(DOWN, buff=0.25)

        self.play(FadeIn(pros_group, shift=UP * 0.1))
        self.wait(0.4)
        self.play(FadeIn(cons_group, shift=UP * 0.1))
        self.play(Indicate(cons[1], color=RED, run_time=1.2))
        self.wait(3.5)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 9: Q3 — Streaming Tools ───────────────────────────────
    def scene_q3_tools(self):
        header = make_label("Q3: Streaming Tools & Transmission Models", font_size=25, color=PURPLE)
        header.to_edge(UP, buff=0.4)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.4)

        # Transmission model definitions
        models = [
            (GREY_B,  "Direct",          "Producer → Consumer (point-to-point, no intermediary)"),
            (ORANGE,  "Broker",          "Messages pass through central broker that routes them"),
            (TEAL,    "Partitioned Log", "Append-only log, consumers track own offset (replay-able)"),
        ]
        model_rows = VGroup()
        for color, name, desc in models:
            name_lbl = make_label(name, font_size=12, color=color)
            desc_lbl = make_label(desc, font_size=11, color=GREY_A)
            content = VGroup(name_lbl, desc_lbl).arrange(RIGHT, buff=0.3)
            box = RoundedRectangle(
                corner_radius=0.08, width=11.0, height=0.48,
                fill_color=DARK_BG, fill_opacity=0.9,
                stroke_color=color, stroke_width=1.1,
            )
            content.move_to(box.get_center())
            model_rows.add(VGroup(box, content))
        model_rows.arrange(DOWN, buff=0.07).next_to(header, DOWN, buff=0.3)

        for row in model_rows:
            self.play(FadeIn(row, shift=LEFT * 0.2), run_time=0.35)
            self.wait(0.2)

        self.wait(0.4)

        # Tool table
        col_labels = ["Tool", "Model", "Notes"]
        col_colors = [WHITE, TEAL, GREY_A]
        col_widths  = [3.2, 3.2, 5.0]

        tools_data = [
            ("ActiveMQ",         "Broker",           "JMS-based, traditional enterprise messaging"),
            ("RabbitMQ",         "Broker",           "AMQP, flexible exchange routing"),
            ("Amazon Kinesis",   "Partitioned Log",  "AWS-managed, shards = partitions"),
            ("Apache Kafka",     "Partitioned Log",  "High-throughput, replay, de facto standard"),
            ("Apache Flink",     "— (processing)",   "Consumes from Kafka/Kinesis; not a transport"),
        ]
        tool_colors = [ORANGE, ORANGE, TEAL, TEAL, BLUE]

        # Header row
        hdr_cells = VGroup()
        for text, color, width in zip(col_labels, col_colors, col_widths):
            cell = RoundedRectangle(
                corner_radius=0.06, width=width, height=0.44,
                fill_color="#21262D", fill_opacity=1,
                stroke_color=color, stroke_width=1.1,
            )
            lbl = make_label(text, font_size=12, color=color)
            lbl.move_to(cell)
            hdr_cells.add(VGroup(cell, lbl))
        hdr_cells.arrange(RIGHT, buff=0.06).next_to(model_rows, DOWN, buff=0.25)
        self.play(FadeIn(hdr_cells, shift=DOWN * 0.1))

        all_rows = VGroup()
        for (tool, model, note), color in zip(tools_data, tool_colors):
            row = VGroup()
            for text, col_color, width in zip([tool, model, note], [color, TEAL if "Log" in model else ORANGE if "Broker" in model else GREY_B, GREY_A], col_widths):
                cell = RoundedRectangle(
                    corner_radius=0.06, width=width, height=0.42,
                    fill_color=DARK_BG, fill_opacity=0.9,
                    stroke_color=GREY_B, stroke_width=0.6,
                )
                lbl = make_label(text, font_size=11, color=col_color)
                lbl.move_to(cell)
                row.add(VGroup(cell, lbl))
            row.arrange(RIGHT, buff=0.06)
            all_rows.add(row)

        all_rows.arrange(DOWN, buff=0.05).next_to(hdr_cells, DOWN, buff=0.05)
        for row in all_rows:
            self.play(FadeIn(row, shift=LEFT * 0.2), run_time=0.3)
            self.wait(0.12)

        # Highlight the two brokers
        self.play(Indicate(all_rows[0][1], color=ORANGE, run_time=1.0))
        self.play(Indicate(all_rows[1][1], color=ORANGE, run_time=1.0))
        # Highlight the two partitioned logs
        self.play(Indicate(all_rows[2][1], color=TEAL, run_time=1.0))
        self.play(Indicate(all_rows[3][1], color=TEAL, run_time=1.0))

        self.wait(3)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 10: Closing ────────────────────────────────────────────
    def scene_closing(self):
        title = make_label("Sheet 5: Streaming", font_size=34, color=TEAL)
        title.move_to(UP * 1.8)
        self.play(AddTextLetterByLetter(title, time_per_char=0.05))
        self.wait(0.8)

        icon_data = [
            (ICON_LIGHTNING, TEAL),
            (ICON_DATABASE,  BLUE),
            (ICON_SERVER,    ORANGE),
            (ICON_SHIELD,    GREEN),
            (ICON_GRAPH,     PURPLE),
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
            "Drop  ·  Buffer  ·  Backpressure  ·  Ordering  ·  Partitioned Logs",
            font_size=17, color=GREY_A,
        )
        themes.move_to(DOWN * 1.5)
        self.play(FadeIn(themes, shift=UP * 0.2))
        self.wait(4)
        self.play(FadeOut(*self.mobjects))
