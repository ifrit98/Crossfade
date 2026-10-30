# PRD-W0 — Workbench: ingest, compute, replay, refuse

**Status:** Ready to implement.
**Owner:** Core engineer. **Reviewers:** Sonar lead (T0 semantics), a second engineer (contracts).
**Dependencies:** None.
**Contracts:** `Record`, `TaskSpec`, `Operation`, `Run` (all of section 01 except `Report`).
**Invariants:** CF-01 to CF-13, CF-23, CF-25.
**Size budget:** 1500 lines of core plus 300 lines of fixture packs, tests included.

## Outcome

An engineer ingests a supplied delay-power profile, computes its weighted RMS width through a registered pack operation, inspects the run's lineage, replays it, and is refused when asking a summary-only record for a reconstruction. All offline, in one command sequence, with every acceptance test green.

## Scope

`records.py`, `tasks.py`, `packs.py`, `runs.py`, `db.py`, `cli.py`; the two fixture packs; two TaskSpecs; the fixtures directory with reference answers stored independently of any implementation.

**Non-goals.** `bench.py` beyond a stub; any estimator of an unknown channel; any simulator; any model; any UI; any fusion; any network access.

## Task T0

`task_id: profile.weighted_rms_width`, `version: 0.1`, `task_kind: transform`.

**Input.** A `Record` of kind `representation`, `payload_kind = array`, with one coordinate `delay` (units of time) and one data variable `weight` (dimensionless, nonnegative point weights), an optional boolean mask `valid`, and a required parameter `reference_time` with units of time. Convention: point weights, not bin-integrated densities. A record declaring a different convention in `processing_history` is refused.

**Output quantities.** `mean_delay` (time), `rms_width` (time), `normalized_width` (1), `n_used` (1), `n_excluded` (1). Each with `origin = computed`, `canonical_kind = power_statistic` for the first three and `not_channel` for the counts. `uncertainty.kind = not_applicable`. `forward_check.status = not_applicable`. `applicability = in_scope` is permitted here and only here, because a deterministic transform on its declared input has no regime.

**Golden case.** `delay = [0, 2] ms`, `weight = [1, 1]`, `reference_time = 2 ms` gives `mean_delay = 1 ms`, `rms_width = 1 ms`, `normalized_width = 0.5`. The same record in seconds gives the same physical result and both original unit strings are recoverable from the two records.

**Refusals.** Zero total included weight; any negative included weight; any nonfinite included value; nonpositive `reference_time`; mismatched lengths; missing units on `delay`, `weight` or `reference_time`; an unmasked invalid entry. A masked invalid entry is excluded and counted. If `reference_time` is absent the task returns `answer = partial` with `normalized_width` omitted, because the TaskSpec permits that; it never invents one.

## Summary comparison task

`task_id: summary.compare`, `version: 0.1`, `task_kind: comparison`. Input: a `Record` of kind `summary`, `payload_kind = structured`, carrying upstream assertions as a JSON list of `{name, value, units, confidence}`. The `summary_fixture` pack's single operation `import_summary` returns each assertion as a quantity with `origin = upstream_asserted` and leaves upstream confidence in `diagnostics`, not in `uncertainty`. A request to run any operation with precondition `has_phase` on this record is `unsupported` with `missing = ["has_phase"]`.

## Functional requirements

| Id | Requirement | Invariant |
|---|---|---|
| W0-F01 | `records.put()` writes the payload blob via temp file and atomic rename, computes `byte_hash` and `manifest_hash`, validates with pint every unit the record keeps (the payload's and the manifest's), and writes the record JSON and SQLite row | CF-01, CF-02, CF-03 |
| W0-F02 | `records.get()` recomputes `byte_hash`, `manifest_hash` and `id` on read and raises on mismatch | CF-01, CF-02 |
| W0-F03 | Metadata correction is `put()` of a new record with `parents = [old]`; there is no update function | CF-01 |
| W0-F04 | `tasks.load()` rejects unknown fields and any quantity without `canonical_kind` or `not_channel` | CF-23, CF-25 |
| W0-F05 | `packs.registry()` imports the listed packs, checks `CORE_API_VERSION`, and fails whole on any error | ADR-09 |
| W0-F06 | `Operation.assess` reads only `capabilities`, `validation_state`, `units`, and params; it never opens the payload | CF-04, CF-05 |
| W0-F07 | `runs.execute()` refuses to start if `assess` is not `supported`; runs the operation in a child process under optional limits; writes outputs, then run JSON, then row | CF-12 |
| W0-F08 | A worker exception, an expired wall-clock limit or the worker's death produces `status = failed` with `error` set and no `result`; a retry is a new run with `attempt_of` | CF-11 |
| W0-F09 | `runs.replay()` re-executes and compares by the op's determinism contract; it refuses a `tolerance` op until that comparison is defined | CF-10 |
| W0-F10 | `Result` serialization uses the enum states; a deterministic op's uncertainty is `not_applicable` and never a number | CF-08, CF-09, CF-13 |
| W0-F11 | `profile_fixture` returns an anchor estimate of kind `descriptors_only` with no payload | CF-07 |
| W0-F12 | `cli` exposes ingest, inspect, assess, run, replay, export; each is one function call | — |

