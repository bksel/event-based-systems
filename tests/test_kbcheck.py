from pathlib import Path

import pytest

import kbcheck

ADR = """---
status: accepted
date: 2026-10-20
deciders: Team
---

# {number}. Some decision
"""


def write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    write(tmp_path, "README.md", "# Repo\n\nSee [decisions](docs/decisions/README.md).\n")
    write(tmp_path, "docs/decisions/README.md", "# Decisions\n\n| [0001](0001-first.md) |\n")
    write(tmp_path, "docs/decisions/template.md", "# {{number}}. {{title}}\n")
    write(tmp_path, "docs/decisions/0001-first.md", ADR.format(number="0001"))
    return tmp_path


def messages(root: Path) -> list[str]:
    return [p.message for p in kbcheck.run(root)[0]]


def test_valid_repo_passes(repo: Path) -> None:
    assert messages(repo) == []


@pytest.mark.parametrize(
    ("heading", "slug"),
    [
        ("Events possible in a state", "events-possible-in-a-state"),
        ("2.3 EF(s) and `safe(s, e)`", "23-efs-and-safes-e"),
        ("Fault → service pairs", "fault--service-pairs"),
        ("start_brew guard", "start_brew-guard"),
        ("See [link](x.md) here", "see-link-here"),
    ],
)
def test_slugify(heading: str, slug: str) -> None:
    assert kbcheck.slugify(heading) == slug


def test_broken_file_link(repo: Path) -> None:
    write(repo, "docs/page.md", "[x](missing.md)\n")
    assert messages(repo) == ["broken link: missing.md"]


def test_anchor_checks(repo: Path) -> None:
    write(repo, "docs/a.md", '# Top\n## Same\n## Same\n<a id="custom"></a>\n')
    write(
        repo, "docs/b.md", "[ok](a.md#same-1) [ok](a.md#custom) [bad](a.md#nope) [self](#b)\n# B\n"
    )
    assert messages(repo) == ["missing anchor: a.md#nope"]


def test_code_and_external_links_ignored(repo: Path) -> None:
    text = "```\n[x](missing.md)\n```\n`[y](missing.md)` [web](https://example.com)\n"
    write(repo, "docs/page.md", text)
    assert messages(repo) == []


def test_inbox_is_ignored(repo: Path) -> None:
    write(repo, "docs/inbox/article.md", "[x](missing.md)\n")
    assert messages(repo) == []


def test_reference_links_checked(repo: Path) -> None:
    write(repo, "docs/page.md", "[x][ref]\n\n[ref]: gone.md\n")
    assert messages(repo) == ["broken link: gone.md"]


def test_adr_frontmatter(repo: Path) -> None:
    text = "---\nstatus: maybe\ndate: 20.10.2026\n---\n\n# 0001. X\n"
    write(repo, "docs/decisions/0001-first.md", text)
    assert messages(repo) == [
        "frontmatter field 'deciders' is missing or empty",
        "status 'maybe' is not one of: accepted, deprecated, proposed, rejected, superseded",
        "date '20.10.2026' is not YYYY-MM-DD",
    ]


def test_adr_missing_frontmatter(repo: Path) -> None:
    write(repo, "docs/decisions/0001-first.md", "# 0001. X\n")
    assert messages(repo) == ["missing frontmatter (--- block with status, date, deciders)"]


def test_adr_title_must_match_number(repo: Path) -> None:
    write(repo, "docs/decisions/0001-first.md", ADR.format(number="0007"))
    assert messages(repo) == ["title number 0007 != file number 0001"]


def test_adr_numbering_and_index(repo: Path) -> None:
    write(repo, "docs/decisions/0003-third.md", ADR.format(number="0003"))
    write(repo, "docs/decisions/0003-again.md", ADR.format(number="0003"))
    write(repo, "docs/decisions/Bad_Name.md", ADR.format(number="0004"))
    result = messages(repo)
    assert "ADR file name must be NNNN-kebab-case-title.md" in result
    assert "ADR number 0003 used more than once: 0003-again.md, 0003-third.md" in result
    assert "ADR numbering has gaps: 0002" in result
    assert "0003-third.md is not listed in the index" in result


def test_superseded(repo: Path) -> None:
    text = ADR.format(number="0001").replace("accepted", "superseded")
    write(repo, "docs/decisions/0001-first.md", text)
    assert messages(repo) == ["superseded ADR needs 'superseded-by: NNNN'"]

    text = text.replace("deciders: Team", "deciders: Team\nsuperseded-by: 0009")
    write(repo, "docs/decisions/0001-first.md", text)
    assert messages(repo) == ["superseded-by 0009 does not exist"]
