import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from manim import (
    BLUE,
    BOLD,
    DOWN,
    GOLD,
    GREEN,
    GREY_A,
    GREY_B,
    LEFT,
    ORANGE,
    ORIGIN,
    PINK,
    PURPLE,
    RED,
    RIGHT,
    TEAL,
    UP,
    WHITE,
    YELLOW,
    AddTextLetterByLetter,
    AnimationGroup,
    Arrow,
    Create,
    DashedLine,
    FadeIn,
    FadeOut,
    GrowArrow,
    Indicate,
    Scene,
    VGroup,
    config,
)

try:
    from manim_slides import Slide as BaseSlide
except Exception:
    BaseSlide = Scene
from libs.ddia_components import (
    ICON_BOOK,
    ICON_CHART,
    ICON_CLOUD,
    ICON_CODE,
    ICON_CODE_FILE,
    ICON_CPU_BOLT,
    ICON_DATABASE,
    ICON_FILE,
    ICON_LAYERS,
    ICON_LIGHTNING,
    ICON_MONITOR,
    ICON_SERVER,
    ICON_SETTINGS,
    ICON_STOPWATCH,
    ICON_STRUCTURE,
    create_rect_glow,
    make_fit_box,
    make_icon,
    make_label,
)
from libs.slide_style import SlideStyleMixin

ICON_KAFKA = "assets/icons/tech/kafka.svg"
ICON_PARQUET = "assets/icons/tech/parquet.svg"
ICON_ES = "assets/icons/tech/elasticsearch.svg"
ICON_KIBANA = "assets/icons/tech/kibana.svg"


config.background_color = "#0D1117"
config.pixel_height = 1080
config.pixel_width = 1920
config.frame_rate = 60


