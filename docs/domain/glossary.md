# Glossary

| Term | Meaning |
|---|---|
| **DES** | Discrete event system. State changes only when events occur. |
| **`E_obs`** | Observable, uncontrollable events, produced by the user and the sensors. See [events](events.md). |
| **`E_con`** | Controllable events, chosen by the supervisor. See [events](events.md). |
| **`EF(s)`** | Set of events feasible in state `s`. |
| **`next_state(s, e)`** | Transition function. In the Petri net it is the firing rule. |
| **`safe(s, e)`** | Extra guard on controllable events that checks actuator safety conditions on top of `EF(s)`. |
| **`R(k)`** | Resources required by drink `k`. See [drinks and resources](drinks-and-resources.md). |
| **`B(f)`** | Resources disabled by fault `f`. |
| **Available drink** | A drink whose `R(k)` contains no blocked resource while `d < Nover`. |
| **`s0`** | Initial state (machine off, cold, full). See [state](state.md). |
| **`sh`**, home state | `ready`, no order, no faults. Must be reachable from every reachable state. |
| **Home marking** | A marking reachable from every reachable marking of the net. |
| **Graceful degradation** | A fault blocks only the drinks that depend on the missing resource. |
| **Partial drink** | A drink finished only in part because of a mid-drink fault, e.g. a cappuccino without milk. |
| **`Ng`** | Capacity of the grounds container (number of pucks). |
| **`Ndue`**, **`Nover`** | Descaling thresholds: warning at `Ndue`, drinks blocked at `Nover`. |
| **P-invariant** | Weighting of places whose weighted token sum stays constant under every firing. Used to prove boundedness and mutual exclusion. |
| **Reachability graph** | Graph of all markings reachable from the initial marking. Finite here because all counters are bounded. |
| **Inhibitor arc** | Arc that enables a transition only when a place is *empty*. Used to model faults blocking transitions. |
| **Policy** | A priority order on `E_con ∩ EF(s)` that the controller uses to resolve conflicts. |
