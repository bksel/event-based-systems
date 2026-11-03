"""Traces: the timed event sequence of a run.

A trace is the bridge to the Petri net and to the scenarios in docs/requirements: replaying it
in the net and here must give the same result (ADR 0003).
"""

from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from espresso.events import E_CON, Event
from espresso.model import next_state
from espresso.params import SIMULATION_BOUNDS, Bounds
from espresso.state import State, initial_state


@dataclass(frozen=True)
class TraceEntry:
    time: float  # seconds of simulated time
    event: Event
    source: str  # "plant" (E_obs) or "controller" (E_con)


def source_of(e: Event) -> str:
    return "controller" if e in E_CON else "plant"


def write_jsonl(trace: Iterable[TraceEntry], path: Path) -> None:
    with path.open("w", encoding="utf-8") as f:
        for t in trace:
            f.write(json.dumps({"time": t.time, "event": t.event, "source": t.source}) + "\n")


def read_jsonl(path: Path) -> list[TraceEntry]:
    with path.open(encoding="utf-8") as f:
        rows = [json.loads(line) for line in f if line.strip()]
    return [TraceEntry(r["time"], Event(r["event"]), r["source"]) for r in rows]


def replay(trace: Iterable[TraceEntry], bounds: Bounds = SIMULATION_BOUNDS) -> list[State]:
    """States s0, s1, … visited by the trace. Raises InfeasibleEvent if it is not a valid run."""
    states = [initial_state(bounds)]
    for t in trace:
        states.append(next_state(states[-1], t.event))
    return states
