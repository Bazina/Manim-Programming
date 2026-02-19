"""Matrix terminal-style replacement transform animation.

Columns of green characters scroll downward over the source mobject,
hiding it as they pass. Once covered, the target replaces the source
beneath the rain, and the rain continues scrolling off to reveal it.

Usage
-----
    self.play(MatrixTransform(old_mob, new_mob))
"""

from __future__ import annotations

import random as _rand

import numpy as np
from manim import (
    DOWN,
    GREEN_A,
    GREEN_E,
    Animation,
    FadeIn,
    FadeOut,
    Mobject,
    AnimationGroup,
    Succession,
    Text,
    VGroup,
    interpolate_color,
    rate_functions,
)


_MATRIX_CHARS = (
    "アイウエオカキクケコサシスセソ"
    "タチツテトナニヌネノハヒフヘホ"
    "マミムメモヤユヨラリルレロワヲン"
    "0123456789ABCDEF"
)

_FONT = "JetBrains Mono"


def _build_column(
    x: float,
    y_top: float,
    length: int,
    row_spacing: float,
    font_size: int,
    rng: _rand.Random,
) -> VGroup:
    """Build a single vertical column of green characters."""
    col = VGroup()
    for i in range(length):
        ch = rng.choice(_MATRIX_CHARS)
        # Head char is brightest, tail fades out
        t = i / max(length - 1, 1)
        shade = interpolate_color(GREEN_A, GREEN_E, t)
        opacity = 1.0 - 0.7 * t
        char = Text(
            ch,
            font=_FONT,
            font_size=font_size,
            fill_color=shade,
            fill_opacity=opacity,
            stroke_width=0,
            weight="BOLD",
        )
        char.move_to(np.array([x, y_top - i * row_spacing, 0.0]))
        col.add(char)
    return col


class MatrixTransform(AnimationGroup):
    """Drop-in replacement for ReplacementTransform with Matrix rain.

    Green character columns scroll downward over the source mobject.
    While they cover it the source fades out and the target fades in,
    then the rain continues off-screen.

    Parameters
    ----------
    mobject : Mobject
        The source mobject (removed from scene after animation).
    target_mobject : Mobject
        The target mobject (added to scene after animation).
    num_cols : int
        Number of rain columns across the mobject width.
    col_length : int
        Number of characters per column.
    font_size : int
        Rain character font size.
    run_time : float
        Total animation duration.
    drop_distance : float
        How far (in scene units) each column travels downward.
    """

    def __init__(
        self,
        mobject: Mobject,
        target_mobject: Mobject,
        num_cols: int = 8,
        col_length: int = 7,
        font_size: int = 14,
        run_time: float = 2.5,
        drop_distance: float = 4.0,
        **kwargs,
    ) -> None:
        self.source = mobject
        self.target = target_mobject
        self._rain_columns = VGroup()  # stored for cleanup

        center = mobject.get_center()
        width = max(mobject.width, target_mobject.width, 1.5)
        col_spacing = width / max(num_cols - 1, 1)
        row_spacing = 0.26

        rng = _rand.Random(42)

        # Build columns that start above the mobject
        rain_height = col_length * row_spacing
        y_start = center[1] + mobject.height / 2 + rain_height + 0.3

        columns = VGroup()
        for c in range(num_cols):
            x = center[0] - width / 2 + c * col_spacing
            col = _build_column(x, y_start, col_length, row_spacing, font_size, rng)
            columns.add(col)
        self._rain_columns = columns

        # Each column slides down by drop_distance with a small stagger
        # Phase 1: columns start falling + source fades out (first 45%)
        # Phase 2: columns keep falling + target fades in  (last 55%)

        t_fade_out = run_time * 0.40
        t_fade_in = run_time * 0.40

        # Column drop animations — each column shifts DOWN over full run_time
        # with a small random stagger per column for organic feel
        drop_vector = DOWN * drop_distance
        col_anims = []
        for i, col in enumerate(columns):
            delay = rng.uniform(0, run_time * 0.15)
            col_run = run_time - delay
            col_anims.append(
                Succession(
                    Animation(col, run_time=delay),  # wait
                    col.animate(run_time=col_run, rate_func=rate_functions.linear).shift(drop_vector),
                )
            )

        # Source fades out during first half
        fade_out_anim = FadeOut(mobject, run_time=t_fade_out)

        # Target fades in during second half
        target_mobject.set_opacity(0)
        fade_in_anim = Succession(
            Animation(target_mobject, run_time=run_time - t_fade_in),  # wait
            FadeIn(target_mobject, run_time=t_fade_in),
        )

        super().__init__(
            *col_anims,
            fade_out_anim,
            fade_in_anim,
            run_time=run_time,
            **kwargs,
        )

    def clean_up_from_scene(self, scene) -> None:
        super().clean_up_from_scene(scene)
        # Remove source + leftover rain columns
        scene.remove(self.source)
        for col in self._rain_columns:
            scene.remove(col)
        # Ensure target stays visible
        if self.target not in scene.mobjects:
            scene.add(self.target)
        self.target.set_opacity(1)
