# Drinks and resources

Source: project proposal, Sections 2 and 2.3.

## Availability rule

Each drink `k` has a set of required resources `R(k)`. The model checks the resources at the
operation that uses them; it does not reject an order based on the complete resource set.

```
R(k) ∩ ⋃_{f ∈ F} B(f) = ∅
```

An order can be accepted only when the machine is powered on, the brew unit is empty, and no
other order is active. The `drink_done` permit place enforces the one-drink-at-a-time rule.

## `R(k)`: required resources

The table lists the resources represented by the model.

| Resource | Espresso | Americano | Cappuccino |
|---|:-:|:-:|:-:|
| grinder | ✓ | ✓ | ✓ |
| brew unit | ✓ | ✓ | ✓ |
| boiler at `brew` | ✓ | ✓ | ✓ |
| pump / water | ✓ | ✓ | ✓ |
| beans | ✓ | ✓ | ✓ |
| cup | ✓ | ✓ | ✓ |
| hot water outlet | | ✓ | |
| boiler at `steam` | | | ✓ |
| milk pump + steamer | | | ✓ |
| milk | | | ✓ |

## `B(f)`: resources disabled by each fault

Decided in [ADR 0010](../decisions/0010-fault-classes-blocked-resources-and-fault-exits.md).

| Fault | Class | `B(f)` | Blocks |
|---|---|---|---|
| `water_empty` | operation failure | pump, boiler, steamer | all affected operations |
| `beans_empty` | operation failure | grinder | grinding |
| `bin_full` | finish | grinder ([S4](../requirements/properties.md#safety)) | grinding/ejection |
| `milk_empty` | operation failure | steamer | steaming |

## Fault during a drink

The model represents water, bean, milk, and bin faults through explicit failure and refill
transitions. The brew unit and cup cannot be removed. The cup is emptied before the next order;
the brew unit is returned to its empty state by grounds ejection. There is no tray mechanism.
