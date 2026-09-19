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
| W0-F01 | `records.put()` writes the payload blob via temp file and atomic rename, computes `byte_hash` and `manifest_hash`, validates units with pint, and writes the record JSON and SQLite row | CF-01, CF-02, CF-03 |
| W0-F02 | `records.get()` recomputes `byte_hash` on read and raises on mismatch | CF-01 |
| W0-F03 | Metadata correction is `put()` of a new record with `parents = [old]`; there is no update function | CF-01 |
| W0-F04 | `tasks.load()` rejects unknown fields and any quantity without `canonical_kind` or `not_channel` | CF-23, CF-25 |
| W0-F05 | `packs.registry()` imports the listed packs, checks `CORE_API_VERSION`, and fails whole on any error | ADR-09 |
| W0-F06 | `Operation.assess` reads only `capabilities`, `validation_state`, `units`, and params; it never opens the payload | CF-04, CF-05 |
| W0-F07 | `runs.execute()` refuses to start if `assess` is not `supported`; writes outputs, then run JSON, then row | CF-12 |
| W0-F08 | A worker exception produces `status = failed` with `error` set and no `result`; a retry is a new run with `attempt_of` | CF-11 |
| W0-F09 | `runs.replay()` re-executes and compares by the op's determinism contract | CF-10 |
| W0-F10 | `Result` serialization uses the enum states; a deterministic op's uncertainty is `not_applicable` and never a number | CF-08, CF-09, CF-13 |
| W0-F11 | `profile_fixture` returns an anchor estimate of kind `descriptors_only` with no payload | CF-07 |
| W0-F12 | `cli` exposes ingest, inspect, assess, run, replay, export; each is one function call | — |

## Acceptance tests

Pytest names follow `test_w0_atNN_<slug>`.

| Id | Given | When | Then |
|---|---|---|---|
| W0-AT-01 | The golden profile in ms | T0 runs | `mean_delay = 1 ms`, `rms_width = 1 ms`, `normalized_width = 0.5` within 1e-12 relative |
| W0-AT-02 | The same profile ingested in seconds | Both run | Physical outputs agree after conversion; both records have different ids and their original unit strings are recoverable |
| W0-AT-03 | A profile with one masked NaN | T0 runs | The entry is excluded, `n_excluded = 1`, result complete |
| W0-AT-04 | A profile with an unmasked NaN | Assess | `unsupported`, reason names the entry |
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

## Implementation increments

Each ends with a runnable test.

1. `Record` model, hashing, `put`/`get`/`verify` on files; `db.py` with the records table. Tests W0-AT-07, 08, 09.
2. `TaskSpec` model and loader; the two YAML files. Test W0-AT-16.
3. `Operation` protocol, `Assessment`, registry. `profile_fixture` with `assess` only. Tests W0-AT-04, 05, 14, 15, 17, 18, 21.
4. `Run`, `Result`, `execute`, worker subprocess, atomic publication. `profile_fixture.run`. Tests W0-AT-01, 02, 03, 06, 10, 11, 19.
5. `replay`. Test W0-AT-12.
6. `summary_fixture`. Test W0-AT-13.
7. `cli`. Test W0-AT-20 as the end-to-end demo script.

## Definition of done

All 21 tests green offline. `cloc` under budget. A `README` in the repo showing the seven-command demo and stating in its first line that this is an engineering fixture, not a validated estimator. No performance claim about any domain.
