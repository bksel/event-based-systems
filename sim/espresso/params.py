"""Parameters: counter bounds (ADR 0011) and operation durations."""

from __future__ import annotations

from dataclasses import dataclass

from espresso.events import Event


@dataclass(frozen=True)
class Bounds:
    ng: int  # grounds container capacity
    ndue: int  # descaling warning threshold
    nover: int  # drinks blocked from here on

    def __post_init__(self) -> None:
        if not (self.ng > 0 and 0 < self.ndue < self.nover):
            raise ValueError(f"invalid bounds: {self}")


ANALYSIS_BOUNDS = Bounds(ng=3, ndue=2, nover=3)
SIMULATION_BOUNDS = Bounds(ng=10, ndue=150, nover=200)

# Seconds per controllable operation, until its completion event. Placeholders until T7
# collects real values.
DEFAULT_DURATIONS: dict[Event, float] = {
    Event.HEAT_TO_BREW: 45.0,
    Event.HEAT_TO_STEAM: 30.0,
    Event.START_GRIND: 10.0,
    Event.START_BREW: 25.0,
    Event.ADD_HOT_WATER: 15.0,
    Event.START_STEAM: 30.0,
    Event.START_RINSE: 10.0,
    Event.START_MILK_CLEANING: 20.0,
    Event.START_DESCALING: 600.0,
}
