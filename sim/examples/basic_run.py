"""Example: how to use the simulator core. This is not the simulator itself.

Runs one espresso order, prints what happened and saves the trace.

    uv run python sim/examples/basic_run.py [trace.jsonl]
"""

import sys
from pathlib import Path

from espresso import (
    Event,
    FixedOrderPolicy,
    ScriptedPlant,
    Simulator,
    enabled,
    is_home,
    replay,
    write_jsonl,
)


def main(trace_path: Path | None = None) -> Simulator:
    # 1. A simulator needs a policy: how the controller resolves conflicts C1–C4.
    #    Bounds, durations and the random seed are optional keyword arguments.
    sim = Simulator(FixedOrderPolicy())

    # 2. The plant produces user and sensor events. ScriptedPlant takes (time, event) pairs.
    #    Completion events (temp_reached, grind_done, ...) are scheduled by the simulator.
    plant = ScriptedPlant(
        [
            (0, Event.POWER_ON),
            (60, Event.ORDER_ESPRESSO),
            (65, Event.CUP_PLACED),  # the order waits at `brewing` until the cup is there
        ]
    )
    plant.install(sim)

    # 3. Observers are called after every event. A GUI would redraw here.
    sim.subscribe(
        lambda entry, state: print(
            f"{entry.time:6.1f}s  {entry.source:<10}  {entry.event:<16} -> mode {state.mode}"
        )
    )

    # 4. Run until nothing is left to do (or sim.run(until=...), or sim.step() one by one).
    sim.run()

    s = sim.state
    print()
    print(f"home state: {is_home(s)}, grounds g = {s.consumables.grounds}, d = {s.descaling}")
    print(f"possible next events: {', '.join(sorted(enabled(s)))}")
    if sim.ignored:
        print(f"ignored (not feasible when they arrived): {sim.ignored}")

    # 5. The trace is the record of the run. Replaying it checks that it is a valid run;
    #    the same file can be replayed in the Petri net.
    assert replay(sim.trace)[-1] == s
    if trace_path is not None:
        write_jsonl(sim.trace, trace_path)
        print(f"trace written to {trace_path}")
    return sim


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else None)
