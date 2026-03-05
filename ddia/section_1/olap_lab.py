import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from manim import *

from libs.ddia_components import (
    DARK_BG, CARD_BG,
    ICON_DATABASE, ICON_SERVER, ICON_SEARCH, ICON_CHECK,
    ICON_SETTINGS, ICON_STOPWATCH,
    ICON_FILE, ICON_CODE_FILE, ICON_CHART, ICON_STRUCTURE,
    ICON_LAYERS, ICON_TRANSFER,
    ICON_LIGHTNING, ICON_BOOK,
    make_label, make_card, make_icon, make_icon_card, make_code_text,
)

config.background_color = "#0D1117"


class OlapLab(Scene):
    def construct(self):
        self.scene_title()
        self.scene_lab_overview()
        self.scene_oltp_vs_olap()
        self.scene_tpch_data()
        self.scene_what_is_etl()
        self.scene_apache_nifi()
        self.scene_nifi_pipeline()
        self.scene_parquet()
        self.scene_star_schema()
        self.scene_sql_query()
        self.scene_deliverables()
        self.scene_closing()

    # ─── Scene 1: Title ───────────────────────────────────────────────
    def scene_title(self):
        icon = make_icon(ICON_DATABASE, color=BLUE, height=1.2)
        title = make_label("Lab 1: OLAP", font_size=44, color=BLUE)
        subtitle = make_label(
            "OLAP · ETL · Star Schema · Parquet",
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

    # ─── Scene 2: Lab Overview ────────────────────────────────────────
    def scene_lab_overview(self):
        header = make_label("What Will You Do?", font_size=30, color=GREEN)
        header.to_edge(UP, buff=0.5)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(1)

        steps = [
            (ICON_DATABASE, BLUE, "Step 1: Import TPC-H",
             "Generate TPC-H data (SF=1) and load into MySQL"),
            (ICON_TRANSFER, ORANGE, "Step 2: Build NiFi Pipeline",
             "ETL from relational MySQL to Parquet files"),
            (ICON_STRUCTURE, GREEN, "Step 3: Star Schema",
             "Transform normalized schema to star schema inside NiFi"),
            (ICON_CHART, PURPLE, "Step 4: Query & Compare",
             "Run the same query on MySQL and Spark, compare 8 runs"),
        ]

        rows = VGroup()
        for icon_path, color, title, desc in steps:
            icon = make_icon(icon_path, color=color, height=0.3)
            t = make_label(title, font_size=15, color=color, weight=BOLD)
            d = make_label(desc, font_size=11, color=GREY_A)
            row_content = VGroup(icon, t, d).arrange(RIGHT, buff=0.15)
            box = RoundedRectangle(
                corner_radius=0.1, width=10.5, height=0.65,
                fill_color=DARK_BG, fill_opacity=0.9,
                stroke_color=color, stroke_width=1.2,
            )
            row_content.move_to(box.get_center())
            rows.add(VGroup(box, row_content))

        rows.arrange(DOWN, buff=0.15).next_to(header, DOWN, buff=0.5)

        for row in rows:
            self.play(FadeIn(row, shift=LEFT * 0.3), run_time=0.5)
            self.wait(0.8)

        self.wait(1)

        # Bottom note
        note = make_label(
            "Groups of 4 — Be ready to demo during discussion!",
            font_size=18, color=YELLOW,
        )
        note.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(note, shift=UP * 0.2))
        self.wait(3)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 3: OLTP vs OLAP ───────────────────────────────────────
    def scene_oltp_vs_olap(self):
        header = make_label("OLTP vs OLAP", font_size=30, color=ORANGE)
        header.to_edge(UP, buff=0.5)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(1)

        # ── Left: OLTP ──
        left_icon = make_icon(ICON_SERVER, color=GREY_A, height=0.6)
        left_title = make_label("OLTP", font_size=22, color=GREY_A)
        left_sub = make_label("Online Transactional Processing", font_size=11, color=GREY_B)
        left_bullets = VGroup(
            make_label("• Row-level operations", font_size=13, color=GREY_B),
            make_label("• Optimized for writes", font_size=13, color=GREY_B),
            make_label("• 3NF normalized schema", font_size=13, color=GREY_B),
            make_label("• MySQL, PostgreSQL", font_size=13, color=GREY_B),
        ).arrange(DOWN, buff=0.1, aligned_edge=LEFT)

        left_content = VGroup(left_icon, left_title, left_sub, left_bullets).arrange(DOWN, buff=0.15)
        left_box = RoundedRectangle(
            corner_radius=0.15, width=4.5, height=3.6,
            fill_color=DARK_BG, fill_opacity=0.9, stroke_color=GREY_B, stroke_width=1.5,
        )
        left_content.move_to(left_box.get_center())
        left_group = VGroup(left_box, left_content).move_to(LEFT * 3 + DOWN * 0.3)

        # ── Right: OLAP ──
        right_icon = make_icon(ICON_CHART, color=BLUE, height=0.6)
        right_title = make_label("OLAP", font_size=22, color=BLUE)
        right_sub = make_label("Online Analytical Processing", font_size=11, color=BLUE_B)
        right_bullets = VGroup(
            make_label("• Aggregations & groupings", font_size=13, color=BLUE_B),
            make_label("• Optimized for reads", font_size=13, color=BLUE_B),
            make_label("• Star schema", font_size=13, color=BLUE_B),
            make_label("• Spark, Hive, BigQuery", font_size=13, color=BLUE_B),
        ).arrange(DOWN, buff=0.1, aligned_edge=LEFT)

        right_content = VGroup(right_icon, right_title, right_sub, right_bullets).arrange(DOWN, buff=0.15)
        right_box = RoundedRectangle(
            corner_radius=0.15, width=4.5, height=3.6,
            fill_color=DARK_BG, fill_opacity=0.9, stroke_color=BLUE, stroke_width=1.5,
        )
        right_content.move_to(right_box.get_center())
        right_group = VGroup(right_box, right_content).move_to(RIGHT * 3 + DOWN * 0.3)

        self.play(FadeIn(left_group, shift=RIGHT * 0.3))
        self.wait(1.5)
        self.play(FadeIn(right_group, shift=LEFT * 0.3))
        self.wait(2)

        # VS label
        vs_label = make_label("VS", font_size=28, color=ORANGE)
        vs_label.move_to(ORIGIN + DOWN * 0.3)
        self.play(FadeIn(vs_label, scale=1.5))
        self.wait(1)

        # Bottom highlight
        highlight = make_label(
            "Convert OLTP schema → OLAP Star Schema for analytics!",
            font_size=20, color=YELLOW,
        )
        highlight.to_edge(DOWN, buff=0.5)
        self.play(AddTextLetterByLetter(highlight, time_per_char=0.03))
        self.wait(3)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 4: TPC-H Benchmark Data ───────────────────────────────
    def scene_tpch_data(self):
        header = make_label("TPC-H Benchmark Data", font_size=30, color=PURPLE)
        header.to_edge(UP, buff=0.5)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(1)

        # Description
        desc = make_label(
            "A standard benchmark database for decision-support queries",
            font_size=18, color=YELLOW,
        )
        desc.next_to(header, DOWN, buff=0.4)
        self.play(FadeIn(desc, shift=UP * 0.2))
        self.wait(2)

        # Tables with sizes — width proportional to row count
        table_data = [
            ("nation", "5 rows", BLUE, 2.0),
            ("supplier", "10,000 rows", TEAL, 3.0),
            ("customer", "150,000 rows", GREEN, 4.5),
            ("partsupp", "300,000 rows", ORANGE, 6.0),
            ("orders", "1,500,000 rows", PURPLE, 8.0),
            ("lineitem", "6,000,000 rows", RED, 10.5),
        ]

        layers = VGroup()
        for name, size, color, width in table_data:
            lbl = make_label(f"{name}  —  {size}", font_size=12, color=color)
            box = RoundedRectangle(
                corner_radius=0.08, width=width, height=0.45,
                fill_color=DARK_BG, fill_opacity=0.9,
                stroke_color=color, stroke_width=1.5,
            )
            lbl.move_to(box.get_center())
            layers.add(VGroup(box, lbl))

        layers.arrange(DOWN, buff=0.08).move_to(DOWN * 0.5)

        for layer in layers:
            self.play(FadeIn(layer, shift=UP * 0.2), run_time=0.4)
            self.wait(0.4)

        self.wait(1)

        # Scale factor note
        sf_note = make_label("Scale Factor = 1", font_size=16, color=GREY_A)
        sf_note.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(sf_note, shift=UP * 0.2))
        self.wait(3)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 5: What is ETL? ────────────────────────────────────────
    def scene_what_is_etl(self):
        header = make_label("ETL: Extract, Transform, Load", font_size=30, color=GREEN)
        header.to_edge(UP, buff=0.5)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(1)

        # Three cards with arrows between them
        extract_card = make_icon_card(
            "Extract", ICON_DATABASE,
            color=BLUE, width=2.4, height=1.8, font_size=14,
        )
        transform_card = make_icon_card(
            "Transform", ICON_TRANSFER,
            color=ORANGE, width=2.4, height=1.8, font_size=14,
        )
        load_card = make_icon_card(
            "Load", ICON_FILE,
            color=GREEN, width=2.4, height=1.8, font_size=14,
        )

        cards = VGroup(extract_card, transform_card, load_card)
        cards.arrange(RIGHT, buff=1.5).move_to(UP * 0.2)

        # Descriptions below each card
        descs = [
            "Pull data from\nMySQL source",
            "Filter, map,\nreshape schema",
            "Write to Parquet\nfiles on disk",
        ]
        desc_labels = VGroup()
        for i, d in enumerate(descs):
            lbl = make_label(d, font_size=11, color=GREY_A)
            lbl.next_to(cards[i], DOWN, buff=0.2)
            desc_labels.add(lbl)

        # Show cards one by one with descriptions
        self.play(FadeIn(extract_card, shift=UP * 0.3))
        self.wait(0.5)
        self.play(FadeIn(desc_labels[0], shift=UP * 0.1))
        self.wait(1)

        # Arrow E → T
        arrow_et = Arrow(
            extract_card.get_right(), transform_card.get_left(),
            buff=0.15, stroke_width=3, color=ORANGE, tip_length=0.12,
        )
        self.play(FadeIn(transform_card, shift=UP * 0.3))
        self.wait(0.3)
        self.play(GrowArrow(arrow_et))
        self.play(FadeIn(desc_labels[1], shift=UP * 0.1))
        self.wait(1)

        # Arrow T → L
        arrow_tl = Arrow(
            transform_card.get_right(), load_card.get_left(),
            buff=0.15, stroke_width=3, color=GREEN, tip_length=0.12,
        )
        self.play(FadeIn(load_card, shift=UP * 0.3))
        self.wait(0.3)
        self.play(GrowArrow(arrow_tl))
        self.play(FadeIn(desc_labels[2], shift=UP * 0.1))
        self.wait(2)

        # Bottom highlight
        bottom = make_label(
            "NiFi handles all three stages in one visual pipeline",
            font_size=18, color=YELLOW,
        )
        bottom.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(bottom, shift=UP * 0.2))
        self.wait(3)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 6: Apache NiFi ─────────────────────────────────────────
    def scene_apache_nifi(self):
        header = make_label("Apache NiFi", font_size=30, color=ORANGE)
        header.to_edge(UP, buff=0.5)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(1)

        # Definition quote
        quote = make_label(
            '"A drag-and-drop tool for automating\n'
            ' data flow between software systems"',
            font_size=20, color=YELLOW,
        )
        quote.next_to(header, DOWN, buff=0.5)
        self.play(FadeIn(quote, shift=UP * 0.2))
        self.wait(2)

        # Concept: Computational Graph with 3 processor types
        proc_types = [
            (ICON_DATABASE, BLUE, "Source\nProcessor", "No input\nneeded"),
            (ICON_SETTINGS, ORANGE, "Processing\nProcessor", "Transform\ndata in-flight"),
            (ICON_FILE, GREEN, "Terminal\nProcessor", "No output\nedges"),
        ]

        procs = VGroup()
        for icon_path, color, title, desc in proc_types:
            ic = make_icon(icon_path, color=color, height=0.35)
            t = make_label(title, font_size=13, color=color, weight=BOLD)
            d = make_label(desc, font_size=10, color=GREY_A)
            content = VGroup(ic, t, d).arrange(DOWN, buff=0.1)
            box = RoundedRectangle(
                corner_radius=0.12, width=2.6, height=1.8,
                fill_color=DARK_BG, fill_opacity=0.9,
                stroke_color=color, stroke_width=1.5,
            )
            content.move_to(box.get_center())
            procs.add(VGroup(box, content))

        procs.arrange(RIGHT, buff=1.0).move_to(DOWN * 0.2)

        self.play(
            AnimationGroup(
                *[FadeIn(p, shift=UP * 0.3) for p in procs],
                lag_ratio=0.15,
            )
        )
        self.wait(1.5)

        # Arrows between processors
        arrow1 = Arrow(
            procs[0].get_right(), procs[1].get_left(),
            buff=0.12, stroke_width=2, color=WHITE, tip_length=0.1,
        )
        arrow2 = Arrow(
            procs[1].get_right(), procs[2].get_left(),
            buff=0.12, stroke_width=2, color=WHITE, tip_length=0.1,
        )
        self.play(GrowArrow(arrow1), GrowArrow(arrow2))
        self.wait(2)

        # Key processors listed below
        proc_names = [
            "ExecuteSQL", "GenerateTableFetch",
            "ConvertAvroToParquet", "PutFile", "PutParquet",
        ]
        proc_labels = VGroup()
        for name in proc_names:
            lbl = make_label(name, font_size=12, color=TEAL)
            box = RoundedRectangle(
                corner_radius=0.06, width=lbl.width + 0.3, height=0.35,
                fill_color=CARD_BG, fill_opacity=0.9,
                stroke_color=TEAL, stroke_width=1,
            )
            lbl.move_to(box.get_center())
            proc_labels.add(VGroup(box, lbl))

        proc_labels.arrange(RIGHT, buff=0.15).to_edge(DOWN, buff=0.5)

        self.play(
            AnimationGroup(
                *[FadeIn(p, shift=UP * 0.2) for p in proc_labels],
                lag_ratio=0.08,
            )
        )
        self.wait(3)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 7: NiFi Pipeline Detail ────────────────────────────────
    def scene_nifi_pipeline(self):
        header = make_label("NiFi ETL Pipeline", font_size=30, color=BLUE)
        header.to_edge(UP, buff=0.5)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(1)

        # Pipeline: MySQL → ExecuteSQL → Transform → ConvertAvroToParquet → Parquet
        mysql_card = make_icon_card(
            "MySQL\n(OLTP)", ICON_DATABASE,
            color=BLUE, width=2.0, height=1.3, font_size=11,
        )
        mysql_card.move_to(LEFT * 5 + DOWN * 0.3)

        transform_card = make_icon_card(
            "Transform\n(Star Schema)", ICON_TRANSFER,
            color=ORANGE, width=2.2, height=1.3, font_size=11,
        )
        transform_card.move_to(ORIGIN + DOWN * 0.3)

        parquet_card = make_icon_card(
            "Parquet\nFiles", ICON_FILE,
            color=GREEN, width=2.0, height=1.3, font_size=11,
        )
        parquet_card.move_to(RIGHT * 5 + DOWN * 0.3)

        # Show source
        self.play(FadeIn(mysql_card, shift=RIGHT * 0.3))
        self.wait(1)

        # Arrow MySQL → Transform
        arr1 = Arrow(
            mysql_card.get_right(), transform_card.get_left(),
            buff=0.12, stroke_width=2.5, color=BLUE, tip_length=0.12,
        )
        arr1_label = make_label("ExecuteSQL", font_size=10, color=GREY_A)
        arr1_label.next_to(arr1, UP, buff=0.08)

        self.play(GrowArrow(arr1), FadeIn(arr1_label))
        self.wait(0.5)
        self.play(FadeIn(transform_card, shift=RIGHT * 0.3))
        self.wait(1)

        # Arrow Transform → Parquet
        arr2 = Arrow(
            transform_card.get_right(), parquet_card.get_left(),
            buff=0.12, stroke_width=2.5, color=GREEN, tip_length=0.12,
        )
        arr2_label = make_label("ConvertAvro\nToParquet", font_size=10, color=GREY_A)
        arr2_label.next_to(arr2, UP, buff=0.08)

        self.play(GrowArrow(arr2), FadeIn(arr2_label))
        self.wait(0.5)
        self.play(FadeIn(parquet_card, shift=RIGHT * 0.3))
        self.wait(2)

        # Batch processing warning
        warning_box = RoundedRectangle(
            corner_radius=0.1, width=8.0, height=0.7,
            fill_color=DARK_BG, fill_opacity=0.95,
            stroke_color=YELLOW, stroke_width=1.5,
        )
        warning_text = make_label(
            "⚠ Process in batches (~1000 rows) to avoid Out-of-Memory!",
            font_size=15, color=YELLOW,
        )
        warning_text.move_to(warning_box.get_center())
        warning = VGroup(warning_box, warning_text).to_edge(DOWN, buff=0.5)

        self.play(FadeIn(warning, shift=UP * 0.2))
        self.wait(3)

        # Note: transformation must happen IN NiFi, not in Spark
        note_box = RoundedRectangle(
            corner_radius=0.1, width=8.0, height=0.7,
            fill_color=DARK_BG, fill_opacity=0.95,
            stroke_color=RED, stroke_width=1.5,
        )
        note_text = make_label(
            "Transform inside NiFi — do NOT just dump and join in Spark",
            font_size=15, color=RED,
        )
        note_text.move_to(note_box.get_center())
        note = VGroup(note_box, note_text).next_to(warning, UP, buff=0.15)

        self.play(FadeIn(note, shift=UP * 0.2))
        self.wait(3)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 8: Parquet File Format ─────────────────────────────────
    def scene_parquet(self):
        header = make_label("Apache Parquet", font_size=30, color=GREEN)
        header.to_edge(UP, buff=0.5)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(1)

        defn = make_label(
            "A hybrid columnar + row-group storage file format",
            font_size=18, color=GREY_A,
        )
        defn.next_to(header, DOWN, buff=0.3)
        self.play(FadeIn(defn, shift=UP * 0.2))
        self.wait(2)
        self.play(FadeOut(defn))
        self.wait(0.3)

        # ── Part A: Row-Oriented vs Column-Oriented (text examples) ──
        section_a = make_label("Row vs Column Storage", font_size=18, color=YELLOW)
        section_a.next_to(header, DOWN, buff=0.3)
        self.play(FadeIn(section_a, shift=UP * 0.2))
        self.wait(1)

        # --- Row-Oriented side ---
        row_title = make_label("Row-Oriented", font_size=15, color=GREY_A, weight=BOLD)

        # Data rows: each row stores all columns together
        row_data = [
            ("Ahmed", "30", "Engineer"),
            ("Sara", "25", "Doctor"),
            ("Omar", "35", "Engineer"),
        ]
        row_entries = VGroup()
        for name, age, job in row_data:
            name_lbl = make_label(name, font_size=11, color=BLUE)
            age_lbl = make_label(age, font_size=11, color=ORANGE)
            job_lbl = make_label(job, font_size=11, color=GREEN)
            sep1 = make_label(",", font_size=11, color=GREY_B)
            sep2 = make_label(",", font_size=11, color=GREY_B)
            row_line = VGroup(name_lbl, sep1, age_lbl, sep2, job_lbl).arrange(RIGHT, buff=0.06)
            entry_box = RoundedRectangle(
                corner_radius=0.06, width=row_line.width + 0.3, height=0.35,
                fill_color="#1E1E1E", fill_opacity=0.95,
                stroke_color=GREY_B, stroke_width=1,
            )
            row_line.move_to(entry_box.get_center())
            row_entries.add(VGroup(entry_box, row_line))
        row_entries.arrange(DOWN, buff=0.08)

        disk_row_label = make_label("On disk:", font_size=10, color=GREY_B)
        disk_row = make_label(
            "Ahmed,30,Eng | Sara,25,Doc | Omar,35,Eng",
            font_size=9, color=GREY_B,
        )
        disk_row_group = VGroup(disk_row_label, disk_row).arrange(DOWN, buff=0.04)

        row_content = VGroup(row_title, row_entries, disk_row_group).arrange(DOWN, buff=0.15)
        row_box = RoundedRectangle(
            corner_radius=0.12, width=5.0, height=3.2,
            fill_color=DARK_BG, fill_opacity=0.9, stroke_color=GREY_B, stroke_width=1.5,
        )
        row_content.move_to(row_box.get_center())
        row_group = VGroup(row_box, row_content).move_to(LEFT * 3.2 + DOWN * 0.5)

        # --- Column-Oriented side ---
        col_title = make_label("Column-Oriented", font_size=15, color=GREEN, weight=BOLD)

        # Data columns: each column stores all values of one field
        col_headers = ["Name", "Age", "Job"]
        col_values = [
            ["Ahmed", "Sara", "Omar"],
            ["30", "25", "35"],
            ["Engineer", "Doctor", "Engineer"],
        ]
        col_hdr_colors = [BLUE, ORANGE, GREEN]

        col_groups = VGroup()
        for i, (hdr, vals, hdr_color) in enumerate(zip(col_headers, col_values, col_hdr_colors)):
            h = make_label(hdr, font_size=11, color=hdr_color, weight=BOLD)
            val_labels = VGroup()
            for v in vals:
                lbl = make_label(v, font_size=10, color=hdr_color)
                val_labels.add(lbl)
            val_labels.arrange(DOWN, buff=0.06)
            col_entry = VGroup(h, val_labels).arrange(DOWN, buff=0.1)
            col_bg = RoundedRectangle(
                corner_radius=0.06, width=col_entry.width + 0.25, height=col_entry.height + 0.2,
                fill_color="#1E1E1E", fill_opacity=0.95,
                stroke_color=hdr_color, stroke_width=1,
            )
            col_entry.move_to(col_bg.get_center())
            col_groups.add(VGroup(col_bg, col_entry))
        col_groups.arrange(RIGHT, buff=0.12)

        disk_col_label = make_label("On disk:", font_size=10, color=GREY_B)
        disk_col = make_label(
            "Ahmed,Sara,Omar | 30,25,35 | Eng,Doc,Eng",
            font_size=9, color=GREY_B,
        )
        disk_col_group = VGroup(disk_col_label, disk_col).arrange(DOWN, buff=0.04)

        col_content = VGroup(col_title, col_groups, disk_col_group).arrange(DOWN, buff=0.15)
        col_box = RoundedRectangle(
            corner_radius=0.12, width=5.0, height=3.2,
            fill_color=DARK_BG, fill_opacity=0.9, stroke_color=GREEN, stroke_width=1.5,
        )
        col_content.move_to(col_box.get_center())
        col_group_card = VGroup(col_box, col_content).move_to(RIGHT * 3.2 + DOWN * 0.5)

        self.play(FadeIn(row_group, shift=RIGHT * 0.3))
        self.wait(2)
        self.play(FadeIn(col_group_card, shift=LEFT * 0.3))
        self.wait(2)

        # Parquet note at bottom
        parquet_note = make_label(
            "Parquet = Column-Oriented → better compression & faster analytics!",
            font_size=15, color=GREEN,
        )
        parquet_note.to_edge(DOWN, buff=0.35)
        self.play(
            Indicate(col_group_card, color=GREEN, scale_factor=1.03),
            FadeIn(parquet_note, shift=UP * 0.2),
        )
        self.wait(3)

        self.play(FadeOut(row_group, col_group_card, parquet_note, section_a))
        self.wait(0.5)

        # ── Part B: Parquet File Internals (correct hierarchy) ────────
        section_b = make_label("Inside a Parquet File", font_size=18, color=YELLOW)
        section_b.next_to(header, DOWN, buff=0.3)
        self.play(FadeIn(section_b, shift=UP * 0.2))
        self.wait(1)

        # Build a nested visual: File contains Row Groups,
        # each Row Group contains Column Chunks,
        # each Column Chunk contains Pages (Data, Dictionary, Index)
        # Footer at the bottom of the file

        # --- Outer: Parquet File box ---
        file_box = RoundedRectangle(
            corner_radius=0.15, width=12.5, height=5.8,
            fill_color="#0F1318", fill_opacity=0.95,
            stroke_color=GREEN, stroke_width=2,
        )
        file_label = make_label("Parquet File", font_size=14, color=GREEN, weight=BOLD)
        file_label.next_to(file_box, UP, buff=0.08)

        # --- Row Group 1 ---
        rg_color = BLUE

        # Column Chunks inside the Row Group
        def _make_col_chunk(col_name, color):
            """Build a column chunk with 3 page types inside."""
            hdr = make_label(col_name, font_size=9, color=color, weight=BOLD)
            pages = VGroup()
            page_defs = [
                ("Data Page", GREY_A),
                ("Dict Page", YELLOW),
                ("Index Page", TEAL),
            ]
            for pname, pcolor in page_defs:
                plbl = make_label(pname, font_size=7, color=pcolor)
                pbox = RoundedRectangle(
                    corner_radius=0.04, width=1.6, height=0.28,
                    fill_color="#1A1F26", fill_opacity=0.9,
                    stroke_color=pcolor, stroke_width=0.8,
                )
                plbl.move_to(pbox.get_center())
                pages.add(VGroup(pbox, plbl))
            pages.arrange(DOWN, buff=0.04)
            chunk_content = VGroup(hdr, pages).arrange(DOWN, buff=0.06)
            chunk_box = RoundedRectangle(
                corner_radius=0.08, width=1.9, height=chunk_content.height + 0.2,
                fill_color="#161B22", fill_opacity=0.9,
                stroke_color=color, stroke_width=1,
            )
            chunk_content.move_to(chunk_box.get_center())
            return VGroup(chunk_box, chunk_content)

        cc_a = _make_col_chunk("Col: Name", BLUE)
        cc_b = _make_col_chunk("Col: Age", ORANGE)
        cc_c = _make_col_chunk("Col: Job", GREEN)

        chunks = VGroup(cc_a, cc_b, cc_c).arrange(RIGHT, buff=0.15)

        rg_label = make_label("Row Group (block of rows)", font_size=11, color=rg_color, weight=BOLD)
        rg_content = VGroup(rg_label, chunks).arrange(DOWN, buff=0.1)
        rg_box = RoundedRectangle(
            corner_radius=0.1, width=rg_content.width + 0.4, height=rg_content.height + 0.25,
            fill_color="#111820", fill_opacity=0.9,
            stroke_color=rg_color, stroke_width=1.5,
        )
        rg_content.move_to(rg_box.get_center())
        rg_group = VGroup(rg_box, rg_content)

        # --- "... more Row Groups" hint ---
        more_rg = make_label("... more Row Groups ...", font_size=10, color=GREY_B)

        # --- Footer ---
        footer_items = VGroup(
            make_label("Schema", font_size=9, color=TEAL),
            make_label("•", font_size=9, color=GREY_B),
            make_label("Row Group metadata", font_size=9, color=TEAL),
            make_label("•", font_size=9, color=GREY_B),
            make_label("Column stats (min/max)", font_size=9, color=TEAL),
            make_label("•", font_size=9, color=GREY_B),
            make_label("Offsets", font_size=9, color=TEAL),
        ).arrange(RIGHT, buff=0.08)
        footer_label = make_label("Footer", font_size=11, color=TEAL, weight=BOLD)
        footer_content = VGroup(footer_label, footer_items).arrange(DOWN, buff=0.06)
        footer_box = RoundedRectangle(
            corner_radius=0.08, width=footer_content.width + 0.4, height=footer_content.height + 0.15,
            fill_color="#161B22", fill_opacity=0.9,
            stroke_color=TEAL, stroke_width=1.5,
        )
        footer_content.move_to(footer_box.get_center())
        footer = VGroup(footer_box, footer_content)

        # Arrange everything inside the file box
        file_inner = VGroup(rg_group, more_rg, footer).arrange(DOWN, buff=0.15)
        file_inner.move_to(file_box.get_center())

        # Position the whole thing
        whole_file = VGroup(file_label, file_box, file_inner)
        whole_file.move_to(DOWN * 0.4)

        # Animate layer by layer
        self.play(FadeIn(file_box), FadeIn(file_label))
        self.wait(0.5)
        self.play(FadeIn(rg_box), FadeIn(rg_label))
        self.wait(0.5)
        self.play(
            AnimationGroup(
                *[FadeIn(cc, shift=UP * 0.2) for cc in [cc_a, cc_b, cc_c]],
                lag_ratio=0.15,
            )
        )
        self.wait(2)
        self.play(FadeIn(more_rg))
        self.wait(0.5)
        self.play(FadeIn(footer))
        self.wait(3)

        # Highlight: "Spark reads the Footer first to know what's inside"
        spark_note = make_label(
            "Spark reads the Footer first — then skips irrelevant Row Groups!",
            font_size=14, color=YELLOW,
        )
        spark_note.to_edge(DOWN, buff=0.2)
        self.play(
            Indicate(footer, color=YELLOW, scale_factor=1.05),
            FadeIn(spark_note, shift=UP * 0.2),
        )
        self.wait(3)

        self.play(FadeOut(*self.mobjects))
        self.wait(0.3)

        # ── Part C: How Spark Optimizes with Parquet ──────────────────
        header2 = make_label("Apache Parquet", font_size=30, color=GREEN)
        header2.to_edge(UP, buff=0.5)
        section_c = make_label("How Spark Optimizes with Parquet", font_size=18, color=YELLOW)
        section_c.next_to(header2, DOWN, buff=0.3)
        self.play(FadeIn(header2), FadeIn(section_c))
        self.wait(1)

        optimizations = [
            (ICON_LIGHTNING, BLUE, "Column Pruning",
             "Read only needed columns\nSELECT name → skip age, job"),
            (ICON_SEARCH, ORANGE, "Predicate Pushdown",
             "Use min/max stats to\nskip entire Row Groups"),
            (ICON_LAYERS, GREEN, "Vectorized Read",
             "Read batches of rows\n~10x faster than row-by-row"),
            (ICON_STOPWATCH, PURPLE, "Partition Pruning",
             "Skip whole directories\nbased on WHERE clause"),
        ]

        opt_cards = VGroup()
        for icon_path, color, title, desc in optimizations:
            ic = make_icon(icon_path, color=color, height=0.28)
            t = make_label(title, font_size=12, color=color, weight=BOLD)
            d = make_label(desc, font_size=9, color=GREY_A)
            content = VGroup(ic, t, d).arrange(DOWN, buff=0.08)
            box = RoundedRectangle(
                corner_radius=0.1, width=2.7, height=1.8,
                fill_color=DARK_BG, fill_opacity=0.9,
                stroke_color=color, stroke_width=1.5,
            )
            content.move_to(box.get_center())
            opt_cards.add(VGroup(box, content))

        opt_cards.arrange(RIGHT, buff=0.2).move_to(DOWN * 0.5)

        self.play(
            AnimationGroup(
                *[FadeIn(c, shift=UP * 0.3) for c in opt_cards],
                lag_ratio=0.15,
            )
        )
        self.wait(2)

        for c in opt_cards:
            self.play(Indicate(c, color=YELLOW, scale_factor=1.05), run_time=0.4)
            self.wait(0.4)

        # Bottom compression note
        comp_note = make_label(
            "+ Snappy compression by default → less disk, faster reads",
            font_size=13, color=GREY_A,
        )
        comp_note.to_edge(DOWN, buff=0.35)
        self.play(FadeIn(comp_note, shift=UP * 0.2))
        self.wait(3)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 9: Star Schema ─────────────────────────────────────────
    def scene_star_schema(self):
        header = make_label("Star Schema Design", font_size=30, color=YELLOW)
        header.to_edge(UP, buff=0.5)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(1)

        # Definition
        defn = make_label(
            "One central Fact table surrounded by Dimension tables",
            font_size=18, color=GREY_A,
        )
        defn.next_to(header, DOWN, buff=0.35)
        self.play(FadeIn(defn, shift=UP * 0.2))
        self.wait(2)

        # Fact table — center
        fact_rect = RoundedRectangle(
            corner_radius=0.15, width=3.5, height=1.4,
            fill_color="#1C2128", fill_opacity=0.95,
            stroke_color=ORANGE, stroke_width=2.5,
        )
        fact_icon = make_icon(ICON_DATABASE, color=ORANGE, height=0.35)
        fact_title = make_label("Fact Table", font_size=16, color=ORANGE, weight=BOLD)
        fact_sub = make_label("lineitem + orders", font_size=11, color=GREY_A)
        fact_content = VGroup(fact_icon, fact_title, fact_sub).arrange(DOWN, buff=0.08)
        fact_content.move_to(fact_rect.get_center())
        fact = VGroup(fact_rect, fact_content).move_to(DOWN * 0.5)

        self.play(FadeIn(fact, shift=UP * 0.3))
        self.wait(1.5)

        # Dimension tables — star positions around fact
        dims = [
            ("Dim: customer", BLUE, LEFT * 4.5 + UP * 0.5),
            ("Dim: supplier", GREEN, RIGHT * 4.5 + UP * 0.5),
            ("Dim: nation", PURPLE, LEFT * 3.5 + DOWN * 2.5),
            ("Dim: partsupp", TEAL, RIGHT * 3.5 + DOWN * 2.5),
        ]

        dim_cards = VGroup()
        dim_arrows = VGroup()
        for name, color, pos in dims:
            card = make_card(
                name, width=2.2, height=0.8,
                fill_color=DARK_BG, label_color=color, font_size=13,
            )
            card[0].set_stroke(color, width=1.5)
            card.move_to(pos)
            dim_cards.add(card)

            arrow = Arrow(
                card.get_center(), fact.get_center(),
                buff=0.4, stroke_width=2, color=color, tip_length=0.1,
            )
            dim_arrows.add(arrow)

        # Animate dimensions one by one
        for i in range(len(dims)):
            self.play(FadeIn(dim_cards[i], shift=DOWN * 0.2))
            self.wait(0.3)
            self.play(GrowArrow(dim_arrows[i]))
            self.wait(0.5)

        self.wait(2)

        # Bottom insight
        insight = make_label(
            "Denormalize JOINs into one fact table for fast analytics",
            font_size=17, color=YELLOW,
        )
        insight.to_edge(DOWN, buff=0.3)
        self.play(FadeIn(insight, shift=UP * 0.2))
        self.wait(3)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 10: The SQL Query ──────────────────────────────────────
    def scene_sql_query(self):
        header = make_label("The 6-Table Query", font_size=30, color=RED)
        header.to_edge(UP, buff=0.5)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(1)

        # SQL query (abbreviated for screen — matches lab doc)
        sql_text = (
            "SELECT n_name, s_name,\n"
            "  SUM(l_quantity)       AS sum_qty,\n"
            "  SUM(l_extendedprice)  AS sum_base_price,\n"
            "  AVG(l_quantity)       AS avg_qty,\n"
            "  COUNT(*)              AS count_order\n"
            "FROM lineitem, orders, customers,\n"
            "     nation, partsupp, supplier\n"
            "WHERE l_shipdate <= DATE '1998-12-01'\n"
            "  AND l_orderkey = o_orderkey\n"
            "  AND o_custkey  = c_custkey\n"
            "  AND c_nationkey = n_nationkey\n"
            "  AND l_ps_id = ps_id\n"
            "  AND ps_suppkey = s_suppkey\n"
            "GROUP BY n_name, s_name"
        )

        code = make_code_text(sql_text, font_size=12, position=DOWN * 0.2)
        self.play(FadeIn(code, shift=UP * 0.3))
        self.wait(3)

        # Highlight the FROM clause tables
        highlight_box = SurroundingRectangle(
            code, color=YELLOW, buff=0.08, corner_radius=0.08, stroke_width=2,
        )
        self.play(Create(highlight_box))
        self.wait(1)

        # 6 tables mini-cards at the bottom
        table_names = ["lineitem", "orders", "customers", "nation", "partsupp", "supplier"]
        table_colors = [RED, PURPLE, BLUE, TEAL, ORANGE, GREEN]
        mini_cards = VGroup()
        for name, color in zip(table_names, table_colors):
            lbl = make_label(name, font_size=10, color=color)
            box = RoundedRectangle(
                corner_radius=0.06, width=lbl.width + 0.25, height=0.3,
                fill_color=CARD_BG, fill_opacity=0.9,
                stroke_color=color, stroke_width=1,
            )
            lbl.move_to(box.get_center())
            mini_cards.add(VGroup(box, lbl))

        mini_cards.arrange(RIGHT, buff=0.12).to_edge(DOWN, buff=0.4)

        self.play(
            AnimationGroup(
                *[FadeIn(c, shift=UP * 0.2) for c in mini_cards],
                lag_ratio=0.08,
            )
        )
        self.wait(1)

        # Joining note
        join_note = make_label(
            "6 JOINs — run 8 times on MySQL & Spark, compare average",
            font_size=14, color=GREY_A,
        )
        join_note.next_to(mini_cards, UP, buff=0.15)
        self.play(FadeIn(join_note, shift=UP * 0.1))
        self.wait(3)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 11: Deliverables ───────────────────────────────────────
    def scene_deliverables(self):
        header = make_label("Deliverables", font_size=30, color=ORANGE)
        header.to_edge(UP, buff=0.5)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(1)

        items = [
            (ICON_DATABASE, BLUE, "TPC-H data generation and insertion steps"),
            (ICON_CODE_FILE, GREEN, "DDL of the OLTP schema in MySQL"),
            (ICON_STRUCTURE, ORANGE, "DDL of the Star schema / NiFi transformation queries"),
            (ICON_TRANSFER, PURPLE, "NiFi ETL graph with processor descriptions"),
            (ICON_CHART, TEAL, "8 runs × 2 systems timing table (MySQL & Spark)"),
            (ICON_BOOK, RED, "Final report containing all deliverables"),
        ]

        rows = VGroup()
        for icon_path, color, desc in items:
            ic = make_icon(icon_path, color=color, height=0.25)
            check = make_icon(ICON_CHECK, color=GREEN, height=0.2)
            d = make_label(desc, font_size=13, color=GREY_A)
            row_content = VGroup(check, ic, d).arrange(RIGHT, buff=0.12)
            box = RoundedRectangle(
                corner_radius=0.08, width=10.5, height=0.5,
                fill_color=DARK_BG, fill_opacity=0.9,
                stroke_color=color, stroke_width=1,
            )
            row_content.move_to(box.get_center())
            rows.add(VGroup(box, row_content))

        rows.arrange(DOWN, buff=0.1).next_to(header, DOWN, buff=0.4)

        for row in rows:
            self.play(FadeIn(row, shift=LEFT * 0.3), run_time=0.4)
            self.wait(0.5)

        self.wait(2)

        # Warning
        warning = make_label(
            "All team members must be ready to answer questions!",
            font_size=17, color=YELLOW,
        )
        warning.to_edge(DOWN, buff=0.4)
        self.play(FadeIn(warning, shift=UP * 0.2))
        self.wait(3)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 12: Closing ────────────────────────────────────────────
    def scene_closing(self):
        title = make_label("Lab 1: OLAP", font_size=36, color=BLUE)
        title.move_to(UP * 1.5)
        self.play(AddTextLetterByLetter(title, time_per_char=0.05))
        self.wait(1)

        # Mini icons row as visual recap
        icon_data = [
            (ICON_DATABASE, BLUE),
            (ICON_TRANSFER, ORANGE),
            (ICON_STRUCTURE, GREEN),
            (ICON_FILE, PURPLE),
            (ICON_CHART, RED),
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
            "ETL · Star Schema · Parquet · NiFi · Spark",
            font_size=20, color=GREY_A,
        )
        themes.move_to(DOWN * 1.2)
        self.play(FadeIn(themes, shift=UP * 0.2))
        self.wait(4)
        self.play(FadeOut(*self.mobjects))


