---
status: proposed
date: 2026-10-26
deciders: Bartosz Ksel
---

# 0011. Bounds for analysis and simulation

## Context

`Ng` bounds the grounds counter `g`, so it affects the size of the reachability graph
([Q2](../open-questions.md#q2-bounds)).

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

The simulator takes `Ng` as a parameter.

## Consequences

- Safety and recoverability are proved on the small net. The bound changes how many drinks pass
  before the `bin_full` guard fires, not the structure of the net. The report has to argue that
  this is why the results carry over to the simulation value.
- The reduced nets go in `model/variants/`.
