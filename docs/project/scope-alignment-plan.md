# Plan: align the simulator with the reduced net

Owner: BK. Status: decided in [ADR 0014](../decisions/0014-align-the-simulator-with-the-reduced-net.md) on 2026-11-26.

[ADR 0013](../decisions/0013-reduce-the-model-scope.md) reduced the scope to what the Petri net
models. The simulator still implements the earlier scope. This page lists where the two differ,
the decisions, and the work that follows. The decisions are recorded in ADR 0014, which is
where they are binding. Where ADR 0014 differs from a proposal below, ADR 0014 applies.

## 1. Differences between the net and the simulator

Read from `model/model.ndr` and `sim/espresso/` on 2026-11-26. Net names are the ones after the
rename (D1), done the same day.

| # | Topic | Net | Simulator now | Proposal |
|---|---|---|---|---|
| 1 | Event names | Had its own names with typos | Catalogue names | Labelled with catalogue events, prefixed names (D1, done) |
| 2 | Power on | `power_on` leaves the boiler `cold`, no warm-up | `heating` mode, then `temp_reached` → `ready` | Follow the net: `power_on` → `ready`, boiler `cold` |
| 3 | Modes | No modes. Faults are places, orders need only "on", the `drink_done` permit and an empty brew unit | `off, heating, ready, preparing, fault, service, descaling` | `m ∈ {off, ready, preparing}`. Faults are shown through `F` only (D2) |
| 4 | Heating | Heats only for an order. With the boiler already at `brew`, `heating_to_brew_end` fires without a heating start | Skips the `heating` stage when the boiler is hot | Always pass the `heating` stage. With a hot boiler, `temp_reached` comes at once |
| 5 | Back to `brew` after a cappuccino (C1) | `CE__heat_to_brew_from_steam` only when an order needs `brew` | Policy goes back at once, while idle | Follow the net. See [Q11](../open-questions.md#q11-policies-to-compare-in-the-reduced-scope) |
| 6 | Grinding and heating (C2) | In parallel or in sequence | Same | No change |
| 7 | Hot water | `CE__add_hot_water` is instant, no completion | `add_hot_water`, then `hot_water_done` after 15 s | Add a `hot_water_done` transition to the net (D3) |
| 8 | End of a drink | `OE__drink_done_espresso` / `OE__drink_done_americano` / `OE__drink_done_cappuccino`, then `CE__eject_grounds` | `eject_grounds` ends the order | One new completion event in the catalogue, e.g. `drink_done`, before `eject_grounds` (D3) |
| 9 | Cup | `cup__empty` / `cup__full`. Brewing fills it, the controller empties it (`CE__empty_cup`) | `absent` / `present`, `cup_placed` and `cup_removed` by the user | Follow the net: cup `empty` / `full`, a new controllable event, e.g. `empty_cup`. Remove `cup_placed` and `cup_removed` |
| 10 | Beans | 4 portions, one per grind. `OE__beans_empty` happens when none are left. A refill restores 4 | `ok` / `empty`, `beans_empty` injected | A bean counter with a capacity parameter. The plant fires `beans_empty` when it reaches 0 |
| 11 | Grounds bin | 5 slots, one per `eject_grounds`. `OE__bin_full` happens when none are left. `empty_bin` restores 5. Grinding is blocked because the brew unit stays `used` | Counter `g`, `bin_full` injected, guard S4 | `bin_full` fired by the plant when `g` reaches capacity |
| 12 | Water and milk | One token each. The fault can happen at any time | Water `ok` / `low` / `empty`, milk `ok` / `empty` | Water and milk `ok` / `empty`, faults injected at any time. Remove `water_low` |
| 13 | Fault during an operation | The operation fails (`*_fail`) and is restarted after the refill (`*_restart`) | Not implemented (fault classes from ADR 0010) | Follow the net: the stage fails and restarts after the service event. Remove fault classes, `abort_drink` and partial drinks |
| 14 | Removed by ADR 0013 | | `overheat`, `cooled_down`, `flow_error`, `clear_flow_error`, `tray_full`, `empty_tray`, `brew_unit_removed`, `insert_brew_unit`, descaling, rinsing, milk cleaning, `reject_order`, `d` | Remove from the catalogue, the code and the tests |
| 15 | Bounds | 4 beans, 5 bin slots | `Ng = 10`, no bean count | `Bounds(beans, bin)` with net values and simulation values. Traces checked against the net are produced with the net values |

## 2. Questions about the net

The IDs are those of the [net's known issues](../../model/README.md#known-issues-open), which
also lists N1–N3. ADR 0014 (D4) answers these.

| # | Observation |
|---|---|
| N4 | `OE__fail_grind` and `OE__fail_steam` have no fault as input, so they can fire at any time. `OE__fail_brew` needs `fault__water_empty`. Should grinding fail only on `beans_empty`, and steaming only on `milk_empty`? |
| N5 | `power_on` and the orders were labelled `CE` (controllable), the catalogue has them as `E_obs`. Same for the refills (spec open point O4). Fixed by D1 |
| N6 | `CE__restart_grind` takes another bean portion. Is a failed grind meant to lose its beans? |
| N7 | After `OE__fail_brew` the pump stays `pump__busy` while water is empty. Is "busy" meant as "allocated"? The reworded S5 depends on it. |

## 3. Decisions (all decided, see ADR 0014)

| # | Decision | Proposal |
|---|---|---|
| D1 | One vocabulary: rename the net's transitions to the catalogue names, or keep a mapping table | Rename. Replay then needs no mapping, and the report uses one set of names. The cost is a one-off edit of `model.ndr` |
| D2 | Modes in the reduced scope | `off, ready, preparing`, with faults in `F` |
| D3 | New events: `drink_done`, `empty_cup`, `hot_water_done` in the net | Add all three, so the net and the simulator have the same events |
| D4 | Answers to N4–N7 | KP proposes, the team agrees |
| D5 | Q11: which policy comparison M3 reports | Open. Needed before T7 starts on policies |
| D6 | What the M2 report says about the simulator, if alignment is not finished by 01.12 | State the reduced scope, the differences in section 1 and the plan |

## 4. Work

The tasks, owners and dates are on the [taskboard](taskboard.md).
