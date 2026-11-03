"""Drinks, recipe stages, R(k), B(f) and fault classes.

Sources: docs/domain/drinks-and-resources.md, ADR 0009 (stages), ADR 0010 (faults).
"""

from __future__ import annotations

from enum import StrEnum

from espresso.events import Event


class Drink(StrEnum):
    ESPRESSO = "espresso"
    AMERICANO = "americano"
    CAPPUCCINO = "cappuccino"


class Stage(StrEnum):
    HEATING = "heating"
    GRINDING = "grinding"
    BREWING = "brewing"
    HOT_WATER = "hot_water"
    STEAM_HEATING = "steam_heating"
    STEAMING = "steaming"
    DONE = "done"
    # Not a recipe stage: the order was for an unavailable drink and waits for reject_order.
    REJECTED = "rejected"


RECIPES: dict[Drink, tuple[Stage, ...]] = {
    Drink.ESPRESSO: (Stage.HEATING, Stage.GRINDING, Stage.BREWING, Stage.DONE),
    Drink.AMERICANO: (Stage.HEATING, Stage.GRINDING, Stage.BREWING, Stage.HOT_WATER, Stage.DONE),
    Drink.CAPPUCCINO: (
        Stage.HEATING,
        Stage.GRINDING,
        Stage.BREWING,
        Stage.STEAM_HEATING,
        Stage.STEAMING,
        Stage.DONE,
    ),
}

ORDER_DRINK: dict[Event, Drink] = {
    Event.ORDER_ESPRESSO: Drink.ESPRESSO,
    Event.ORDER_AMERICANO: Drink.AMERICANO,
    Event.ORDER_CAPPUCCINO: Drink.CAPPUCCINO,
}


def next_stage(drink: Drink, stage: Stage) -> Stage:
    stages = RECIPES[drink]
    return stages[stages.index(stage) + 1]


class Resource(StrEnum):
    GRINDER = "grinder"
    BREW_UNIT = "brew_unit"
    BOILER = "boiler"
    PUMP = "pump"
    HOT_WATER_OUTLET = "hot_water_outlet"
    STEAMER = "steamer"


ALL_ACTUATORS = frozenset(Resource)

# R(k). Consumables (beans, water, milk) are covered by the faults that block their actuator.
_ESPRESSO = frozenset({Resource.GRINDER, Resource.BREW_UNIT, Resource.BOILER, Resource.PUMP})
REQUIRED: dict[Drink, frozenset[Resource]] = {
    Drink.ESPRESSO: _ESPRESSO,
    Drink.AMERICANO: _ESPRESSO | {Resource.HOT_WATER_OUTLET},
    Drink.CAPPUCCINO: _ESPRESSO | {Resource.STEAMER},
}


class FaultClass(StrEnum):
    STOP = "stop"  # abort the running drink at once
    FINISH = "finish"  # finish the running drink, block later ones
    PARTIAL = "partial"  # milk_empty during a cappuccino: partial drink


FAULT_CLASS: dict[Event, FaultClass] = {
    Event.OVERHEAT: FaultClass.STOP,
    Event.WATER_EMPTY: FaultClass.STOP,
    Event.FLOW_ERROR: FaultClass.STOP,
    Event.BREW_UNIT_REMOVED: FaultClass.STOP,
    Event.BEANS_EMPTY: FaultClass.STOP,
    Event.BIN_FULL: FaultClass.FINISH,
    Event.TRAY_FULL: FaultClass.FINISH,
    Event.MILK_EMPTY: FaultClass.PARTIAL,
}

# B(f): resources disabled by each fault.
BLOCKED_BY: dict[Event, frozenset[Resource]] = {
    Event.OVERHEAT: ALL_ACTUATORS,
    Event.WATER_EMPTY: frozenset({Resource.PUMP, Resource.BOILER, Resource.STEAMER}),
    Event.FLOW_ERROR: frozenset({Resource.PUMP}),
    Event.BREW_UNIT_REMOVED: frozenset({Resource.GRINDER, Resource.PUMP}),
    Event.BEANS_EMPTY: frozenset({Resource.GRINDER}),
    Event.BIN_FULL: frozenset({Resource.GRINDER}),
    Event.TRAY_FULL: frozenset({Resource.PUMP}),
    Event.MILK_EMPTY: frozenset({Resource.STEAMER}),
}


def blocked_resources(faults: frozenset[Event]) -> frozenset[Resource]:
    """The union of B(f) over the active faults."""
    return frozenset().union(*(BLOCKED_BY[f] for f in faults))
