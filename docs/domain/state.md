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
| `p` | Current order: drink and recipe stage | drink × stage, or `∅` |

## Initial state `s0`

Mode `off`, boiler `cold`, all resources `idle`, consumables full, `g = d = 0`, `F = ∅`, `p = ∅`.

## Home state `sh`

The machine runs continuously, so instead of a final state we use the **home state**: mode
`ready`, no order, no faults. Recoverability ([L1](../requirements/properties.md#recoverability))
means `sh` is a home marking of the net.

## Not yet defined

- The recipe stages in `p` for each drink. See [Q1](../open-questions.md#q1-recipe-stages).
- The values of `Ng`, `Ndue`, `Nover`. See [Q2](../open-questions.md#q2-bounds).
- Whether `m` stays a single variable or is split into places in the Petri net (the net may make
  some modes implicit).
