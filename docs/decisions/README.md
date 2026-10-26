# Architecture decision records

An ADR records one decision: the context, the options, what we chose, and the consequences.
ADRs are never deleted. If we change our mind, we write a new ADR and mark the old one
`superseded` with `superseded-by: NNNN`.

## Process

1. `just adr "Short imperative title"` creates `NNNN-short-imperative-title.md` with status
   `proposed` and adds it to the table below.
2. Fill it in, set `deciders`, and open a PR. Discuss it in the PR or at the Tuesday meeting.
3. Once agreed, set `status: accepted` (or `rejected`) and update the status column below.
4. `just kb` checks the frontmatter, numbering, titles, `superseded-by` targets, and that every
   ADR is listed here.

Allowed statuses: `proposed`, `accepted`, `rejected`, `deprecated`, `superseded`.

## Index

| ADR | Title | Status |
|---|---|---|
| [0001](0001-record-architecture-decisions.md) | Record architecture decisions | accepted |
| [0002](0002-petri-nets-as-modelling-formalism.md) | Use Petri nets as the modelling formalism | accepted |
| [0003](0003-python-discrete-event-simulator.md) | Implement plant and controller as a Python discrete event simulator | accepted |
| [0004](0004-one-drink-at-a-time.md) | Three-drink menu, one drink at a time | accepted |
| [0005](0005-monorepo-with-uv-and-just.md) | Monorepo with uv, ruff, pytest and just | accepted |
| [0006](0006-markdown-knowledge-base.md) | Plain Markdown knowledge base with an untracked inbox | accepted |
| [0007](0007-petri-net-analysis-tool.md) | Choose the Petri net analysis tool | proposed |
| [0008](0008-reports-in-latex-via-overleaf.md) | Write reports in LaTeX on Overleaf, synced with the repo | accepted |
