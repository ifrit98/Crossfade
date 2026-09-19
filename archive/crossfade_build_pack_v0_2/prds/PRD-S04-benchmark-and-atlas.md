# PRD-S04 — Benchmark runner and scoped evaluation atlas

**Status:** Draft; fixture implementation can start after S00–S02.  
**Owner:** ML evaluation engineer.  
**Reviewers:** Technical lead, numerical/domain reviewer.  
**Dependencies:** TaskSpec, artifact/lineage records, operation SDK; S03 for real scientific comparisons.  
**Requirements:** CF-006–007, CF-011–016.  
**Source basis:** TS §10–11; proposed amendments R02, R04, R09; `04_evaluation_protocol.md`.

## Outcome

A researcher can run a declared comparison and recover the exact observations, splits, budgets, configurations, and limitations supporting its conclusion, including valid negative or inconclusive findings.

## Scope

An experiment specification, grouped split manifest, prediction-input allowlist, run scheduling over the local executor, metric aggregation, budget records, EvaluationReport, and a minimal searchable claim index. Use synthetic test runs to validate the reporting logic before real transfer data exists.

Non-goals: proving transfer, automated hypothesis invention, a sophisticated web dashboard, distributed hyperparameter optimization, mandatory MLflow integration, or a graph database.

## Experiment inputs

Each specification binds a TaskSpec version, immutable data manifests, source/target roles, train/development/test group membership, baseline/candidate variants, all pretraining exposure, normalization policy, primary metric, effect/decision rule, seed/tuning plan, and resource accounting convention.

Missing preregistration fields permit an exploratory run but block a confirmatory label. A task may explicitly declare its experiment exploratory rather than pretending that a decision rule was set in advance.

## Leakage controls

Root observation and session/group IDs propagate to all derived views. The split checker verifies that forbidden ancestor groups do not cross partitions. The feature builder can access only fields marked prediction-time available. Oracle/simulation truth is stored behind a separately tagged handle and is not passed to the deployment-path operation.

A truth-derived regime used only for post-hoc reporting is distinguished from a regime available for routing. Unlabeled test data is still test exposure; a transductive arm must be declared separately.

## Reports and claims

RunManifest represents each attempted execution. EvaluationReport combines completed and failed attempts, identifies missing arms, and reports metric denominators and exclusions. TransferClaim references valid reports and records supported, evidence-against, or inconclusive outcomes within tested scope.

An invalid or incomplete report cannot create a conclusive claim. A valid negative experiment is a successful delivery of this software slice. A crash is not evidence of negative transfer.

The initial atlas can be an index of JSON/Markdown reports and relational metadata. It must support finding claims by task, source/target direction, model version, tested conditions, and outcome. A report with no transfer comparison need not create a Mapping.

## Functional requirements

| ID | Requirement |
|---|---|
| S04-F01 | Experiment and split manifests are immutable and versioned. |
| S04-F02 | Leakage checks cover shared roots, not only duplicate file names. |
| S04-F03 | Deployment-path feature construction rejects training-only/evaluation-only fields. |
| S04-F04 | All variants record target data exposure, upstream pretraining cost, tuning, parameters, and measured resource use. |
| S04-F05 | Metric aggregation uses the declared independent grouping unit. |
| S04-F06 | Reports disclose incomplete arms, failed seeds, exclusions, and protocol deviations. |
| S04-F07 | Positive, negative, and inconclusive outcomes are representable without changing the experiment definition. |
| S04-F08 | The atlas distinguishes tested support from an unverified bounding box. |
| S04-F09 | Model-promotion rules are distinct from experiment-completion rules. |
| S04-F10 | Exported comparison reports resolve to actual runs, data, and versions. |

## Acceptance tests

**AT-01 — Root leakage:** place different derived views of one root recording in train and test. Verify the checker rejects the prohibited split.

**AT-02 — Oracle feature:** mark a target-derived regime coordinate as evaluation-only and attempt to use it for routing. Verify the deployment-path builder rejects it. A separate oracle diagnostic arm must be labeled accordingly.

**AT-03 — Locked normalization:** attempt to fit normalization using held-out groups. Verify the fit scope is invalid under the declared protocol.

**AT-04 — Positive comparison fixture:** aggregate synthetic metric records with a predefined informative positive effect and verify the report applies the configured decision rule without inventing extra significance claims.

**AT-05 — Negative comparison fixture:** aggregate a valid candidate-worse fixture and verify successful experiment completion plus an appropriate evidence-against claim.

**AT-06 — Inconclusive fixture:** aggregate a fixture that does not resolve the meaningful effect threshold and verify an inconclusive outcome, not proof of no effect.

**AT-07 — Failed arm:** inject a missing/failed required baseline arm. Verify report invalid/incomplete status and no conclusive transfer verdict.

**AT-08 — Budget accounting:** supply a pretrained candidate and scratch baseline with matched adaptation budgets but different upstream costs. Verify both adaptation and total-cost views retain those differences.

**AT-09 — Sparse support:** evaluate isolated regime cells inside a larger bounding box. Verify the atlas does not mark untested interior cells validated.

**AT-10 — Replay:** rebuild a report from persisted fixture run records and obtain the same metrics, denominators, and decision under the same report version.

## Implementation increments

Implement schemas and artificial positive/negative/inconclusive fixtures. Add split and field-access checks. Integrate local execution and budget recording. Add aggregation with a specified grouping unit and configurable decision rule. Finish with report export and a small claim index.

## Definition of done

All acceptance fixtures, a reproducible comparison report, an atlas entry for each valid scientific outcome type, and documentation of test-exposure and decision semantics. No real-world performance claim can be made until approved domain data and reference operations are supplied.
