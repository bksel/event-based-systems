import math
import re
from pathlib import Path

import ndrlayout

ROOT = Path(__file__).resolve().parent.parent

TINY = """\
p 10.0 10.0 off 1 n
p 10.0 10.0 on 0 n
p 10.0 10.0 beans 2 n {} ne
p 10.0 10.0 cup_full 0 n
t 10.0 10.0 power_on c 0 w n {} ne
t 10.0 10.0 brew c 0 w n {} ne
t 10.0 10.0 drink c 0 w n {} ne
e off power_on 1 n
e power_on on 1 n
e on brew 1 n
e beans brew 1 n
e cup_full brew ?-1 n
e brew on 1 n
e brew cup_full 1 n
e cup_full drink 1 n
h tiny
"""


def laid_out(text: str, *, curves: bool = True) -> str:
    net = ndrlayout.parse(text)
    ndrlayout.layout(net)
    ndrlayout.fit(net)
    if curves:
        ndrlayout.route(net)
    return ndrlayout.render(net, edges=curves)


def without_coordinates(text: str) -> list[str]:
    return [re.sub(r"^([pt])\s+\S+\s+\S+", r"\1 X Y", line) for line in text.splitlines()]


def test_parse_reads_nodes_markings_and_arc_kinds():
    net = ndrlayout.parse(TINY)
    assert {n.name for n in net.nodes.values() if n.kind == "p"} == {
        "off",
        "on",
        "beans",
        "cup_full",
    }
    assert net.nodes["beans"].tokens == 2
    inhibitor = [a for a in net.arcs if a.kind == "?-"]
    assert [(a.source, a.target, a.weight) for a in inhibitor] == [("cup_full", "brew", "1")]


def test_without_curves_only_node_coordinates_change():
    out = laid_out(TINY, curves=False)
    assert without_coordinates(out) == without_coordinates(TINY)
    assert out != TINY


def test_with_curves_the_net_is_unchanged():
    before, after = ndrlayout.parse(TINY), ndrlayout.parse(laid_out(TINY))
    assert after.arcs == before.arcs  # names, kinds and weights; the geometry is not compared
    assert [line for line in laid_out(TINY).splitlines() if line[0] not in "pte"] == ["h tiny"]


def test_polar_matches_nd():
    # Calibrated against nd: 0 turns points right, 0.25 up (y grows downwards on screen).
    right, up = ndrlayout.polar_to_vector(0.0, 10), ndrlayout.polar_to_vector(0.25, 10)
    assert right == (10.0, -0.0)
    assert abs(up[0]) < 1e-9 and up[1] == -10.0
    for v in [(3.0, 4.0), (-2.0, 7.0), (5.0, -1.0)]:
        back = ndrlayout.polar_to_vector(*ndrlayout.vector_to_polar(v))
        assert math.isclose(back[0], v[0]) and math.isclose(back[1], v[1])


def side(net, arc, start, end):
    """Which side of the straight line start -> end the arc's midpoint lies on (+1 / -1)."""
    a, b = net.nodes[start], net.nodes[end]
    mx, my = ndrlayout.bezier(*ndrlayout.path_points(net, arc), 0.5)
    return math.copysign(1, (b.x - a.x) * (my - a.y) - (b.y - a.y) * (mx - a.x))


def test_opposite_arcs_between_two_nodes_bow_apart():
    # brew takes `on` and puts it back: two arcs between the same nodes.
    net = ndrlayout.parse(laid_out(TINY))
    there = next(a for a in net.arcs if (a.source, a.target) == ("on", "brew"))
    back = next(a for a in net.arcs if (a.source, a.target) == ("brew", "on"))
    assert there.c1 is not None and back.c1 is not None
    # Seen in the same direction (on -> brew), the two curves are on opposite sides.
    assert side(net, there, "on", "brew") == -side(net, back, "on", "brew")


def test_curve_avoids_a_node_in_the_way():
    text = "p 0.0 0.0 a 0 n\np 100.0 0.0 obstacle 0 n\nt 200.0 0.0 t 0 w n\ne a t 1 n\nh x\n"
    net = ndrlayout.parse(text)
    assert ndrlayout.clearance_of(net, net.arcs[0]) < 1  # straight line hits the obstacle
    ndrlayout.route(net)
    assert net.arcs[0].c1 is not None
    assert ndrlayout.clearance_of(net, net.arcs[0]) >= 40


def test_curved_arc_is_written_in_long_form():
    text = "p 0.0 0.0 a 0 n\np 100.0 0.0 obstacle 0 n\nt 200.0 0.0 t 0 w n\ne a t ?-2 n\nh x\n"
    net = ndrlayout.parse(text)
    ndrlayout.route(net)
    line = ndrlayout.render(net).splitlines()[3]
    assert re.fullmatch(r"e a [0-9.]+ [0-9.]+ t [0-9.]+ [0-9.]+ \?-2 n", line)
    again = ndrlayout.parse(ndrlayout.render(net)).arcs[0]
    assert (again.kind, again.weight) == ("?-", "2")


def test_layout_is_deterministic():
    assert laid_out(TINY) == laid_out(TINY)


def test_nodes_are_spread_out_and_positive():
    net = ndrlayout.parse(laid_out(TINY))
    nodes = list(net.nodes.values())
    assert all(n.x > 0 and n.y > 0 for n in nodes)
    closest = min(
        math.hypot(a.x - b.x, a.y - b.y) for i, a in enumerate(nodes) for b in nodes[i + 1 :]
    )
    assert closest > 30  # pixels; overlapping nodes would be unreadable in nd


def test_model_net_is_unchanged_apart_from_coordinates():
    text = (ROOT / "model" / "model.ndr").read_text(encoding="utf-8")
    before, after = ndrlayout.parse(text), ndrlayout.parse(laid_out(text))
    assert after.arcs == before.arcs
    assert {n: v.tokens for n, v in after.nodes.items()} == {
        n: v.tokens for n, v in before.nodes.items()
    }


def test_svg_preview_draws_every_node():
    net = ndrlayout.parse(laid_out(TINY))
    svg = ndrlayout.svg(net)
    assert svg.count("<circle") >= 4  # places (inhibitor ends add more circles)
    assert svg.count('fill="#333"') == 3  # transitions


def test_main_writes_output_and_svg(tmp_path):
    src = tmp_path / "net.ndr"
    src.write_text(TINY, encoding="utf-8")
    out, preview = tmp_path / "out.ndr", tmp_path / "out.svg"
    assert ndrlayout.main([str(src), "-o", str(out), "--svg", str(preview)]) == 0
    assert out.read_text(encoding="utf-8") != TINY
    assert preview.read_text(encoding="utf-8").startswith("<svg")
    assert src.read_text(encoding="utf-8") == TINY  # input untouched without --in-place
