# State

Source: project proposal, Section 2.1.

The state is a tuple `s = (m, r, c, d, F, p) ∈ S`.

| Symbol | Meaning | Domain |
|---|---|---|
| `m` | Operating mode | `off`, `heating`, `ready`, `preparing`, `fault`, `service`, `descaling` |
| `r` | Resources | grinder, pump, steamer ∈ {`idle`, `busy`}; boiler ∈ {`cold`, `brew`, `steam`}; brew unit ∈ {`empty`, `loaded`, `used`}; cup ∈ {`absent`, `present`} |
| `c` | Consumables | water ∈ {`ok`, `low`, `empty`}; beans, milk ∈ {`ok`, `empty`}; grounds counter `g ∈ {0..Ng}`; drip tray ∈ {`ok`, `full`} |
| `d` | Descaling counter (drinks since the last descaling) | `{0..Nover}`, warning threshold `Ndue < Nover` |
| `F` | Set of active faults (several can be active at once) | `F ⊆ 𝓕` |
| `p` | Current order: drink and recipe stage | drink × stage, or `∅`. Stages in [ADR 0009](../decisions/0009-fix-recipe-stages-and-completion-events.md) |

## Initial state `s0`

Mode `off`, boiler `cold`, all resources `idle`, consumables full, `g = d = 0`, `F = ∅`, `p = ∅`.

## Home state `sh`

The machine runs continuously, so instead of a final state we use the **home state**: mode
`ready`, no order, no faults. Recoverability ([L1](../requirements/properties.md#recoverability))
means `sh` is a home marking of the net.

## Mode `fault`

`m = fault` iff the active faults block every drink. If some drink is still available, the
machine stays `ready` and orders for blocked drinks are rejected. See [ADR 0010](../decisions/0010-fault-classes-blocked-resources-and-fault-exits.md).

## Bounds

Analysis uses `Ng = 3, Ndue = 2, Nover = 3`. The simulator defaults to `Ng = 10, Ndue = 150,
Nover = 200`. See [ADR 0011](../decisions/0011-bounds-for-analysis-and-simulation.md).

## Recipe stages

| Drink | Stages |
|---|---|
| Espresso | `heating → grinding → brewing → done` |
| Americano | `heating → grinding → brewing → hot_water → done` |
| Cappuccino | `heating → grinding → brewing → steam_heating → steaming → done` |

See [ADR 0009](../decisions/0009-fix-recipe-stages-and-completion-events.md).

## Not yet defined

- Whether `m` stays a single variable or is split into places in the Petri net (the net may make
  some modes implicit).
