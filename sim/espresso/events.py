"""Event alphabet: E_obs and E_con.

Names match docs/domain/events.md exactly. Add a new event there first, then here.
"""

from __future__ import annotations

from enum import StrEnum


class Event(StrEnum):
    # E_obs: user
    POWER_ON = "power_on"
    ORDER_ESPRESSO = "order_espresso"
    ORDER_AMERICANO = "order_americano"
    ORDER_CAPPUCCINO = "order_cappuccino"
    CUP_PLACED = "cup_placed"
    CUP_REMOVED = "cup_removed"
    # E_obs: completion
    TEMP_REACHED = "temp_reached"
    GRIND_DONE = "grind_done"
    BREW_DONE = "brew_done"
    STEAM_DONE = "steam_done"
    HOT_WATER_DONE = "hot_water_done"
    RINSE_DONE = "rinse_done"
    MILK_CLEANING_DONE = "milk_cleaning_done"
    DESCALING_DONE = "descaling_done"
    # E_obs: sensor and warning
    COOLED_DOWN = "cooled_down"
    WATER_LOW = "water_low"
    # E_obs: fault
    WATER_EMPTY = "water_empty"
    BEANS_EMPTY = "beans_empty"
    MILK_EMPTY = "milk_empty"
    BIN_FULL = "bin_full"
    TRAY_FULL = "tray_full"
    BREW_UNIT_REMOVED = "brew_unit_removed"
    FLOW_ERROR = "flow_error"
    OVERHEAT = "overheat"
    # E_obs: service
    REFILL_WATER = "refill_water"
    REFILL_BEANS = "refill_beans"
    REFILL_MILK = "refill_milk"
    EMPTY_BIN = "empty_bin"
    EMPTY_TRAY = "empty_tray"
    INSERT_BREW_UNIT = "insert_brew_unit"
    DESCALING_CONFIRMED = "descaling_confirmed"
    CLEAR_FLOW_ERROR = "clear_flow_error"
    # E_con
    HEAT_TO_BREW = "heat_to_brew"
    HEAT_TO_STEAM = "heat_to_steam"
    START_GRIND = "start_grind"
    START_BREW = "start_brew"
    ADD_HOT_WATER = "add_hot_water"
    START_STEAM = "start_steam"
    EJECT_GROUNDS = "eject_grounds"
    START_RINSE = "start_rinse"
    START_MILK_CLEANING = "start_milk_cleaning"
    START_DESCALING = "start_descaling"
    ABORT_DRINK = "abort_drink"
    REJECT_ORDER = "reject_order"


E = Event

ORDERS = frozenset({E.ORDER_ESPRESSO, E.ORDER_AMERICANO, E.ORDER_CAPPUCCINO})
USER = ORDERS | {E.POWER_ON, E.CUP_PLACED, E.CUP_REMOVED}
COMPLETION = frozenset(
    {
        E.TEMP_REACHED,
        E.GRIND_DONE,
        E.BREW_DONE,
        E.STEAM_DONE,
        E.HOT_WATER_DONE,
        E.RINSE_DONE,
        E.MILK_CLEANING_DONE,
        E.DESCALING_DONE,
    }
)
FAULTS = frozenset(
    {
        E.WATER_EMPTY,
        E.BEANS_EMPTY,
        E.MILK_EMPTY,
        E.BIN_FULL,
        E.TRAY_FULL,
        E.BREW_UNIT_REMOVED,
        E.FLOW_ERROR,
        E.OVERHEAT,
    }
)
SERVICE = frozenset(
    {
        E.REFILL_WATER,
        E.REFILL_BEANS,
        E.REFILL_MILK,
        E.EMPTY_BIN,
        E.EMPTY_TRAY,
        E.INSERT_BREW_UNIT,
        E.DESCALING_CONFIRMED,
        E.CLEAR_FLOW_ERROR,
    }
)
E_OBS = USER | COMPLETION | FAULTS | SERVICE | {E.COOLED_DOWN, E.WATER_LOW}
E_CON = frozenset(Event) - E_OBS

# Controllable event -> the completion event that ends it. Missing = instantaneous.
COMPLETED_BY: dict[Event, Event] = {
    E.HEAT_TO_BREW: E.TEMP_REACHED,
    E.HEAT_TO_STEAM: E.TEMP_REACHED,
    E.START_GRIND: E.GRIND_DONE,
    E.START_BREW: E.BREW_DONE,
    E.ADD_HOT_WATER: E.HOT_WATER_DONE,
    E.START_STEAM: E.STEAM_DONE,
    E.START_RINSE: E.RINSE_DONE,
    E.START_MILK_CLEANING: E.MILK_CLEANING_DONE,
    E.START_DESCALING: E.DESCALING_DONE,
}

# Fault -> the event that clears it (ADR 0010).
CLEARED_BY: dict[Event, Event] = {
    E.WATER_EMPTY: E.REFILL_WATER,
    E.BEANS_EMPTY: E.REFILL_BEANS,
    E.MILK_EMPTY: E.REFILL_MILK,
    E.BIN_FULL: E.EMPTY_BIN,
    E.TRAY_FULL: E.EMPTY_TRAY,
    E.BREW_UNIT_REMOVED: E.INSERT_BREW_UNIT,
    E.FLOW_ERROR: E.CLEAR_FLOW_ERROR,
    E.OVERHEAT: E.COOLED_DOWN,
}
