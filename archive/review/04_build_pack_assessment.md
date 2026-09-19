# Build pack v0.2: what to keep, merge, and cut

*Written 2026-09-18. Dissects `crossfade_build_pack_v0_2/` with one question in front: is this the simplest way to get the same result? The spec doc has been updated to v0.2 to match the conclusions here.*

---

## 0. Verdict

The pack's discipline is right and its scaffolding is about twice the size it needs to be. The evaluation protocol and the acceptance tests are the best parts and cost nothing to keep, because they are rules, not code. The object model, the slice count, and the PRD template are where complexity creeps in ahead of any real task.

| Component | Verdict | Reason |
|---|---|---|
| `04_evaluation_protocol.md` | KEEP WHOLE | Firewall, splits, pairing bases, budget views, decision rule, three gates. This is discipline, not infrastructure, and it is the highest-value document in the pack |
| `05_decision_register.md` | KEEP | Twenty ADRs with a "blocks" column. Cheap, and the "blocks" column is what stops open research questions from freezing the platform |
| PRD acceptance tests (S00, S01, S02, S04) | KEEP | Concrete, testable, and mostly about refusing to fabricate. Port them into pytest as written |
| Thirteen record types | CUT TO FIVE | `Record`, `TaskSpec`, `Operation`, `Run`, `Report`. Details below |
| `CapabilityAssessment` as a stored object with a `conditional` state | CUT | It is the return value of `assess`. `conditional` is `unsupported` with a named missing parameter |
| Twelve slices | MERGE TO FOUR NOW, THREE LATER | S00+S01+S02 are one demo. S07 is a property of estimators, not a slice. S05+S06 are one charter |
| PRD template | KEEP AS CHECKLIST | Do not require every field for every slice; a three-person team will stop writing PRDs |
| Immutable store with logical-record digest, quarantine, tamper detection, interrupted-write safety, export bundles | KEEP THE REQUIREMENTS, NOT A FRAMEWORK | All of it is ~200 lines over hashed files plus SQLite. The risk is building a storage layer |
| Pack SDK with manifest, version compatibility, operation graph, conformance suite, third-pack exercise | SIMPLIFY | A pack is a Python package exposing `OPERATIONS`. One integer `core_api_version`. One parametrized pytest. No discovery, no graph |
| Two fixture packs for T0 | KEEP, BUT MAKE THE THIRD PACK REAL | The summary-only pack tests the bypass path and is cheap. The third pack should be the sonar simulation pack, not another toy |
| Reason-code vocabulary for preflight | DEFER | Free strings plus `supported/unsupported/unknown` until three real operations exist and the codes fall out of them |
| Five state dimensions on results | KEEP | Cheap, and the alternative (one Boolean) was the review's most concrete catch |
| "No shared code" replaced by documented independence | KEEP BOTH | Per the referee response |
| Missing: an S03 PRD, a data manifest, a simulator choice | ADD FIRST | These are the critical path and the pack does not write them |

---

## 1. The object model

The amendments define `ArtifactRef`, `Observation`, `Representation`, `AnchorEstimate`, `TaskSpec`, `OperationSpec`, `CapabilityAssessment`, `Result`, `RunManifest`, `EvaluationReport`, `TransferClaim`, `Mapping`, `Review`, plus enums for five state dimensions. Thirteen types and five enums to compute an RMS width.

From first principles, what does W0 (the T0 fixture) actually need to store?

- Something observed or derived, with a payload, a manifest, hashes, and parents. Observation, representation, anchor estimate and structured summary differ only in a `kind` tag and which optional fields are populated. **One type: `Record`.**
- A statement of what a run may see and must return. **`TaskSpec`.**
- An executable unit with preconditions. Its `assess` method returns supported/unsupported/unknown with reasons. That return value is not a stored object. **`Operation`.**
- One execution attempt, its inputs, versions, environment, status, and its result with typed states. The review splits `RunManifest` from `Result`; they are always written together and read together. **One type: `Run`.**
- One declared comparison over runs, with splits, metrics, budgets, validity, and what it supports. `EvaluationReport`, `TransferClaim` and `Mapping` are three views of the same experiment. A claim is a field of a report. A mapping is a claim with `implemented = true`. **One type: `Report`.**
- `Review` is a comment on any of the above, and for v0.2 it is a text field with a `kind` tag. It becomes its own type when someone builds a review UI.

Five types. The information content is identical to the review's thirteen. What is lost is the ability to store a claim without its report or a manifest without its result, and that loss is desirable.

The `conditional` assessment state deserves its own note. The review's flow is: assess returns conditional with unmet conditions, the user supplies a versioned assumption, the run cites it. That is a small state machine with an authorization step. The same outcome with no state machine: an operation declares its required parameters, including assumptions like `assume_wssus: bool`. If the TaskSpec supplies them, assess returns supported and the run records the parameters. If not, assess returns unsupported and names the missing parameter. Assumptions are just parameters that happen to be physical claims.

---

## 2. The storage layer

PRD-S01 asks for content hashing, a separate logical-record digest, metadata revisions with lineage, quarantine status, tamper detection, interrupted-write safety, export bundles, offline replay, and separate acquisition and ingestion times. Every requirement is right. The question is what it costs.

