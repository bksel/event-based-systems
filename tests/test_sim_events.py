"""The code's event alphabet must match the KB catalogue (docs/domain/events.md)."""

import re
from pathlib import Path

from espresso.events import CLEARED_BY, COMPLETED_BY, COMPLETION, E_CON, E_OBS, FAULTS, SERVICE
from espresso.params import DEFAULT_DURATIONS

CATALOGUE = (Path(__file__).resolve().parent.parent / "docs/domain/events.md").read_text(
    encoding="utf-8"
)
OBSERVABLE, rest = CATALOGUE.split("## Controllable")
CONTROLLABLE, PAIRS = rest.split("## Fault → service")
ROW = re.compile(r"^\| `([a-z_]+)` \| ([^|]+?) \|", re.M)


def names(section):
    return {name for name, _ in ROW.findall(section)}


def category(name):
    return {n: c.strip() for n, c in ROW.findall(OBSERVABLE)}[name]


def test_observable_events_match_catalogue():
    assert {str(e) for e in E_OBS} == names(OBSERVABLE)


def test_controllable_events_match_catalogue():
    assert {str(e) for e in E_CON} == names(CONTROLLABLE)


def test_categories_match_catalogue():
    assert {str(e) for e in FAULTS} == {n for n in names(OBSERVABLE) if category(n) == "fault"}
    assert {str(e) for e in SERVICE} == {n for n in names(OBSERVABLE) if category(n) == "service"}
    assert {str(e) for e in COMPLETION} == {
        n for n in names(OBSERVABLE) if category(n) == "completion"
    }


def test_fault_service_pairs_match_catalogue():
    pairs = re.findall(r"^\| `([a-z_]+)` \| `([a-z_]+)`", PAIRS, re.M)
    assert {(str(f), str(s)) for f, s in CLEARED_BY.items()} == set(pairs)


def test_every_timed_operation_has_a_duration():
    assert set(COMPLETED_BY) <= set(DEFAULT_DURATIONS)
    assert set(COMPLETED_BY) <= E_CON
    assert set(COMPLETED_BY.values()) <= COMPLETION
