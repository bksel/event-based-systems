# Open questions

Gaps and ambiguities found while turning the proposal into the KB. When one is resolved, write
the answer here (or link the ADR that settles it) and update the affected KB pages.

Format: `## Qn. Title`, then *Status* (open / resolved), *Owner*, the question, and the answer.

## Q1. Recipe stages

*Status:* open · *Owner:* T3 (BK, KP)

What are the stages of `p` for each drink? For example, espresso:
`idle → heating → grinding → brewing → ejecting → done`? Does cappuccino brew first or steam
first? That choice is conflict [C1](requirements/properties.md#prioritization-conflicts), so the
stages may have to allow both orders.

## Q2. Bounds

*Status:* open · *Owner:* T3

Values of `Ng`, `Ndue`, `Nover`. They determine the size of the reachability graph, so use small
values for analysis (e.g. `Ng = 3`) and realistic ones in the simulator?

## Q3. Missing completion events

*Status:* open · *Owner:* T3

`add_hot_water`, `eject_grounds`, `start_rinse`, `start_milk_cleaning` and `start_descaling` have
no completion event in `E_obs`. Should we add `hot_water_done`, `rinse_done`, …, or treat these
operations as instantaneous?

## Q4. Faults without a service event

*Status:* open · *Owner:* T3 / T6

- `flow_error`: how is it cleared? Does the user need to do anything, or does the controller retry?
- `overheat`: needs some way out, e.g. a `cooled_down` sensor event.
- `water_low`: is it a fault in `F` (and which drinks does it block), or only a warning?

## Q5. Cup removed mid-drink

*Status:* open · *Owner:* T3

`cup_removed` while the pump is running would violate [S2](requirements/properties.md#safety).
Does the controller abort the drink, pause it, or is `cup_removed` treated as a fault?

## Q6. Partial drinks

*Status:* open · *Owner:* T3 / T4

General rule for faults during a drink: which faults let the current stage finish (`bin_full`),
which stop it immediately (`overheat`, `water_empty`), and which give a partial drink
(`milk_empty`)? This depends on `B(f)` in [drinks and resources](domain/drinks-and-resources.md).

## Q7. Petri net tool

*Status:* open · *Owner:* KP

TINA or PIPE? See [ADR 0007](decisions/0007-petri-net-analysis-tool.md).

## Q8. Overleaf sync with a monorepo

*Status:* open · *Owner:* BK

Overleaf's GitHub sync links a project to a *whole* repository, and it may need a premium (or
institutional) account. Check what our accounts allow. See
[ADR 0008](decisions/0008-reports-in-latex-via-overleaf.md).
