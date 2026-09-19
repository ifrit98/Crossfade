# 01. Contracts

Five record types. All are Pydantic v2 models serialized to JSON. Field lists are **[P]**; the invariants at the end are **[G]**. Unknown fields are rejected on load (`extra="forbid"`), so a contract change is a version bump, never a silent addition.

---

## 1. `Record`

Anything observed or derived. Observation, representation, anchor estimate and structured summary are one type distinguished by `kind`; each `kind` populates a subset of the optional fields.

```python
class Record(BaseModel):
    schema_version: int = 1
    id: str                              # "rec_" + sha256(byte_hash + manifest_hash)[:16]
    kind: Literal["observation", "representation", "anchor_estimate", "summary"]
    payload_kind: Literal["array", "structured"]
    payload_ref: str                     # "blobs/<byte_hash>"
    byte_hash: str                       # sha256 of payload bytes (zarr: sorted chunk hashes; JSON: canonical bytes)
    manifest_hash: str                   # sha256 of canonical JSON of every field except id, byte_hash, manifest_hash, ingested_at

    source_system: str
    acquired_at: datetime | None         # None is allowed and means unknown; never inferred
    ingested_at: datetime
    data_use: str | None                 # owner-supplied label; not interpreted

    capability_label: Literal["C0", "C1", "C2", "C3"]     # summary only; never authorizes
    capabilities: list[str]              # e.g. has_phase, has_array_geometry, has_source_reference, has_calibration, has_timing, upstream_asserted

    coords: dict[str, CoordSpec]         # arrays only; name -> {units, dtype, length, attrs}
    units: dict[str, str]                # arrays only; data variable -> pint-parseable unit
    masks: list[str]                     # arrays only; names of boolean mask variables
    group_ids: dict[str, str]            # session, instrument, environment, source_recording, scene; used by splits

    processing_history: list[ProcessingStep]   # {op_id, op_version, params, transform_class}
    parents: list[str]                   # record ids; derivation only, never a dependence model
    produced_by_run: str | None          # provenance; excluded from identity so a replay's output reuses the record
    validation_state: Literal["eligible", "quarantined"]
    validation_notes: list[str]          # why quarantined, plus advisory notes such as nonfinite:<var>

    regime: dict[str, RegimeCoord] | None       # name -> {value, units, provenance, availability, uncertainty}
    anchor: AnchorFields | None          # required when kind == "anchor_estimate"
```

```python
class CoordSpec(BaseModel):
    units: str; dtype: str; length: int; attrs: dict[str, str] = {}

class ProcessingStep(BaseModel):
    op_id: str; op_version: str; params: dict; transform_class: Literal["exact", "coordinate", "lossy", "physical"]

class RegimeCoord(BaseModel):
    value: float | None
    units: str = "1"
    provenance: Literal["metadata", "estimated", "oracle"]
    availability: Literal["inference", "supervision", "evaluation_only"]
    uncertainty: float | None = None

class AnchorFields(BaseModel):
    anchor_kind: Literal["impulse_response", "delay_doppler", "delay_scale", "power_statistic", "descriptors_only"]
    descriptors: dict[str, Descriptor]   # name -> {value, units, definition, canonical_kind}
    statistical_semantics: Literal["realization", "expectation", "estimate", "posterior_samples", "pseudo_label"]
    normalization: dict[str, str | float]
    assumptions: list[str]
    identifiable: list[str]
    ambiguous: list[str]
    uncertainty_ref: str | None          # run id whose Result.uncertainty applies
```

**Identity.** `id` derives from `byte_hash` and `manifest_hash` together (W0 implementation note: deriving it from the manifest alone would collide for two payloads with one manifest). Two records with identical `byte_hash` and different `units` have different ids. `produced_by_run` is provenance, not identity, so a replay that reproduces identical bytes and manifest reuses the existing record. Correcting metadata creates a new record with `parents=[old_id]`; the old record is untouched.

