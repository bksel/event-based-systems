# GUI specification

Owner: BK. Status: draft for team review.

The GUI is a window on the Python simulator ([ADR 0012](../docs/decisions/0012-simulator-architecture.md)).
It lets a person act as the **user and the plant** of the coffee machine (order drinks, cause
faults, do service actions), and it shows what the **controller** does in response. It is the tool
for the demonstration and for producing traces that are checked against the Petri net.

Scope is the **reduced scope** of [ADR 0013](../docs/decisions/0013-reduce-the-model-scope.md):
no descaling, rinsing, milk cleaning, cup removal, order rejection or drip tray, and four faults.

Requirement IDs (`GUI-F…`, `GUI-NF…`) are used in issues and PRs. Priorities: **must**,
**should**, **could**.

## 1. Principles

These hold for every part of the GUI. A PR that breaks one is not merged.

1. **The GUI never changes the state.** It reads the state and injects events. All behaviour lives
   in `espresso/model.py`.
2. **The GUI only plays the user and the plant.** It can inject uncontrollable events (`E_obs`).
   Controllable events (`E_con`, e.g. `start_grind`) are chosen by the controller. They are shown
   in the event log and are never buttons.
3. **Enablement comes from the model.** A button is enabled iff the session says its event can be
   injected (`session.can_inject(e)`, which uses `feasible(s, e)`). No widget re-implements a
   rule such as "orders only when ready".
4. **Names come from the [event catalogue](../docs/domain/events.md).** Labels may be friendly
   ("Refill water"), but tooltips, the log and the code use the catalogue name (`refill_water`).
5. **Widgets talk only to the session.** They import enums from `espresso.state`,
   `espresso.events` and `espresso.drinks`, and nothing else from `espresso`.

## 2. Architecture

```text
 ┌──────────── widgets (team) ────────────┐
 │ status · machine · orders · service ·  │
 │ fault injector · event log · time bar  │
 └───────────────┬────────────────────────┘
       signals ↑ │ ↓ inject / play / step / reset
 ┌───────────────┴────────────────────────┐
 │ Session (core, BK)                     │  sim/gui/session.py
 │   Qt adapter around espresso.Simulator │
 │   clock, speed, trace export, net check│
 └───────────────┬────────────────────────┘
 ┌───────────────┴────────────────────────┐
 │ espresso: Simulator, model, controller │  sim/espresso/
 └────────────────────────────────────────┘
```

A `FakeSession` with the same interface returns canned states, so widgets can be built and tried
before the real session is finished.

### 2.1 Session interface (the contract)

Widgets are written against this interface only. Changing it needs BK's review.

```python
class Session(QObject):
    # Signals
    state_changed = Signal(object)    # State, after every fired event and after reset
    event_fired = Signal(object)      # TraceEntry(time, event, source)
    event_ignored = Signal(object)    # TraceEntry of an injected event that was not feasible
    running_changed = Signal(bool)    # play / pause
    time_changed = Signal(float)      # simulated time in seconds

    # Reading
    def state(self) -> State: ...
    def time(self) -> float: ...
    def can_inject(self, event: Event) -> bool: ...  # event is a GUI event and feasible now
    def is_running(self) -> bool: ...

    # Acting
    def inject(self, event: Event) -> None: ...  # at the current time, processed at once
    def play(self) -> None: ...
    def pause(self) -> None: ...
    def step(self) -> None: ...                  # process the next queued event
    def set_speed(self, factor: float) -> None:  # simulated s per wall-clock s; inf = max
    def reset(self, seed: int | None = None) -> None: ...

    # Results
    def trace(self) -> list[TraceEntry]: ...
    def export_trace(self, path: Path) -> None: ...  # JSONL, espresso.trace.write_jsonl
```

`GUI_EVENTS`, the events a person can inject, is defined next to the session:

| Group | Events |
|---|---|
| User | `power_on`, `order_espresso`, `order_americano`, `order_cappuccino` |
| Fault | `water_empty`, `beans_empty`, `milk_empty`, `bin_full` |
| Service | `refill_water`, `refill_beans`, `refill_milk`, `empty_bin` |

### 2.2 Time

Simulated time runs on a `QTimer` (tick about 50 ms). Each tick advances the simulator by
`tick × speed` seconds with `Simulator.run(until=…)`. Injecting while paused processes the
injected event and the controller's reaction at once, but the clock does not move. Durations are
in `espresso/params.py`.

## 3. Window layout

