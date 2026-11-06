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
| **`B(f)`** | Resources unavailable to the operation affected by modeled fault `f`. |
| **Resource check** | An arc guard evaluated when the corresponding operation starts. |
| **`s0`** | Initial state (machine off, cold, full). See [state](state.md). |
| **`sh`**, home state | Powered on, no order, empty brew unit and cup, and no modeled fault. |
| **Home marking** | A marking reachable from every reachable marking of the net. |
| **One active drink** | The `drink_done` permit prevents a second order until completion. |
| **`Ng`** | Capacity of the grounds container (number of pucks). |
| **P-invariant** | Weighting of places whose weighted token sum stays constant under every firing. Used to prove boundedness and mutual exclusion. |
| **Reachability graph** | Graph of all markings reachable from the initial marking. Finite here because all counters are bounded. |
| **Inhibitor arc** | Arc that enables a transition only when a place is *empty*. Used to model faults blocking transitions. |
| **Policy** | A priority order on `E_con ∩ EF(s)` that the controller uses to resolve conflicts. |
