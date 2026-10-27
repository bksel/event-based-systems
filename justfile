# Run `just` to list recipes.

# Windows has no `sh`; run recipes in PowerShell instead
set windows-shell := ["powershell.exe", "-NoLogo", "-Command"]

# List available recipes
default:
    @just --list

# Create .venv with Python and dev tools (run after clone and after pulling dependency changes)
setup:
    uv sync

# Run every check: knowledge base, lint, tests
check: kb lint test

# Check knowledge base links and ADRs
kb:
    uv run python tools/kbcheck.py

# Lint and check formatting
lint:
    uv run ruff check .
    uv run ruff format --check .

# Auto-fix lint issues and format code
fmt:
    uv run ruff check --fix .
    uv run ruff format .

# Run tests, e.g. `just test -k anchor`
test *args:
    uv run pytest {{args}}

# New ADR from the template, e.g. `just adr "Use TINA for analysis"`
adr title:
    uv run python tools/newdoc.py adr {{quote(title)}}

# New meeting notes (defaults to today), e.g. `just meeting 2026-11-03`
meeting date="":
    uv run python tools/newdoc.py meeting {{date}}

# New source summary for something in docs/inbox, e.g. `just source "Murata 1989"`
source title:
    uv run python tools/newdoc.py source {{quote(title)}}
