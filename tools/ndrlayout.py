"""Lay out a Tina .ndr Petri net with a force-directed algorithm, curving arcs where needed.

The algorithm is the one behind Obsidian's graph view (d3-force): arcs pull their two nodes
together like springs, every pair of nodes pushes apart, a weak gravity pulls everything towards
the centre, and nodes may not overlap. Positions start on a deterministic spiral, so the same net
always gets the same layout.

Arcs stay straight where they can, as in Obsidian. An arc becomes a Bezier curve only where a
straight line would be unreadable: arcs between the same two nodes (a transition that takes a
token and puts it back) bow apart, and an arc whose line would cross another node bends around
it. nd stores a curve as one control point near each end of the arc: an absolute direction (a
fraction of a turn, anticlockwise from "right") and a distance in pixels.

Only the x/y of places (`p`) and transitions (`t`) and the shape of arcs (`e`) change. Names,
markings, arc kinds and weights are kept, so the net itself is untouched.

Usage:
    python tools/ndrlayout.py model/model.ndr --in-place
    python tools/ndrlayout.py model/model.ndr -o laid.ndr --svg preview.svg
"""

from __future__ import annotations

import argparse
import math
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from html import escape
from pathlib import Path

TOKEN = re.compile(r"\{[^}]*\}|\S+")
NODE_LINE = re.compile(r"^([pt])(\s+)(\S+)(\s+)(\S+)")

Vector = tuple[float, float]


@dataclass
class Node:
    name: str
    kind: str  # "p" (place) or "t" (transition)
    x: float
    y: float
    tokens: int = 0
    vx: float = 0.0
    vy: float = 0.0


@dataclass
class Arc:
    source: str
    target: str
    kind: str  # "" normal, "?" read, "?-" inhibitor
    weight: str
    # Drawing only, not part of the net: the line it came from, and the control points of a
    # curve relative to the source and the target node (screen coordinates, y down).
    line: int = field(default=-1, compare=False)
    anchor: str = field(default="n", compare=False)
    c1: Vector | None = field(default=None, compare=False)  # None: straight
    c2: Vector | None = field(default=None, compare=False)


@dataclass
class Net:
    lines: list[str]
    nodes: dict[str, Node] = field(default_factory=dict)
    arcs: list[Arc] = field(default_factory=list)


def parse(text: str) -> Net:
    net = Net(lines=text.splitlines(keepends=True))
    for number, line in enumerate(net.lines):
        tokens = TOKEN.findall(line)
        if not tokens:
            continue
        if tokens[0] in ("p", "t") and len(tokens) >= 4:
            node = Node(tokens[3], tokens[0], float(tokens[1]), float(tokens[2]))
            if node.kind == "p" and len(tokens) >= 5 and tokens[4].isdigit():
                node.tokens = int(tokens[4])
            net.nodes[node.name] = node
        elif tokens[0] == "e":
            # Short form: e src dst weight anchor. Long form adds angle and radius after each end.
            long_form = len(tokens) >= 8
            target = tokens[4] if long_form else tokens[2]
            weight = tokens[7] if long_form else tokens[3]
            kind = "?-" if weight.startswith("?-") else "?" if weight.startswith("?") else ""
            arc = Arc(tokens[1], target, kind, weight[len(kind) :], line=number, anchor=tokens[-1])
            if long_form:
                arc.c1 = polar_to_vector(float(tokens[2]), float(tokens[3]))
                arc.c2 = polar_to_vector(float(tokens[5]), float(tokens[6]))
            net.arcs.append(arc)
    return net


def polar_to_vector(turn: float, radius: float) -> Vector:
    """nd's (angle, radius): angle in turns, anticlockwise from +x, on a screen with y down."""
    angle = 2 * math.pi * turn
    return radius * math.cos(angle), -radius * math.sin(angle)


def vector_to_polar(v: Vector) -> tuple[float, float]:
    return (math.atan2(-v[1], v[0]) / (2 * math.pi)) % 1.0, math.hypot(*v)


