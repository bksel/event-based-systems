---
status: accepted
date: 2026-10-26
deciders: Bartosz Ksel
---

# 0006. Plain Markdown knowledge base with an untracked inbox

## Context

We need a shared place for the domain model, requirements, decisions, meeting notes and literature
notes. It must be readable on GitHub without extra tools, and it must not fill the repository with
copyrighted PDFs.

## Options considered

1. **Plain Markdown in `docs/`**: renders on GitHub, works with any editor, can be checked by a script.
2. **Obsidian vault**: graph view and wikilinks, but wikilinks render poorly on GitHub and everyone
   needs Obsidian.
3. **MkDocs site**: nicer to browse, but adds a build step.

## Decision

Plain Markdown in `docs/` with standard relative links, plus:

- `docs/inbox/`: a local drop zone for raw articles. Its own `.gitignore` keeps everything except
  the README untracked.
- `docs/sources/`: one tracked summary per source, created with `just source`.
- `tools/kbcheck.py` (`just kb`): checks that links and anchors resolve and that ADRs are well
  formed.

## Consequences

- Raw material is not shared through git. Teammates get the citation/URL from the summary.
- Wikilinks (`[[...]]`) are not supported. Use relative links.
