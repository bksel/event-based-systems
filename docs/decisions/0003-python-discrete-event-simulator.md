---
status: accepted
date: 2026-10-20
deciders: Bartosz Ksel, Krzysztof Pogoda, Maciej Smolarz, Polona Umek
---

# 0003. Implement plant and controller as a Python discrete event simulator

## Context

We need to demonstrate the controller live, run fault and service scenarios, and compare
prioritization policies on random orders and faults ([E1–E3, C1–C4](../requirements/properties.md#efficiency)).

## Decision

We write a discrete event simulator in Python (proposal Section 2.8):

- The **plant** generates observable events: orders, sensor events, random faults, service actions.
- The **controller** selects controllable events using `EF(s)`, `safe(s, e)` and a pluggable
  **prioritization policy**.
- A simple **GUI** with buttons for user and fault events is used for the demonstration.

## Consequences

- The internal structure of the simulator (modules, GUI toolkit, whether it executes the Petri
  net directly) is still open and belongs to T5/T6. Record it in a new ADR.
- We need a way to check that the simulator and the analysed net agree, e.g. by replaying traces
  in both.
