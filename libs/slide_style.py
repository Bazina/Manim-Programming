"""Shared visual + slide-checkpoint helpers for DDIA presentations.

All DDIA scene classes mix this in to inherit the canonical card / row / flow
helpers used by `ddia/section_7/project_weather_stations.py` and to delegate
slide checkpoints to `libs.slide_controls.slide_checkpoint`.

Subclasses can override any method or class attribute.
"""

from manim import (
    DOWN,
    GREY_A,
    LEFT,
    RIGHT,
    TEAL,
    UP,
    Arrow,
    FadeIn,
    Indicate,
    RoundedRectangle,
    VGroup,
)

from libs.ddia_components import (
    DARK_BG,
    make_code_text,
    make_fit_box,
    make_icon,
    make_label,
)
from libs.slide_controls import slide_checkpoint


class SlideStyleMixin:
    slide_stop_mode = "phase"
    max_duration_before_split_reverse = 4.0

    def _card(
        self, title, desc, color, width=11.5, height=None, title_size=13, desc_size=11
    ):
        t = make_label(title, font_size=title_size, color=color)
        d = make_label(desc, font_size=desc_size, color=GREY_A)
        content = VGroup(t, d).arrange(DOWN, buff=0.12, aligned_edge=LEFT)
        h = height or content.height + 0.42
        box = RoundedRectangle(
            corner_radius=0.09,
            width=width,
            height=h,
            fill_color=DARK_BG,
            fill_opacity=0.9,
            stroke_color=color,
            stroke_width=1.3,
        )
        content.move_to(box.get_center())
        return VGroup(box, content)

    def _icon_row_card(self, icon_path, color, title, desc, glow=False):
        ic = make_icon(icon_path, color=color, height=0.32)
        t = make_label(title, font_size=13, color=color)
        d = make_label(desc, font_size=11, color=GREY_A)
        text_col = VGroup(t, d).arrange(DOWN, buff=0.05, aligned_edge=LEFT)
        content = VGroup(ic, text_col).arrange(RIGHT, buff=0.22)
        return make_fit_box(
            content,
            color,
            pad_x=0.85,
            pad_y=max(0.36, 0.75 - content.height),
            glow=glow,
        )

    def _play_glow_row(self, row, glow, color):
        """Pulse card with Indicate then bloom the glow in the same beat."""
        self.play(
            Indicate(row, color=color, scale_factor=1.04, run_time=0.7),
            FadeIn(glow, run_time=1.0),
        )

    def _flow_node(self, label, color, width=2.2, height=0.9):
        box = RoundedRectangle(
            corner_radius=0.1,
            width=width,
            height=height,
            fill_color=DARK_BG,
            fill_opacity=0.9,
            stroke_color=color,
            stroke_width=1.5,
        )
        lbl = make_label(label, font_size=10, color=color)
        lbl.move_to(box.get_center())
        return VGroup(box, lbl)

    def _flow_arrow(self, left_node, right_node, color=GREY_A, label=None, label_dir=UP):
        a = Arrow(
            left_node.get_right(),
            right_node.get_left(),
            buff=0.1,
            stroke_width=2.0,
            color=color,
            tip_length=0.15,
        )
        if label:
            lbl = make_label(label, font_size=9, color=color)
            lbl.next_to(a, label_dir, buff=0.07)
            return VGroup(a, lbl)
        return a

    def _section_header(self, text, color=TEAL):
        hdr = make_label(text, font_size=30, color=color)
        hdr.to_edge(UP, buff=0.45)
        return hdr

    def _code_box(
        self, lines, title, color, width=5.8, font_size=11, language="json"
    ):
        text = "\n".join(lines)
        title_lbl = make_label(title, font_size=10, color=color)
        code = make_code_text(
            text,
            font_size=font_size,
            language=language,
            force_code_object=True,
            with_background=False,
        )
        content = VGroup(title_lbl, code).arrange(DOWN, buff=0.12)
        box = RoundedRectangle(
            corner_radius=0.1,
            width=width,
            height=content.height + 0.5,
            fill_color="#161B22",
            fill_opacity=0.95,
            stroke_color=color,
            stroke_width=1.2,
        )
        content.move_to(box.get_center())
        return VGroup(box, content)

    def _next_slide(
        self,
        phase=False,
        enabled=True,
        notes="",
        loop=False,
        auto_next=False,
        playback_rate=1.0,
        reversed_playback_rate=1.0,
        dedent_notes=True,
        skip_animations=False,
        direction="horizontal",
        **kwargs,
    ):
        slide_checkpoint(
            self,
            phase=phase,
            enabled=enabled,
            slide_stop_mode=self.slide_stop_mode,
            loop=loop,
            auto_next=auto_next,
            playback_rate=playback_rate,
            reversed_playback_rate=reversed_playback_rate,
            notes=notes,
            dedent_notes=dedent_notes,
            skip_animations=skip_animations,
            direction=direction,
            **kwargs,
        )
