# System overview

Source: project proposal, Section 1 and the introduction of Section 2.

The plant is a fully automatic espresso machine for home or small office use. We design its
**supervisory, event-based controller**, not the low-level loops (the temperature PID, motor
drives). At this level the machine is a discrete event system driven by user requests, sensor
events and service actions.

## Components (actuators)

| Component | Role | States in the model |
|---|---|---|
| Grinder | Grinds beans into the brew unit | `idle`, `busy` |
| Boiler (single) | Heats water to brew *or* steam temperature | `cold`, `brew`, `steam` |
| Water pump | Pushes water through the brew unit / hot-water outlet | `idle`, `busy` |
| Brewing unit | Holds the coffee puck. Removable by the user | `empty`, `loaded`, `used` |
| Milk pump + steam frother | Froths milk for cappuccino | `idle`, `busy` |

The single boiler and the shared hydraulic path are the main **resource conflicts**.

## Sensors

Water tank level, bean presence, milk presence, grounds container counter, drip tray level,
brewing unit presence, boiler temperature, cup presence.

## Menu

| Drink | Uses |
|---|---|
| Espresso | Grinder, brew unit, pump, boiler at brew temperature |
| Americano | Espresso plus hot water |
| Cappuccino | Espresso plus milk, with the boiler at steam temperature |

These three drinks together use every resource. At most **one drink is prepared at a time**
(see [ADR 0004](../decisions/0004-one-drink-at-a-time.md)). Full resource sets are in
[Drinks and resources](drinks-and-resources.md).

## Design goals

- **Safe**: no actuator runs in a condition that can damage the machine or hurt the user.
- **Recoverable**: after any combination of faults, the machine returns to normal operation once
  the service actions are done. It never gets stuck.
- **Efficient**: the order of operations affects preparation time and how often the boiler
  changes temperature.
- **Graceful degradation**: a fault blocks only the drinks that depend on the missing resource.

Formal versions of these goals are in [Properties](../requirements/properties.md).
