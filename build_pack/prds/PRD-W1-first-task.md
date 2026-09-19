# PRD-W1 — First real task: delay spread and arrival count from simulated beam time series

**Status:** Ready pending one sign-off: the sonar lead confirms the target quantity (ADR-10) and accepts the image-source simulator as the first generator (ADR-11). The PRD is written against the proposed answers so a yes is sufficient to start.
**Owner:** Pack engineer with the sonar lead. **Reviewers:** Core engineer, numerical reviewer.
**Dependencies:** W0 contracts. Runs alongside W0's last increments.
**Contracts:** Adds `Report`, `ExperimentSpec`, `SplitManifest`, `Claim` (section 01 §5); adds `bench.py`.
**Invariants:** CF-14, CF-15, CF-17, CF-18, CF-19, CF-22, CF-24.
**Size budget:** `packs/sonar_sim` 1200 lines including the simulator; `bench.py` 500 lines.

## Outcome

A researcher generates simulated beam time series over a designed regime grid, estimates RMS delay spread and resolvable-arrival count with two classical estimators, gets a bootstrap uncertainty on each, runs a preregistered comparison with grouped splits and leakage checks, and reads a report that characterizes each estimator's error per regime cell against exact truth. The report is the first entry in the atlas and contains no transfer claim.

## Why this task **[P]**

RMS delay spread and arrival count are functionals of the power-delay profile, which is a marginal of the scattering function, so they are anchor descriptors under ADR-03. Their truth is exact in an image-source simulator. Their classical estimators are ones the sonar lead already runs. Their governing regime groups, `Π_τ` and `Π_f`, are the ones with plausible sonar-HF overlap, so the same descriptors carry into W2 as the transfer candidates.

## TaskSpecs

Two YAML files, `pdp.rms_delay_spread.v0.1` and `pdp.arrival_count.v0.1`. Shared fields:

- `task_kind: estimation`
- `allowed_inputs`: `beam_timeseries` (prediction_evidence), `fs` (prediction_metadata), `band` (prediction_metadata), `array_geometry` (prediction_metadata), `local_sound_speed` (prediction_metadata); `arrival_list` (evaluation_only); `sim_params` (training_only)
- `required_capabilities`: `has_timing`, `has_phase`
- `params`: `window_s` (lossy processing parameter, recorded), `cepstral_lifter` (estimator parameter), `assume_point_source: bool` (`is_assumption = True`)
- `quantities`: `rms_delay_spread` (s, `canonical_kind = power_statistic`), `arrival_count` (1, `canonical_kind = power_statistic`, `ambiguity_allowed = True` because arrivals within one resolution cell are ambiguous by definition)
- `truth_source`: `{kind: exact, description: "functional of the simulator arrival list", error_model: "none for the simulator; resolution-cell merging rule stated for arrival_count"}`
- `regime_coords`: `Π_τ` (availability `inference`, estimated from `band` and the estimate itself; and `oracle` from `arrival_list` for diagnostics), `Π_f` (inference, from `band` and water depth if supplied, else null), `SNR_cell` (estimated)
- `split_policy`: `{unit: scene, held_out_groups: [scene, environment], pretraining_exposure: none}` where `scene` is one sampled environment-and-geometry, and `environment` is a bottom type
- `uncertainty_requirement`: `{kinds_accepted: [ensemble_summary, predictive_interval], may_be_unavailable: false}`
- `baselines`: `[pdp.rms_delay_spread.direct_from_truth]` for the arm-1 sanity check, `[autocorr_pdp, cepstral_pdp]` as the classical arms
- `completion_rule`: a valid report over all planned cells with both estimators
- `promotion_rule`: not applicable in W1; no model is promoted

The inference-time metadata inventory (what a real recording actually carries) is section 12 question 4 in the spec; the `allowed_inputs` above are the proposal.

## Simulator `sonar_sim.sim` **[P]**

Image-source Pekeris waveguide per `06_data_and_simulators.md`. Interface: `simulate(scene: SceneParams, source: SourceParams, seed) -> (beam_timeseries: xr.Dataset, arrival_list: xr.Dataset)`. The arrival list is stored as a separate `Record` with `capabilities = ["oracle"]` and reachable only through `bench.oracle_fields`. Scene parameters are stored as `training_only`.

Regime grid: water depth {50, 100, 200} m; range {1, 3, 10} km; bottom {sand, silt, rock} as sound speed and density pairs; center frequency {200, 500, 1000} Hz with fractional bandwidth {0.3, 0.6}; SNR per cell {−10, 0, 10} dB. That is 486 cells; sample 3 scenes per cell with different source and receiver depths. Cells are the atlas's tested support.

## Operations `sonar_sim.ops`

| Op | Class | Preconditions | Output | Uncertainty |
|---|---|---|---|---|
| `beamform_stft` | lossy | `has_phase`, `has_array_geometry` | representation record, complex STFT per beam, `window_s` recorded | not_applicable |
| `autocorr_pdp` | none (estimator) | `has_phase`, `has_timing` | anchor estimate, kind `power_statistic`, PDP on a delay grid plus the two descriptors | ensemble_summary via block bootstrap over time segments |
| `cepstral_pdp` | none (estimator) | `has_timing` (works on magnitude) | anchor estimate, kind `descriptors_only`, the two descriptors | ensemble_summary via block bootstrap |
| `direct_from_truth` | none | `oracle` | the two descriptors from the arrival list | not_applicable; `path = diagnostic` |

