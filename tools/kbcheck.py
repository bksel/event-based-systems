"""Knowledge base consistency checker.

Checks that relative Markdown links (and their #anchors) resolve, and that the
ADRs in docs/decisions/ are well formed. Prints one ``path:line: message`` per
problem and exits with status 1 if any were found.

Usage: python tools/kbcheck.py [--root PATH]
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from urllib.parse import unquote

# Directories never scanned. docs/inbox holds untracked raw material.
EXCLUDED_DIRS = {".git", ".venv", ".ruff_cache", ".pytest_cache", "node_modules", "__pycache__"}
EXCLUDED_PATHS = {Path("docs/inbox")}

ADR_DIR = Path("docs/decisions")
ADR_INDEX = "README.md"
ADR_NON_RECORDS = {"README.md", "template.md"}
ADR_FILENAME = re.compile(r"^(\d{4})-[a-z0-9]+(?:-[a-z0-9]+)*\.md$")
ADR_TITLE = re.compile(r"^(\d{4})\.\s+\S")
ADR_STATUSES = {"proposed", "accepted", "rejected", "deprecated", "superseded"}
ADR_REQUIRED = ("status", "date", "deciders")

FENCE = re.compile(r"^\s*(```|~~~)")
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
INLINE_CODE = re.compile(r"`+[^`]*`+")
INLINE_LINK = re.compile(r"!?\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
REF_LINK = re.compile(r"^\s*\[[^\]]+\]:\s*<?(\S+?)>?(?:\s+\"[^\"]*\")?\s*$")
HTML_ID = re.compile(r"""<a\s+[^>]*(?:id|name)=["']([^"']+)["']""")
URL_SCHEME = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")


@dataclass(frozen=True)
class Problem:
    path: Path
    line: int
    message: str

    def __str__(self) -> str:
        return f"{self.path}:{self.line}: {self.message}"


@dataclass
class Document:
    path: Path
    anchors: set[str]
    links: list[tuple[int, str]]
    lines: list[str]


def slugify(heading: str) -> str:
    """Anchor GitHub generates for a heading (without duplicate suffixes)."""
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", heading)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"[^\w\- ]", "", text.strip().lower())
    return text.replace(" ", "-")


def parse(path: Path) -> Document:
    lines = path.read_text(encoding="utf-8").splitlines()
    anchors: set[str] = set()
    seen: dict[str, int] = {}
    links: list[tuple[int, str]] = []
    in_fence = False
    for number, line in enumerate(lines, start=1):
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if match := HEADING.match(line):
            slug = slugify(match.group(2))
            count = seen.get(slug, 0)
            anchors.add(slug if count == 0 else f"{slug}-{count}")
            seen[slug] = count + 1
        anchors.update(HTML_ID.findall(line))
        if match := REF_LINK.match(line):
            links.append((number, match.group(1)))
            continue
        for target in INLINE_LINK.findall(INLINE_CODE.sub("", line)):
            links.append((number, target))
    return Document(path, anchors, links, lines)


def markdown_files(root: Path) -> list[Path]:
    files = []
    for path in sorted(root.rglob("*.md")):
        relative = path.relative_to(root)
        if any(part in EXCLUDED_DIRS for part in relative.parts):
            continue
        if any(relative.is_relative_to(excluded) for excluded in EXCLUDED_PATHS):
            continue
        files.append(path)
    return files


def resolve(root: Path, source: Path, target: str) -> tuple[Path, str]:
    """Split a link target into the file it points to and its fragment."""
    path_part, _, fragment = target.partition("#")
    path_part = unquote(path_part)
    if not path_part:
        return source, fragment
    if path_part.startswith("/"):
        return (root / path_part.lstrip("/")).resolve(), fragment
    return (source.parent / path_part).resolve(), fragment


def check_links(root: Path, docs: dict[Path, Document]) -> list[Problem]:
    problems = []
    for doc in docs.values():
        rel = doc.path.relative_to(root)
        for line, target in doc.links:
            if URL_SCHEME.match(target):
                continue
            resolved, fragment = resolve(root, doc.path, target)
            if not resolved.exists():
                problems.append(Problem(rel, line, f"broken link: {target}"))
                continue
            if not fragment or resolved.suffix != ".md":
                continue
            linked = docs.get(resolved) or parse(resolved)
            if fragment not in linked.anchors:
                problems.append(Problem(rel, line, f"missing anchor: {target}"))
    return problems


def frontmatter(lines: list[str]) -> tuple[dict[str, tuple[int, str]], int] | None:
    """Flat ``key: value`` frontmatter with line numbers, and the closing line index."""
    if not lines or lines[0].strip() != "---":
        return None
    fields = {}
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return fields, index
        key, sep, value = line.partition(":")
        if sep:
            fields[key.strip()] = (index + 1, value.strip())
    return None


def check_adr(doc: Document, rel: Path, number: str) -> list[Problem]:
    parsed = frontmatter(doc.lines)
    if parsed is None:
        return [Problem(rel, 1, "missing frontmatter (--- block with status, date, deciders)")]
    fields, end = parsed
    problems = []
    for key in ADR_REQUIRED:
        if not fields.get(key, (0, ""))[1]:
            problems.append(Problem(rel, 1, f"frontmatter field '{key}' is missing or empty"))

    status_line, status = fields.get("status", (1, ""))
    if status and status not in ADR_STATUSES:
        allowed = ", ".join(sorted(ADR_STATUSES))
        problems.append(Problem(rel, status_line, f"status '{status}' is not one of: {allowed}"))

    date_line, value = fields.get("date", (1, ""))
    if value:
        try:
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
                raise ValueError
            date.fromisoformat(value)
        except ValueError:
            problems.append(Problem(rel, date_line, f"date '{value}' is not YYYY-MM-DD"))

    if status == "superseded" and "superseded-by" not in fields:
        problems.append(Problem(rel, status_line, "superseded ADR needs 'superseded-by: NNNN'"))
    if "superseded-by" in fields and status != "superseded":
        line = fields["superseded-by"][0]
        problems.append(Problem(rel, line, "'superseded-by' set but status is not 'superseded'"))

    title = next((line for line in doc.lines[end + 1 :] if line.strip()), "")
    match = ADR_TITLE.match(title.removeprefix("# ")) if title.startswith("# ") else None
    if match is None:
        problems.append(
            Problem(rel, end + 2, f"first line after frontmatter must be '# {number}. Title'")
        )
    elif match.group(1) != number:
        problems.append(
            Problem(rel, end + 2, f"title number {match.group(1)} != file number {number}")
        )
    return problems


def check_adrs(root: Path, docs: dict[Path, Document]) -> list[Problem]:
    adr_dir = root / ADR_DIR
    if not adr_dir.is_dir():
        return [Problem(ADR_DIR, 0, "ADR directory does not exist")]
    problems = []
    records: dict[str, list[Path]] = {}
    superseded_by: list[tuple[Path, int, str]] = []

    for path in sorted(adr_dir.glob("*.md")):
        rel = path.relative_to(root)
        if path.name in ADR_NON_RECORDS:
            continue
        match = ADR_FILENAME.match(path.name)
        if match is None:
            problems.append(Problem(rel, 0, "ADR file name must be NNNN-kebab-case-title.md"))
            continue
        number = match.group(1)
        records.setdefault(number, []).append(path)
        doc = docs[path.resolve()]
        problems.extend(check_adr(doc, rel, number))
        parsed = frontmatter(doc.lines)
        if parsed and "superseded-by" in parsed[0]:
            line, value = parsed[0]["superseded-by"]
            superseded_by.append((rel, line, value))

    for number, paths in records.items():
        if len(paths) > 1:
            names = ", ".join(p.name for p in paths)
            problems.append(
                Problem(ADR_DIR, 0, f"ADR number {number} used more than once: {names}")
            )

    numbers = sorted(int(n) for n in records)
    missing = sorted(set(range(1, (numbers[-1] if numbers else 0) + 1)) - set(numbers))
    if missing:
        gaps = ", ".join(f"{n:04d}" for n in missing)
        problems.append(Problem(ADR_DIR, 0, f"ADR numbering has gaps: {gaps}"))

    for rel, line, value in superseded_by:
        if value not in records:
            problems.append(Problem(rel, line, f"superseded-by {value} does not exist"))

    index_path = adr_dir / ADR_INDEX
    if not index_path.exists():
        problems.append(Problem(ADR_DIR / ADR_INDEX, 0, "ADR index is missing"))
        return problems
    index = docs[index_path.resolve()]
    indexed = {resolve(root, index.path, target)[0] for _, target in index.links}
    for paths in records.values():
        for path in paths:
            if path.resolve() not in indexed:
                problems.append(
                    Problem(ADR_DIR / ADR_INDEX, 0, f"{path.name} is not listed in the index")
                )
    return problems


def run(root: Path) -> tuple[list[Problem], int]:
    root = root.resolve()
    docs = {path.resolve(): parse(path) for path in markdown_files(root)}
    return check_links(root, docs) + check_adrs(root, docs), len(docs)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args(argv)
    problems, count = run(args.root)
    for problem in problems:
        print(problem)
    if problems:
        print(f"kbcheck: {len(problems)} problem(s) in {count} file(s)", file=sys.stderr)
        return 1
    print(f"kbcheck: OK ({count} file(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
