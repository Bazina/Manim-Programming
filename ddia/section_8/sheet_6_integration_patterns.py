import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from manim import (
    config,
    Scene,
    VGroup,
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

from libs.ddia_components import (
    ICON_DATABASE,
    ICON_CODE,
    ICON_LIGHTNING,
    ICON_STOPWATCH,
    ICON_CHECK,
    ICON_DANGER,
    ICON_STRUCTURE,
    ICON_LAYERS,
    ICON_CHART,
    ICON_SETTINGS,
    ICON_CODE_FILE,
    ICON_TRANSFER,
    create_rect_glow,
    make_comparison_table,
    make_label,
    make_icon,
    make_code_text,
)
from libs.slide_style import SlideStyleMixin

config.background_color = "#0D1117"


class Sheet6IntegrationPatterns(SlideStyleMixin, BaseSlide):

    # Stop policy: "off", "scene", or "phase".
    # Avoid reverse-video generation to prevent PyAV malloc failures on long renders.
    max_duration_before_split_reverse = 8.0

    def construct(self):
        self.scene_title()
        self.scene_q1_intro()
        self.scene_q1_completeness()
        self.scene_q2_intro()
        self.scene_q2_pipeline_diagram()
        self.scene_q2_channels()
        self.scene_q2_routers()
        self.scene_q2_transformers()
        self.scene_q2_endpoints()
        self.scene_q3_intro()
        self.scene_q3_channels()
        self.scene_q3_routers()
        self.scene_q3_aggregator()
        self.scene_q3_endpoints()
        self.scene_q3_full_diagram()
        self.scene_closing()

    # ─── Shared helper: reveal rows with glow indices ─────────────────
    def _reveal_rows(self, items, glow_indices=None, anchor=None, anchor_dir=DOWN,
                     anchor_buff=0.3, run_time=0.45, wait_after=0.35):
        """items: list of (icon_path, color, title, desc). glow_indices: set of ints."""
        glow_indices = glow_indices or set()
        rows = VGroup()
        glow_map = {}
        color_map = {}
        for j, (icon_path, color, title, desc) in enumerate(items):
            result = self._icon_row_card(icon_path, color, title, desc,
                                         glow=(j in glow_indices))
            if isinstance(result, tuple):
                card, g = result
                rows.add(card)
                glow_map[j] = g
                color_map[j] = color
            else:
                rows.add(result)
        rows.arrange(DOWN, buff=0.1)
        if anchor is not None:
            rows.next_to(anchor, anchor_dir, buff=anchor_buff)
        for idx, g in glow_map.items():
            g.move_to(rows[idx])
            self.add(g)
            self.bring_to_back(g)
            g.set_opacity(0)

        for i, row in enumerate(rows):
            self.play(FadeIn(row, shift=LEFT * 0.3), run_time=run_time)
            if i in glow_map:
                self._play_glow_row(row, glow_map[i], color_map[i])
            self.wait(wait_after)
            if i < len(rows) - 1:
                self._next_slide(phase=True)
        return rows

    # ─── Scene 1: Title ───────────────────────────────────────────────
    def scene_title(self):
        icon = make_icon(ICON_TRANSFER, color=TEAL, height=1.1)
        title = make_label("Sheet 6: Integration Patterns", font_size=34, color=TEAL)
        sub = make_label(
            "Aggregators  ·  Channels  ·  Routers  ·  Transformers  ·  Endpoints",
            font_size=16, color=GREY_B,
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

    # ─── Scene 2: Q1 Intro — Aggregator Completeness ──────────────────
    def scene_q1_intro(self):
        header = self._section_header("Q1: Aggregator Completeness Conditions", color=TEAL)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.4)

        intro = make_label(
            "When should the Aggregator stop waiting and emit its result?",
            font_size=14, color=GREY_A,
        )
        intro.next_to(header, DOWN, buff=0.3)
        self.play(FadeIn(intro, shift=UP * 0.1))
        self.wait(0.4)

        items = [
            (ICON_STOPWATCH, ORANGE, "Time Out",
             "Decide once a fixed waiting window closes"),
            (ICON_LIGHTNING, BLUE, "External Event",
             "Triggered by a specific event (e.g. end-of-day signal)"),
            (ICON_CHECK, GREEN, "First Best",
             "Emit as soon as the first acceptable response arrives"),
            (ICON_LAYERS, PURPLE, "Wait for All",
             "Block until every expected participant has responded"),
            (ICON_SETTINGS, YELLOW, "Time Out with Override",
             "Timeout OR an override (e.g. minimum threshold reached) ends the wait"),
        ]
        self._reveal_rows(items, glow_indices={4}, anchor=intro, anchor_buff=0.35,
                          run_time=0.4, wait_after=0.25)
        self.wait(2)
        self._next_slide()
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 3: Q1 Completeness Table ───────────────────────────────
    def scene_q1_completeness(self):
        header = self._section_header(
            "Q1: Scenario → Completeness Condition",
            color=TEAL,
        )
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.4)

        rows_data = [
            (
                "Bidding for an ad poster", BLUE,
                "Time Out", ORANGE,
                "Stop when bid window closes", GREY_A,
            ),
            (
                "Bank end-of-day", BLUE,
                "External Event", TEAL,
                "Specific time-of-day trigger fires", GREY_A,
            ),
            (
                "Patrol cars → 911 call", BLUE,
                "First Best", GREEN,
                "First available unit answers", GREY_A,
            ),
            (
                "Leader w/ ALL consistency", BLUE,
                "Wait for All", PURPLE,
                "Every replica must acknowledge", GREY_A,
            ),
            (
                "Bidding (min $100K)", BLUE,
                "Time Out w/ Override", YELLOW,
                "Timeout OR threshold reached", GREY_A,
            ),
        ]
        table = make_comparison_table(
            col_headers=["Scenario", "Completeness Condition", "Why?"],
            col_colors=[GREY_A, TEAL, GREY_B],
            col_x_positions=[-4.8, -0.2, 4.4],
            rows_data=rows_data,
            header_font_size=13,
            row_font_size=11,
            note_font_size=10,
            row_spacing=0.52,
        )
        table.next_to(header, DOWN, buff=0.4)

        self.play(FadeIn(table[0]), FadeIn(table[1]))
        self.wait(0.3)
        # Reveal rows one at a time
        for i, row in enumerate(table[2]):
            self.play(FadeIn(row, shift=LEFT * 0.15), run_time=0.4)
            # Highlight verdict cell
            self.play(Indicate(row[1], color=row[1].color, run_time=0.7))
            self.wait(0.2)
            if i < len(table[2]) - 1:
                self._next_slide(phase=True)

        # Final glow on the most subtle one — "Time Out with Override"
        last_row = table[2][4]
        glow = create_rect_glow(last_row[1], color=YELLOW, max_opacity=0.28, spread=0.32)
        self.add(glow)
        self.bring_to_back(glow)
        glow.set_opacity(0)
        self._play_glow_row(last_row[1], glow, YELLOW)
        self.wait(3)
        self._next_slide()
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 4: Q2 Intro — ATM CDC Pipeline ─────────────────────────
    def scene_q2_intro(self):
        header = self._section_header(
            "Q2: ATM → Central Server CDC Pipeline",
            color=ORANGE,
        )
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.4)

        setup = make_label(
            "CDC watches ATM transaction logs → wraps each change as a message →",
            font_size=12, color=GREY_A,
        )
        setup2 = make_label(
            "Kafka topic → Apache NiFi (JSON → record) → MySQL at the central server.",
            font_size=12, color=GREY_A,
        )
        VGroup(setup, setup2).arrange(DOWN, buff=0.12).next_to(header, DOWN, buff=0.3)
        self.play(FadeIn(setup, shift=UP * 0.1))
        self.play(FadeIn(setup2, shift=UP * 0.1))
        self.wait(0.4)

        items = [
            (ICON_DATABASE, BLUE, "ATM Local DB",
             "Source of truth for the ATM transaction log"),
            (ICON_TRANSFER, ORANGE, "CDC (Change Data Capture)",
             "Polls transaction log, wraps each change in a JSON envelope"),
            (ICON_LIGHTNING, YELLOW, "Kafka Topic",
             "Durable, partitioned message channel between CDC and NiFi"),
            (ICON_CODE, PURPLE, "Apache NiFi",
             "Consumes JSON, normalizes into a record schema for MySQL"),
            (ICON_DATABASE, GREEN, "Central MySQL",
             "Idempotent receiver — applies records to the central store"),
        ]
        self._reveal_rows(items, glow_indices={1, 3}, anchor=setup2, anchor_buff=0.4,
                          run_time=0.4, wait_after=0.2)
        self.wait(2)
        self._next_slide()
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 5: Q2 Pipeline Diagram ─────────────────────────────────
    def scene_q2_pipeline_diagram(self):
        header = self._section_header("Q2: Pipeline Topology", color=ORANGE)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.4)

        atm = self._flow_node("ATM\nTxn Log", BLUE, width=1.9, height=1.0)
        cdc = self._flow_node("CDC", ORANGE, width=1.5, height=1.0)
        kafka = self._flow_node("Kafka\nTopic", YELLOW, width=1.7, height=1.0)
        nifi = self._flow_node("NiFi", PURPLE, width=1.5, height=1.0)
        mysql = self._flow_node("Central\nMySQL", GREEN, width=1.9, height=1.0)

        flow = VGroup(atm, cdc, kafka, nifi, mysql).arrange(RIGHT, buff=1.1)
        flow.move_to(UP * 0.4)

        a1 = self._flow_arrow(atm, cdc, color=ORANGE, label="poll", label_dir=UP)
        a2 = self._flow_arrow(cdc, kafka, color=YELLOW, label="JSON", label_dir=UP)
        a3 = self._flow_arrow(kafka, nifi, color=PURPLE, label="consume", label_dir=UP)
        a4 = self._flow_arrow(nifi, mysql, color=GREEN, label="record", label_dir=UP)

        self.play(AnimationGroup(
            *[FadeIn(n, shift=DOWN * 0.15) for n in [atm, cdc, kafka, nifi, mysql]],
            lag_ratio=0.2,
        ))
        self.wait(0.3)
        for a in [a1, a2, a3, a4]:
            arrow_part = a[0] if isinstance(a, VGroup) else a
            self.play(GrowArrow(arrow_part), run_time=0.4)
            if isinstance(a, VGroup) and len(a) > 1:
                self.play(FadeIn(a[1]), run_time=0.25)
            self._next_slide(phase=True)

        # Pattern legend below
        legend = VGroup(
            make_label("Point-to-Point channels link every adjacent pair",
                       font_size=11, color=ORANGE),
            make_label("CDC = Envelope Wrapper  ·  NiFi = Normalizer / Translator",
                       font_size=11, color=PURPLE),
            make_label("CDC pulls (Polling) · NiFi pushed from Kafka (Event-Driven) · MySQL idempotent",
                       font_size=11, color=GREEN),
        ).arrange(DOWN, buff=0.12).to_edge(DOWN, buff=0.5)
        self.play(FadeIn(legend, shift=UP * 0.15))
        self.wait(3)
        self._next_slide()
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 6: Q2 Channel Pattern ──────────────────────────────────
    def scene_q2_channels(self):
        header = self._section_header("Q2: Channel Pattern", color=BLUE)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.4)

        verdict = make_label(
            "Point-to-Point — exactly one consumer per message",
            font_size=15, color=BLUE,
        )
        verdict.next_to(header, DOWN, buff=0.3)
        self.play(FadeIn(verdict, shift=UP * 0.1))
        self.wait(0.4)

        items = [
            (ICON_TRANSFER, BLUE, "CDC ↔ Transaction Log",
             "CDC tails one log writer's stream of changes"),
            (ICON_TRANSFER, BLUE, "CDC ↔ Kafka",
             "CDC produces directly into a dedicated topic partition"),
            (ICON_TRANSFER, BLUE, "Kafka ↔ NiFi",
             "Each partition is read by exactly one NiFi consumer"),
            (ICON_TRANSFER, BLUE, "NiFi ↔ MySQL",
             "NiFi writes records to a single MySQL endpoint"),
        ]
        self._reveal_rows(items, glow_indices={0}, anchor=verdict, anchor_buff=0.4,
                          run_time=0.45, wait_after=0.3)
        self.wait(2.5)
        self._next_slide()
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 7: Q2 Router Pattern ───────────────────────────────────
    def scene_q2_routers(self):
        header = self._section_header("Q2: Router Pattern", color=PURPLE)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.4)

        verdict = make_label(
            "Content-Based Router — Kafka routes messages by topic name",
            font_size=15, color=PURPLE,
        )
        verdict.next_to(header, DOWN, buff=0.3)
        self.play(FadeIn(verdict, shift=UP * 0.1))
        self.wait(0.4)

        items = [
            (ICON_TRANSFER, PURPLE, "Internal Topic Router",
             "Kafka brokers dispatch each producer record to the named topic"),
            (ICON_CODE, ORANGE, "Producer Side",
             "CDC selects the topic per change → routing key on write"),
            (ICON_LIGHTNING, YELLOW, "Consumer Side",
             "NiFi subscribes to the topic — content type determines flow"),
        ]
        self._reveal_rows(items, glow_indices={0}, anchor=verdict, anchor_buff=0.4,
                          run_time=0.45, wait_after=0.3)
        self.wait(2.5)
        self._next_slide()
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 8: Q2 Transformer Patterns ─────────────────────────────
    def scene_q2_transformers(self):
        header = self._section_header("Q2: Transformer Patterns", color=YELLOW)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.4)

        verdict = make_label(
            "Two transformers reshape the message as it moves through the pipeline",
            font_size=14, color=GREY_A,
        )
        verdict.next_to(header, DOWN, buff=0.3)
        self.play(FadeIn(verdict, shift=UP * 0.1))
        self.wait(0.4)

        items = [
            (ICON_LAYERS, ORANGE, "Envelope Wrapper — CDC → Kafka",
             "Wraps the raw row change in a JSON envelope w/ metadata"),
            (ICON_STRUCTURE, PURPLE, "Normalizer / Translator — NiFi → MySQL",
             "Converts JSON message into a flat record matching MySQL schema"),
        ]
        self._reveal_rows(items, glow_indices={0, 1}, anchor=verdict, anchor_buff=0.4,
                          run_time=0.5, wait_after=0.35)

        # Mini diagram showing the two transformations
        msg1 = make_code_text(
            '{"op":"insert","row":{...}}',
            font_size=9, language="json", force_code_object=True,
            glow=False, with_background=False,
        )
        msg2 = make_code_text(
            "INSERT INTO txn VALUES(...)",
            font_size=9, language="sql", force_code_object=True,
            glow=False, with_background=False,
        )
        arrow = Arrow(LEFT * 1.4, RIGHT * 1.4, buff=0,
                      stroke_width=2.0, color=PURPLE, tip_length=0.15)
        translate_lbl = make_label("translate", font_size=9, color=PURPLE)
        translate_lbl.next_to(arrow, UP, buff=0.08)

        mini = VGroup(msg1, VGroup(arrow, translate_lbl), msg2).arrange(RIGHT, buff=0.4)
        mini.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(mini, shift=UP * 0.15))
        self.wait(3)
        self._next_slide()
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 9: Q2 Endpoint Patterns ────────────────────────────────
    def scene_q2_endpoints(self):
        header = self._section_header("Q2: Endpoint Patterns", color=GREEN)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.4)

        verdict = make_label(
            "Each hop has a distinct consumer-style endpoint",
            font_size=14, color=GREY_A,
        )
        verdict.next_to(header, DOWN, buff=0.3)
        self.play(FadeIn(verdict, shift=UP * 0.1))
        self.wait(0.4)

        items = [
            (ICON_STOPWATCH, ORANGE, "Polling Consumer — CDC ← Txn Log",
             "CDC periodically scans the transaction log for new changes"),
            (ICON_LIGHTNING, YELLOW, "Event-Driven Consumer — Kafka ← CDC",
             "Kafka push-delivers each record as soon as CDC publishes"),
            (ICON_CHECK, GREEN, "Idempotent Receiver — MySQL ← NiFi",
             "Re-applying a record (e.g. on retry) is safe — no duplicate side effects"),
        ]
        self._reveal_rows(items, glow_indices={2}, anchor=verdict, anchor_buff=0.4,
                          run_time=0.45, wait_after=0.3)
        self.wait(2.5)
        self._next_slide()
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 10: Q3 Intro — Credit Card System ──────────────────────
    def scene_q3_intro(self):
        header = self._section_header(
            "Q3: Credit Card System — Business Rules",
            color=RED,
        )
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.4)

        rules = [
            (ICON_CHART, GREEN, "Gas — 5% discount",
             "Any gas-station purchase is auto-discounted at 5%"),
            (ICON_CHART, BLUE, "EgyptAir — 2% discount",
             "Any flight booking with EgyptAir is discounted at 2%"),
            (ICON_CHART, TEAL, "Uber — 1% discount",
             "Any Uber ride is discounted at 1%"),
            (ICON_DANGER, RED, "Failed Payments Log",
             "All failed payments stored separately, released in statement"),
            (ICON_TRANSFER, ORANGE, "Foreign Currency = 8% interest",
             "Conversion transformer adds 8% to any non-local-currency purchase"),
            (ICON_STOPWATCH, YELLOW, "Limit 50K / month",
             "Hard ceiling — beyond limit, no purchase valid until 25th"),
            (ICON_CODE_FILE, PURPLE, "Statement on the 25th",
             "Monthly statement is released for the card owner to review"),
        ]
        self._reveal_rows(rules, glow_indices={5, 6}, anchor=header, anchor_buff=0.35,
                          run_time=0.35, wait_after=0.18)
        self.wait(2)
        self._next_slide()
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 11: Q3 Channels ────────────────────────────────────────
    def scene_q3_channels(self):
        header = self._section_header("Q3: Channel Patterns", color=BLUE)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.4)

        rows_data = [
            (
                "Dead Letter", RED,
                "Message NOT received", GREY_A,
                "Network failure between components", GREY_A,
            ),
            (
                "Invalid", ORANGE,
                "Received but invalid", GREY_A,
                "Spending limit reached → reject", GREY_A,
            ),
        ]
        table = make_comparison_table(
            col_headers=["Channel", "Trigger", "Example"],
            col_colors=[BLUE, GREY_B, GREY_B],
            col_x_positions=[-4.5, -0.2, 4.0],
            rows_data=rows_data,
            header_font_size=13,
            row_font_size=12,
            note_font_size=10,
            row_spacing=0.55,
        )
        table.next_to(header, DOWN, buff=0.5)
        self.play(FadeIn(table[0]), FadeIn(table[1]))
        self.wait(0.3)
        for i, row in enumerate(table[2]):
            self.play(FadeIn(row, shift=LEFT * 0.15), run_time=0.4)
            self.play(Indicate(row[0], color=row[0].color, run_time=0.7))
            self.wait(0.2)
            if i < len(table[2]) - 1:
                self._next_slide(phase=True)

        items = [
            (ICON_DANGER, RED, "Dead Letter Channel",
             "If no system component received the message (network problem)"),
            (ICON_DANGER, ORANGE, "Invalid Channel",
             "If a component received but deemed message invalid (limit reached)"),
        ]
        rows = self._reveal_rows(items, glow_indices={0}, anchor=table, anchor_buff=0.55,
                                 run_time=0.45, wait_after=0.3)
        self.wait(2)
        self._next_slide()
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 12: Q3 Routers ─────────────────────────────────────────
    def scene_q3_routers(self):
        header = self._section_header("Q3: Router Patterns", color=PURPLE)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.4)

        rows_data = [
            (
                "Content-Based Router", PURPLE,
                "Static discount rules", GREY_A,
                "If gas/EgyptAir/Uber → fixed branch", GREY_A,
            ),
            (
                "Dynamic Router", YELLOW,
                "Rules can change over time", GREY_A,
                "Promo rules updated by ops team", GREY_A,
            ),
            (
                "Content Enricher", TEAL,
                "Add data from external source", GREY_A,
                "Fetch discount % → attach to purchase msg", GREY_A,
            ),
        ]
        table = make_comparison_table(
            col_headers=["Router", "When", "Behaviour"],
            col_colors=[PURPLE, GREY_B, GREY_B],
            col_x_positions=[-4.5, -0.2, 4.0],
            rows_data=rows_data,
            header_font_size=13,
            row_font_size=11,
            note_font_size=10,
            row_spacing=0.5,
        )
        table.next_to(header, DOWN, buff=0.4)
        self.play(FadeIn(table[0]), FadeIn(table[1]))
        for i, row in enumerate(table[2]):
            self.play(FadeIn(row, shift=LEFT * 0.15), run_time=0.4)
            self.play(Indicate(row[0], color=row[0].color, run_time=0.7))
            if i < len(table[2]) - 1:
                self._next_slide(phase=True)

        # Glow the Content Enricher row — the canonical answer
        target = table[2][2][0]
        glow = create_rect_glow(target, color=TEAL, max_opacity=0.28, spread=0.32)
        self.add(glow)
        self.bring_to_back(glow)
        glow.set_opacity(0)
        self._play_glow_row(target, glow, TEAL)

        note = make_label(
            "Enrichment = discount % fetched from discounts data source → added to purchase message",
            font_size=11, color=GREY_A,
        )
        note.to_edge(DOWN, buff=0.6)
        self.play(FadeIn(note, shift=UP * 0.1))
        self.wait(3)
        self._next_slide()
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 13: Q3 Aggregator ──────────────────────────────────────
    def scene_q3_aggregator(self):
        header = self._section_header(
            "Q3: Aggregator — Timeout with Override",
            color=YELLOW,
        )
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.4)

        intro = make_label(
            "Statement aggregator collects purchases for a card across the month",
            font_size=13, color=GREY_A,
        )
        intro.next_to(header, DOWN, buff=0.3)
        self.play(FadeIn(intro, shift=UP * 0.1))
        self.wait(0.3)

        items = [
            (ICON_STOPWATCH, YELLOW, "Timeout → 25th of each month",
             "Calendar trigger — statement released on the 25th"),
            (ICON_DANGER, RED, "Override → 50K spending limit reached",
             "Short-circuit emission — block further purchases until next cycle"),
        ]
        rows = self._reveal_rows(items, glow_indices={0, 1}, anchor=intro,
                                 anchor_buff=0.4, run_time=0.5, wait_after=0.4)

        # Visual: clock face + threshold meter
        stopwatch = make_icon(ICON_STOPWATCH, color=YELLOW, height=0.6)
        clock_lbl = make_label("25th", font_size=12, color=YELLOW)
        clock_grp = VGroup(stopwatch, clock_lbl).arrange(DOWN, buff=0.08)

        sep = make_label("OR", font_size=14, color=GREY_A)

        danger = make_icon(ICON_DANGER, color=RED, height=0.6)
        limit_lbl = make_label("50K reached", font_size=12, color=RED)
        limit_grp = VGroup(danger, limit_lbl).arrange(DOWN, buff=0.08)

        trigger_row = VGroup(clock_grp, sep, limit_grp).arrange(RIGHT, buff=0.7)
        trigger_row.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(trigger_row, shift=UP * 0.15))
        self.wait(3)
        self._next_slide()
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 14: Q3 Endpoints ───────────────────────────────────────
    def scene_q3_endpoints(self):
        header = self._section_header("Q3: Endpoint Patterns", color=GREEN)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.4)

        verdict = make_label(
            "By banking business nature — never lose, never duplicate",
            font_size=14, color=GREY_A,
        )
        verdict.next_to(header, DOWN, buff=0.3)
        self.play(FadeIn(verdict, shift=UP * 0.1))
        self.wait(0.4)

        items = [
            (ICON_CHECK, GREEN, "Idempotent Receiver",
             "Same purchase delivered twice → charged once (safe retries)"),
            (ICON_LAYERS, BLUE, "Durable Subscriber",
             "Survives crashes — messages persisted until acknowledged"),
        ]
        self._reveal_rows(items, glow_indices={0, 1}, anchor=verdict,
                          anchor_buff=0.4, run_time=0.5, wait_after=0.4)

        note = make_label(
            "Combined: every purchase is delivered exactly once, even across outages",
            font_size=12, color=YELLOW,
        )
        note.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(note, shift=UP * 0.1))
        self.wait(3)
        self._next_slide()
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 15: Q3 Full System Diagram ─────────────────────────────
    def scene_q3_full_diagram(self):
        header = self._section_header(
            "Q3: Credit Card System — Full Sketch",
            color=TEAL,
        )
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.4)

        # Top row: source → router → enricher → aggregator → endpoint
        purchase = self._flow_node("Purchase\nMessage", BLUE, width=1.9, height=0.95)
        router = self._flow_node("Content-Based\nRouter", PURPLE, width=2.0, height=0.95)
        enricher = self._flow_node("Content\nEnricher", TEAL, width=1.8, height=0.95)
        aggregator = self._flow_node("Aggregator\n(Timeout+Override)", YELLOW,
                                     width=2.4, height=0.95)
        endpoint = self._flow_node("Idempotent\nReceiver", GREEN, width=2.0, height=0.95)

        top = VGroup(purchase, router, enricher, aggregator, endpoint).arrange(RIGHT, buff=0.35)
        top.move_to(UP * 1.1)

        a1 = self._flow_arrow(purchase, router, color=BLUE)
        a2 = self._flow_arrow(router, enricher, color=PURPLE)
        a3 = self._flow_arrow(enricher, aggregator, color=TEAL)
        a4 = self._flow_arrow(aggregator, endpoint, color=YELLOW)

        self.play(AnimationGroup(
            *[FadeIn(n, shift=DOWN * 0.15) for n in top],
            lag_ratio=0.18,
        ))
        for arr in [a1, a2, a3, a4]:
            self.play(GrowArrow(arr), run_time=0.4)
            self._next_slide(phase=True)

        # Bottom row: branch channels off router
        dead = self._flow_node("Dead Letter\nChannel", RED, width=1.9, height=0.85)
        invalid = self._flow_node("Invalid\nChannel", ORANGE, width=1.9, height=0.85)
        fx = self._flow_node("FX Translator\n(+8%)", BLUE, width=2.0, height=0.85)
        log = self._flow_node("Failed-Payments\nLog", GREY_B, width=2.0, height=0.85)

        bottom = VGroup(dead, invalid, fx, log).arrange(RIGHT, buff=0.5)
        bottom.move_to(DOWN * 1.5)

        # Connecting branch arrows from router/enricher down
        b1 = Arrow(router.get_bottom(), dead.get_top(), buff=0.08,
                   stroke_width=1.6, color=RED, tip_length=0.13)
        b2 = Arrow(router.get_bottom(), invalid.get_top(), buff=0.08,
                   stroke_width=1.6, color=ORANGE, tip_length=0.13)
        b3 = Arrow(enricher.get_bottom(), fx.get_top(), buff=0.08,
                   stroke_width=1.6, color=BLUE, tip_length=0.13)
        b4 = Arrow(aggregator.get_bottom(), log.get_top(), buff=0.08,
                   stroke_width=1.6, color=GREY_B, tip_length=0.13)

        self.play(AnimationGroup(
            *[FadeIn(n, shift=UP * 0.15) for n in bottom],
            lag_ratio=0.18,
        ))
        for arr in [b1, b2, b3, b4]:
            self.play(GrowArrow(arr), run_time=0.35)

        # Glow the aggregator — the centerpiece
        glow = create_rect_glow(aggregator[0], color=YELLOW,
                                max_opacity=0.28, spread=0.34)
        self.add(glow)
        self.bring_to_back(glow)
        glow.set_opacity(0)
        self._play_glow_row(aggregator, glow, YELLOW)
        self.wait(0.4)

        # Legend
        legend = VGroup(
            make_label("Channels: Dead-Letter · Invalid",
                       font_size=10, color=RED),
            make_label("Routers: Content-Based · Content Enricher",
                       font_size=10, color=PURPLE),
            make_label("Transformer: FX Translator (8% interest)",
                       font_size=10, color=BLUE),
            make_label("Endpoint: Idempotent Receiver + Durable Subscriber",
                       font_size=10, color=GREEN),
        ).arrange(DOWN, buff=0.06, aligned_edge=LEFT)
        legend.to_edge(DOWN, buff=0.2).to_edge(LEFT, buff=0.4)
        self.play(FadeIn(legend, shift=UP * 0.1))
        self.wait(4)
        self._next_slide()
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 16: Closing ────────────────────────────────────────────
    def scene_closing(self):
        title = make_label("Sheet 6: Integration Patterns",
                           font_size=32, color=TEAL)
        title.move_to(UP * 1.8)
        self.play(AddTextLetterByLetter(title, time_per_char=0.05))
        self.wait(0.6)

        icon_data = [
            (ICON_STOPWATCH, YELLOW),
            (ICON_TRANSFER, BLUE),
            (ICON_STRUCTURE, PURPLE),
            (ICON_LAYERS, ORANGE),
            (ICON_CHECK, GREEN),
        ]
        icons_row = (
            VGroup(*[make_icon(p, color=c, height=0.5) for p, c in icon_data])
            .arrange(RIGHT, buff=0.55)
            .move_to(ORIGIN)
        )
        self.play(
            AnimationGroup(*[FadeIn(ic, shift=UP * 0.2) for ic in icons_row],
                           lag_ratio=0.1)
        )
        self.wait(0.8)

        themes = make_label(
            "Aggregators  ·  Channels  ·  Routers  ·  Transformers  ·  Endpoints",
            font_size=16, color=GREY_A,
        )
        themes.move_to(DOWN * 1.5)
        self.play(FadeIn(themes, shift=UP * 0.2))
        self.wait(4)
        self._next_slide()
        self.play(FadeOut(*self.mobjects))
