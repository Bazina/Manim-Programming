import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from manim import (
    BLUE,
    DOWN,
    GREEN,
    GREY_A,
    ORANGE,
    PINK,
    PURPLE,
    RED,
    TEAL,
    YELLOW,
    Scene,
    VGroup,
    config,
)

from libs.ddia_components import (
    ICON_BOMB,
    ICON_BUG,
    ICON_CHECK,
    ICON_CODE,
    ICON_CPU_BOLT,
    ICON_DANGER,
    ICON_DATABASE,
    ICON_HELP,
    ICON_LOCK,
    ICON_SCALE,
    ICON_SEARCH,
    ICON_SERVER,
    ICON_SHIELD,
    ICON_SHIELD_WARNING,
    ICON_SIREN,
    ICON_STOPWATCH,
    ICON_STREAM,
    ICON_TUNING,
    ICON_USER,
    make_icon,
    make_label,
)

config.background_color = "#0D1117"


class IconTest(Scene):
    def construct(self):
        icons_data = [
            ("DANGER", ICON_DANGER, "#A20E00"),
            ("SHIELD", ICON_SHIELD, GREEN),
            ("BUG", ICON_BUG, YELLOW),
            ("SIREN", ICON_SIREN, ORANGE),
            ("USER", ICON_USER, BLUE),
            ("BOMB", ICON_BOMB, PURPLE),
            ("LOCK", ICON_LOCK, TEAL),
            ("CODE", ICON_CODE, PINK),
            ("DATABASE", ICON_DATABASE, BLUE),
            ("SERVER", ICON_SERVER, GREEN),
            ("CHECK", ICON_CHECK, GREEN),
            ("SCALE", ICON_SCALE, ORANGE),
            ("TUNING", ICON_TUNING, PURPLE),
            ("HELP", ICON_HELP, YELLOW),
            ("SEARCH", ICON_SEARCH, TEAL),
            ("STREAM", ICON_STREAM, RED),
            ("STOPWATCH", ICON_STOPWATCH, ORANGE),
            ("CPU_BOLT", ICON_CPU_BOLT, BLUE),
            ("SHIELD_WARN", ICON_SHIELD_WARNING, YELLOW),
        ]

        groups = VGroup()
        for name, path, color in icons_data:
            icon = make_icon(path, color=color, height=0.6)
            label = make_label(name, font_size=10, color=GREY_A)
            g = VGroup(icon, label).arrange(DOWN, buff=0.1)
            groups.add(g)

        groups.arrange_in_grid(rows=4, buff=0.4)
        self.add(groups)
        self.wait(3)