```text
┌───────────────────────────────────────────────────────────────────────┐
│ [▶/⏸] [Step] Speed [1× 5× 20× max]  t = 132.0 s   seed [0] [Reset]    │  time bar
├───────────────────────┬───────────────────────────┬───────────────────┤
│ STATUS                │ MACHINE                   │ EVENT LOG         │
│  PREPARING            │  boiler   BREW (→ steam)  │ 120.0 plant  ord… │
│  cappuccino · steaming│  grinder  idle            │ 120.0 ctrl   heat…│
│  faults: milk_empty   │  pump     idle            │ 165.0 plant  temp…│
│                       │  steamer  BUSY            │  …                │
│ ORDER                 │  brew unit used · cup full│                   │
│  [Espresso]           │ CONSUMABLES               │                   │
│  [Americano]          │  water ■ ok   milk □ empty│                   │
│  [Cappuccino] ⚠ milk  │  beans ▮▮▮▯   bin ▮▮▯▯▯▯  │ [Export trace]    │
├───────────────────────┴───────────────────────────┤ [Check vs net]    │
│ SERVICE  [Refill water] [Refill beans] [Refill milk] [Empty bin]       │
│ FAULTS   [water_empty] [beans_empty] [milk_empty] [bin_full]   [Power] │
└────────────────────────────────────────────────────────────────────────┘
```

The layout is a guide, not a requirement. Regions and their content are the requirements.

## 4. Functional requirements

### Status (W1)

| ID | Pri | Requirement |
|---|---|---|
| GUI-F1 | must | Show the mode `m` in capitals (`OFF`, `HEATING`, `READY`, `PREPARING`, `FAULT`, as the model defines them), with a colour per mode. An unknown mode is shown in a neutral colour, not as an error. |
| GUI-F2 | must | Show the current order: drink and recipe stage, or "no order". |
| GUI-F3 | must | Show the set of active faults `F` as a list. Several faults can be active at once. |
| GUI-F4 | should | Show whether the machine is in the home state (`is_home`). |

### Machine and consumables (W2)

| ID | Pri | Requirement |
|---|---|---|
| GUI-F5 | must | Show each resource and its state: boiler (and heating target), grinder, pump, steamer, brew unit, cup. Busy actuators stand out. |
| GUI-F6 | must | Show each consumable. Counters (grounds `g` against the bin capacity, and beans if the model counts them) are bars. Two-valued consumables (water, milk) are ok/empty indicators. |
| GUI-F7 | must | Every state is shown as text as well as colour. |

### Ordering (W3)

| ID | Pri | Requirement |
|---|---|---|
| GUI-F8 | must | Buttons for `power_on`, `order_espresso`, `order_americano`, `order_cappuccino`, each enabled iff `can_inject`. |
| GUI-F9 | should | A drink whose resources are missing is marked (e.g. "⚠ milk"), but stays orderable when the model allows it. Under ADR 0013 resources are checked when an operation starts, not when the order arrives, so the order is accepted and the operation then fails. |

### Service and fault injection (W4)

| ID | Pri | Requirement |
|---|---|---|
| GUI-F10 | must | Buttons for the four service events, each enabled iff `can_inject` (normally: its fault is active). |
| GUI-F11 | must | A fault injector with a button for each of the four faults, enabled iff `can_inject`. |
| GUI-F12 | should | The fault injector is visually separate from the user controls (it is the plant, not the user). |

### Event log (W5)

| ID | Pri | Requirement |
|---|---|---|
| GUI-F13 | must | Append every fired event: simulated time, source (`plant` / `controller`), catalogue name. Plant and controller rows look different. |
| GUI-F14 | must | Show ignored events (injected but not feasible) in a distinct style. |
| GUI-F15 | must | "Export trace" saves the run as JSONL (`export_trace`). |
| GUI-F16 | could | "Check against net" replays the trace on the Petri net and shows pass/fail and the first event that could not fire (needs core task C3). |
| GUI-F17 | could | Filter the log by source. |

### Time bar (W6)

| ID | Pri | Requirement |
|---|---|---|
| GUI-F18 | must | Play/pause, step, and the simulated time. |
| GUI-F19 | must | Speed choice: 1×, 5×, 20×, max. |
| GUI-F20 | must | Reset with a seed field. Reset clears the log. |

## 5. Non-functional requirements

| ID | Pri | Requirement |
|---|---|---|
| GUI-NF1 | must | PySide6 (already a dependency). Starts with `just gui`. |
| GUI-NF2 | must | The window stays responsive at every speed. No blocking loop in a slot. |
| GUI-NF3 | must | The same seed and the same clicks at the same simulated times give the same trace. |
| GUI-NF4 | must | `just check` passes. The session has unit tests that run without a display. |
| GUI-NF5 | must | Each widget is its own class in `sim/gui/widgets/`, takes the session in its constructor and works with both `Session` and `FakeSession`. |
| GUI-NF6 | should | Readable at 1280×720. |

## 6. Acceptance scenarios

Each scenario is checked by hand before the demo. The "check" column says what must be visible.
The exact stage sequence and what happens after a fault come from the model (core task C0), so
the details below follow it.