## Implementation notes (branch `w0-workbench`)

Details settled while implementing. The first two, and the notes on manifest units, record integrity and tolerance replay, are reflected in `01_contracts.md`; the rest change no contract.

- AT-04 and AT-05 value checks (unmasked nonfinite, zero total weight, negative weight) are made in `run`, not `assess`, because `assess` never opens the payload. The run succeeds with `answer = unsupported` and the reasons in `diagnostics`. The negative `reference_time` check is a parameter check and stays in `assess`.
- `Record.id` derives from both hashes; `produced_by_run` and `validation_notes` were added. `verify()` reports `orphan_outputs` for AT-11.
- The worker is a child Python process started with `sys.executable`. It gets the parent's `sys.path` and imports the operation from its pack module by `op_id`, as `registry()` does; the operation object is never pickled. So `execute` needs the operation to be listed in an imported pack's `OPERATIONS`, and raises `RegistryError` otherwise. The parent keeps assess, parameter validation and publication, in the same order.
- `execute(..., limits=WorkerLimits(wall_seconds, memory_bytes))`; `None` means no limit. The wall-clock limit covers the child's whole life, interpreter start and imports included; when it expires the parent kills and reaps the child. The memory limit is `RLIMIT_AS` (address space), set in the child before the pack is imported. A memory limit the platform refuses to set fails the run; the operation never runs unlimited instead.
- Every worker failure is a failed run with `error` set and no `result`. An exception gives its type, message and traceback; an expired wall-clock limit names `wall_seconds` and its value; a child that exits without a result, or exits nonzero after writing one, names its exit code or signal. A result counts only if the child exits 0. A failure to start the worker or read its reply gives its type, message and traceback. An interrupt of the parent kills and reaps the child, then propagates with no run written, as in W0-AT-11. A `MemoryError` under a memory limit names `memory_bytes`.
- `verify()` lists as `orphan_outputs` every record with `produced_by_run` that no run's `result.outputs` references, as "Publication order" in `01_contracts.md` says. It used to list only outputs whose run was never written, which missed the outputs of a run that failed after publishing them (W0-AT-23).
- Manifest units on array records (W0-AT-25). `put` used to keep the manifest's `units` and `coords` through `setdefault` while validating only the payload's attributes, so a manifest could restate a coordinate in other units unchecked. Now the record keeps the payload's units overlaid name by name by the manifest's, and pint checks them all. A manifest unit that doesn't parse gives `unparseable_units:<name>:<unit>`; one that differs from the payload's attribute gives `units_conflict:<name>`; either quarantines. Units compare as strings. A payload variable without a `units` attribute stays `missing_units` whatever the manifest says. A quarantined record keeps an unparseable unit as given, where it used to drop it from `units` or write `"?"` in `CoordSpec.units`. For a payload coordinate the manifest supplies only the units, and `dtype`, `length` and `attrs` come from the payload, so a manifest repeating the payload's units yields the same record as one that leaves them out.
- Record integrity (W0-AT-26). `manifest_hash` used to be computed from the caller's manifest before validation, so it could not be recomputed from the stored record, and `get` and `verify` checked only the payload. Now it is the sha256 of the stored record's canonical JSON less `id`, `byte_hash`, `manifest_hash`, `ingested_at`, `payload_ref` and `produced_by_run`. `get` and `verify` recompute `byte_hash`, `manifest_hash` and `id` and check `id` against the file name; `get` raises `IntegrityError` and `verify` lists the record in `mismatches`. Record ids changed as a result; no fixture or test hard-codes one.
- Tolerance replay (W0-AT-27). `replay` of an op whose `determinism` isn't `exact` raises `NotImplementedError` before executing, so no run is written. Before, it executed and compared nothing.
- On macOS (Darwin 24, arm64), `setrlimit(RLIMIT_AS)` failed with `EINVAL` at 1, 8 and 64 GiB and succeeded at 512 GiB, for a Python process whose virtual size was about 392 GiB. So a memory limit fails every run there. W0-AT-24 is skipped where the limit can't be set or isn't enforced; the test of the refusal runs where it can't be set.
- **Open: the limit values.** The spec doesn't fix them, so `execute` has no default limit. They block the CLI flags for the limits, nothing else.
- **Open: the tolerance comparison.** Which values replay compares for a `tolerance` op (output payloads or result quantities), and whether `tolerance` is absolute or relative. The contract doesn't say. It blocks replay of the first op declaring `determinism = "tolerance"`; none exists in W0.

## Acceptance tests

Pytest names follow `test_w0_atNN_<slug>`.

