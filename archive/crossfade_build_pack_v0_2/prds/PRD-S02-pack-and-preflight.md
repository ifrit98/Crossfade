# PRD-S02 — Domain-pack SDK and capability preflight

**Status:** Draft, ready for engineering review.  
**Owner:** Platform/SDK engineer.  
**Reviewers:** Pack author and numerical reviewer.  
**Dependencies:** S00 contracts; integration with S01 artifacts/results.  
**Requirements:** CF-003–005, CF-008, CF-010–011.  
**Source basis:** TS §§4–7; proposed amendments R01, R03, R06.

## Outcome

A pack author can register a new domain-specific operation without editing the core, and the platform can determine whether a requested task is supported by the supplied evidence before running numerical code.

## Scope

Versioned pack manifests, explicit operation capabilities, deterministic preflight, a small operation graph, typed unsupported/unknown outcomes, fixture pack implementations, and reusable conformance tests.

Non-goals: automatic discovery or execution of arbitrary remote code, LLM planning, universal anchor conversion, scientific estimator selection by benchmark score, and production deployment of new sensing algorithms.

## Pack interface

The initial interface exposes manifest loading, input validation, task/capability assessment, supported operation enumeration, and execution of an explicitly selected approved operation. Optional model/forward-check functions are declared capabilities, not methods that must return invented defaults.

A pack manifest records name/version, compatible core schema versions, operation IDs, input/output schemas, assumptions, transformations, fixtures, code/dependency references, and data-use/resource needs. Vocabulary and extensive regime metadata are optional unless a particular task requires them.

An OperationSpec defines its input contract, required capabilities, output contract, meaningful diagnostics, and determinism/failure semantics. Operations use data refs and contexts rather than relying on undocumented process-global state.

## Capability assessment

The assessment returns supported, conditional, unsupported, or unknown, with machine-readable reasons and human-readable explanations. Suggested reasons include missing phase, unknown source reference, missing calibration, unsupported transform, incompatible units, missing normalization, unavailable observation model, and unresolved identifiability assumptions.

The exact capability vocabulary should be minimal and task-driven. C0–C3 remains a display summary; a higher tier never bypasses an unmet prerequisite.

A conditional result lists conditions; it does not silently execute. Explicitly approved assumptions, once supplied, are versioned and attached to the resulting run.

## Required fixture packs

**Profile fixture pack:** supports T0 with declared point-weight and unit semantics. It returns descriptors only and has no full complex spreading-function estimator. This must be a valid pack.

**Summary fixture pack:** supports structured output import/comparison, has no forward model and no anchor estimator, and refuses reconstruction. This must also be a valid pack.

These packs demonstrate integration extensibility, not two scientifically independent propagation models or real cross-domain transfer.

## Functional requirements

| ID | Requirement |
|---|---|
| S02-F01 | The core registers operations without conditional logic on domain names. |
| S02-F02 | Pack/core version incompatibility fails before execution. |
| S02-F03 | Preflight checks semantic and capability prerequisites, not just array shape. |
| S02-F04 | Unsupported/unknown results preserve reason codes and required missing inputs. |
| S02-F05 | A partial AnchorEstimate may omit the field payload and return named descriptors. |
| S02-F06 | Missing forward models produce unavailable diagnostics, never synthetic passed checks. |
| S02-F07 | The selected operation graph is persisted with the run; L2–L4 bypass is supported. |
| S02-F08 | Transform semantics distinguish reversible conversion, coordinate change, lossy processing, and physical intervention. |
| S02-F09 | Pack test fixtures are reusable by third-party authors under the same SDK. |
| S02-F10 | Execution is limited to trusted installed packs and respects local resource/egress policy; SDK conformance is not represented as a security sandbox. |

## Acceptance tests

**AT-01 — Extensibility:** register the summary fixture pack without editing core source. Verify its operation appears and can run on eligible evidence.

**AT-02 — False capability:** supply a record labeled C3 that lacks a task-required reference. Verify preflight refuses the operation despite the tier label.

**AT-03 — Partial anchor:** run the profile fixture pack and serialize a descriptor-only AnchorEstimate without a fabricated full-grid payload.

**AT-04 — Summary bypass:** execute comparison on the summary pack without calling any anchor, encoder, or forward-model function.

**AT-05 — Missing model:** request a forward check on a pack without a forward model. Verify unavailable state and reason, not passed or an invented default.

**AT-06 — Semantic mismatch:** offer an array with the right shape but incompatible units/profile convention. Verify preflight rejects it before numerical execution.

**AT-07 — Version mismatch:** load an incompatible manifest version. Verify a precise compatibility failure and no fallback that changes scientific interpretation.

**AT-08 — Approved condition:** begin with a conditional request, supply a versioned permitted assumption, and verify the resulting run cites that assumption. Verify no assumption is invented automatically.

**AT-09 — Conformance:** run the same SDK conformance suite against both fixture packs and include positive, unsupported, and invalid-data cases.

## Implementation increments

Define manifest and OperationSpec first. Build the two fixture packs independently against those contracts. Implement preflight and reason codes. Add operation-plan persistence and local execution integration. Finally publish pack-author documentation and conformance tests.

## Definition of done

Two fixture packs, schema/version checks, capability refusal tests, partial-anchor support, bypass demonstration, and a documented third-pack integration exercise. No choice of a universal learned architecture or full-field anchor is needed to pass.