def layout(
    net: Net,
    *,
    iterations: int = 300,
    link_distance: float = 60.0,
    charge: float = -500.0,
    gravity: float = 0.05,
    radius: float = 30.0,
) -> None:
    """Move the nodes of `net` in place (d3-force: link, many-body, x/y gravity, collide)."""
    nodes = list(net.nodes.values())
    index = {n.name: i for i, n in enumerate(nodes)}

    # Spiral start (d3's phyllotaxis), independent of the old, possibly messy, coordinates.
    golden = math.pi * (3 - math.sqrt(5))
    for i, n in enumerate(nodes):
        r = 10 * math.sqrt(0.5 + i)
        n.x, n.y, n.vx, n.vy = r * math.cos(i * golden), r * math.sin(i * golden), 0.0, 0.0

    pairs = sorted(
        {
            tuple(sorted((index[a.source], index[a.target])))
            for a in net.arcs
            if a.source != a.target
        }
    )
    degree = [0] * len(nodes)
    for s, t in pairs:
        degree[s] += 1
        degree[t] += 1

    alpha, alpha_min = 1.0, 0.001
    alpha_decay = 1 - alpha_min ** (1 / iterations)
    velocity_decay = 0.4

    for _ in range(iterations):
        alpha += (0 - alpha) * alpha_decay

        # Links: springs towards link_distance, weaker on busy nodes.
        for s, t in pairs:
            a, b = nodes[s], nodes[t]
            dx = (b.x + b.vx) - (a.x + a.vx) or 1e-6
            dy = (b.y + b.vy) - (a.y + a.vy) or 1e-6
            dist = math.hypot(dx, dy)
            strength = 1 / min(degree[s], degree[t])
            k = (dist - link_distance) / dist * alpha * strength
            bias = degree[s] / (degree[s] + degree[t])
            b.vx -= dx * k * bias
            b.vy -= dy * k * bias
            a.vx += dx * k * (1 - bias)
            a.vy += dy * k * (1 - bias)

        # Many-body: every pair repels (charge < 0), falling off with the squared distance.
        for i, a in enumerate(nodes):
            for b in nodes[i + 1 :]:
                dx, dy = b.x - a.x, b.y - a.y
                d2 = max(dx * dx + dy * dy, 1.0)
                k = charge * alpha / d2
                a.vx += dx * k
                a.vy += dy * k
                b.vx -= dx * k
                b.vy -= dy * k

        # Gravity (d3 forceX/forceY towards 0): keeps the graph compact instead of stretched.
        for n in nodes:
            n.vx -= n.x * gravity * alpha
            n.vy -= n.y * gravity * alpha

        for n in nodes:
            n.vx *= 1 - velocity_decay
            n.vy *= 1 - velocity_decay
            n.x += n.vx
            n.y += n.vy

        # Collide: push overlapping nodes apart.
        for i, a in enumerate(nodes):
            for b in nodes[i + 1 :]:
                dx, dy = b.x - a.x, b.y - a.y
                dist = math.hypot(dx, dy) or 1e-6
                overlap = 2 * radius - dist
                if overlap > 0:
                    shift = overlap / dist / 2
                    a.x -= dx * shift
                    a.y -= dy * shift
                    b.x += dx * shift
                    b.y += dy * shift

        # Center: keep the mean position at the origin.
        cx = sum(n.x for n in nodes) / len(nodes)
        cy = sum(n.y for n in nodes) / len(nodes)
        for n in nodes:
            n.x -= cx
            n.y -= cy


def fit(net: Net, *, scale: float = 2.0, margin: float = 60.0) -> None:
    """Scale to nd's pixel coordinates and move into the positive quadrant."""
    nodes = net.nodes.values()
    min_x = min(n.x for n in nodes)
    min_y = min(n.y for n in nodes)
    for n in nodes:
        n.x = round((n.x - min_x) * scale + margin)
        n.y = round((n.y - min_y) * scale + margin)


def bezier(p0: Vector, p1: Vector, p2: Vector, p3: Vector, t: float) -> Vector:
    u = 1 - t
    return (
        u**3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t**3 * p3[0],
        u**3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t**3 * p3[1],
    )


def controls(a: Node, b: Node, bend: float) -> tuple[Vector, Vector]:
    """Control vectors of a symmetric bow from a to b, leaving and arriving `bend` radians off
    the straight line. A positive bend bows clockwise on screen, seen from a."""
    dx, dy = b.x - a.x, b.y - a.y
    length = math.hypot(dx, dy) or 1.0
    ux, uy = dx / length, dy / length
    cos, sin, reach = math.cos(bend), math.sin(bend), length / 3
    c1 = (reach * (ux * cos - uy * sin), reach * (ux * sin + uy * cos))
    c2 = (reach * (-ux * cos - uy * sin), reach * (ux * sin - uy * cos))
    return c1, c2


