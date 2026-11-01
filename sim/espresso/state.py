"""The state s = (m, r, c, d, F, p) from docs/domain/state.md.

All classes are immutable. Change a state only through model.next_state.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

from espresso.drinks import Drink, Stage
from espresso.events import Event
from espresso.params import SIMULATION_BOUNDS, Bounds


class Mode(StrEnum):
    OFF = "off"
    HEATING = "heating"
    READY = "ready"
    PREPARING = "preparing"
    FAULT = "fault"
    SERVICE = "service"
    DESCALING = "descaling"


class Actuator(StrEnum):
    IDLE = "idle"
    BUSY = "busy"


class Boiler(StrEnum):
    COLD = "cold"
    BREW = "brew"
    STEAM = "steam"


class BrewUnit(StrEnum):
    EMPTY = "empty"
    LOADED = "loaded"
    USED = "used"


class Cup(StrEnum):
    ABSENT = "absent"
    PRESENT = "present"


class Water(StrEnum):
    OK = "ok"
    LOW = "low"
    EMPTY = "empty"


class Supply(StrEnum):
    """Beans and milk."""

    OK = "ok"
    EMPTY = "empty"


class Tray(StrEnum):
    OK = "ok"
    FULL = "full"


@dataclass(frozen=True)
class Resources:
    """r. `heating_to` is the boiler's target while the heater is on (None = heater off).

    It is not in the KB tuple yet: the KB has no way to say "heating has started".
    """

    grinder: Actuator = Actuator.IDLE
    pump: Actuator = Actuator.IDLE
    steamer: Actuator = Actuator.IDLE
    boiler: Boiler = Boiler.COLD
    heating_to: Boiler | None = None
    brew_unit: BrewUnit = BrewUnit.EMPTY
    cup: Cup = Cup.ABSENT


@dataclass(frozen=True)
class Consumables:
    """c. `grounds` is the counter g."""

    water: Water = Water.OK
    beans: Supply = Supply.OK
    milk: Supply = Supply.OK
    grounds: int = 0
    tray: Tray = Tray.OK


@dataclass(frozen=True)
class Order:
    """p: the current drink and its recipe stage."""

    drink: Drink
    stage: Stage


@dataclass(frozen=True)
class State:
    mode: Mode  # m
    resources: Resources  # r
    consumables: Consumables  # c
    descaling: int  # d
    faults: frozenset[Event]  # F
    order: Order | None  # p
    bounds: Bounds = field(default=SIMULATION_BOUNDS)  # parameters, not part of the tuple


def initial_state(bounds: Bounds = SIMULATION_BOUNDS) -> State:
    """s0: off, cold, idle, full, g = d = 0, no faults, no order."""
    return State(
        mode=Mode.OFF,
        resources=Resources(),
        consumables=Consumables(),
        descaling=0,
        faults=frozenset(),
        order=None,
        bounds=bounds,
    )


def is_home(s: State) -> bool:
    """sh: ready, no order, no faults."""
    return s.mode is Mode.READY and s.order is None and not s.faults
