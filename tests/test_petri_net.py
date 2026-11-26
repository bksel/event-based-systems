"""Integrity of the Petri net (model/model.ndr), checked with Tina.

Skipped when Tina is not on PATH (see model/TINA.md). Set PETRI_NET to check another net
file, e.g. `PETRI_NET=model/variants/small.ndr just test -k petri`. The reachability tests use
the complete graph only: if the state limit is hit, test_reachability_graph_is_complete fails
and the tests that depend on the graph are skipped, since a partial graph proves nothing.
"""

import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

DEFAULT_NET = Path(__file__).resolve().parent.parent / "model" / "model.ndr"
NET = Path(os.environ.get("PETRI_NET", DEFAULT_NET))
STATE_LIMIT = 200_000  # over 10x the current net; raise it if the net grows

pytestmark = pytest.mark.skipif(
    shutil.which("tina") is None, reason="Tina is not on PATH (see model/TINA.md)"
)


def tina(*args: str, timeout: float = 120) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["tina", *args], capture_output=True, text=True, timeout=timeout, check=False
    )


@pytest.fixture(scope="module")
def reachability(tmp_path_factory):
    """Summary (stdout) and full report (file) of the reachability graph.

    -s 0 turns off Tina's early "possibly unbounded" test, which ignores inhibitor arcs and gives
    false alarms on our net.
    """
    report = tmp_path_factory.mktemp("tina") / "reachability.txt"
    run = tina("-R", "-s", "0", "-c", str(STATE_LIMIT), str(NET), str(report))
    assert run.returncode == 0, run.stdout + run.stderr
    return run.stdout, report.read_text(encoding="utf-8")


def complete(reachability):
    """The graph, or skip: results from an incomplete graph prove nothing either way."""
    summary, report = reachability
    if "enumeration not completed" in report or "possibly" in summary:
        pytest.skip("reachability graph incomplete, see test_reachability_graph_is_complete")
    return summary, report


def summary_row(summary: str, name: str) -> list[str]:
    """Columns of a row in Tina's summary box: "states" -> [count, props, psets, dead, live]."""
    match = re.search(rf"^#\s+{name}\s+(.+?)\s*#\s*$", summary, re.M)
    assert match, summary
    return match.group(1).split()


def test_net_parses_without_skipped_lines():
    run = tina("-p", str(NET))
    output = run.stdout + run.stderr
    assert run.returncode == 0, output
    assert "bad line" not in output, output


def test_reachability_graph_is_complete(reachability):
    summary, report = reachability
    assert "enumeration not completed" not in report, (
        f"more than {STATE_LIMIT} states: results are incomplete"
    )
    assert "possibly" not in summary, summary


def test_net_is_bounded(reachability):
    summary, _ = reachability
    verdict = re.search(r"^#\s+((?:not |possibly )?bounded),", summary, re.M)
    assert verdict, summary
    assert verdict.group(1) == "bounded", (
        f"an unbounded place means some transition can fire without limit:\n{summary}"
    )


def test_no_deadlocks(reachability):  # L2
    summary, report = complete(reachability)
    dead = summary_row(summary, "states")[3]
    assert dead == "0", re.search(r"dead marking\(s\):.*", report).group(0)


def test_every_transition_can_fire(reachability):
    # A transition that never fires is guarded by a condition that cannot be met: a wrong or
    # missing arc.
    _, report = complete(reachability)
    match = re.search(r"(\d+) dead transition\(s\)", report)
    assert match, report[-2000:]
    assert match.group(1) == "0", re.search(r"dead transition\(s\):.*", report).group(0)


# L1: recoverability. Home state sh (docs/domain/state.md): switched on, no order, no faults.
# As a marking: only these places are marked, the ones in HOME_ONE with one token each. The
# counters and the boiler may have any value. A place not listed (a recipe stage, an operation
# in progress, a fault) makes the marking not a home marking.
HOME_ONE = {"drink_done", "brew_unit__empty", "cup__empty", "pump__idle"} | {
    "water_available",
    "milk_available",
}
HOME_ANY = {"beans_available", "bin_space_available", "boiler__cold", "boiler__brew"} | {
    "boiler__steam"
}


def section(report: str, start: str, end: str) -> str:
    begin = report.index(start)
    return report[begin : report.index(end, begin)]


def markings(report: str) -> dict[int, dict[str, int]]:
    out = {}
    for m in re.finditer(
        r"^(\d+) : (.*)$", section(report, "MARKINGS:", "REACHABILITY GRAPH:"), re.M
    ):
        tokens = {}
        for item in m.group(2).split():
            place, _, n = item.partition("*")
            tokens[place] = int(n or 1)
        out[int(m.group(1))] = tokens
    return out


def successors(report: str) -> dict[int, set[int]]:
    graph = section(report, "REACHABILITY GRAPH:", "LIVENESS ANALYSIS")
    out = {}
    for m in re.finditer(r"^(\d+) -> (.*)$", graph, re.M):
        out[int(m.group(1))] = {int(edge.rpartition("/")[2]) for edge in m.group(2).split(", ")}
    return out


def components(report: str) -> list[set[int]]:
    sccs = report[report.index("STRONG CONNECTED COMPONENTS:") :]
    return [set(map(int, m.group(1).split())) for m in re.finditer(r"^\d+ : ([\d ]+)$", sccs, re.M)]


def is_home(tokens: dict[str, int]) -> bool:
    return set(tokens) <= HOME_ONE | HOME_ANY and all(tokens.get(p) == 1 for p in HOME_ONE)