**Quarantine.** `put()` runs pint over every entry in `units` and every `CoordSpec.units`. Any failure, or any array without `units` for a data variable, sets `validation_state="quarantined"`. A quarantined record is stored, listable, and refused by every `assess` with reason `quarantined:<detail>`.

---

## 2. `TaskSpec`

What a run may see and must return. Loaded from YAML in `tasks/`; the filename carries the version.

```python
class TaskSpec(BaseModel):
    schema_version: int = 1
    task_id: str                         # e.g. "pdp.rms_delay_spread"
    version: str                         # e.g. "0.1"
    task_kind: Literal["transform", "estimation", "comparison"]
    question: str

    allowed_inputs: list[FieldRef]       # each with availability class
    required_capabilities: list[str]
    params: dict[str, ParamSpec]         # name -> {type, units, required, is_assumption, description}

    quantities: dict[str, QuantitySpec]  # name -> {definition, units, canonical_kind | "not_channel", ambiguity_allowed}
    truth_source: TruthSpec              # {kind: exact|simulated|measured|none, description, error_model}
    normalization: NormSpec              # {rule, reversible, fit_scope: train|train_dev}
    regime_coords: list[RegimeRef]       # {name, availability}

    baselines: list[str]                 # op ids or arm names that must be run for a claim
    metrics: list[MetricSpec]            # {name, direction, units, independent_unit}
    split_policy: SplitPolicy            # {unit, held_out_groups, pretraining_exposure}
    uncertainty_requirement: UncReq      # {kinds_accepted, may_be_unavailable}

    completion_rule: str                 # text; what makes an experiment on this task complete
    promotion_rule: str                  # text; what makes a model on this task promotable
```

```python
class FieldRef(BaseModel):
    name: str
    availability: Literal["prediction_metadata", "prediction_evidence", "prediction_estimate", "training_only", "evaluation_only"]
```

**The firewall lives here.** `bench.firewall(task, phase="deploy")` returns only fields whose availability is one of the first three. Training-only and evaluation-only fields are served through a different function, `bench.oracle_fields(task)`, and any op that receives them is tagged `diagnostic` on its run. There is no way to reach an oracle field through the deploy handle.

**Assumptions are parameters.** A physical assumption an operation needs (for example `assume_wssus: true`) is a `ParamSpec` with `is_assumption=True`. If the caller supplies it, `assess` may return `supported` and the run records it under `assumptions_used`. If not, `assess` returns `unsupported` with `missing=["assume_wssus"]`. Nothing is ever assumed on the caller's behalf.

---

## 3. `Operation`

A pack's executable unit. A `Protocol`, not a base class.

```python
class Assessment(BaseModel):
    status: Literal["supported", "unsupported", "unknown"]
    reasons: list[str]                   # free text in v0.3; a code vocabulary is derived later from real ops
    missing: list[str]                   # capabilities or params

class Operation(Protocol):
    op_id: str
    version: str
    preconditions: list[str]             # capabilities the record must carry
    params_model: type[BaseModel]        # declares every accepted parameter; unknown params are refused
    transform_class: Literal["exact", "coordinate", "lossy", "physical", "none"]
    determinism: Literal["exact", "tolerance"]
    tolerance: float | None
    is_model: bool                       # True routes through the learned path and the deploy firewall

    def assess(self, task: TaskSpec, record: Record, params: BaseModel) -> Assessment: ...
    def run(self, task: TaskSpec, record: Record, params: BaseModel, ctx: RunContext) -> Result: ...
```

`assess` MUST be pure and fast: it reads the record's `capabilities`, `validation_state`, `units`, `coords`, `processing_history`, `validation_notes` and the supplied params, and returns. It never opens the payload. Consequently value-level checks (a nonfinite unmasked sample, zero total weight, a negative weight) happen in `run` and produce `answer = unsupported` with reasons in `diagnostics`; the run itself `succeeded`. `run` receives a `RunContext` with the store, the seed, and a scratch directory; it returns a `Result` and may write output records through `ctx.put()`.

