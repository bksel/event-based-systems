---
status: proposed
date: 2026-10-26
deciders: Bartosz Ksel
---

# 0011. Bounds for analysis and simulation

## Context

The grounds-bin capacity bounds the counter `g`, so it affects the size of the reachability graph
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
| Grounds/bin capacity | 5 slots in the net | 10 (simulator default) |

The simulator takes its bin capacity as a parameter.

## Consequences

- The bound changes how many drinks pass before the `bin_full` guard fires, not the structure of
   the net. The report has to account for the different net and simulator capacities.
- The reduced nets go in `model/variants/`.
