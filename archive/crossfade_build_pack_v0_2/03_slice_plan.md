# Vertical slice plan

Each slice must demonstrate a complete user-visible operation, not merely create one of the L0–L7 packages. These are proposed scopes and dependencies, not staffing or calendar commitments. Software completion and scientific model promotion are separate gates.

## Dependency map

S00 defines the shared task and result semantics. S01 and S02 can be developed together against those fixtures. S03 adds approved reference operations. S04 adds repeatable comparison and claim recording. S05–S07 develop and assess learned inference. S08 can integrate output-only evidence without waiting for successful transfer. S09 is an optional architecture experiment. S10 explains stable records. S11 addresses quantitative fusion separately.

| Slice | Deliverable | Dependencies | Readiness |
|---|---|---|---|
| S00 Task and fixture | Versioned TaskSpec, result states, deterministic reference fixture. | None | Detailed PRD supplied. |
| S01 Evidence and replay | Import, semantic validation, immutable lineage, replayable run. | S00 semantics | Detailed PRD supplied. |
| S02 Pack and preflight | Two independently implemented fixture packs; deterministic capability assessment. | S00; integrates with S01 | Detailed PRD supplied. |
| S03 Descriptor bridge | One approved reference operation per selected research domain; partial anchors and tests. | S01–S02; actual task/data choice | Conditional scope; pack-specific methods not yet specified. |
| S04 Benchmark and atlas | Split manifest, comparison runner, report, and scoped claim record. | S00–S02; S03 for real baseline results | Detailed PRD supplied; synthetic tests can start early. |
| S05 Self-supervised baseline | One declared pretraining method versus scratch and simple baselines. | S03–S04, approved data/splits/transforms | Research charter required. |
| S06 Transfer trial | Preregistered source-to-target comparison and learning curves. | S04–S05, pairing and regime feasibility | Research charter required; a positive result is not guaranteed. |
| S07 Uncertainty and checks | Calibrated or explicitly unvalidated uncertainties; available forward checks. | Result skeleton from S00; S03 and S04 diagnostics | Implement incrementally, not only after S06. |
| S08 Output-only integration | One read-only upstream adapter, evidence comparison, lineage warnings. | S01–S02 and Result contract | Can proceed in parallel with research. |
| S09 Conditional routing trial | Dense versus routed model ablation with true deployment-time features. | S06 baseline evidence and resource budget | Optional; not part of minimum viable workbench. |
| S10 Explanation and drafts | Cited explanations and reviewable metadata/pack drafts. | S04 or S08 stable records | Later; no numeric inference authority. |
| S11 Quantitative fusion | Declared association and dependency model with tested combination rule. | S07–S08; approved use case | Separately gated; comparison alone does not establish fusion. |

## S00 — Task and fixture

**User outcome:** an engineer can state precisely what a run is allowed to see and what it is supposed to return.

Implement Task T0 (deterministic profile-width calculation), one output-only comparison task, common statuses, and source/truth separation. Name physical dimensions and normalization explicitly. Use the fixture to settle the smallest necessary contracts.

**Acceptance:** the known profile produces the reference values; missing units and missing reference scale are distinguishable failures; summary-only input is eligible for comparison but not channel reconstruction. No performance claim about acoustic/RF transfer is created.

## S01 — Evidence and replay

**User outcome:** a researcher can import evidence, run an operation, inspect its ancestry, and reproduce the result.

Implement immutable payload storage, a semantic manifest, minimal relational metadata, content verification, versioned transformations, worker attempt records, and export/replay. Incomplete data is archived in quarantine rather than reinterpreted.

**Acceptance:** tampering is detected; unit changes change scientific record identity; a failed attempt is retained; replay agrees within a declared numerical tolerance in the pinned fixture environment.

## S02 — Pack and preflight

**User outcome:** a new domain can register a supported operation without core code branching on its name.

Implement a minimal manifest/operation SDK and deterministic capability assessor. One fixture pack supports T0; another supports only structured output comparison. Provide conformance tests reusable by later pack authors.

**Acceptance:** the second pack is added without modifying core logic; incompatible capabilities fail before worker execution; absent forward models remain explicitly unavailable; partial anchors do not require a fake full-field payload.

## S03 — Descriptor bridge

**User outcome:** an approved scientific task can run against a selected domain through a classical or otherwise established reference operation.

Define an actual descriptor, input view, reference-truth source, uncertainty, and limitations with the domain owner. Implement only the representation kind needed. Compare the direct descriptor calculation from an already supplied anchor against any proposed learned estimation route.

