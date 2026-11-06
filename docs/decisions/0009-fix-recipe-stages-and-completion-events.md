---
status: proposed
date: 2026-10-26
deciders: Bartosz Ksel
---

# 0009. Fix recipe stages and completion events

## Context

The order component `p` needs a stage for every drink before the order part of the net can be
drawn ([Q1](../open-questions.md#q1-recipe-stages)). Several controllable events had no completion
event, so their operations would either never end or have to be instantaneous
([Q3](../open-questions.md#q3-missing-completion-events)).

## Options considered

1. **Cappuccino in either order** (brew then steam, or steam then brew), left to the policy as
   conflict C1: more freedom, but steaming first leaves hot milk waiting and does not match how a
   cappuccino is made.
2. **Cappuccino in a fixed order, coffee first and milk on top**: matches the real drink and gives
   a smaller net.
3. **Instantaneous operations** for hot water: a smaller net, while the simulator does not
  measure its duration separately.
4. **A completion event for every modeled operation that takes time**: every modeled operation
  remains visible in time.

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
- `brewing` (`start_brew` … `brew_done`) uses the fixed cup resource (S2).
- `steam_heating` (`heat_to_steam` … `temp_reached`) and `steaming` (`start_steam` …
  `steam_done`) always come **after** brewing: coffee first, milk on top.
- `done`: `eject_grounds` moves the puck to the grounds container (`g := g + 1`), then `p := ∅`
  and `m := ready`.

`hot_water_done` completes the modeled hot-water operation. `eject_grounds` is instantaneous.

## Consequences

- The boiler keeps its current temperature after a drink. A water fault also leaves the boiler
  temperature unchanged.
- [Events](../domain/events.md), [state](../domain/state.md) and
  [properties](../requirements/properties.md) are updated to match.
