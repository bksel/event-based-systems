# Simulator

Owners: T5 (MS, architecture BK), T6 (PU), T7 (BK, MS).

Python discrete event simulator ([ADR 0003](../docs/decisions/0003-python-discrete-event-simulator.md)):
the plant generates observable events, the controller picks controllable events using `EF(s)`,
`safe(s, e)` and a prioritization policy, and a GUI drives the demonstration. The structure and
its rules are in [ADR 0012](../docs/decisions/0012-simulator-architecture.md). Read that first.

## Layout

```
sim/
  espresso/        the package (import espresso)
    events.py      event names, exactly as in docs/domain/events.md
    drinks.py      drinks, recipe stages, R(k), B(f), fault classes
    params.py      bounds and operation durations
    state.py       the state s = (m, r, c, d, F, p), s0, sh
    model.py       EF(s), safe(s, e), next_state(s, e), invariant check  <- all behaviour
    policy.py      prioritization policies
    controller.py  picks the next controllable event
    engine.py      clock, event queue, trace
    plant.py       sources of plant events
    trace.py       traces, JSONL files, replay
  examples/        usage examples, not part of the package
```

## Running

`just setup` installs the package in editable mode. Then:

```sh
uv run python sim/examples/basic_run.py            # one espresso, printed step by step
uv run python sim/examples/basic_run.py out.jsonl  # also save the trace
just test -k sim                                   # simulator tests
```

## Where to add things

- **New behaviour** (a fault during a drink, descaling, ...): `model.py` only, and a test in
  `tests/test_sim_model.py`. Search for `TODO(MS)`. Update the KB in the same PR.
- **A new policy**: a class with `choose(state, candidates)` in `policy.py`.
- **A random plant or experiments**: `plant.py` and a new module. Use `sim.rng` for
  randomness so runs are reproducible.
- **The GUI**: a separate module that uses `Simulator.inject`, `step`/`run` and `subscribe`.
  It must not change the state itself.
