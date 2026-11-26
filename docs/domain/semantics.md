# Semantics: EF, next_state and safe

Source: the Petri net `model/model.ndr` after the fixes of 2026-11-26, in the reduced scope
([ADR 0013](../decisions/0013-reduce-the-model-scope.md),
[ADR 0014](../decisions/0014-align-the-simulator-with-the-reduced-net.md)). The net is the
reference: this page describes what it does, in terms of the state `s`. Where the simulator
still differs, see the [scope alignment plan](../project/scope-alignment-plan.md).

This page is a technical reference for the M2 report, not report text.

## 1. State

A state is a reachable marking `M` of the net. It is read as the tuple `s = (m, r, c, F, p)`:

| Part | Value | Read from the marking |
|---|---|---|
| `m` | `off`, `ready`, `preparing` | `off` iff `machine__off`. Otherwise `preparing` iff `drink_done` is 0 (an order holds the one-drink permit), else `ready` |
| `r.boiler` | `cold`, `brew`, `steam` | `boiler__cold`, `boiler__brew`, `boiler__steam`. No boiler place is marked while `m = off` |
| `r.pump` | `idle`, `busy` | `pump__idle`, `pump__busy` |
| `r.brew_unit` | `empty`, `loaded`, `used` | `brew_unit__empty`, `brew_unit__loaded`, `brew_unit_used` |
| `r.cup` | `empty`, `full` | `cup__empty`, `cup__full` |
| `c.water`, `c.milk` | `ok`, `empty` | `water_available`, `milk_available` |
| `c.beans` = `b` | `0..Nb`, `Nb = 4` | tokens in `beans_available` |
| `c.grounds` = `g` | `0..Ng`, `Ng = 5` | `Ng` minus the tokens in `bin_space_available` |
| `F` | subset of {`water_empty`, `milk_empty`, `beans_empty`, `bin_full`} | `fault__<name>` marked |
| `p` | `∅`, or the status of each task of the order | see below |

An order is a set of **tasks**, one per operation its drink needs. Each task is `todo`,
`running`, `failed` or `done`:

| Drink | Tasks |
|---|---|
| espresso | `heat`, `grind`, `brew` |
| americano | `heat`, `grind`, `brew`, `hot_water` |
| cappuccino | `heat`, `grind`, `brew`, `steam_heat`, `steam` |

| Task | `todo` | `running` | `failed` | `done` |
|---|---|---|---|---|
| `heat` | `recipe__heating_to_brew` | – (heating is one step) | – | `heating_to_brew_ended` |
| `grind` | `recipe__grinding` | `grinding_started` | `grind_failed` | `grinding_ended` |
| `brew` | `recipe__brewing` | `brewing_started` | `brewing_failed` | `brewing_ended` |
| `hot_water` | `recipe__hot_water` | – (one step) | – | `hot_water_ended` |
| `steam_heat` | `recipe__steam_heating` | – (one step) | – | `heating_to_steam_ended` |
| `steam` | `recipe__milk` | `steam_started` | `steam_failed` | `steam_ended` |

`p = ∅` iff `drink_done` is marked. A done task's place is consumed by the step that uses it
(for example, `start_brew` takes `heat` and `grind` done), so not every done task stays visible.

