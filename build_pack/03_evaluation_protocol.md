# 03. Evaluation protocol

Kept nearly whole from the v0.2 pack, which was its best document, with four changes: regime matching is per descriptor; H1 to H5 are restated against that; the simulator-independence rule requires both code independence and documented assumption independence; and the record model is the five types of section 01. Everything here is **[G]** unless tagged.

## 1. Three levels of demonstration

| Level | What it shows | What it does not show |
|---|---|---|
| E0 Contract fixture | T0 computes a known property of a supplied profile; storage, units, capability handling, replay work | Anything about channels or transfer |
| E1 Within-domain estimation | A declared descriptor is estimated from permitted observations and compared to independent truth with its own error model; classical and from-scratch baselines characterized | Transfer |
| E2 Cross-domain transfer | Only the declared transfer intervention changes; target utility is measured under held-out conditions; shared-simulator smoke tests, independent-domain evidence and measured-data validation are reported separately | Universal generalization |

An E0 result is never promoted to E1 or E2 by relabeling data.

## 2. Preregistration

An `ExperimentSpec` is confirmatory only if every field is filled: task version, data manifests, roles, arms with exposure, primary metric, effect rule with a frozen timestamp, seeds, tuning policy, budgets, independent unit, expected failure modes, exclusions. A spec missing any of these may run with `exploratory = true` and produces no claim.

No universal percentage threshold is invented. Baseline variability is estimated on development data; the meaningful effect for the task is agreed; the rule is frozen before the locked test is viewed.

## 3. Hypotheses **[H]**

| Id | Statement | Reported as | Completion |
|---|---|---|---|
| H1 | For a fixed descriptor and budget, source pretraining produces a practically meaningful target gain in the cells where the descriptor's governing groups overlap | `delta = baseline_loss − candidate_loss` at the independent unit, with CI | supported, evidence_against, inconclusive |
| H2 | Transfer varies with overlap distance per descriptor | The transfer surface: delta as a function of per-group distance | A gain outside predicted overlap is a finding; never a failed gate |
| H3 | Conditioning on regime coordinates improves held-out utility over unconditioned arms under interventions that separate regime from domain identity | Ablation delta; routing telemetry is diagnostic only | supported, evidence_against, inconclusive |
| H4 | A named mechanism, waveguide interference structure, estimated in one bounded dispersive waveguide remains predictive in another and beats shortcut controls | Effect versus shuffled-pair and nuisance-matched controls | Deferred until the sonar lead approves the observable |
| H5 | Uncertainty quality survives shift, or applicability flags it | Coverage, interval width, accepted-case error, abstention rate, all with denominators | supported, evidence_against, inconclusive |

**Per-descriptor regime matching.** The placeholder sonar and HF ranges are disjoint in `M = v/c` and `β_B = B/f_c` and overlap in `Π_τ`, `Π_ν`, `Π_f`, `Π_L`. So H1 is run per descriptor: arrival-structure descriptors (RMS delay spread, arrival count, striation slope) are the candidates; Doppler descriptors are the predicted negative control. Real support is established from pack regime declarations before H1 runs. A laboratory acoustic-and-RF substitute tests portability and is labeled as such; it does not validate the sonar-HF claim.

## 4. Feature and truth firewall

Every field in a `TaskSpec.allowed_inputs` has one availability class: `prediction_metadata`, `prediction_evidence`, `prediction_estimate`, `training_only`, `evaluation_only`. The deploy handle, `bench.firewall(task, "deploy")`, serves only the first three. Oracle fields are served by `bench.oracle_fields(task)`, and any run that calls it has `path = "diagnostic"`. Diagnostic runs cannot satisfy the promotion gate.

Anchor estimates used for pairing are `pseudo_label` records carrying estimator version, input lineage and uncertainty. Test reference answers never choose routing, positive pairs or normalizers on the deploy path. Post-hoc stratification by truth is reporting only.

## 5. Splits and exposure

Split at the task's independent unit (`SplitPolicy.unit`, one of the `group_ids` keys). Every derived record inherits its root's `group_ids`; `bench.check_leakage()` walks `parents` to the root and refuses a partition crossing. Test membership is frozen and hashed before any pretraining. Target-domain unlabeled exposure is recorded per arm. Transductive arms are declared as such.

Normalization, regime selection, pairing thresholds and calibration are fit on `train` or `train_dev` per `NormSpec.fit_scope`; a fit touching `test` is refused.

## 6. Pairing and simulator evidence

Each pair record declares one basis:

| Basis | Kind of supervision |
|---|---|
| `same_event` | Two instruments observed one physical event |
| `controlled_mechanism` | Two independent simulators rendered a deliberately corresponding mechanism |
| `descriptor_matched` | Pseudo-pair by matching estimated descriptors; weakest |
| `negative` | Deliberately unpaired |

They are never pooled. Shuffled-pair and nuisance-matched controls run where the task's shortcut risks call for them.

**Simulator independence.** A cross-domain claim from simulation requires both:

1. No shared forward-physics kernel between the two generators. Shared array libraries, schemas and readers are fine; shared propagation code is not.
2. A written independence statement (`templates/independence_statement.md`) covering scene distribution, approximation family, and truth construction.

Both simplified in-house generators proposed in section 06 share the approximation family "discrete paths with per-path delay and gain," which is the anchor assumption itself. The statement must say so, and measured-data validation is required before any real-world claim.

## 7. Budgets

Two views, always both.

| View | Controlled | Reported |
|---|---|---|
| Adaptation efficiency | Target labels, target unlabeled exposure, adaptation tuning, adaptation compute | Source pretraining cost as an upstream line item |
| Total cost | Nothing | Simulation, all pretraining, tuning, adaptation, inference, storage, amortization assumptions |

For any sparse arm, total and active parameters both. Declare which variables are controlled; report the rest.

## 8. Baseline ladder

Required in order; every arm above the first is compared to every arm below it.

1. Direct or classical calculation
2. Physically normalized descriptors plus a linear or small head
3. Independent target model from scratch
4. Target-only self-supervised pretraining
5. Pooled or domain-conditioned model
6. Dense shared/private model with adapters
7. Routed variant (optional, W2 later)

## 9. Metrics and decisions

Effect is `delta = baseline_loss − candidate_loss`; positive favors the candidate; original losses are reported alongside. No ratio that is undefined at zero baseline loss.

Aggregate at the independent unit; windows and seeds are not independent observations. Include uncertainty from both grouping and training variation where the design allows. With too few units the inference is `inconclusive`.

A positive primary result requires the preregistered effect and its CI to clear the rule. Evidence against requires an informative comparison; lack of significance is not proof of no effect.

For uncertainty: coverage alone is insufficient. Report width, proper scores where applicable, accepted-case error, forward-check failure rate, and abstention count, each with the population denominator.

## 10. Records

`Run` is one attempt. `Report` aggregates a comparison with validity `valid`, `invalid` or `incomplete`. `Claim` is a section of a report with outcome `supported`, `evidence_against` or `inconclusive`. `Mapping` is recorded only for an implemented correspondence. Negative transfer is a measured delta, never a crashed job.

## 11. Gates

| Gate | Question | Passes when | Does not imply |
|---|---|---|---|
| Delivery | Did the declared arms run validly and reproducibly? | Required arms present; leakage checks pass; report rebuilds from persisted runs | Any scientific result |
| Scientific | What does the result support? | A scoped claim with effect, CI, budgets and limitations, in any direction | Deployment fitness |
| Promotion | Is the model useful for its declared inputs? | Preregistered utility and uncertainty criteria met at the independent unit on relevant data | Anything beyond tested cells |
