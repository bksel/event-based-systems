# Taskboard

Owner: BK, who keeps it up to date. Last updated 2026-11-26.

This is the single list of who does what by when. It replaces GitHub issues. When you finish a
task or get stuck, tell BK, or edit the status here in your PR. The larger tasks T1–T8 are in the
[work plan](workplan.md). The background for the tasks below is in the
[scope alignment plan](scope-alignment-plan.md) and
[ADR 0014](../decisions/0014-align-the-simulator-with-the-reduced-net.md).

Status: **todo**, **doing**, **done**, **blocked** (say on what).

## Before M2 (01.12.2026)

| ID | Task | Owner | Due | Needs | Status |
|---|---|---|---|---|---|
| A0 | Decide D1–D7 and record them ([ADR 0014](../decisions/0014-align-the-simulator-with-the-reduced-net.md)) | BK | 26.11 | | done |
| A3a | Rename the net's transitions to the catalogue names (D1), `tests/test_petri_net.py` passes | BK | 27.11 | A0 | done |
| A11 | Check L1 on the renamed net ([Q10](../open-questions.md#q10-checking-l1-with-tina)) | BK | 29.11 | A3a | done |
| A12 | Write the safety properties as Tina formulas and check them. List the places not covered by P-invariants | BK | 29.11 | A3a | done |
| A13 | `EF`, `next_state` and `safe` for the reduced scope, as definitions for the report | BK | 29.11 | A0 | todo |
| A14 | M2 report: simulator section (what exists, what changes, from the plan) | MS | 30.11 | | todo |
| A15 | M2 report: assemble, check and submit | BK | 01.12 | A11–A14 | todo |
| A16 | Message the team: decisions, this board, the report sections | BK | 27.11 | A0 | todo |
| A17 | Online meeting, 30 min, notes in [meetings](../meetings/README.md) | BK | 29.11 | A16 | todo |

## After M2

| ID | Task | Owner | Due | Needs | Status |
|---|---|---|---|---|---|
| A2 | Update the KB to the reduced scope: events, state, drinks and resources, properties, glossary | BK | 04.12 | A0 | todo |
| A3b | Change the net according to D3 and D4, fix the [net's known issues](../../model/README.md#known-issues-open) N1–N4, N6, N7, check that `tests/test_petri_net.py` still passes | KP | 08.12 | A3a | todo |
| A4 | Align the simulator with the net: events, drinks, state, params, model, policy, tests | BK | 08.12 | A2 | todo |
| A5 | Replay tool: run a JSONL trace in Tina, one test trace per drink and per fault | BK, KP | 11.12 | A3b, A4 | todo |
| A6 | GUI core: `Session`, `FakeSession`, main window ([GUI spec](../../sim/gui_specification.md) C1, C2) | BK | 08.12 | A4 | todo |
| A10 | Update the GUI spec to ADR 0014 (modes, events, its open points) | BK | 03.12 | A0 | todo |
| A7 | GUI widgets W1–W6 against `FakeSession`. Until A6: read the GUI spec and send questions | PU | 05.01 | A6 | todo |
| A8 | Random plant, metrics E1–E3 from traces, experiment runner | MS | 15.12 | A4 | todo |
| A9 | Baseline and optimised policies (D5), experiments | BK, MS | 22.12 | A8 | todo |
| A18 | M3 report: verification chapter | KP | 05.01 | A3b | todo |

## Done

| ID | Task | Owner | Done |
|---|---|---|---|
| – | GUI specification ([sim/gui_specification.md](../../sim/gui_specification.md)) | BK | 25.11 |
| – | Accept the reduced scope ([ADR 0013](../decisions/0013-reduce-the-model-scope.md), Q9) | BK | 25.11 |
| – | Scope alignment plan and Q11 | BK | 26.11 |
| – | Fix net issues N8 and N9 found by the safety checks ([model README](../../model/README.md#verification-status)) | BK | 26.11 |
