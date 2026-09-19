# Crossfade — Formalization and Build Pack v0.2

**Date:** September 17, 2026  
**Status:** Proposed amendments and draft implementation requirements; not an approved replacement for the uploaded specification.  
**Basis:** `Untitled.md` (Crossfade Technical Spec), `synthesis.md` (Refereeing Plan 1 and Plan 2), and the supplied conversation transcript. See `sources.md` and `source_manifest.json`.

## Recommendation

Begin the evidence, capability, task-contract, and experiment-runner slices now. Keep the choice of a universal anchor, regime-routed mixture of experts, and positive cross-domain transfer as research decisions rather than prerequisites for the workbench.

Retain the project's wave-propagation focus, existing-processing-chain boundary, domain packs, shared/private research direction, provenance, and negative-result atlas. The amendments change the strength of particular requirements, not the scientific objective.

## Contents

| Document | Purpose |
|---|---|
| `01_architecture_review.md` | Source-grounded assessment and the changes needed before implementation. |
| `02_contract_amendments.md` | Proposed v0.2 interfaces, states, execution paths, and numbered requirements. |
| `03_slice_plan.md` | Twelve vertical slices, dependencies, deliverables, and promotion gates. |
| `04_evaluation_protocol.md` | Leakage controls, hypotheses, comparisons, and scientific decision rules. |
| `05_decision_register.md` | Proposed architecture decisions and unresolved decisions with limited blocking scope. |
| `prds/PRD-S00-task-and-fixture.md` | First task contract and acceptance fixture. |
| `prds/PRD-S01-evidence-and-replay.md` | Immutable evidence, semantic validation, and reproducible execution. |
| `prds/PRD-S02-pack-and-preflight.md` | Domain-pack SDK and capability-aware operation planning. |
| `prds/PRD-S04-benchmark-and-atlas.md` | Reproducible comparisons and a minimal evaluation atlas. |
| `prd_template.md` | Template for subsequent engineering PRDs and research charters. |
| `sources.md` | Source locations and scope of external checks. |
| `source_manifest.json` | Checksums of the unchanged uploaded source files. |

## Suggested first implementation sequence

Adopt the proposed S00 task/result semantics, implement S01 and S02 together against the small fixture, and add S04 before evaluating learned transfer. S03 supplies approved domain-specific reference operations once its task and data dependencies are settled. An output-only adapter can proceed independently of successful transfer.

The first demonstration is deliberately small: ingest a supplied profile, calculate a declared descriptor, preserve its units and lineage, reproduce the result, and reject an unsupported request on a summary-only input. This is an engineering test, not a cross-domain scientific result.

## Reading the requirements

“MUST” and “SHALL” in this package describe **proposed** implementation contracts. They do not establish that any scientific hypothesis is true. Proposed defaults are identified as such; unavailable datasets, domain expertise, empirical thresholds, and model-performance evidence have not been invented.

The four detailed PRDs are starter specifications. Later slices are scoped cards pending the dependencies identified in the plan. No model has been trained, simulator integrated, production system connected, or performance benchmark executed as part of this review. The source files have not been modified.
