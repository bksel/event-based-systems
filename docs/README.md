# Knowledge base

The single place for what we know and what we decided. When the code, the Petri net model, or
the reports disagree with the KB, either the KB is wrong (fix it) or something else is (open an
issue).

Run `just kb` to check that links and ADRs are consistent.

## Domain model

- [System overview](domain/system-overview.md): the machine, its components and sensors, the menu
- [State](domain/state.md): the state tuple `s = (m, r, c, d, F, p)`, the initial and home states
- [Events](domain/events.md): the catalogue of observable and controllable events, fault/service pairs
- [Drinks and resources](domain/drinks-and-resources.md): `R(k)`, `B(f)`, drink availability
- [Glossary](domain/glossary.md)

## Requirements

- [Properties](requirements/properties.md): safety, recoverability and efficiency criteria, with IDs

## Decisions and open questions

- [Architecture decision records](decisions/README.md): why things are the way they are
- [Open questions](open-questions.md): things that are not decided yet

## Sources

- [Source summaries](sources/README.md): summaries of papers and articles (raw files go in
  [inbox](inbox/README.md), which is not tracked)

## Project

- [Work plan](project/workplan.md): tasks, owners, milestones
- [Meeting notes](meetings/README.md)

## Writing rules

- Use relative links (`../decisions/0002-petri-nets.md`), never absolute GitHub URLs to our own files.
- Write event and state names exactly as in the [event catalogue](domain/events.md), in `code`.
- Give requirements and open questions stable IDs (`S1`, `Q4`) and refer to them by ID.
- Record decisions as ADRs. Don't bury them in meeting notes.
