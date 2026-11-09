---
status: proposed
date: 2026-10-26
deciders: Bartosz Ksel
---

# 0010. Fault classes, blocked resources and fault exits

## Context

Recoverability ([L1](../requirements/properties.md#recoverability)) fails by construction while
`overheat` and `flow_error` have no event that clears them
([Q4](../open-questions.md#q4-faults-without-a-service-event)). The behaviour after a mid-drink
fault ([Q6](../open-questions.md#q6-partial-drinks)) or when the cup is removed during a drink
([Q5](../open-questions.md#q5-cup-removed-mid-drink)) was undefined. `B(f)` was empty, so `EF(s)`
and S6 could not be written.

## Options considered

1. **One rule for all faults**: abort the drink on any fault. Simple, but it breaks L3 (partial
   cappuccino) and wastes drinks that could finish.
2. **Three fault classes**: stop at once, finish the drink, or partial drink. Closer to a real
   machine and needed for L3.
3. **`cup_removed` as a fault**: it would need a service event, and the cup is not a machine
   failure.
4. **`cup_removed` aborts the running drink**: the order is lost, and no extra fault is needed.

## Decision

We choose options 2 and 4.

**Fault classes and `B(f)`:**

| Fault | Class | `B(f)` | Blocks | Cleared by |
|---|---|---|---|---|
| `overheat` | stop | all actuators | all drinks | `cooled_down` (new sensor event) |
| `water_empty` | stop | pump, boiler, steamer | all drinks | `refill_water` |
| `flow_error` | stop | pump | all drinks | `clear_flow_error` (new service event, user checks and confirms) |
| `brew_unit_removed` | stop | grinder, pump | all drinks | `insert_brew_unit` |
| `beans_empty` | stop | grinder | all drinks | `refill_beans` |
| `bin_full` | finish | grinder | all drinks | `empty_bin` (also `g := 0`) |
| `tray_full` | finish | pump | all drinks | `empty_tray` |
| `milk_empty` | partial | steamer | cappuccino | `refill_milk` |

- **stop**: the running operation stops at once and the controller fires `abort_drink`
  (`p := ∅`, a used puck is ejected).
- **finish**: the current drink completes and later drinks are blocked.
- **partial**: during a cappuccino, the espresso part is finished, steaming is skipped or stopped,
  and a partial drink is reported (L3). In any other drink the fault has no immediate effect.
- A fault that does not affect the current drink only blocks future orders (graceful degradation).

**Mode `fault`:** `m = fault` iff the active faults block every drink. If some drink is still
available, `m` returns to `ready` and orders for blocked drinks get `reject_order`. Once the last
blocking fault is cleared, `m := ready`.

**`overheat`** turns the heater off, and `cooled_down` leaves the boiler `cold`.

**`water_low`** is a warning, not a fault in `𝓕`: water becomes `low`, nothing is blocked, and
`refill_water` sets it back to `ok`.

**`cup_removed`** while the pump or the steamer is running triggers `abort_drink`. Before
brewing, removing the cup only makes the order wait at the `brewing` stage
([ADR 0009](0009-fix-recipe-stages-and-completion-events.md)).

## Consequences

- Every fault in `𝓕` now has a clearing event, so L1 can hold.
- Two new events: `cooled_down` (sensor) and `clear_flow_error` (service).
- `B(f)` gives the inhibitor arcs of the net and the availability rule in the simulator.
- [Events](../domain/events.md), [drinks and resources](../domain/drinks-and-resources.md) and
  [state](../domain/state.md) are updated to match.
