---
status: accepted
date: 2026-10-20
deciders: Bartosz Ksel, Krzysztof Pogoda, Maciej Smolarz, Polona Umek
---

# 0002. Use Petri nets as the modelling formalism

## Context

The machine has several resources that work concurrently (heating while grinding), shared
resources (one boiler, one hydraulic path), bounded counters (grounds container, descaling) and
faults that can be active together. We must prove safety and recoverability
([properties](../requirements/properties.md)).

## Options considered

1. **Finite automaton**: simple semantics, but needs the explicit product of all component states.
   Concurrent faults blow up the state space and are hard to write down.
2. **Petri net**: resources are places with tokens (the grounds container is a place with `Ng`
   tokens). Concurrency comes for free. Faults are places with inhibitor arcs. There are standard
   analyses for boundedness, deadlock freedom and home markings.

## Decision

We model the machine as a Petri net (proposal Section 2.7, refs: Murata 1989; Cassandras &
Lafortune 2021). `next_state(s, e)` is the net's firing rule.

## Consequences

- Inhibitor arcs make some analyses undecidable in general. Our net is bounded, so the
  reachability graph is finite and the analysis is still possible.
- The simulator must implement the same semantics as the net. See
  [ADR 0003](0003-python-discrete-event-simulator.md).
