---
status: proposed
date: 2026-10-26
deciders: Bartosz Ksel
---

# 0009. Fix recipe stages and completion events

## Context

The order component `p` needs a stage for every drink before the order part of the net can be
drawn ([Q1](../open-questions.md#q1-recipe-stages)). Five controllable events had no completion
event, so their operations would either never end or have to be instantaneous
([Q3](../open-questions.md#q3-missing-completion-events)).

## Options considered

1. **Cappuccino in either order** (brew then steam, or steam then brew), left to the policy as
   conflict C1: more freedom, but steaming first leaves hot milk waiting and does not match how a
   cappuccino is made.
2. **Cappuccino in a fixed order, coffee first and milk on top**: matches the real drink and gives
   a smaller net.
3. **Instantaneous operations** for rinsing, cleaning, hot water and descaling: a smaller net, but
   the simulator cannot measure their duration (E1, E3).
4. **A completion event for every operation that takes time**: more events, but every operation
   is visible in time.

## Decision

We choose options 2 and 4.

Recipe stages (the stage part of `p`):

| Drink | Stages |
|---|---|
| Espresso | `heating → grinding → brewing → done` |
| Americano | `heating → grinding → brewing → hot_water → done` |
| Cappuccino | `heating → grinding → brewing → steam_heating → steaming → done` |

- `heating` (`heat_to_brew` … `temp_reached`) is skipped if the boiler is already at `brew`.
  Grinding may run during heating. That choice is conflict C2.
- `brewing` (`start_brew` … `brew_done`) needs a cup (S2). If there is no cup, the order waits at
  this stage until `cup_placed`.
- `steam_heating` (`heat_to_steam` … `temp_reached`) and `steaming` (`start_steam` …
  `steam_done`) always come **after** brewing: coffee first, milk on top.
- `done`: `eject_grounds` moves the puck to the grounds container (`g := g + 1`), then `p := ∅`
  and `m := ready`.

New completion events in `E_obs`: `hot_water_done`, `rinse_done`, `milk_cleaning_done`,
`descaling_done`. `eject_grounds` is instantaneous.

Descaling runs in this order: `d ≥ Ndue` → the machine asks for descaling → the user adds the
agent and confirms (`descaling_confirmed`) → `start_descaling` → `descaling_done` → `d := 0`.

## Consequences

- Conflict C1 no longer exists as "brew or steam first". It is reformulated as the boiler
  temperature after a cappuccino: switch back to `brew` right away (faster next espresso, E1) or
  stay at `steam` until a drink needs `brew` (fewer switches if milk drinks follow, E2). The
  proposal described C1 the old way, so the M2 report must mention the change.
- `d` is incremented at `brew_done`, so partial drinks count towards descaling.
- [Events](../domain/events.md), [state](../domain/state.md) and
  [properties](../requirements/properties.md) are updated to match.
