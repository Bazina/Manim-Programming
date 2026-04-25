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
    UP,
    DOWN,
    LEFT,
    RIGHT,
    BOLD,
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
    ICON_LIGHTNING,
    ICON_CODE,
    ICON_STOPWATCH,
    ICON_CHART,
    ICON_STRUCTURE,
    ICON_GRAPH,
    ICON_BOOK,
    ICON_LAYERS,
    ICON_TRANSFER,
    ICON_CHECKLIST,
    ICON_CODE_FILE,
    ICON_CLOUD,
    make_label,
    make_icon,
    make_code_text,
    make_comparison_table,
    create_rect_glow,
)

config.background_color = "#0D1117"
config.pixel_height = 1080
config.pixel_width = 1920
config.frame_rate = 60

# ── Java syntax color map ─────────────────────────────────────────────
JAVA_T2C = {
    "long": "#4EC9B0",
    "new": "#C586C0",
    "Properties": "#4EC9B0",
    "String": "#4EC9B0",
    "void": "#4EC9B0",
    "static": "#C586C0",
    "public": "#C586C0",
    "private": "#C586C0",
    "Connection": "#9CDCFE",
    "Factory": "#9CDCFE",
    "Session": "#9CDCFE",
    "Topic": "#9CDCFE",
    "Message": "#9CDCFE",
    "Consumer": "#9CDCFE",
    "Kafka": "#9CDCFE",
    "ActiveMQ": "#CE9178",
    "AUTO_ACKNOWLEDGE": "#DCDCAA",
    "currentTimeMillis": "#DCDCAA",
    "create": "#DCDCAA",
    "Session": "#DCDCAA",
    "Text": "#DCDCAA",
    "send": "#DCDCAA",
    "start": "#DCDCAA",
    "put": "#DCDCAA",
    "false": "#569CD6",
    "true": "#569CD6",
    '"bootstrap.servers"': "#CE9178",
    '"key.serializer"': "#CE9178",
    '"value"': "#CE9178",
    '"localhost:9092"': "#CE9178",
    "//": "#6A9955",
    "System": "#DCDCAA",
    "(": "#FFD700",
    ")": "#FFD700",
    "{": "#FFD700",
    "}": "#FFD700",
    ";": "#D4D4D4",
}

# Bash script color map
BASH_T2C = {
    "--topic": "#9CDCFE",
    "num-records": "#9CDCFE",
    "record-size": "#9CDCFE",
    "throughput": "#9CDCFE",
    "bootstrap": "#9CDCFE",
    "producer-perf-test.sh": "#DCDCAA",
    "kafka": "#DCDCAA",
    "#": "#6A9955",
}


