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
