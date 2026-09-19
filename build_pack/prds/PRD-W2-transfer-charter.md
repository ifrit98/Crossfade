# PRD-W2 — Research charter: second domain and transfer trial

**Status:** Charter. The software parts are ready; the scientific parts have open inputs listed at the end. A positive result is not promised; a valid report in any direction completes the slice.
**Owner:** Model engineer with the pack engineer and the sonar lead. **Reviewers:** Core engineer, numerical reviewer.
**Dependencies:** W1 complete; W1 split policy frozen and test membership hashed before any pretraining begins (CF-16).
**Contracts:** No new types. Adds `packs/hf_sim`, `packs/sonar_sim/models.py`, `packs/hf_sim/models.py`.
**Invariants:** CF-16, CF-18, CF-19, CF-22, plus all of W1's.
**Size budget:** `hf_sim` 1000 lines; models 2000 lines.

## Outcome

The team measures whether pretraining on one domain's simulated observations reduces the target-domain data needed to estimate the two W1 descriptors, per descriptor, across a designed regime overlap, with typed uncertainty, and records a scoped claim for each direction. The atlas gains its first transfer entries, positive, negative or inconclusive.

## Software deliverables (delivery gate)

1. `packs/hf_sim`: the multimode skywave simulator per section 06, an `import_rangedoppler` lossy transform, a `multimode_dd` estimator producing a `delay_doppler` anchor with the two descriptors, and a bootstrap uncertainty. Independence statement written and stored as a record.
2. `models.py` in each pack: a masked-modeling pretraining op (`is_model = True`, ladder arm 4), a from-scratch estimator op (arm 3), a normalized-features-plus-head op (arm 2), a pooled op with domain token (arm 5), and a dense shared/private op with adapters (arm 6). All read inputs only through `firewall(task, "deploy")`.
3. Pairing records with a declared basis per section 03 §6. The primary basis is `controlled_mechanism`: for each regime cell in the overlap, the two simulators render scenes whose PDP descriptors are deliberately matched. `descriptor_matched` pseudo-pairs are the secondary basis and are never pooled with the primary.
4. The regime coverage report from section 06 §5, produced before any transfer run.

## Hypotheses tested **[H]**

H1 and H2 per section 03, for `rms_delay_spread` and `arrival_count`, in both directions sonar→HF and HF→sonar. H5 for the dense arm's bootstrap or ensemble uncertainty. H3 and H4 are not in W2's first trial; H4 requires the sonar lead's approval of the striation observable and is the natural second trial.

The predicted negative control: a Doppler-spread descriptor, added to both packs as a third quantity if time allows, on which no transfer is expected because `M` and `β_B` do not overlap.

## Arms and budgets

| Arm | Ladder | Pretrained from | Target labels | Target unlabeled |
|---|---|---|---|---|
| A1 classical | 1 | none | 0 | 0 |
| A2 features + head | 2 | none | N per curve point | 0 |
| A3 scratch | 3 | none | N | 0 |
| A4 target SSL | 4 | target unlabeled | N | all train |
| A5 pooled | 5 | both, labeled | N | all train both |
| A6 dense shared/private, source-pretrained | 6 | source SSL then source labeled | N | source all; target 0 |
| A6' dense shared/private, source + target SSL | 6 | source and target SSL | N | all train both |

Learning curve: N in {8, 32, 128, 512} target scenes. Controlled: target labels, adaptation compute (fixed epochs and optimizer), tuning budget (fixed grid). Reported: upstream pretraining compute, total parameters. Seeds: 5. Independent unit: scene, held out by scene and environment.

## Effect rule (to be frozen before the locked test)

Primary metric: absolute `rms_delay_spread` error in resolution cells at the independent unit. Effect: `delta = A3_loss − A6_loss` at each N. Meaningful delta: to be set from A3's development-set variability across seeds, as the smallest delta exceeding two seed-standard-deviations at N = 32; frozen and timestamped in the `ExperimentSpec` before the test partition is read. Decision: supported if the CI of delta excludes zero and exceeds the meaningful delta at two or more N; evidence_against if the CI excludes the meaningful delta in the other direction at two or more N; inconclusive otherwise.

## Shortcut controls

- Shuffled-pair control: A6 trained with pairing bases permuted; a gain surviving this is not transfer.
- Nuisance-matched control: target scenes matched to source scenes on SNR and bandwidth only, not on descriptors.
- Oracle-regime diagnostic: A6 given oracle `Π_τ`; run as `diagnostic`; reported separately; cannot promote.

## Acceptance tests

| Id | Given | When | Then |
|---|---|---|---|
| W2-AT-01 | HF golden scene | `multimode_dd` | Descriptors match the fixture within tolerance; anchor kind `delay_doppler` |
| W2-AT-02 | Both packs | Independence statement | Stored as a record; names the shared approximation family |
| W2-AT-03 | Manifests for both | Coverage report | Lists cells per descriptor and the intersection; H1 refuses to run on an empty intersection |
| W2-AT-04 | Pretraining requested before test hash exists | Execute | Refused, CF-16 |
| W2-AT-05 | Any model op given an evaluation-only field on the deploy path | Firewall | Refused; the diagnostic path tags the run |
| W2-AT-06 | Full trial, one direction | Report | `valid`; per-N metrics with CIs; budgets in both views; claims per descriptor with cells listed |
| W2-AT-07 | One seed of A6 crashes | Report | `incomplete`; no claim; the crash is not recorded as evidence against |
| W2-AT-08 | Shuffled-pair control | Report | Reported alongside; a claim citing A6 lists the control's delta |
| W2-AT-09 | Doppler-spread negative control, if implemented | Report | Its claim is recorded whatever its outcome; a positive delta is a finding |
| W2-AT-10 | Rebuild from persisted runs | Report | Identical |

## Open inputs (block the scientific gate, not the software)

| Input | Who | Blocks |
|---|---|---|
| Pairing basis approval: is `controlled_mechanism` via matched descriptors an acceptable primary basis, or does the lead want `same_event`-like pairs from a shared physical scene definition? | Sonar lead | Trial design |
| HF simulator simplification acceptance | An HF-familiar reviewer | `hf_sim` sign-off |
| Whether the W1 estimators' error model (from the W1 report) is tight enough in the overlap cells to serve as pseudo-label truth for A6' | Numerical reviewer | A6' arm |
| Named measured dataset for the reality check | Sonar lead | Any real-world claim; not the simulated trial |

## Definition of done

Ten tests green. One valid report per direction per descriptor, each with claims, controls and both budget views. A two-page summary: the transfer surface per descriptor, what the controls showed, and whether any arm is worth a routing ablation. The atlas index lists the claims. No promotion of any model is part of completion.
