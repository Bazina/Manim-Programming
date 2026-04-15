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
    DashedLine,
    FadeIn,
    FadeOut,
    AddTextLetterByLetter,
    Indicate,
    UP,
    DOWN,
    LEFT,
    RIGHT,
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
    ICON_STRUCTURE,
    ICON_LIGHTNING,
    ICON_CODE,
    ICON_GRAPH,
    ICON_BOOK,
    make_label,
    make_icon,
    make_code_text,
    create_rect_glow,
)

config.background_color = "#0D1117"

# ── PL/pgSQL color map ────────────────────────────────────────────────
PLPGSQL_T2C = {
    "CREATE": "#C586C0",
    "OR": "#C586C0",
    "REPLACE": "#C586C0",
    "FUNCTION": "#C586C0",
    "OUT": "#C586C0",
    "AS": "#C586C0",
    "DECLARE": "#C586C0",
    "BEGIN": "#C586C0",
    "END": "#C586C0",
    "SELECT": "#C586C0",
    "INTO": "#C586C0",
    "LANGUAGE": "#C586C0",
    "PLPGSQL": "#C586C0",
    "TABLE": "#C586C0",
    "NOT": "#C586C0",
    "NULL": "#C586C0",
    "DEFAULT": "#C586C0",
    "bigint": "#4EC9B0",
    "int": "#4EC9B0",
    "insta5": "#9CDCFE",
    "next_id": "#DCDCAA",
    "nextval": "#DCDCAA",
    "FLOOR": "#DCDCAA",
    "EXTRACT": "#DCDCAA",
    "clock_timestamp": "#DCDCAA",
    "our_epoch": "#9CDCFE",
    "seq_id": "#9CDCFE",
    "now_millis": "#9CDCFE",
    "shard_id": "#9CDCFE",
    "result": "#9CDCFE",
    "1314220021721": "#B5CEA8",
    "1024": "#B5CEA8",
    "23": "#B5CEA8",
    "10": "#B5CEA8",
    "5": "#B5CEA8",
    "<<": "#D4D4D4",
    "|": "#D4D4D4",
    "%%": "#D4D4D4",
    "(": "#FFD700",
    ")": "#FFD700",
    ";": "#D4D4D4",
    ":=": "#D4D4D4",
}


