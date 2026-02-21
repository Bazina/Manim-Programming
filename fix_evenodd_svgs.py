"""
Fix SVG icons for Manim compatibility.

Manim's SVGMobject ignores fill-rule="evenodd", which causes compound paths
(a single <path d="..."> with multiple sub-paths) to render incorrectly —
inner cutout shapes get filled instead of appearing as holes.

This script fixes the issue by:
1. Splitting compound paths into individual sub-paths
2. Computing the signed area (winding direction) of each sub-path
3. Detecting which sub-paths are "holes" (contained inside a larger shape)
4. Reversing the winding of hole sub-paths
5. Recombining into a single path with fill-rule="nonzero"

Usage:
    python fix_evenodd_svgs.py                     # fix ALL icons in assets/icons/
    python fix_evenodd_svgs.py assets/icons/ui/     # fix icons in a specific folder
    python fix_evenodd_svgs.py path/to/icon.svg     # fix a single file
"""

import os
import re
import sys
import math
from pathlib import Path
from xml.etree import ElementTree as ET


# ── SVG Path Parsing ──────────────────────────────────────────────────

def tokenize_path(d):
    """Tokenize an SVG path d-attribute into a list of (command, args) tuples."""
    # Match command letters followed by their numeric arguments
    token_re = re.compile(r'([MmZzLlHhVvCcSsQqTtAa])|([+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?)')
    tokens = []
    for m in token_re.finditer(d):
        if m.group(1):
            tokens.append(m.group(1))
        else:
            tokens.append(float(m.group(2)))
    return tokens


def parse_path_to_subpaths(d):
    """Parse SVG path d-attribute into a list of sub-paths.

    Each sub-path is a list of (command, points) segments.
    Sub-paths are separated by 'M'/'m' commands.
    Returns list of sub-path strings.
    """
    # Split on M/m commands (each starts a new sub-path)
    # We need to keep the M command with each sub-path
    subpath_strings = []
    current = ""

    tokens = tokenize_path(d)
    i = 0
    while i < len(tokens):
        t = tokens[i]
        if isinstance(t, str) and t in ('M', 'm'):
            if current.strip():
                subpath_strings.append(current.strip())
            current = str(t)
            i += 1
        elif isinstance(t, str):
            current += " " + str(t)
            i += 1
        else:
            current += " " + format_num(t)
            i += 1

    if current.strip():
        subpath_strings.append(current.strip())

    return subpath_strings


def format_num(n):
    """Format a number, removing unnecessary trailing zeros."""
    if n == int(n):
        return str(int(n))
    return f"{n:g}"


# ── Sub-path to absolute coordinates ─────────────────────────────────