| Id | Given | When | Then |
|---|---|---|---|
| W0-AT-01 | The golden profile in ms | T0 runs | `mean_delay = 1 ms`, `rms_width = 1 ms`, `normalized_width = 0.5` within 1e-12 relative |
| W0-AT-02 | The same profile ingested in seconds | Both run | Physical outputs agree after conversion; both records have different ids and their original unit strings are recoverable |
| W0-AT-03 | A profile with one masked NaN | T0 runs | The entry is excluded, `n_excluded = 1`, result complete |
| W0-AT-04 | A profile with an unmasked NaN; separately, an unmasked NaN or `inf` in `delay` | Assess | `unsupported`, reason names the entry (`nonfinite:delay[i]` for a delay). A masked NaN in `delay` is excluded and counted, as in W0-AT-03 |
| W0-AT-05 | Zero total weight; negative reference | Assess | `unsupported` with the specific reason each |
| W0-AT-06 | A profile missing `reference_time` | T0 runs | `answer = partial`, `normalized_width` absent, no invented value |
| W0-AT-07 | A profile with no units on `delay` | Ingest | Stored with `validation_state = quarantined`; assess returns `unsupported` with reason `quarantined:...` |
| W0-AT-08 | Identical bytes, units `ms` and `s` | Ingest both | Same `byte_hash`, different `manifest_hash`, different ids |
| W0-AT-09 | A stored blob altered on disk | `get()` | Raises integrity error; replay refuses |
| W0-AT-10 | A worker that raises after validation | Execute | Run persisted as `failed` with `error`; no result; outputs directory has no orphan referenced by a run |
| W0-AT-11 | A worker killed between output write and run write | Execute | No run row exists; `verify` lists the orphan blob |
| W0-AT-12 | A succeeded T0 run | Replay | New run with `attempt_of` set; outputs byte-identical (determinism `exact`) |
| W0-AT-13 | A summary record | `import_summary` | Quantities have `origin = upstream_asserted`; upstream confidence is in `diagnostics`; `uncertainty.kind = not_applicable` |
| W0-AT-14 | A summary record | Assess an op with precondition `has_phase` | `unsupported`, `missing = ["has_phase"]` |
| W0-AT-15 | A record labeled C3 with `capabilities` lacking `has_source_reference` | Assess an op requiring it | `unsupported`; the label did not authorize |
| W0-AT-16 | A TaskSpec with an unknown field; a TaskSpec with a quantity lacking `canonical_kind` | Load | Both rejected with the field named |
| W0-AT-17 | `crossfade.toml` listing a pack with `CORE_API_VERSION = 2` | Registry | Fails whole, names the pack |
| W0-AT-18 | A run requested with a param not in `params_model` | Assess | `unsupported`, names the param |
| W0-AT-19 | The `profile_fixture` golden run | Inspect output record | `anchor.anchor_kind = descriptors_only`, `payload_ref` absent |
| W0-AT-20 | Network disabled | Full demo sequence | Passes |
| W0-AT-21 | Every registered op, every declared precondition | Conformance | `assess` refuses a record lacking that capability |
| W0-AT-22 | A worker that never returns, `wall_seconds = 1` | Execute | Returns in under 10 s; run `failed`, `error` names the wall-clock limit; the child process is gone |
| W0-AT-23 | A worker that publishes an output, then kills itself with SIGKILL | Execute | Run `failed`, `error` names the signal, no result; `verify` lists the orphan output |
| W0-AT-24 | A worker that allocates past `memory_bytes` | Execute | Run `failed`; `error` names the limit or the signal. Skipped where the platform doesn't enforce the limit |
| W0-AT-25 | An array record whose manifest `coords` give `delay` the unit `s` while the payload attribute says `ms` | Ingest; assess | Quarantined with a note naming `delay`; assess `unsupported` with a `quarantined:` reason. An unparseable manifest unit also quarantines. A manifest repeating the payload's units yields the same `id` as the bare manifest |
| W0-AT-26 | A stored record whose JSON has had a unit edited on disk | `get()`; `verify()` | `get` raises integrity error; `verify` lists the record in `mismatches`. Putting identical input twice still yields one `id` |
| W0-AT-27 | An op declaring `determinism = "tolerance"` | Replay | Raises before executing; no new run file or row exists |

## Implementation increments

Each ends with a runnable test.

1. `Record` model, hashing, `put`/`get`/`verify` on files; `db.py` with the records table. Tests W0-AT-07, 08, 09, 25, 26.
2. `TaskSpec` model and loader; the two YAML files. Test W0-AT-16.
3. `Operation` protocol, `Assessment`, registry. `profile_fixture` with `assess` only. Tests W0-AT-04, 05, 14, 15, 17, 18, 21.
4. `Run`, `Result`, `execute`, worker subprocess, atomic publication. `profile_fixture.run`. Tests W0-AT-01, 02, 03, 06, 10, 11, 19, 22, 23, 24.
5. `replay`. Tests W0-AT-12, 27.
6. `summary_fixture`. Test W0-AT-13.
7. `cli`. Test W0-AT-20 as the end-to-end demo script.

## Definition of done

All 27 tests green offline, W0-AT-24 where the platform enforces the memory limit. `cloc` under budget. A `README` in the repo showing the seven-command demo and stating in its first line that this is an engineering fixture, not a validated estimator. No performance claim about any domain.
