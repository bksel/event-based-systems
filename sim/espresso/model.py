"""Semantics of the machine: EF(s), safe(s, e) and next_state(s, e).

This is the only module that decides how the state changes. Everything else (controller,
engine, GUI) chooses or schedules events and calls next_state.

Not implemented yet (follow-up issues): stop- and partial-class faults during a drink,
cup_removed while the pump or steamer runs, abort_drink, rinsing, milk cleaning and descaling.
Until then these events are simply not in EF(s) in those situations.
"""

from __future__ import annotations

from dataclasses import replace

from espresso.drinks import (
    FAULT_CLASS,
    ORDER_DRINK,
    REQUIRED,
    Drink,
    FaultClass,
    Resource,
    Stage,
    blocked_resources,
    next_stage,
)
from espresso.events import CLEARED_BY, COMPLETION, FAULTS, ORDERS, SERVICE, Event
from espresso.state import (
    Actuator,
    Boiler,
    BrewUnit,
    Cup,
    Mode,
    Order,
    State,
    Supply,
    Tray,
    Water,
)

E = Event
IDLE, BUSY = Actuator.IDLE, Actuator.BUSY

FAULT_OF_SERVICE = {service: fault for fault, service in CLEARED_BY.items()}

# Resources each controllable actuation uses, for B(f) and the safety guards.
USES: dict[Event, frozenset[Resource]] = {
    E.HEAT_TO_BREW: frozenset({Resource.BOILER}),
    E.HEAT_TO_STEAM: frozenset({Resource.BOILER}),
    E.START_GRIND: frozenset({Resource.GRINDER}),
    E.START_BREW: frozenset({Resource.PUMP, Resource.BREW_UNIT}),
    E.ADD_HOT_WATER: frozenset({Resource.PUMP, Resource.HOT_WATER_OUTLET}),
    E.START_STEAM: frozenset({Resource.STEAMER}),
}


class InfeasibleEvent(ValueError):
    """next_state was called with an event that is not in EF(s)."""


class InvariantViolation(AssertionError):
    """A reachable state breaks a safety property or a consistency rule."""


def blocked_by_faults(s: State, drink: Drink) -> bool:
    return bool(REQUIRED[drink] & blocked_resources(s.faults))


def available(s: State, drink: Drink) -> bool:
    """Availability rule from docs/domain/drinks-and-resources.md."""
    return not blocked_by_faults(s, drink) and s.descaling < s.bounds.nover


def is_idle(s: State) -> bool:
    """Switched on, no drink in preparation."""
    return s.mode in (Mode.READY, Mode.FAULT) and s.order is None


def expected_completions(s: State) -> frozenset[Event]:
    """Completion events of the operations running in s."""
    r = s.resources
    out = set()
    if r.heating_to is not None:
        out.add(E.TEMP_REACHED)
    if r.grinder is BUSY:
        out.add(E.GRIND_DONE)
    if r.pump is BUSY:
        out.add(E.BREW_DONE if s.order and s.order.stage is Stage.BREWING else E.HOT_WATER_DONE)
    if r.steamer is BUSY:
        out.add(E.STEAM_DONE)
    return frozenset(out)


def feasible(s: State, e: Event) -> bool:
    """e ∈ EF(s)."""
    if s.mode is Mode.OFF:
        return e is E.POWER_ON
    r, c = s.resources, s.consumables
    stage = s.order.stage if s.order else None

    if e in ORDERS:
        return is_idle(s)
    if e in COMPLETION:
        return e in expected_completions(s)
    if e in FAULTS:
        # TODO(MS): stop and partial faults during a drink (ADR 0010).
        return e not in s.faults and (FAULT_CLASS[e] is FaultClass.FINISH or is_idle(s))
    if e is E.REFILL_WATER:
        return c.water is not Water.OK
    if e is E.DESCALING_CONFIRMED:
        return False  # TODO(MS): descaling
    if e in SERVICE:
        return FAULT_OF_SERVICE[e] in s.faults

    match e:
        case E.CUP_PLACED:
            return r.cup is Cup.ABSENT
        case E.CUP_REMOVED:
            # TODO(MS): removing the cup while pumping or steaming aborts the drink.
            return r.cup is Cup.PRESENT and r.pump is IDLE and r.steamer is IDLE
        case E.WATER_LOW:
            return c.water is Water.OK
        case E.COOLED_DOWN:
            return E.OVERHEAT in s.faults
        case E.HEAT_TO_BREW:
            return (
                r.heating_to is None
                and r.boiler is not Boiler.BREW
                and (
                    s.mode is Mode.HEATING
                    or stage is Stage.HEATING
                    or (is_idle(s) and r.boiler is Boiler.STEAM)  # C1: back to brew
                )
            )
        case E.HEAT_TO_STEAM:
            return (
                r.heating_to is None
                and r.boiler is not Boiler.STEAM
                and stage is Stage.STEAM_HEATING
            )
        case E.START_GRIND:
            # Allowed during heating too: grinding in parallel is conflict C2.
            return (
                stage in (Stage.HEATING, Stage.GRINDING)
                and r.grinder is IDLE
                and r.brew_unit is BrewUnit.EMPTY
            )
        case E.START_BREW:
            return (
                stage is Stage.BREWING
                and r.pump is IDLE
                and r.brew_unit is BrewUnit.LOADED
                and r.boiler is Boiler.BREW
            )
        case E.ADD_HOT_WATER:
            return stage is Stage.HOT_WATER and r.pump is IDLE
        case E.START_STEAM:
            return stage is Stage.STEAMING and r.steamer is IDLE
        case E.EJECT_GROUNDS:
            return stage is Stage.DONE and r.brew_unit is BrewUnit.USED and c.grounds < s.bounds.ng
        case E.REJECT_ORDER:
            return stage is Stage.REJECTED
        case _:
            # TODO(MS): abort_drink, rinsing, milk cleaning, descaling.
            return False


