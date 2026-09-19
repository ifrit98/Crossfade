# 04. Slices

Four slices ship now, three wait for a reason to exist. Each is a complete user-visible operation with a demo and a test suite. Estimates are planning numbers for the funding conversation, labeled as such, and assume the sonar lead's W1 input arrives in the first two weeks. **[P]**

## Dependency map

```
W0 Workbench ──┬──▶ W1 First task ──▶ W2 Transfer charter ──▶ (later) routing ablation
               │                                          └──▶ (later) explanations
               └──▶ W3 Output-only adapter ──────────────────▶ (later) fusion
```

W0 and W3 share `Record` and `Run` and nothing else. W1 shapes the contracts alongside W0; they are specified together and W1 starts the day its quantity is confirmed. W2 depends on W1's split policy for its pretraining start and on W1's estimators for its baselines.

## The slices

| Slice | Deliverable | Gate | Estimate | Blocked by |
|---|---|---|---|---|
| W0 Workbench | Ingest a supplied profile; compute T0; preserve units and lineage; replay; refuse reconstruction on a summary record. One demo, one test suite | Delivery: all W0 acceptance tests pass offline | 2 to 3 weeks, one engineer | Nothing |
| W1 First task | Simulated beam time series from an in-house image-source waveguide; RMS delay spread and arrival count via cepstral and autocorrelation estimators; bootstrap uncertainty; bench with grouped splits and leakage checks; a report characterizing the classical estimators | Delivery and scientific: classical error characterized, not assumed zero | 4 to 6 weeks, two people | Sonar lead confirms the quantity and the simulator simplification |
| W2 Transfer charter | HF pack with an independent multimode simulator; SSL pretraining arm; dense shared/private arm; one preregistered transfer trial per descriptor with typed uncertainty | Scientific: a scoped claim, any direction | 8 to 12 weeks, two to three people | W1 split policy frozen; pairing basis chosen; independence statement written |
| W3 Output-only adapter | Read-only import of one existing system's summary export; comparison; duplicate-evidence warnings; no upstream write | Delivery | 2 to 3 weeks, parallel to W1 | Which system and which export format |
| Later: routing | Dense versus routed ablation with deploy-time features | Only after W2 shows a dense arm worth beating | Deferred | W2 result |
| Later: explanations | LLM over records; pack-metadata drafts for human approval | After W1 records are stable | Deferred | Stable `Run` and `Report` |
| Later: fusion | Numerical combination under a declared dependence model | After a use case exists | Deferred | A use case |

## What each gate refuses

- **W0:** any anonymous tensor; any record without explicit capabilities; any fabricated default for a missing unit, reference scale or convention; any assessment that coerces `unknown` to `supported`.
- **W1:** any learned-arm result without ladder arms 1 and 2; any random-window split; any oracle coordinate on the reference or learned path; any estimator without a typed uncertainty or an explicit `unavailable`.
- **W2:** any gain measured on one simulator relabeled; any missing independence statement; any pretraining before test membership is frozen; any calibration claim validated only on the training cells; any claim from an `invalid` or `incomplete` report.
- **W3:** any write to upstream processing; any duplicate evidence counted twice; any upstream confidence relabeled as a Crossfade estimate.

## Why these merges

- S00, S01 and S02 from v0.2 are tested by the same T0 demo and the v0.2 pack already says to build them together. Splitting them produced three PRDs for one fixture.
- S07 (uncertainty) is not a slice. Every estimator in W1 and W2 carries a typed uncertainty or an explicit `unavailable`; shipping one without it violates CF-08.
- S05 (SSL arm) and S06 (transfer trial) are two arms of one preregistered charter and are meaningless apart.
- S04 (bench) is inside W1 because a bench with only synthetic metric fixtures is a unit test, not a deliverable. Its synthetic fixtures are W1's first tests.

## Team

One person on packs and estimators (the sonar lead's domain), one on the core and bench, and from W2 one on models. Nothing in W0 to W3 needs more, and adding a fourth person before W2 would be spent on coordination.
