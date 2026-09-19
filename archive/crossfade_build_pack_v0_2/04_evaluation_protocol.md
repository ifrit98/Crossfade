# Evaluation protocol: engineering completion versus scientific evidence

## 1. Three levels of demonstration

**E0 — Contract fixture.** Task T0 computes a known property of a supplied profile and demonstrates storage, units, capability handling, and replay. This proves no cross-domain learning.

**E1 — Within-domain estimation.** Estimate a declared quantity from permitted observations; evaluate against independent reference truth with its own error limitations. A full channel need not be the target. Establish the classical/direct baseline and a learned-from-scratch baseline.

**E2 — Cross-domain transfer.** Change only the declared transfer intervention and measure target-domain utility under held-out conditions. Separate shared simulator smoke tests from independent-domain evidence and from measured-data validation.

Do not promote an E0 result to E1 or E2 by changing dataset labels.

## 2. Mandatory preregistration fields

An experiment specification contains the TaskSpec version, source and target data manifests, primary transfer direction, allowed model inputs, truth source, pairing rule, regime-matching rule, baseline variants, adaptation budgets, all pretraining exposure, independent test unit, seeds, tuning policy, primary metric, practical effect threshold, statistical decision procedure, expected failure modes, resource limits, and exclusions.

Do not invent a universal percentage gain threshold. Estimate baseline variability on development data, agree what improvement matters for the selected task, and freeze that rule before viewing the locked test outcomes. Exploratory runs remain useful but are labeled exploratory.

## 3. Hypotheses replacing the current H1–H5

| Original | Proposed formulation | Completion rule |
|---|---|---|
| H1: matched-regime gain | For a fixed task and data budget, source pretraining produces a practically meaningful target gain in the declared overlap region. | Report effect, uncertainty, and supported/evidence-against/inconclusive verdict. |
| H2: mismatched null/negative | Estimate how transfer changes across support overlap, distance, and task conditions. | A gain outside the proposed overlap is retained as a finding, not rejected. |
| H3: router follows physics | Under interventions or controlled comparisons that separate regime from domain identity, does conditioning improve held-out utility over simpler alternatives? | Routing telemetry alone is insufficient. |
| H4: mechanism transfer | A precisely defined named relationship remains predictive under the declared changes and beats shortcut controls. | Defer until the correspondence and observable are approved. |
| H5: calibration survives | Measure uncertainty quality and selective prediction under held-out conditions. | Report coverage, informativeness, errors among accepted cases, and abstention rate; unknown applicability remains possible. |

The current illustrative sonar/HF ranges do not overlap on all the proposed matching coordinates. Real support must be established before H1 is run. A laboratory acoustic/RF pilot may test portability, as the synthesis itself allows, but must not be presented as validation of the intended sonar/HF transfer claim. [TS §§3, 10–12; SYN §2.8]

## 4. Feature and truth firewall

Each input field is classified as prediction-time metadata, prediction-time measured evidence, a prediction-time estimate, training-only supervision, or evaluation-only reference.

A deployment-path feature builder has access only to the first three. Training-only and evaluation-only data should be exposed through different handles, not merely removed from a tensor by convention. Oracle-regime experiments run through a separately labeled diagnostic path and cannot satisfy deployment promotion gates.

Anchor estimates used for pair creation retain their estimator version, input lineage, uncertainty, and training data scope. Estimated anchors are pseudo-labels, not exact truth. Test reference answers cannot be used to choose model routing, positive pairs, or normalizers in the deployment-path evaluation.

Post-hoc truth-based stratification may be useful for reporting but is labeled as such and does not become a model feature or a prospective applicability guarantee.

## 5. Splits and exposure

Split at the independent unit appropriate to the task, such as session, environment, instrument, scene, or source recording. All derived windows, transforms, and augmentations inherit the relevant root group. Check shared ancestors and near-duplicate policies where applicable.

