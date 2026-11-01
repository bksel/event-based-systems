from dataclasses import replace

import pytest

from espresso import E_CON, Controller, Event, FixedOrderPolicy, initial_state, next_state
from espresso.state import Boiler, Mode

E = Event


def run(s, *events):
    for e in events:
        s = next_state(s, e)
    return s


class Recorder:
    """A policy that records what it was offered and returns a fixed answer."""

    def __init__(self, answer=None):
        self.answer = answer
        self.offered = None

    def choose(self, s, candidates):
        self.offered = candidates
        return self.answer


@pytest.fixture
def ready():
    return run(initial_state(), E.POWER_ON, E.HEAT_TO_BREW, E.TEMP_REACHED)


def test_candidates_are_enabled_and_safe(ready):
    s = run(ready, E.ORDER_ESPRESSO, E.START_GRIND, E.GRIND_DONE)  # no cup yet
    policy = Recorder()
    Controller(policy).decide(s)
    assert E.START_BREW not in policy.offered  # enabled, but unsafe (S2)
    assert policy.offered <= E_CON


def test_reject_order_bypasses_the_policy(ready):
    s = run(ready, E.MILK_EMPTY, E.ORDER_CAPPUCCINO)
    policy = Recorder(answer=None)
    assert Controller(policy).decide(s) is E.REJECT_ORDER
    assert policy.offered is None  # never asked


def test_policy_may_wait(ready):
    s = next_state(ready, E.ORDER_ESPRESSO)
    assert Controller(Recorder(answer=None)).decide(s) is None


def test_policy_choice_outside_candidates_is_an_error(ready):
    with pytest.raises(ValueError):
        Controller(Recorder(answer=E.START_STEAM)).decide(ready)


def test_fixed_order_heats_before_grinding():
    s = replace(next_state(initial_state(), E.POWER_ON), mode=Mode.READY)
    s = next_state(s, E.ORDER_ESPRESSO)  # cold boiler: both heating and grinding enabled
    assert Controller(FixedOrderPolicy()).decide(s) is E.HEAT_TO_BREW


def test_fixed_order_priority_is_configurable():
    s = replace(next_state(initial_state(), E.POWER_ON), mode=Mode.READY)
    s = next_state(s, E.ORDER_ESPRESSO)
    grind_first = FixedOrderPolicy(priority=(E.START_GRIND, E.HEAT_TO_BREW))
    assert Controller(grind_first).decide(s) is E.START_GRIND


def test_fixed_order_returns_to_brew_after_steam(ready):  # C1 baseline
    s = replace(ready, resources=replace(ready.resources, boiler=Boiler.STEAM))
    assert Controller(FixedOrderPolicy()).decide(s) is E.HEAT_TO_BREW