def enabled(s: State) -> frozenset[Event]:
    """EF(s)."""
    return frozenset(e for e in Event if feasible(s, e))


def safe(s: State, e: Event) -> bool:
    """safe(s, e): the actuator guards S1–S6 on top of EF(s)."""
    uses = USES.get(e)
    if not uses:
        return True
    r, c = s.resources, s.consumables
    faults = s.faults
    if s.order is not None:
        # Finish-class faults let the drink in preparation complete (ADR 0010); they only
        # block later drinks. The physical guards below (S1–S4) still apply.
        faults = frozenset(f for f in faults if FAULT_CLASS[f] is not FaultClass.FINISH)
    if uses & blocked_resources(faults):  # B(f), including S5 (overheat blocks everything)
        return False
    if Resource.PUMP in uses and (c.water is Water.EMPTY or r.cup is Cup.ABSENT):  # S1, S2
        return False
    if Resource.STEAMER in uses and (c.milk is Supply.EMPTY or r.cup is Cup.ABSENT):  # S3
        return False
    return not (Resource.GRINDER in uses and c.grounds >= s.bounds.ng)  # S4


def next_state(s: State, e: Event) -> State:
    """The state after e. Raises InfeasibleEvent if e ∉ EF(s)."""
    if not feasible(s, e):
        raise InfeasibleEvent(f"{e} is not feasible in mode {s.mode} with order {s.order}")
    return _settle_mode(_apply(s, e))