| Requirement | Simplest implementation | Lines |
|---|---|---|
| Immutable payloads | Write to `store/<sha256>` via temp file and atomic rename; no update API exists | 20 |
| Byte hash and manifest hash | `hashlib.sha256` over bytes; over canonical JSON of the manifest | 15 |
| Revisions with lineage | New record with `parents=[old_id]`; old record untouched | 10 |
| Quarantine | `validation_state` field set at ingest by a pint check | 30 |
| Tamper detection | Recompute hash on read, raise on mismatch | 10 |
| Interrupted-write safety | The atomic rename above; run rows written only after outputs exist | 15 |
| Export | `tar` the store directory plus a SQLite dump | 20 |
| Index | SQLite via stdlib `sqlite3`, three tables: records, runs, reports | 60 |

Roughly 200 lines, most of it the SQLite schema. The tech-debt risk is not that these requirements are wrong. It is that an engineer reads the PRD and builds a `Store` abstract base class with three backends. One backend, files plus SQLite, until concurrency exists. The review agrees with this in ADR-014 and ADR-015; the PRD's language just makes it sound bigger than it is.

Arrays go through xarray to zarr. Zarr is chunked and content-addressable enough for this purpose; hashing the zarr directory's chunk files gives the byte hash. Structured summaries are JSON. Units are checked at ingest with pint. That is the whole array story.

---

## 3. The pack SDK

PRD-S02 asks for a manifest with name, version, compatible core versions, operation ids, schemas, assumptions, transformations, fixtures, dependency references and resource needs; an OperationSpec with input contract, capabilities, output contract, diagnostics, determinism and failure semantics; an operation graph persisted with the run; a conformance suite; and a documented third-pack integration exercise.

The simplest thing with the same guarantees:

```
# packs/sonar_sim/__init__.py
CORE_API_VERSION = 1
OPERATIONS = [beamform_stft, cepstral_arrivals, ray_blind_deconv]

# each operation is a class with:
#   op_id, version, preconditions: list[str], params_schema: pydantic model
#   assess(task, record) -> Assessment(status, reasons, missing)
#   run(task, record, params) -> Run
```

Registration is a list of import paths in `crossfade.toml`. Version compatibility is one integer compared at import. The "operation graph" is the list of ops a task ran, in order, stored on the `Run`; there is no DAG engine. Conformance is one `pytest` file parametrized over every registered pack, asserting that each op's `assess` refuses a record missing each declared precondition, and that `run` on the pack's golden fixture reproduces its stored answer.

That is the whole SDK. It grows when a real pack needs something it does not have, and not before.

---

## 4. The slices

Twelve slices, four with PRDs. From first principles, what are the distinct user-visible deliverables?

1. **A workbench that can ingest, compute, replay, and refuse.** S00, S01 and S02 are all tested by the same T0 demo; the pack itself says to build them together. One slice.
2. **A real estimate of a real quantity with a benchmark around it.** S03 and S04. S04's fixture version can start early, but a benchmark runner with only synthetic metrics is a unit test, not a deliverable.
3. **A second domain and a transfer trial.** S05 (SSL arm), S06 (transfer trial), S07 (uncertainty). Uncertainty is a property of every estimator in slices 2 and 3, not a slice; shipping an estimator without it contradicts the spec. S05 and S06 are two arms of one preregistered charter.
4. **An output-only adapter.** S08, parallel, independent of transfer.
5. **Later:** routing ablation (S09), explanations (S10), fusion (S11). Each waits for a reason to exist.

Four now, three later. The spec's section 11 now reads this way.

The missing slice is the one the pack could not write: S03's target quantity. The pack correctly says it needs domain sign-off. The mistake is sequencing everything else ahead of it. The referee response proposed RMS delay spread and resolvable-arrival count from simulated beam time series, and the spec's section 12 puts that question first.

---

## 5. The PRD template and the PRDs

The template has ten sections and a research addendum with twelve more fields. For a slice like W0 that is fine once. For a three-person team writing seven of them it is a tax. Keep it as a checklist: a PRD includes the sections that apply, and a reviewer asks about the ones missing.

The four PRDs themselves are good, and specifically their acceptance tests are good. S00's AT-01 through AT-06, S01's AT-01 through AT-09, S02's AT-01 through AT-09, and S04's AT-01 through AT-10 should be ported to pytest names as written. They are mostly tests of refusal: refuse to guess units, refuse to fabricate a full-grid anchor, refuse a C3 label without a source reference, refuse a split that leaks a root, refuse to pass an unavailable forward check. That is the right thing to test first.

Two PRD details to change:

- S02 AT-08 (conditional request, supply an assumption, run cites it) becomes: request with a missing parameter is unsupported and names it; request with the parameter supplied runs and records it. Same guarantee, no state machine.
- S04's "minimal searchable claim index" is a SQLite table with five columns. The PRD's language should say so, or someone will reach for a search service.

---

## 6. What the pack does not contain

- **No S03 PRD.** The first real task. Critical path.
- **No data manifest.** Which public datasets, which fields, which truth. ADR-020 names this as open and blocking the reality gate, correctly. It should also be named as blocking W2's design, since the pairing protocol depends on what truth exists.
- **No simulator choice.** The evaluation protocol's independence rule cannot be applied until two generators are named.
- **No estimate of size.** Nothing in the pack says how big W0 is. The spec now says roughly 1500 lines including tests for W0, and that estimate is the check against scope creep: if W0 passes 3000 lines, something became a framework.

---

## 7. The one-sentence rule for the build

If a component can be a Pydantic model, a function, or a pytest, it is not a service, a base class, a plugin system, or a state machine. Every requirement in the pack survives that rule. Most of the pack's apparent size does not.
