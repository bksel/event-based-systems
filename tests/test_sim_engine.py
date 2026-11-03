import pytest

from espresso import (
    ANALYSIS_BOUNDS,
    Event,
    FixedOrderPolicy,
    Mode,
    ScriptedPlant,
    Simulator,
    is_home,
    read_jsonl,
    replay,
    write_jsonl,
)
from espresso.state import Boiler

E = Event


def simulate(*script, **kwargs):
    sim = Simulator(FixedOrderPolicy(), **kwargs)  # checks the invariants after every event
    ScriptedPlant(script).install(sim)
    sim.run()
    return sim


def events(sim):
    return [t.event for t in sim.trace]


def test_espresso_run():
    sim = simulate((0, E.POWER_ON), (60, E.ORDER_ESPRESSO), (65, E.CUP_PLACED))
    assert events(sim) == [
        E.POWER_ON,
        E.HEAT_TO_BREW,
        E.TEMP_REACHED,
        E.ORDER_ESPRESSO,
        E.START_GRIND,
        E.CUP_PLACED,
        E.GRIND_DONE,
        E.START_BREW,
        E.BREW_DONE,
        E.EJECT_GROUNDS,
    ]
    assert is_home(sim.state)
    assert sim.state.consumables.grounds == 1 and sim.state.descaling == 1
    assert not sim.ignored


@pytest.mark.parametrize("order", [E.ORDER_AMERICANO, E.ORDER_CAPPUCCINO])
def test_other_drinks_end_at_home(order):
    sim = simulate((0, E.POWER_ON), (60, order), (60, E.CUP_PLACED))
    assert is_home(sim.state)
    assert sim.state.resources.boiler is Boiler.BREW  # baseline returns to brew after steam (C1)


def test_completion_comes_after_the_duration():
    sim = simulate((0, E.POWER_ON), durations={E.HEAT_TO_BREW: 12.5})
    assert sim.trace[-1].event is E.TEMP_REACHED and sim.trace[-1].time == 12.5


def test_infeasible_plant_event_is_ignored():
    sim = simulate((0, E.ORDER_ESPRESSO), (1, E.POWER_ON))
    assert [t.event for t in sim.ignored] == [E.ORDER_ESPRESSO]
    assert E.ORDER_ESPRESSO not in events(sim)


def test_overheat_cancels_heating():
    # Cappuccino, then the baseline heats back to brew; overheat interrupts that.
    sim = simulate((0, E.POWER_ON), (60, E.ORDER_CAPPUCCINO), (60, E.CUP_PLACED), (200, E.OVERHEAT))
    assert sim.state.mode is Mode.FAULT
    assert E.OVERHEAT in sim.state.faults
    assert events(sim)[-1] is E.OVERHEAT  # the cancelled temp_reached never arrives


def test_order_while_preparing_is_ignored():
    sim = simulate(
        (0, E.POWER_ON), (60, E.ORDER_ESPRESSO), (61, E.ORDER_ESPRESSO), (62, E.CUP_PLACED)
    )
    assert len(sim.ignored) == 1 and is_home(sim.state)


def test_runs_with_analysis_bounds():
    script = [(0, E.POWER_ON), (0, E.CUP_PLACED)]
    script += [(100 * i, E.ORDER_ESPRESSO) for i in range(1, 4)]
    sim = simulate(*script, bounds=ANALYSIS_BOUNDS)
    assert sim.state.consumables.grounds == 3  # = Ng
    # d = Nover: no drink is available any more until descaling (not implemented yet).
    assert sim.state.descaling == ANALYSIS_BOUNDS.nover


def test_same_seed_same_trace():
    script = [(0, E.POWER_ON), (60, E.ORDER_CAPPUCCINO), (70, E.CUP_PLACED)]
    assert simulate(*script, seed=1).trace == simulate(*script, seed=1).trace


def test_trace_round_trip_and_replay(tmp_path):
    sim = simulate((0, E.POWER_ON), (60, E.ORDER_AMERICANO), (65, E.CUP_PLACED))
    path = tmp_path / "trace.jsonl"
    write_jsonl(sim.trace, path)
    loaded = read_jsonl(path)
    assert loaded == sim.trace
    assert replay(loaded)[-1] == sim.state
