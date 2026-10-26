# Simulator

Owners: T5 (MS), T6 (PU), T7 (BK, MS).

Python discrete event simulator ([ADR 0003](../docs/decisions/0003-python-discrete-event-simulator.md)):
the plant generates observable events, the controller picks controllable events using `EF(s)`,
`safe(s, e)` and a prioritization policy, and a GUI drives the demonstration.

Not started yet. The package layout, GUI toolkit and the way the simulator relates to the Petri
net model are for T5 to decide and record as an ADR (`just adr "..."`).

When code is added here, also update `pyproject.toml`: switch `[tool.uv] package` to `true`, or
add `sim` to the pytest `pythonpath`.
