"""Event-based supervisory controller of an espresso machine: simulator core.

See ADR 0012 for the architecture and sim/examples/ for how to use it.
"""

from espresso.controller import Controller
from espresso.drinks import Drink, Stage
from espresso.engine import Simulator
from espresso.events import E_CON, E_OBS, Event
from espresso.model import (
    InfeasibleEvent,
    InvariantViolation,
    available,
    check_invariants,
    enabled,
    next_state,
    safe,
)
from espresso.params import ANALYSIS_BOUNDS, SIMULATION_BOUNDS, Bounds
from espresso.plant import ScriptedPlant
from espresso.policy import FixedOrderPolicy, Policy
from espresso.state import Mode, State, initial_state, is_home
from espresso.trace import TraceEntry, read_jsonl, replay, write_jsonl

__all__ = [
    "ANALYSIS_BOUNDS",
    "E_CON",
    "E_OBS",
    "SIMULATION_BOUNDS",
    "Bounds",
    "Controller",
    "Drink",
    "Event",
    "FixedOrderPolicy",
    "InfeasibleEvent",
    "InvariantViolation",
    "Mode",
    "Policy",
    "ScriptedPlant",
    "Simulator",
    "Stage",
    "State",
    "TraceEntry",
    "available",
    "check_invariants",
    "enabled",
    "initial_state",
    "is_home",
    "next_state",
    "read_jsonl",
    "replay",
    "safe",
    "write_jsonl",
]
