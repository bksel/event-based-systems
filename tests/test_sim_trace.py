import pytest

from espresso import (
    ANALYSIS_BOUNDS,
    Event,
    InfeasibleEvent,
    TraceEntry,
    initial_state,
    read_jsonl,
    replay,
    write_jsonl,
)

E = Event


def test_jsonl_round_trip(tmp_path):
    trace = [TraceEntry(0.0, E.POWER_ON, "plant"), TraceEntry(0.0, E.HEAT_TO_BREW, "controller")]
    path = tmp_path / "t.jsonl"
    write_jsonl(trace, path)
    assert read_jsonl(path) == trace
    assert '"event": "power_on"' in path.read_text()  # names as in the catalogue


def test_replay_returns_every_state():
    trace = [TraceEntry(0.0, E.POWER_ON, "plant"), TraceEntry(0.0, E.HEAT_TO_BREW, "controller")]
    states = replay(trace)
    assert len(states) == 3 and states[0] == initial_state()


def test_replay_uses_the_given_bounds():
    assert replay([], ANALYSIS_BOUNDS)[0].bounds == ANALYSIS_BOUNDS


def test_replay_rejects_an_invalid_trace():
    with pytest.raises(InfeasibleEvent):
        replay([TraceEntry(0.0, E.ORDER_ESPRESSO, "plant")])
