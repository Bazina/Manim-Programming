import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from manim import (
    BOLD,
    config,
    Scene,
    VGroup,
    RoundedRectangle,
    Line,
    FadeIn,
    FadeOut,
    AddTextLetterByLetter,
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
    DARK_BG,
    ICON_FILE,
    ICON_CODE_FILE,
    ICON_LAYERS,
    ICON_STRUCTURE,
    ICON_CHART,
    ICON_DATABASE,
    ICON_LIGHTNING,
    ICON_CHECK,
    ICON_DANGER,
    ICON_CODE,
    create_rect_glow,
    make_comparison_table,
    make_fit_box,
    make_label,
    make_icon,
)
from libs.slide_style import SlideStyleMixin

config.background_color = "#0D1117"


class Sheet2FileFormats(SlideStyleMixin, BaseSlide):

    # Avoid PyAV malloc failures on long renders.
    max_duration_before_split_reverse = 8.0

    def construct(self):
        self.scene_title()
        self.scene_intro_attributes()
        self.scene_avro()
        self.scene_protobuf()
        self.scene_messagepack()
        self.scene_thrift()
        self.scene_q1_table()
        self.scene_q1_insights()
        self.scene_q2_intro()
        self.scene_q2_case_a()
        self.scene_q2_case_b()
        self.scene_q2_case_c()
        self.scene_q2_case_d()
        self.scene_q3_parquet_intro()
        self.scene_q3_row_vs_col()
        self.scene_q3_layout()
        self.scene_q3_encodings()
        self.scene_q3_metadata()
        self.scene_closing()

    # ─── Local helpers ────────────────────────────────────────────────
    def _verdict_badge(self, text, color, width=8.0):
        box = RoundedRectangle(
            corner_radius=0.1, width=width, height=0.56,
            fill_color=DARK_BG, fill_opacity=0.95,
            stroke_color=color, stroke_width=1.8,
        )
        lbl = make_label(text, font_size=13, color=color)
        lbl.move_to(box.get_center())
        return VGroup(box, lbl)

    def _reveal_rows(self, rows, glow_indices=None, glow_color=None):
        """Sequentially reveal a list of cards; glow on selected indices.

        `_play_glow_row` already pulses Indicate + FadeIn(glow) — don't double it.
        Rows must be plain card mobjects (NOT (card, glow) tuples).
        """
        glow_indices = glow_indices or set()
        glow_map = {}
        for i in glow_indices:
            color = glow_color if glow_color else TEAL
            g = create_rect_glow(rows[i], color=color, max_opacity=0.45, spread=0.42, layers=24)
            self.add(g)
            self.bring_to_back(g)
            g.set_opacity(0)
            glow_map[i] = (g, color)
        for i, row in enumerate(rows):
            self.play(FadeIn(row, shift=RIGHT * 0.15), run_time=0.32)
            if i in glow_map:
                g, c = glow_map[i]
                self._play_glow_row(row, g, c)
            self.wait(0.1)
            if i < len(rows) - 1:
                self._next_slide(phase=True)

    # ─── Scene 1: Title ───────────────────────────────────────────────
    def scene_title(self):
        icon = make_icon(ICON_FILE, color=TEAL, height=1.1)
        title = make_label("Sheet 2: File Formats", font_size=36, color=TEAL)
        sub = make_label(
            "JSON  ·  MessagePack  ·  Avro  ·  Protobuf  ·  Thrift  ·  Parquet",
            font_size=17, color=GREY_B,
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

    # ─── Scene 2: Intro Attributes ────────────────────────────────────
    def scene_intro_attributes(self):
        header = self._section_header("File Formats — What attributes matter?", color=TEAL)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.3)

        rows = [
            self._icon_row_card(
                ICON_LAYERS, BLUE,
                "Row-oriented  vs.  Column-oriented",
                "How records are laid out on disk — full row together, or one column at a time.",
            ),
            self._icon_row_card(
                ICON_CODE_FILE, GREEN,
                "Encodings applied to data",
                "Compression schemes — RLE, dictionary, delta — shrink repetitive data on disk.",
            ),
            self._icon_row_card(
                ICON_DATABASE, ORANGE,
                "Data format on disk",
                "Binary vs. text  ·  schema embedded vs. external  ·  block layout  ·  metadata position.",
            ),
        ]
        VGroup(*rows).arrange(DOWN, buff=0.22).next_to(header, DOWN, buff=0.45)

        # Glow the encoding axis — that's the real differentiator across formats
        self._reveal_rows(rows, glow_indices={1}, glow_color=GREEN)

        note = make_label(
            "These three axes decide which format wins for a given workload.",
            font_size=11, color=YELLOW,
        )
        note.to_edge(DOWN, buff=0.35)
        self.play(FadeIn(note, shift=UP * 0.1))
        self.wait(3)
        self._next_slide()
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 3: Apache Avro ─────────────────────────────────────────
    def scene_avro(self):
        header = self._section_header("Apache Avro — Binary + Schema", color=ORANGE)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.3)

        intro = make_label(
            "Binary serialization. Metadata + schema embedded; data stored in blocks of binary records.",
            font_size=11, color=GREY_A,
        )
        intro.next_to(header, DOWN, buff=0.2)
        self.play(FadeIn(intro, shift=UP * 0.1))
        self.wait(0.4)

        rows = [
            self._icon_row_card(
                ICON_LAYERS, GREEN,
                "Schema Evolution",
                "Change schema without breaking existing data — backward + forward compatible.",
            ),
            self._icon_row_card(
                ICON_CODE, BLUE,
                "No code generation needed",
                "Use Avro data directly — no codegen step like Protobuf or Thrift.",
            ),
            self._icon_row_card(
                ICON_FILE, TEAL,
                "Self-describing messages",
                "Serialized data carries embedded schema info — decode without external schema.",
            ),
            self._icon_row_card(
                ICON_CHART, PURPLE,
                "Compression",
                "Block-level compression — efficient for large datasets at scale.",
            ),
            self._icon_row_card(
                ICON_DANGER, RED,
                "Cons: Schema overhead per record",
                "Each serialized record may carry schema bytes — bloats single small messages.",
            ),
        ]
        VGroup(*rows).arrange(DOWN, buff=0.13).next_to(intro, DOWN, buff=0.3)

        self._reveal_rows(rows, glow_indices={0}, glow_color=GREEN)

        self.wait(2.5)
        self._next_slide()
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 4: Google Protobuf ─────────────────────────────────────
    def scene_protobuf(self):
        header = self._section_header("Google Protobuf — Speed + Codegen", color=BLUE)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.3)

        intro = make_label(
            "Binary on disk. Schema lives in a separate .proto file; supports schema evolution.",
            font_size=11, color=GREY_A,
        )
        intro.next_to(header, DOWN, buff=0.2)
        self.play(FadeIn(intro, shift=UP * 0.1))
        self.wait(0.4)

        rows = [
            self._icon_row_card(
                ICON_LIGHTNING, YELLOW,
                "Efficiency",
                "Highly efficient ser/deser speed — built for high-performance scenarios.",
            ),
            self._icon_row_card(
                ICON_LAYERS, GREEN,
                "Schema Management + Versioning",
                "Backward + forward compatibility of data structures via field numbers.",
            ),
            self._icon_row_card(
                ICON_CODE, TEAL,
                "Cross-language support",
                "Libraries for many languages — interop across heterogeneous systems.",
            ),
            self._icon_row_card(
                ICON_DANGER, RED,
                "Cons: Codegen required",
                "Must run protoc to generate language bindings — adds build step.",
            ),
            self._icon_row_card(
                ICON_DANGER, ORANGE,
                "Cons: Data size at scale",
                "Larger than Avro on bulk-message workloads (no block-level compression).",
            ),
        ]
        VGroup(*rows).arrange(DOWN, buff=0.13).next_to(intro, DOWN, buff=0.3)

        self._reveal_rows(rows, glow_indices={0}, glow_color=YELLOW)

        self.wait(2.5)
        self._next_slide()
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 5: MessagePack ─────────────────────────────────────────
    def scene_messagepack(self):
        header = self._section_header("MessagePack — Compact Schemaless Binary", color=PURPLE)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.3)

        intro = make_label(
            "Schemaless binary serialization. Byte sequence; no metadata; lightweight for streaming.",
            font_size=11, color=GREY_A,
        )
        intro.next_to(header, DOWN, buff=0.2)
        self.play(FadeIn(intro, shift=UP * 0.1))
        self.wait(0.4)

        rows = [
            self._icon_row_card(
                ICON_FILE, GREEN,
                "Compactness",
                "Tight binary format — small footprint reduces network + storage cost.",
            ),
            self._icon_row_card(
                ICON_CHECK, TEAL,
                "Simplicity",
                "No schema definitions — drop-in for ad-hoc serialization tasks.",
            ),
            self._icon_row_card(
                ICON_CODE, BLUE,
                "Interoperability",
                "Libraries available across many programming languages.",
            ),
            self._icon_row_card(
                ICON_DANGER, RED,
                "Cons: Schemaless — managing versions is on you",
                "No schema = no automatic compatibility checks — versioning becomes app-level concern.",
            ),
        ]
        VGroup(*rows).arrange(DOWN, buff=0.14).next_to(intro, DOWN, buff=0.3)

        self._reveal_rows(rows, glow_indices={0, 3}, glow_color=ORANGE)

        self.wait(2.5)
        self._next_slide()
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 6: Apache Thrift ───────────────────────────────────────
    def scene_thrift(self):
        header = self._section_header("Apache Thrift — Binary + RPC", color=GREEN)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.3)

        intro = make_label(
            "Framework for data types + cross-language RPC. Binary encoding via Thrift protocol.",
            font_size=11, color=GREY_A,
        )
        intro.next_to(header, DOWN, buff=0.2)
        self.play(FadeIn(intro, shift=UP * 0.1))
        self.wait(0.4)

        rows = [
            self._icon_row_card(
                ICON_LIGHTNING, YELLOW,
                "Efficient binary encoding",
                "Compact serialized form — good for high-performance services.",
            ),
            self._icon_row_card(
                ICON_CODE, BLUE,
                "Code generation across languages",
                "Generates bindings for many languages — seamless integration with existing codebases.",
            ),
            self._icon_row_card(
                ICON_LAYERS, TEAL,
                "Built-in RPC support",
                "First-class Remote Procedure Calls — built for distributed systems.",
            ),
            self._icon_row_card(
                ICON_DANGER, RED,
                "Cons: Codegen required",
                "Like Protobuf — needs a generation step in your build.",
            ),
        ]
        VGroup(*rows).arrange(DOWN, buff=0.14).next_to(intro, DOWN, buff=0.3)

        self._reveal_rows(rows, glow_indices={2}, glow_color=TEAL)

        self.wait(2.5)
        self._next_slide()
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 7: Q1 Size Table ───────────────────────────────────────
    def scene_q1_table(self):
        header = self._section_header("Q1: File Size Comparison", color=TEAL)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.3)

        sub = make_label(
            "Same SVG-viewer menu JSON, encoded with 1 message vs. 100 repeated messages.",
            font_size=11, color=GREY_A,
        )
        sub.next_to(header, DOWN, buff=0.2)
        self.play(FadeIn(sub, shift=UP * 0.1))
        self.wait(0.3)

        # Winners — Protobuf for 1-message, Avro for 100-message
        winner_1msg_idx = 3
        winner_100_idx = 2

        formats = [
            ("JSON",        "618 (compact)", "65,800", GREY_A),
            ("MessagePack", "451",            "44,703", PURPLE),
            ("Avro",        "897",            "32,263", ORANGE),
            ("Protobuf",    "350",            "35,000", BLUE),
            ("Thrift",      "493",            "49,300", GREEN),
        ]

        rows_data = []
        for i, (fmt, s1, s100, color) in enumerate(formats):
            s1_color = BLUE if i == winner_1msg_idx else GREY_A
            s100_color = ORANGE if i == winner_100_idx else GREY_A
            rows_data.append((fmt, color, s1, s1_color, s100, s100_color))

        table = make_comparison_table(
            col_headers     = ["Format", "1 message (B)", "100 messages (B)"],
            col_colors      = [TEAL, TEAL, TEAL],
            col_x_positions = [-4.6, -1.0, 2.6],
            rows_data       = rows_data,
        )
        table.next_to(sub, DOWN, buff=0.4)
        hdrs_grp, div, body_rows = table[0], table[1], table[2]

        self.play(FadeIn(hdrs_grp), FadeIn(div))
        self.wait(0.3)

        # Per-column glow on winners
        winner_p_row = body_rows[winner_1msg_idx]
        winner_a_row = body_rows[winner_100_idx]
        p_glow = create_rect_glow(winner_p_row[1], color=BLUE, max_opacity=0.32, spread=0.4)
        a_glow = create_rect_glow(winner_a_row[2], color=ORANGE, max_opacity=0.32, spread=0.4)
        for g in (p_glow, a_glow):
            self.add(g)
            self.bring_to_back(g)
            g.set_opacity(0)

        for i, row in enumerate(body_rows):
            self.play(FadeIn(row, shift=RIGHT * 0.15), run_time=0.4)
            if i == winner_1msg_idx:
                self._play_glow_row(row[1], p_glow, BLUE)
            if i == winner_100_idx:
                self._play_glow_row(row[2], a_glow, ORANGE)
            if i < len(body_rows) - 1:
                self._next_slide(phase=True)

        # Winner badges — stacked below the table so they don't overlap cells
        badges = VGroup(
            make_label(
                "↑ Protobuf wins (smallest single message)",
                font_size=13, color=BLUE,
            ),
            make_label(
                "↑ Avro wins at scale (smallest at 100 messages)",
                font_size=13, color=ORANGE,
            ),
        ).arrange(DOWN, buff=0.18)
        badges.next_to(body_rows[-1], DOWN, buff=0.5)
        badges.set_x(0)
        self._next_slide(phase=True)
        self.play(FadeIn(badges[0], shift=UP * 0.1))
        self.wait(0.4)
        self.play(FadeIn(badges[1], shift=UP * 0.1))
        self.wait(0.5)

        note = make_label(
            "Single message → Protobuf (no schema bytes).   100 messages → Avro (block compression amortizes schema).",
            font_size=11, color=YELLOW,
        )
        note.to_edge(DOWN, buff=0.4)
        self.play(FadeIn(note, shift=UP * 0.1))
        self.wait(3.5)
        self._next_slide()
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 8: Q1 Insights ─────────────────────────────────────────
    def scene_q1_insights(self):
        header = self._section_header("Q1: Key Insights", color=YELLOW)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.3)

        rows = [
            self._icon_row_card(
                ICON_CHECK, GREEN,
                "Use JSON unless you have a storage problem",
                "Human-readable + ubiquitous tooling — pick binary only when bytes truly matter.",
            ),
            self._icon_row_card(
                ICON_DANGER, RED,
                "Lots of repeated fields across rows? Avoid:",
                "Thrift, Protobuf, MessagePack — they don't exploit inter-message repetition.",
            ),
            self._icon_row_card(
                ICON_LAYERS, ORANGE,
                "Avro + Protobuf compress across messages",
                "They exploit consecutive-message patterns — pay off as batch size grows.",
            ),
            self._icon_row_card(
                ICON_FILE, BLUE,
                "Avro pays metadata cost per message",
                "Hurts single-message workloads, amortizes across large batches.",
            ),
            self._icon_row_card(
                ICON_CHART, PURPLE,
                "100 messages is not enough to draw final conclusions",
                "Real benchmarks: Avro hits ~50% compression on 50 GB Reddit dataset.",
            ),
        ]
        VGroup(*rows).arrange(DOWN, buff=0.14).next_to(header, DOWN, buff=0.4)

        self._reveal_rows(rows, glow_indices={0}, glow_color=GREEN)

        self.wait(3)
        self._next_slide()
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 9: Q2 Intro ────────────────────────────────────────────
    def scene_q2_intro(self):
        header = self._section_header("Q2: Avro Schema Evolution", color=ORANGE)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.3)

        sub = make_label(
            "Original Employee schema — analyze 4 modifications for Backward + Forward compat.",
            font_size=11, color=GREY_A,
        )
        sub.next_to(header, DOWN, buff=0.2)
        self.play(FadeIn(sub, shift=UP * 0.1))
        self.wait(0.3)

        orig_code = self._code_box(
            [
                "record Employee {",
                "    string address = \"Egypt\"",
                "    long   salary;",
                "    string name;",
                "}",
            ],
            title="Original Schema",
            color=TEAL,
            width=7.5,
            font_size=12,
            language="text",
        )
        orig_code.next_to(sub, DOWN, buff=0.4)
        self.play(FadeIn(orig_code, shift=UP * 0.15))
        self.wait(0.4)

        # Definitions of Backward / Forward
        defs = VGroup(
            self._icon_row_card(
                ICON_LAYERS, BLUE,
                "Backward compatibility",
                "New reader can read OLD data — new schema reads records written with old schema.",
            ),
            self._icon_row_card(
                ICON_LAYERS, GREEN,
                "Forward compatibility",
                "Old reader can read NEW data — old schema reads records written with new schema.",
            ),
        ).arrange(DOWN, buff=0.16)
        defs.next_to(orig_code, DOWN, buff=0.35)

        self.play(FadeIn(defs[0], shift=RIGHT * 0.1))
        self._next_slide(phase=True)
        self.play(FadeIn(defs[1], shift=RIGHT * 0.1))
        self.wait(2)
        self._next_slide()
        self.play(FadeOut(*self.mobjects))

    # ─── Q2 case helper ──────────────────────────────────────────────
    def _q2_case(self, case_label, new_schema_lines, backward_text, backward_ok,
                 forward_text, forward_ok, glow_target=None):
        header = self._section_header(f"Q2.{case_label}: Schema Change", color=ORANGE)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.3)

        # Two-column: old | new
        old_code = self._code_box(
            [
                "record Employee {",
                "    string address = \"Egypt\"",
                "    long   salary;",
                "    string name;",
                "}",
            ],
            title="Original",
            color=GREY_B,
            width=5.4,
            font_size=11,
            language="text",
        )
        new_code = self._code_box(
            new_schema_lines,
            title=f"Modified ({case_label})",
            color=TEAL,
            width=5.4,
            font_size=11,
            language="text",
        )
        codes = VGroup(old_code, new_code).arrange(RIGHT, buff=0.4)
        codes.next_to(header, DOWN, buff=0.35)

        self.play(FadeIn(old_code, shift=RIGHT * 0.1))
        self._next_slide(phase=True)
        self.play(FadeIn(new_code, shift=LEFT * 0.1))
        self.wait(0.4)

        # Verdict cards
        b_color = GREEN if backward_ok else RED
        f_color = GREEN if forward_ok else RED
        b_card = self._icon_row_card(
            ICON_CHECK if backward_ok else ICON_DANGER,
            b_color,
            f"Backward: {'OK' if backward_ok else 'BROKEN'}",
            backward_text,
        )
        f_card = self._icon_row_card(
            ICON_CHECK if forward_ok else ICON_DANGER,
            f_color,
            f"Forward: {'OK' if forward_ok else 'BROKEN'}",
            forward_text,
        )
        verdicts = VGroup(b_card, f_card).arrange(DOWN, buff=0.16)
        verdicts.next_to(codes, DOWN, buff=0.35)

        # Glow on breaking changes
        glow_indices = set()
        if not backward_ok:
            glow_indices.add(0)
        if not forward_ok:
            glow_indices.add(1)

        rows = [b_card, f_card]
        glow_map = {}
        for i in glow_indices:
            color = RED
            g = create_rect_glow(rows[i], color=color, max_opacity=0.3, spread=0.34)
            self.add(g)
            self.bring_to_back(g)
            g.set_opacity(0)
            glow_map[i] = (g, color)

        for i, row in enumerate(rows):
            self.play(FadeIn(row, shift=RIGHT * 0.15), run_time=0.4)
            if i in glow_map:
                g, c = glow_map[i]
                self._play_glow_row(row, g, c)
            if i < len(rows) - 1:
                self._next_slide(phase=True)

        self.wait(3)
        self._next_slide()
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 10: Q2.a ───────────────────────────────────────────────
    def scene_q2_case_a(self):
        self._q2_case(
            "a",
            [
                "record Employee {",
                "    string name;",
                "    string family_name;",
                "    union { null, long } salary;",
                "    long   age;",
                "}",
            ],
            backward_text="Old records lack family_name + age — new reader cannot fill them in.",
            backward_ok=False,
            forward_text="Old reader discards family_name + age — fields it does not know about.",
            forward_ok=True,
        )

    # ─── Scene 11: Q2.b ───────────────────────────────────────────────
    def scene_q2_case_b(self):
        self._q2_case(
            "b",
            [
                "record Employee {",
                "    long   salary;",
                "    string name;",
                "}",
            ],
            backward_text="Only an optional field (address) was removed — new reader skips it.",
            backward_ok=True,
            forward_text="Old reader still sees salary + name — removed optional has no effect.",
            forward_ok=True,
        )

    # ─── Scene 12: Q2.c ───────────────────────────────────────────────
    def scene_q2_case_c(self):
        self._q2_case(
            "c",
            [
                "record Employee {",
                "    string  name;",
                "    boolean active = true;",
                "    long    salary;",
                "}",
            ],
            backward_text="Old records have no `active` — default `true` fills in cleanly.",
            backward_ok=True,
            forward_text="Old reader doesn't know `active` — simply ignores the new field.",
            forward_ok=True,
        )

    # ─── Scene 13: Q2.d ───────────────────────────────────────────────
    def scene_q2_case_d(self):
        header = self._section_header("Q2.d: External Tool Verification", color=PURPLE)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.3)

        sub = make_label(
            "Validate manual analysis with an automated Avro compatibility checker.",
            font_size=11, color=GREY_A,
        )
        sub.next_to(header, DOWN, buff=0.2)
        self.play(FadeIn(sub, shift=UP * 0.1))
        self.wait(0.3)

        tool_card = self._card(
            "ExpediaGroup/avro-compatibility",
            "User-friendly API for checking + reporting Avro schema incompatibilities.\n"
            "Open repo in IntelliJ → Compatibility class → paste main → run → observe output.",
            color=TEAL, width=11.0,
        )
        tool_card.next_to(sub, DOWN, buff=0.4)
        self.play(FadeIn(tool_card, shift=UP * 0.15))
        self.wait(0.5)

        rows = [
            self._icon_row_card(
                ICON_CHECK, GREEN,
                "Confirms our manual analysis on cases a, b, c",
                "Programmatic verdicts match what we derived by hand.",
            ),
            self._icon_row_card(
                ICON_DANGER, YELLOW,
                "If a tool disagrees with you — do not edit your answer",
                "Discuss the discrepancy with the TA; understanding the gap is the point.",
            ),
        ]
        VGroup(*rows).arrange(DOWN, buff=0.16).next_to(tool_card, DOWN, buff=0.35)

        self._reveal_rows(rows, glow_indices={0}, glow_color=GREEN)

        self.wait(3)
        self._next_slide()
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 14: Q3 Parquet Intro ───────────────────────────────────
    def scene_q3_parquet_intro(self):
        header = self._section_header("Q3: Parquet — Columnar Storage", color=BLUE)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.3)

        intro = make_label(
            "Optimized for storing + querying large analytical datasets.",
            font_size=12, color=GREY_A,
        )
        intro.next_to(header, DOWN, buff=0.2)
        self.play(FadeIn(intro, shift=UP * 0.1))
        self.wait(0.3)

        rows = [
            self._icon_row_card(
                ICON_LAYERS, TEAL,
                "Files organized columnar-fashion on disk",
                "Each column stored separately — read only the columns your query needs.",
            ),
            self._icon_row_card(
                ICON_STRUCTURE, ORANGE,
                "Row groups → column chunks",
                "File split into row groups; within each, every column stored as its own chunk.",
            ),
            self._icon_row_card(
                ICON_CODE_FILE, GREEN,
                "Per-column encoding + compression",
                "RLE, Dictionary, Delta — each column compressed independently by data shape.",
            ),
            self._icon_row_card(
                ICON_CHART, PURPLE,
                "Rich metadata: schema + statistics",
                "File + row-group metadata, column min/max stats enable query pruning.",
            ),
        ]
        VGroup(*rows).arrange(DOWN, buff=0.14).next_to(intro, DOWN, buff=0.35)

        # Glow the columnar layout — Parquet's defining feature
        self._reveal_rows(rows, glow_indices={0, 1}, glow_color=TEAL)

        self.wait(3)
        self._next_slide()
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 14b: Row vs Column storage (borrowed from olap_lab) ───
    def scene_q3_row_vs_col(self):
        header = self._section_header("Row vs Column Storage", color=YELLOW)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.3)

        # --- Row-Oriented side ---
        row_title = make_label("Row-Oriented", font_size=15, color=GREY_A, weight=BOLD)
        row_data = [
            ("Ahmed", "30", "Engineer"),
            ("Sara",  "25", "Doctor"),
            ("Omar",  "35", "Engineer"),
        ]
        row_entries = VGroup()
        for name, age, job in row_data:
            n = make_label(name, font_size=11, color=BLUE)
            a = make_label(age, font_size=11, color=ORANGE)
            j = make_label(job, font_size=11, color=GREEN)
            s1 = make_label(",", font_size=11, color=GREY_B)
            s2 = make_label(",", font_size=11, color=GREY_B)
            row_line = VGroup(n, s1, a, s2, j).arrange(RIGHT, buff=0.06)
            entry_box = RoundedRectangle(
                corner_radius=0.06, width=row_line.width + 0.3, height=0.35,
                fill_color="#1E1E1E", fill_opacity=0.95,
                stroke_color=GREY_B, stroke_width=1,
            )
            row_line.move_to(entry_box.get_center())
            row_entries.add(VGroup(entry_box, row_line))
        row_entries.arrange(DOWN, buff=0.08)

        disk_row_lbl = make_label("On disk:", font_size=10, color=GREY_B)
        disk_row_val = make_label(
            "Ahmed,30,Eng | Sara,25,Doc | Omar,35,Eng",
            font_size=9, color=GREY_B,
        )
        disk_row = VGroup(disk_row_lbl, disk_row_val).arrange(DOWN, buff=0.04)

        row_content = VGroup(row_title, row_entries, disk_row).arrange(DOWN, buff=0.15)
        row_box = RoundedRectangle(
            corner_radius=0.12, width=5.0, height=3.2,
            fill_color=DARK_BG, fill_opacity=0.9, stroke_color=GREY_B, stroke_width=1.5,
        )
        row_content.move_to(row_box.get_center())
        row_group = VGroup(row_box, row_content).move_to(LEFT * 3.2 + DOWN * 0.4)

        # --- Column-Oriented side ---
        col_title = make_label("Column-Oriented", font_size=15, color=GREEN, weight=BOLD)
        col_headers = ["Name", "Age", "Job"]
        col_values = [
            ["Ahmed", "Sara", "Omar"],
            ["30", "25", "35"],
            ["Engineer", "Doctor", "Engineer"],
        ]
        col_hdr_colors = [BLUE, ORANGE, GREEN]

        col_groups = VGroup()
        for hdr, vals, c in zip(col_headers, col_values, col_hdr_colors):
            h = make_label(hdr, font_size=11, color=c, weight=BOLD)
            val_labels = VGroup(*[make_label(v, font_size=10, color=c) for v in vals])
            val_labels.arrange(DOWN, buff=0.06)
            col_entry = VGroup(h, val_labels).arrange(DOWN, buff=0.1)
            col_bg = RoundedRectangle(
                corner_radius=0.06,
                width=col_entry.width + 0.25,
                height=col_entry.height + 0.2,
                fill_color="#1E1E1E", fill_opacity=0.95,
                stroke_color=c, stroke_width=1,
            )
            col_entry.move_to(col_bg.get_center())
            col_groups.add(VGroup(col_bg, col_entry))
        col_groups.arrange(RIGHT, buff=0.12)

        disk_col_lbl = make_label("On disk:", font_size=10, color=GREY_B)
        disk_col_val = make_label(
            "Ahmed,Sara,Omar | 30,25,35 | Eng,Doc,Eng",
            font_size=9, color=GREY_B,
        )
        disk_col = VGroup(disk_col_lbl, disk_col_val).arrange(DOWN, buff=0.04)

        col_content = VGroup(col_title, col_groups, disk_col).arrange(DOWN, buff=0.15)
        col_box = RoundedRectangle(
            corner_radius=0.12, width=5.0, height=3.2,
            fill_color=DARK_BG, fill_opacity=0.9, stroke_color=GREEN, stroke_width=1.5,
        )
        col_content.move_to(col_box.get_center())
        col_card = VGroup(col_box, col_content).move_to(RIGHT * 3.2 + DOWN * 0.4)

        self.play(FadeIn(row_group, shift=RIGHT * 0.3))
        self.wait(1.0)
        self._next_slide(phase=True)
        self.play(FadeIn(col_card, shift=LEFT * 0.3))
        self.wait(0.5)

        # Glow + Indicate the column side as the winner for analytics
        col_glow = create_rect_glow(col_box, color=GREEN, max_opacity=0.4, spread=0.4)
        self.add(col_glow)
        self.bring_to_back(col_glow)
        col_glow.set_opacity(0)
        self._play_glow_row(col_card, col_glow, GREEN)

        verdict = make_label(
            "Parquet = Column-Oriented → better compression & faster analytics",
            font_size=14, color=GREEN,
        )
        verdict.to_edge(DOWN, buff=0.35)
        self.play(FadeIn(verdict, shift=UP * 0.15))
        self.wait(3)
        self._next_slide()
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 15: Q3.a Layout ────────────────────────────────────────
    def scene_q3_layout(self):
        header = self._section_header("Q3.a: Parquet Layout — Row-Oriented or Column-Oriented?", color=BLUE)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.3)

        # Nested visual: Row Group → Column Chunks → (Data/Dict/Index Pages)
        rg_color = BLUE
        col_colors = [TEAL, GREEN, PURPLE]
        col_names = ["col Name", "col Age", "col Job"]

        def _col_chunk(name, color):
            hdr = make_label(name, font_size=9, color=color, weight=BOLD)
            pages = VGroup()
            for pname, pcolor in [
                ("Data Page",  GREY_A),
                ("Dict Page",  YELLOW),
                ("Index Page", TEAL),
            ]:
                plbl = make_label(pname, font_size=7, color=pcolor)
                pbox = RoundedRectangle(
                    corner_radius=0.04, width=1.6, height=0.26,
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

        chunks = VGroup(*[_col_chunk(n, c) for n, c in zip(col_names, col_colors)])
        chunks.arrange(RIGHT, buff=0.18)

        rg_label = make_label(
            "Row Group  (block of rows)", font_size=11, color=rg_color, weight=BOLD,
        )
        rg_content = VGroup(rg_label, chunks).arrange(DOWN, buff=0.1)
        rg_box = RoundedRectangle(
            corner_radius=0.1,
            width=rg_content.width + 0.4, height=rg_content.height + 0.25,
            fill_color="#111820", fill_opacity=0.9,
            stroke_color=rg_color, stroke_width=1.5,
        )
        rg_content.move_to(rg_box.get_center())
        rg_group = VGroup(rg_box, rg_content)

        more_rg = make_label("... more Row Groups ...", font_size=10, color=GREY_B)
        footer = make_label("FOOTER  (metadata · stats · offsets)", font_size=11, color=TEAL)
        footer_box = RoundedRectangle(
            corner_radius=0.08, width=rg_group.width, height=0.45,
            fill_color="#161B22", fill_opacity=0.9,
            stroke_color=TEAL, stroke_width=1.4,
        )
        footer.move_to(footer_box.get_center())
        footer_group = VGroup(footer_box, footer)

        file_inner = VGroup(rg_group, more_rg, footer_group).arrange(DOWN, buff=0.3)
        file_box = RoundedRectangle(
            corner_radius=0.15,
            width=file_inner.width + 0.7, height=file_inner.height + 1.2,
            fill_color="#0F1318", fill_opacity=0.95,
            stroke_color=BLUE, stroke_width=2,
        )
        file_label = make_label("Parquet File", font_size=14, color=BLUE, weight=BOLD)
        file_label.next_to(file_box, UP, buff=0.08)
        file_inner.move_to(file_box.get_center())

        whole = VGroup(file_label, file_box, file_inner)
        whole.next_to(header, DOWN, buff=0.4)

        self.play(FadeIn(file_box), FadeIn(file_label))
        self.wait(0.3)
        self.play(FadeIn(rg_box), FadeIn(rg_label))
        self.wait(0.2)
        self.play(AnimationGroup(*[FadeIn(c, shift=UP * 0.15) for c in chunks], lag_ratio=0.15))
        self.wait(0.5)
        self._next_slide(phase=True)
        self.play(FadeIn(more_rg))
        self.wait(0.2)
        self.play(FadeIn(footer_group, shift=UP * 0.1))

        # Glow the hybrid structure — row group is row-partitioned, chunks are columnar
        rg_glow = create_rect_glow(rg_box, color=rg_color, max_opacity=0.4, spread=0.4)
        self.add(rg_glow)
        self.bring_to_back(rg_glow)
        rg_glow.set_opacity(0)
        self._play_glow_row(rg_group, rg_glow, rg_color)

        # Verdict
        verdict = self._verdict_badge(
            "HYBRID — row groups (row-oriented partitioning) + column chunks inside",
            ORANGE, width=10.5,
        )
        verdict.to_edge(DOWN, buff=0.3)
        glow = create_rect_glow(verdict, color=ORANGE, max_opacity=0.3, spread=0.4)
        self.add(glow)
        self.bring_to_back(glow)
        glow.set_opacity(0)
        self.play(FadeIn(verdict, shift=UP * 0.15))
        self._play_glow_row(verdict, glow, ORANGE)

        self.wait(3)
        self._next_slide()
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 16: Q3.b Encodings ─────────────────────────────────────
    def scene_q3_encodings(self):
        header = self._section_header("Q3.b: Per-Column Encodings", color=GREEN)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.3)

        sub = make_label(
            "Three classic encodings — each exploits a different data pattern.",
            font_size=11, color=GREY_A,
        )
        sub.next_to(header, DOWN, buff=0.2)
        self.play(FadeIn(sub, shift=UP * 0.1))
        self.wait(0.3)

        # Three compact rows: name + 1-line example, side-by-side encoded result
        def _enc_row(name, desc, before, after, color):
            t = make_label(name, font_size=12, color=color)
            d = make_label(desc, font_size=10, color=GREY_A)
            head_col = VGroup(t, d).arrange(DOWN, buff=0.04, aligned_edge=LEFT)
            before_lbl = make_label(before, font_size=10, color=GREY_B)
            arrow_lbl = make_label("→", font_size=12, color=color)
            after_lbl = make_label(after, font_size=10, color=color)
            ex_row = VGroup(before_lbl, arrow_lbl, after_lbl).arrange(RIGHT, buff=0.18)
            content = VGroup(head_col, ex_row).arrange(DOWN, buff=0.08, aligned_edge=LEFT)
            return make_fit_box(content, color, pad_x=0.5, pad_y=0.22)

        c1 = _enc_row(
            "Run-Length Encoding (RLE)",
            "Collapse runs of repeated values into (value → count).",
            "1,1,1,2,2,2,2,2",
            "1→3,  2→5",
            TEAL,
        )
        c2 = _enc_row(
            "Dictionary Encoding",
            "Map distinct values to small integer codes.",
            "EGY,EGY,EGY,KSA,KSA",
            "EGY→1, KSA→2  ⇒  1,1,1,2,2",
            ORANGE,
        )
        c3 = _enc_row(
            "Delta Encoding",
            "Store differences from the previous value.",
            "10001, 10002, 10003",
            "base 10000  ⇒  1, 0, 0",
            PURPLE,
        )

        cards = VGroup(c1, c2, c3).arrange(DOWN, buff=0.18, aligned_edge=LEFT)
        cards.next_to(sub, DOWN, buff=0.35)

        rows = [c1, c2, c3]
        # Glow Dictionary encoding — usually the biggest win on real columnar data
        self._reveal_rows(rows, glow_indices={1}, glow_color=ORANGE)

        self.wait(3)
        self._next_slide()
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 17: Q3.c Metadata position ─────────────────────────────
    def scene_q3_metadata(self):
        header = self._section_header("Q3.c: Where Does Metadata Live?", color=PURPLE)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))
        self.wait(0.3)

        # Visual: file as a stacked rectangle, metadata block at bottom
        file_box = RoundedRectangle(
            corner_radius=0.12, width=4.5, height=5.6,
            fill_color="#161B22", fill_opacity=0.7,
            stroke_color=GREY_B, stroke_width=1.4,
        )
        file_box.move_to(LEFT * 3.5 + DOWN * 0.3)
        file_lbl = make_label("Parquet File", font_size=11, color=GREY_A)
        file_lbl.next_to(file_box, UP, buff=0.1)

        blocks_data = [
            ("Header (magic 'PAR1')", GREY_B, 0.45),
            ("Row Group 1\n(column chunks)", BLUE, 1.05),
            ("Row Group 2\n(column chunks)", ORANGE, 1.05),
            ("Row Group N\n…", TEAL, 0.8),
            ("FOOTER: Metadata\nschema · stats · offsets", PURPLE, 0.85),
        ]
        block_grp = VGroup()
        for txt, color, h in blocks_data:
            b = RoundedRectangle(
                corner_radius=0.06, width=4.2, height=h,
                fill_color=DARK_BG, fill_opacity=0.95,
                stroke_color=color, stroke_width=1.2,
            )
            l = make_label(txt, font_size=9, color=color)
            l.move_to(b.get_center())
            block_grp.add(VGroup(b, l))
        block_grp.arrange(DOWN, buff=0.06).move_to(file_box.get_center())

        footer_block = block_grp[-1]
        glow = create_rect_glow(footer_block, color=PURPLE, max_opacity=0.35, spread=0.4)
        self.add(glow)
        self.bring_to_back(glow)
        glow.set_opacity(0)

        self.play(FadeIn(file_lbl), FadeIn(file_box))
        for blk in block_grp:
            self.play(FadeIn(blk, shift=UP * 0.1), run_time=0.32)
        self._play_glow_row(footer_block, glow, PURPLE)
        self.wait(0.3)

        # Explanation cards on the right
        rows = [
            self._icon_row_card(
                ICON_FILE, PURPLE,
                "Metadata sits at the END of the file",
                "Footer holds schema, row-group offsets, per-column statistics.",
            ),
            self._icon_row_card(
                ICON_LIGHTNING, YELLOW,
                "Why? Enables one-pass write",
                "Writer streams data forward; doesn't need to rewind to update a header.",
            ),
            self._icon_row_card(
                ICON_CHART, GREEN,
                "Statistics need all the data first",
                "min/max/count per column only known after every record is processed.",
            ),
            self._icon_row_card(
                ICON_STRUCTURE, BLUE,
                "Reader seeks to the end first",
                "Loads footer, then jumps to the row groups + columns needed for the query.",
            ),
        ]
        cards = VGroup(*rows).arrange(DOWN, buff=0.14)
        cards.set_width(6.0)
        cards.next_to(file_box, RIGHT, buff=0.5)

        self._reveal_rows(rows, glow_indices={0}, glow_color=PURPLE)

        self.wait(3)
        self._next_slide()
        self.play(FadeOut(*self.mobjects))

    # ─── Scene 18: Closing ────────────────────────────────────────────
    def scene_closing(self):
        title = make_label("Sheet 2: File Formats", font_size=34, color=TEAL)
        title.move_to(UP * 1.8)
        self.play(AddTextLetterByLetter(title, time_per_char=0.05))
        self.wait(0.6)

        icon_data = [
            (ICON_FILE,       TEAL),
            (ICON_CODE_FILE,  BLUE),
            (ICON_LAYERS,     ORANGE),
            (ICON_STRUCTURE,  GREEN),
            (ICON_CHART,      PURPLE),
        ]
        icons_row = (
            VGroup(*[make_icon(p, color=c, height=0.5) for p, c in icon_data])
            .arrange(RIGHT, buff=0.55)
            .move_to(ORIGIN)
        )
        self.play(
            AnimationGroup(*[FadeIn(ic, shift=UP * 0.2) for ic in icons_row], lag_ratio=0.1)
        )
        self.wait(0.8)

        themes = make_label(
            "Avro  ·  Protobuf  ·  MessagePack  ·  Thrift  ·  Parquet",
            font_size=17, color=GREY_A,
        )
        themes.move_to(DOWN * 1.3)
        takeaway = make_label(
            "Pick the format for your workload: single message? bulk batch? analytical scan?",
            font_size=12, color=YELLOW,
        )
        takeaway.move_to(DOWN * 2.0)
        self.play(FadeIn(themes, shift=UP * 0.2))
        self.play(FadeIn(takeaway, shift=UP * 0.15))
        self.wait(4)
        self._next_slide()
        self.play(FadeOut(*self.mobjects))
