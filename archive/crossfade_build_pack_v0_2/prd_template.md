# PRD / research charter template

## Header

ID, title, status, owner role, reviewer roles, version, source requirements, upstream dependencies, affected contracts.

## Outcome

One sentence describing the user's end-to-end action and the observable result. Do not define a slice merely as a layer or library.

## Scope and non-goals

State what is implemented, what is excluded, what is mocked, and which assumptions are provisional. For a research slice, identify the scientific claim separately from the software deliverable.

## Inputs, outputs, and states

Name the TaskSpec and schema versions. Declare inference-time fields, truth sources, capability requirements, payload semantics, normalization, uncertainty, and failure states. List new or changed contracts; do not change shared contracts implicitly.

## Functional requirements

Use stable requirement IDs with one testable obligation per requirement. Include missing data, unsupported operations, cancellation, retry, invalid records, and out-of-scope evidence. Specify who may write each record type.

## Implementation plan

List ordered increments: contract/fixture, operation implementation, persistence/execution, diagnostics, evaluation, documentation. Every increment should end with a runnable test or inspectable artifact.

## Acceptance criteria

Use Given/When/Then where practical. Distinguish deterministic unit checks, integration tests, numerical approximation tests, calibration evidence, and user review. Tie each criterion to requirement IDs.

For research: a reproducible valid negative or inconclusive result completes the experiment slice. Promotion of a model requires a different, preregistered evidence rule.

## Data and reproducibility

Data manifest, split unit, lineage, reference-truth quality, model/preprocessing versions, seeds, environment lock, determinism level, numerical tolerance, resource and exposure accounting.

## Risks and unresolved decisions

Identify the smallest slice blocked by each unresolved decision. Record the fallback. Do not mark all development blocked because the ultimate transfer claim is unproven.

## Definition of done

Tests, fixtures, documentation, report/manifests, migration notes, rollback/disable path where relevant, known limitations, and a demo that does not overstate scientific scope.

## Additional fields for a research charter

Hypothesis, primary metric and meaningful effect size, baselines, controlled budgets, permitted data exposure, independent evaluation unit, seed/tuning plan, test-lock rule, shortcut controls, statistical decision procedure, negative-result handling, and model-promotion gate.
