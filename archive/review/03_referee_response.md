# Response to the v0.2 architecture review

*Written 2026-09-18. Examines each claim in `review/01_architecture_review.md` and `review/02_contract_amendments.md` against the sources and from first principles. Verdicts: ACCEPT, ACCEPT WITH MODIFICATION, PUSH BACK.*

---

## 0. Summary verdict

The review is correct on its central framing and on every factual check it ran. Its most valuable contributions are R02 (TaskSpec and the anchor's role per experiment), R04 (the regime-overlap contradiction), R09 (H2 must not be a gate), and the identifiability correction on paired views. Those four change the science, not just the paperwork.

Where I push back is on three things: the anchor family must keep a canonical kind per regime or the "spine" degenerates into "any descriptor"; the "no shared code" rule should be kept alongside the review's independence documentation rather than replaced by it; and the T0 fixture is too far from a real task to shape the contracts on its own, so S03's target quantity has to be chosen now, not after S00–S02.

Two of the review's corrections are corrections of my errors, and I want to name them plainly. I overstated the narrowband/wideband distinction as existence rather than parsimony. I mis-attributed CSI-CLIP++ to "Wang et al."; the authors are Jun Jiang, Wenjun Yu, Yunfan Li, Yuan Gao and Shugong Xu. The doc has been corrected.

| Item | Verdict | One-line reason |
|---|---|---|
| Framing: separate guarantees, provisional choices, hypotheses | ACCEPT | This is the right epistemic hygiene and it was already implicit in both plans |
| R01 Typed anchor family, optional payload | ACCEPT WITH MODIFICATION | Keep a canonical kind per regime and versioned conversions, or the anchor stops being an anchor |
| R01 Delay-Doppler is general, scaling is parsimonious | ACCEPT | Verified in the source; my spec was wrong on this point |
| R02 TaskSpec; anchor role fixed per task | ACCEPT | Real ambiguity in the spec; real leakage risk in simulation |
| R03 C0–C3 describe, preconditions authorize | ACCEPT | Tiers are necessary conditions, never sufficient ones |
| R04 Regime overlap is infeasible as tabulated | ACCEPT | My own table is disjoint in `v/c` and `B/f_c`; the pilot demanded overlap in both |
| R04 Regime coordinates are task-scoped hypotheses | ACCEPT WITH MODIFICATION | Yes, but the disjointness is itself a scientific result that sharpens the hypothesis; see §2 |
| R05 MoE is an ablation, not a mandate | ACCEPT | Shodh-MoE covers two fluid regimes; I generalized too far |
| R05 CSI-CLIP++ is ideal-CSI evidence | ACCEPT | Verified: perfect ray-traced CSI, IFFT CIR, no SNR noise |
| R05 Paired-view identifiability does not name physical factors | ACCEPT | The strongest correction in the review; see §3 |
| R06 Typed uncertainty and forward-check states | ACCEPT | Boolean `in_scope` was under-specified |
| R07 Lineage is not a dependence model | ACCEPT WITH MODIFICATION | Withhold numerical fusion by default, but shared-observation lineage does license one conservative rule |
| R08 Resampling, windowing, retune are not conventions | ACCEPT | I was wrong; they are lossy processing or physical changes |
| R08 xarray attrs are not validated | ACCEPT | Use pint-xarray or an explicit validator |
| R08 C0 as structured records | ACCEPT | Forcing summaries into tensors was a mistake |
| R09 Experiment delivery vs scientific support vs promotion | ACCEPT | H2 as a gate could reject a discovery |
| R09 Separate RunManifest, EvaluationReport, TransferClaim, Mapping | ACCEPT | Records, not services; cheap |
| R09 Budget accounting: adaptation vs total, active vs total params | ACCEPT | Standard and necessary |
| R10 Output-only integration decoupled from transfer | ACCEPT | This was plan 2's own point and I sequenced it wrongly |
| R10 Replace calendar with dependency gates | ACCEPT WITH MODIFICATION | Gates for engineering; keep rough durations for the funding conversation |
| Two-simulator rule: replace "no shared code" | PUSH BACK | Keep both; code independence is a cheap auditable proxy, assumption independence is the real target |
| T0 fixture (RMS width of a supplied PDP) | ACCEPT WITH MODIFICATION | Fine as a contract test; insufficient to shape the contracts; pick S03's quantity now |
| Deterministic rule-based planner in v0.2 | ACCEPT | Obviously right |
| Packs as trusted executable code, constrained workers | ACCEPT | Sensible and cheap |
| Product definition: "capability-aware evidence and experiment platform" | ACCEPT WITH MODIFICATION | Right for v0.2 engineering; must not lose plan 1's forward-model core as the semantic target |

---

## 1. R01: the anchor

**What the review gets right.** The spec said every pack must estimate `h(τ, α)` and every `AnchorEstimate` carries a labeled grid, and in the same document allowed output-only packs with no estimator. That does not compose. And the claim that delay-scale is "the correct description" for wideband channels was an overstatement. Matz, Bölcskei and Hlawatsch state that virtually any linear channel is a superposition of time-frequency shift operators; the delay-Doppler spreading function always exists. Scaling representations are "more parsimonious" in the wideband regime. The correct statement is about sparsity, not existence: a wideband channel with a few discrete moving paths is sparse in delay-scale and smeared in delay-Doppler.

**Where I push back.** The review's typed family with optional payload is right, but as written it lets "anchor" mean "whatever descriptors this pack happens to produce." That loses the thing that made the anchor useful: a shared target that cross-domain pairing is defined against. Two amendments preserve the review's flexibility without that loss:

1. **Each regime declares a canonical representation kind**, chosen by sparsity: delay-scale where `M · β_B · T · B` exceeds a declared threshold, delay-Doppler otherwise. The threshold is a pack-declared, tested number, not routing logic baked into the core.
2. **Descriptors are defined as functionals of the canonical kind**, even when only the descriptor is estimated. RMS delay spread is a functional of the power-delay profile, which is a marginal of the scattering function. A descriptor-only pack still says which functional of which canonical object it is estimating. That is what makes descriptors from two packs comparable.

This keeps the review's "common vocabulary, not common reconstruction" while keeping the vocabulary anchored to physics.

**Spreading versus scattering.** The review is right that these must not be conflated. The spec did write `S_H` for the realization and `C_H = E|S_H|²` for the statistic, but the `AnchorEstimate` object did not carry the distinction. The review's `statistical_semantics` field (realization, expectation, estimate, posterior samples, pseudo-label) is the correct fix.

---

## 2. R04: regime coordinates and the overlap contradiction

**The contradiction is real and it is mine.** Section 3 of the spec tabulates sonar at `M` in [1e-3, 1e-2] and `β_B` in [0.3, 1], HF at `M` in [1e-6, 1e-5] and `β_B` in [1e-3, 1e-2]. Section 11 then requires the simulation grid to overlap in `(M, β_B, Π_τ, Π_f)`. Those two sections cannot both be satisfied.

**But the review under-reads what the contradiction means.** It treats it as a pilot-feasibility bug. From first principles it is a scientific result: if sonar and HF never overlap in `M` and `β_B`, then the dimensionless-matching hypothesis itself predicts that the Doppler-treatment structure of the channel does not transfer between them, and that whatever transfers must live in the coordinates that do overlap: `Π_τ` (delay spread in resolution cells), `Π_ν` (Doppler spread over observation), `Π_f` (modes above cutoff), `Π_L` (aperture in wavelengths). Those are the coordinates governing multipath arrival structure, modal interference, and waveguide fading. That is exactly the "ionosphere as flipped ocean" intuition from the transcript, now stated as: the shared structure is the waveguide, not the Doppler.

So the amendment I would make is stronger than the review's:

> Regime matching is per-coordinate and per-descriptor. The hypothesis is that a descriptor transfers between two systems to the extent that the dimensionless groups governing that descriptor overlap. `M` and `β_B` govern Doppler descriptors; `Π_τ`, `Π_f`, `Π_L` govern arrival and interference descriptors. The sonar-HF pilot should therefore test arrival-structure and interference descriptors first, and should expect Doppler descriptors not to transfer.

This makes the review's "measure the transfer surface as a function of overlap distance" the operationalization, and it makes H4 (waveguide-invariant-style mechanism transfer) the primary hypothesis rather than an add-on. I accept the review's fields on each coordinate (provenance, missingness, inference-time availability) without reservation. The oracle-coordinate leakage concern is real in simulation: if `Π_τ` is computed from the simulator's true delay spread and the target is delay spread, the router has the answer. Inference-time coordinates must be estimated from permitted inputs or from metadata that would genuinely be available.

**On IT-π.** The review is right that IT-π does not validate this coordinate set. It ranks candidate groups by predictive information for a given target. That is precisely the tool for the per-descriptor version of the hypothesis above: run it per descriptor, per domain, and see whether the same groups rank highest in both. Agreement is evidence for shared governing physics; disagreement locates where the analogy breaks.

---

## 3. R05: the identifiability correction on paired views

This is the most important technical correction in the review and I want to reason through it rather than just accept it.

**The spec's claim.** Intra-domain multi-view contrastive learning among raw signal, time-frequency view, and anchor estimate of the same recording makes shared content identifiable, citing von Kügelgen et al. and Gresele et al.

**Why that is wrong as stated.** The von Kügelgen result identifies the content partition, the latent factors invariant across the two views, up to an invertible map. It requires that the views differ by *independent style variation*. If view B is a deterministic function of view A (a spectrogram is a deterministic function of the waveform; an IFFT-derived CIR is a deterministic function of CSI), then the "content" shared between them is simply all the information in the coarser view. There is no style to strip. Contrastive learning on such pairs learns an encoder consistent across representations, which is useful as an interface test, but it does not isolate a physical factor. Gresele's multi-view result similarly needs views that are *different noisy mixings* of the same sources.

**What follows.** The views that do carry independent nuisance variation, and therefore can isolate physical content, are:

- Different receivers or sub-arrays observing the same event (independent instrument noise and geometry)
- Different time windows of a stationary source through a slowly varying channel (independent noise realizations, shared channel structure)
- Different processing chains applied by different upstream systems to the same recording (independent processing artifacts)
- Simulated pairs with controlled variation: same channel, different source; same source, different channel. This was plan 1's proposal and it now looks like the right one.

The deterministic re-representations (waveform, spectrogram, CIR of one recording) should be retained as *consistency* losses, which is what CSI-CLIP++ actually demonstrates, and not described as identifiability-conferring. The spec's loss L2 should be split into L2a (representation consistency, deterministic views) and L2b (content isolation, independently varying views), with only L2b claimed as an alignment basis.

**On CSI-CLIP++.** Verified: perfect ray-traced CSI from DeepMIMO, CIR by IFFT along subcarriers, and "SNR-dependent noise effects are not considered." It is evidence that CIR-CSI consistency pretraining yields a transferable encoder under ideal acquisition. It is not evidence about blind inference from noisy, heterogeneous, legacy outputs. The spec cited it correctly for the anchor-as-pretraining-target idea and over-cited it for the harder claim.

---

## 4. R02: TaskSpec and the anchor's role

**Accept in full.** The spec placed L2 (anchor estimator) before L3 (encoder) in the architecture, showed the encoder consuming observations in the training diagram, and evaluated H1 on anchor-descriptor estimation. My intent was that L2 classical estimators produce training targets and paired views while the encoder consumes observations, but I never wrote that down, and the review is right that an encoder given an estimated channel and asked for a functional of it is doing arithmetic, not inference.

The three-task distinction (compute a descriptor from a supplied channel; estimate it from permitted observations; transfer that estimator) is the right ladder. Only the third tests the research claim. Every experiment must state which one it is.

One addition: the TaskSpec's `allowed_features` must explicitly enumerate which regime coordinates are available at inference time and how each is estimated. This closes the leakage path in §2.

---

## 5. R07: lineage and fusion

**Accept the principle.** PROV records derivation, not covariance. Two results from the same observation are not independent, but knowing that does not give you the joint distribution.

**One modification.** Shared-observation lineage does license one conservative rule without any dependence model: never multiply likelihoods from two views of one observation; treat them as one piece of evidence, taking the more conservative of the two. That is a valid v0.2 fusion rule for the duplicate-evidence case. Model-error dependency (two different models on different observations, sharing a training set or an architecture) is the case where dependence is genuinely unknown and fusion should be withheld. The review's "record evidence overlap and model-error dependency separately" is right; I would just not let "withhold by default" block the one case that has a safe answer.

---

## 6. R08: transformation semantics

**Accept, and I was wrong.** The spec called `fs` resampling and window choice "convention" and carrier retune within band "convention." Resampling discards information unless the signal is oversampled; window choice changes the observation operator `M_d`; retuning the carrier observes a different physical channel. Under the spec's own generative model these are lossy processing and physical intervention respectively. The review's four-way split (exact convention, coordinate transform, lossy processing, physical intervention) with per-transformation equivalence tests is correct. The only exact conventions in the original list are unit relabeling and array-coordinate rotation.

---

## 7. R09: gates

**Accept.** H2 (zero or negative transfer at mismatched regime) as a gate condition would fail the pilot if transfer unexpectedly appeared across a regime boundary. That is backwards; such a result would be the most interesting thing the pilot could produce. Preregister H2 as a prediction, measure the transfer surface, and gate only on: was the comparison run validly (delivery), what does it support (scientific), and is the model useful for its declared inputs (promotion).

The budget-accounting split is also right. A pretrained encoder that needs fewer target labels and more total compute is two true statements, and a sparse MoE's active parameters are not its total parameters.

---

## 8. Where I push back

### 8.1 The two-simulator rule

The review replaces "no shared code" with "documented independence of forward-physics and data-generation assumptions, followed by measured-data validation." The target is right: shared scene distributions, shared approximations, and shared truth construction produce correlated evidence even with disjoint code. But "documented independence" is a judgment, and "no shared code" is a cheap, mechanically auditable proxy that catches the most common failure (one channel model, two labels). Keep both. Require no shared physics kernel *and* a written independence statement covering scene distribution, approximation family, and truth construction. Drop neither.

### 8.2 The T0 fixture and the shape of the contracts

T0 (weighted RMS width of a supplied delay-power profile; equal weights at 0 and 2 ms gives mean 1 ms, RMS width 1 ms, normalized 0.5 against a 2 ms reference) is a fine contract test. It exercises units, normalization, replay, partial capability, result states. Accept it.

But the review proposes six new contracts (TaskSpec, OperationSpec, CapabilityAssessment, RunManifest, EvaluationReport, TransferClaim) plus amendments to six existing ones, and proposes to build S00–S02 and the fixture version of S04 against T0 before S03 has a target quantity. That is the governance-heavy failure mode the synthesis flagged in both original plans, now with more objects. Contracts shaped only by a toy will be reshaped by the first real task. The review's own answer is that S03 needs a signed-off quantity, which puts the sonar lead's answers to section 12 on the critical path.

So: choose S03's target quantity now, in parallel with S00. The natural first real task, given what the sonar lead already runs, is **RMS delay spread and resolvable-arrival count from beam time series in simulation at C3**, with the classical cepstral and ray-based estimators as baselines. It is a functional of the canonical anchor, it has exact truth in simulation, it has a classical baseline, and it is the descriptor whose governing groups (`Π_τ`, `Π_f`) plausibly overlap between sonar and HF per §2. Let that task and T0 shape the contracts together.

### 8.3 Calendar versus gates

Accept dependency gates for engineering sequencing. But the pitch to Tim is a funding conversation, and funding conversations need durations. Keep the rough sizing as a planning estimate labeled as such, gated on the listed dependencies. Removing all durations from the document that goes to Tim would be a mistake.

### 8.4 Product definition

The review's "capability-aware evidence and experiment platform for wave-propagation inference" is the right v0.2 engineering definition. It is also, essentially, plan 2's framing winning over plan 1's. That is correct for what gets built first. The thing to protect is that plan 1's generative formulation `y_d = M_d[F_d(θ_shared, θ_private; c_d)] + ε_d` remains the *semantic target* that TaskSpec, OperationSpec and AnchorEstimate are typed against, even where `F_d` is absent. The review keeps forward validation "when available" and keeps the anchor as a candidate, so this is compatible. I flag it because a platform whose contracts are all "optional, unavailable, unknown" can drift into a provenance system with no physics in it. The canonical-kind rule in §1 and the S03 task in §8.2 are the guardrails.

---

## 9. What I would do next

1. Adopt the review's contract amendments with the three modifications above (canonical kind per regime; keep no-shared-code alongside independence documentation; conservative duplicate-evidence fusion rule).
2. Rewrite spec section 3 to state regime matching per descriptor, and section 8 to split L2 into consistency and content-isolation losses. Rewrite section 10's H2 as a prediction, not a gate. Rewrite section 6's transform classification.
3. Put the S03 target quantity to the sonar lead as the first question, ahead of the rest of section 12: is RMS delay spread plus arrival count from beam time series the right first descriptor, and which simulator produces truth for it?
4. Start S00 (T0) and S01 immediately. Start S03's spec the day the quantity is agreed. Do not let S04's fixture version run ahead of S03's spec.
5. Update the citation to CSI-CLIP++ (done) and add the ideal-acquisition caveat wherever it is cited.
