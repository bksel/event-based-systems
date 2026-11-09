---
status: accepted
date: 2026-10-20
deciders: Bartosz Ksel, Krzysztof Pogoda, Maciej Smolarz, Polona Umek
---

# 0004. Three-drink menu, one drink at a time

## Context

A larger menu or several orders in parallel would grow the model without exercising new
resources.

## Decision

The menu is espresso, americano and cappuccino, which together use every resource. At most one
drink is prepared at a time (proposal Section 2).

## Consequences

- `p` holds a single order. A request queue can be added later without changing the structure of
  the model.
- Orders arriving while `m ≠ ready` are rejected (`reject_order`).
