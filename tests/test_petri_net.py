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
