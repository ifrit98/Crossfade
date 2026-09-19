# Proposed v0.2 contract amendments

## 1. Product definition and boundaries

Crossfade is a capability-aware evidence and experiment platform for wave-propagation inference. It supports domain-owned observation models, partial channel/anchor descriptions, reusable inference components, and scoped empirical claims of transfer.

Interoperability remains independently valuable. Representation transfer is measured. Numerical fusion requires its own dependency and association model. Detection, classification, tracking, and changes to upstream processing remain outside the present build package, consistent with the technical spec's scope boundary. [TS lines 19–22, 219]

## 2. Retain L0–L7 ownership; replace the mandatory linear pipeline

The eight layer names can remain useful package boundaries. Execution is a validated operation graph, not a requirement to visit every layer.

**Output-only path:** artifact and observation -> pack validation -> imported/derived structured result -> provenance-aware comparison.

**Reference path:** observation -> capability preflight -> approved reference operation -> partial anchor/descriptors -> result -> evaluation.

**Learned path:** observation plus allowed context -> selected model -> estimate/uncertainty -> available diagnostics -> result -> evaluation.

An optional anchor may be an input, a supervision target, or an output. Its role is fixed in the TaskSpec for each experiment. L6's runner manages all paths; it is not merely a stage after L5. L7 consumes persisted records and creates drafts, never authoritative scientific fields.

The task planner is deterministic and rule-based in v0.2. An LLM is not needed to choose valid operations.

## 3. Minimal contracts

The definitions below are interface proposals, not a mandate for separate services or a database table for every nested object.

### ArtifactRef and Observation

`ArtifactRef` contains artifact ID, payload checksum, media type, storage location, byte length, and provenance/import metadata. A logical record hash additionally covers the canonical semantic manifest, including coordinates, units, masks, and interpretation version. Identical bytes with different units must not collide as equivalent scientific records.

`Observation` retains the original required semantics and adds:

- `schema_version`, `payload_ref`, `payload_kind` (array or structured record), and `manifest_hash`;
- acquisition interval, clock/reference information when known, and separately recorded ingestion time;
- `capability_summary` (C0–C3) plus explicit `capabilities`;
- validation state (eligible, quarantined, or rejected for a named operation);
- source/session/instrument grouping identifiers when known;
- data-use/egress labels supplied by the data owner, without inferring regulatory status;
- metadata revisions and lineage referencing immutable predecessor records.

Array views use named dimensions and validated coordinate/unit semantics. Structured C0 evidence need not be made into an artificial dense tensor. Missing metadata is explicit. Incomplete originals can be archived, but unsupported scientific operations remain blocked.

### TaskSpec

Required fields:

| Field | Contract |
|---|---|
| `task_id`, `version` | Stable identity and semantic version. |
| `question`, `task_kind` | Deterministic transform, estimation, prediction, or evidence comparison. |
| `input_contract`, `allowed_features` | Exactly what may be available when a prediction is made. |
| `quantities` | Definition, units, support/domain, and allowed ambiguities for each output. |
| `truth_contract` | How reference answers are obtained and their uncertainty or limitations. |
| `normalization` | Rule, fitting scope, reversible parameters, and version. |
| `regime_contract` | Relevant coordinates, provenance, missingness, and inference availability. |
| `baseline_ids`, `metrics` | Required comparisons and metric semantics. |
| `split_policy` | Unit of independence, held-out groups, and pretraining exposure rules. |
| `uncertainty_requirement` | Required kind, optional/unavailable behavior, and applicability checks. |
| `success_rule` | Engineering completion versus scientific model-promotion thresholds. |

An estimated regime coordinate may be used only with an estimator that sees permitted inference-time inputs. Oracle coordinates are separately tagged and excluded from deployment-path claims.

### DomainPack and OperationSpec

Retain the pack's vocabulary, priors, regimes, observation model, optional forward model, estimators, and tests. Add a manifest with pack version, core-contract compatibility, operation list, dependency lock reference, code revision, and fixtures.

Each operation declares input/output schemas, required capabilities, assumptions, optional diagnostics, determinism level, resource policy, and failure semantics. Numerical engines are implementations of operations; the core does not branch on domain names.

`assess(task, observation)` returns a `CapabilityAssessment`:

- `supported` with a runnable plan;
- `conditional` with explicit unmet conditions and required authorization/metadata;
- `unsupported` with missing capability or incompatible semantics;
- `unknown` when the prerequisites cannot be established.

Unknown is never converted to supported by default. A conditional assessment is not itself permission to execute.

### Representation and AnchorEstimate

Retain Representation's information-retention contract. Extend AnchorEstimate with:

| Field | Meaning |
|---|---|
| `representation_kind` | impulse-response, delay–Doppler spreading, delay–scale spreading, statistical power description, or descriptors-only; tagged and versioned. |
| `payload_ref` | Optional array/sparse representation; absent when only descriptors are available. |
| `descriptors` | Named values or estimates with units and definitions. |
| `statistical_semantics` | Realization, expectation/statistic, estimate, posterior samples, or pseudo-label. |
| `normalization` | Reference scales, sign conventions, acquisition bandwidth, and transform metadata required by that representation. |
| `identifiability` | Per-quantity status and ambiguity/equivalence information. |
| `uncertainty` | Appropriate uncertainty object, or explicit unavailable status. |
| `regime` | Coordinates with origin, uncertainty, and applicability. |
| `assumptions`, `diagnostics` | Preconditions and checks actually performed. |