**Registry.** `packs.registry()` reads `crossfade.toml`, imports each listed module, checks `CORE_API_VERSION == 1`, and returns `dict[op_id, Operation]`. An import failure or version mismatch fails registry construction with the module named; there is no partial registry.

---

## 4. `Run`

One execution attempt and its result.

```python
class Run(BaseModel):
    schema_version: int = 1
    run_id: str                          # "run_" + uuid4
    task_id: str; task_version: str
    op_id: str; op_version: str
    inputs: list[str]                    # record ids
    params: dict
    assumptions_used: list[str]
    code_rev: str                        # git rev or "dirty:<rev>"
    env_lock_hash: str                   # sha256 of the resolved dependency list
    seed: int | None
    path: Literal["reference", "learned", "output_only", "diagnostic"]
    started_at: datetime; finished_at: datetime | None
    status: Literal["succeeded", "failed", "cancelled"]
    attempt_of: str | None               # previous run_id when this is a retry
    error: str | None
    result: Result | None                # None unless status == "succeeded"
```

```python
class Result(BaseModel):
    quantities: dict[str, Quantity]      # name -> {value, units, origin: upstream_asserted|computed|inferred}
    outputs: list[str]                   # record ids written by the run
    answer: Literal["complete", "partial", "abstained", "unsupported"]
    applicability: Literal["in_scope", "out_of_scope", "unknown"] = "unknown"
    forward_check: ForwardCheck          # {status: passed|failed|unavailable|not_applicable, residual, threshold, in_sample}
    uncertainty: Uncertainty             # {kind: posterior|confidence_interval|predictive_interval|ensemble_summary|unavailable|not_applicable,
                                         #  estimand, method, version, validated_on, conditional_on_plugin, payload_ref}
    alternatives: list[dict] = []
    diagnostics: dict = {}
```

**Publication order.** `execute()` writes output records first, then the run JSON, then the SQLite row, each via temp file and atomic rename. A crash between steps leaves output blobs without a run that references them, which `verify` reports as orphans; it never leaves a run that references missing outputs.

**Replay.** `replay(run_id)` loads the run, re-resolves the op by `op_id` and `op_version`, re-executes with the same inputs, params and seed, and compares: exact byte equality when `determinism == "exact"`, else within `tolerance`. It records a new run with `attempt_of = run_id` and `path` unchanged.

---

## 5. `Report`

One declared comparison over runs, and what it supports.

```python
class ExperimentSpec(BaseModel):
    experiment_id: str
    task_id: str; task_version: str
    data_manifests: list[str]            # record ids of manifest records, or paths
    roles: dict[str, Literal["source", "target"]]      # manifest -> role
    arms: dict[str, ArmSpec]             # name -> {op_id, params, pretrained_from, exposure}
    primary_metric: str
    effect_rule: EffectRule              # {meaningful_delta, decision: text, frozen_at}
    seeds: list[int]; tuning_policy: str
    budgets: dict[str, Budget]           # arm -> {target_labels, target_unlabeled, adapt_compute, upstream_compute}
    exploratory: bool = False            # True when preregistration fields are incomplete

class SplitManifest(BaseModel):
    unit: str                            # the group_ids key used as the independent unit
    partitions: dict[str, list[str]]     # train/dev/test -> group ids
    frozen_at: datetime
    hash: str

class Report(BaseModel):
    schema_version: int = 1
    report_id: str
    experiment: ExperimentSpec
    split: SplitManifest
    runs: list[str]
    metrics: dict[str, dict[str, MetricValue]]   # arm -> metric -> {value, ci_low, ci_high, n_units, denominator}
    budgets_observed: dict[str, Budget]
    validity: Literal["valid", "invalid", "incomplete"]
    deviations: list[str]
    claims: list[Claim]
    mappings: list[Mapping]

class Claim(BaseModel):
    direction: str                       # "sonar_sim -> hf_sim"
    descriptor: str
    regime_cells_tested: list[dict]      # the cells actually evaluated, never a bounding box
    arm: str; baseline_arm: str
    outcome: Literal["supported", "evidence_against", "inconclusive"]
    effect: float; effect_ci: tuple[float, float]
    limitations: list[str]

class Mapping(BaseModel):
    from_domain: str; to_domain: str; descriptor: str
    implemented: bool
    claim_refs: list[int]                # indices into claims
```

