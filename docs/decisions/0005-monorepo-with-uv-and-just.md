---
status: accepted
date: 2026-10-26
deciders: Bartosz Ksel
---

# 0005. Monorepo with uv, ruff, pytest and just

## Context

Code, model files, the knowledge base and the LaTeX reports have to stay consistent with each
other, and every team member must be able to set up the environment quickly on Linux, macOS or
Windows.

## Decision

- **One repository** holds `docs/`, `model/`, `sim/`, `reports/` and `tools/`.
- **uv** manages Python and dependencies (`pyproject.toml` + `uv.lock`).
- **ruff** for linting and formatting, **pytest** for tests.
- **just** is the single entry point for commands (`just check`, `just adr`, …), so nobody has to
  remember tool invocations.

## Consequences

- Teammates install two tools (uv, just). See [SETUP](../../SETUP.md).
- `uv.lock` is committed. Change dependencies only with `uv add` / `uv remove`.
- Checks run locally with `just check`. There is no CI for now.
