# Petri net model

Owners: T3 (BK, KP), T4 (KP).

This folder will hold:

- the Petri net model files, in the format of the tool chosen in
  [ADR 0007](../docs/decisions/0007-petri-net-analysis-tool.md)
- exported analysis results (reachability graph statistics, P-invariants, deadlock/home-marking
  results) used in the M2 and M3 reports
- notes on how each place and transition maps to the [state](../docs/domain/state.md) and the
  [events](../docs/domain/events.md)

Suggested layout, adjust once the tool is chosen:

```
model/
  espresso.<ext>          # the full net
  variants/               # reduced nets for analysis (small Ng, Nover)
  analysis/               # tool outputs, committed as text
```


safdsfdsfdsafdsafskjfkjfds



