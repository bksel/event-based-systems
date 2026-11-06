# State

Source: project proposal, Section 2.1.

The state is a tuple `s = (m, r, c, F, p) ∈ S`.

| Symbol | Meaning | Domain |
|---|---|---|
| `m` | Operating mode | `off`, `heating`, `ready`, `preparing`, `fault`, `service` |
| `r` | Resources | grinder, pump, steamer ∈ {`idle`, `busy`}; boiler ∈ {`cold`, `brew`, `steam`}; brew unit ∈ {`empty`, `loaded`, `used`}; cup ∈ {`empty`, `full`} |
| `c` | Consumables | water, milk ∈ {`ok`, `empty`}; beans have four availability tokens; grounds capacity is bounded; there is no drip-tray state |
| `F` | Modeled faults | water empty, beans empty, milk empty, bin full |
| `p` | Current order: drink and recipe stage | drink × stage, or `∅`. Stages in [ADR 0009](../decisions/0009-fix-recipe-stages-and-completion-events.md) |

## Initial state `s0`

Mode `off`, boiler temperature is established by `power_on`, all resources `idle`, water and milk
available, four bean-availability tokens, empty grounds bin, `F = ∅`, `p = ∅`. A water fault does
not change the boiler temperature.

## Home state `sh`

The machine runs continuously, so instead of a final state we use the **home state**: powered on,
no order, empty brew unit and cup, and no active modeled fault.

## Bounds

The model uses four bean-availability tokens and five grounds-bin slots. See
[ADR 0011](../decisions/0011-bounds-for-analysis-and-simulation.md).

## Recipe stages

| Drink | Stages |
|---|---|
| Espresso | `heating → grinding → brewing → done` |
| Americano | `heating → grinding → brewing → hot_water → done` |
| Cappuccino | `heating → grinding → brewing → steam_heating → steaming → done` |

See [ADR 0009](../decisions/0009-fix-recipe-stages-and-completion-events.md).

The heating target says whether heating has started and to which temperature. It is set by
`heat_to_brew` / `heat_to_steam` and cleared by `temp_reached` or `overheat`
([ADR 0012](../decisions/0012-simulator-architecture.md)).

## Not yet defined

- Whether `m` stays a single variable or is split into places in the Petri net (the net may make
  some modes implicit).
