"""Plant: the source of user and sensor events.

Completion events are not generated here; the simulator schedules them itself when a
controllable operation starts. A random plant (orders, faults, service delays) comes with T7.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING

from espresso.events import Event

if TYPE_CHECKING:
    from espresso.engine import Simulator


class ScriptedPlant:
    """Feeds a fixed list of (time, event) pairs, e.g. a scenario from scenarios.md."""

    def __init__(self, script: Iterable[tuple[float, Event]]) -> None:
        self.script = tuple(script)

    def install(self, sim: Simulator) -> None:
        for time, event in self.script:
            sim.inject(event, at=time)