def subpath_to_points(subpath_d):
    """Convert a sub-path d-string to a list of (x, y) points on the path.

    We sample the path densely enough to compute area and containment.
    Only need the outline points (start/end of each segment).
    """
    tokens = tokenize_path(subpath_d)
    points = []
    cx, cy = 0.0, 0.0  # current point
    sx, sy = 0.0, 0.0  # sub-path start
    i = 0
    cmd = None

    def consume(n):
        nonlocal i
        vals = []
        while len(vals) < n and i < len(tokens):
            t = tokens[i]
            if isinstance(t, (int, float)):
                vals.append(float(t))
                i += 1
            else:
                break
        return vals

    while i < len(tokens):
        t = tokens[i]
        if isinstance(t, str):
            cmd = t
            i += 1
        else:
            # Implicit repeat of last command
            pass

        if cmd is None:
            i += 1
            continue

        if cmd == 'M':
            vals = consume(2)
            if len(vals) >= 2:
                cx, cy = vals[0], vals[1]
                sx, sy = cx, cy
                points.append((cx, cy))
                cmd = 'L'  # subsequent coords are implicit lineto
        elif cmd == 'm':
            vals = consume(2)
            if len(vals) >= 2:
                cx += vals[0]
                cy += vals[1]
                sx, sy = cx, cy
                points.append((cx, cy))
                cmd = 'l'
        elif cmd == 'L':
            vals = consume(2)
            if len(vals) >= 2:
                cx, cy = vals[0], vals[1]
                points.append((cx, cy))
        elif cmd == 'l':
            vals = consume(2)
            if len(vals) >= 2:
                cx += vals[0]
                cy += vals[1]
                points.append((cx, cy))
        elif cmd == 'H':
            vals = consume(1)
            if vals:
                cx = vals[0]
                points.append((cx, cy))
        elif cmd == 'h':
            vals = consume(1)
            if vals:
                cx += vals[0]
                points.append((cx, cy))
        elif cmd == 'V':
            vals = consume(1)
            if vals:
                cy = vals[0]
                points.append((cx, cy))
        elif cmd == 'v':
            vals = consume(1)
            if vals:
                cy += vals[0]
                points.append((cx, cy))
        elif cmd == 'C':
            vals = consume(6)
            if len(vals) >= 6:
                # Sample cubic bezier at a few points for area calculation
                x0, y0 = cx, cy
                x1, y1 = vals[0], vals[1]
                x2, y2 = vals[2], vals[3]
                x3, y3 = vals[4], vals[5]
                for t in [0.25, 0.5, 0.75, 1.0]:
                    u = 1 - t
                    px = u**3*x0 + 3*u**2*t*x1 + 3*u*t**2*x2 + t**3*x3
                    py = u**3*y0 + 3*u**2*t*y1 + 3*u*t**2*y2 + t**3*y3
                    points.append((px, py))
                cx, cy = x3, y3
        elif cmd == 'c':
            vals = consume(6)
            if len(vals) >= 6:
                x0, y0 = cx, cy
                x1, y1 = cx+vals[0], cy+vals[1]
                x2, y2 = cx+vals[2], cy+vals[3]
                x3, y3 = cx+vals[4], cy+vals[5]
                for t in [0.25, 0.5, 0.75, 1.0]:
                    u = 1 - t
                    px = u**3*x0 + 3*u**2*t*x1 + 3*u*t**2*x2 + t**3*x3
                    py = u**3*y0 + 3*u**2*t*y1 + 3*u*t**2*y2 + t**3*y3
                    points.append((px, py))
                cx, cy = x3, y3
        elif cmd == 'S':
            vals = consume(4)
            if len(vals) >= 4:
                cx, cy = vals[2], vals[3]
                points.append((cx, cy))
        elif cmd == 's':
            vals = consume(4)
            if len(vals) >= 4:
                cx += vals[2]
                cy += vals[3]
                points.append((cx, cy))
        elif cmd == 'Q':
            vals = consume(4)
            if len(vals) >= 4:
                x0, y0 = cx, cy
                x1, y1 = vals[0], vals[1]
                x2, y2 = vals[2], vals[3]
                for t in [0.25, 0.5, 0.75, 1.0]:
                    u = 1 - t
                    px = u**2*x0 + 2*u*t*x1 + t**2*x2
                    py = u**2*y0 + 2*u*t*y1 + t**2*y2
                    points.append((px, py))
                cx, cy = x2, y2
        elif cmd == 'q':
            vals = consume(4)
            if len(vals) >= 4:
                x0, y0 = cx, cy
                x1, y1 = cx+vals[0], cy+vals[1]
                x2, y2 = cx+vals[2], cy+vals[3]
                for t in [0.25, 0.5, 0.75, 1.0]:
                    u = 1 - t
                    px = u**2*x0 + 2*u*t*x1 + t**2*x2
                    py = u**2*y0 + 2*u*t*y1 + t**2*y2
                    points.append((px, py))
                cx, cy = x2, y2
        elif cmd == 'A':
            vals = consume(7)
            if len(vals) >= 7:
                cx, cy = vals[5], vals[6]
                points.append((cx, cy))
        elif cmd == 'a':
            vals = consume(7)
            if len(vals) >= 7:
                cx += vals[5]
                cy += vals[6]
                points.append((cx, cy))
        elif cmd in ('Z', 'z'):
            points.append((sx, sy))
            cx, cy = sx, sy
        else:
            i += 1

    return points


