---
status: proposed
date: 2026-10-26
deciders: Bartosz Ksel
---

# 0010. Modeled resource faults

## Context

The model needs explicit transitions for the four resource faults it represents: water, beans,
milk, and grounds-bin capacity. The brew unit and cup are fixed resources, and tray mechanics are
outside the model.

## Options considered

1. **Model only resource faults used by the net**: keep water, beans, milk, and bin faults.
2. **Keep the brew unit and cup fixed**: no removal or insertion events are modeled.

## Decision

We choose options 1 and 2.

**Fault classes and `B(f)`:**

| Fault | Class | `B(f)` | Blocks | Cleared by |
|---|---|---|---|---|
| `water_empty` | operation failure | pump, boiler, steamer | affected operation | `refill_water` |
| `beans_empty` | operation failure | grinder | grinding | `refill_beans` |
| `bin_full` | finish | grinder | grinding/ejection | `empty_bin` |
| `milk_empty` | operation failure | steamer | steaming | `refill_milk` |

Fault transitions affect the operation that uses the unavailable resource. A water fault does not
change the boiler temperature. The bin fault is cleared by emptying the bin, which restores five
bin-space tokens. The cup and brew unit remain in the model and are emptied through the normal
recipe flow.

## Consequences

- Each modeled fault has a clearing event.
- Resource checks are represented by ordinary and inhibitor arcs at the operation that uses them.
- [Events](../domain/events.md), [drinks and resources](../domain/drinks-and-resources.md) and
  [state](../domain/state.md) are updated to match.
