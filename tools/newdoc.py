"""Create knowledge base documents from templates and register them in their index.

Usage:
    python tools/newdoc.py adr "Use TINA for reachability analysis"
    python tools/newdoc.py meeting [YYYY-MM-DD]
    python tools/newdoc.py source "Murata 1989 - Petri nets properties"
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"


def slug(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")


def render(template: Path, **values: str) -> str:
    text = template.read_text(encoding="utf-8")
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", value)
    return text


def append_to_index(index: Path, line: str) -> None:
    text = index.read_text(encoding="utf-8")
    index.write_text(text.rstrip("\n") + "\n" + line + "\n", encoding="utf-8")


def create(path: Path, content: str) -> Path:
    if path.exists():
        sys.exit(f"newdoc: {path.relative_to(ROOT)} already exists")
    path.write_text(content, encoding="utf-8")
    print(f"newdoc: created {path.relative_to(ROOT)}")
    return path


def new_adr(title: str) -> None:
    folder = DOCS / "decisions"
    numbers = [int(p.name[:4]) for p in folder.glob("[0-9][0-9][0-9][0-9]-*.md")]
    number = f"{max(numbers, default=0) + 1:04d}"
    path = folder / f"{number}-{slug(title)}.md"
    today = date.today().isoformat()
    create(path, render(folder / "template.md", number=number, title=title, date=today))
    append_to_index(folder / "README.md", f"| [{number}]({path.name}) | {title} | proposed |")


def new_meeting(day: str) -> None:
    folder = DOCS / "meetings"
    path = folder / f"{day}.md"
    create(path, render(folder / "template.md", date=day))
    append_to_index(folder / "README.md", f"- [{day}]({path.name})")


def new_source(title: str) -> None:
    folder = DOCS / "sources"
    path = folder / f"{slug(title)}.md"
    today = date.today().isoformat()
    create(path, render(folder / "template.md", title=title, date=today))
    append_to_index(folder / "README.md", f"| [{title}]({path.name}) | | |")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    kinds = parser.add_subparsers(dest="kind", required=True)
    kinds.add_parser("adr").add_argument("title")
    kinds.add_parser("meeting").add_argument("date", nargs="?", default=date.today().isoformat())
    kinds.add_parser("source").add_argument("title")
    args = parser.parse_args(argv)
    if args.kind == "adr":
        new_adr(args.title)
    elif args.kind == "meeting":
        new_meeting(args.date)
    else:
        new_source(args.title)
    return 0


if __name__ == "__main__":
    sys.exit(main())
