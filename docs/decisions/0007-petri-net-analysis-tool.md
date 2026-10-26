---
status: proposed
date: 2026-10-26
deciders: Krzysztof Pogoda, Bartosz Ksel
---

# 0007. Choose the Petri net analysis tool

## Context

The proposal names "TINA or PIPE" (Section 2.8). We need reachability graphs, P-invariants,
deadlock and home-marking checks ([L1, L2](../requirements/properties.md#recoverability)) on a net
with inhibitor arcs. The model files will live in `model/`.

## Options considered

1. **TINA**: <!-- to evaluate: inhibitor arcs, invariants, home-state check, file format, OS support -->
2. **PIPE**: <!-- to evaluate -->
3. **Both**: draw in one, analyse in the other? <!-- cost of keeping two files in sync -->

## Decision

*Open.* See [Q7](../open-questions.md#q7-petri-net-tool).

## Consequences

<!-- e.g. file format committed to model/, how analysis results are exported for the reports -->
