import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from manim import (
    config,
    Scene,
    VGroup,
    RoundedRectangle,
    Rectangle,
    DashedLine,
    Arrow,
    Create,
    FadeIn,
    FadeOut,
    GrowFromEdge,
    GrowArrow,
    AnimationGroup,
    AddTextLetterByLetter,
    ORIGIN,
    UP,
    DOWN,
    LEFT,
    RIGHT,
    BOLD,
    WHITE,
    GREY_A,
    GREY_B,
    BLUE,
    BLUE_B,
    GREEN,
    GREEN_B,
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
    ICON_SETTINGS,
    ICON_STOPWATCH,
    ICON_CODE_FILE,
    ICON_CHART,
    ICON_STRUCTURE,
    ICON_LAYERS,
    ICON_TRANSFER,
    ICON_CLOUD,
    ICON_MONITOR,
    ICON_LIGHTNING,
    ICON_BOOK,
    ICON_GRAPH,
    ICON_CODE,
    make_label,
    make_icon,
    make_icon_card,
    make_code_text,
    create_rect_glow,
)

config.background_color = "#0D1117"

# ── Real tech brand icon paths ─────────────────────────────────────────
ICON_TECH_MONGODB = "assets/icons/tech/mongodb-plain.svg"
ICON_TECH_MYSQL = "assets/icons/tech/mysql.svg"
ICON_TECH_SPRING = "assets/icons/tech/spring.svg"
ICON_TECH_GRPC = "assets/icons/tech/grpc-plain.svg"

# ── Protobuf syntax-highlighting color map ────────────────────────────
PROTO_T2C = {
    "syntax": "#C586C0",
    "message": "#C586C0",
    "service": "#C586C0",
    "rpc": "#C586C0",
    "returns": "#C586C0",
    "repeated": "#C586C0",
    "optional": "#C586C0",
    "reserved": "#C586C0",
    "int32": "#4EC9B0",
    "string": "#4EC9B0",
    "bool": "#4EC9B0",
    "float": "#4EC9B0",
}

# ── MySQL DDL color map ───────────────────────────────────────────────
MYSQL_T2C = {
    "CREATE": "#C586C0",
    "TABLE": "#C586C0",
    "INSERT": "#C586C0",
    "INTO": "#C586C0",
    "VALUES": "#C586C0",
    "NOT": "#C586C0",
    "NULL": "#C586C0",
    "VARCHAR": "#4EC9B0",
    "ratings": "#4EC9B0",
    "movieId": "#9CDCFE",
    "(": "#FFD700",
    ")": "#FFD700",
    ",": "#D4D4D4",
    ";": "#D4D4D4",
}


