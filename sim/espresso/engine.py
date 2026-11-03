"""Discrete event simulator: virtual clock, event queue, controller reactions, trace."""

from __future__ import annotations

import heapq
import itertools
import math
import random
from collections.abc import Callable, Mapping

from espresso.controller import Controller
from espresso.events import COMPLETED_BY, COMPLETION, E_OBS, Event
from espresso.model import check_invariants, expected_completions, feasible, next_state
from espresso.params import DEFAULT_DURATIONS, SIMULATION_BOUNDS, Bounds
from espresso.policy import Policy
from espresso.state import State, initial_state
from espresso.trace import TraceEntry, source_of

Observer = Callable[[TraceEntry, State], None]


class Simulator:
    """Runs the plant and the controller in simulated time.

    Plant events are injected with `inject`. After each one the controller fires controllable
    events until its policy waits. Each controllable operation schedules its completion event
    after its duration; if the operation stops early (a fault), the completion is cancelled.

    Plant events that are not in EF(s) when their time comes are recorded in `ignored`, not in
    `trace`, so the trace is always a valid run.
    """

    def __init__(
        self,
        policy: Policy,
        *,
        bounds: Bounds = SIMULATION_BOUNDS,
        durations: Mapping[Event, float] = DEFAULT_DURATIONS,
        seed: int = 0,
        check: bool = True,
        max_reactions: int = 100,
    ) -> None:
        self.controller = Controller(policy)
        self.state = initial_state(bounds)
        self.time = 0.0
        self.durations = dict(durations)
        self.rng = random.Random(seed)  # for random plants; one seeded RNG per run
        self.check = check
        self.max_reactions = max_reactions
        self.trace: list[TraceEntry] = []
        self.ignored: list[TraceEntry] = []
        self._queue: list[tuple[float, int, Event]] = []
        self._seq = itertools.count()
        self._pending: dict[Event, int] = {}  # completion event -> seq of its live queue entry
        self._observers: list[Observer] = []

    def subscribe(self, observer: Observer) -> None:
        """Call observer(entry, new_state) after every fired event, e.g. to update a GUI."""
        self._observers.append(observer)

    def inject(self, event: Event, at: float | None = None) -> None:
        """Queue a plant event at time `at` (default: now)."""
        if event not in E_OBS or event in COMPLETION:
            raise ValueError(f"{event} is not a plant event that can be injected")
        time = self.time if at is None else float(at)
        if time < self.time:
            raise ValueError(f"cannot inject {event} at {time}, the clock is at {self.time}")
        heapq.heappush(self._queue, (time, next(self._seq), event))

    def step(self) -> bool:
        """Process the next queued event and the controller's reaction. False if none is left."""
        while self._queue:
            time, seq, event = heapq.heappop(self._queue)
            if event in COMPLETION:
                if self._pending.get(event) != seq:
                    continue  # cancelled
                del self._pending[event]
            self.time = time
            if not feasible(self.state, event):
                self.ignored.append(TraceEntry(time, event, source_of(event)))
                return True
            self._fire(event)
            self._react()
            return True
        return False

    def run(self, until: float = math.inf) -> None:
        """Process events up to and including time `until`."""
        while self._queue and self._queue[0][0] <= until:
            self.step()
        if until != math.inf:
            self.time = max(self.time, until)

    def _fire(self, event: Event) -> None:
        self.state = next_state(self.state, event)
        if self.check:
            check_invariants(self.state)
        entry = TraceEntry(self.time, event, source_of(event))
        self.trace.append(entry)
        if (completion := COMPLETED_BY.get(event)) is not None:
            seq = next(self._seq)
            heapq.heappush(self._queue, (self.time + self.durations[event], seq, completion))
            self._pending[completion] = seq
        running = expected_completions(self.state)
        for completion in [c for c in self._pending if c not in running]:
            del self._pending[completion]
        for observer in self._observers:
            observer(entry, self.state)

    def _react(self) -> None:
        for _ in range(self.max_reactions):
            event = self.controller.decide(self.state)
            if event is None:
                return
            self._fire(event)
        raise RuntimeError(f"controller fired {self.max_reactions} events without waiting")
