---
status: proposed
date: 2026-11-09
deciders: Krzysztof Pogoda
---

# 0013. Reduce the model scope

## Context

While drawing the Petri net (T3, branch `feature/petri-net`), KP built a smaller model than the
one agreed in ADRs [0004](0004-one-drink-at-a-time.md),
[0009](0009-fix-recipe-stages-and-completion-events.md),
[0010](0010-fault-classes-blocked-resources-and-fault-exits.md) and
[0011](0011-bounds-for-analysis-and-simulation.md), and edited those ADRs and the KB to match.
Those ADRs were agreed with the supervisor, so they were restored, and the reduction is recorded
here as a proposal. The full edited texts are in commits `57dc233` and `aa9c925`.

KP's reason: the full scope could not be modelled as a net. This has not been verified yet. BK
will check whether the agreed scope can be modelled before the team decides.

## Options considered

1. **Keep the agreed scope**: the model matches the proposal and the ADRs above, and the
   simulator already implements most of it. The net is larger and takes more work to draw and
   analyse.
2. **Reduce the scope as below**: a smaller net that is easier to analyse. Several requirements
   and both C3 and C4 disappear, and the M2 report has to explain why it deviates from the
   proposal.

## Proposed changes

- **Descaling removed**: the counter `d`, `Ndue`, `Nover`, `descaling_confirmed`,
  `start_descaling`, `descaling_done`, the mode `descaling` and conflict C3.
- **Rinsing and milk cleaning removed**: `start_rinse`, `rinse_done`, `start_milk_cleaning`,
  `milk_cleaning_done` and conflict C4.
- **Fewer faults**: only `water_empty`, `beans_empty`, `milk_empty` and `bin_full`, each cleared by
  its refill or `empty_bin`. Removed: `overheat` and `cooled_down`, `flow_error` and
  `clear_flow_error`, `tray_full` and `empty_tray`, `brew_unit_removed` and `insert_brew_unit`, and
  the warning `water_low`.
- **Fault classes replaced**: instead of stop / finish / partial, a fault makes the operation that
  uses the missing resource fail. `abort_drink`, partial drinks and graceful degradation (L3 as
  written) are removed.
- **Fixed cup and brew unit**: `cup_placed` and `cup_removed` are removed. The cup is `empty` or
  `full` and is emptied by the recipe flow before the next order.
- **No order rejection**: `reject_order` is removed. A single `drink_done` permit token blocks a
  second order until the current drink completes, and resources are checked when each operation
  starts, not when the order arrives.
- **No `temp_reached`**: the boiler keeps its temperature after a drink and after a water fault.
- **Bounds**: 5 grounds-bin slots and 4 bean tokens in the net, a bin capacity of 10 in the
  simulator.
- **Requirements reworded**:
  - S5 becomes "pump, grinder and steamer run only when their resource permit is available".
  - S6 becomes "a second drink cannot be ordered while one is active".
  - L3 becomes "every modelled fault has a recovery path".
- **State**: `s = (m, r, c, F, p)`, without `d`.

## Decision

Open, until BK has verified whether the agreed scope can be modelled. Then the team decides,
and the decision is checked with the supervisor. See
[Q9](../open-questions.md#q9-reduced-model-scope).

## Consequences

If accepted:

- ADRs 0009, 0010 and 0011 are superseded in the affected parts, and the KB (events, state,
  drinks and resources, properties, glossary) is updated to match.
- The simulator drops the removed events and behaviour, and its tests are updated
  (`tests/test_sim_events.py` checks the code against the event catalogue).
- The M2 report must state and justify the deviation from the proposal.

If rejected, the net is extended to the agreed scope.
