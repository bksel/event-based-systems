---
status: proposed
date: 2026-11-01
deciders: Bartosz Ksel
---

# 0012. Simulator architecture

## Context

[ADR 0003](0003-python-discrete-event-simulator.md) left the simulator's internal structure open:
its modules, whether it executes the Petri net directly, and the GUI toolkit. The simulator
(T5) is needed for M2, while the Petri net (T3) and the analysis tool
([Q7](../open-questions.md#q7-petri-net-tool)) are still in progress. Several people will
build on the simulator: the core (T5), fault scenarios and the GUI (T6), and the policies and
experiments (T7). They need a structure that is fixed early and easy to read.

## Options considered

1. **Execute the Petri net**: a generic net engine that loads the net drawn in the analysis
   tool. One source of truth, but blocked until Q7 and the net are done. Timing and policies
   also fit poorly on raw transitions.
2. **Define the net in Python**: places and transitions as data, executed here and exported to
   the tool. Not blocked by Q7, but it means drawing the net in code before T3 does.
3. **Hand-coded state and transition function**: the state tuple `s = (m, r, c, d, F, p)` as
   Python data, and `EF`, `safe` and `next_state` as plain functions that follow the KB.
   Readable and not blocked, but it duplicates the semantics of the net, so the two must be
   checked against each other.

## Decision

We choose option 3. The simulator is a Python package `espresso` in `sim/espresso/`:

| Module | Contents |
|---|---|
| `events.py` | The event alphabet, with names exactly as in the [event catalogue](../domain/events.md) |
| `drinks.py` | Drinks, recipe stages ([ADR 0009](0009-fix-recipe-stages-and-completion-events.md)), `R(k)`, `B(f)`, fault classes ([ADR 0010](0010-fault-classes-blocked-resources-and-fault-exits.md)) |
| `params.py` | Bounds ([ADR 0011](0011-bounds-for-analysis-and-simulation.md)) and operation durations |
| `state.py` | The immutable state, `s0` and `sh` |
| `model.py` | `EF(s)`, `safe(s, e)`, `next_state(s, e)` and the invariant check. **The only place that defines behaviour.** |
| `policy.py` | The policy interface and the fixed-order baseline |
| `controller.py` | Picks the next controllable event |
| `engine.py` | Simulated clock, event queue, completion scheduling, trace, observers |
| `plant.py` | Sources of plant events. For now, a scripted plant |
| `trace.py` | Trace entries, JSONL files, replay |

Rules:

- **Pure semantics.** `State` is immutable and `next_state` has no side effects. The controller,
  the engine and the GUI never change the state themselves. They only choose or schedule
  events.
- **Agreement with the net through traces.** The simulator is not generated from the net. A
  trace (a JSONL list of timed events) must be a valid run both here and in the net. The
  scenarios in `docs/requirements` and random runs are replayed in both
  (ADR 0003, consequence).
- **Orders are always accepted as events.** An order arriving while the machine is idle (`ready`
  or `fault`) is always feasible. If the drink is unavailable, the order takes the stage
  `rejected` and the controller answers with `reject_order`. Plant events that are not in
  `EF(s)` when they arrive, such as an order during preparation, are ignored and logged
  separately, so the trace stays a valid run.
- **Mandatory reactions come before the policy.** `abort_drink` and `reject_order` are rules, not
  choices. A policy only orders the remaining candidates (conflicts C1–C4). It may also return
  "wait", which C1 and C3 need.
- **Time.** Simulated seconds. Each controllable operation schedules its completion event after
  a configurable duration. Instantaneous events take no time. Events at the same time are
  processed in insertion order. A completion is cancelled if its operation stops early.
- **Safety checked at run time.** After every event the engine asserts S1–S5, the counter
  bounds, and the rule that `m = fault` iff the active faults block every drink. Every
  simulation run therefore also tests the controller.
- **Reproducible.** There is one seeded random generator per run. The same seed and inputs give
  the same trace.
- **Standard library only.** We use our own `heapq` queue rather than SimPy. The queue is small,
  and we need full control over ordering and cancellation.
- **GUI-agnostic.** `step()`, `run(until)` and observer callbacks let a GUI drive the simulator
  step by step or in scaled real time. The toolkit is chosen in T6.
- **Metrics from the trace.** E1–E3 are computed from the trace afterwards, not inside the
  engine.

## Consequences

- The simulator does not wait for the analysis tool or the finished net.
- The semantics exist twice, in the net and in `model.py`. The trace replay check is the
  safeguard, and the net is the reference when they disagree.
- The state has one variable that the KB does not have: the boiler's heating target
  (`heating_to`), which records that heating has started. [State](../domain/state.md) now
  lists it.
- The KB rule "an order is in `EF(s)` only if the drink is available" is replaced by the rule
  above. [Drinks and resources](../domain/drinks-and-resources.md) is updated.
- The first version covers power-on, the nominal path of all three drinks, waiting for the cup,
  idle faults and their service events, finish-class faults during a drink, and rejecting
  orders. Still missing, and tracked as issues: stop- and partial-class faults during a drink,
  removing the cup mid-drink, `abort_drink`, rinsing, milk cleaning, descaling, a random plant,
  the optimised policy, the GUI, and trace replay in the net. A stop-class fault must switch the
  blocked actuators off in the same transition, or the invariant check fails.
- `pyproject.toml` builds `sim/espresso` as a package, so `uv sync` installs it in editable mode
  and `import espresso` works from scripts and tests.