def _apply(s: State, e: Event) -> State:
    r, c, p = s.resources, s.consumables, s.order

    def res(**changes) -> State:
        return replace(s, resources=replace(r, **changes))

    def stage(new: Stage) -> Order:
        assert p is not None
        return replace(p, stage=new)

    if e in ORDERS:
        drink = ORDER_DRINK[e]
        if not available(s, drink):
            return replace(s, order=Order(drink, Stage.REJECTED))
        brew_ready = r.boiler is Boiler.BREW and r.heating_to is None
        first = Stage.GRINDING if brew_ready else Stage.HEATING
        return replace(s, mode=Mode.PREPARING, order=Order(drink, first))

    if e in FAULTS:
        s = replace(s, faults=s.faults | {e})
        if e is E.WATER_EMPTY:
            return replace(s, consumables=replace(c, water=Water.EMPTY))
        if e is E.BEANS_EMPTY:
            return replace(s, consumables=replace(c, beans=Supply.EMPTY))
        if e is E.MILK_EMPTY:
            return replace(s, consumables=replace(c, milk=Supply.EMPTY))
        if e is E.TRAY_FULL:
            return replace(s, consumables=replace(c, tray=Tray.FULL))
        if e is E.OVERHEAT:
            return replace(s, resources=replace(r, heating_to=None))  # heater off
        return s

    if e in SERVICE or e is E.COOLED_DOWN:
        s = replace(s, faults=s.faults - {FAULT_OF_SERVICE[e]})
        if e is E.REFILL_WATER:
            return replace(s, consumables=replace(c, water=Water.OK))
        if e is E.REFILL_BEANS:
            return replace(s, consumables=replace(c, beans=Supply.OK))
        if e is E.REFILL_MILK:
            return replace(s, consumables=replace(c, milk=Supply.OK))
        if e is E.EMPTY_BIN:
            return replace(s, consumables=replace(c, grounds=0))
        if e is E.EMPTY_TRAY:
            return replace(s, consumables=replace(c, tray=Tray.OK))
        if e is E.COOLED_DOWN:
            return replace(s, resources=replace(r, boiler=Boiler.COLD))
        return s

    match e:
        case E.POWER_ON:
            return replace(s, mode=Mode.HEATING)
        case E.CUP_PLACED:
            return res(cup=Cup.PRESENT)
        case E.CUP_REMOVED:
            return res(cup=Cup.ABSENT)
        case E.WATER_LOW:
            return replace(s, consumables=replace(c, water=Water.LOW))
        case E.HEAT_TO_BREW:
            return res(heating_to=Boiler.BREW)
        case E.HEAT_TO_STEAM:
            return res(heating_to=Boiler.STEAM)
        case E.TEMP_REACHED:
            s = res(boiler=r.heating_to, heating_to=None)
            if s.mode is Mode.HEATING:
                return replace(s, mode=Mode.READY)
            if p is not None and p.stage is Stage.HEATING:
                loaded = r.brew_unit is BrewUnit.LOADED
                return replace(s, order=stage(Stage.BREWING if loaded else Stage.GRINDING))
            if p is not None and p.stage is Stage.STEAM_HEATING:
                return replace(s, order=stage(Stage.STEAMING))
            return s
        case E.START_GRIND:
            return res(grinder=BUSY)
        case E.GRIND_DONE:
            s = res(grinder=IDLE, brew_unit=BrewUnit.LOADED)
            if p is not None and p.stage is Stage.GRINDING:
                return replace(s, order=stage(Stage.BREWING))
            return s
        case E.START_BREW | E.ADD_HOT_WATER:
            return res(pump=BUSY)
        case E.BREW_DONE:
            # d counts at brew_done, so partial drinks count too (ADR 0009).
            s = res(pump=IDLE, brew_unit=BrewUnit.USED)
            assert p is not None
            return replace(s, descaling=s.descaling + 1, order=stage(next_stage(p.drink, p.stage)))
        case E.HOT_WATER_DONE:
            return replace(res(pump=IDLE), order=stage(Stage.DONE))
        case E.START_STEAM:
            return res(steamer=BUSY)
        case E.STEAM_DONE:
            return replace(res(steamer=IDLE), order=stage(Stage.DONE))
        case E.EJECT_GROUNDS:
            s = res(brew_unit=BrewUnit.EMPTY)
            return replace(
                s,
                consumables=replace(c, grounds=c.grounds + 1),
                order=None,
                mode=Mode.READY,
            )
        case E.REJECT_ORDER:
            return replace(s, order=None)
    raise AssertionError(f"feasible but not implemented: {e}")


def _settle_mode(s: State) -> State:
    """When idle, m = fault iff the active faults block every drink (ADR 0010)."""
    if not is_idle(s):
        return s
    all_blocked = all(blocked_by_faults(s, k) for k in Drink)
    return replace(s, mode=Mode.FAULT if all_blocked else Mode.READY)


def check_invariants(s: State) -> None:
    """Raise InvariantViolation if s breaks S1–S5 or a consistency rule.

    A stop-class fault must therefore switch the blocked actuators off in the same transition,
    not wait for abort_drink.
    """
    r, c = s.resources, s.consumables
    problems = []
    if r.pump is BUSY and c.water is Water.EMPTY:
        problems.append("S1: pump runs without water")
    if r.pump is BUSY and r.cup is Cup.ABSENT:
        problems.append("S2: pump runs without a cup")
    if r.steamer is BUSY and c.milk is Supply.EMPTY:
        problems.append("S3: steamer runs without milk")
    if r.grinder is BUSY and c.grounds >= s.bounds.ng:
        problems.append("S4: grinder runs with a full grounds container")
    running = BUSY in (r.grinder, r.pump, r.steamer) or r.heating_to is not None
    if E.OVERHEAT in s.faults and running:
        problems.append("S5: actuator runs during overheat")
    if not 0 <= c.grounds <= s.bounds.ng or not 0 <= s.descaling <= s.bounds.nover:
        problems.append("counter out of bounds")
    if is_idle(s):
        all_blocked = all(blocked_by_faults(s, k) for k in Drink)
        if (s.mode is Mode.FAULT) != all_blocked:
            problems.append("m = fault must hold iff the faults block every drink")
    if problems:
        raise InvariantViolation("; ".join(problems))
