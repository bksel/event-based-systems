---
status: accepted
date: 2026-10-20
deciders: Bartosz Ksel, Krzysztof Pogoda, Maciej Smolarz, Polona Umek
---

# 0008. Write reports in LaTeX on Overleaf, synced with the repo

## Context

The three milestone reports are written jointly. The proposal (Section 5) commits to LaTeX on
Overleaf, synchronised with the repository.

## Decision

The report sources live in `reports/<milestone>/` (`proposal`, `progress`, `final`), each with a
`main.tex`. They are edited on Overleaf and synced through git. The submitted PDF of each
milestone is committed next to its sources.

## Consequences

- Overleaf's GitHub sync works on a *whole* repository, and the git integration may need a
  premium or institutional account. To be checked, see
  [Q8](../open-questions.md#q8-overleaf-sync-with-a-monorepo). [SETUP](../../SETUP.md#overleaf)
  describes the options.
- LaTeX build artefacts are ignored by git.
