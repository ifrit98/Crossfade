# Proposed architecture decision register

All defaults below are proposals. “Open” identifies a decision not settled by the uploaded material. Open research decisions block only the dependent scientific slices, not the entire platform.

| ID | Decision | Proposed default | Status | Blocks |
|---|---|---|---|---|
| ADR-001 | Product unit | Capability-aware task execution with auditable evidence; transfer is a measured extension. | Proposed | S00 semantics |
| ADR-002 | Anchor interface | Tagged family with optional field payload and descriptor-only estimates. | Proposed | S02–S03 |
| ADR-003 | Execution topology | Rule-based operation DAG, with summary-only bypass. | Proposed | S02 |
| ADR-004 | Capability model | Explicit preconditions; C0–C3 retained only as summaries. | Proposed | S02 |
| ADR-005 | Scientific task | T0 is a deterministic contract fixture; E1/E2 target quantity chosen separately. | T0 proposed; E1/E2 open | S03, S05–S07 |
| ADR-006 | Reference truth | Versioned measured or simulated reference with limitations; estimated anchors are pseudo-labels. | Proposed; actual source open | S03, S06 |
| ADR-007 | Regime semantics | Task-scoped, nullable, uncertainty/provenance-bearing; oracle values segregated. | Proposed | S04, S06 |
| ADR-008 | First scientific domains | Preserve sonar/HF objective; approve any lab substitute only as a portability pilot. | Open | Domain-specific S03/S06 |
| ADR-009 | First learned architecture | Simple baseline ladder and dense shared/private first; routing optional. | Proposed | S05, S09 |
| ADR-010 | Self-supervised start | Small trial may overlap contract work once splits/transforms are frozen. | Proposed | S05 |
| ADR-011 | Uncertainty | Typed method-specific objects, including unavailable/not-applicable. | Proposed | S00, S07 |
| ADR-012 | Forward checks | Optional capabilities with explicit unavailable status; no invented forward model. | Proposed | S02, S07 |
| ADR-013 | Atlas model | Runs -> evaluation reports -> scoped claims; Mapping is not every experiment. | Proposed | S04 |
| ADR-014 | Persistence | Local artifact store and embedded metadata database for initial fixture; replaceable interfaces. | Proposed | S01 |
| ADR-015 | Shared deployment | Choose shared database/object-store backends only after concurrency and environment needs are known. | Open, nonblocking | Later deployment |
| ADR-016 | Integration sequence | Output-only integration can proceed without successful transfer; no unvalidated augmentation. | Proposed | S08 |
| ADR-017 | Quantitative fusion | Separate association/dependence contract; default to comparison only. | Proposed | S11 |
| ADR-018 | LLM authority | Read records, write reviewable drafts; no authority over numeric results or claim verdicts. | Proposed | S10 |
| ADR-019 | Acceptance economics | Adaptation-budget and total-cost comparisons reported separately. | Proposed | S04–S06 |
| ADR-020 | Evidence availability | Identify actual datasets, permissions, fields, partitions, reference truth, and environment coverage before reality claims. | Open | S03/S06 reality gate |

## Mathematical sign-off required before scientific estimator implementation

The domain owner and numerical reviewer should approve each representation's definition, convention, normalization, units, statistical meaning, physical approximation, and numerical conformance tests. The technical spec's speed-to-scale expression and wideband criterion are not adopted here as universal executable rules. This package does not silently supply a corrected universal formula.

Review the distinction among a complex spreading function, a scattering/power statistic, an estimated impulse response, and a modal description. Document which conversions are exact, approximate, lossy, or unavailable. Keep that decision local to the relevant operation and task. [TS §2; R1]

## Decisions needed to finalize the first scientific PRD

The inputs needed are concrete, not another general architecture discussion: one target quantity, one source and target observation format, a real reference-truth source, an inference-time metadata inventory, a feasible overlap/pairing policy, and a baseline. Each belongs in TaskSpec or the data manifest.

Where those inputs are absent, implementation proceeds on T0 and the output-only fixture. No new data collection campaign, deployment environment, compute allocation, or team availability is assumed.
