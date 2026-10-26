# Supervisory control of an automatic espresso machine

Course project for *Event Based Control* (2026/27). We design an event-based supervisory
controller for a fully automatic espresso machine, including fault handling and service actions.
The machine is modelled as a Petri net, the model is verified for **safety** and
**recoverability**, and a Python discrete event simulator is used to compare **event
prioritization policies**.

**Team:** Bartosz Ksel (coordinator), Krzysztof Pogoda, Maciej Smolarz, Polona Umek

## Repository layout

| Path | Contents |
|---|---|
| [`docs/`](docs/README.md) | Knowledge base: domain model, requirements, decisions (ADRs), sources, meetings. **Start here.** |
| [`model/`](model/README.md) | Petri net model files and analysis results |
| [`sim/`](sim/README.md) | Python discrete event simulator (plant, controller, policies, GUI) |
| [`reports/`](reports/README.md) | LaTeX sources and submitted PDFs of the milestone reports |
| `tools/` | Repository tooling: KB checker, document generator |
| `tests/` | Tests |

## Getting started

Follow [SETUP.md](SETUP.md) once. After that:

```sh
just          # list all commands
just check    # KB consistency + lint + tests; run before every PR
```

How we work (branches, PRs, ADRs, the inbox) is described in [CONTRIBUTING.md](CONTRIBUTING.md).

## Milestones

| | Date | |
|---|---|---|
| M1 | 20.10.2026 | Proposal ✔ |
| M2 | 01.12.2026 | Model verified, simulator working |
| M3 | 12.01.2027 | Final report and live demonstration |