class InstagramShardingIDs(Scene):
    def construct(self):
        self.scene_title()
        self.scene_the_problem()
        self.scene_existing_solutions()
        self.scene_bit_layout()
        self.scene_worked_example()
        self.scene_plpgsql_function()
        self.scene_logical_vs_physical()
        self.scene_comparison()
        self.scene_key_takeaways()
        self.scene_closing()

    # ─── Helper ───────────────────────────────────────────────────────
    def _bit_segment(self, label, bits, color, width):
        box = RoundedRectangle(
            corner_radius=0.08,
            width=width,
            height=0.7,
            fill_color=DARK_BG,
            fill_opacity=0.9,
            stroke_color=color,
            stroke_width=1.5,
        )
        lbl = make_label(label, font_size=11, color=color)
        bit_lbl = make_label(f"{bits} bits", font_size=9, color=GREY_A)
        content = VGroup(lbl, bit_lbl).arrange(DOWN, buff=0.05)
        content.move_to(box.get_center())
        return VGroup(box, content)

    def _card(self, icon_path, color, title, sub):
        ic = make_icon(icon_path, color=color, height=0.4)
        t = make_label(title, font_size=13, color=color)
        s = make_label(sub, font_size=10, color=GREY_A)
        content = VGroup(ic, t, s).arrange(DOWN, buff=0.1)
        box = RoundedRectangle(
            corner_radius=0.12,
            width=3.6,
            height=1.9,
            fill_color=DARK_BG,
            fill_opacity=0.9,
            stroke_color=color,
            stroke_width=1.5,
        )
        content.move_to(box.get_center())
        return VGroup(box, content)

    # ─── Scene 1: Title ───────────────────────────────────────────────
    def scene_title(self):
        icon = make_icon(ICON_DATABASE, color=ORANGE, height=1.1)
        title = make_label(
            "Sharding & IDs at Instagram",
            font_size=32,
            color=ORANGE,
        )
        subtitle = make_label(
            "64-bit  ·  Time-sortable  ·  In-Database Snowflake",
            font_size=18,
            color=GREY_B,
        )
        VGroup(icon, title, subtitle).arrange(DOWN, buff=0.4)

        self.play(FadeIn(icon, shift=DOWN * 0.3))
        self.wait(0.4)
        self.play(AddTextLetterByLetter(title, time_per_char=0.04))
        self.wait(0.4)
        self.play(FadeIn(subtitle, shift=UP * 0.2))
        self.wait(3)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 2: The Problem ─────────────────────────────────────────
    def scene_the_problem(self):
        header = make_label("The Problem", font_size=30, color=RED)
        header.to_edge(UP, buff=0.5)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.5)

        # Show multiple shards with conflicting IDs
        shards = VGroup()
        for i, name in enumerate(["Shard A", "Shard B", "Shard C"]):
            shard_icon = make_icon(ICON_DATABASE, color=BLUE, height=0.35)
            shard_label = make_label(name, font_size=12, color=BLUE)
            ids_text = make_label(
                f"id=1, id=2, id=3 ...",
                font_size=10,
                color=GREY_A,
            )
            content = VGroup(shard_icon, shard_label, ids_text).arrange(DOWN, buff=0.08)
            box = RoundedRectangle(
                corner_radius=0.12,
                width=3.2,
                height=1.6,
                fill_color=DARK_BG,
                fill_opacity=0.9,
                stroke_color=BLUE,
                stroke_width=1.3,
            )
            content.move_to(box.get_center())
            shards.add(VGroup(box, content))

        shards.arrange(RIGHT, buff=0.5).move_to(DOWN * 0.1)

        for shard in shards:
            self.play(FadeIn(shard, shift=UP * 0.2), run_time=0.5)
            self.wait(0.3)

        # Collision warning
        collision = make_label(
            "AUTO_INCREMENT → same IDs on every shard → collisions!",
            font_size=16,
            color=RED,
        )
        collision.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(collision, shift=UP * 0.2))
        self.wait(3)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 3: Existing Solutions ──────────────────────────────────
    def scene_existing_solutions(self):
        header = make_label("Solutions Instagram Evaluated", font_size=28, color=TEAL)
        header.to_edge(UP, buff=0.5)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.5)

        solutions = [
            (
                ICON_CODE,
                PURPLE,
                "App-Generated IDs",
                "MongoDB ObjectId / UUID",
                "96–128 bits, large",
            ),
            (
                ICON_SERVER,
                BLUE,
                "Dedicated Service",
                "Twitter Snowflake + ZooKeeper",
                "Extra infra overhead",
            ),
            (
                ICON_DATABASE,
                GREEN,
                "DB Ticket Servers",
                "Flickr odd/even pair",
                "Write bottleneck risk",
            ),
        ]

        cards = VGroup()
        for icon_path, color, title, desc, con in solutions:
            ic = make_icon(icon_path, color=color, height=0.35)
            t = make_label(title, font_size=13, color=color)
            d = make_label(desc, font_size=10, color=GREY_A)
            c = make_label("✗ " + con, font_size=10, color=RED)
            content = VGroup(ic, t, d, c).arrange(DOWN, buff=0.08)
            box = RoundedRectangle(
                corner_radius=0.12,
                width=3.6,
                height=2.0,
                fill_color=DARK_BG,
                fill_opacity=0.9,
                stroke_color=color,
                stroke_width=1.3,
            )
            content.move_to(box.get_center())
            cards.add(VGroup(box, content))

        cards.arrange(RIGHT, buff=0.4).move_to(DOWN * 0.2)
        for card in cards:
            self.play(FadeIn(card, shift=UP * 0.2), run_time=0.5)
            self.wait(0.5)

        verdict = make_label(
            "Snowflake was closest — but Instagram wanted no extra services",
            font_size=16,
            color=YELLOW,
        )
        verdict.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(verdict, shift=UP * 0.2))
        self.wait(3)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 4: 64-Bit ID Layout ───────────────────────────────────
    def scene_bit_layout(self):
        header = make_label("64-Bit ID Layout", font_size=28, color=ORANGE)
        header.to_edge(UP, buff=0.5)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.5)

        ts_seg = self._bit_segment("Timestamp\n(ms since epoch)", 41, BLUE, 5.5)
        shard_seg = self._bit_segment("Shard ID", 13, GREEN, 2.8)
        seq_seg = self._bit_segment("Sequence\n% 1024", 10, PURPLE, 2.5)

        layout = VGroup(ts_seg, shard_seg, seq_seg).arrange(RIGHT, buff=0.12)
        layout.move_to(UP * 0.5)

        msb = make_label("MSB", font_size=10, color=GREY_A)
        lsb = make_label("LSB", font_size=10, color=GREY_A)
        msb.next_to(layout, LEFT, buff=0.15)
        lsb.next_to(layout, RIGHT, buff=0.15)

        self.play(FadeIn(ts_seg, shift=DOWN * 0.2))
        self.wait(0.5)
        self.play(FadeIn(shard_seg, shift=DOWN * 0.2))
        self.wait(0.5)
        self.play(FadeIn(seq_seg, shift=DOWN * 0.2))
        self.wait(0.3)
        self.play(FadeIn(msb), FadeIn(lsb))

        # Annotations
        details = VGroup(
            make_label(
                "41 bits → ~69 years from custom epoch (Jan 1, 2011)",
                font_size=14,
                color=BLUE,
            ),
            make_label(
                "13 bits → up to 8,192 logical shards",
                font_size=14,
                color=GREEN,
            ),
            make_label(
                "10 bits → 1,024 IDs per shard per millisecond",
                font_size=14,
                color=PURPLE,
            ),
        ).arrange(DOWN, buff=0.15, aligned_edge=LEFT)
        details.move_to(DOWN * 1.3)

        for d in details:
            self.play(FadeIn(d, shift=LEFT * 0.2), run_time=0.4)
            self.wait(0.4)

        total = make_label(
            "Total: 64-bit bigint — fits natively in PostgreSQL, Redis, and most languages",
            font_size=15,
            color=YELLOW,
        )
        total.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(total, shift=UP * 0.2))
        self.wait(3)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 5: Worked Example ─────────────────────────────────────
    def scene_worked_example(self):
        header = make_label("Worked Example", font_size=28, color=GREEN)
        header.to_edge(UP, buff=0.5)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.5)

        # Context
        context_lines = VGroup(
            make_label(
                "Epoch: Jan 1, 2011    Time: Sep 9, 2011 5:00 PM",
                font_size=13,
                color=GREY_A,
            ),
            make_label(
                "ms since epoch: 1,387,263,000    user_id: 31,341    shards: 2,000",
                font_size=13,
                color=GREY_A,
            ),
        ).arrange(DOWN, buff=0.08)
        context_lines.next_to(header, DOWN, buff=0.35)
        self.play(FadeIn(context_lines, shift=UP * 0.1))
        self.wait(0.8)

        # Step-by-step bit operations
        steps = [
            ("Step 1: Timestamp", "id  = 1387263000 << 23", BLUE),
            ("Step 2: Shard ID", "id |= 1341 << 10", GREEN),
            (
                "Step 3: Sequence",
                "id |= (5001 % 1024)   →  905",
                PURPLE,
            ),
        ]

        step_group = VGroup()
        for label, code, color in steps:
            lbl = make_label(label, font_size=13, color=color)
            c = make_label(code, font_size=14, color=WHITE)
            row = VGroup(lbl, c).arrange(RIGHT, buff=0.3)
            step_group.add(row)

        step_group.arrange(DOWN, buff=0.25, aligned_edge=LEFT)
        step_group.move_to(DOWN * 0.4)

        for step in step_group:
            self.play(FadeIn(step, shift=LEFT * 0.2), run_time=0.5)
            self.wait(0.8)

        # Show the bit composition visually
        note = make_label(
            "shard = 31341 % 2000 = 1341    sequence = 5001 % 1024 = 905",
            font_size=13,
            color=ORANGE,
        )
        note.next_to(step_group, DOWN, buff=0.3)
        self.play(FadeIn(note, shift=UP * 0.1))

        result = make_label(
            "Result: a unique 64-bit bigint encoding time + shard + sequence",
            font_size=16,
            color=YELLOW,
        )
        result.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(result, shift=UP * 0.2))
        self.wait(3)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 6: PL/pgSQL Function ──────────────────────────────────
    def scene_plpgsql_function(self):
        header = make_label("PL/pgSQL: next_id() Function", font_size=28, color=BLUE)
        header.to_edge(UP, buff=0.5)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.5)

        sql = (
            "CREATE OR REPLACE FUNCTION\n"
            "  insta5.next_id(OUT result bigint)\n"
            "AS $$\n"
            "DECLARE\n"
            "  our_epoch bigint := 1314220021721;\n"
            "  seq_id    bigint;\n"
            "  now_millis bigint;\n"
            "  shard_id  int := 5;\n"
            "BEGIN\n"
            "  SELECT nextval('insta5.table_id_seq')\n"
            "    %% 1024 INTO seq_id;\n"
            "  SELECT FLOOR(EXTRACT(EPOCH FROM\n"
            "    clock_timestamp()) * 1000)\n"
            "    INTO now_millis;\n"
            "  result := (now_millis - our_epoch)\n"
            "    << 23;\n"
            "  result := result | (shard_id << 10);\n"
            "  result := result | (seq_id);\n"
            "END;\n"
            "$$ LANGUAGE PLPGSQL;"
        )
        code = make_code_text(sql, font_size=10, t2c=PLPGSQL_T2C)
        code.move_to(LEFT * 2.5 + DOWN * 0.4)
        glow = create_rect_glow(code.bg, color=BLUE)
        self.play(FadeIn(VGroup(glow, code), shift=UP * 0.2))
        self.wait(0.8)

        # Annotations on the right
        annotations = VGroup(
            make_label("① Custom epoch — not Unix 1970", font_size=13, color=BLUE),
            make_label("② Per-schema sequence → seq_id", font_size=13, color=GREEN),
            make_label("③ ms timestamp from clock", font_size=13, color=TEAL),
            make_label("④ Bit-shift & OR to compose ID", font_size=13, color=PURPLE),
            make_label("⑤ shard_id hard-coded per schema", font_size=13, color=ORANGE),
        ).arrange(DOWN, buff=0.18, aligned_edge=LEFT)
        annotations.move_to(RIGHT * 3.5 + DOWN * 0.3)

        for a in annotations:
            self.play(FadeIn(a, shift=LEFT * 0.2), run_time=0.35)
            self.wait(0.3)

        note = make_label(
            "Each schema has its own next_id() with a unique shard_id constant",
            font_size=15,
            color=YELLOW,
        )
        note.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(note, shift=UP * 0.2))
        self.wait(3)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 7: Logical vs Physical Shards ─────────────────────────
    def scene_logical_vs_physical(self):
        header = make_label("Logical vs Physical Shards", font_size=28, color=GREEN)
        header.to_edge(UP, buff=0.5)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.5)

        # Physical servers (2 boxes)
        phys_servers = VGroup()
        for name in ["Physical Server 1", "Physical Server 2"]:
            box = RoundedRectangle(
                corner_radius=0.12,
                width=5.5,
                height=2.8,
                fill_color=DARK_BG,
                fill_opacity=0.9,
                stroke_color=TEAL,
                stroke_width=1.5,
            )
            lbl = make_label(name, font_size=14, color=TEAL)
            lbl.move_to(box.get_top() + DOWN * 0.2)
            phys_servers.add(VGroup(box, lbl))
        phys_servers.arrange(RIGHT, buff=0.6).move_to(DOWN * 0.3)

        # Logical shard chips inside each server
        colors = [BLUE, GREEN, PURPLE, ORANGE]
        for i, server in enumerate(phys_servers):
            sbox = server[0]
            schemas = VGroup()
            for j in range(4):
                idx = i * 4 + j
                chip = RoundedRectangle(
                    corner_radius=0.06,
                    width=1.05,
                    height=0.55,
                    fill_color="#21262D",
                    fill_opacity=1,
                    stroke_color=colors[j],
                    stroke_width=1,
                )
                clbl = make_label(f"schema_{idx}", font_size=8, color=colors[j])
                clbl.move_to(chip.get_center())
                schemas.add(VGroup(chip, clbl))
            schemas.arrange_in_grid(rows=2, cols=2, buff=0.12)
            schemas.move_to(sbox.get_center() + DOWN * 0.15)
            server.add(schemas)

        self.play(FadeIn(phys_servers[0], shift=RIGHT * 0.2), run_time=0.6)
        self.wait(0.5)
        self.play(FadeIn(phys_servers[1], shift=LEFT * 0.2), run_time=0.6)
        self.wait(0.8)

        # Migration arrow
        arrow = Arrow(
            phys_servers[0].get_right() + RIGHT * 0.1,
            phys_servers[1].get_left() + LEFT * 0.1,
            buff=0.05,
            stroke_width=2.5,
            color=YELLOW,
            tip_length=0.15,
        )
        move_label = make_label(
            "Move schemas\nto scale out",
            font_size=11,
            color=YELLOW,
        )
        move_label.next_to(arrow, UP, buff=0.08)
        self.play(FadeIn(arrow), FadeIn(move_label))

        note = make_label(
            "Thousands of logical shards → few physical servers. Scale = move schemas, no re-keying",
            font_size=15,
            color=YELLOW,
        )
        note.to_edge(DOWN, buff=0.45)
        self.play(FadeIn(note, shift=UP * 0.2))
        self.wait(3)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 8: Comparison Table ────────────────────────────────────
    def scene_comparison(self):
        header = make_label(
            "Comparison With Lab 2 ID Strategies",
            font_size=26,
            color=TEAL,
        )
        header.to_edge(UP, buff=0.4)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.5)

        col_labels = ["Criterion", "Auto-Inc", "UUID", "Instagram"]
        col_colors = [WHITE, BLUE, PURPLE, ORANGE]
        col_widths = [3.5, 2.5, 2.5, 3.0]

        rows_data = [
            ("Size", "8 bytes", "36 bytes", "8 bytes (bigint)"),
            ("Time-sortable", "Single DB only", "No (v4)", "Yes — by design"),
            ("Distributed safe", "Conflicts", "Best", "Yes — shard-aware"),
            ("Extra service", "No", "No", "No — in-DB PL/pgSQL"),
            ("Shard routing in ID", "No", "No", "Yes (13 bits)"),
            ("Max IDs/ms/shard", "1 (sequence)", "Unlimited", "1,024"),
        ]

        # Header row
        header_cells = VGroup()
        for text, color, width in zip(col_labels, col_colors, col_widths):
            cell = RoundedRectangle(
                corner_radius=0.06,
                width=width,
                height=0.45,
                fill_color="#21262D",
                fill_opacity=1,
                stroke_color=color,
                stroke_width=1.2,
            )
            lbl = make_label(text, font_size=13, color=color)
            lbl.move_to(cell)
            header_cells.add(VGroup(cell, lbl))
        header_cells.arrange(RIGHT, buff=0.06).next_to(header, DOWN, buff=0.25)
        self.play(FadeIn(header_cells, shift=DOWN * 0.1))
        self.wait(0.2)

        all_rows = VGroup()
        for criterion, auto, uuid, insta in rows_data:
            row = VGroup()
            for text, color, width in zip(
                [criterion, auto, uuid, insta],
                [GREY_A, BLUE_B, PURPLE, ORANGE],
                col_widths,
            ):
                cell = RoundedRectangle(
                    corner_radius=0.06,
                    width=width,
                    height=0.42,
                    fill_color=DARK_BG,
                    fill_opacity=0.9,
                    stroke_color=GREY_B,
                    stroke_width=0.6,
                )
                lbl = make_label(text, font_size=11, color=color)
                lbl.move_to(cell)
                row.add(VGroup(cell, lbl))
            row.arrange(RIGHT, buff=0.06)
            all_rows.add(row)

        all_rows.arrange(DOWN, buff=0.05).next_to(header_cells, DOWN, buff=0.05)
        for row in all_rows:
            self.play(FadeIn(row, shift=LEFT * 0.2), run_time=0.3)
            self.wait(0.12)
        self.wait(3)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 9: Key Takeaways ───────────────────────────────────────
    def scene_key_takeaways(self):
        header = make_label("Key Takeaways", font_size=28, color=YELLOW)
        header.to_edge(UP, buff=0.5)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.5)

        takeaways = [
            (BLUE, "Embed shard routing in the ID → no extra lookup"),
            (GREEN, "Custom epoch extends 41-bit timestamp to ~69 years"),
            (PURPLE, "Logical ≠ physical shards → rebalance without re-keying"),
            (ORANGE, "No new services — everything runs inside PostgreSQL"),
            (RED, "Trade-off: 1,024 IDs/ms/shard ceiling per shard"),
        ]

        items = VGroup()
        for color, text in takeaways:
            bullet = make_label("▸", font_size=16, color=color)
            lbl = make_label(text, font_size=15, color=WHITE)
            row = VGroup(bullet, lbl).arrange(RIGHT, buff=0.15)
            items.add(row)

        items.arrange(DOWN, buff=0.25, aligned_edge=LEFT)
        items.move_to(DOWN * 0.2)

        for item in items:
            self.play(FadeIn(item, shift=LEFT * 0.2), run_time=0.4)
            self.wait(0.6)

        self.wait(3)
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 10: Closing ────────────────────────────────────────────
    def scene_closing(self):
        icon = make_icon(ICON_DATABASE, color=ORANGE, height=0.8)
        title = make_label(
            "Sharding & IDs at Instagram",
            font_size=26,
            color=ORANGE,
        )
        subtitle = make_label(
            "64-bit · Time-sortable · Zero extra services",
            font_size=16,
            color=GREY_B,
        )
        source = make_label(
            "Source: instagram-engineering.com (2012)",
            font_size=12,
            color=GREY_A,
        )
        VGroup(icon, title, subtitle, source).arrange(DOWN, buff=0.3)

        self.play(FadeIn(icon, shift=DOWN * 0.2))
        self.wait(0.3)
        self.play(AddTextLetterByLetter(title, time_per_char=0.04))
        self.play(FadeIn(subtitle, shift=UP * 0.2))
        self.play(FadeIn(source, shift=UP * 0.1))
        self.wait(3)
        self.play(FadeOut(*self.mobjects))
