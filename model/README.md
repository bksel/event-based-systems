# Petri net model

Owners: T3 (BK, KP), T4 (KP).

`model.ndr` is the Petri net of the machine, in the format of Tina 4.0.0
([ADR 0007](../docs/decisions/0007-petri-net-analysis-tool.md)). How to install Tina, edit the
net, lay it out and analyse it is described in [TINA.md](TINA.md).

## Scope

The net models the **reduced scope** accepted in
[ADR 0013](../docs/decisions/0013-reduce-the-model-scope.md) ([Q9](../docs/open-questions.md#q9-reduced-model-scope)):
there is no descaling, rinsing or milk cleaning, no order rejection, no cup removal, and only four
faults. The [KB](../docs/README.md) still describes the earlier scope until it is updated to match.

## Verification status

[tests/test_petri_net.py](../tests/test_petri_net.py) checks the net with Tina on every
`just check` (skipped when Tina is not installed):

| Check | Result |
|---|---|
| `tina -p`: the file parses with no skipped lines | ✓ |
| Reachability graph complete and bounded | ✓ 18,716 states |
| No deadlocks (L2) | ✓ |
| Every transition can fire | ✓ |

Not verified yet (**open**):

- **L1, the home state.** Tina's "reversible" means that the initial marking `s0` (machine off)
  is a home marking, and `s0` is never reached again after power-on. L1 is about the home state
  `sh`, so it needs a separate check. The method still has to be worked out:
  [Q10](../docs/open-questions.md#q10-checking-l1-with-tina).
- **Safety S1–S6.** These are not yet written as properties that Tina can check (e.g. with
  `selt`).
- **P-invariants.** `struct` reports that the net is not covered by P-invariants. Which places are
  not conserved, and whether that is intended, has not been checked.

## Structure

| Part | Places | Transitions |
|---|---|---|
| Power and boiler | `machine__off`, `boiler__cold`, `boiler__brew`, `boiler__steam` | `OE__power_on`, `CE__heat_to_brew`, `CE__heat_to_brew_from_steam`, `CE__heat_to_steam` |
| Orders | `drink_done` (one-drink permit), `recipe__*` (stages still to do) | `OE__order_espresso`, `OE__order_americano`, `OE__order_cappuccino` |
| Heating stage | `recipe__heating_to_brew`, `heating_to_brew_ended`, `heating_to_steam_ended` | `OE__temp_reached_brew`, `OE__temp_reached_steam` |
| Grinding | `beans_available` (4 tokens), `grinding_started`, `grinding_ended`, `grind_failed` | `CE__start_grind`, `OE__grind_done`, `OE__fail_grind`, `CE__restart_grind` |
| Brew unit and grounds | `brew_unit__empty`, `brew_unit__loaded`, `brew_unit_used`, `bin_space_available` (5 tokens) | `CE__eject_grounds` |
| Brewing | `pump__idle`, `pump__busy`, `cup__empty`, `cup__full`, `brewing_started`, `brewing_ended`, `brewing_failed` | `CE__start_brew`, `OE__brew_done`, `OE__fail_brew`, `CE__restart_brew`, `CE__empty_cup` |
| Hot water and steam | `hot_water_ended`, `steam_started`, `steam_ended`, `steam_failed` | `CE__add_hot_water`, `CE__start_steam`, `OE__steam_done`, `OE__fail_steam`, `CE__restart_steam` |
| Drink completion | | `OE__drink_done_espresso`, `OE__drink_done_americano`, `OE__drink_done_cappuccino` |
| Faults and service | `water_available`, `milk_available`, `fault__water_empty`, `fault__beans_empty`, `fault__milk_empty`, `fault__bin_full` | `OE__water_empty`, `OE__beans_empty`, `OE__milk_empty`, `OE__bin_full`, `OE__refill_water`, `OE__refill_beans`, `OE__refill_milk`, `OE__empty_bin` |

An order puts one token into each stage place its drink needs. The `drink_done` token blocks a
second order until the drink is complete. Heating is a single step, and `temp_reached_*` mark the
heating stage as done.

Names ([ADR 0014](../docs/decisions/0014-align-the-simulator-with-the-reduced-net.md), D1):

- A transition's **label** is its event in the [event catalogue](../docs/domain/events.md).
  Traces are replayed by label.
- A transition's **name** is the label with a prefix that says whether the controller can choose
  it: `CE__` for controllable events (`E_con`), `OE__` for observable, uncontrollable ones
  (`E_obs`). The prefix comes from the catalogue, so orders, `power_on` and the refills are
  `OE__`: the user decides them, not the controller.
- Names are unique. Where several transitions stand for one event, the name adds a suffix:
  `CE__heat_to_brew_from_steam` (label `heat_to_brew`), `OE__temp_reached_brew` and
  `OE__temp_reached_steam` (label `temp_reached`), and `OE__drink_done_*` (label `drink_done`).
- `fail_*`, `restart_*`, `drink_done` and `empty_cup` are not in the catalogue yet (A2 on the
  [taskboard](../docs/project/taskboard.md)). A failure is a plant event (`OE__`), a restart is
  a controller decision (`CE__`), `drink_done` is a completion (`OE__`) and `empty_cup` is
  controllable (`CE__`).

## Known issues (open)

These were found in review. Fixing N1–N4, N6 and N7 is task A3b on the
[taskboard](../docs/project/taskboard.md). ADR 0014 (D4) decides N4, N6 and N7.

| ID | Issue | Conflicts with |
|---|---|---|
| N1 | `CE__empty_cup` can fire in the middle of a drink, and `CE__add_hot_water` and `CE__start_steam` do not check the cup, so hot water or milk can go into an emptied cup | S2 |
| N2 | `CE__add_hot_water` does not use the pump (`pump__idle` / `pump__busy`) | S1, S2 |
| N3 | `OE__water_empty` and `OE__milk_empty` can fire before `OE__power_on` | [events](../docs/domain/events.md) |
| N4 | `OE__fail_grind` and `OE__fail_steam` fire without any fault, and the `CE__restart_*` transitions have no counterpart in the KB | [ADR 0010](../docs/decisions/0010-fault-classes-blocked-resources-and-fault-exits.md) |
| N5 | Names did not match the [event catalogue](../docs/domain/events.md). **Fixed** on 2026-11-26 (ADR 0014, D1): transitions labelled with catalogue events, prefixes set from the catalogue, typos in place names fixed (`recipe__milk`, `fault__milk_empty`) | events |
| N6 | `CE__restart_grind` takes another bean portion, so a failed grind loses its beans | ADR 0014, D4 |
| N7 | After `OE__fail_brew` the pump stays `pump__busy` while the water is empty. ADR 0014 (D4) reads "busy" as "allocated" | S1 |
