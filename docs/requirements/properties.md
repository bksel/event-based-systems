# Properties

Source: project proposal, Sections 2.5 and 2.6. Refer to these by ID in the model, code, tests
and reports.

## Safety

No reachable state allows an unsafe actuation. `safe(s, e)` enforces this on top of `EF(s)`.

| ID | Requirement |
|---|---|
| S1 | The pump never runs without water. |
| S2 | The pump never runs without a cup. |
| S3 | The steamer never runs without milk. |
| S4 | The grinder never runs with a full grounds container. |
| S5 | No actuator runs while `overheat` is active. |
| S6 | A drink is never started unless every resource in `R(k)` is available. |

## Recoverability

| ID | Requirement |
|---|---|
| L1 | From every reachable state, the home state `sh` is reachable once the user performs the service actions for the active faults (`sh` is a home marking). |
| L2 | The net is deadlock-free. |
| L3 | A mid-drink fault (e.g. `milk_empty` during a cappuccino) does not block the machine. A partial drink is reported. |

**Verification:** check both on the reachability graph (finite, because all counters are
bounded) and support them with P-invariants.

## Efficiency

| ID | Criterion |
|---|---|
| E1 | Drink preparation time |
| E2 | Number of boiler temperature changes |
| E3 | Availability: the fraction of time in which the machine can serve a drink |

## Prioritization conflicts

Situations in which several controllable events are enabled at once. Each policy resolves them as a
priority order on `E_con ∩ EF(s)`.

| ID | Conflict |
|---|---|
| C1 | Boiler temperature after a cappuccino: switch back to `brew` at once, or stay at `steam` until a drink needs `brew`. The cappuccino order itself is fixed, brew then steam ([ADR 0009](../decisions/0009-fix-recipe-stages-and-completion-events.md)). |
| C2 | Heating and grinding in parallel, or one after the other. |
| C3 | Descaling once due: immediately, or after a period of inactivity. |
| C4 | Rinsing after every milk drink, or after a batch. |

At least two policies are compared: a **fixed-order baseline** and an **optimised policy**, using
simulation with randomly generated orders and faults.