@pytest.fixture(scope="module")
def graph(reachability):
    _, report = complete(reachability)
    marks = markings(report)
    home = {s for s, tokens in marks.items() if is_home(tokens)}
    return marks, successors(report), components(report), home


def test_home_state_is_reachable_from_every_marking(graph):  # L1
    marks, succ, _, home = graph
    assert home, "no reachable marking is a home marking"
    pred: dict[int, set[int]] = {s: set() for s in marks}
    for s, targets in succ.items():
        for t in targets:
            pred[t].add(s)
    reaches_home, todo = set(home), list(home)
    while todo:
        for p in pred[todo.pop()] - reaches_home:
            reaches_home.add(p)
            todo.append(p)
    stuck = sorted(set(marks) - reaches_home)
    assert not stuck, f"{len(stuck)} markings cannot reach sh, e.g. {marks[stuck[0]]}"


def test_some_home_marking_is_reachable_from_everywhere(graph):  # L1, the strong form
    # A finite graph always ends in a component it cannot leave. With exactly one such
    # component, every marking can reach all of it, so a home marking in it is a home marking
    # of the net in Tina's sense.
    _, succ, sccs, home = graph
    bottom = [c for c in sccs if all(succ.get(s, set()) <= c for s in c)]
    assert len(bottom) == 1, f"{len(bottom)} components that cannot be left"
    assert bottom[0] & home, "the component that cannot be left has no home marking"


# Safety, reduced scope (ADR 0013 rewords S5 and S6). Each property is a condition on every
# reachable marking or on every edge of the graph. "Runs" means the operation's `*_started` place
# is marked. Properties the net breaks today are xfail(strict=True): they are listed in the
# model README as known issues and fixed in task A3b. When a fix lands, the test passes, strict
# turns that into a failure, and the marker must be removed.
ACTIVE_PREFIXES = ("recipe__",)
ACTIVE_SUFFIXES = ("_started", "_ended", "_failed")


def labelled_edges(report: str) -> list[tuple[int, str, int]]:
    graph = section(report, "REACHABILITY GRAPH:", "LIVENESS ANALYSIS")
    out = []
    for m in re.finditer(r"^(\d+) -> (.*)$", graph, re.M):
        for edge in m.group(2).split(", "):
            transition, _, target = edge.rpartition("/")
            out.append((int(m.group(1)), transition, int(target)))
    return out


def drink_active(tokens: dict[str, int]) -> bool:
    return any(p.startswith(ACTIVE_PREFIXES) or p.endswith(ACTIVE_SUFFIXES) for p in tokens)


def violations(marks, condition) -> list[dict[str, int]]:
    return [tokens for tokens in marks.values() if condition(tokens)]


def input_arcs(transition: str) -> set[str]:
    """Places with an ordinary (not inhibitor) arc into the transition, read from the .ndr file."""
    places = set()
    for line in NET.read_text(encoding="utf-8").splitlines():
        fields = line.split()
        if fields[:1] != ["e"] or fields[-2].startswith("?"):
            continue
        names = [f for f in fields[1:-2] if not re.fullmatch(r"-?[\d.]+", f)]
        if names[-1] == transition:
            places.add(names[0])
    return places


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="N8: water_empty does not stop the pump, OE__fail_brew does it later",
)
def test_s1_pump_never_runs_without_water(graph):
    marks = graph[0]
    bad = violations(marks, lambda m: "brewing_started" in m and "water_available" not in m)
    assert not bad, f"{len(bad)} markings, e.g. {bad[0]}"


def test_s2_pump_never_runs_without_a_cup(graph):
    # The reduced scope has a fixed cup (ADR 0013): it is always there, empty or full.
    marks = graph[0]
    bad = violations(marks, lambda m: ("cup__empty" in m) == ("cup__full" in m))
    assert not bad, f"{len(bad)} markings without exactly one cup state, e.g. {bad[0]}"


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="N8: milk_empty does not stop the steamer, OE__fail_steam does it later",
)
def test_s3_steamer_never_runs_without_milk(graph):
    marks = graph[0]
    bad = violations(marks, lambda m: "steam_started" in m and "milk_available" not in m)
    assert not bad, f"{len(bad)} markings, e.g. {bad[0]}"


@pytest.mark.xfail(
    strict=True, raises=AssertionError, reason="N9: CE__start_grind does not check the grounds bin"
)
def test_s4_grinder_never_runs_with_a_full_grounds_container(graph):
    marks = graph[0]
    bad = violations(marks, lambda m: "grinding_started" in m and "bin_space_available" not in m)
    assert not bad, f"{len(bad)} markings, e.g. {bad[0]}"


@pytest.mark.parametrize(
    ("transition", "permit"),
    [
        ("CE__start_grind", "beans_available"),
        ("CE__restart_grind", "beans_available"),
        ("CE__start_brew", "water_available"),
        ("CE__restart_brew", "water_available"),
        ("CE__add_hot_water", "water_available"),
        ("CE__start_steam", "milk_available"),
        ("CE__restart_steam", "milk_available"),
    ],
)
def test_s5_operations_start_only_with_their_permit(transition, permit):
    # S5 as reworded in ADR 0013, read as a guard on starting. That the permit stays available
    # while the operation runs is S1 and S3.
    assert permit in input_arcs(transition), f"{transition} does not take {permit}"


def test_s6_no_order_while_a_drink_is_active(graph, reachability):
    marks = graph[0]
    _, report = reachability
    bad = [
        (t, marks[source])
        for source, t, _ in labelled_edges(report)
        if t.startswith("OE__order_") and drink_active(marks[source])
    ]
    assert not bad, f"{len(bad)} orders accepted during a drink, e.g. {bad[0]}"
