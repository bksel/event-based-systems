---
status: accepted
date: 2026-11-26
deciders: Bartosz Ksel
---

# 0014. Align the simulator with the reduced net

## Context

[ADR 0013](0013-reduce-the-model-scope.md) reduced the scope to what the Petri net models, but
the simulator still implements the earlier scope. The
[scope alignment plan](../project/scope-alignment-plan.md) lists 15 differences between the two,
questions about the net (the
[net's known issues](../../model/README.md#known-issues-open) N4–N7) and the decisions D1–D7 needed to resolve them.
[Q11](../open-questions.md#q11-policies-to-compare-in-the-reduced-scope) asked which policies
to compare once C3 and C4 were gone. M2 is due on 01.12.2026.

## Options considered

1. **Keep two vocabularies and a mapping table** between the net and the simulator: no changes
   to the net, but every replay, test and report needs the mapping.
2. **One vocabulary, with the simulator following the net**, plus three new events so that
   both can describe the same runs. The net has to be edited and verified again.

## Decision

We choose option 2, with these decisions:

- **D1. One vocabulary.** Each transition of the net is labelled with its event from the
  [event catalogue](../domain/events.md). Its name is the label with the prefix `CE__`
  (controllable) or `OE__` (observable, uncontrollable), and the catalogue decides which (this
  fixes N5).
- **D2. Modes.** `m ∈ {off, ready, preparing}`. Faults are shown only in `F`. `power_on` leaves
  the boiler `cold`, and the boiler heats only for an order.
- **D3. New events.** `drink_done` (completion, before `eject_grounds`), `empty_cup`
  (controllable, the cup is `empty` or `full`) and `hot_water_done` (completion, also added to
  the net). `cup_placed` and `cup_removed` are removed.
- **D4. Failures.** The grind fail and restart transitions are removed: beans are taken when
  grinding starts, so a grind cannot run out halfway (this answers N4 and N6). Steaming fails only
  on `milk_empty` (N4). A failed operation restarts after its service event. "Pump busy" in the
  net means "allocated", and the pump runs only between the start of brewing and its end (N7).
  Beans and the grounds bin are counters, and the plant fires `beans_empty` and `bin_full` when
  they run out. `water_empty` and `milk_empty` can happen at any time.
- **D5. Policies** (answers Q11). C1 is fixed by the net: the boiler goes back to `brew` only
  when an order needs it. We compare a **baseline** that grinds after heating with an
  **optimised** policy that grinds during heating (C2), measured with E1–E3 under random orders
  and faults.
- **D6. M2 content.** The renamed net, `EF`, `next_state` and `safe` written as definitions for
  the reduced scope, the Tina results, and the simulator attached as it is, with the differences
  and this plan. The net changes from D3 and D4 come after M2 and are verified again.
- **D7. Schedule.** T4 verification before M2 moves to BK. KP takes the net changes and their
  verification after M2. T6 ends on 05.01.2027 instead of 15.12.2026.

## Consequences

- The KB (events, state, drinks and resources, properties, glossary) is updated to the reduced
  scope after M2. Until then the M2 report is the reference.
- N8 and N9, two defects found by the safety checks, are fixed before M2 (decided by BK on
  2026-11-26), because the checks are automated and both fixes are small. The other net changes
  of D3 and D4 stay after M2.
- `model.ndr` changes twice: relabelled and renamed before M2, extended (D3, D4) after M2.
- The simulator drops the removed events, modes and fault classes. Its tests change with it.
- With one vocabulary, a trace replay in the net needs no mapping table.
- The tasks are on the [taskboard](../project/taskboard.md).