Freeze test membership before self-supervised pretraining. Report whether target-domain unlabeled training data was used. Access to held-out test inputs without labels is a distinct transductive protocol, not ordinary unseen-domain evaluation.

Fit normalization, regime selection, feature selection, pairing thresholds, and calibration on allowed training/development partitions. The test set cannot guide those choices. Record repeat test inspection and protocol revisions as deviations requiring a new evaluation scope.

## 6. Pairing and simulator evidence

A pair record declares one of four bases: same measured event, controlled corresponding mechanism across distinct simulators, descriptor-matched pseudo-pair, or a deliberately unpaired/negative example. These are not equivalent kinds of supervision.

Use shuffled-pair and nuisance-matched controls where they answer the task's specific shortcut concerns. The fact that two descriptors match does not establish equivalence of their full channel operators.

The proposed replacement for “share no code” is **independent forward-physics implementation and documented generator lineage**. Shared array libraries, coordinate schemas, or file readers are not the scientific problem. Shared latent generators, scene distributions, approximations, or ground-truth construction can remain correlated even when simulator source files differ. Record these dependencies and add measured-data validation before claiming real-world transfer.

## 7. Comparison budgets

Use two separately reported views:

**Adaptation efficiency:** match target labeled data, target unlabeled exposure, adaptation tuning, and adaptation resources. Report source pretraining resources as upstream costs rather than pretending they are zero.

**Total-cost efficiency:** include simulation generation, all pretraining, tuning, adaptation, inference, storage/latency where relevant, and reuse assumptions. State when costs are amortized across multiple target tasks.

For routed models, report total parameters and active parameters, plus measured resource use. Exact simultaneous equality of total parameters, active parameters, FLOPs, wall-clock time, and tuning search is generally not the comparison being made; declare which variables are controlled and report the rest.

Required baseline ladder: direct deterministic or classical task baseline; normalized descriptors plus a simple head; independent target model; target-only pretraining where applicable; pooled/domain-conditioned model; dense shared/private model. Routing is an additional arm, not a replacement for these comparisons.

## 8. Metrics and decisions

For a lower-is-better loss, report an effect such as `delta = baseline_loss - candidate_loss`, so positive delta favors the candidate. Report the original losses as well. Do not use a ratio that becomes undefined at a zero-loss baseline.

Aggregate at the declared independent unit rather than treating windows or multiple seeds as independent observations of the environment. Include uncertainty reflecting both data grouping and training variation where the design permits. Choose the procedure before the final test. With too few independent groups, mark the inference limited or inconclusive.

A positive primary result requires the preregistered practical effect and uncertainty criteria. Evidence against a useful gain requires an appropriately informative comparison; lack of significance alone is not proof of no effect. Secondary metrics and additional directions are reported with their exploratory or adjusted status.

For uncertainty, calibration alone is insufficient: report interval/set informativeness, proper scoring metrics where appropriate, accepted-case error, failure-check rate, and abstention counts. Always include the population denominator so a model cannot appear excellent by hiding most difficult cases.

## 9. Separate records

A RunManifest records one execution attempt. An EvaluationReport aggregates the comparison. A TransferClaim describes what the comparison supports. A Mapping represents an actual proposed/implemented correspondence.

Run status can be succeeded/failed/cancelled. Report validity can be valid/invalid/incomplete. A valid claim can be supported/evidence-against/inconclusive. Negative transfer is a measured result, not a crashed training job.

## 10. Promotion gates

**Software gate:** the runner executes the declared arms, catches injected leakage, preserves failures, and produces reproducible reports.

**Scientific gate:** the evidence supports a bounded transfer statement, with caveats and resource accounting.

**Deployment gate:** the model accepts actual deployment inputs, has appropriate diagnostics and applicability behavior, and satisfies the task's utility requirements on relevant measured data.

Passing the software gate does not imply the other two. Failing the scientific gate does not invalidate a functioning workbench.
