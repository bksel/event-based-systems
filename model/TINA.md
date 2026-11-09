# Setting up Tina

The Petri net is drawn and analysed with **Tina 4.0.0** (TIme petri Net Analyzer, LAAS-CNRS),
as decided in [ADR 0007](../docs/decisions/0007-petri-net-analysis-tool.md). The net is
`model.ndr`, in Tina's `.ndr` format.

Tina is a set of separate programs:

| Program | Use |
|---|---|
| `nd` | Graphical editor (NetDraw). Opens and saves `.ndr` files and runs the other tools from its menus |
| `tina` | Builds the reachability graph and reports boundedness, liveness and deadlocks |
| `sift` | Faster reachability check, e.g. stop at the first deadlock |
| `struct` | Structural analysis: P- and T-semiflows (invariants) |
| `selt` | LTL model checker on graphs produced by `tina` |

No registration is needed. Only 64-bit builds exist.

## 1. Install

Download from <https://projects.laas.fr/tina/download.php>. Take the **regular** build, not
the "large" one.

### Linux

File: `tina-4.0.0-amd64-linux.tgz` (or `arm64` on ARM machines).

```sh
mkdir -p ~/.local/opt
tar -xzf ~/Downloads/tina-4.0.0-amd64-linux.tgz -C ~/.local/opt
```

Add the `bin` directory to `PATH`:

```sh
# bash / zsh: add to ~/.bashrc or ~/.zshrc
export PATH="$HOME/.local/opt/tina-4.0.0/bin:$PATH"

# fish
fish_add_path ~/.local/opt/tina-4.0.0/bin
```

Open a new terminal afterwards.

### Windows

File: `tina-4.0.0-amd64-mswin.zip`.

1. Unpack it, e.g. to `C:\tools\` so that you get `C:\tools\tina-4.0.0\bin\`.
2. Add that `bin` folder to `PATH`. In PowerShell:

   ```powershell
   $bin = "C:\tools\tina-4.0.0\bin"
   [Environment]::SetEnvironmentVariable("Path", "$env:Path;$bin", "User")
   ```

   Or use *Settings → System → About → Advanced system settings → Environment Variables*.
3. Open a new terminal.

You can also start `nd.exe` by double-clicking it in the `bin` folder.

### macOS

File: `tina-4.0.0-arm64-darwin.dmg` on Apple Silicon (macOS 13 or later), or
`tina-4.0.0-amd64-darwin.dmg` on Intel Macs (macOS 10.14 or later).

1. Open the `.dmg` and drag `nd.app` into *Applications*.
2. The app is not signed, so macOS may refuse to start it. Right-click `nd.app` → *Open* and
   confirm, or allow it in *System Settings → Privacy & Security*.
3. Use light mode. `nd` does not support dark mode yet.
4. The command-line tools are inside the app. Add them to `PATH` in `~/.zshrc`:

   ```sh
   export PATH="/Applications/nd.app/Contents/MacOS/bin:$PATH"
   ```

## 2. Check the installation

From the repository root:

```sh
tina -p model/model.ndr
```

`-p` only parses the net. A good net prints `parsed net model`, the number of places,
transitions and arcs, and exits with status 0. Any `bad line N` message means the file has an
error that Tina skips. The analysis results are then wrong or empty.

## 3. Edit the net

```sh
nd model/model.ndr
```

- `nd` expects a 3-button mouse. The middle button is **Shift + right click**. *Help → nd help*
  lists the mouse bindings.
- Save as `.ndr` (the default). It is a text format, so changes show up in `git diff`.
- **Inhibitor arcs go from a place to a transition.** In the file they look like
  `e <place> <transition> ?-1 n`. Tina rejects an arc written the other way round.
- Use the event names from the [event catalogue](../docs/domain/events.md) in transition
  labels, so traces from the net can be compared with the simulator
  ([ADR 0003](../docs/decisions/0003-python-discrete-event-simulator.md)).

### Automatic layout

When the drawing gets messy, let the computer place the nodes. Close `nd` first:

```sh
just layout                      # model/model.ndr, in place
uv run python tools/ndrlayout.py model/model.ndr -o laid.ndr --svg laid.svg   # try it first
```

This uses a force-directed layout, the same idea as Obsidian's graph view. Arcs pull nodes
together, nodes push each other apart, and a weak gravity keeps the net compact, so connected
parts of the net end up close together. Arcs stay straight, except where that would be
unreadable. Two arcs between the same nodes bow apart, and an arc that would cross another node
curves around it. Only positions and arc shapes change: the places, transitions, arcs and
markings stay exactly the same. `--svg` writes a preview you can open in a browser.
`--charge` (more negative means more spread out), `--gravity` and `--link-distance` tune it,
and `--no-curves` keeps the arcs as they are.

A curved arc is stored as `e <from> <angle> <radius> <to> <angle> <radius> <weight> n`: one
control point near each end. The angle is a fraction of a turn, anticlockwise from "right"
(0.25 is up), and the radius is in pixels.

## 4. Analyse

Always run `tina -p` first. Then:

```sh
mkdir -p model/analysis

# Reachability graph, with a limit on the number of states.
# The summary at the end says whether the net is bounded, live and reversible (home state).
tina -R -c 200000 model/model.ndr model/analysis/reachability.txt

# Stop at the first deadlock (L2), or report the number of states if there is none.
sift -dead model/model.ndr

# P-invariants (conservation of tokens). "not invariant" means some places are not covered.
struct -P model/model.ndr
```

- Always set a limit with `-c`. On an unbounded net, `tina -R` otherwise never finishes. If it
  reports `class limit reached` or `possibly bounded`, the graph is incomplete, and nothing it
  says about deadlocks or home states counts as proof.
- `tina -C` (coverability graph) ignores inhibitor arcs. It prints a warning when it does this.
  Don't use it to prove boundedness of our net.
- `man tina`, `man struct` and `man sift` explain the options. The text versions are in the Tina
  `doc/txt` folder.
- Commit the results used in the reports to `model/analysis/` as text, together with the exact
  command that produced them.
