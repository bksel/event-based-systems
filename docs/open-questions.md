# Open questions

Gaps and ambiguities found while turning the proposal into the KB. When one is resolved, write
the answer here (or link the ADR that settles it) and update the affected KB pages.

Format: `## Qn. Title`, then *Status* (open / resolved), *Owner*, the question, and the answer.

## Q1. Recipe stages

*Status:* resolved · *Owner:* T3 (BK, KP)

What are the stages of `p` for each drink? For example, espresso:
`idle → heating → grinding → brewing → ejecting → done`? Does cappuccino brew first or steam
first? That choice is conflict [C1](requirements/properties.md#prioritization-conflicts), so the
stages may have to allow both orders.

**Answer:** espresso is `heating → grinding → brewing → done`. Americano adds `hot_water` after
brewing. A cappuccino always brews first and steams after (coffee in the cup, milk on top), so C1
is reformulated. See [ADR 0009](decisions/0009-fix-recipe-stages-and-completion-events.md).

## Q2. Bounds

*Status:* resolved, ADR proposed · *Owner:* T3

Values of `Ng`, `Ndue`, `Nover`. They determine the size of the reachability graph, so use small
values for analysis (e.g. `Ng = 3`) and realistic ones in the simulator?

**Answer:** analysis `Ng = 3, Ndue = 2, Nover = 3`, simulation `Ng = 10, Ndue = 150, Nover = 200`
(parameters). See [ADR 0011](decisions/0011-bounds-for-analysis-and-simulation.md).

## Q3. Missing completion events

*Status:* resolved, ADR proposed · *Owner:* T3

`add_hot_water`, `eject_grounds`, `start_rinse`, `start_milk_cleaning` and `start_descaling` have
no completion event in `E_obs`. Should we add `hot_water_done`, `rinse_done`, …, or treat these
operations as instantaneous?

**Answer:** add `hot_water_done`, `rinse_done`, `milk_cleaning_done` and `descaling_done`.
`eject_grounds` is instantaneous. See
[ADR 0009](decisions/0009-fix-recipe-stages-and-completion-events.md).

## Q4. Faults without a service event

*Status:* resolved, ADR proposed · *Owner:* T3 / T6

- `flow_error`: how is it cleared? Does the user need to do anything, or does the controller retry?
- `overheat`: needs some way out, e.g. a `cooled_down` sensor event.
- `water_low`: is it a fault in `F` (and which drinks does it block), or only a warning?

**Answer:** `flow_error` is cleared by a new service event `clear_flow_error`, and `overheat` by
a new sensor event `cooled_down`. `water_low` is only a warning. See
[ADR 0010](decisions/0010-fault-classes-blocked-resources-and-fault-exits.md).

## Q5. Cup removed mid-drink

*Status:* resolved, ADR proposed · *Owner:* T3

`cup_removed` while the pump is running would violate [S2](requirements/properties.md#safety).
Does the controller abort the drink, pause it, or is `cup_removed` treated as a fault?

**Answer:** if the pump or the steamer is running, the controller fires `abort_drink`. Before
brewing, the order waits for `cup_placed`. It is not a fault. See
[ADR 0010](decisions/0010-fault-classes-blocked-resources-and-fault-exits.md).

## Q6. Partial drinks

*Status:* resolved, ADR proposed · *Owner:* T3 / T4

General rule for faults during a drink: which faults let the current stage finish (`bin_full`),
which stop it immediately (`overheat`, `water_empty`), and which give a partial drink
(`milk_empty`)? This depends on `B(f)` in [drinks and resources](domain/drinks-and-resources.md).

**Answer:** stop and abort: `overheat`, `water_empty`, `flow_error`, `brew_unit_removed`,
`beans_empty`. Finish the drink: `bin_full`, `tray_full`. Partial drink: `milk_empty` during a
cappuccino. See [ADR 0010](decisions/0010-fault-classes-blocked-resources-and-fault-exits.md).

## Q7. Petri net tool

*Status:* resolved · *Owner:* KP

TINA or PIPE? See [ADR 0007](decisions/0007-petri-net-analysis-tool.md).

**Answer:** Tina 4.0.0. See [ADR 0007](decisions/0007-petri-net-analysis-tool.md).

## Q8. Overleaf sync with a monorepo

*Status:* open · *Owner:* BK

Overleaf's GitHub sync links a project to a *whole* repository, and it may need a premium (or
institutional) account. Check what our accounts allow. See
[ADR 0008](decisions/0008-reports-in-latex-via-overleaf.md).

## Q9. Reduced model scope

*Status:* resolved, scope reduced ([ADR 0013](decisions/0013-reduce-the-model-scope.md)) · *Owner:* BK (verify the net), then all

KP's Petri net leaves out descaling, rinsing, milk cleaning, several faults, cup removal and
order rejection. Do we reduce the agreed scope to match the net, or extend the net? This would
change ADRs agreed with the supervisor. See
[ADR 0013](decisions/0013-reduce-the-model-scope.md).

## Q10. Checking L1 with Tina

*Status:* resolved · *Owner:* BK, KP (T4)

Tina's "reversible" result means that the initial marking `s0` is a home marking. Our home state
`sh` is not `s0`, because the machine starts `off` and never returns to it. How do we show that
`sh` is reachable from every reachable marking
([L1](requirements/properties.md#recoverability))? Options: a `selt` formula, or checking that all
markings after power-on form one strongly connected component that contains `sh`. See
[ADR 0007](decisions/0007-petri-net-analysis-tool.md) and the
[net's verification status](../model/README.md#verification-status).

**Answer:** a test reads the reachability report. It checks that a home marking is reachable from
every marking, and that the graph has exactly one component that cannot be left, containing a
home marking. Both hold. See the
[net's verification status](../model/README.md#verification-status) and
`tests/test_petri_net.py`.

## Q11. Policies to compare in the reduced scope

*Status:* resolved ([ADR 0014](decisions/0014-align-the-simulator-with-the-reduced-net.md), D5) · *Owner:* BK, MS (T7)

[ADR 0013](decisions/0013-reduce-the-model-scope.md) removes conflicts C3 and C4, so only
[C1 and C2](requirements/properties.md#prioritization-conflicts) are left, and neither looks
like a real trade-off:

- **C1.** Every drink brews first, so the next drink always needs `brew`. Going back to `brew`
  at once cannot make E1 worse, and waiting does not save a temperature change (E2). The net
  also allows only one choice: `CE__heat_to_brew_from_steam` needs a pending order, so a policy that goes
  back to `brew` while idle produces traces that the net rejects.
- **C2.** Grinding during heating can only shorten preparation (E1). The net allows both
  orders.

The current `FixedOrderPolicy` already makes the eager choice in both, so the baseline is
already the best policy for E1. This follows from the model and has not been checked by
simulation yet.

Which comparison do we report in M3? Options:

1. Add a metric that makes C2 a trade-off: grounds wasted when a fault (e.g. `water_empty`)
   arrives after grinding, against preparation time. Depends on what happens to a failed
   drink.
2. Add a cost for keeping the boiler hot, and a standby rule after inactivity. This adds a new
   conflict to the model and the net.
3. Keep C1 and C2 as they are and explain in M3 why one policy dominates.

**Answer:** C1 stays as the net fixes it. We compare a baseline that grinds after heating with an
optimised policy that grinds during heating (C2), measured with E1–E3. Option 1 does not work:
a failed operation restarts after the service event, so no grounds are wasted. See
[ADR 0014](decisions/0014-align-the-simulator-with-the-reduced-net.md).
