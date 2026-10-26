# Work plan

Source: project proposal, Section 3. Classes are on Tuesdays, 13:15–15:00, room L1.5, C-16. There
are no classes in the week of 17 November or over the Christmas break (22.12–04.01), which is a
time buffer.

## Team

| Initials | Name | Role |
|---|---|---|
| BK | Bartosz Ksel | Coordinator; system analysis, Petri net model, prioritization policies |
| KP | Krzysztof Pogoda | Petri net model, safety and recoverability analysis |
| MS | Maciej Smolarz | Simulator core, experiments |
| PU | Polona Umek | Fault and service scenarios, GUI |

## Tasks

| Task | Description | Period | Owner | Effort [h] | Lives in |
|---|---|---|---|---:|---|
| T1 | System analysis, components and events | 12.10–19.10 | BK | 8 | `docs/domain/` |
| T2 | Project proposal | 12.10–20.10 | all | 16 | `reports/proposal/` |
| T3 | Petri net model, EF, next_state | 20.10–10.11 | BK, KP | 30 | `model/`, `docs/` |
| T4 | Safety and recoverability analysis | 03.11–01.12 | KP | 25 | `model/`, `docs/requirements/` |
| T5 | Simulator core (plant + controller) | 20.10–01.12 | MS | 40 | `sim/` |
| T6 | Fault and service scenarios, GUI | 17.11–15.12 | PU | 30 | `sim/` |
| T7 | Prioritization policies, experiments | 24.11–15.12 | BK, MS | 25 | `sim/` |
| T8 | Final report and presentation | 08.12–12.01 | all | 35 | `reports/final/` |
| – | Meetings and coordination | whole project | all | 30 | `docs/meetings/` |
| | | | | **239** | |

## Milestones

| Milestone | Date | Deliverable |
|---|---|---|
| M1 | 20.10.2026 | Proposal report (PDF and hard copy). **Done.** See [reports/proposal](../../reports/proposal/). |
| M2 | 01.12.2026 | Progress report: complete Petri net, `EF`, `next_state`, `safe`, reachability results. Attached: model files and simulator source archive. |
| M3 | 12.01.2027 | Final report: model, safety/recoverability verification, policies and their comparison, simulator user guide. Attached: source, model files, simulation results. PDF, hard copy, live demo. |

## Working agreements

Weekly 30-minute meeting right after the Tuesday class, plus extra online meetings before each
milestone. Progress is tracked as GitHub issues (one issue per task, using the Task template).
Each PR is reviewed by another team member. Decisions are made by consensus, then by majority
vote, and a tie goes to the coordinator. They are recorded as ADRs. See
[CONTRIBUTING](../../CONTRIBUTING.md).
