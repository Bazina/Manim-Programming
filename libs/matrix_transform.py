"""Matrix terminal-style replacement transform animation.

Characters scroll cyclically inside a bounding box over the source mobject.
Once covered, the source swaps to the target and the rain fades away.

Usage
-----
    self.play(MatrixTransform(old_mob, new_mob))
"""

from __future__ import annotations

import random as _rand

import numpy as np
from manim import (
    GREEN_A,
    Animation,
    FadeIn,
    FadeOut,
    Mobject,
    AnimationGroup,
    Succession,
    Rectangle,
    Text,
    VGroup,
)


_MATRIX_CHARS = "0123456789ABCDEF#@$%&"

_FONT = "JetBrains Mono"


class _CyclicRainColumn(Animation):
    """Animate a column of characters scrolling downward in a cycle.

    Characters that fall below the box bottom teleport back to the top,
    creating an endless scrolling effect.
    """

    def __init__(
        self,
        column: VGroup,
        y_top: float,
        y_bottom: float,
        speed: float = 3.0,
        **kwargs,
    ):
        self.col = column
        self.y_top = y_top
        self.y_bottom = y_bottom
        self.speed = speed
        self.span = y_top - y_bottom
        # store original y positions
        self.start_ys = [ch.get_center()[1] for ch in column]
        super().__init__(column, **kwargs)

    def interpolate_mobject(self, alpha: float) -> None:
        distance = self.speed * self.run_time * alpha
        for ch, start_y in zip(self.col, self.start_ys):
            new_y = start_y - distance
            # wrap around cyclically
            new_y = self.y_top - ((self.y_top - new_y) % self.span)
            ch.move_to(np.array([ch.get_center()[0], new_y, 0.0]))


def _build_dense_column(
    x: float,
    y_top: float,
    y_bottom: float,
    row_spacing: float,
    font_size: int,
    rng: _rand.Random,
) -> VGroup:
    """Build a dense column filling the full height with green chars."""
    col = VGroup()
    span = y_top - y_bottom
    num_chars = int(span / row_spacing) + 2  # overfill slightly for seamless wrap
    for i in range(num_chars):
        ch = rng.choice(_MATRIX_CHARS)
        char = Text(
            ch,
            font=_FONT,
            font_size=font_size,
            fill_color=GREEN_A,
            fill_opacity=rng.uniform(0.8, 1.0),
            stroke_width=0,
            weight="BOLD",
        )
        y = y_top - i * row_spacing
        char.move_to(np.array([x, y, 0.0]))
        col.add(char)
    return col


class MatrixTransform(AnimationGroup):
    """Drop-in replacement for ReplacementTransform with Matrix rain.

    A green bounding box appears around the source. Columns of small green
    hex characters scroll cyclically downward inside the box. While the
    rain scrolls, the source fades out and the target fades in.
    After the transition the box and rain disappear.

    Parameters
    ----------
    mobject : Mobject
        The source mobject (removed from scene after animation).
    target_mobject : Mobject
        The target mobject (added to scene after animation).
    num_cols : int
        Number of character columns across the box.
    font_size : int
        Rain character font size.
    run_time : float
        Total animation duration.
    scroll_speed : float
        How fast the characters scroll (scene units per second).
    box_padding : float
        Padding around the mobject for the bounding box.
    """

    def __init__(
        self,
        mobject: Mobject,
        target_mobject: Mobject,
        num_cols: int = 30,
        font_size: int = 6,
        run_time: float = 1.0,
        scroll_speed: float = 5.0,
        box_padding: float = 0.1,
        **kwargs,
    ) -> None:
        self.source = mobject
        self.target = target_mobject

        center = mobject.get_center()
        w = max(mobject.width, target_mobject.width, 1.2) + box_padding * 2
        h = max(mobject.height, target_mobject.height, 0.8) + box_padding * 2

        # Invisible bounding box (no border)
        box = Rectangle(
            width=w, height=h,
            stroke_width=0,
            fill_opacity=0,
        ).move_to(center)
        self._box = box

        y_top = center[1] + h / 2
        y_bottom = center[1] - h / 2
        x_left = center[0] - w / 2
        col_spacing = w / max(num_cols, 1)
        row_spacing = 0.08  # very dense rows

        rng = _rand.Random(42)

        # Build dense columns that fill the box
        columns = VGroup()
        col_anims = []
        for c in range(num_cols):
            x = x_left + (c + 0.5) * col_spacing
            col = _build_dense_column(x, y_top, y_bottom, row_spacing, font_size, rng)
            columns.add(col)
            # Each column scrolls at slightly different speed for organic feel
            speed_jitter = rng.uniform(0.85, 1.15) * scroll_speed
            col_anims.append(
                _CyclicRainColumn(
                    col,
                    y_top=y_top,
                    y_bottom=y_bottom,
                    speed=speed_jitter,
                    run_time=run_time,
                )
            )

        self._rain_columns = columns

        # Timing: rain covers object, source/target swap underneath, rain lifts
        t_fade_out = run_time * 0.25
        t_fade_in = run_time * 0.25
        t_wait_before_in = run_time * 0.45

        # Source fades out quickly in first portion
        fade_out_anim = FadeOut(mobject, run_time=t_fade_out)

        # Target fades in after midpoint
        target_mobject.set_opacity(0)
        fade_in_anim = Succession(
            Animation(target_mobject, run_time=t_wait_before_in),
            FadeIn(target_mobject, run_time=t_fade_in),
        )

        # Rain: fade in fast, hold, fade out fast
        rain_in = FadeIn(columns, run_time=run_time * 0.08)
        rain_hold = Animation(columns, run_time=run_time * 0.82)
        rain_out = FadeOut(columns, run_time=run_time * 0.10)
        rain_anim = Succession(rain_in, rain_hold, rain_out)

        super().__init__(
            *col_anims,
            fade_out_anim,
            fade_in_anim,
            rain_anim,
            run_time=run_time,
            **kwargs,
        )

    def clean_up_from_scene(self, scene) -> None:
        super().clean_up_from_scene(scene)
        scene.remove(self.source)
        scene.remove(self._box)
        for col in self._rain_columns:
            scene.remove(col)
        if self.target not in scene.mobjects:
            scene.add(self.target)
        self.target.set_opacity(1)
