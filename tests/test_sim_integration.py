"""End-to-end runs through the whole stack: plant -> engine -> controller -> model -> trace.

The engine checks S1–S5 and the mode rule after every event, so these runs also test safety.
"""

import random

import pytest

from espresso import (
    ANALYSIS_BOUNDS,
    E_OBS,
    Event,
    FixedOrderPolicy,
    Mode,
    ScriptedPlant,
    Simulator,
    enabled,
    is_home,
    replay,
)
from espresso.events import CLEARED_BY, COMPLETION
from espresso.state import Cup

E = Event


def test_a_day_with_faults_and_service():
    """Three drinks, graceful degradation, a finish-class fault mid-drink, a full bin."""
    sim = Simulator(FixedOrderPolicy(), bounds=ANALYSIS_BOUNDS)
    ScriptedPlant(
        [
            (0, E.POWER_ON),
            (0, E.CUP_PLACED),
            (100, E.ORDER_ESPRESSO),  # drink 1
            (200, E.MILK_EMPTY),
            (210, E.ORDER_CAPPUCCINO),  # rejected: no milk
            (220, E.ORDER_AMERICANO),  # drink 2: still available
            (225, E.TRAY_FULL),  # finish class: drink 2 completes
            (400, E.ORDER_ESPRESSO),  # rejected: machine in fault mode
            (410, E.EMPTY_TRAY),
            (420, E.REFILL_MILK),
            (500, E.ORDER_CAPPUCCINO),  # drink 3, grounds g = Ng afterwards
            (800, E.BIN_FULL),
            (810, E.EMPTY_BIN),
        ]
    ).install(sim)

    modes = []
    sim.subscribe(lambda entry, s: modes.append((entry.event, s.mode)))
    sim.run()

    served = [t.time for t in sim.trace if t.event is E.EJECT_GROUNDS]
    rejected = [t.time for t in sim.trace if t.event is E.REJECT_ORDER]
    assert len(served) == 3
    assert rejected == [210, 400]
    assert (E.TRAY_FULL, Mode.PREPARING) in modes  # drink 2 was not interrupted
    assert (E.REJECT_ORDER, Mode.FAULT) in modes
    assert is_home(sim.state)
    assert sim.state.consumables.grounds == 0 and sim.state.descaling == 3
    assert not sim.ignored
    assert replay(sim.trace, ANALYSIS_BOUNDS)[-1] == sim.state


@pytest.mark.parametrize("seed", range(20))
def test_random_plant_never_breaks_safety(seed):
    """A random user: at random times, any plant event that is feasible right now.

    Runs until 300 plant events. Fails if an invariant breaks, the controller loops, or the
    trace is not a valid run.
    """
    rng = random.Random(seed)
    sim = Simulator(FixedOrderPolicy(), bounds=ANALYSIS_BOUNDS, seed=seed)
    plant_events = sorted(E_OBS - COMPLETION)
    for _ in range(300):
        options = [e for e in plant_events if e in enabled(sim.state)]
        sim.inject(rng.choice(options), at=sim.time + rng.uniform(0, 40))
        sim.run(until=sim.time + 40)
    assert replay(sim.trace, ANALYSIS_BOUNDS)[-1] == sim.state
    recover(sim)
    assert is_home(sim.state), sim.state  # L1: sh is reachable once the user does the service


def recover(sim):
    """Let things finish, then do what the user and sensors would: service every active fault."""
    sim.run()
    s = sim.state
    if s.consumables.grounds >= s.bounds.ng and E.BIN_FULL not in s.faults:
        sim.inject(E.BIN_FULL)  # the sensor reports what the counter already says
    if s.resources.cup is not Cup.PRESENT:
        sim.inject(E.CUP_PLACED)  # a drink may be waiting for its cup
    sim.run()
    for fault in sorted(sim.state.faults):
        sim.inject(CLEARED_BY[fault])
    sim.run()