**Acceptance:** valid and invalid cases have documented expected behavior; truth is separate from prediction inputs; normalization and approximation tests pass; reference error is characterized rather than assumed zero.

**Blockers:** actual data manifest, task definition, source/measurement assumptions, pack-specific reference operation. The uploaded spec does not settle these details.

## S04 — Benchmark and atlas

**User outcome:** a researcher can execute a specified comparison and recover exactly what evidence supports a transfer claim.

Implement grouped splits, input allowlists, run manifests, report aggregation, per-domain metrics, budget accounting, and the minimum claim/atlas records. File-backed reports and a relational index are sufficient initially.

**Acceptance:** deliberate lineage leaks are caught; oracle features are rejected from the deployment path; a valid negative and an inconclusive outcome can complete a trial; incomplete trials cannot be labeled conclusive evidence against transfer.

## S05 — Self-supervised baseline

**User outcome:** the team learns whether a bounded amount of pretraining helps a selected task.

Choose one initial objective after the observation/transform contract is settled. Compare target scratch, target-only self-supervision, and source-domain pretraining under declared exposure and adaptation budgets. Store pretrained weights and fitted normalizers with data lineage.

**Acceptance:** the protocol is reproducible, all data exposure is reported, and the result is useful even when scratch wins. “Unlabeled” never exempts the test set from contamination rules.

## S06 — Transfer trial

**User outcome:** the team measures how transfer varies with target-data budget and conditions.

Preregister one source-target direction, primary metric, meaningful effect threshold, independent test units, and negative/shortcut controls. Pairing provenance must distinguish same-event, controlled corresponding mechanism, descriptor-matched pseudo-pair, and unpaired examples.

**Acceptance:** produce a valid comparison report and scoped claim. Frozen-encoder, few-shot adaptation, and full fine-tuning results are separated. Report oracle-regime ablations separately. Do not require mismatched-regime performance to be negative.

## S07 — Uncertainty and forward checks

**User outcome:** consumers can tell what an uncertainty means and whether its validation applies.

Select one inference method suitable for the actual task; a neural posterior is not mandatory. Implement applicability with unknown states and checks at the actual observation level. Measure both calibration and informativeness; wide intervals or total abstention are not hidden behind a single success statistic.

**Acceptance:** absent diagnostics are never passed; held-out coverage and accepted-case risk are reported with denominators; low-quality anchor estimates are propagated or the conditional approximation is disclosed.

## S08 — Output-only integration

**User outcome:** existing output can be reviewed with provenance without changing the upstream system.

Begin with a read-only file/export adapter or another interface that is actually available. Preserve upstream assertions and confidence semantics as upstream, not Crossfade-generated estimates. Add record comparison and shared-source warnings.

**Acceptance:** no writes to upstream processing; repeated views of the same observation do not inflate apparent evidence; missing calibration is visible; no unsupported numerical fusion occurs.

## S09 — Conditional routing trial

**User outcome:** the team knows whether routing earns its complexity.

Compare dense shared/private, parameter-efficient conditioning, and routed variants only as justified by the chosen baseline. Track active and total parameters, routing stability, deployment-time coordinate availability, and per-domain changes. A router receiving regime coordinates trivially depending on those coordinates is not evidence of discovering physics.

**Acceptance:** retain the simpler model unless routing improves preregistered utility without unacceptable regressions. Routing explanations are diagnostic metadata, not proof of mechanism transfer.

## S10 — Explanation and drafts

**User outcome:** a reviewer can understand a recorded result and propose metadata corrections.

Read only persisted TaskSpec, Result, EvaluationReport, and Mapping/TransferClaim records. Draft explanations, assumptions, test cases, and pack metadata. Keep human approval and scientific adjudication separate from presentation feedback.

**Acceptance:** every factual quantity traces to a record; tool permissions cannot overwrite numeric fields or verdicts; untrusted source text cannot authorize additional actions. No LoRA requirement is introduced by this slice.

## S11 — Quantitative fusion

**User outcome:** a narrowly defined set of associated results can be combined under an explicit dependence model.

Require a same-situation association contract, compatible estimands, and documented evidence/model dependencies. A combination method must have its own calibration and failure tests. Do not treat arbitrary result distributions as likelihoods.

**Acceptance:** duplicated evidence and unknown dependence produce conservative explicit behavior; disjoint lineage alone does not authorize an independence assumption. Defer this slice until its use case exists.