class ProjectWeatherStations(SlideStyleMixin, BaseSlide):
    def construct(self):
        self.scene_title()
        self.scene_overview()
        self.scene_architecture()
        self.scene_weather_station_mock()
        self.scene_kafka_pipeline()
        self.scene_bitcask()
        self.scene_bitcask_client()
        self.scene_archiving_and_kibana()
        self.scene_kubernetes()
        self.scene_jfr_profiling()
        self.scene_deliverables()
        self.scene_bonus()
        self.scene_closing()

    # ─── Helpers ──────────────────────────────────────────────────────

    # ─── Scene 1: Title ───────────────────────────────────────────────
    def scene_title(self):
        icon = make_icon(ICON_CLOUD, color=TEAL, height=1.1)
        title = make_label(
            "Project: Weather Stations Monitoring", font_size=34, color=TEAL
        )
        sub = make_label(
            "IoT Data Streams  ·  Kafka  ·  BitCask  ·  Parquet  ·  Kubernetes",
            font_size=17,
            color=GREY_B,
        )
        course = make_label(
            "Designing Data-Intensive Applications",
            font_size=13,
            color=GREY_B,
        )
        VGroup(icon, title, sub, course).arrange(DOWN, buff=0.4)
        self.play(FadeIn(icon, shift=DOWN * 0.3))
        self.wait(0.4)
        self.play(AddTextLetterByLetter(title, time_per_char=0.04))
        self.wait(0.4)
        self.play(FadeIn(sub, shift=UP * 0.2))
        self.wait(0.3)
        self.play(FadeIn(course, shift=UP * 0.15))
        self.wait(3)
        self._next_slide()
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 2: Overview ────────────────────────────────────────────
    def scene_overview(self):
        header = self._section_header("Overview — IoT Weather Stations", color=TEAL)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.5)

        context = make_label(
            "IoT devices emit high-frequency data streams — weather stations report status every second",
            font_size=13,
            color=GREY_A,
        )
        context.next_to(header, DOWN, buff=0.35)
        self.play(FadeIn(context, shift=UP * 0.1))
        self.wait(0.4)

        items = [
            (
                ICON_LIGHTNING,
                ORANGE,
                "10 Weather Stations",
                "Each emits 1 reading/sec to Kafka — battery status + weather metrics",
            ),
            (
                ICON_SERVER,
                BLUE,
                "1 Central Base Station",
                "Consumes Kafka stream — archives to Parquet, indexes in BitCask",
            ),
            (
                ICON_DATABASE,
                GREEN,
                "2 Index Variants",
                "BitCask (latest per station)  +  ElasticSearch/Kibana (full history)",
            ),
            (
                ICON_CLOUD,
                PURPLE,
                "Kubernetes Cluster",
                "All components containerized — Docker + K8s orchestration",
            ),
        ]
        GLOW = {2}
        rows = VGroup()
        glow_map = {}
        color_map = {}
        for j, (icon_path, color, title, desc) in enumerate(items):
            result = self._icon_row_card(icon_path, color, title, desc, glow=(j in GLOW))
            if isinstance(result, tuple):
                card, g = result
                rows.add(card)
                glow_map[j] = g
                color_map[j] = color
            else:
                rows.add(result)
        rows.arrange(DOWN, buff=0.15, aligned_edge=LEFT).next_to(context, DOWN, buff=0.38)
        for idx, g in glow_map.items():
            g.move_to(rows[idx])

        for i, row in enumerate(rows):
            self.play(FadeIn(row, shift=LEFT * 0.3), run_time=0.45)
            if i in glow_map:
                self._play_glow_row(row, glow_map[i], color_map[i])
            self.wait(0.25)
            if i < len(rows) - 1:
                self._next_slide(phase=True)

        self.wait(2.5)
        self._next_slide()
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 3: Architecture ────────────────────────────────────────
    def scene_architecture(self):
        header = self._section_header("System Architecture", color=ORANGE)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.3)

        # ── Layout constants ─────────────────────────────────────────
        DIV1_X, DIV2_X = -1.8, 3.0
        SEC1_X, SEC2_X, SEC3_X = -4.8, 0.7, 5.2
        MAIN_Y, HDR_Y = 0.1, 2.2

        # ── Section labels + dividers ────────────────────────────────
        sec_labels = VGroup(
            make_label("Data Acquisition", font_size=13, color=ORANGE),
            make_label("Data Processing\n& Archiving", font_size=13, color=BLUE),
            make_label("Indexing", font_size=13, color=GREEN),
        )
        sec_labels[0].move_to([SEC1_X, HDR_Y, 0])
        sec_labels[1].move_to([SEC2_X, HDR_Y, 0])
        sec_labels[2].move_to([SEC3_X, HDR_Y, 0])

        div1 = DashedLine(
            [DIV1_X, HDR_Y + 0.6, 0],
            [DIV1_X, -3.4, 0],
            color=GREY_B,
            stroke_width=0.9,
            dash_length=0.13,
        )
        div2 = DashedLine(
            [DIV2_X, HDR_Y + 0.6, 0],
            [DIV2_X, -3.4, 0],
            color=GREY_B,
            stroke_width=0.9,
            dash_length=0.13,
        )

        self.play(FadeIn(sec_labels))
        self.play(Create(div1), Create(div2))
        self.wait(0.3)
        self._next_slide(phase=True)

        # ── Helper: icon node (icon above, label below) ──────────────

        def arch_node(icon_path, label, color, icon_h=0.48):
            ic = make_icon(icon_path, color=color, height=icon_h)
            lbl = make_label(label, font_size=11, color=color)
            return VGroup(ic, lbl).arrange(DOWN, buff=0.1)

        # ── Section 1: Weather Stations ──────────────────────────────
        st1  = arch_node(ICON_CPU_BOLT, "Station 1",  BLUE, icon_h=0.4)
        st2  = arch_node(ICON_CPU_BOLT, "Station 2",  BLUE, icon_h=0.4)
        st3  = arch_node(ICON_CPU_BOLT, "Station 3",  BLUE, icon_h=0.4)
        dots = make_label("·\n·\n·", font_size=14, color=GREY_B)
        st10 = arch_node(ICON_CPU_BOLT, "Station 10", BLUE, icon_h=0.4)
        station_col = VGroup(st1, st2, st3, dots, st10)
        station_col.arrange(DOWN, buff=0.22).move_to([SEC1_X - 1.0, MAIN_Y, 0])
        station_nodes = [st1, st2, st3, st10]

        for item in station_col:
            self.play(FadeIn(item, shift=RIGHT * 0.12), run_time=0.22)
        self.wait(0.2)

        # ── Kafka ────────────────────────────────────────────────────
        kafka_node = arch_node(ICON_KAFKA, "Kafka", WHITE, icon_h=0.52)
        kafka_node.move_to([DIV1_X - 0.9, MAIN_Y, 0])
        self.play(FadeIn(kafka_node, shift=RIGHT * 0.2))

        kafka_arrows = VGroup(
            *[
                Arrow(
                    st.get_right(),
                    kafka_node.get_left(),
                    buff=0.1,
                    stroke_width=1.4,
                    color=GREY_B,
                    tip_length=0.11,
                )
                for st in station_nodes
            ]
        )
        self.play(AnimationGroup(*[GrowArrow(a) for a in kafka_arrows], lag_ratio=0.12))
        self.wait(0.3)
        self._next_slide(phase=True)

        # ── Base Central Station ─────────────────────────────────────
        bcs_node = arch_node(ICON_SERVER, "Base Central\nStation", BLUE, icon_h=0.5)
        bcs_node.move_to([SEC2_X - 0.4, MAIN_Y, 0])

        k2bcs = Arrow(
            kafka_node.get_right(),
            bcs_node.get_left(),
            buff=0.1,
            stroke_width=2.0,
            color=ORANGE,
            tip_length=0.15,
        )
        self.play(GrowArrow(k2bcs))
        self.play(FadeIn(bcs_node, shift=RIGHT * 0.2))
        self.wait(0.3)
        self._next_slide(phase=True)

        # ── Parquet Files (below BCS) ────────────────────────────────
        parquet_node = arch_node(ICON_PARQUET, "Parquet Files", TEAL, icon_h=0.48)
        parquet_node.move_to([SEC2_X + 0.6, -2.0, 0])

        bcs2parquet = Arrow(
            bcs_node.get_bottom(),
            parquet_node.get_top(),
            buff=0.1,
            stroke_width=1.7,
            color=BLUE,
            tip_length=0.13,
        )
        self.play(GrowArrow(bcs2parquet))
        self.play(FadeIn(parquet_node, shift=DOWN * 0.2))
        self.wait(0.2)

        # ── Bitcask Store (top-right) ────────────────────────────────
        bitcask_node = arch_node(ICON_DATABASE, "Bitcask Store", BLUE, icon_h=0.48)
        bitcask_node.move_to([SEC3_X - 0.7, 0.9, 0])

        bcs2bitcask = Arrow(
            bcs_node.get_right(),
            bitcask_node.get_left(),
            buff=0.1,
            stroke_width=1.7,
            color=BLUE,
            tip_length=0.13,
        )
        self.play(GrowArrow(bcs2bitcask))
        self.play(FadeIn(bitcask_node, shift=RIGHT * 0.2))
        self.wait(0.3)
        self._next_slide(phase=True)

        # ── Elasticsearch + Kibana ────────────────────────────────────
        es_node = arch_node(ICON_ES, "elasticsearch", YELLOW, icon_h=0.48)
        kibana_node = arch_node(ICON_KIBANA, "Kibana", PINK, icon_h=0.48)
        VGroup(es_node, kibana_node).arrange(RIGHT, buff=0.3).move_to(
            [SEC3_X + 0.3, -1.1, 0]
        )

        p2es = Arrow(
            parquet_node.get_right(),
            es_node.get_left(),
            buff=0.1,
            stroke_width=1.7,
            color=TEAL,
            tip_length=0.13,
        )

        self.play(
            FadeIn(es_node, shift=RIGHT * 0.2), FadeIn(kibana_node, shift=RIGHT * 0.2)
        )
        self.play(GrowArrow(p2es))

        cluster_note = make_label(
            "All components run inside a Kubernetes cluster", font_size=12, color=PURPLE
        )
        cluster_note.to_edge(DOWN, buff=0.35)
        self.play(FadeIn(cluster_note, shift=UP * 0.1))
        self.wait(3.5)
        self._next_slide()
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 4: Weather Station Mock ───────────────────────────────
    def scene_weather_station_mock(self):
        header = self._section_header("Weather Station Mock", color=ORANGE)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.5)

        schema_lines = [
            "{",
            '  "station_id": <long>,',
            '  "s_no": <long>,           // auto-incremental per station',
            '  "battery_status": "low" | "medium" | "high",',
            '  "status_timestamp": <epoch_ms>,',
            '  "weather": {',
            '    "humidity": <int>,      // percentage',
            '    "temperature": <int>,   // fahrenheit',
            '    "wind_speed": <int>     // km/h',
            "  }",
            "}",
        ]
        schema_box = self._code_box(
            schema_lines,
            "Weather Status Message (JSON)",
            ORANGE,
            width=6.2,
            font_size=9,
        )
        self._next_slide(
            phase=True, notes="Schema shown; discuss fields before distribution"
        )

        # Battery distribution card — right of schema
        dist_title = make_label(
            "Battery Status Distribution", font_size=13, color=YELLOW
        )
        dist_rows = VGroup(
            make_label("Low      =  30 %", font_size=12, color=RED),
            make_label("Medium  =  40 %", font_size=12, color=ORANGE),
            make_label("High      =  30 %", font_size=12, color=GREEN),
        ).arrange(DOWN, buff=0.18, aligned_edge=LEFT)
        dist_content = VGroup(dist_title, dist_rows).arrange(
            DOWN, buff=0.2, aligned_edge=LEFT
        )
        dist_group = make_fit_box(dist_content, YELLOW, pad_x=0.7, pad_y=0.5)

        mock_row = VGroup(schema_box, dist_group).arrange(RIGHT, buff=0.5)
        mock_row.next_to(header, DOWN, buff=0.45)
        self.play(FadeIn(schema_box, shift=LEFT * 0.3))
        self.wait(0.5)
        self.play(FadeIn(dist_group, shift=RIGHT * 0.3))
        self.wait(0.5)

        drop_lbl = make_label(
            "⚠  Randomly DROP 10 % of messages — simulates network loss",
            font_size=13,
            color=RED,
        )
        drop_lbl.to_edge(DOWN, buff=0.45)
        self.play(FadeIn(drop_lbl, shift=UP * 0.15))
        self.play(Indicate(drop_lbl, color=RED, run_time=1.2))
        self.wait(3.5)
        self._next_slide()
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 5: Kafka Pipeline ──────────────────────────────────────
    def scene_kafka_pipeline(self):
        header = self._section_header(
            "Kafka Pipeline — Producer + Processor", color=BLUE
        )
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.5)

        # Top row: Station → Kafka → Central
        station = self._flow_node("Weather\nStation", ORANGE, width=2.1, height=0.9)
        kafka = self._flow_node("Kafka\nTopic", TEAL, width=2.1, height=0.9)
        central = self._flow_node("Central\nStation", BLUE, width=2.1, height=0.9)
        VGroup(station, kafka, central).arrange(RIGHT, buff=1.2).move_to(UP * 1.3)

        a1 = self._flow_arrow(station, kafka, ORANGE, "produce")
        a2 = self._flow_arrow(kafka, central, TEAL, "consume")

        # Bottom row: Processor → Rain Topic
        processor = self._flow_node("Kafka\nProcessor", PURPLE, width=2.1, height=0.9)
        rain_topic = self._flow_node("Rain Alerts\nTopic", RED, width=2.4, height=0.9)
        processor.next_to(kafka, DOWN, buff=1.1)
        rain_topic.next_to(processor, RIGHT, buff=1.1)

        a3 = Arrow(
            kafka.get_bottom(),
            processor.get_top(),
            buff=0.1,
            stroke_width=1.8,
            color=PURPLE,
            tip_length=0.13,
        )
        a4 = self._flow_arrow(processor, rain_topic, RED, "hum>70%", label_dir=DOWN)

        self.play(
            AnimationGroup(
                FadeIn(station), FadeIn(kafka), FadeIn(central), lag_ratio=0.2
            )
        )
        self.play(GrowArrow(a1[0]), FadeIn(a1[1]))
        self.play(GrowArrow(a2[0]), FadeIn(a2[1]))
        self.wait(0.5)

        self.play(FadeIn(processor, shift=DOWN * 0.15))
        proc_glow = create_rect_glow(processor, color=PURPLE, max_opacity=0.22, spread=0.3)
        self.add(proc_glow)
        proc_glow.set_opacity(0)
        self.bring_to_back(proc_glow)
        self.play(FadeIn(proc_glow), run_time=0.4)
        self.play(GrowArrow(a3))
        self.play(FadeIn(rain_topic, shift=RIGHT * 0.15))
        self.play(GrowArrow(a4[0]), FadeIn(a4[1]))
        self.wait(0.5)
        self._next_slide(
            phase=True, notes="Pipeline flow shown; discuss processor implementation"
        )

        notes = VGroup(
            make_label(
                "✓  Java Kafka Producer API — send() to main topic",
                font_size=12,
                color=GREEN,
            ),
            make_label(
                "✓  Kafka Processor (or Kafka DSL) — filter humidity > 70 % → rain alert topic",
                font_size=12,
                color=GREEN,
            ),
            make_label(
                "✓  Try simple producer example first — confirm output before integrating",
                font_size=12,
                color=YELLOW,
            ),
        ).arrange(DOWN, buff=0.14, aligned_edge=LEFT)
        notes.to_edge(DOWN, buff=0.42)
        self.play(FadeIn(notes, shift=UP * 0.1))
        self.wait(3.5)
        self._next_slide()
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 6: BitCask ─────────────────────────────────────────────
    def scene_bitcask(self):
        header = self._section_header("Central Station — BitCask Riak", color=GREEN)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.5)

        desc = make_label(
            "Key-value store — key = station_id  ·  value = latest weather status",
            font_size=13,
            color=GREY_A,
        )
        desc.next_to(header, DOWN, buff=0.35)
        self.play(FadeIn(desc))
        self.wait(0.4)

        impl_items = [
            (
                ICON_FILE,
                GREEN,
                "Segment Files",
                "Append-only log files — each write appended to the active segment",
            ),
            (
                ICON_CODE_FILE,
                TEAL,
                "Hint Files  (required)",
                "Index of key → (file_id, offset, size) — mandatory for fast crash recovery",
            ),
            (
                ICON_SETTINGS,
                ORANGE,
                "Compaction",
                "Scheduled merge of segment files — removes stale keys, non-disruptive to readers",
            ),
            (
                ICON_STRUCTURE,
                BLUE,
                "In-Memory KeyDir",
                "Hash table maps every key to latest value location — O(1) reads",
            ),
        ]
        GLOW = {1, 2}
        rows = VGroup()
        glow_map = {}
        color_map = {}
        for j, (icon_path, color, title, desc_text) in enumerate(impl_items):
            result = self._icon_row_card(icon_path, color, title, desc_text, glow=(j in GLOW))
            if isinstance(result, tuple):
                card, g = result
                rows.add(card)
                glow_map[j] = g
                color_map[j] = color
            else:
                rows.add(result)
        rows.arrange(DOWN, buff=0.15, aligned_edge=LEFT).next_to(desc, DOWN, buff=0.35)
        for idx, g in glow_map.items():
            g.move_to(rows[idx])

        for i, row in enumerate(rows):
            self.play(FadeIn(row, shift=LEFT * 0.3), run_time=0.4)
            if i in glow_map:
                self._play_glow_row(row, glow_map[i], color_map[i])
            self.wait(0.3)
            if i < len(rows) - 1:
                self._next_slide(phase=True)

        not_required = make_label(
            "NOT required: checksums  ·  tombstone deletions",
            font_size=12,
            color=GREY_B,
        )
        not_required.to_edge(DOWN, buff=0.45)
        self.play(FadeIn(not_required, shift=UP * 0.1))
        self.wait(3)
        self._next_slide()
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 6b: BitCask Client ─────────────────────────────────────
    def scene_bitcask_client(self):
        header = self._section_header("BitCask Client — bash / Python", color=GREEN)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.4)

        client_items = [
            (
                "--view-all",
                "Print all keys + latest values → CSV file named <timestamp>.csv  (cols: key, value)",
            ),
            ("--view --key=X", "Print to stdout the value for key X"),
            (
                "--perf --clients=100",
                "Launch 100 threads — each queries all keys → CSV with thread number appended to timestamp",
            ),
        ]
        rows = VGroup()
        for cmd, desc_text in client_items:
            cmd_lbl = make_label(
                f"./bitcask_client.sh  {cmd}", font_size=12, color=TEAL
            )
            desc_lbl = make_label(desc_text, font_size=11, color=GREY_A)
            content = VGroup(cmd_lbl, desc_lbl).arrange(
                DOWN, buff=0.1, aligned_edge=LEFT
            )
            rows.add(make_fit_box(content, TEAL, pad_x=0.85, pad_y=0.38))
        rows.arrange(DOWN, buff=0.18, aligned_edge=LEFT).next_to(header, DOWN, buff=0.5)

        for i, row in enumerate(rows):
            self.play(FadeIn(row, shift=LEFT * 0.3), run_time=0.45)
            self.wait(0.4)
            if i < len(rows) - 1:
                self._next_slide(phase=True)

        use_note = make_label(
            "Used by TAs during discussion — BitCask correctness verified via this client",
            font_size=13,
            color=YELLOW,
        )
        use_note.to_edge(DOWN, buff=0.45)
        self.play(FadeIn(use_note, shift=UP * 0.1))
        self.wait(3.5)
        self._next_slide()
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 7: Archiving + Kibana ─────────────────────────────────
    def scene_archiving_and_kibana(self):
        header = self._section_header("Archiving + Historical Analysis", color=BLUE)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.5)

        parquet_items = [
            (
                ICON_LAYERS,
                BLUE,
                "Parquet Files",
                "Archive all statuses — partitioned by time and station_id",
            ),
            (
                ICON_CODE,
                TEAL,
                "Batch Writes",
                "Write in batches of ~10 000 records — avoids frequent IO blocking",
            ),
            (
                ICON_CHART,
                ORANGE,
                "ElasticSearch / Kibana",
                "Connect Parquet as data source → index via ES → visualize via Kibana",
            ),
        ]
        GLOW = {1, 2}
        rows = VGroup()
        glow_map = {}
        color_map = {}
        for j, (icon_path, color, title, desc_text) in enumerate(parquet_items):
            result = self._icon_row_card(icon_path, color, title, desc_text, glow=(j in GLOW))
            if isinstance(result, tuple):
                card, g = result
                rows.add(card)
                glow_map[j] = g
                color_map[j] = color
            else:
                rows.add(result)
        rows.arrange(DOWN, buff=0.18, aligned_edge=LEFT).next_to(header, DOWN, buff=0.45)
        for idx, g in glow_map.items():
            g.move_to(rows[idx])

        for i, row in enumerate(rows):
            self.play(FadeIn(row, shift=LEFT * 0.3), run_time=0.45)
            if i in glow_map:
                self._play_glow_row(row, glow_map[i], color_map[i])
            self.wait(0.35)
            if i < len(rows) - 1:
                self._next_slide(phase=True)

        self.wait(0.4)
        self._next_slide(phase=True)

        kibana_title = make_label(
            "Required Kibana Visualizations", font_size=14, color=YELLOW
        )
        kibana_rows = VGroup(
            make_label(
                "▸  Count of low-battery statuses per station  (should confirm ~30 %)",
                font_size=12,
                color=GREEN,
            ),
            make_label(
                "▸  Count of dropped messages per station  (should confirm ~10 %)",
                font_size=12,
                color=RED,
            ),
        ).arrange(DOWN, buff=0.14, aligned_edge=LEFT)
        kib_group = VGroup(kibana_title, kibana_rows).arrange(
            DOWN, buff=0.18, aligned_edge=LEFT
        )
        kib_group.to_edge(DOWN, buff=0.45)
        self.play(FadeIn(kib_group, shift=UP * 0.1))
        self.wait(3.5)
        self._next_slide()
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 8: Kubernetes Deployment ──────────────────────────────
    def scene_kubernetes(self):
        header = self._section_header("Deployment — Docker + Kubernetes", color=PURPLE)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.5)

        k8s_items = [
            (
                ICON_CODE_FILE,
                ORANGE,
                "Dockerfile — Weather Station",
                "Containerize the station mock — used for 10 K8s service replicas",
            ),
            (
                ICON_CODE_FILE,
                BLUE,
                "Dockerfile — Central Station",
                "Containerize the Java central server",
            ),
            (
                ICON_LAYERS,
                PURPLE,
                "K8s yaml — Full Cluster",
                "10× station  ·  1× central  ·  Kafka + Zookeeper  ·  Elastic + Kibana",
            ),
            (
                ICON_DATABASE,
                GREEN,
                "Shared Persistent Volume",
                "Mounted storage for Parquet files + BitCask segment files across pods",
            ),
        ]
        GLOW = {2}
        rows = VGroup()
        glow_map = {}
        color_map = {}
        for j, (icon_path, color, title, desc_text) in enumerate(k8s_items):
            result = self._icon_row_card(icon_path, color, title, desc_text, glow=(j in GLOW))
            if isinstance(result, tuple):
                card, g = result
                rows.add(card)
                glow_map[j] = g
                color_map[j] = color
            else:
                rows.add(result)
        rows.arrange(DOWN, buff=0.18, aligned_edge=LEFT).next_to(header, DOWN, buff=0.45)
        for idx, g in glow_map.items():
            g.move_to(rows[idx])

        for i, row in enumerate(rows):
            self.play(FadeIn(row, shift=LEFT * 0.3), run_time=0.45)
            if i in glow_map:
                self._play_glow_row(row, glow_map[i], color_map[i])
            self.wait(0.35)
            if i < len(rows) - 1:
                self._next_slide(phase=True)

        self.wait(3)
        self._next_slide()
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 9: JFR Profiling ───────────────────────────────────────
    def scene_jfr_profiling(self):
        header = self._section_header(
            "Profile Central Station — Java Flight Recorder", color=YELLOW
        )
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.5)

        intro = make_label(
            "JFR: built into JVM  ·  near-zero overhead  ·  diagnostic + profiling data",
            font_size=13,
            color=GREY_A,
        )
        intro.next_to(header, DOWN, buff=0.35)
        self.play(FadeIn(intro))
        self.wait(0.4)

        metrics = [
            (
                ICON_MONITOR,
                ORANGE,
                "Top 10 Classes by Memory",
                "Highest total heap allocated — reveals memory-hungry objects",
            ),
            (
                ICON_STOPWATCH,
                RED,
                "GC Pauses Count",
                "Number of garbage collection stop-the-world events in a 1-minute run",
            ),
            (
                ICON_STOPWATCH,
                YELLOW,
                "GC Maximum Pause Duration",
                "Longest single GC pause — indicator of latency spikes",
            ),
            (
                ICON_CHART,
                BLUE,
                "List of I/O Operations",
                "File reads/writes during the run — confirms Parquet + BitCask IO patterns",
            ),
        ]
        GLOW = {0}
        rows = VGroup()
        glow_map = {}
        color_map = {}
        for j, (icon_path, color, title, desc_text) in enumerate(metrics):
            result = self._icon_row_card(icon_path, color, title, desc_text, glow=(j in GLOW))
            if isinstance(result, tuple):
                card, g = result
                rows.add(card)
                glow_map[j] = g
                color_map[j] = color
            else:
                rows.add(result)
        rows.arrange(DOWN, buff=0.15, aligned_edge=LEFT).next_to(intro, DOWN, buff=0.35)
        for idx, g in glow_map.items():
            g.move_to(rows[idx])

        for i, row in enumerate(rows):
            self.play(FadeIn(row, shift=LEFT * 0.3), run_time=0.4)
            if i in glow_map:
                self._play_glow_row(row, glow_map[i], color_map[i])
            self.wait(0.3)
            if i < len(rows) - 1:
                self._next_slide(phase=True)

        run_note = make_label(
            "Run full system for 1 minute → record JFR snapshot → include report",
            font_size=13,
            color=GREEN,
        )
        run_note.to_edge(DOWN, buff=0.45)
        self.play(FadeIn(run_note, shift=UP * 0.15))
        self.wait(3.5)
        self._next_slide()
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 10: Deliverables ───────────────────────────────────────
    def scene_deliverables(self):
        header = self._section_header("Deliverables", color=GREEN)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.5)

        items = [
            (
                ICON_CODE,
                TEAL,
                "Source Code",
                "Full implementation — stations, central station, processors",
            ),
            (
                ICON_CODE_FILE,
                ORANGE,
                "Docker & K8s Files",
                "Dockerfile (station)  ·  Dockerfile (central)  ·  K8s yaml",
            ),
            (
                ICON_CHART,
                BLUE,
                "Kibana Screenshots",
                "Battery distribution (30/40/30)  ·  10 % dropped messages — verified",
            ),
            (
                ICON_FILE,
                PURPLE,
                "Sample Parquet File",
                "Example output demonstrating time + station_id partitioned archiving",
            ),
            (
                ICON_DATABASE,
                GREEN,
                "Sample BitCask LSM Directory",
                "Segment files + hint files snapshot",
            ),
            (
                ICON_BOOK,
                YELLOW,
                "Report",
                "Contains all of the above — JFR profiling output included",
            ),
        ]
        rows = VGroup()
        for icon_path, color, title, desc_text in items:
            rows.add(self._icon_row_card(icon_path, color, title, desc_text))
        rows.arrange(DOWN, buff=0.12, aligned_edge=LEFT).next_to(header, DOWN, buff=0.42)

        for i, row in enumerate(rows):
            self.play(FadeIn(row, shift=LEFT * 0.3), run_time=0.38)
            self.wait(0.28)
            if i < len(rows) - 1:
                self._next_slide(phase=True)

        note = make_label(
            "Groups of 4  ·  All members must be ready to answer questions  ·  No copying",
            font_size=13,
            color=RED,
        )
        note.to_edge(DOWN, buff=0.45)
        self.play(FadeIn(note, shift=UP * 0.1))
        self.wait(3)
        self._next_slide(phase=True)

        # ── Working Application finale ────────────────────────────────
        self.play(FadeOut(header, rows, note), run_time=0.7)

        finale_title = make_label("Working Application", font_size=40, color=GOLD)
        finale_sub = make_label(
            "End-to-end system — Stations · Kafka · BitCask · Parquet · ES/Kibana · K8s",
            font_size=16,
            color=GREY_A,
        )
        finale_content = VGroup(finale_title, finale_sub).arrange(
            DOWN, buff=0.3, aligned_edge=LEFT
        )
        finale_box, finale_glow = make_fit_box(
            finale_content, GOLD, pad_x=1.4, pad_y=0.9, align="center",
            glow=True, glow_opacity=0.35, glow_spread=0.55,
        )
        finale_box.move_to(ORIGIN)
        finale_glow.move_to(finale_box)
        self.play(FadeIn(finale_box, scale=0.85), run_time=1.2)
        self._play_glow_row(finale_box, finale_glow, GOLD)
        self.wait(4)
        self._next_slide()
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 11: Bonus ──────────────────────────────────────────────
    def scene_bonus(self):
        header = self._section_header("Bonus", color=PINK)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.5)

        # Open-Meteo block
        meteo_title = make_label("Open-Meteo Integration", font_size=15, color=TEAL)
        meteo_desc = make_label(
            "Integrate with open-meteo.com — free open-source weather API\n"
            "Collect real weather data and feed it into Kafka alongside station mocks\n"
            "Requires implementing a Channel Adapter pattern",
            font_size=12,
            color=GREY_A,
        )
        meteo_content = VGroup(meteo_title, meteo_desc).arrange(
            DOWN, buff=0.12, aligned_edge=LEFT
        )
        meteo_group = make_fit_box(meteo_content, TEAL, pad_x=0.85, pad_y=0.44)
        meteo_group.next_to(header, DOWN, buff=0.45)

        self.play(FadeIn(meteo_group, shift=LEFT * 0.3))
        self.wait(0.5)
        self._next_slide(phase=True, notes="Open-Meteo shown; move to EIP patterns")

        # EIP patterns block
        eip_title = make_label(
            "Enterprise Integration Patterns  (5–6 patterns required)",
            font_size=15,
            color=ORANGE,
        )
        patterns = [
            (
                "Dead-Letter Channel",
                RED,
                "Route unprocessable messages to a side channel",
            ),
            ("Claim Check", BLUE, "Store large payloads externally, pass only a token"),
            (
                "Invalid-Message Channel",
                ORANGE,
                "Separate invalid-format messages from main flow",
            ),
            ("Polling Consumer", GREEN, "Pull from queue at regular intervals"),
            ("Idempotent Receiver", TEAL, "Safely re-process duplicate messages"),
            (
                "Envelope Wrapper",
                PURPLE,
                "Wrap message with metadata before publishing",
            ),
        ]
        pattern_rows = VGroup()
        for name, color, hint in patterns:
            n_lbl = make_label(f"▸  {name}", font_size=12, color=color, weight=BOLD)
            h_lbl = make_label(hint, font_size=11, color=GREY_A)
            row = VGroup(n_lbl, h_lbl).arrange(RIGHT, buff=0.35)
            pattern_rows.add(row)
        pattern_rows.arrange(DOWN, buff=0.14, aligned_edge=LEFT)

        eip_content = VGroup(eip_title, pattern_rows).arrange(
            DOWN, buff=0.18, aligned_edge=LEFT
        )
        eip_group = make_fit_box(eip_content, ORANGE, pad_x=0.85, pad_y=0.44)
        eip_group.next_to(meteo_group, DOWN, buff=0.28)

        self.play(FadeIn(eip_group, shift=LEFT * 0.3))
        self.wait(3.5)
        self._next_slide()
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 12: Closing ────────────────────────────────────────────
    def scene_closing(self):
        icon = make_icon(ICON_CLOUD, color=TEAL, height=0.9)
        title = make_label("Good luck!", font_size=38, color=WHITE)
        sub1 = make_label(
            "Build the pipeline  ·  Index the data  ·  Containerize everything",
            font_size=17,
            color=GREY_A,
        )
        sub2 = make_label(
            "Stations → Kafka → Central Station → BitCask + Parquet → Kibana",
            font_size=14,
            color=GREY_B,
        )
        VGroup(icon, title, sub1, sub2).arrange(DOWN, buff=0.38)
        self.play(FadeIn(icon, shift=DOWN * 0.2))
        self.wait(0.3)
        self.play(AddTextLetterByLetter(title, time_per_char=0.05))
        self.wait(0.4)
        self.play(FadeIn(sub1, shift=UP * 0.15))
        self.wait(0.4)
        self.play(FadeIn(sub2, shift=UP * 0.15))
        self.wait(4)
        self._next_slide()
        self.play(FadeOut(*self.mobjects))
