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

**To be defined by the team (T3).** The proposal only gives examples:

- `milk_empty` blocks cappuccino but not espresso.
- `bin_full` blocks grinding but lets a drink that is already brewing finish.
- `overheat`: no actuator may run (see [S4](../requirements/properties.md#safety)).

| Fault | `B(f)` |
|---|---|
| `water_low` | |
| `water_empty` | |
| `beans_empty` | |
| `milk_empty` | |
| `bin_full` | |
| `tray_full` | |
| `brew_unit_removed` | |
| `flow_error` | |
| `overheat` | |

## Fault during a drink

If a fault affects the drink in preparation, the mode becomes `fault` and the running operation
stops. Otherwise the mode does not change. Special case from the proposal: `milk_empty` during a
cappuccino. The controller finishes the espresso part, reports a partial drink, and must not block
the machine. See [Q6](../open-questions.md#q6-partial-drinks) for the general rule.
