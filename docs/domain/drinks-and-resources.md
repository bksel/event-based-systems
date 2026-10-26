# Drinks and resources

Source: project proposal, Sections 2 and 2.3.

## Availability rule

Each drink `k` has a set of required resources `R(k)`. Each fault `f ∈ 𝓕` disables a set of
resources `B(f)`. Drink `k` is **available** in state `s` iff

```
R(k) ∩ ⋃_{f ∈ F} B(f) = ∅   and   d < Nover
```

An order for `k` is in `EF(s)` iff `m = ready` and `k` is available. Otherwise the controller
answers with `reject_order`.

## `R(k)`: required resources

The first three rows come from the proposal. Everything marked *(inferred)* still needs the team's
confirmation.

| Resource | Espresso | Americano | Cappuccino |
|---|:-:|:-:|:-:|
| grinder | ✓ | ✓ | ✓ |
| brew unit | ✓ | ✓ | ✓ |
| boiler at `brew` | ✓ | ✓ | ✓ |
| pump / water *(inferred)* | ✓ | ✓ | ✓ |
| beans *(inferred)* | ✓ | ✓ | ✓ |
| cup *(inferred)* | ✓ | ✓ | ✓ |
| hot water outlet | | ✓ | |
| boiler at `steam` | | | ✓ |
| milk pump + steamer | | | ✓ |
| milk *(inferred)* | | | ✓ |

## `B(f)`: resources disabled by each fault

Decided in [ADR 0010](../decisions/0010-fault-classes-blocked-resources-and-fault-exits.md). `water_low` is a warning, not a fault, and blocks nothing.

| Fault | Class | `B(f)` | Blocks |
|---|---|---|---|
| `overheat` | stop | all actuators ([S5](../requirements/properties.md#safety)) | all drinks |
| `water_empty` | stop | pump, boiler, steamer | all drinks |
| `flow_error` | stop | pump | all drinks |
| `brew_unit_removed` | stop | grinder, pump | all drinks |
| `beans_empty` | stop | grinder | all drinks |
| `bin_full` | finish | grinder ([S4](../requirements/properties.md#safety)) | all drinks |
| `tray_full` | finish | pump | all drinks |
| `milk_empty` | partial | steamer | cappuccino |

## Fault during a drink

The class of the fault decides what happens to the drink in preparation:

- **stop**: the running operation stops at once and the controller fires `abort_drink`.
- **finish**: the current drink completes, and later drinks are blocked.
- **partial**: `milk_empty` during a cappuccino. The controller finishes the espresso part, skips
  or stops steaming, reports a partial drink, and does not block the machine (L3).

A fault that does not affect the current drink only blocks future orders. The mode becomes
`fault` only if no drink is available any more. Removing the cup while the pump or the steamer
runs also aborts the drink. See [ADR 0010](../decisions/0010-fault-classes-blocked-resources-and-fault-exits.md).
