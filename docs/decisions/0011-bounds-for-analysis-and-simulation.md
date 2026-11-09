---
status: proposed
date: 2026-10-26
deciders: Bartosz Ksel
---

# 0011. Bounds for analysis and simulation

## Context

`Ng`, `Ndue` and `Nover` bound the counters `g` and `d`, so they set the size of the reachability
graph ([Q2](../open-questions.md#q2-bounds)). Realistic values (hundreds of drinks between
descalings) would make the graph far too large to analyse.

## Options considered

1. **The same values everywhere**: one parameter set, but either the analysis explodes or the
   simulation is unrealistic.
2. **Small values for analysis, realistic ones for simulation**: the counter structure is the
   same and only the bounds differ.

## Decision

We choose option 2.

| Bound | Analysis (net) | Simulation (default) |
|---|---:|---:|
| `Ng` | 3 | 10 |
| `Ndue` | 2 | 150 |
| `Nover` | 3 | 200 |

The simulator takes the bounds as parameters.

## Consequences

- Safety and recoverability are proved on the small net. The bounds change only how many drinks
  pass before the `bin_full` and descaling guards fire, not the structure of the net. The report
  has to argue that this is why the results carry over to the simulation values.
- The reduced nets go in `model/variants/`.
