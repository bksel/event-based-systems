# Setup manual

Do this once per machine. It takes about 10 minutes.

## 1. Install the tools

You need **git**, **uv** (Python and dependency manager) and **just** (command runner). uv
downloads the right Python version itself, so you don't need to install Python.

| OS | uv | just |
|---|---|---|
| Fedora | `sudo dnf install uv` | `sudo dnf install just` |
| Ubuntu / Debian | `curl -LsSf https://astral.sh/uv/install.sh \| sh` | `sudo apt install just` (24.04+) or `uv tool install rust-just` |
| macOS | `brew install uv` | `brew install just` |
| Windows | `winget install astral-sh.uv` | `winget install Casey.Just` |

Any OS: `uv tool install rust-just` installs just through uv.

Check:

```sh
git --version
uv --version
just --version
```

**Windows:** the justfile makes `just` run recipes in PowerShell, so no POSIX shell is needed
(the error "could not find the shell / `sh`" comes from `just`, not `uv`). Also set
`git config --global core.autocrlf input` to avoid line-ending noise.

## 2. Clone and install

```sh
git clone git@github.com:bksel/event-based-systems.git
cd event-based-systems
just setup       # = uv sync: creates .venv with Python 3.12, pytest, ruff
just check       # should end with "kbcheck: OK" and all tests passing
```

If `git clone` over SSH fails, add an SSH key to GitHub
(<https://docs.github.com/en/authentication/connecting-to-github-with-ssh>) or clone over HTTPS.

## 3. Editor

Any editor works. For VS Code, recommended extensions: *Python*, *Ruff* (charliermarsh.ruff),
*markdownlint*, *LaTeX Workshop* (only if you build reports locally). Select `.venv/bin/python`
as the interpreter.

Optional: to use a free AI assistant in VS Code, see [AI-ASSISTANTS.md](AI-ASSISTANTS.md).

## 4. Daily commands

| Command | What it does |
|---|---|
| `just` | List all recipes |
| `just check` | Everything below: `kb`, `lint`, `test` |
| `just kb` | Check KB links, anchors and ADRs |
| `just lint` / `just fmt` | Check / fix code style |
| `just test` | Run tests (`just test -k name` to filter) |
| `just adr "Title"` | New ADR, added to the decisions index |
| `just meeting [date]` | New meeting notes |
| `just source "Title"` | New source summary (for a file in `docs/inbox/`) |
| `uv add <pkg>` | Add a runtime dependency (commit `pyproject.toml` and `uv.lock`) |
| `uv add --dev <pkg>` | Add a dev dependency |

## 5. Petri net tool

To be decided in [ADR 0007](docs/decisions/0007-petri-net-analysis-tool.md). Installation
instructions will be added here once the tool is chosen.

- TINA: <https://projects.laas.fr/tina/>
- PIPE: <https://pipe2.sourceforge.net/>

## Overleaf

Reports live in `reports/<milestone>/main.tex` ([ADR 0008](docs/decisions/0008-reports-in-latex-via-overleaf.md)).
Overleaf offers two ways to sync, and **both may need a premium or institutional account**. Check
whether the university provides Overleaf Professional/Commons.

1. **GitHub sync** (Menu → GitHub). Links one Overleaf project to the *whole* repository. Open it,
   then set *Main document* to `reports/progress/main.tex`. Push and pull happen through buttons
   in Overleaf. Every Overleaf user then sees the whole repo, which is acceptable.
2. **Overleaf Git bridge** (Menu → Git). The Overleaf project has its own git URL. Keep one
   Overleaf project per report and copy changes between it and `reports/<milestone>/`, either by
   hand or with `git subtree`.

Without premium: edit on Overleaf, then download the source ZIP before each milestone and commit
it to `reports/<milestone>/`. Only one person (the report owner) does this, to avoid conflicts.

Until this is settled, see [Q8](docs/open-questions.md#q8-overleaf-sync-with-a-monorepo).
