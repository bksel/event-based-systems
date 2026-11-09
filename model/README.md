# Petri net model

Owners: T3 (BK, KP), T4 (KP).

`model.ndr` is the Petri net of the machine, in the format of Tina 4.0.0
([ADR 0007](../docs/decisions/0007-petri-net-analysis-tool.md)). How to install Tina, edit the
net, lay it out and analyse it is described in [TINA.md](TINA.md).

## Scope

The net models a **reduced scope**, not the scope agreed in ADRs
[0009](../docs/decisions/0009-fix-recipe-stages-and-completion-events.md)–[0011](../docs/decisions/0011-bounds-for-analysis-and-simulation.md):
there is no descaling, rinsing or milk cleaning, no order rejection, no cup removal, and only four
faults. Whether the scope is reduced or the net is extended is **open**:
[ADR 0013](../docs/decisions/0013-reduce-the-model-scope.md),
[Q9](../docs/open-questions.md#q9-reduced-model-scope). Until that is settled, the
[KB](../docs/README.md) describes the agreed scope, and the net differs from it.

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
| Power and boiler | `machine__off`, `boiler__cold`, `boiler__brew`, `boiler__steam` | `CE__power__on`, `CE__heating_to_brew`, `CE__heating_to_steam`, `CE__cooling_to_brew` |
| Orders | `drink_done` (one-drink permit), `recipe__*` and `reciple__milk` (stages still to do) | `CE__order_espresso`, `CE__order_americano`, `CE_order_cappucino` |
| Heating stage | `recipe__heating_to_brew`, `heating_to_brew_ended`, `heating_to_steam_ended` | `heating_to_brew_end`, `heating_to_steam_end` |
| Grinding | `beans_available` (4 tokens), `grinding_started`, `grinding_ended`, `grind_failed` | `CE__grind__start`, `OE__grind__end`, `OE__grind__fail`, `CE__grind_restart` |
| Brew unit and grounds | `brew_unit__empty`, `brew_unit__loaded`, `brew_unit_used`, `bin_space_available` (5 tokens) | `CE__eject_grounds` |
| Brewing | `pump__idle`, `pump__busy`, `cup__empty`, `cup__full`, `brewing_started`, `brewing_ended`, `brewing_failed` | `CE__brewing_start`, `OE__brewing_end`, `OE__brewing_fail`, `CE__brewing_restart`, `CE__cup_empty` |
| Hot water and steam | `hot_water_ended`, `steam_started`, `steam_ended`, `steam_failed` | `CE__add_hot_woter`, `CE__steam_start`, `OE__steam_end`, `OE_steam_fail`, `CE_steam_restart` |
| Drink completion | | `OE__espresso_done`, `OE__americano_done`, `OE__cappucino_done` |
| Faults and service | `water_available`, `milk_available`, `fault__water_empty`, `fault__beans_empty`, `fault_milk_empty`, `fault__bin_full` | `OE__water_empty`, `OE__beans_empty`, `OE_mile_empty`, `OE__bin_full`, `CE__water_refill`, `CE__beans_refill`, `CE_milk_refill`, `CE__empty_bin` |

An order puts one token into each stage place its drink needs. The `drink_done` token blocks a
second order until the drink is complete. The boiler has no `temp_reached` event: heating is a
single step, and `heating_to_*_end` mark the heating stage as done.

Names: `CE__` is meant to mark controllable events (`E_con`) and `OE__` observable ones
(`E_obs`), with `__` between a namespace and a name. The net does not follow this consistently
yet (N5 below).

## Known issues (open)

These were found in review and are **not fixed yet**. Each still needs an issue on GitHub.

| ID | Issue | Conflicts with |
|---|---|---|
| N1 | `CE__cup_empty` can fire in the middle of a drink, and `CE__add_hot_woter` and `CE__steam_start` do not check the cup, so hot water or milk can go into an emptied cup | S2 |
| N2 | `CE__add_hot_woter` does not use the pump (`pump__idle` / `pump__busy`) | S1, S2 |
| N3 | `OE__water_empty` and `OE_mile_empty` can fire before `CE__power__on` | [events](../docs/domain/events.md) |
| N4 | `OE__grind__fail` and `OE_steam_fail` fire without any fault, and the `*_restart` transitions have no counterpart in the KB | [ADR 0010](../docs/decisions/0010-fault-classes-blocked-resources-and-fault-exits.md) |
| N5 | Names do not match the [event catalogue](../docs/domain/events.md): typos (`woter`, `mile`, `reciple`, `cappucino`), `CE_` vs `CE__`, user and service events marked `CE__` (orders, `power__on`, refills, `cup_empty`, `empty_bin`), and `heating_to_*_end` with no prefix. Traces from the net cannot be compared with the simulator until this is fixed ([ADR 0003](../docs/decisions/0003-python-discrete-event-simulator.md)) | events |