| # | Steps | Check |
|---|---|---|
| A1 | Start, `power_on`, play | `HEATING`, then `READY`. Orders become enabled. |
| A2 | `order_espresso`, play | The log shows the controller's heating/grinding/brewing events and their completions. Back to `READY`, `g` increases by one. |
| A3 | While A2 runs, try to order again | Order buttons are disabled until the drink is done (S6). |
| A4 | `order_americano`, then `order_cappuccino` | The americano adds hot water. The cappuccino heats to steam and steams. A later espresso heats back to brew. |
| A5 | During brewing, inject `water_empty` | The pump stops, the fault is listed, `refill_water` is enabled. After `refill_water` the machine recovers to `READY` (L3). |
| A6 | Inject `milk_empty`, then order a cappuccino | The cappuccino is accepted and fails at steaming. `refill_milk` lets it recover. Espresso is unaffected. |
| A7 | Order drinks until the bin is full | `bin_full` appears, grinding is blocked, `empty_bin` resets `g` to 0. |
| A8 | Reset with seed 0, repeat A1–A2 twice, export both traces | The two files are identical (GUI-NF3). |
| A9 | Export the trace of A1–A7, run the net check | Every event fires in the net (needs C3). |

## 7. Work breakdown

Core tasks come first, because the widgets depend on them. C2 lets widget work start before C1
is done.

| Task | What | Owner | Needs |
|---|---|---|---|
| C0 | Reduce the simulator to ADR 0013: events, drinks, model, tests, and the KB pages (events, state, drinks and resources) | BK | |
| C1 | `Session`: Qt adapter, clock, speed, reset, export, unit tests | BK | C0 |
| C2 | `FakeSession` and the main window with empty regions | BK | |
| C3 | Net replay: event → transition mapping in the KB, replay tool in `tools/`, used by GUI-F16 and tests | BK | C0 |
| W1 | Status panel (GUI-F1–F4) | | C2 |
| W2 | Machine and consumables panel (GUI-F5–F7) | | C2 |
| W3 | Order panel (GUI-F8–F9) | | C2 |
| W4 | Service panel and fault injector (GUI-F10–F12) | | C2 |
| W5 | Event log and export (GUI-F13–F17) | | C2 |
| W6 | Time bar (GUI-F18–F20) | | C2 |
| T1 | Run scenarios A1–A9, report problems as issues | | all |

**Definition of done for a widget task:** the widget meets its requirements with `FakeSession` and
`Session`, follows the principles in section 1, `just check` passes, and the PR has a screenshot.

Files:

```text
sim/gui/
  app.py           main window, layout (C2)
  session.py       Session, GUI_EVENTS (C1)
  fake_session.py  FakeSession (C2)
  widgets/         one module per region (W1–W6)
tools/netreplay.py replay a JSONL trace in Tina (C3)
```

## 8. Open points

| # | Question | Decided by |
|---|---|---|
| O1 | Do `beans_empty` and `bin_full` also happen on their own when the counters run out, or only from the injector? `water_empty` and `milk_empty` have no counter, so they need the injector either way. | team, with C0 |
| O2 | After a fault, does the running drink continue once the fault is cleared (the net has `*_restart` transitions), or is it dropped? The GUI only shows what the model does. | team, with C0 |
| O3 | Net transitions without a simulator event (`OE__espresso_done`, `OE__americano_done`, `OE__cappucino_done`, `CE__cup_empty`, `CE__cooling_to_brew`): add events to the model, or treat them as silent in the replay? | team, with C3 |
| O4 | The net labels `power_on`, the orders and the refills as `CE__…` (controllable), the catalogue as `E_obs`. Which one is right should be settled before the M2 report. | team |

## Appendix A. Draft event → transition mapping

For C3. To be verified against `model/model.ndr`, and moved to the KB once agreed.

| Simulator event | Net transition |
|---|---|
| `power_on` | `CE__power__on` |
| `order_espresso` / `order_americano` / `order_cappuccino` | `CE__order_espresso` / `CE__order_americano` / `CE_order_cappucino` |
| `heat_to_brew` / `heat_to_steam` | `CE__heating_to_brew` / `CE__heating_to_steam` |
| `temp_reached` | `heating_to_brew_end` or `heating_to_steam_end`, by the heating target |
| `start_grind` / `grind_done` | `CE__grind__start` / `OE__grind__end` |
| `start_brew` / `brew_done` | `CE__brewing_start` / `OE__brewing_end` |
| `add_hot_water` / `hot_water_done` | `CE__add_hot_woter` / (none, see O3) |
| `start_steam` / `steam_done` | `CE__steam_start` / `OE__steam_end` |
| `eject_grounds` | `CE__eject_grounds` |
| `water_empty` / `beans_empty` / `milk_empty` / `bin_full` | `OE__water_empty` / `OE__beans_empty` / `OE_mile_empty` / `OE__bin_full` |
| `refill_water` / `refill_beans` / `refill_milk` / `empty_bin` | `CE__water_refill` / `CE__beans_refill` / `CE_milk_refill` / `CE__empty_bin` |
| (none) | `OE__grind__fail`, `OE__brewing_fail`, `OE_steam_fail` and the matching `*_restart`: depends on O2 |

The net and the simulator may order grinding and heating differently: the simulator allows
grinding during heating (conflict C2). The replay must accept every order the net allows, so
this is checked in C3.