def signed_area(points):
    """Compute the signed area of a polygon using the shoelace formula.

    Positive = counter-clockwise, Negative = clockwise (in standard math coords).
    In SVG coords (y-down), positive = clockwise.
    """
    n = len(points)
    if n < 3:
        return 0.0
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += points[i][0] * points[j][1]
        area -= points[j][0] * points[i][1]
    return area / 2.0


def bounding_box(points):
    """Get (min_x, min_y, max_x, max_y) bounding box of points."""
    if not points:
        return (0, 0, 0, 0)
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return (min(xs), min(ys), max(xs), max(ys))


def bbox_contains(outer, inner):
    """Check if outer bounding box fully contains inner bounding box."""
    return (outer[0] <= inner[0] and inner[2] <= outer[2] and
            outer[1] <= inner[1] and inner[3] <= outer[3])


def point_in_polygon(px, py, polygon):
    """Ray casting algorithm to test if point is inside polygon."""
    n = len(polygon)
    inside = False
    j = n - 1
    for i in range(n):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        if ((yi > py) != (yj > py)) and (px < (xj - xi) * (py - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


def reverse_subpath(subpath_d):
    """Reverse the winding direction of an SVG sub-path.

    Strategy: parse to absolute coordinates, reverse the point order,
    and rebuild the path. For complex paths with curves, we reverse
    each segment.
    """
    tokens = tokenize_path(subpath_d)
    segments = []  # list of (cmd, abs_points)
    cx, cy = 0.0, 0.0
    sx, sy = 0.0, 0.0
    i = 0
    cmd = None
    has_close = False

    def consume(n):
        nonlocal i
        vals = []
        while len(vals) < n and i < len(tokens):
            t = tokens[i]
            if isinstance(t, (int, float)):
                vals.append(float(t))
                i += 1
            else:
                break
        return vals

    while i < len(tokens):
        t = tokens[i]
        if isinstance(t, str):
            cmd = t
            i += 1
        # else: implicit repetition

        if cmd is None:
            i += 1
            continue

        if cmd == 'M':
            vals = consume(2)
            if len(vals) >= 2:
                cx, cy = vals[0], vals[1]
                sx, sy = cx, cy
                segments.append(('M', [(cx, cy)]))
                cmd = 'L'
        elif cmd == 'm':
            vals = consume(2)
            if len(vals) >= 2:
                cx += vals[0]; cy += vals[1]
                sx, sy = cx, cy
                segments.append(('M', [(cx, cy)]))
                cmd = 'l'
        elif cmd == 'L':
            vals = consume(2)
            if len(vals) >= 2:
                start = (cx, cy)
                cx, cy = vals[0], vals[1]
                segments.append(('L', [start, (cx, cy)]))
        elif cmd == 'l':
            vals = consume(2)
            if len(vals) >= 2:
                start = (cx, cy)
                cx += vals[0]; cy += vals[1]
                segments.append(('L', [start, (cx, cy)]))
        elif cmd == 'H':
            vals = consume(1)
            if vals:
                start = (cx, cy)
                cx = vals[0]
                segments.append(('L', [start, (cx, cy)]))
        elif cmd == 'h':
            vals = consume(1)
            if vals:
                start = (cx, cy)
                cx += vals[0]
                segments.append(('L', [start, (cx, cy)]))
        elif cmd == 'V':
            vals = consume(1)
            if vals:
                start = (cx, cy)
                cy = vals[0]
                segments.append(('L', [start, (cx, cy)]))
        elif cmd == 'v':
            vals = consume(1)
            if vals:
                start = (cx, cy)
                cy += vals[0]
                segments.append(('L', [start, (cx, cy)]))
        elif cmd == 'C':
            vals = consume(6)
            if len(vals) >= 6:
                start = (cx, cy)
                cp1 = (vals[0], vals[1])
                cp2 = (vals[2], vals[3])
                end = (vals[4], vals[5])
                cx, cy = end
                segments.append(('C', [start, cp1, cp2, end]))
        elif cmd == 'c':
            vals = consume(6)
            if len(vals) >= 6:
                start = (cx, cy)
                cp1 = (cx+vals[0], cy+vals[1])
                cp2 = (cx+vals[2], cy+vals[3])
                end = (cx+vals[4], cy+vals[5])
                cx, cy = end
                segments.append(('C', [start, cp1, cp2, end]))
        elif cmd == 'S':
            vals = consume(4)
            if len(vals) >= 4:
                start = (cx, cy)
                cp2 = (vals[0], vals[1])
                end = (vals[2], vals[3])
                cx, cy = end
                # For reversal, approximate S as C with reflected control point
                segments.append(('C', [start, start, cp2, end]))
        elif cmd == 's':
            vals = consume(4)
            if len(vals) >= 4:
                start = (cx, cy)
                cp2 = (cx+vals[0], cy+vals[1])
                end = (cx+vals[2], cy+vals[3])
                cx, cy = end
                segments.append(('C', [start, start, cp2, end]))
        elif cmd == 'Q':
            vals = consume(4)
            if len(vals) >= 4:
                start = (cx, cy)
                cp = (vals[0], vals[1])
                end = (vals[2], vals[3])
                cx, cy = end
                segments.append(('Q', [start, cp, end]))
        elif cmd == 'q':
            vals = consume(4)
            if len(vals) >= 4:
                start = (cx, cy)
                cp = (cx+vals[0], cy+vals[1])
                end = (cx+vals[2], cy+vals[3])
                cx, cy = end
                segments.append(('Q', [start, cp, end]))
        elif cmd == 'A':
            vals = consume(7)
            if len(vals) >= 7:
                start = (cx, cy)
                rx, ry, rot, large, sweep, ex, ey = vals
                cx, cy = ex, ey
                # Reverse arc: flip the sweep flag
                segments.append(('A', [start, rx, ry, rot, large, sweep, (ex, ey)]))
        elif cmd == 'a':
            vals = consume(7)
            if len(vals) >= 7:
                start = (cx, cy)
                rx, ry, rot, large, sweep = vals[0], vals[1], vals[2], vals[3], vals[4]
                ex, ey = cx + vals[5], cy + vals[6]
                cx, cy = ex, ey
                segments.append(('A', [start, rx, ry, rot, large, sweep, (ex, ey)]))
        elif cmd in ('Z', 'z'):
            has_close = True
            if abs(cx - sx) > 0.0001 or abs(cy - sy) > 0.0001:
                segments.append(('L', [(cx, cy), (sx, sy)]))
            cx, cy = sx, sy
        else:
            i += 1
            continue

    # Now reverse: skip the M, reverse the drawing segments, rebuild
    if not segments:
        return subpath_d

    # Separate M from drawing commands
    move = segments[0]
    draw_segs = segments[1:]

    # Reverse order of segments and reverse each one
    reversed_segs = []
    for seg in reversed(draw_segs):
        cmd_type = seg[0]
        if cmd_type == 'L':
            # L [start, end] → L [end, start], new endpoint is old start
            reversed_segs.append(('L', [seg[1][1], seg[1][0]]))
        elif cmd_type == 'C':
            # C [start, cp1, cp2, end] → C [end, cp2, cp1, start]
            reversed_segs.append(('C', [seg[1][3], seg[1][2], seg[1][1], seg[1][0]]))
        elif cmd_type == 'Q':
            # Q [start, cp, end] → Q [end, cp, start]
            reversed_segs.append(('Q', [seg[1][2], seg[1][1], seg[1][0]]))
        elif cmd_type == 'A':
            # A [start, rx, ry, rot, large, sweep, end]
            # Reverse: swap start/end, flip sweep flag
            start, rx, ry, rot, large, sweep, end = seg[1]
            new_sweep = 1 - sweep
            reversed_segs.append(('A', [end, rx, ry, rot, large, new_sweep, start]))

    # Build new path string
    if not reversed_segs:
        return subpath_d

    # Start point is the endpoint of the first reversed segment (which was the last original endpoint)
    first = reversed_segs[0]
    if first[0] == 'L':
        start_pt = first[1][0]
    elif first[0] == 'C':
        start_pt = first[1][0]
    elif first[0] == 'Q':
        start_pt = first[1][0]
    elif first[0] == 'A':
        start_pt = first[1][0]
    else:
        start_pt = move[1][0]

    parts = [f"M{format_num(start_pt[0])} {format_num(start_pt[1])}"]

    for seg in reversed_segs:
        cmd_type = seg[0]
        if cmd_type == 'L':
            end = seg[1][1]
            parts.append(f"L{format_num(end[0])} {format_num(end[1])}")
        elif cmd_type == 'C':
            _, cp1, cp2, end = seg[1]
            parts.append(f"C{format_num(cp1[0])} {format_num(cp1[1])} {format_num(cp2[0])} {format_num(cp2[1])} {format_num(end[0])} {format_num(end[1])}")
        elif cmd_type == 'Q':
            _, cp, end = seg[1]
            parts.append(f"Q{format_num(cp[0])} {format_num(cp[1])} {format_num(end[0])} {format_num(end[1])}")
        elif cmd_type == 'A':
            _, rx, ry, rot, large, sweep, end = seg[1]
            parts.append(f"A{format_num(rx)} {format_num(ry)} {format_num(rot)} {int(large)} {int(sweep)} {format_num(end[0])} {format_num(end[1])}")

    if has_close:
        parts.append("Z")

    return " ".join(parts)


# ── Main fix logic ────────────────────────────────────────────────────

def fix_evenodd_path(d_attr):
    """Fix a compound evenodd path by reversing inner (hole) sub-paths.

    For nonzero fill-rule: outer shapes are CW, holes are CCW (or vice versa).
    We detect which sub-paths are holes and reverse them so they have opposite
    winding to their parent.
    """
    subpaths = parse_path_to_subpaths(d_attr)
    if len(subpaths) <= 1:
        return d_attr  # nothing to fix

    # Compute points, areas, and bboxes for each sub-path
    info = []
    for sp in subpaths:
        pts = subpath_to_points(sp)
        area = signed_area(pts)
        bbox = bounding_box(pts)
        info.append({
            'd': sp,
            'points': pts,
            'area': area,
            'abs_area': abs(area),
            'bbox': bbox,
        })

    # Sort by absolute area descending (largest = outermost shapes)
    sorted_indices = sorted(range(len(info)), key=lambda i: info[i]['abs_area'], reverse=True)

    # For each sub-path, determine its nesting depth
    # A sub-path is "inside" another if its centroid is inside the other's polygon
    for idx in range(len(info)):
        info[idx]['depth'] = 0
        # Check centroid of this sub-path against all larger sub-paths
        pts = info[idx]['points']
        if not pts:
            continue
        # Use centroid of bounding box as test point
        bb = info[idx]['bbox']
        test_x = (bb[0] + bb[2]) / 2
        test_y = (bb[1] + bb[3]) / 2

        for other_idx in range(len(info)):
            if other_idx == idx:
                continue
            if info[other_idx]['abs_area'] <= info[idx]['abs_area']:
                continue
            if not bbox_contains(info[other_idx]['bbox'], info[idx]['bbox']):
                continue
            if point_in_polygon(test_x, test_y, info[other_idx]['points']):
                info[idx]['depth'] += 1

    # For nonzero fill-rule: even depth = filled (outer), odd depth = hole
    # Outer shapes should be CW (positive area in SVG coords), holes should be CCW
    # In SVG coords (y-down), positive signed area = clockwise
    fixed_subpaths = []
    for i, sp_info in enumerate(info):
        is_hole = sp_info['depth'] % 2 == 1
        area = sp_info['area']

        # In SVG coords: positive area = CW, negative = CCW
        # We want: outer = CW (positive), holes = CCW (negative)
        is_cw = area > 0

        if is_hole and is_cw:
            # Hole but CW → reverse to CCW
            fixed_subpaths.append(reverse_subpath(sp_info['d']))
        elif not is_hole and not is_cw:
            # Outer but CCW → reverse to CW
            fixed_subpaths.append(reverse_subpath(sp_info['d']))
        else:
            # Already correct winding
            fixed_subpaths.append(sp_info['d'])

    return " ".join(fixed_subpaths)


def fix_svg_file(filepath):
    """Fix evenodd paths in an SVG file."""
    ET.register_namespace('', 'http://www.w3.org/2000/svg')

    tree = ET.parse(filepath)
    root = tree.getroot()
    ns = {'svg': 'http://www.w3.org/2000/svg'}
    modified = False

    # Find all path elements with fill-rule="evenodd"
    for path in root.iter('{http://www.w3.org/2000/svg}path'):
        fill_rule = path.get('fill-rule', '')
        if fill_rule != 'evenodd':
            continue

        d = path.get('d', '')
        if not d:
            continue

        # Check if it's a compound path (multiple M commands)
        m_count = len(re.findall(r'[Mm]', d))
        if m_count <= 1:
            continue

        # Fix the path
        fixed_d = fix_evenodd_path(d)
        path.set('d', fixed_d)
        path.set('fill-rule', 'nonzero')
        if path.get('clip-rule') == 'evenodd':
            path.set('clip-rule', 'nonzero')
        modified = True

    # Also handle paths without namespace prefix (some SVGs)
    for path in root.iter('path'):
        fill_rule = path.get('fill-rule', '')
        if fill_rule != 'evenodd':
            continue

        d = path.get('d', '')
        if not d:
            continue

        m_count = len(re.findall(r'[Mm]', d))
        if m_count <= 1:
            continue

        fixed_d = fix_evenodd_path(d)
        path.set('d', fixed_d)
        path.set('fill-rule', 'nonzero')
        if path.get('clip-rule') == 'evenodd':
            path.set('clip-rule', 'nonzero')
        modified = True

    if modified:
        tree.write(filepath, xml_declaration=False)
        return True
    return False


def fix_directory(dirpath):
    """Fix all SVG files in a directory tree."""
    fixed = 0
    total = 0
    for root, dirs, files in os.walk(dirpath):
        for f in files:
            if not f.endswith('.svg'):
                continue
            total += 1
            filepath = os.path.join(root, f)
            try:
                if fix_svg_file(filepath):
                    fixed += 1
            except Exception as e:
                print(f"  Error processing {filepath}: {e}")
    print(f"Fixed {fixed}/{total} SVG files in {dirpath}")
    return fixed


# ── CLI ───────────────────────────────────────────────────────────────

if __name__ == '__main__':
    if len(sys.argv) > 1:
        target = sys.argv[1]
    else:
        target = os.path.join(os.path.dirname(__file__), 'assets', 'icons')

    if os.path.isfile(target):
        result = fix_svg_file(target)
        if result:
            print(f"✓ Fixed {target}")
        else:
            print(f"  No evenodd paths to fix in {target}")
    elif os.path.isdir(target):
        fix_directory(target)
    else:
        print(f"Error: {target} not found")
        sys.exit(1)

