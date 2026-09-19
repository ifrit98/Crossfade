# PRD-S01 — Immutable evidence and replay

**Status:** Draft, ready for implementation planning after S00 semantics are adopted.  
**Owner:** Platform engineer.  
**Reviewers:** Technical lead and numerical reviewer.  
**Dependencies:** S00 fixtures and schema conventions.  
**Requirements:** CF-001–003, CF-011–012.  
**Source basis:** TS §§4–5, 11; proposed amendments R08 and R10.

## Outcome

A researcher can import an observation, execute a declared operation, inspect everything that produced its result, and replay the run without manually reconstructing the environment or preprocessing choices.

## Scope

An immutable artifact store, a versioned semantic manifest, minimal metadata/run persistence, a local worker execution record, export/replay, and command/API operations sufficient for T0. Store arrays and structured C0 records. Keep the storage API independent of the initial local backend.

Non-goals: streaming ingest, multi-tenant service, external account integration, model training, graph database, enterprise ontology, and unattended execution of untrusted packs.

## Record identity

Store a byte checksum for each artifact and a distinct logical-record digest covering the canonical semantic manifest plus referenced payload checksums. The manifest includes interpretation version, units, coordinates, masks, and processing definitions. Two records with identical numeric bytes but different units are not scientifically interchangeable.

Metadata correction produces a successor interpretation with a lineage link; it does not edit the original imported record. Preserve acquisition time and ingestion time separately. Record clock/coordinate uncertainty when supplied; do not invent missing timing information.

Incomplete evidence can be archived with a quarantine status. Analysis eligibility is determined by S02 preflight. Archival success does not mean scientific validation succeeded.

## Functional requirements

| ID | Requirement |
|---|---|
| S01-F01 | Imports preserve original payload bytes or explicitly record any decoding/transcoding derivation. |
| S01-F02 | Content integrity and logical-record integrity are independently verifiable. |
| S01-F03 | Metadata revisions and derived views form immutable, resolvable lineage. |
| S01-F04 | Arrays and structured records have tagged payload schemas. |
| S01-F05 | Every run records task/config versions, inputs, code/pack version, environment lock, seed where applicable, output refs, and status. |
| S01-F06 | Retry/cancellation/failure attempts remain persisted and linked. |
| S01-F07 | Replay states the determinism contract: exact artifact match or numerical equivalence in a specified environment/tolerance. |
| S01-F08 | Partial writes do not create a successful completed run pointing to missing output artifacts. |
| S01-F09 | Exported bundles carry enough manifests and references to identify missing dependencies rather than silently substituting them. |
| S01-F10 | Data-owner egress labels are propagated; automatic external telemetry is disabled in the local fixture path. |

## Acceptance tests

**AT-01 — Round trip:** import a T0 array record and a C0 structured record, reopen them, and verify payload checksums and semantic fields.

**AT-02 — Semantic collision:** import identical payload bytes under seconds and milliseconds. Verify that byte checksums may match but logical-record identities differ.

**AT-03 — Revision:** correct a unit annotation by creating a successor record. Verify the original remains unchanged and both interpretation histories are queryable.

**AT-04 — Tamper detection:** alter an archived test payload and verify integrity checks refuse trusted replay.

**AT-05 — Successful replay:** rerun the golden T0 record using the recorded pinned environment/config. Verify the same scientific output within the declared tolerance, and distinguish replay attempt IDs from content identity.

**AT-06 — Failure preservation:** inject a worker failure after input validation. Verify no successful result is published, the failed attempt is retained, and a retry creates a linked new attempt.

**AT-07 — Interrupted write:** interrupt output publication. Verify uncommitted artifacts cannot be mistaken for a completed scientific result.

**AT-08 — Incomplete import:** ingest a payload with missing physical metadata. Verify archival success plus quarantine/analysis-ineligible status; no inferred units are added automatically.

**AT-09 — Offline fixture:** execute and replay the fixture without network access, assuming dependencies were previously installed. No dependency installation claim is made for an arbitrary empty machine.

## Implementation increments

Implement content storage and canonical manifest hashing first. Add schema validation and metadata revision semantics. Add the local run/attempt store and worker lifecycle. Then implement result publication and replay. Finish with export, integrity inspection, and fault-injection tests.

Suggested user-facing operation names are `ingest`, `inspect`, `run`, `replay`, and `export`. These are proposed interface names, not commands already implemented by this documentation package.

## Reproducibility scope

Exact bitwise determinism is required only where the operation promises it. Numerical workers may promise equivalence within declared tolerances in specified environments. Record nondeterministic components and environment drift rather than claiming that matching random seeds guarantee identical learned results.

## Definition of done

Golden and corrupted fixtures, local storage implementation, metadata/run schemas, replay demonstration, fault-injection tests, and documentation of integrity boundaries. No production deployment or scientific transfer claim is part of completion.
