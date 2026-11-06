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

What grounds-bin capacity should be used in the model and simulator? It determines the size of
the reachability graph, so use five slots in the model and a realistic value in the simulator?

**Answer:** the net uses five slots and the simulator defaults to ten (parameter). See
[ADR 0011](decisions/0011-bounds-for-analysis-and-simulation.md).

## Q3. Missing completion events

*Status:* resolved, ADR proposed · *Owner:* T3

`add_hot_water` and `eject_grounds` have no completion event in `E_obs`. Should hot water be
instantaneous or receive a completion event?

**Answer:** use `hot_water_done`; `eject_grounds` is instantaneous. Rinsing and milk cleaning are
out of scope. See
[ADR 0009](decisions/0009-fix-recipe-stages-and-completion-events.md).

## Q4. Faults outside the model

*Status:* resolved, ADR proposed · *Owner:* T3 / T6

The former `flow_error` and `overheat` cases are outside the current model.

**Answer:** these fault classes are outside the current model. See
[ADR 0010](decisions/0010-fault-classes-blocked-resources-and-fault-exits.md).

## Q5. Fixed cup and brew unit

*Status:* resolved, ADR proposed · *Owner:* T3

Can the cup or brew unit be removed during preparation?

**Answer:** no. Both are fixed resources; the cup and brew unit are emptied by the normal recipe
flow before another order.

## Q6. Resource fault behavior

*Status:* resolved, ADR proposed · *Owner:* T3 / T4

What faults and service actions are represented by the model?

**Answer:** `water_empty`, `beans_empty`, `milk_empty`, and `bin_full`, with their corresponding
refill or emptying transitions. Other fault classes and partial-drink reporting are out of scope.

## Q7. Petri net tool

*Status:* open · *Owner:* KP

TINA or PIPE? See [ADR 0007](decisions/0007-petri-net-analysis-tool.md).

## Q8. Overleaf sync with a monorepo

*Status:* open · *Owner:* BK

Overleaf's GitHub sync links a project to a *whole* repository, and it may need a premium (or
institutional) account. Check what our accounts allow. See
[ADR 0008](decisions/0008-reports-in-latex-via-overleaf.md).
