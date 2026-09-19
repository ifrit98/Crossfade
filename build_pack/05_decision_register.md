# 05. Decision register

Each row is a decision, its tag, its status, and the slice it blocks if open. Open research decisions block only their dependent slices.

| Id | Decision | Choice | Tag | Status | Blocks |
|---|---|---|---|---|---|
| ADR-01 | Product unit | Capability-aware task execution with an auditable ledger; transfer is a measured extension | P | Adopted | — |
| ADR-02 | Record model | Five types: `Record`, `TaskSpec`, `Operation`, `Run`, `Report` | P | Adopted | — |
| ADR-03 | Anchor | Typed family on `Record.anchor`; optional payload; descriptors as functionals of a canonical kind; canonical kind per regime box declared by the pack | P | Adopted | — |
| ADR-04 | Execution | Three paths chosen by `assess`; no planner; no DAG engine | P | Adopted | — |
| ADR-05 | Capability model | Explicit `capabilities` list plus per-op `preconditions`; C0 to C3 as labels only | G | Adopted | — |
| ADR-06 | Assumptions | Parameters with `is_assumption = True`; no `conditional` state | G | Adopted | — |
| ADR-07 | Storage | Content-hashed files plus SQLite via stdlib; zarr for arrays; JSON for structured | P | Adopted | — |
| ADR-08 | Units | pint validation at `put`; quarantine on failure | G | Adopted | — |
| ADR-09 | Pack registration | Explicit import-path list in `crossfade.toml`; one `CORE_API_VERSION` integer | G | Adopted | — |
| ADR-10 | First scientific task | RMS delay spread and resolvable-arrival count from beam time series, simulated, C3 | P | Proposed, awaiting sonar lead | W1 |
| ADR-11 | W1 simulator | In-house image-source isovelocity waveguide (Pekeris) for exact arrival truth; refraction-capable code as a second generator later | P | Proposed, awaiting sonar lead | W1 |
| ADR-12 | Truth | Exact from the simulator's arrival list in W1; estimated anchors are `pseudo_label` everywhere | G | Adopted | — |
| ADR-13 | Regime coordinates | Task-scoped, provenance-bearing, nullable, with availability class; per-descriptor matching | G for fields, H for matching | Adopted | — |
| ADR-14 | First learned arm | Dense shared/private with adapters, after ladder arms 1 to 5; routing is arm 7 and optional | P | Adopted | W2 |
| ADR-15 | SSL start | Masked modeling begins when W1's split policy is frozen and test membership hashed | G | Adopted | W2 |
| ADR-16 | Uncertainty | Typed kinds per `Result.uncertainty`; `unavailable` and `not_applicable` are legitimate; block bootstrap for classical estimators in W1 | G for typing, P for method | Adopted | — |
| ADR-17 | Forward checks | Only where a pack declares a forward model; otherwise `unavailable` | G | Adopted | — |
| ADR-18 | Atlas | `Report` holds `claims[]`; `Mapping` only for implemented correspondences; tested cells listed, never a box | G | Adopted | — |
| ADR-19 | Simulator independence | No shared physics kernel and a written independence statement, both | G | Adopted | W2 |
| ADR-20 | Integration | Output-only adapter proceeds without any transfer result; no unvalidated learned augmentation | G | Adopted | — |
| ADR-21 | Fusion | Two rules only: shared-parent results are one evidence; unknown dependence withholds combination | G | Adopted | — |
| ADR-22 | LLM authority | Reads records; writes drafts for human approval; never a quantity or verdict | G | Adopted | — |
| ADR-23 | Budgets | Adaptation and total cost reported separately; active and total parameters for sparse arms | G | Adopted | — |
| ADR-24 | Data for reality gate | Named datasets with fields and truth before any real-world claim | G | Open | W2 reality gate |
| ADR-25 | W3 target | Which existing system and which export format | P | Open | W3 |
| ADR-26 | Shared deployment | Choose shared storage and a registry only when concurrency exists | P | Open, nonblocking | — |
| ADR-27 | Size budgets | Per `00_meta_architecture.md`; overrun triggers review | G | Adopted | — |
| ADR-28 | Calendar | Dependency gates for sequencing; planning estimates kept and labeled | P | Adopted | — |

## Sign-offs required before an estimator becomes a reference operation

The sonar lead and a numerical reviewer approve, per representation: its definition, sign and normalization conventions, statistical meaning, physical approximations, and its conformance tests. The wideband sparsity criterion `TB · (v/c)` is a pack-declared threshold with a test, not core logic. Conversions between anchor kinds are tagged exact, approximate, lossy or unavailable at the operation, never globally.

## Inputs that unblock W1

One target quantity (ADR-10), one simulator simplification accepted (ADR-11), the inference-time metadata inventory for a real recording, and the classical estimators the lead already runs with their known failure regimes. These are section 12 of the spec, first block.
