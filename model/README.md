# Petri net model

`model.ndr` is the Tina 4.0 net. Place and transition labels use namespaced `snake_case`:
`namespace__name`, with `__` separating the namespace and `_` separating words within either part.
Shared recipe stages use one `grind__ready → grind__active → brew__ready → brew__active →
drink__post_brew` path; a separate drink-identity token selects the drink-specific continuation.
The canonical event names are in [the event catalogue](../docs/domain/events.md). Cappuccino
identity is retained through steaming before the shared grounds-ejection stage.

The net uses ordinary arcs and inhibitor arcs. Complementary permit places (for example,
fault/resource conditions. Grounds capacity is represented by five tokens in the bin-space place;
each ejection consumes one, and an inhibitor arc enables the bin-full fault when the place is empty.
`beans__available` is represented by four availability tokens; grinding consumes one and refill
restores four.
The boiler's stable temperatures are `boiler__cold`, `boiler__at_brew`, and `boiler__at_steam`;
the machine powers on ready with the boiler cold. Temperature changes are abstracted as direct
steps: heat cold→brew, heat brew→steam, and cool steam→brew. A water fault does not change the
boiler temperature. The model omits transient heating/cooling phases and `temp_reached` events. Separate
transitions are needed for each step because a standard place/transition net cannot branch on the
temperature-place input.

## Verification status

Descaling, tray mechanics, cup removal, brew-unit removal, order rejection, rinse, and milk
cleaning are not part of the current net. The model has been statically compared with the current
state, event, resource and property documentation. It is **not yet verified** by Tina.

The current model checks resources at operation start rather than rejecting an order based on the
complete resource set. Water, beans, milk, and bin faults have explicit failure/refill paths.
The `drink_done` permit prevents a second order while a drink is active.
- Tina 4.0 was not available in the current environment, so this file has not been opened or
  analyzed by the Tina executable. Structural and reachability claims still need Tina validation.

These items must be addressed before using reachability, P-invariant, deadlock or home-marking
results as evidence for the requirements in [Properties](../docs/requirements/properties.md).
