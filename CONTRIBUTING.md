# Contributing

## Workflow

1. **Issue first.** Every piece of work has a GitHub issue. Use the *Task* template for T1–T8
   subtasks, *Bug* for defects, and *Decision* for anything that needs an ADR.
2. **Branch** from `main`: `<initials>/<short-topic>`, e.g. `kp/fault-places`, `ms/event-queue`.
3. **Commit** small, focused changes with messages in the imperative mood
   (`Add inhibitor arcs for overheat`). Put `#12` in the message or the PR to link the issue.
4. **Run `just check`** before pushing.
5. **Open a PR.** The template asks for the issue, a summary and a checklist. At least one other
   team member reviews it. Merge with *squash and merge*.
6. **Never push directly to `main`.**

## Knowledge base

- The KB in [`docs/`](docs/README.md) is the source of truth. If your change alters behaviour,
  events, states or requirements, update the KB in the same PR.
- Event and state names come from the [event catalogue](docs/domain/events.md). To add an event,
  add it there first.
- Refer to requirements and open questions by ID (`S3`, `L1`, `Q5`). Reference them in code
  comments and tests too, e.g. `def test_pump_needs_cup():  # S2`.
- Use relative Markdown links. `just kb` fails on broken links and anchors.

## Decisions (ADRs)

Write an ADR when a decision affects more than one task, is hard to reverse, or will be defended
in a report. Use `just adr "Title"` and see the [decisions README](docs/decisions/README.md) for
the process. Chat and meeting decisions count only once they are recorded as an ADR or an issue.

## Sources and the inbox

Put raw articles, PDFs and slides in [`docs/inbox/`](docs/inbox/README.md). They are not
tracked. Summarise them with `just source "Title"`, and commit only the summary.

## Code

- Python 3.12+. Style is enforced by ruff (`just fmt` fixes most of it).
- Tests go in `tests/`, named `test_<module>.py`.
- Dependencies only through `uv add` / `uv remove`. Always commit `uv.lock`.
