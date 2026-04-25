"""
Shared components for DDIA (Designing Data-Intensive Applications) animations.

Contains common constants, helper functions for creating labels, cards, icons,
user icons, and syntax-highlighted code blocks used across DDIA scenes.
"""

from manim import (
    BLUE,
    BOLD,
    DOWN,
    GREY_B,
    ORIGIN,
    WHITE,
    YELLOW,
    Circle,
    Group,
    ImageMobject,
    RoundedRectangle,
    SVGMobject,
    Text,
    VGroup,
)

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
ICON_SHIELD = "assets/icons/security/ShieldCheckBold.svg"
ICON_SHIELD_WARNING = "assets/icons/security/ShieldWarningBold.svg"
ICON_BUG = "assets/icons/it/BugBold.svg"
ICON_FILE = "assets/icons/files/FileBold.svg"
ICON_CODE_FILE = "assets/icons/files/CodeFileBold.svg"
ICON_CHART = "assets/icons/business/ChartSquareBold.svg"
ICON_STRUCTURE = "assets/icons/it/StructureBold.svg"
ICON_CHECKLIST = "assets/icons/list/ChecklistBold.svg"
ICON_LAYERS = "assets/icons/tools/LayersBold.svg"
ICON_TRANSFER = "assets/icons/arrows/RoundTransferHorizontalBold.svg"
ICON_GRAPH = "assets/icons/business/GraphUpBold.svg"
ICON_BOOK = "assets/icons/school/BookBold.svg"

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
    "GROUP": "#C586C0",
    "BY": "#C586C0",
    "AS": "#C586C0",
    "AND": "#C586C0",
    "AVG": "#DCDCAA",
    "SUM": "#DCDCAA",
    "COUNT": "#DCDCAA",
    "INTERVAL": "#C586C0",
    "DATE": "#C586C0",
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


# ── Glow effects ──────────────────────────────────────────────────────


def create_glow(vmobject, color=YELLOW, rad=1, num_layers=60):
    """
    Create a radial glow behind any VMobject using concentric circles.

    Good for dots, small circles, or any focal-point mobject.
    """
    glow_group = VGroup()
    for idx in range(num_layers):
        new_circle = Circle(
            radius=rad * (1.002 ** (idx ** 2)) / 400,
            stroke_opacity=0,
            fill_color=color,
            fill_opacity=max(0, 0.2 - idx / 300),
        ).move_to(vmobject)
        glow_group.add(new_circle)
    return glow_group


def create_rect_glow(
        rect,
        color=None,
        layers=20,
        max_opacity=0.12,
        spread=0.25,
):
    """
    Create a soft rectangular glow behind a RoundedRectangle (or any rect-like VMobject).

    Layers of progressively larger, more transparent rounded-rectangles are
    stacked behind the source rectangle to simulate a neon / glowing edge.

    Parameters
    ----------
    rect : RoundedRectangle
        The rectangle to glow around.
    color : Color | str | None
        Glow color.  Defaults to the rectangle's stroke color.
    layers : int
        How many glow shells (more = smoother but heavier).
    max_opacity : float
        Opacity of the innermost (brightest) glow shell.
    spread : float
        Total extra size (in scene units) the glow extends beyond the rect.
    """
    if color is None:
        color = rect.get_stroke_color()

    base_w = rect.width
    base_h = rect.height
    corner = getattr(rect, "corner_radius", 0.15)
    if not isinstance(corner, (int, float)):
        corner = 0.15

    glow = VGroup()
    for i in range(layers):
        t = (i + 1) / layers  # 0→1
        extra = spread * t  # size growth
        opacity = max_opacity * (1 - t) ** 1.5  # fade out

        shell = RoundedRectangle(
            corner_radius=corner + extra * 0.3,
            width=base_w + extra,
            height=base_h + extra,
            stroke_opacity=0,
            fill_color=color,
            fill_opacity=opacity,
        )
        shell.move_to(rect)
        glow.add(shell)

    return glow


# ── Primitive builders ────────────────────────────────────────────────


def make_label(text, font_size=20, color=WHITE, weight=BOLD):
    """Create a styled text label with the project font."""
    return Text(text, font=FONT, font_size=font_size, weight=weight).set_color(color)


def make_card(
        label_text,
        width=2.2,
        height=0.8,
        fill_color=CARD_BG,
        label_color=WHITE,
        font_size=18,
        glow=True,
        glow_color=None,
):
    """Create a rounded-rectangle card with a centered label and optional glow."""
    rect = RoundedRectangle(
        corner_radius=0.15,
        width=width,
        height=height,
        fill_color=fill_color,
        fill_opacity=0.9,
        stroke_color=GREY_B,
        stroke_width=1.5,
    )
    label = make_label(label_text, font_size=font_size, color=label_color)
    label.move_to(rect.get_center())

    if glow:
        g_color = glow_color or label_color
        glow_layer = create_rect_glow(rect, color=g_color)
        group = VGroup(glow_layer, rect, label)
    else:
        group = VGroup(rect, label)

    group.rect = rect
    group.label_mob = label
    return group


