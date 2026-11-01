"""Prioritization policies: they resolve conflicts C1–C4 (docs/requirements/properties.md).

A policy only chooses among the controllable events that are enabled and safe. It may return
None to wait, e.g. to keep the boiler at steam after a cappuccino (C1).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from espresso.events import Event
from espresso.state import State

E = Event


class Policy(Protocol):
    def choose(self, s: State, candidates: frozenset[Event]) -> Event | None: ...


DEFAULT_PRIORITY = (
    E.EJECT_GROUNDS,
    E.HEAT_TO_BREW,  # C1: back to brew at once after a cappuccino
    E.HEAT_TO_STEAM,
    E.START_GRIND,  # C2: grinds while heating, since both are enabled together
    E.START_BREW,
    E.ADD_HOT_WATER,
    E.START_STEAM,
)


@dataclass(frozen=True)
class FixedOrderPolicy:
    """Baseline: the first candidate in a fixed priority order."""

    priority: tuple[Event, ...] = DEFAULT_PRIORITY

    def choose(self, s: State, candidates: frozenset[Event]) -> Event | None:
        return next((e for e in self.priority if e in candidates), None)