def path_points(net: Net, arc: Arc) -> tuple[Vector, Vector, Vector, Vector]:
    """Start, two control points and end of the arc's cubic Bezier (straight: controls = ends)."""
    a, b = net.nodes[arc.source], net.nodes[arc.target]
    p0, p3 = (a.x, a.y), (b.x, b.y)
    if arc.c1 is None or arc.c2 is None:
        return p0, p0, p3, p3
    return p0, (a.x + arc.c1[0], a.y + arc.c1[1]), (b.x + arc.c2[0], b.y + arc.c2[1]), p3


def clearance_of(net: Net, arc: Arc) -> float:
    """Smallest distance between the arc's path and any node other than its two ends."""
    points = path_points(net, arc)
    others = [n for n in net.nodes.values() if n.name not in (arc.source, arc.target)]
    best = math.inf
    for i in range(1, 20):
        x, y = bezier(*points, i / 20)
        for n in others:
            best = min(best, math.hypot(n.x - x, n.y - y))
    return best


def route(
    net: Net,
    *,
    clearance: float = 40.0,
    bends: tuple[float, ...] = (0.0, 0.35, 0.6, 0.85, 1.1),
    pair_bend: float = 0.3,
) -> None:
    """Decide which arcs are curved and set their control points.

    Each arc tries bends from `bends`, smallest first and both sides, and keeps the first one
    whose path stays `clearance` pixels away from all other nodes. If none does, it keeps the one
    that gets furthest away. Arcs between the same two nodes always bow apart, by at least
    `pair_bend`, on alternating sides.
    """
    groups: dict[frozenset[str], list[Arc]] = defaultdict(list)
    for arc in net.arcs:
        groups[frozenset((arc.source, arc.target))].append(arc)

    for members in groups.values():
        for i, arc in enumerate(members):
            # Sides are counted from the alphabetically first node of the pair, so two opposite
            # arcs given opposite sides really end up on opposite sides.
            sign = 1 if arc.source < arc.target else -1
            if len(members) > 1:
                side = 1 if i % 2 == 0 else -1
                least = pair_bend * (1 + i // 2)
                options = [side * b for b in (least, *bends) if b >= least]
            else:
                options = [s * b for b in bends for s in ((1, -1) if b else (1,))]
            best_bend, best_gap = options[0], -1.0
            for bend in options:
                set_bend(net, arc, sign * bend)
                gap = clearance_of(net, arc)
                if gap >= clearance:
                    best_bend = bend
                    break
                if gap > best_gap:
                    best_bend, best_gap = bend, gap
            set_bend(net, arc, sign * best_bend)


def set_bend(net: Net, arc: Arc, bend: float) -> None:
    if bend == 0:
        arc.c1 = arc.c2 = None
    else:
        arc.c1, arc.c2 = controls(net.nodes[arc.source], net.nodes[arc.target], bend)


def edge_line(arc: Arc) -> str:
    weight = f"{arc.kind}{arc.weight}"
    if arc.c1 is None or arc.c2 is None:
        return f"e {arc.source} {arc.target} {weight} {arc.anchor}\n"
    (t1, r1), (t2, r2) = vector_to_polar(arc.c1), vector_to_polar(arc.c2)
    return (
        f"e {arc.source} {t1:.4f} {r1:.1f} {arc.target} {t2:.4f} {r2:.1f} {weight} {arc.anchor}\n"
    )


def render(net: Net, *, edges: bool = True) -> str:
    """The net as .ndr text with the new positions and, if `edges`, the new arc shapes."""
    by_line = {arc.line: arc for arc in net.arcs} if edges else {}
    out = []
    for number, line in enumerate(net.lines):
        if number in by_line:
            out.append(edge_line(by_line[number]))
            continue
        tokens = TOKEN.findall(line)
        if tokens and tokens[0] in ("p", "t") and len(tokens) >= 4 and tokens[3] in net.nodes:
            n = net.nodes[tokens[3]]
            line = NODE_LINE.sub(
                lambda m, n=n: f"{m[1]}{m[2]}{n.x:.1f}{m[4]}{n.y:.1f}", line, count=1
            )
        out.append(line)
    return "".join(out)


def trim(point: Vector, towards: Vector, distance: float) -> Vector:
    dx, dy = towards[0] - point[0], towards[1] - point[1]
    length = math.hypot(dx, dy) or 1.0
    return point[0] + dx / length * distance, point[1] + dy / length * distance


def svg(net: Net) -> str:
    """A preview drawn like nd: circles are places (with token counts), bars are transitions,
    arcs follow the same Bezier curves."""
    nodes = net.nodes
    width = max(n.x for n in nodes.values()) + 160
    height = max(n.y for n in nodes.values()) + 80
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{height:.0f}" '
        'font-family="sans-serif" font-size="11">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<defs><marker id="arrow" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="7" '
        'markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#555"/></marker></defs>',
    ]
    for a in net.arcs:
        p0, p1, p2, p3 = path_points(net, a)
        source_gap = 16 if nodes[a.source].kind == "p" else 6
        target_gap = 16 if nodes[a.target].kind == "p" else 6
        start = trim(p0, p1 if p1 != p0 else p3, source_gap)
        end_dir = p2 if p2 != p3 else p0
        end = trim(p3, end_dir, target_gap + (6 if a.kind == "?-" else 0))
        path = (
            f"M{start[0]:.1f},{start[1]:.1f} C{p1[0]:.1f},{p1[1]:.1f} "
            f"{p2[0]:.1f},{p2[1]:.1f} {end[0]:.1f},{end[1]:.1f}"
        )
        if a.kind == "?-":
            cx, cy = trim(p3, end_dir, target_gap + 3)
            parts.append(
                f'<path d="{path}" fill="none" stroke="#c0392b"/>'
                f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="3" fill="white" stroke="#c0392b"/>'
            )
        else:
            dash = ' stroke-dasharray="4 3"' if a.kind == "?" else ""
            parts.append(
                f'<path d="{path}" fill="none" stroke="#555"{dash} marker-end="url(#arrow)"/>'
            )
        if a.weight not in ("1", ""):
            mx, my = bezier(p0, p1, p2, p3, 0.5)
            parts.append(
                f'<text x="{mx:.1f}" y="{my - 3:.1f}" fill="#555">{escape(a.weight)}</text>'
            )
    for n in nodes.values():
        if n.kind == "p":
            parts.append(f'<circle cx="{n.x}" cy="{n.y}" r="14" fill="#eef4fb" stroke="#2c5d8f"/>')
            if n.tokens:
                parts.append(
                    f'<text x="{n.x}" y="{n.y + 4}" text-anchor="middle" font-weight="bold">'
                    f"{n.tokens}</text>"
                )
        else:
            parts.append(f'<rect x="{n.x - 4}" y="{n.y - 12}" width="8" height="24" fill="#333"/>')
        parts.append(f'<text x="{n.x}" y="{n.y + 27}" text-anchor="middle">{escape(n.name)}</text>')
    parts.append("</svg>\n")
    return "\n".join(parts)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("ndr", type=Path, help="input .ndr file")
    target = parser.add_mutually_exclusive_group()
    target.add_argument("-o", "--output", type=Path, help="write the laid-out net here")
    target.add_argument("--in-place", action="store_true", help="overwrite the input file")
    parser.add_argument("--svg", type=Path, help="also write an SVG preview")
    parser.add_argument("--iterations", type=int, default=300)
    parser.add_argument("--link-distance", type=float, default=60.0)
    parser.add_argument("--charge", type=float, default=-500.0, help="repulsion (negative)")
    parser.add_argument("--gravity", type=float, default=0.05, help="pull towards the centre")
    parser.add_argument("--scale", type=float, default=2.0, help="pixels per layout unit")
    parser.add_argument(
        "--no-curves", action="store_true", help="only move nodes, keep the arc lines as they are"
    )
    args = parser.parse_args(argv)

    net = parse(args.ndr.read_text(encoding="utf-8"))
    if not net.nodes:
        print(f"ndrlayout: no places or transitions in {args.ndr}", file=sys.stderr)
        return 1
    layout(
        net,
        iterations=args.iterations,
        link_distance=args.link_distance,
        charge=args.charge,
        gravity=args.gravity,
    )
    fit(net, scale=args.scale)
    if not args.no_curves:
        route(net)

    text = render(net, edges=not args.no_curves)
    if args.in_place:
        args.ndr.write_text(text, encoding="utf-8")
    elif args.output:
        args.output.write_text(text, encoding="utf-8")
    elif not args.svg:
        sys.stdout.write(text)
    if args.svg:
        args.svg.write_text(svg(net), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
