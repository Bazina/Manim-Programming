"""
Shared components for DDIA (Designing Data-Intensive Applications) animations.

Contains common constants, helper functions for creating labels, cards, icons,
user icons, and syntax-highlighted code blocks used across DDIA scenes.
"""

from manim import *

# ── Theme ─────────────────────────────────────────────────────────────
FONT = "JetBrains Mono"
DARK_BG = "#161B22"
CARD_BG = "#21262D"

# ── Icon paths (relative to project root / assets_dir) ────────────────
ICON_DATABASE = "assets/icons/ui/DatabaseBold.svg"
ICON_SERVER = "assets/icons/devices/ServerBold.svg"
ICON_SEARCH = "assets/icons/search/MagnifierBold.svg"
ICON_STREAM = "assets/icons/notifications/NotificationUnreadLinesBold.svg"
ICON_STOPWATCH = "assets/icons/time/StopwatchBold.svg"
ICON_CPU_BOLT = "assets/icons/devices/CpuBoltBold.svg"
ICON_CHECK = "assets/icons/ui/CheckCircleBold.svg"
ICON_SCALE = "assets/icons/arrows/RoundArrowUpBold.svg"
ICON_TUNING = "assets/icons/settings/TuningBold.svg"
ICON_DANGER = "assets/icons/ui/DangerCircleBold.svg"
ICON_HELP = "assets/icons/ui/HelpBold.svg"
ICON_SIREN = "assets/icons/security/SirenBold.svg"
ICON_USER = "assets/icons/users/UserBold.svg"
ICON_BOMB = "assets/icons/security/BombBold.svg"
ICON_LOCK = "assets/icons/security/LockBold.svg"
ICON_CODE = "assets/icons/it/CodeBold.svg"
ICON_LIGHTNING = "assets/icons/devices/LightningBold.svg"
ICON_CLOUD = "assets/icons/devices/CloudStorageBold.svg"
ICON_MONITOR = "assets/icons/devices/MonitorBold.svg"
ICON_SETTINGS = "assets/icons/settings/SettingsBold.svg"


# ── SQL / code syntax-highlighting color map (VS Code style) ─────────
SQL_T2C = {
    # Keywords
    "SELECT": "#C586C0",
    "FROM": "#C586C0",
    "JOIN": "#C586C0",
    "ON": "#C586C0",
    "WHERE": "#C586C0",
    "INSERT": "#C586C0",
    "INTO": "#C586C0",
    "VALUES": "#C586C0",
    "SET": "#C586C0",
    "GET": "#C586C0",
    "PUT": "#C586C0",
    "PUBLISH": "#C586C0",
    "SUBSCRIBE": "#C586C0",
    "CREATE": "#C586C0",
    "INDEX": "#C586C0",
    "RUN": "#C586C0",
    "MATCH": "#C586C0",
    "EVERY": "#C586C0",
    "JOB": "#C586C0",
    "PROCESS": "#C586C0",
    "EXPIRE": "#C586C0",
    # Tables / objects
    "tweets": "#4EC9B0",
    "users": "#4EC9B0",
    "follows": "#4EC9B0",
    "cache": "#4EC9B0",
    "orders": "#4EC9B0",
    "events": "#4EC9B0",
    "messages": "#4EC9B0",
    "products": "#4EC9B0",
    "logs": "#4EC9B0",
    "channel": "#4EC9B0",
    # Columns / fields
    "sender_": "#9CDCFE",
    "followee_": "#9CDCFE",
    "follower_": "#9CDCFE",
    "name": "#9CDCFE",
    "email": "#9CDCFE",
    "user_id": "#9CDCFE",
    "title": "#9CDCFE",
    "data": "#9CDCFE",
    "session": "#9CDCFE",
    "daily_report": "#9CDCFE",
    "id": "#9CDCFE",
    # String values
    "current_user": "#CE9178",
    "'alice'": "#CE9178",
    "'session_42'": "#CE9178",
    "'keyword'": "#CE9178",
    "'new_order'": "#CE9178",
    "'24h'": "#CE9178",
    # Operators & punctuation
    "*": "#D4D4D4",
    "=": "#D4D4D4",
    ",": "#D4D4D4",
    ".": "#D4D4D4",
    ";": "#D4D4D4",
    "(": "#FFD700",
    ")": "#FFD700",
}


# ── Primitive builders ────────────────────────────────────────────────

def make_label(text, font_size=20, color=WHITE, weight=BOLD):
    """Create a styled text label with the project font."""
    return Text(text, font=FONT, font_size=font_size, weight=weight).set_color(color)


def make_card(label_text, width=2.2, height=0.8, fill_color=CARD_BG, label_color=WHITE, font_size=18):
    """Create a rounded-rectangle card with a centered label."""
    rect = RoundedRectangle(
        corner_radius=0.15, width=width, height=height,
        fill_color=fill_color, fill_opacity=0.9, stroke_color=GREY_B, stroke_width=1.5,
    )
    label = make_label(label_text, font_size=font_size, color=label_color)
    label.move_to(rect.get_center())
    return VGroup(rect, label)


def make_icon(icon_path, color=WHITE, height=0.6):
    """Load an SVG icon and set its color and height."""
    icon = SVGMobject(icon_path, fill_color=color)
    icon.set(height=height)
    return icon


def make_icon_card(label_text, icon_path, color=BLUE, width=2.0, height=1.6, font_size=14):
    """Card with an SVG icon on top and a label below."""
    rect = RoundedRectangle(
        corner_radius=0.15, width=width, height=height,
        fill_color=CARD_BG, fill_opacity=0.9, stroke_color=color, stroke_width=1.5,
    )
    icon = make_icon(icon_path, color=color, height=0.5)
    label = make_label(label_text, font_size=font_size, color=color, weight=BOLD)
    content = VGroup(icon, label).arrange(DOWN, buff=0.15)
    content.move_to(rect.get_center())
    return VGroup(rect, content)


def make_user_icon(name, color=BLUE, radius=0.3, font_size=16, image_path=None):
    """Create a user avatar — either from an image or a colored circle."""
    if image_path is not None:
        img = ImageMobject(image_path)
        img.set(height=2 * radius)
        icon_label = make_label(name, font_size=font_size, color=WHITE)
        icon_label.next_to(img, DOWN, buff=0.15)
        result = Group(img, icon_label)
        result.circle = img  # expose for arrow anchoring
        return result
    else:
        circle = Circle(radius=radius, fill_color=color, fill_opacity=0.8,
                        stroke_color=WHITE, stroke_width=1.5)
        icon_label = make_label(name, font_size=font_size, color=WHITE)
        icon_label.next_to(circle, DOWN, buff=0.15)
        return VGroup(circle, icon_label)


def make_code_text(text, font_size=16, position=ORIGIN, t2c=None):
    """Create an IDE-styled syntax-highlighted code snippet with a dark background."""
    code = Text(
        text,
        font=FONT,
        font_size=font_size,
        color="#D4D4D4",
        weight=BOLD,
        stroke_width=0,
        t2c=t2c or SQL_T2C,
    )
    bg = RoundedRectangle(
        corner_radius=0.1,
        width=code.width + 0.4,
        height=code.height + 0.25,
        fill_color="#1E1E1E",
        fill_opacity=0.95,
        stroke_color="#3E3E3E",
        stroke_width=1,
    )
    bg.move_to(code.get_center())
    return VGroup(bg, code).move_to(position)

