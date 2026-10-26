---
status: accepted
date: 2026-10-26
deciders: Bartosz Ksel
---

# 0001. Record architecture decisions

## Context

Four people work on the model, the analysis, the simulator and the reports over three months.
Decisions made in a group chat or at a meeting are easy to lose. The final report also has to
justify the design choices.

## Decision

We record every significant decision as an ADR in `docs/decisions/`, in the lightweight MADR
format given by [template.md](template.md). A decision is significant if it affects more than
one task, is hard to reverse, or will be explained in a report.

## Consequences

- Decisions from chat or meetings must be turned into an ADR (or an issue) to count.
- The final report's design chapter can be assembled largely from the ADRs.
- `just kb` checks ADRs, so a malformed one fails the check.
