# Research charter fields

In addition to the PRD checklist. The deliverable is an experiment and its evidence, not a promised winning model. A valid negative or inconclusive result completes the slice.

- Hypotheses tested, by id from `03_evaluation_protocol.md` §3, per descriptor and direction.
- Arms with ladder position, pretraining source, target labels, target unlabeled exposure.
- Controlled variables and reported variables, in both budget views.
- Primary metric, independent unit, seeds.
- Effect rule: how the meaningful delta is set, the decision procedure, and the commitment to freeze it with a timestamp before the test partition is read.
- Shortcut controls: shuffled-pair, nuisance-matched, oracle-regime diagnostic, and any task-specific ones.
- Pairing basis per pair record.
- Simulator independence statement reference, when simulation is involved.
- Open inputs that block the scientific gate, separated from those that block the software.
- Promotion rule, stated even when no promotion is planned.