**Validity.** `bench.aggregate()` sets `invalid` if any required arm is missing or any leakage check failed, `incomplete` if any seed failed, `valid` otherwise. Claims are written only from `valid` reports. A failed arm is a failed run and never evidence against anything.

---

## 6. Invariants

Each has a test. The slice column names where it is first enforced.

| Id | Invariant | Tag | Slice |
|---|---|---|---|
| CF-01 | Payload blobs are written once and never modified; there is no update path | G | W0 |
| CF-02 | Record identity covers payload bytes and semantic manifest; same bytes with different units are different records | G | W0 |
| CF-03 | Every array record has validated units on every data variable and coordinate, or is quarantined | G | W0 |
| CF-04 | A capability label never authorizes an operation; `assess` checks explicit capabilities and params | G | W0 |
| CF-05 | `assess` returns `unknown` when prerequisites cannot be established; `unknown` is never coerced to `supported` | G | W0 |
| CF-06 | A `TaskSpec` fixes allowed inputs by availability class; the deploy handle cannot return training-only or evaluation-only fields | G | W0 |
| CF-07 | An anchor estimate may omit its payload; no field is fabricated to satisfy a shape | G | W0 |
| CF-08 | A deterministic transform reports `uncertainty.kind = not_applicable`; a learned estimate without validated uncertainty reports `unavailable`; neither is ever a number | G | W0 |
| CF-09 | A forward check with no forward model is `unavailable`, never `passed` | G | W0 |
| CF-10 | Every run resolves to immutable inputs, a versioned op, a code revision and an environment lock | G | W0 |
| CF-11 | Failed and cancelled runs are persisted and linked; a retry is a new run with `attempt_of` set | G | W0 |
| CF-12 | Outputs are published before the run that references them; a run never references a missing output | G | W0 |
| CF-13 | Every quantity carries an origin: `upstream_asserted`, `computed` or `inferred` | G | W0 |
| CF-14 | Splits are at the declared independent unit; every derived record inherits its root's group ids; the checker refuses a partition crossing | G | W1 |
| CF-15 | Oracle-provenance regime coordinates and evaluation-only fields never reach a run on the `learned` or `reference` path; a run that uses them is `diagnostic` | G | W1 |
| CF-16 | Test membership is frozen before any pretraining; unlabeled test exposure is recorded as exposure | G | W2 |
| CF-17 | A valid negative or inconclusive report completes an experiment; an invalid or incomplete report produces no claim | G | W1 |
| CF-18 | Every claim names its arm, baseline arm, direction, descriptor, regime cells tested, effect and budgets | G | W1 |
| CF-19 | Tested support is the list of evaluated cells; the atlas never marks an untested interior cell validated | G | W1 |
| CF-20 | Shared-parent results are one piece of evidence; unknown model dependence withholds numerical fusion | G | W3 |
| CF-21 | No pack operation writes to an upstream system | G | W3 |
| CF-22 | Anchor-estimate uncertainty is propagated or the result is tagged `conditional_on_plugin` naming the estimate | G | W1 |
| CF-23 | Every quantity in a `TaskSpec` names a `canonical_kind` or is tagged `not_channel` | G | W0 |
| CF-24 | Every transform in a pack has a class and an equivalence test | G | W1 |
| CF-25 | Unknown fields on any record type are rejected on load | G | W0 |