The P-invariants of the net guarantee that each of `m`'s off/on places, the boiler, the pump,
the brew unit and the cup is in exactly one state, and that `c.water = empty` iff
`water_empty ∈ F` (the same for milk). See the
[net's verification status](../../model/README.md#verification-status).

**Initial state `s0`:** `m = off`, pump `idle`, brew unit `empty`, cup `empty`, water and milk
`ok`, `b = 4`, `g = 0`, `F = ∅`, `p = ∅`.

**Home state `sh`:** `m = ready`, `p = ∅`, `F = ∅`, pump `idle`, brew unit `empty`, cup `empty`,
any boiler state, `b` and `g` any value (L1 is checked for this set).

## 2. EF and next_state

Each transition `t` has a **label** `λ(t)`, its event in the [event catalogue](events.md). A
transition is enabled in `M` iff every input place holds at least the arc weight and every
inhibitor place is empty.

```text
EF(s)            = { λ(t) | t is enabled in M }
next_state(s, e) = M − Pre(t) + Post(t), for the transition t enabled in M with λ(t) = e
```

`next_state` is a function because no reachable marking enables two transitions with the same
label. This matters for the labels that several transitions share (`heat_to_brew`,
`temp_reached`, `water_empty`, `milk_empty`, `drink_done`), and it is checked by
`test_next_state_is_a_function` in `tests/test_petri_net.py`.

## 3. Events

The table gives each event's enabling condition and effect in terms of `s`. Conditions in
**[brackets]** are the safety guards of `safe(s, e)` (section 4). `CE` and `OE` are the
transition name prefixes: controllable and observable, uncontrollable.

### User and sensors

| Event | | Enabled iff | Effect |
|---|---|---|---|
| `power_on` | OE | `m = off` | `m := ready`, boiler `:= cold` |
| `order_k` | OE | `m ≠ off`, `p = ∅`, brew unit `empty` | `p :=` the tasks of drink `k`, all `todo` |
| `water_empty` | OE | water `ok` | water `:= empty`, `F += water_empty`. If `brew` is `running`, it becomes `failed` in the same step (the pump stays `busy`, N7) |
| `milk_empty` | OE | milk `ok` | milk `:= empty`, `F += milk_empty`. If `steam` is `running`, it becomes `failed` in the same step |
| `beans_empty` | OE | `b = 0`, `beans_empty ∉ F` | `F += beans_empty` |
| `bin_full` | OE | `g = Ng`, `bin_full ∉ F` | `F += bin_full` |
| `refill_water` | OE | `water_empty ∈ F` | water `:= ok`, `F −= water_empty` |
| `refill_milk` | OE | `milk_empty ∈ F` | milk `:= ok`, `F −= milk_empty` |
| `refill_beans` | OE | `beans_empty ∈ F` | `b := Nb`, `F −= beans_empty` |
| `empty_bin` | OE | `bin_full ∈ F` | `g := 0`, `F −= bin_full` |

`water_empty` and `milk_empty` can also happen while `m = off` (N3, open).

### Operations

| Event | | Enabled iff | Effect |
|---|---|---|---|
| `heat_to_brew` | CE | `heat` `todo`, boiler `cold` or `steam`, **[water `ok`]** | boiler `:= brew` |
| `temp_reached` | OE | `heat` `todo` and boiler `brew`; or `steam_heat` `todo`, `brew` `done` and boiler `steam` | that task `:= done` |
| `start_grind` | CE | `grind` `todo` and not `running` or `failed`, brew unit `empty`, **[`b ≥ 1`]**, **[`g < Ng`]** | `grind := running`, brew unit `:= loaded`, `b := b − 1` |
| `grind_done` | OE | `grind` `running` | `grind := done` |
| `fail_grind` | OE | `grind` `running` | `grind := failed` (without a fault: N4, open) |
| `restart_grind` | CE | `grind` `failed`, **[`b ≥ 1`]** | `grind := running`, `b := b − 1` (N6, open) |
| `start_brew` | CE | `brew` `todo`, `heat` and `grind` `done`, brew unit `loaded`, pump `idle`, cup `empty`, **[water `ok`]** | `brew := running`, pump `:= busy`, brew unit `:= used`, cup `:= full` |
| `brew_done` | OE | `brew` `running`, water `ok` | `brew := done`, pump `:= idle` |
| `restart_brew` | CE | `brew` `failed`, **[water `ok`]** | `brew := running` |
| `add_hot_water` | CE | `hot_water` `todo`, `brew` `done`, **[water `ok`]** | `hot_water := done` (one step, without the pump: N2, open) |
| `heat_to_steam` | CE | `steam_heat` `todo`, `brew` `done`, boiler `brew`, **[water `ok`]** | boiler `:= steam` |
| `start_steam` | CE | `steam` `todo`, `steam_heat` `done`, **[milk `ok`]** | `steam := running` |
| `steam_done` | OE | `steam` `running`, milk `ok` | `steam := done` |
| `restart_steam` | CE | `steam` `failed`, **[milk `ok`]** | `steam := running` |
| `drink_done` | OE | the drink's last task is `done` (espresso: `brew`; americano: `hot_water`; cappuccino: `steam`) | `p := ∅`, so `m := ready` |
| `eject_grounds` | CE | `p = ∅`, brew unit `used`, `g < Ng` | brew unit `:= empty`, `g := g + 1` |
| `empty_cup` | CE | cup `full` | cup `:= empty` (also during a drink: N1, open) |

The boiler heats only for an order, and it goes back from `steam` to `brew` only when the next
order needs it. So conflict C1 has no choice left in the net, and C2 is the choice between
`heat_to_brew` and `start_grind` when both are enabled
([ADR 0014](../decisions/0014-align-the-simulator-with-the-reduced-net.md), D5).

## 4. safe

The net models the closed loop: the plant and the supervisor together. Splitting each guard
into a plant part and a safety part gives the supervisor:

```text
EF(s)        events the plant allows: the conditions above, without the [brackets]
safe(s, e)   true for e ∈ E_obs; for e ∈ E_con, the [bracketed] conditions of e
enabled(s)   = { e ∈ EF(s) | e ∈ E_obs, or safe(s, e) }    what the net enables
```

| Controllable event | `safe(s, e)` | Property |
|---|---|---|
| `start_brew`, `restart_brew`, `add_hot_water` | water `ok` | S1, S5 |
| `start_steam`, `restart_steam` | milk `ok` | S3, S5 |
| `start_grind` | `b ≥ 1` and `g < Ng` | S5, S4 |
| `restart_grind` | `b ≥ 1` | S5 |
| `heat_to_brew`, `heat_to_steam` | water `ok` | none of S1–S6: keeps the boiler from heating dry |
| `eject_grounds`, `empty_cup` | true | – |

The remaining properties do not come from `safe`:

- **S1 and S3 while running** hold because `water_empty` and `milk_empty` stop the running
  operation in the same step (N8, fixed), so `safe` only has to guard the start.
- **S2** holds because the cup is fixed (ADR 0013): it is always there, `empty` or `full`.
- **S6** is enforced by the plant: orders are uncontrollable, and the machine does not accept
  one while `p ≠ ∅` (the one-drink permit). The supervisor could not disable an order.

All of S1–S6 are checked on the reachability graph. See the
[net's verification status](../../model/README.md#verification-status).
