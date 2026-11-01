from dataclasses import replace

import pytest

from espresso import Event, InfeasibleEvent, Mode, Stage, enabled, initial_state, next_state, safe
from espresso.drinks import RECIPES, Drink
from espresso.model import available
from espresso.state import Boiler, Cup, Water

E = Event


def run(s, *events):
    for e in events:
        s = next_state(s, e)
    return s


@pytest.fixture
def ready():
    """Switched on and heated to brew, no cup."""
    return run(initial_state(), E.POWER_ON, E.HEAT_TO_BREW, E.TEMP_REACHED)


def test_initial_state_matches_kb():
    s = initial_state()
    assert s.mode is Mode.OFF
    assert s.resources.boiler is Boiler.COLD
    assert s.consumables.grounds == s.descaling == 0
    assert not s.faults and s.order is None


def test_only_power_on_is_feasible_in_s0():
    assert enabled(initial_state()) == {E.POWER_ON}


def test_infeasible_event_raises():
    with pytest.raises(InfeasibleEvent):
        next_state(initial_state(), E.ORDER_ESPRESSO)


@pytest.mark.parametrize(
    ("order", "tail"),
    [
        (E.ORDER_ESPRESSO, []),
        (E.ORDER_AMERICANO, [E.ADD_HOT_WATER, E.HOT_WATER_DONE]),
        (
            E.ORDER_CAPPUCCINO,
            [E.HEAT_TO_STEAM, E.TEMP_REACHED, E.START_STEAM, E.STEAM_DONE],
        ),
    ],
)
def test_stages_follow_adr_0009(ready, order, tail):
    s = run(ready, E.CUP_PLACED, order)
    stages = [s.order.stage]
    for e in [E.START_GRIND, E.GRIND_DONE, E.START_BREW, E.BREW_DONE, *tail]:
        s = next_state(s, e)
        if s.order and s.order.stage not in stages:
            stages.append(s.order.stage)
    # Boiler already at brew, so the heating stage is skipped.
    assert stages == list(RECIPES[s.order.drink][1:])
    s = next_state(s, E.EJECT_GROUNDS)
    assert s.mode is Mode.READY and s.order is None
    assert s.consumables.grounds == 1 and s.descaling == 1


def test_order_from_cold_starts_with_heating():
    s = run(initial_state(), E.POWER_ON)
    s = replace(s, mode=Mode.READY)  # skip the warm-up
    s = next_state(s, E.ORDER_ESPRESSO)
    assert s.order.stage is Stage.HEATING
    assert {E.HEAT_TO_BREW, E.START_GRIND} <= enabled(s)  # C2: grinding may run in parallel


def test_pump_needs_a_cup(ready):  # S2
    s = run(ready, E.ORDER_ESPRESSO, E.START_GRIND, E.GRIND_DONE)
    assert E.START_BREW in enabled(s)
    assert not safe(s, E.START_BREW)
    assert safe(next_state(s, E.CUP_PLACED), E.START_BREW)


def test_pump_needs_water(ready):  # S1
    s = run(ready, E.CUP_PLACED, E.ORDER_ESPRESSO, E.START_GRIND, E.GRIND_DONE)
    s = replace(s, consumables=replace(s.consumables, water=Water.EMPTY))
    assert not safe(s, E.START_BREW)


def test_grinder_blocked_when_bin_is_full(ready):  # S4
    s = next_state(ready, E.ORDER_ESPRESSO)
    full = replace(s, consumables=replace(s.consumables, grounds=s.bounds.ng))
    assert safe(s, E.START_GRIND)
    assert not safe(full, E.START_GRIND)


def test_fault_blocks_only_dependent_drinks(ready):  # graceful degradation, S6
    s = next_state(ready, E.MILK_EMPTY)
    assert s.mode is Mode.READY
    assert not available(s, Drink.CAPPUCCINO)
    assert available(s, Drink.ESPRESSO)


def test_order_for_blocked_drink_is_rejected(ready):
    s = run(ready, E.MILK_EMPTY, E.ORDER_CAPPUCCINO)
    assert s.order.stage is Stage.REJECTED
    assert enabled(s) & {E.REJECT_ORDER}
    s = next_state(s, E.REJECT_ORDER)
    assert s.order is None and s.mode is Mode.READY


def test_fault_mode_iff_every_drink_blocked(ready):
    s = next_state(ready, E.BEANS_EMPTY)
    assert s.mode is Mode.FAULT
    s = next_state(s, E.REFILL_BEANS)
    assert s.mode is Mode.READY and not s.faults


def test_finish_fault_lets_the_drink_complete(ready):
    s = run(ready, E.CUP_PLACED, E.ORDER_ESPRESSO, E.START_GRIND, E.TRAY_FULL)
    assert s.mode is Mode.PREPARING
    s = run(s, E.GRIND_DONE)
    assert safe(s, E.START_BREW)  # tray_full blocks the pump only for later drinks
    s = run(s, E.START_BREW, E.BREW_DONE, E.EJECT_GROUNDS)
    assert s.mode is Mode.FAULT  # now every drink is blocked


def test_overheat_cleared_by_cooled_down_leaves_boiler_cold(ready):
    s = run(ready, E.OVERHEAT, E.COOLED_DOWN)
    assert s.resources.boiler is Boiler.COLD and not s.faults


def test_cup_can_be_removed_and_placed_while_idle(ready):
    s = run(ready, E.CUP_PLACED, E.CUP_REMOVED)
    assert s.resources.cup is Cup.ABSENT