class Lab4JMSKafka(Scene):
    def construct(self):
        self.scene_title()
        self.scene_lab_overview()
        self.scene_tools_intro()
        self.scene_performance_overview()
        self.scene_response_time()
        self.scene_max_throughput()
        self.scene_median_latency()
        self.scene_usability()
        self.scene_integrations()
        self.scene_deliverables()
        self.scene_closing()

    # ─── Helpers ──────────────────────────────────────────────────────
    def _tool_card(self, title, subtitle, icon, color, width=3.8, height=2.0):
        box = RoundedRectangle(
            corner_radius=0.12,
            width=width,
            height=height,
            fill_color=DARK_BG,
            fill_opacity=0.95,
            stroke_color=color,
            stroke_width=1.6,
        )
        ic = make_icon(icon, color=color, height=0.5)
        lbl = make_label(title, font_size=18, color=color, weight=BOLD)
        sub = make_label(subtitle, font_size=11, color=GREY_B)
        content = VGroup(ic, lbl, sub).arrange(DOWN, buff=0.12)
        content.move_to(box.get_center())
        g = create_rect_glow(box, color=color)
        return VGroup(g, box, content)

    def _metric_row(self, label, jms_val, kafka_val, color=WHITE, y=0):
        lbl = make_label(label, font_size=13, color=GREY_A)
        jms = make_label(jms_val, font_size=13, color=ORANGE)
        kafka = make_label(kafka_val, font_size=13, color=TEAL)
        lbl.move_to([-3.5, y, 0])
        jms.move_to([0.8, y, 0])
        kafka.move_to([3.8, y, 0])
        return VGroup(lbl, jms, kafka)

    def _section_header(self, text, color=TEAL):
        hdr = make_label(text, font_size=30, color=color)
        hdr.to_edge(UP, buff=0.45)
        return hdr

    def _code_box(self, lines, title, color, width=5.8, font_size=11, t2c=None):
        text = "\n".join(lines)
        box = RoundedRectangle(
            corner_radius=0.1,
            width=width,
            height=len(lines) * 0.32 + 0.7,
            fill_color="#161B22",
            fill_opacity=0.95,
            stroke_color=color,
            stroke_width=1.2,
        )
        title_lbl = make_label(title, font_size=10, color=color)
        code = make_code_text(text, font_size=font_size, t2c=t2c or JAVA_T2C)
        content = VGroup(title_lbl, code).arrange(DOWN, buff=0.1)
        content.move_to(box.get_center())
        return VGroup(box, content)

    # ─── Scene 1: Title ───────────────────────────────────────────────
    def scene_title(self):
        icon = make_icon(ICON_TRANSFER, color=ORANGE, height=1.1)
        title = make_label("Lab 4: JMS vs Kafka", font_size=36, color=ORANGE)
        sub = make_label(
            "Performance  ·  Usability  ·  Integrations",
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
        header = self._section_header("What Will You Do?", color=GREEN)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.6)

        steps = [
            (ICON_LIGHTNING,  ORANGE, "A) Performance",
             "Response time · Max throughput · Median latency"),
            (ICON_CODE,       BLUE,   "B) Usability",
             "Setup steps · Lines of code · API call count"),
            (ICON_CLOUD,      TEAL,   "C) Integrations",
             "Hadoop · Cassandra · Cloud platforms"),
            (ICON_BOOK,       PURPLE, "D) Report & Recommendation",
             "Summary per tool · Conclusion with justification"),
        ]
        cards = VGroup()
        for icon, color, label, desc in steps:
            ic = make_icon(icon, color=color, height=0.38)
            lbl = make_label(label, font_size=15, color=color, weight=BOLD)
            d = make_label(desc, font_size=11, color=GREY_B)
            row_content = VGroup(ic, VGroup(lbl, d).arrange(DOWN, buff=0.05)).arrange(
                RIGHT, buff=0.25
            )
            box = RoundedRectangle(
                corner_radius=0.1,
                width=10,
                height=0.9,
                fill_color=DARK_BG,
                fill_opacity=0.9,
                stroke_color=color,
                stroke_width=1.2,
            )
            row_content.move_to(box.get_center()).shift(LEFT * 0.3)
            cards.add(VGroup(box, row_content))

        cards.arrange(DOWN, buff=0.2)
        cards.next_to(header, DOWN, buff=0.5)

        for card in cards:
            self.play(FadeIn(card, shift=RIGHT * 0.3), run_time=0.4)
            self.wait(0.3)

        self.wait(2.5)

        constraint_lbl = make_label(
            "Constraints: 1 KB messages  ·  Java API only  ·  Groups of 4",
            font_size=13,
            color=YELLOW,
        )
        constraint_lbl.to_edge(DOWN, buff=0.4)
        self.play(FadeIn(constraint_lbl, shift=UP * 0.15))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 3: Tools Introduction ─────────────────────────────────
    def scene_tools_intro(self):
        header = self._section_header("The Two Tools", color=ORANGE)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.6)

        jms_card = self._tool_card(
            "JMS / ActiveMQ",
            "Broker · Java EE Standard\nPoint-to-point & Pub/Sub",
            ICON_SERVER,
            ORANGE,
        )
        kafka_card = self._tool_card(
            "Apache Kafka",
            "Partitioned Log · Distributed\nHigh-throughput event streaming",
            ICON_DATABASE,
            TEAL,
        )
        pair = VGroup(jms_card, kafka_card).arrange(RIGHT, buff=1.0)
        pair.next_to(header, DOWN, buff=0.7)

        self.play(FadeIn(jms_card, shift=LEFT * 0.4))
        self.wait(0.3)
        self.play(FadeIn(kafka_card, shift=RIGHT * 0.4))
        self.wait(1.0)

        vs = make_label("VS", font_size=28, color=WHITE)
        vs.move_to(pair.get_center())
        self.play(FadeIn(vs))
        self.wait(0.5)

        # Transmission model labels
        jms_model = make_label("Broker Model", font_size=13, color=ORANGE)
        kafka_model = make_label("Partitioned Log", font_size=13, color=TEAL)
        jms_model.next_to(jms_card, DOWN, buff=0.25)
        kafka_model.next_to(kafka_card, DOWN, buff=0.25)
        self.play(FadeIn(jms_model), FadeIn(kafka_model))
        self.wait(1.5)

        # Simple broker diagram for JMS
        prod_box = RoundedRectangle(corner_radius=0.08, width=1.2, height=0.45,
                                    fill_color=DARK_BG, fill_opacity=0.9,
                                    stroke_color=ORANGE, stroke_width=1.2)
        broker_box = RoundedRectangle(corner_radius=0.08, width=1.4, height=0.45,
                                      fill_color=DARK_BG, fill_opacity=0.9,
                                      stroke_color=ORANGE, stroke_width=1.6)
        cons_box = RoundedRectangle(corner_radius=0.08, width=1.2, height=0.45,
                                    fill_color=DARK_BG, fill_opacity=0.9,
                                    stroke_color=ORANGE, stroke_width=1.2)
        prod_lbl = make_label("Producer", font_size=9, color=ORANGE)
        broker_lbl = make_label("Broker", font_size=9, color=ORANGE)
        cons_lbl = make_label("Consumer", font_size=9, color=ORANGE)
        prod_lbl.move_to(prod_box.get_center())
        broker_lbl.move_to(broker_box.get_center())
        cons_lbl.move_to(cons_box.get_center())
        jms_diag = VGroup(
            VGroup(prod_box, prod_lbl),
            VGroup(broker_box, broker_lbl),
            VGroup(cons_box, cons_lbl),
        ).arrange(RIGHT, buff=0.3)
        arr1 = Arrow(jms_diag[0].get_right(), jms_diag[1].get_left(),
                     buff=0.05, color=ORANGE, stroke_width=1.5, max_tip_length_to_length_ratio=0.2)
        arr2 = Arrow(jms_diag[1].get_right(), jms_diag[2].get_left(),
                     buff=0.05, color=ORANGE, stroke_width=1.5, max_tip_length_to_length_ratio=0.2)
        jms_full_diag = VGroup(jms_diag, arr1, arr2)
        jms_full_diag.next_to(jms_model, DOWN, buff=0.3)

        # Partitioned log diagram for Kafka
        log_box = RoundedRectangle(corner_radius=0.08, width=1.6, height=0.45,
                                   fill_color=DARK_BG, fill_opacity=0.9,
                                   stroke_color=TEAL, stroke_width=1.6)
        log_lbl = make_label("Partition Log", font_size=9, color=TEAL)
        log_lbl.move_to(log_box.get_center())
        p_box = RoundedRectangle(corner_radius=0.08, width=1.1, height=0.45,
                                 fill_color=DARK_BG, fill_opacity=0.9,
                                 stroke_color=TEAL, stroke_width=1.2)
        c_box = RoundedRectangle(corner_radius=0.08, width=1.1, height=0.45,
                                 fill_color=DARK_BG, fill_opacity=0.9,
                                 stroke_color=TEAL, stroke_width=1.2)
        p_lbl = make_label("Producer", font_size=9, color=TEAL)
        c_lbl = make_label("Consumer", font_size=9, color=TEAL)
        p_lbl.move_to(p_box.get_center())
        c_lbl.move_to(c_box.get_center())
        kafka_row = VGroup(
            VGroup(p_box, p_lbl),
            VGroup(log_box, log_lbl),
            VGroup(c_box, c_lbl),
        ).arrange(RIGHT, buff=0.3)
        k_arr1 = Arrow(kafka_row[0].get_right(), kafka_row[1].get_left(),
                       buff=0.05, color=TEAL, stroke_width=1.5, max_tip_length_to_length_ratio=0.2)
        k_arr2 = Arrow(kafka_row[1].get_right(), kafka_row[2].get_left(),
                       buff=0.05, color=TEAL, stroke_width=1.5, max_tip_length_to_length_ratio=0.2)
        offset_note = make_label("offset →", font_size=8, color=GREY_B)
        offset_note.next_to(kafka_row[1], DOWN, buff=0.08)
        kafka_full_diag = VGroup(kafka_row, k_arr1, k_arr2, offset_note)
        kafka_full_diag.next_to(kafka_model, DOWN, buff=0.3)

        self.play(FadeIn(jms_full_diag), FadeIn(kafka_full_diag))
        self.wait(3)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 4: Performance Overview ───────────────────────────────
    def scene_performance_overview(self):
        header = self._section_header("A) Performance — 3 Metrics", color=ORANGE)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.6)

        metrics = [
            (ICON_STOPWATCH, BLUE,   "1. Response Time",
             "Median of 1000 produce/consume\ncalls — 1 KB each"),
            (ICON_GRAPH,     GREEN,  "2. Max Throughput",
             "Highest msg/sec sustained\nwithout dropped messages"),
            (ICON_LIGHTNING, YELLOW, "3. Median Latency",
             "50th percentile of\nproduce→consume delay (10K msgs)"),
        ]
        cards = VGroup()
        for icon, color, title, desc in metrics:
            ic = make_icon(icon, color=color, height=0.42)
            lbl = make_label(title, font_size=14, color=color, weight=BOLD)
            d = make_label(desc, font_size=10, color=GREY_B)
            content = VGroup(ic, lbl, d).arrange(DOWN, buff=0.1)
            box = RoundedRectangle(
                corner_radius=0.12,
                width=3.8,
                height=2.4,
                fill_color=DARK_BG,
                fill_opacity=0.9,
                stroke_color=color,
                stroke_width=1.4,
            )
            content.move_to(box.get_center())
            cards.add(VGroup(box, content))

        cards.arrange(RIGHT, buff=0.35)
        cards.next_to(header, DOWN, buff=0.5)

        for card in cards:
            self.play(FadeIn(card, shift=UP * 0.3), run_time=0.45)
            self.wait(0.3)

        self.wait(3)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 5: Response Time ───────────────────────────────────────
    def scene_response_time(self):
        header = self._section_header("Response Time", color=BLUE)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.5)

        desc = make_label(
            "Median of 1000 produce calls  +  1000 consume calls  ·  1 KB messages",
            font_size=14,
            color=GREY_A,
        )
        desc.next_to(header, DOWN, buff=0.3)
        self.play(FadeIn(desc))
        self.wait(0.4)

        jms_lines = [
            "// JMS — Measure produce response time",
            "long start = System.currentTimeMillis();",
            "producer.send(msg);",
            "long elapsed = System.currentTimeMillis() - start;",
        ]
        kafka_lines = [
            "// Kafka — Measure produce response time",
            "long start = System.currentTimeMillis();",
            "producer.send(record).get();  // sync",
            "long elapsed = System.currentTimeMillis() - start;",
        ]
        jms_box = self._code_box(jms_lines, "JMS (ActiveMQ)", ORANGE, width=6.0)
        kafka_box = self._code_box(kafka_lines, "Kafka", TEAL, width=6.0)
        pair = VGroup(jms_box, kafka_box).arrange(RIGHT, buff=0.5)
        pair.next_to(desc, DOWN, buff=0.4)
        self.play(FadeIn(jms_box, shift=LEFT * 0.3))
        self.wait(0.3)
        self.play(FadeIn(kafka_box, shift=RIGHT * 0.3))
        self.wait(1.0)

        protocol = make_label(
            "Protocol:  produce 1000 msgs → record median  |  leave 1000 in queue → consume 1000 → record median",
            font_size=12,
            color=YELLOW,
        )
        protocol.next_to(pair, DOWN, buff=0.4)
        self.play(FadeIn(protocol))
        self.wait(3)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 6: Max Throughput ──────────────────────────────────────
    def scene_max_throughput(self):
        header = self._section_header("Max Throughput", color=GREEN)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.5)

        algo_lines = [
            "for X in [100, 200, 400, 800, ...]:   # exponential",
            "  T = 1000ms / X                       # period",
            "  for i in range(X):",
            "    send_message()",
            "    sleep(T - 0.2*T)  # thread-switch buffer",
            "  if any_failed: report X_prev as MAX; break",
        ]
        algo_box = RoundedRectangle(
            corner_radius=0.1, width=8.5, height=2.5,
            fill_color=DARK_BG, fill_opacity=0.95,
            stroke_color=GREEN, stroke_width=1.2,
        )
        algo_title = make_label("Algorithm", font_size=11, color=GREEN)
        algo_code = make_code_text("\n".join(algo_lines), font_size=11, t2c={
            "for": "#C586C0", "in": "#C586C0", "if": "#C586C0",
            "range": "#DCDCAA", "sleep": "#DCDCAA",
            "#": "#6A9955",
        })
        algo_content = VGroup(algo_title, algo_code).arrange(DOWN, buff=0.1)
        algo_content.move_to(algo_box.get_center())
        algo_vg = VGroup(algo_box, algo_content)
        algo_vg.next_to(header, DOWN, buff=0.45)
        self.play(FadeIn(algo_vg))
        self.wait(0.8)

        kafka_script_lines = [
            "# Kafka built-in perf scripts:",
            "kafka-producer-perf-test.sh \\",
            "  --topic test --num-records 10000 \\",
            "  --record-size 1024 --throughput 1000",
            "",
            "kafka-consumer-perf-test.sh \\",
            "  --topic test --messages 10000 \\",
            "  --bootstrap-server localhost:9092",
        ]
        kafka_box = RoundedRectangle(
            corner_radius=0.1, width=7.0, height=2.8,
            fill_color=DARK_BG, fill_opacity=0.95,
            stroke_color=TEAL, stroke_width=1.2,
        )
        k_title = make_label("Kafka — Built-in Scripts", font_size=11, color=TEAL)
        k_code = make_code_text("\n".join(kafka_script_lines), font_size=10, t2c=BASH_T2C)
        k_content = VGroup(k_title, k_code).arrange(DOWN, buff=0.1)
        k_content.move_to(kafka_box.get_center())
        kafka_vg = VGroup(kafka_box, k_content)

        jms_note_box = RoundedRectangle(
            corner_radius=0.1, width=4.5, height=2.8,
            fill_color=DARK_BG, fill_opacity=0.95,
            stroke_color=ORANGE, stroke_width=1.2,
        )
        jms_note_lbl = make_label("JMS — Use JMeter", font_size=11, color=ORANGE)
        jms_note_body = make_label(
            "Configure:\n· Number of threads\n· Ramp-up time\n· Loop count\nJustify each setting in report",
            font_size=11, color=GREY_A,
        )
        jms_note_content = VGroup(jms_note_lbl, jms_note_body).arrange(DOWN, buff=0.15)
        jms_note_content.move_to(jms_note_box.get_center())
        jms_note_vg = VGroup(jms_note_box, jms_note_content)

        bottom_pair = VGroup(jms_note_vg, kafka_vg).arrange(RIGHT, buff=0.5)
        bottom_pair.next_to(algo_vg, DOWN, buff=0.35)
        self.play(FadeIn(jms_note_vg, shift=LEFT * 0.3))
        self.wait(0.3)
        self.play(FadeIn(kafka_vg, shift=RIGHT * 0.3))
        self.wait(3)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 7: Median Latency ──────────────────────────────────────
    def scene_median_latency(self):
        header = self._section_header("Median Latency (End-to-End)", color=YELLOW)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.5)

        desc = make_label(
            "Time from producer send → consumer receive  ·  10 000 messages  ·  report 50th percentile",
            font_size=13,
            color=GREY_A,
        )
        desc.next_to(header, DOWN, buff=0.3)
        self.play(FadeIn(desc))

        steps = [
            "1. Start consumer (actively polling all messages)",
            "2. Producer: embed send_timestamp in message body",
            "3. On consume: latency = now() − send_timestamp",
            "4. Repeat for 10 000 messages",
            "5. Report the median (50th percentile)",
        ]
        step_vg = VGroup()
        for s in steps:
            lbl = make_label(s, font_size=14, color=GREY_A)
            step_vg.add(lbl)
        step_vg.arrange(DOWN, buff=0.22, aligned_edge=LEFT)
        step_vg.next_to(desc, DOWN, buff=0.5)
        step_vg.shift(LEFT * 1.5)

        for step in step_vg:
            self.play(FadeIn(step, shift=RIGHT * 0.2), run_time=0.35)
            self.wait(0.25)

        self.wait(1.5)

        # Producer timeline arrows
        prod = make_label("Producer", font_size=12, color=ORANGE)
        cons = make_label("Consumer", font_size=12, color=TEAL)
        arrow = Arrow(LEFT * 1.8, RIGHT * 1.8, color=YELLOW,
                      stroke_width=2, max_tip_length_to_length_ratio=0.12)
        latency_lbl = make_label("latency", font_size=11, color=YELLOW)
        latency_lbl.next_to(arrow, UP, buff=0.08)
        prod.next_to(arrow, LEFT, buff=0.15)
        cons.next_to(arrow, RIGHT, buff=0.15)
        timeline = VGroup(prod, arrow, latency_lbl, cons)
        timeline.next_to(step_vg, RIGHT, buff=1.0)
        self.play(FadeIn(prod), GrowArrow(arrow), FadeIn(latency_lbl), FadeIn(cons))
        self.wait(3)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 8: Usability ───────────────────────────────────────────
    def scene_usability(self):
        header = self._section_header("B) Usability", color=BLUE)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.5)

        metrics_intro = make_label(
            "Compare setup friction and code verbosity between JMS and Kafka",
            font_size=14, color=GREY_A,
        )
        metrics_intro.next_to(header, DOWN, buff=0.3)
        self.play(FadeIn(metrics_intro))
        self.wait(0.4)

        # each row: (metric, metric_color, jms_val, jms_color, kafka_val, kafka_color)
        usability_rows = [
            ("Setup steps",           GREY_A, "~? steps", ORANGE, "~? steps", TEAL),
            ("Time to Hello World",   GREY_A, "~? ms", ORANGE, "~? ms", TEAL),
            ("Lines to produce",      GREY_A, "~? lines", ORANGE, "~? lines", TEAL),
            ("Lines to consume",      GREY_A, "~? lines", ORANGE, "~? lines", TEAL),
            ("API calls (produce op)",GREY_A, "~? calls", ORANGE, "~? calls", TEAL),
        ]
        table = make_comparison_table(
            col_headers     = ["Metric",        "JMS (ActiveMQ)", "Kafka"],
            col_colors      = [WHITE,            ORANGE,           TEAL],
            col_x_positions = [-3.5,             0.8,              3.8],
            rows_data       = usability_rows,
        )
        table.next_to(metrics_intro, DOWN, buff=0.35)
        hdrs_grp, div, rows = table[0], table[1], table[2]

        self.play(FadeIn(hdrs_grp))
        self.play(FadeIn(div))
        for row in rows:
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.35)
            self.wait(0.2)

        self.wait(3)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 9: Integrations ────────────────────────────────────────
    def scene_integrations(self):
        header = self._section_header("C) Integrations", color=TEAL)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.5)

        note = make_label(
            "Research task — find integrations relevant to Data-Intensive Applications (with references)",
            font_size=13,
            color=GREY_A,
        )
        note.next_to(header, DOWN, buff=0.3)
        self.play(FadeIn(note))
        self.wait(0.5)

        categories = [
            (ICON_DATABASE, BLUE,   "Hadoop Ecosystem",
             "HDFS · Hive · HBase\nKafka: Kafka Connect HDFS sink\nJMS: limited native support"),
            (ICON_LAYERS,   PURPLE, "Columnar Stores",
             "Cassandra · ClickHouse\nKafka: Kafka Connect Cassandra sink\nJMS: manual integration"),
            (ICON_CLOUD,    TEAL,   "Cloud Platforms",
             "AWS MSK · GCP Pub/Sub · Azure Event Hub\nKafka: managed cloud offerings\nJMS: ActiveMQ on EC2/VMs"),
        ]
        cat_cards = VGroup()
        for icon, color, title, body in categories:
            ic = make_icon(icon, color=color, height=0.45)
            lbl = make_label(title, font_size=15, color=color, weight=BOLD)
            body_lbl = make_label(body, font_size=11, color=GREY_B)
            content = VGroup(ic, lbl, body_lbl).arrange(DOWN, buff=0.1)
            box = RoundedRectangle(
                corner_radius=0.12,
                width=3.8,
                height=2.5,
                fill_color=DARK_BG,
                fill_opacity=0.95,
                stroke_color=color,
                stroke_width=1.3,
            )
            content.move_to(box.get_center())
            cat_cards.add(VGroup(box, content))

        cat_cards.arrange(RIGHT, buff=0.5)
        cat_cards.next_to(note, DOWN, buff=0.5)

        for card in cat_cards:
            self.play(FadeIn(card, shift=UP * 0.25), run_time=0.4)
            self.wait(0.25)

        self.wait(1.5)

        research_tip = make_label(
            "Tip: Kafka has 200+ connectors via Confluent Hub · JMS connectors are vendor-specific",
            font_size=12,
            color=YELLOW,
        )
        research_tip.to_edge(DOWN, buff=0.4)
        self.play(FadeIn(research_tip))
        self.wait(3)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 10: Deliverables ───────────────────────────────────────
    def scene_deliverables(self):
        header = self._section_header("Deliverables", color=GREEN)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.5)

        items = [
            (ICON_CHART,     ORANGE, "Performance Table",
             "Produce RT · Consume RT · Max Throughput · Median Latency"),
            (ICON_CODE_FILE, BLUE,   "Code Snippets",
             "Measurement code for each metric in both JMS and Kafka"),
            (ICON_CHECKLIST, GREEN,  "Usability Table",
             "Setup steps · Lines of code · API calls per operation"),
            (ICON_BOOK,      PURPLE, "Integrations Summary",
             "Research findings with references for both tools"),
            (ICON_STRUCTURE, TEAL,   "Tool Summary",
             "Advantages & Disadvantages per tool"),
            (ICON_CHECK,     YELLOW, "Conclusion",
             "Recommendation with clear justification"),
        ]

        left_items = items[:3]
        right_items = items[3:]

        def make_item_row(icon, color, title, desc):
            ic = make_icon(icon, color=color, height=0.3)
            lbl = make_label(title, font_size=13, color=color, weight=BOLD)
            d = make_label(desc, font_size=10, color=GREY_B)
            row_content = VGroup(ic, VGroup(lbl, d).arrange(DOWN, buff=0.04)).arrange(
                RIGHT, buff=0.18
            )
            return row_content

        left_vg = VGroup(*[make_item_row(*it) for it in left_items]).arrange(
            DOWN, buff=0.35, aligned_edge=LEFT
        )
        right_vg = VGroup(*[make_item_row(*it) for it in right_items]).arrange(
            DOWN, buff=0.35, aligned_edge=LEFT
        )
        columns = VGroup(left_vg, right_vg).arrange(RIGHT, buff=1.2)
        columns.next_to(header, DOWN, buff=0.55)

        for lrow, rrow in zip(left_vg, right_vg):
            self.play(FadeIn(lrow, shift=RIGHT * 0.2), FadeIn(rrow, shift=RIGHT * 0.2), run_time=0.4)
            self.wait(0.25)

        self.wait(2)

        note = make_label(
            "All members must be ready to answer questions  ·  No copying from other teams",
            font_size=12,
            color=RED,
        )
        note.to_edge(DOWN, buff=0.4)
        self.play(FadeIn(note))
        self.wait(3)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 11: Closing ────────────────────────────────────────────
    def scene_closing(self):
        icon = make_icon(ICON_TRANSFER, color=ORANGE, height=0.9)
        title = make_label("Good luck!", font_size=36, color=WHITE)
        sub1 = make_label(
            "Test both tools · Let data guide your recommendation",
            font_size=17,
            color=GREY_A,
        )
        sub2 = make_label(
            "JMS vs Kafka — the best tool depends on your workload",
            font_size=14,
            color=GREY_B,
        )
        group = VGroup(icon, title, sub1, sub2).arrange(DOWN, buff=0.35)
        self.play(FadeIn(icon, shift=DOWN * 0.2))
        self.wait(0.3)
        self.play(AddTextLetterByLetter(title, time_per_char=0.05))
        self.wait(0.4)
        self.play(FadeIn(sub1, shift=UP * 0.15))
        self.wait(0.4)
        self.play(FadeIn(sub2, shift=UP * 0.15))
        self.wait(4)
        self.play(FadeOut(*self.mobjects))