The first release implements only the representation kind needed by its fixture. The enum is extensible; this proposal does not require implementing conversions among all kinds.

### Result and diagnostic states

A Result contains the task ID/version, producing run, quantity records, evidence references, assumptions, provenance, and diagnostics. Each quantity records whether it is upstream-asserted, deterministically computed, or inferred.

Do not overload one validity Boolean:

| Dimension | States |
|---|---|
| Execution | succeeded, failed, cancelled |
| Answer | complete, partial, abstained, unsupported |
| Applicability | in-scope, out-of-scope, unknown |
| Forward check | passed, failed, unavailable, not-applicable |
| Uncertainty kind | posterior, confidence interval/set, predictive interval/distribution, ensemble summary, unavailable, not-applicable |

For uncertainties, store the estimand, conditioning information, method/version, assumptions, calibration/evaluation references, and joint-dependence representation where available. A numerical point can be reported as a summary of a distribution or a deterministic computation; it must not imply a fabricated confidence level.

A forward-check record includes the checked representation, masks, residual metric, threshold and its provenance, diagnostic inputs, and any withheld observations. In-sample agreement is labeled as such, not presented as independent validation.

### RunManifest, EvaluationReport, and TransferClaim

`RunManifest` records task, inputs, split, config, code, pack, model, environment, seed, preprocessing, resources, timestamps, outputs, and outcome. Retries create linked attempts rather than overwriting failed runs.

`EvaluationReport` combines runs into a specified comparison, with denominators, uncertainty over metrics, independent grouping units, exclusions, budgets, and protocol deviations.

`TransferClaim` links evaluation reports to source/target domains, tasks, model variants, regimes actually tested, transfer direction, and limitations. Claim outcomes are supported, evidence-against, or inconclusive. Invalid evaluation is a report-quality status, not evidence against transfer.

Keep `Mapping` for an implemented or proposed correspondence. A baseline-only run need not invent a mapping. Mapping validation references TransferClaims and EvaluationReports.

## 4. Execution and storage

Proposed initial packaging is a modular Python repository with a contracts package, artifact storage interface, metadata/run store, pack SDK, operation executor, and evaluation/report modules. Use local array storage and an embedded relational database for the single-user fixture implementation. Keep storage interfaces replaceable for a shared deployment later; a database migration is not a scientific redesign.

No service mesh, graph neural network, mandatory graph database, or distributed scheduler is needed for the initial slice. PROV-compatible relationships can be represented with ordinary records and edges. A later ML lifecycle service can mirror Crossfade IDs but must not be the only repository of scientific semantics.

Isolation, authorization and egress controls apply to workers and tools. A Python pack is executable code, not safe merely because it conforms to the SDK. For the initial local release, execute only explicitly installed/trusted packs in constrained workers; do not claim that this is a complete sandbox for hostile code.

## 5. Proposed invariants and ownership

| ID | Requirement | Primary slices |
|---|---|---|
| CF-001 | Original artifacts are immutable; metadata reinterpretation creates a new record. | S01 |
| CF-002 | Scientific record identity covers payload and semantic manifest. | S01 |
| CF-003 | An analysis view has validated units, dimensions, coordinates, masks, and representation semantics. | S00–S02 |
| CF-004 | Capability tiers alone never authorize an operation. | S02 |
| CF-005 | Unsupported or unknown prerequisites produce an explicit non-success assessment. | S02 |
| CF-006 | A TaskSpec fixes allowed prediction-time inputs and evaluation truth. | S00, S04 |
| CF-007 | Training-only/oracle information cannot enter the deployment-path feature builder. | S04–S06 |
| CF-008 | Anchor payloads may be partial; no field is fabricated to satisfy a universal shape. | S02, S03 |
| CF-009 | Point, statistical, posterior, and unavailable uncertainty semantics are not conflated. | S00, S07 |
| CF-010 | Missing forward validation is never labeled passed. | S02, S07 |
| CF-011 | Every derived result resolves to immutable source and versioned operations. | S01–S04 |
| CF-012 | Failed and cancelled attempts remain auditable. | S01, S04 |
| CF-013 | All trial arms share declared split policies; test exposure is recorded. | S04–S06 |
| CF-014 | A valid negative or inconclusive trial satisfies experiment-delivery requirements. | S04, S06 |
| CF-015 | Every gain statement names a baseline, direction, scope, and resource accounting convention. | S04, S06 |
| CF-016 | Applicability can be unknown; a bounding box is not proof of full interior validation. | S04, S07 |
| CF-017 | Shared lineage and model dependency are recorded separately; unknown dependence blocks unsupported fusion. | S08, S11 |
| CF-018 | No workbench adapter modifies the upstream processing chain. | S08 |
| CF-019 | Explanation tools cannot write authoritative quantities, uncertainty, or claim verdicts. | S10 |
| CF-020 | Private-path or anchor-estimation uncertainty is propagated or its omission disclosed. | S03, S07 |

## 6. The first end-to-end contract fixture

Proposed Task T0 computes the weighted RMS width of a **supplied, explicitly defined delay-power profile**. For equal point weights at 0 and 2 milliseconds, the mean is 1 millisecond and RMS width is 1 millisecond. With an explicit reference time of 2 milliseconds, normalized width is 0.5. Values are interpreted as point weights, not bin-integrated densities; that distinction is part of the task definition.

This deliberately simple fixture checks units, normalization, metadata, replay, partial capability, and result states. It does not estimate an unknown channel, validate either target domain, or establish transfer. A second C0 fixture exercises archival and comparison while refusing a request for an unavailable complex channel.