def make_icon(icon_path, color=WHITE, height=0.6):
    """Load an SVG icon and set its color and height."""
    icon = SVGMobject(icon_path, fill_color=color)
    icon.set(height=height)
    return icon


def make_icon_card(
        label_text, icon_path, color=BLUE, width=2.0, height=1.6, font_size=14,
        glow=True, glow_color=None,
):
    """Card with an SVG icon on top and a label below, with optional glow."""
    rect = RoundedRectangle(
        corner_radius=0.15,
        width=width,
        height=height,
        fill_color=CARD_BG,
        fill_opacity=0.9,
        stroke_color=color,
        stroke_width=1.5,
    )
    icon = make_icon(icon_path, color=color, height=0.5)
    label = make_label(label_text, font_size=font_size, color=color, weight=BOLD)
    content = VGroup(icon, label).arrange(DOWN, buff=0.15)
    content.move_to(rect.get_center())

    if glow:
        g_color = glow_color or color
        glow_layer = create_rect_glow(rect, color=g_color)
        group = VGroup(glow_layer, rect, content)
    else:
        group = VGroup(rect, content)

    group.rect = rect
    group.content = content
    return group


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
        circle = Circle(
            radius=radius,
            fill_color=color,
            fill_opacity=0.8,
            stroke_color=WHITE,
            stroke_width=1.5,
        )
        icon_label = make_label(name, font_size=font_size, color=WHITE)
        icon_label.next_to(circle, DOWN, buff=0.15)
        return VGroup(circle, icon_label)


def make_comparison_table(
    col_headers,
    col_colors,
    col_x_positions,
    rows_data,
    header_font_size=13,
    row_font_size=12,
    note_font_size=11,
    row_spacing=0.42,
):
    """
    Build a styled comparison table (usability-style).

    Parameters
    ----------
    col_headers     : list[str]          — column header labels
    col_colors      : list[color]        — header label colors (same length as col_headers)
    col_x_positions : list[float]        — x-coordinate for each column centre
    rows_data       : list of tuples     — each tuple: (col0_text, col0_color,
                                            col1_text, col1_color,
                                            col2_text, col2_color, ...)
                                          Colors and texts alternate: text, color, text, color …
                                          Last column text uses note_font_size.
    row_spacing     : float              — vertical distance between data rows

    Returns
    -------
    VGroup containing: header labels, divider Line, data row VGroups (in order).
    Caller positions the returned group; rows live at y=0 relative to header.
    """
    from manim import Line, GREY_B, BOLD

    n_cols = len(col_headers)

    # Column headers
    hdrs = VGroup()
    for text, color, x in zip(col_headers, col_colors, col_x_positions):
        lbl = make_label(text, font_size=header_font_size, color=color, weight=BOLD)
        lbl.move_to([x, 0, 0])
        hdrs.add(lbl)

    # Divider line
    x_min = col_x_positions[0] - 2.0
    x_max = col_x_positions[-1] + 2.0
    div = Line([x_min, 0, 0], [x_max, 0, 0], color=GREY_B, stroke_width=0.8)
    div.next_to(hdrs, DOWN, buff=0.1)

    # Data rows — each tuple: (text0, color0, text1, color1, ..., textN, colorN)
    all_rows = VGroup()
    row_y = div.get_bottom()[1] - 0.05
    for entry in rows_data:
        row_y -= row_spacing
        row = VGroup()
        for i in range(n_cols):
            text  = entry[i * 2]
            color = entry[i * 2 + 1]
            fs = note_font_size if i == n_cols - 1 else row_font_size
            lbl = make_label(text, font_size=fs, color=color)
            lbl.move_to([col_x_positions[i], row_y, 0])
            row.add(lbl)
        all_rows.add(row)

    return VGroup(hdrs, div, all_rows)


def make_code_text(text, font_size=16, position=ORIGIN, t2c=None, glow=True, glow_color=None):
    """Create an IDE-styled syntax-highlighted code snippet with a dark background and optional glow."""
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

    if glow:
        g_color = glow_color or "#3E3E3E"
        glow_layer = create_rect_glow(bg, color=g_color, max_opacity=0.06, spread=0.2)
        group = VGroup(glow_layer, bg, code).move_to(position)
    else:
        group = VGroup(bg, code).move_to(position)

    group.bg = bg
    group.code = code
    return group