class MicroserviceLab(Scene):
    def construct(self):
        self.scene_title()
        self.scene_lab_overview()
        self.scene_monolith_vs_microservices()
        self.scene_app_architecture()
        self.scene_ratings_mysql()
        self.scene_mongodb_caching()
        self.scene_grpc_trending()
        self.scene_jmeter_overview()
        self.scene_jmeter_graphs()
        self.scene_deliverables()
        self.scene_closing()

    # ─── Scene 1: Title ───────────────────────────────────────────────
    def scene_title(self):
        icon = make_icon(ICON_TECH_SPRING, color=BLUE, height=1.2)
        title = make_label(
            "Lab 2: Microservices & Data Models",
            font_size=38,
            color=BLUE,
        )
        subtitle = make_label(
            "MySQL · MongoDB · gRPC · JMeter",
            font_size=20,
            color=GREY_B,
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
            (
                ICON_TECH_MYSQL,
                BLUE,
                "Step 1: Ratings → MySQL",
                "Replace the in-memory list with a relational DB schema",
            ),
            (
                ICON_TECH_MONGODB,
                TEAL,
                "Step 2: Cache MovieDB → MongoDB",
                "Add a document-store cache to cut external API latency",
            ),
            (
                ICON_TECH_GRPC,
                ORANGE,
                "Step 3: gRPC Trending Movies Service",
                "Build a new binary-protocol microservice with Protobuf",
            ),
            (
                ICON_STOPWATCH,
                PURPLE,
                "Step 4: JMeter Performance Testing",
                "Measure P90 latency & throughput before & after each change",
            ),
            (
                ICON_BOOK,
                GREEN,
                "Step 5: Report & Discussion",
                "Answer discussion questions and submit all measurements",
            ),
        ]

        rows = VGroup()
        for icon_path, color, title, desc in steps:
            ic = make_icon(icon_path, color=color, height=0.3)
            t = make_label(title, font_size=15, color=color, weight=BOLD)
            d = make_label(desc, font_size=11, color=GREY_A)
            row_content = VGroup(ic, t, d).arrange(RIGHT, buff=0.15)
            box = RoundedRectangle(
                corner_radius=0.1,
                width=13.5,
                height=0.65,
                fill_color=DARK_BG,
                fill_opacity=0.9,
                stroke_color=color,
                stroke_width=1.2,
            )
            row_content.move_to(box.get_center())
            rows.add(VGroup(box, row_content))

        rows.arrange(DOWN, buff=0.15).next_to(header, DOWN, buff=0.5)

        for row in rows:
            self.play(FadeIn(row, shift=LEFT * 0.3), run_time=0.5)
            self.wait(0.8)

        self.wait(1)

        note = make_label(
            "Groups of 4 — measure before & after every change!",
            font_size=18,
            color=YELLOW,
        )
        note.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(note, shift=UP * 0.2))
        self.wait(3)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 3: Monolith vs Microservices ──────────────────────────
    def scene_monolith_vs_microservices(self):
        header = make_label("Monolith vs Microservices", font_size=30, color=ORANGE)
        header.to_edge(UP, buff=0.5)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(1)

        # ── Left: Monolith ──
        left_icon = make_icon(ICON_SERVER, color=GREY_A, height=0.6)
        left_title = make_label("Monolith", font_size=22, color=GREY_A)
        left_sub = make_label("One Big Deployable Unit", font_size=11, color=GREY_B)
        left_bullets = VGroup(
            make_label("Single codebase & deploy", font_size=13, color=GREY_B),
            make_label("Shared relational database", font_size=13, color=GREY_B),
            make_label("Tightly coupled components", font_size=13, color=GREY_B),
            make_label("One failure can crash all", font_size=13, color=GREY_B),
        ).arrange(DOWN, buff=0.1, aligned_edge=LEFT)

        left_content = VGroup(left_icon, left_title, left_sub, left_bullets).arrange(
            1.1 * DOWN, buff=0.15
        )
        left_box = RoundedRectangle(
            corner_radius=0.15,
            width=4.5,
            height=3.6,
            fill_color=DARK_BG,
            fill_opacity=0.9,
            stroke_color=GREY_B,
            stroke_width=1.5,
        )
        left_content.move_to(left_box.get_center())
        left_group = VGroup(left_box, left_content).move_to(
            LEFT * 3 + DOWN * 0.3
        )

        # ── Right: Microservices ──
        right_icon = make_icon(ICON_STRUCTURE, color=GREEN, height=0.6)
        right_title = make_label("Microservices", font_size=22, color=GREEN)
        right_sub = make_label(
            "Independent, Focused Services", font_size=11, color=GREEN_B
        )
        right_bullets = VGroup(
            make_label("Independent deployments", font_size=13, color=GREEN_B),
            make_label("Polyglot persistence", font_size=13, color=GREEN_B),
            make_label("Communicate via APIs", font_size=13, color=GREEN_B),
            make_label("Scale each service separately", font_size=13, color=GREEN_B),
        ).arrange(DOWN, buff=0.1, aligned_edge=LEFT)

        right_content = VGroup(
            right_icon, right_title, right_sub, right_bullets
        ).arrange(1.1 * DOWN, buff=0.15)
        right_box = RoundedRectangle(
            corner_radius=0.15,
            width=4.5,
            height=3.6,
            fill_color=DARK_BG,
            fill_opacity=0.9,
            stroke_color=GREEN,
            stroke_width=1.5,
        )
        right_content.move_to(right_box.get_center())
        right_glow = create_rect_glow(right_box, color=GREEN)
        right_group = VGroup(right_glow, right_box, right_content).move_to(
            RIGHT * 3 + DOWN * 0.3
        )

        self.play(FadeIn(left_group, shift=RIGHT * 0.3))
        self.wait(1.5)
        self.play(FadeIn(right_group, shift=LEFT * 0.3))
        self.wait(2)

        vs_label = make_label("VS", font_size=28, color=ORANGE)
        vs_label.move_to(ORIGIN + DOWN * 0.3)
        self.play(FadeIn(vs_label, scale=1.5))

        self.wait(3)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 4: Movie Rating App Architecture ───────────────────────
    def scene_app_architecture(self):
        header = make_label("Movie Rating App Architecture", font_size=30, color=BLUE)
        header.to_edge(UP, buff=0.3)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.5)

        # ── Row 0: Eureka Discovery Server (top center) ──────────────
        discovery_card = make_icon_card(
            "Discovery Server Eureka",
            ICON_GRAPH,
            color=ORANGE,
            width=2.8,
            height=1.2,
            font_size=10,
        )
        discovery_card.move_to(DOWN * 2.0)

        # ── Row 1: Movie Catalog (center accumulator) ─────────────────
        catalog_card = make_icon_card(
            "Movie Catalog",
            ICON_LAYERS,
            color=BLUE,
            width=2.4,
            height=1.2,
            font_size=11,
        )
        catalog_card.move_to(LEFT * 4.2 + UP * 0.4)

        # ── Row 2: Movie Info (left) and Ratings Data (right) ─────────
        movie_info_card = make_icon_card(
            "Movie Info",
            ICON_MONITOR,
            color=TEAL,
            width=2.2,
            height=1.2,
            font_size=11,
        )
        ratings_card = make_icon_card(
            "Ratings Data",
            ICON_TECH_MYSQL,
            color=PURPLE,
            width=2.2,
            height=1.2,
            font_size=11,
        )
        movie_info_card.move_to(RIGHT * 2.8 + UP * 1.1)
        ratings_card.move_to(RIGHT * 2.8 + DOWN * 0.6)

        # ── Row 3: External API and MySQL DB ──────────────────────────
        moviedb_card = make_icon_card(
            "The MovieDB API",
            ICON_CLOUD,
            color=ORANGE,
            width=2.0,
            height=1.1,
            font_size=10,
        )

        moviedb_card.move_to(RIGHT * 5.6 + UP * 1.1)

        # ── Call arrows (thick) ───────────────────────────────────────
        arrow_cat_info = Arrow(
            catalog_card.get_right() + UP * 0.18,
            movie_info_card.get_left() + DOWN * 0.12,
            buff=0.08,
            stroke_width=2.5,
            color=TEAL,
            tip_length=0.12,
        )
        arrow_cat_ratings = Arrow(
            catalog_card.get_right() + DOWN * 0.18,
            ratings_card.get_left() + UP * 0.12,
            buff=0.08,
            stroke_width=2.5,
            color=PURPLE,
            tip_length=0.12,
        )
        arrow_info_db = Arrow(
            movie_info_card.get_right(),
            moviedb_card.get_left(),
            buff=0.08,
            stroke_width=2.5,
            color=ORANGE,
            tip_length=0.12,
        )

        # ── Registration arrows → Eureka (thin) ───────────────────────
        reg_catalog = Arrow(
            catalog_card.get_bottom() + RIGHT * 0.4,
            discovery_card.get_top() + LEFT * 0.9,
            buff=0.08,
            stroke_width=1.5,
            color=ORANGE,
            tip_length=0.08,
        )
        # ── Animate ───────────────────────────────────────────────────
        # 1. Discovery server appears first
        self.play(FadeIn(discovery_card, shift=DOWN * 0.2))
        self.wait(0.3)

        # 2. Catalog registers with Eureka
        self.play(FadeIn(catalog_card, shift=DOWN * 0.2))
        self.play(GrowArrow(reg_catalog))
        self.wait(0.5)

        # 3. Catalog calls out to leaf services
        self.play(GrowArrow(arrow_cat_info), GrowArrow(arrow_cat_ratings))
        self.play(
            FadeIn(movie_info_card, shift=UP * 0.2),
            FadeIn(ratings_card, shift=UP * 0.2),
        )
        # Keep only catalog registration to discovery in this simplified view.
        self.wait(0.8)

        # 4. Leaf services connect to their data sources
        self.play(FadeIn(moviedb_card, shift=DOWN * 0.2))
        self.play(GrowArrow(arrow_info_db))
        self.wait(2)

        goal = make_label(
            "Your job: add MongoDB cache + new gRPC Trending service",
            font_size=16,
            color=YELLOW,
        )
        goal.to_edge(DOWN, buff=0.3)
        self.play(FadeIn(goal, shift=UP * 0.2))
        self.wait(3)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 5: Ratings → MySQL ────────────────────────────────────
    def scene_ratings_mysql(self):
        header = make_label("Step 1 — Ratings → MySQL", font_size=30, color=BLUE)
        header.to_edge(UP, buff=0.5)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(1)

        # Left: In-memory (dim / old)
        old_icon = make_icon(ICON_CODE, color=GREY_B, height=0.5)
        old_title = make_label("In-Memory List", font_size=16, color=GREY_B)
        old_sub = make_label("ArrayList<Rating>", font_size=11, color=GREY_A)
        old_bullets = VGroup(
            make_label("No: lost on restart", font_size=12, color=RED),
            make_label("No: not queryable", font_size=12, color=RED),
            make_label("No: no persistence", font_size=12, color=RED),
        ).arrange(DOWN, buff=0.1, aligned_edge=LEFT)
        old_content = VGroup(old_icon, old_title, old_sub, old_bullets).arrange(
            DOWN, buff=0.15
        )
        old_box = RoundedRectangle(
            corner_radius=0.15,
            width=3.5,
            height=2.9,
            fill_color=DARK_BG,
            fill_opacity=0.9,
            stroke_color=GREY_B,
            stroke_width=1.5,
        )
        old_content.move_to(old_box.get_center())
        old_group = VGroup(old_box, old_content).move_to(LEFT * 3.2 + UP * 0.3)

        # Right: MySQL (bright / new)
        new_icon = make_icon(ICON_TECH_MYSQL, color=BLUE, height=0.5)
        new_title = make_label("MySQL Database", font_size=16, color=BLUE)
        new_sub = make_label("Relational · Persistent", font_size=11, color=BLUE_B)
        new_bullets = VGroup(
            make_label("Yes: survives restarts", font_size=12, color=GREEN),
            make_label("Yes: SQL queries and JOINs", font_size=12, color=GREEN),
            make_label("Yes: indexed lookups", font_size=12, color=GREEN),
        ).arrange(DOWN, buff=0.1, aligned_edge=LEFT)
        new_content = VGroup(new_icon, new_title, new_sub, new_bullets).arrange(
            DOWN, buff=0.15
        )
        new_box = RoundedRectangle(
            corner_radius=0.15,
            width=3.5,
            height=2.9,
            fill_color=DARK_BG,
            fill_opacity=0.9,
            stroke_color=BLUE,
            stroke_width=1.5,
        )
        new_content.move_to(new_box.get_center())
        new_glow = create_rect_glow(new_box, color=BLUE)
        new_group = VGroup(new_glow, new_box, new_content).move_to(
            RIGHT * 3.2 + UP * 0.3
        )

        mig_arrow = Arrow(
            old_group.get_right(),
            new_group.get_left(),
            buff=0.15,
            stroke_width=3,
            color=BLUE,
            tip_length=0.15,
        )
        mig_label = make_label("migrate", font_size=13, color=BLUE)
        mig_label.next_to(mig_arrow, UP, buff=0.08)

        self.play(FadeIn(old_group, shift=RIGHT * 0.3))
        self.wait(1)
        self.play(GrowArrow(mig_arrow))
        self.play(FadeIn(mig_label, shift=DOWN * 0.1))
        self.play(FadeIn(new_group, shift=LEFT * 0.3))
        self.wait(1.5)

        # SQL schema
        sql_text = (
            "CREATE TABLE ratings (\n"
            "  movieId  VARCHAR(255),\n"
            "  rating   INT NOT NULL\n"
            ");\n"
            "INSERT INTO ratings\n"
            "VALUES ('tt0111161', 5);"
        )
        code = make_code_text(
            sql_text, font_size=12, position=DOWN * 2.3, t2c=MYSQL_T2C
        )
        self.play(FadeIn(code, shift=UP * 0.3))
        self.wait(3)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 6: MongoDB Caching ─────────────────────────────────────
    def scene_mongodb_caching(self):
        header = make_label("Step 2 — MongoDB Caching", font_size=30, color=TEAL)
        header.to_edge(UP, buff=0.5)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(1)

        # ── Part A: No cache ──
        part_a_label = make_label("Before: No Cache", font_size=18, color=RED)
        part_a_label.to_edge(LEFT, buff=1.0).shift(UP * 0.5)
        self.play(FadeIn(part_a_label, shift=RIGHT * 0.2))

        movie_info_a = make_icon_card(
            "Movie Info\nService",
            ICON_MONITOR,
            color=TEAL,
            width=2.0,
            height=1.3,
            font_size=11,
            glow=False,
        )
        moviedb_a = make_icon_card(
            "MovieDB\nAPI",
            ICON_CLOUD,
            color=ORANGE,
            width=2.0,
            height=1.3,
            font_size=11,
            glow=False,
        )
        movie_info_a.move_to(LEFT * 2.4 + DOWN * 0.3)
        moviedb_a.move_to(RIGHT * 2.4 + DOWN * 0.3)

        arrow_a = Arrow(
            movie_info_a.get_right(),
            moviedb_a.get_left(),
            buff=0.08,
            stroke_width=2.5,
            color=RED,
            tip_length=0.1,
        )
        slow_lbl = make_label("~2000 ms every call!", font_size=13, color=RED)
        slow_lbl.next_to(arrow_a, UP, buff=0.08)

        self.play(
            FadeIn(movie_info_a, shift=UP * 0.2),
            FadeIn(moviedb_a, shift=UP * 0.2),
        )
        self.play(GrowArrow(arrow_a))
        self.play(FadeIn(slow_lbl))
        self.wait(2)

        self.play(
            FadeOut(part_a_label),
            FadeOut(movie_info_a),
            FadeOut(moviedb_a),
            FadeOut(arrow_a),
            FadeOut(slow_lbl),
        )

        # ── Part B: With MongoDB cache ──
        part_b_label = make_label("After: MongoDB Cache", font_size=18, color=TEAL)
        part_b_label.to_edge(LEFT, buff=1.0).shift(UP * 0.5)
        self.play(FadeIn(part_b_label, shift=RIGHT * 0.2))

        movie_info_b = make_icon_card(
            "Movie Info\nService",
            ICON_MONITOR,
            color=TEAL,
            width=1.9,
            height=1.3,
            font_size=11,
            glow=False,
        )
        mongo_card = make_icon_card(
            "MongoDB\nCache",
            ICON_TECH_MONGODB,
            color=GREEN,
            width=1.9,
            height=1.3,
            font_size=11,
            glow=False,
        )
        moviedb_b = make_icon_card(
            "MovieDB\nAPI",
            ICON_CLOUD,
            color=ORANGE,
            width=1.9,
            height=1.3,
            font_size=11,
            glow=False,
        )
        movie_info_b.move_to(LEFT * 4.2 + DOWN * 0.3)
        mongo_card.move_to(ORIGIN + DOWN * 0.3)
        moviedb_b.move_to(RIGHT * 4.2 + DOWN * 0.3)
        # The Mongo SVG has a slightly uneven visual center; nudge icon to balance it.
        mongo_card.content[0].shift(LEFT * 0.1)
        mongo_glow = create_rect_glow(mongo_card.rect, color=GREEN)
        mongo_card_with_glow = VGroup(mongo_glow, mongo_card)

        arrow_b1 = Arrow(
            movie_info_b.get_right(),
            mongo_card.get_left(),
            buff=0.08,
            stroke_width=2.5,
            color=GREEN,
            tip_length=0.1,
        )
        fast_lbl = make_label("~5 ms (cache hit!)", font_size=12, color=GREEN)
        fast_lbl.next_to(arrow_b1, UP, buff=0.08)

        arrow_b2 = Arrow(
            mongo_card.get_right(),
            moviedb_b.get_left(),
            buff=0.08,
            stroke_width=2,
            color=GREY_B,
            tip_length=0.1,
        )
        miss_lbl = make_label("fallback on miss", font_size=11, color=GREY_A)
        miss_lbl.next_to(arrow_b2, UP, buff=0.08)

        self.play(
            FadeIn(movie_info_b, shift=UP * 0.2),
            FadeIn(mongo_card_with_glow, shift=UP * 0.2),
            FadeIn(moviedb_b, shift=UP * 0.2),
        )
        self.play(GrowArrow(arrow_b1))
        self.play(FadeIn(fast_lbl))
        self.wait(0.5)
        self.play(GrowArrow(arrow_b2))
        self.play(FadeIn(miss_lbl))
        self.wait(1.5)

        insight = make_label(
            "Test P90 latency with 10M movies: before vs after caching",
            font_size=16,
            color=YELLOW,
        )
        insight.to_edge(DOWN, buff=0.4)
        self.play(FadeIn(insight, shift=UP * 0.2))
        self.wait(3)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 7: gRPC Trending Movies Service ────────────────────────
    def scene_grpc_trending(self):
        header = make_label(
            "Step 3 — gRPC Trending Movies Service", font_size=27, color=ORANGE
        )
        header.to_edge(UP, buff=0.5)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(1)

        # Service flow: Catalog → gRPC → Trending → Ratings DB
        catalog_card = make_icon_card(
            "Catalog\nService",
            ICON_LAYERS,
            color=BLUE,
            width=2.0,
            height=1.3,
            font_size=11,
            glow=False,
        )
        trending_card = make_icon_card(
            "Trending\nService",
            ICON_TECH_GRPC,
            color=ORANGE,
            width=2.0,
            height=1.3,
            font_size=11,
            glow=False,
        )
        db_card = make_icon_card(
            "Ratings\nDB",
            ICON_TECH_MYSQL,
            color=PURPLE,
            width=2.0,
            height=1.3,
            font_size=11,
            glow=False,
        )
        catalog_card.move_to(LEFT * 4.0 + UP * 0.9)
        trending_card.move_to(ORIGIN + UP * 0.9)
        db_card.move_to(RIGHT * 4.0 + UP * 0.9)
        grpc_glow = create_rect_glow(trending_card.rect, color=ORANGE)
        trending_card_with_glow = VGroup(grpc_glow, trending_card)

        arrow_grpc = Arrow(
            catalog_card.get_right(),
            trending_card.get_left(),
            buff=0.08,
            stroke_width=2.5,
            color=ORANGE,
            tip_length=0.12,
        )
        grpc_lbl = make_label("gRPC call", font_size=12, color=ORANGE)
        grpc_lbl.next_to(arrow_grpc, UP, buff=0.08)

        arrow_db = Arrow(
            trending_card.get_right(),
            db_card.get_left(),
            buff=0.08,
            stroke_width=2.5,
            color=PURPLE,
            tip_length=0.12,
        )
        db_lbl = make_label("query top-N", font_size=12, color=PURPLE)
        db_lbl.next_to(arrow_db, UP, buff=0.08)

        self.play(FadeIn(catalog_card, shift=DOWN * 0.2))
        self.wait(0.4)
        self.play(GrowArrow(arrow_grpc))
        self.play(FadeIn(grpc_lbl))
        self.play(FadeIn(trending_card_with_glow, shift=DOWN * 0.2))
        self.wait(0.4)
        self.play(GrowArrow(arrow_db))
        self.play(FadeIn(db_lbl))
        self.play(FadeIn(db_card, shift=DOWN * 0.2))
        self.wait(1.5)

        # Concept cards: Protobuf, HTTP/2, .proto schema
        concept_data = [
            (
                ICON_CODE,
                BLUE,
                "Protobuf",
                "Binary serialization\nSmaller & faster than JSON",
            ),
            (
                ICON_LIGHTNING,
                ORANGE,
                "HTTP/2",
                "Multiplexed streams\nLow-latency transport",
            ),
            (
                ICON_STRUCTURE,
                GREEN,
                ".proto Schema",
                "Service & message\ndefinitions in one file",
            ),
        ]
        concepts = VGroup()
        for icon_path, color, title, desc in concept_data:
            ic = make_icon(icon_path, color=color, height=0.3)
            t = make_label(title, font_size=13, color=color, weight=BOLD)
            d = make_label(desc, font_size=10, color=GREY_A)
            content = VGroup(ic, t, d).arrange(DOWN, buff=0.1)
            box = RoundedRectangle(
                corner_radius=0.12,
                width=2.9,
                height=1.6,
                fill_color=DARK_BG,
                fill_opacity=0.9,
                stroke_color=color,
                stroke_width=1.2,
            )
            content.move_to(box.get_center())
            concepts.add(VGroup(box, content))

        concepts.arrange(RIGHT, buff=0.4).move_to(DOWN * 1.8)
        self.play(
            AnimationGroup(
                *[FadeIn(c, shift=UP * 0.3) for c in concepts],
                lag_ratio=0.15,
            )
        )
        self.wait(3)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 8: JMeter Overview ─────────────────────────────────────
    def scene_jmeter_overview(self):
        header = make_label(
            "Step 4 — JMeter Performance Testing", font_size=27, color=PURPLE
        )
        header.to_edge(UP, buff=0.5)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(1)

        # Three JMeter component cards
        comp_data = [
            (
                ICON_SETTINGS,
                BLUE,
                "Thread Group",
                "Threads: 100\nRamp-up: 30 s\nLoop: 10",
            ),
            (
                ICON_TRANSFER,
                ORANGE,
                "HTTP Sampler",
                "GET /catalog/{userId}\nCaptures status & latency",
            ),
            (
                ICON_CHART,
                GREEN,
                "Listeners",
                "Summary Report\nAggregate Report\nResponse Time Graph",
            ),
        ]
        comp_cards = VGroup()
        for icon_path, color, title, desc in comp_data:
            ic = make_icon(icon_path, color=color, height=0.35)
            t = make_label(title, font_size=13, color=color, weight=BOLD)
            d = make_label(desc, font_size=10, color=GREY_A)
            content = VGroup(ic, t, d).arrange(DOWN, buff=0.1)
            box = RoundedRectangle(
                corner_radius=0.12,
                width=3.0,
                height=2.1,
                fill_color=DARK_BG,
                fill_opacity=0.9,
                stroke_color=color,
                stroke_width=1.5,
            )
            content.move_to(box.get_center())
            comp_cards.add(VGroup(box, content))

        comp_cards.arrange(RIGHT, buff=0.5).move_to(UP * 0.4)
        self.play(
            AnimationGroup(
                *[FadeIn(c, shift=DOWN * 0.2) for c in comp_cards],
                lag_ratio=0.15,
            )
        )
        self.wait(1.5)

        arrow1 = Arrow(
            comp_cards[0].get_right(),
            comp_cards[1].get_left(),
            buff=0.1,
            stroke_width=2,
            color=WHITE,
            tip_length=0.1,
        )
        arrow2 = Arrow(
            comp_cards[1].get_right(),
            comp_cards[2].get_left(),
            buff=0.1,
            stroke_width=2,
            color=WHITE,
            tip_length=0.1,
        )
        self.play(GrowArrow(arrow1), GrowArrow(arrow2))
        self.wait(1)

        # Performance vs Stress test comparison (bottom)
        perf_data = [
            (
                ICON_STOPWATCH,
                PURPLE,
                "Performance Test",
                "100 threads · 5 minutes · normal load",
            ),
            (
                ICON_LIGHTNING,
                RED,
                "Stress Test",
                "500 threads · ramp to limit · find breaking point",
            ),
        ]
        test_cards = VGroup()
        for icon_path, color, title, desc in perf_data:
            ic = make_icon(icon_path, color=color, height=0.3)
            t = make_label(title, font_size=13, color=color, weight=BOLD)
            d = make_label(desc, font_size=11, color=GREY_A)
            content = VGroup(ic, t, d).arrange(DOWN, buff=0.1)
            box = RoundedRectangle(
                corner_radius=0.1,
                width=5.4,
                height=1.2,
                fill_color=DARK_BG,
                fill_opacity=0.9,
                stroke_color=color,
                stroke_width=1.2,
            )
            content.move_to(box.get_center())
            test_cards.add(VGroup(box, content))

        test_cards.arrange(RIGHT, buff=0.6).to_edge(DOWN, buff=0.5)
        self.play(
            AnimationGroup(
                *[FadeIn(c, shift=UP * 0.2) for c in test_cards],
                lag_ratio=0.2,
            )
        )
        self.wait(3)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 9: JMeter Results Graphs ──────────────────────────────
    def scene_jmeter_graphs(self):
        header = make_label("JMeter Results: Cache Impact", font_size=28, color=GREEN)
        header.to_edge(UP, buff=0.5)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(1)

        illust_note = make_label(
            "* Illustrative values — replace with your own JMeter measurements",
            font_size=11,
            color=GREY_B,
        )
        illust_note.next_to(header, DOWN, buff=0.15)
        self.play(FadeIn(illust_note, shift=DOWN * 0.1))
        self.wait(0.5)

        note = make_label(
            "Average hides outliers; read p50, p90, and p99 from JMeter.",
            font_size=17,
            color=YELLOW,
        )
        note.next_to(illust_note, DOWN, buff=0.25)
        self.play(FadeIn(note, shift=UP * 0.2))
        self.wait(1.5)

        bar_heights = [0.35, 0.9, 1.9, 3.0, 3.4, 2.7, 1.5, 0.8, 0.45, 0.22, 0.12, 0.08]
        bar_colors = [GREEN] * 7 + [ORANGE] * 2 + [RED] * 3
        bars = VGroup()
        for h, color in zip(bar_heights, bar_colors):
            bar = Rectangle(
                width=0.45,
                height=h,
                fill_color=color,
                fill_opacity=0.75,
                stroke_color=color,
                stroke_width=1,
            )
            bars.add(bar)
        bars.arrange(RIGHT, buff=0.06, aligned_edge=DOWN)
        bars.move_to(DOWN * 0.25)

        x_label = make_label("Response Time ->", font_size=12, color=GREY_A)
        x_label.next_to(bars, DOWN, buff=0.2)

        self.play(AnimationGroup(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.06))
        self.play(FadeIn(x_label))
        self.wait(1)

        p50_line = DashedLine(
            bars[4].get_top() + UP * 0.15,
            bars[4].get_bottom() + DOWN * 0.3,
            color=GREEN,
            stroke_width=2,
        )
        p50_label = make_label("p50", font_size=11, color=GREEN)
        p50_label.next_to(p50_line, UP, buff=0.1)

        p90_line = DashedLine(
            bars[8].get_top() + UP * 0.15,
            bars[8].get_bottom() + DOWN * 0.3,
            color=ORANGE,
            stroke_width=2,
        )
        p90_label = make_label("p90", font_size=11, color=ORANGE)
        p90_label.next_to(p90_line, UP, buff=0.1)

        p99_line = DashedLine(
            bars[10].get_top() + UP * 0.15,
            bars[10].get_bottom() + DOWN * 0.3,
            color=RED,
            stroke_width=2,
        )
        p99_label = make_label("p99", font_size=11, color=RED)
        p99_label.next_to(p99_line, UP, buff=0.1)

        self.play(Create(p50_line), FadeIn(p50_label))
        self.wait(0.8)
        self.play(Create(p90_line), FadeIn(p90_label))
        self.wait(0.8)
        self.play(Create(p99_line), FadeIn(p99_label))
        self.wait(1.5)

        tail_box = RoundedRectangle(
            corner_radius=0.1,
            width=7.8,
            height=0.9,
            fill_color=DARK_BG,
            fill_opacity=0.95,
            stroke_color=RED,
            stroke_width=1.5,
        )
        tail_text = make_label(
            "Cache lowers tail latency: p90 ~2000 ms -> ~120 ms (illustrative)",
            font_size=13,
            color=YELLOW,
        )
        tail_text.move_to(tail_box.get_center())
        tail_group = VGroup(tail_box, tail_text)
        tail_group.to_edge(DOWN, buff=0.35)

        self.play(FadeIn(tail_group, shift=UP * 0.2))
        self.wait(3)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 10: Deliverables ───────────────────────────────────────
    def scene_deliverables(self):
        header = make_label("Deliverables", font_size=30, color=ORANGE)
        header.to_edge(UP, buff=0.5)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(1)

        items = [
            (ICON_TECH_MYSQL, BLUE, "MySQL schema — CREATE TABLE DDL for ratings"),
            (
                ICON_TECH_MONGODB,
                TEAL,
                "MongoDB schema — collection structure & indexes",
            ),
            (ICON_CHART, ORANGE, "JMeter P90 & throughput — before vs after caching"),
            (ICON_STOPWATCH, PURPLE, "JMeter test plans (.jmx files) for both tests"),
            (
                ICON_CODE_FILE,
                GREEN,
                "Running app: Catalog + Ratings + Trending services",
            ),
            (ICON_BOOK, RED, "Final report with answers to discussion questions"),
        ]

        rows = VGroup()
        for icon_path, color, desc in items:
            ic = make_icon(icon_path, color=color, height=0.25)
            check = make_icon(ICON_CHECK, color=GREEN, height=0.2)
            d = make_label(desc, font_size=13, color=GREY_A)
            row_content = VGroup(check, ic, d).arrange(RIGHT, buff=0.12)
            box = RoundedRectangle(
                corner_radius=0.08,
                width=10.5,
                height=0.5,
                fill_color=DARK_BG,
                fill_opacity=0.9,
                stroke_color=color,
                stroke_width=1,
            )
            row_content.move_to(box.get_center())
            rows.add(VGroup(box, row_content))

        rows.arrange(DOWN, buff=0.1).next_to(header, DOWN, buff=0.4)

        for row in rows:
            self.play(FadeIn(row, shift=LEFT * 0.3), run_time=0.4)
            self.wait(0.5)

        self.wait(2)

        warning = make_label(
            "All team members must be ready to answer questions!",
            font_size=17,
            color=YELLOW,
        )
        warning.to_edge(DOWN, buff=0.4)
        self.play(FadeIn(warning, shift=UP * 0.2))
        self.wait(3)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 11: Closing ────────────────────────────────────────────
    def scene_closing(self):
        title = make_label(
            "Lab 2: Microservices & Data Models", font_size=34, color=BLUE
        )
        title.move_to(UP * 1.5)
        self.play(AddTextLetterByLetter(title, time_per_char=0.05))
        self.wait(1)

        icon_data = [
            (ICON_TECH_MYSQL, BLUE),
            (ICON_TECH_MONGODB, TEAL),
            (ICON_TECH_GRPC, ORANGE),
            (ICON_STOPWATCH, PURPLE),
            (ICON_GRAPH, GREEN),
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
            "MySQL · MongoDB · gRPC · Protobuf · JMeter",
            font_size=20,
            color=GREY_A,
        )
        themes.move_to(DOWN * 1.2)
        self.play(FadeIn(themes, shift=UP * 0.2))
        self.wait(4)
        self.play(FadeOut(*self.mobjects))
