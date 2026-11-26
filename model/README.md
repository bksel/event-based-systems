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
| L1: a home marking is reachable from every marking | ✓ 61 home markings, every marking reaches one |
| L1, strong form: one component that cannot be left, and it contains a home marking | ✓ 18,480 markings, 60 of the 61 home markings |
| S1: the pump never runs without water | ✗ 504 markings (N8) |
| S2: the pump never runs without a cup | ✓ the cup is always there (fixed cup) |
| S3: the steamer never runs without milk | ✗ 168 markings (N8) |
| S4: the grinder never runs with a full grounds container | ✗ 864 markings (N9) |
| S5 (reworded): grinding, brewing, hot water and steaming start only with their permit | ✓ |
| S6 (reworded): no order while a drink is active | ✓ |

**L1** (checked on 2026-11-26, method from [Q10](../docs/open-questions.md#q10-checking-l1-with-tina)).
The tests read the markings, the edges and the strongly connected components from Tina's
reachability report. A **home marking** is one where only these places are marked: `drink_done`,
`brew_unit__empty`, `cup__empty`, `pump__idle`, `water_available`, `milk_available` (one token
each), and the counters and the boiler places (any value). So the machine is on, has no order,
nothing is running and no fault is active. Results:

- Every one of the 18,716 reachable markings can reach a home marking.
- The graph has one component that cannot be left (18,480 markings). Every marking leads into
  it, so each of the 60 home markings inside it can be reached again from every reachable
  marking: it is a home marking of the net in Tina's sense.
- The 61st home marking is the one right after `OE__power_on`, with the boiler `cold`. It is
  never reached again, because the boiler does not return to `cold`. For the same reason
  `OE__power_on` and `CE__heat_to_brew` are the two transitions that are not live.
- Tina's "not reversible" refers to the initial marking (machine off), which is never reached
  again after power-on. It does not contradict L1.
- The net lets every transition fire, so "once the user performs the service actions" in L1 is
  covered: the service transitions are part of the graph.

**Safety** (checked on 2026-11-26, the reduced scope of
[ADR 0013](../docs/decisions/0013-reduce-the-model-scope.md), which rewords S5 and S6). Each
property is a condition on every reachable marking, or on every edge for S6. An operation
**runs** while its `*_started` place is marked. S1, S3, S4 and S6 were also checked with `selt`
on the same graph, with the same results:

```text
[] - (brewing_started /\ - water_available)      S1   FALSE
[] - (steam_started /\ - milk_available)         S3   FALSE
[] - (grinding_started /\ - bin_space_available) S4   FALSE
[] - (drink_done /\ (recipe__brewing \/ recipe__grinding \/ recipe__heating_to_brew))  S6  TRUE
```

Shortest counterexamples from power-on (prefixes left out):

- **S1:** `power_on → order_americano → heat_to_brew → start_grind → grind_done →
  temp_reached_brew → start_brew → water_empty`. The pump runs without water until `fail_brew`
  fires, and if `refill_water` comes first it never stops.
- **S3:** the same pattern for a cappuccino: `… → start_steam → milk_empty`.
- **S4:** five espressos fill the bin (`bin_space_available` reaches 0), and the next order
  starts the grinder: `… → eject_grounds → order_americano → start_grind`.

The tests for S1, S3 and S4 are marked as expected failures (`xfail`, strict) until the net is
fixed (A3b on the [taskboard](../docs/project/taskboard.md)).

**P-invariants** (`struct -P`). `struct` ignores inhibitor arcs, but they only block firing, so
every invariant it finds also holds for this net. There are 13 P-semiflows. Among them, the pump,
the cup and the boiler are each in exactly one state, and `pump__idle + brewing_started +
brewing_failed = 1` (the pump counts as busy while a brew has failed, N7). Seven places are not
covered, all by construction:

- `beans_available`, `bin_space_available`, `fault__beans_empty`, `fault__bin_full`: a refill or
  `empty_bin` restores a fixed number of tokens however many are left, so no weighted sum stays
  constant. The net is still bounded, because the inhibitor arcs allow the fault only at 0.
- `recipe__hot_water`, `recipe__milk`, `recipe__steam_heating`: only one kind of drink creates
  each of them.

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

These were found in review and by the checks above. Fixing N1–N4 and N6–N9 is task A3b on the
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
| N8 | `OE__water_empty` and `OE__milk_empty` do not stop a running pump or steamer. That takes a separate `OE__fail_brew` / `OE__fail_steam`, and a refill can come first. Found by the S1 and S3 checks | S1, S3 |
| N9 | `CE__start_grind` does not check `bin_space_available`, so the grinder starts with the grounds bin full. Found by the S4 check | S4 |
