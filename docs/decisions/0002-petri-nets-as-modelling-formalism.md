---
status: accepted
date: 2026-10-20
deciders: Bartosz Ksel, Krzysztof Pogoda, Maciej Smolarz, Polona Umek
---

# 0002. Use Petri nets as the modelling formalism

## Context

The machine has several resources that work concurrently (heating while grinding), shared
resources (one boiler, one hydraulic path), a bounded grounds-container counter and faults that
can be active together. We must prove safety and recoverability
([properties](../requirements/properties.md)).

## Options considered

1. **Finite automaton**: simple semantics, but needs the explicit product of all component states.
   Concurrent faults blow up the state space and are hard to write down.
2. **Petri net**: resources are places with tokens (grounds capacity is represented by a bounded
   token count). Concurrency comes for free. Fault and resource conditions are represented by
   places and arcs. There are standard analyses for boundedness, deadlock freedom and home markings.

## Decision

We model the machine as a Petri net (proposal Section 2.7, refs: Murata 1989; Cassandras &
Lafortune 2021). `next_state(s, e)` is the net's firing rule.

## Consequences

- The model uses ordinary arcs and inhibitor arcs. Complementary permit places guard resource and
  fault conditions; an inhibitor arc tests when the grounds free-slot count reaches zero.
- The simulator must implement the same semantics as the net. See
  [ADR 0003](0003-python-discrete-event-simulator.md).