Each estimator's `assumptions` list includes `assume_point_source` and the resolution-cell merging rule used for `arrival_count`. Each states `identifiable = [rms_delay_spread]`, `ambiguous = [arrival_count within one cell]`.

**Transform tests (CF-24).** `beamform_stft` declares `window_s` as lossy and ships a test showing that the retained-information contract holds: RMS delay spread estimated from two window lengths agrees within the declared tolerance on the golden scene, and the tolerance is recorded in the pack's `TRANSFORMS`.

## Bench `crossfade/bench.py`

`ExperimentSpec` loader; `SplitManifest` builder that groups by `scene` and hashes; `check_leakage()` walking `parents` to the root and refusing crossings; `firewall()` and `oracle_fields()`; `aggregate()` at the independent unit with bootstrap CIs; `Report` writer; `claim_index()` as one SQLite table.

## Experiment W1-E1 (preregistered)

Arms: `autocorr_pdp`, `cepstral_pdp`, and `direct_from_truth` as the diagnostic sanity arm. Primary metric: absolute error in `rms_delay_spread` in units of the resolution cell `1/B`, aggregated per scene. Secondary: `arrival_count` error under the stated merging rule; coverage of the bootstrap interval at the nominal level; abstention rate when SNR is below a declared floor. Effect rule: this experiment characterizes, it does not compare a candidate against a baseline, so `effect_rule.decision` is "report per-cell error and coverage; no claim of superiority." Seeds: 5. Budgets: reported, nothing controlled.

Claims written: one per estimator per descriptor, `outcome = supported` if coverage is within tolerance across tested cells, else `evidence_against` with the failing cells listed. These are claims about the estimator's error model, not about transfer.

## Functional requirements

| Id | Requirement | Invariant |
|---|---|---|
| W1-F01 | The simulator writes the arrival list as a separate record reachable only via `oracle_fields` | CF-15 |
| W1-F02 | Every derived record inherits `group_ids` from its root; the checker refuses a split where any root crosses partitions | CF-14 |
| W1-F03 | A run that calls `oracle_fields` has `path = diagnostic` | CF-15 |
| W1-F04 | Both estimators return `ensemble_summary` with the bootstrap method, block length and count recorded | CF-08, CF-22 |
| W1-F05 | `arrival_count` results list the merging rule under `assumptions_used` and the ambiguity under `alternatives` | CF-07 |
| W1-F06 | `aggregate()` refuses to run if any planned cell has fewer than the declared minimum scenes and marks the report `incomplete` | CF-17 |
| W1-F07 | Claims list the cells actually evaluated | CF-19 |
| W1-F08 | Every transform in `TRANSFORMS` has an equivalence test | CF-24 |
| W1-F09 | `beamform_stft` records `window_s` and the STFT parameters in `processing_history` with `transform_class = lossy` | CF-24 |

## Acceptance tests

| Id | Given | When | Then |
|---|---|---|---|
| W1-AT-01 | Golden scene | `direct_from_truth` | Matches the fixture's stored descriptor values exactly |
| W1-AT-02 | Golden scene at 10 dB | `autocorr_pdp` and `cepstral_pdp` | Each within its fixture tolerance; run path is `reference` |
| W1-AT-03 | A split placing two windows of one scene in train and test | `check_leakage` | Refused, names the scene |
| W1-AT-04 | An op that requests `arrival_list` through the deploy handle | Firewall | Refused; through `oracle_fields` the run is `diagnostic` |
| W1-AT-05 | The full grid, 5 seeds | W1-E1 | Report `valid`; per-cell error and coverage tables present; claims list 486 cells |
| W1-AT-06 | One cell with 1 scene | Aggregate | Report `incomplete`; no claim for that cell |
| W1-AT-07 | Two window lengths on the golden scene | Transform test | Delay-spread agreement within the declared tolerance |
| W1-AT-08 | SNR −10 dB cells | Both estimators | Abstention or wide intervals, reported with denominators; never a silent point |
| W1-AT-09 | Rebuild from persisted runs | Report | Identical metrics and claims |
| W1-AT-10 | A record labeled C3 whose `capabilities` lacks `has_array_geometry` | `beamform_stft` | `unsupported` |

## Implementation increments

1. Simulator with golden scene and stored arrival list; W1-AT-01.
2. `autocorr_pdp`, `cepstral_pdp` with bootstrap; W1-AT-02, 08, 10.
3. `beamform_stft` with transform test; W1-AT-07.
4. `bench`: splits, leakage, firewall; W1-AT-03, 04.
5. `bench`: aggregate, report, claims, index; W1-AT-05, 06, 09.

## Definition of done

Ten tests green. A report in the store with claims about estimator error per cell. A one-page summary for the sonar lead: which cells each estimator is trustworthy in, which it is not, and what that implies for the W2 pairing grid. No transfer claim anywhere.
