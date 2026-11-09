---
status: accepted
date: 2026-11-09
deciders: Bartosz Ksel, Krzysztof Pogoda
---

# 0007. Choose the Petri net analysis tool

## Context

The proposal names "TINA or PIPE" (Section 2.8). We need reachability graphs, P-invariants,
deadlock and home-marking checks ([L1, L2](../requirements/properties.md#recoverability)) on a net
with inhibitor arcs. The model files will live in `model/`.

## Options considered

1. **TINA**: supports inhibitor arcs. It builds reachability graphs with boundedness, liveness and
   reversibility summaries (`tina`), checks for deadlocks (`sift`), computes P- and T-semiflows
   (`struct`), and has an LTL model checker (`selt`). It has a graphical editor (`nd`) and
   command-line tools, and is available for Linux, Windows and macOS. Nets are saved as text
   (`.ndr`), so `git diff` shows changes.
2. **PIPE**: not evaluated in depth. The first net was already drawn in Tina's format, and Tina
   covers every analysis we need.
3. **Both**: draw in one tool and analyse in the other. Two files would have to be kept in sync,
   and nothing is gained over option 1.

## Decision

We use **Tina 4.0.0**. The net is `model/model.ndr`. Installation and usage are described in
[model/TINA.md](../../model/TINA.md).

## Consequences

- Every team member who works on the net installs Tina (see [SETUP](../../SETUP.md)).
- Analysis results used in the reports are committed as text to `model/analysis/`, together with
  the command that produced them.
- Results count as evidence only for a complete reachability graph. A run that stops at the
  `-c` state limit, or the coverability graph (`-C`, which ignores inhibitor arcs), proves
  nothing about L1 and L2.
- `tina` reports reversibility, which means the *initial* marking is a home marking. Our home
  state `sh` is not `s0` (the machine starts `off`), so checking L1 needs an extra step. The step
  will be added to [model/TINA.md](../../model/TINA.md).
