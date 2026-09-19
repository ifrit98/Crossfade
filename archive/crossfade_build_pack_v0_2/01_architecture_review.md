# Crossfade architecture review

## Assessment

The synthesis is useful as a research rationale, and the technical specification is useful as an architectural direction. Neither should be translated mechanically into implementation tickets. Several scientific hypotheses have become unconditional interfaces, and several acceptance gates currently require a preferred experimental outcome rather than a valid experiment.

The strongest existing commitments are separable interoperability/transfer/fusion contracts, immutable evidence, domain-owned observation semantics, explicit identifiability, measured transfer, preservation of negative results, and an LLM over typed results. Preserve these. [TS §§1, 4–6, 10; SYN §§0–2]

The essential v0.2 change is to separate three kinds of statement: an engineering guarantee, a provisional architectural choice, and a scientific hypothesis. A reproducible run is an engineering guarantee. A routed backbone is a provisional choice. Transfer between selected regimes is a hypothesis.

## R01 — Replace one mandatory anchor payload with a typed anchor family

**Source position.** Every pack must estimate `h(tau, alpha)`, and every `AnchorEstimate` must contain its labeled grid. The same spec admits summary-only packs with no anchor estimator. [TS lines 26–59, 117–141, 194, 217]

**Review.** The common channel structure remains a strong candidate anchor. However, interoperability cannot depend on recovering a full channel, and a descriptor estimate cannot truthfully be represented as a recovered complex field.

The source also overstates the narrowband/wideband distinction. Matz, Bölcskei, and Hlawatsch explicitly describe a general delay–Doppler operator representation and note that scaling-based representations can be more parsimonious in the wideband regime. This is not a reason to prohibit delay–Doppler as an operator representation outside a narrowband physical-path approximation. Their channel-statistics section also distinguishes complex spreading functions from second-order scattering functions. [R1]

**Proposed amendment.** Preserve the name `AnchorEstimate`, but add a tagged representation kind, optional payload, named descriptors, uncertainty, normalization, identifiability, and applicability. Permit descriptor-only and unavailable outcomes. Treat representation conversion as a versioned operation with assumptions, not a universal cast. Preserve the distinction between complex channel realizations and power/statistical descriptions.

## R02 — Add TaskSpec before choosing the encoder

**Source position.** Layer 2 estimates the anchor before Layer 3, while H1 measures estimation of anchor descriptors. Section 8 separately shows the encoder consuming observations. [TS lines 91–117, 227–245, 295]

**Review.** These are different model placements. If the answer is already in the anchor supplied to the encoder, a downstream descriptor head may only rediscover a deterministic calculation. A simulator-derived target embedded in routing coordinates would be a more serious form of leakage.

**Proposed amendment.** A versioned `TaskSpec` declares prediction-time inputs, target quantities, evaluation truth, permitted nuisance information, baseline, metric, and uncertainty meaning. Distinguish three experiments: a deterministic descriptor calculation from an existing channel representation; estimation from actual measurements; and transfer of the measurement-to-descriptor estimator. Only the third tests learned transfer. Ground-truth anchors and target-derived regime coordinates stay on the supervision/evaluation side unless explicitly available at deployment.

## R03 — Treat C0–C3 as descriptions, not permissions

**Source position.** C2 supports coherent estimation and C3 supports full estimation and blind deconvolution. [TS lines 134–155]

**Review.** Data richness is not proof of source knowledge, calibration, synchronization, processing invertibility, or physical identifiability. The blind-deconvolution reference requires structural assumptions; raw samples alone do not remove ambiguity. [R6]

**Proposed amendment.** Retain C0–C3 for familiar display terminology. Authorize operations using explicit capabilities and task-specific preconditions. Return supported, conditionally supported, unsupported, or unknown, with reason codes. A pack can be useful without a forward model or anchor estimator.

## R04 — Make regime matching a hypothesis, and check that matching is feasible

**Source position.** Matching dimensionless coordinates should imply shared structure; distant coordinates should not transfer. The illustrative sonar and HF values are disjoint in both speed ratio and fractional bandwidth. The pilot nevertheless requires overlap in those coordinates. [TS lines 63–85, 295–299, 344–351; SYN lines 127–140]

**Review.** Those illustrative intervals cannot support the proposed matched-regime test as written. The spec calls the values placeholders, so this is a pilot feasibility issue, not proof that real overlap is impossible. More generally, equality in a selected set of dimensionless groups does not establish equality of all omitted governing relationships or task distributions.

IT-pi supports data-driven identification of useful dimensionless variables and conditional predictive limits. It does not validate this particular coordinate set or prove cross-medium equivalence. [R5]

**Proposed amendment.** Make each coordinate task-scoped, provenance-bearing, nullable, and marked as available at inference or supervision-only. Add an actual support-overlap check before model training. Use distant regimes to measure the transfer surface, not to demand a negative result. Do not declare every interior point of a sparsely sampled box validated.

## R05 — Change “MoE is the answer” into an ablation

**Source position.** The encoder is a regime-routed mixture of experts; the cited literature is said to demand routing. [TS lines 223–260; SYN lines 148–156]

**Review.** The checked routing paper studies two fluid regimes and reports domain-separated routing and simultaneous low validation error. Its discussion limits what the experiment establishes. It does not demonstrate that this architecture is best for Crossfade's inverse tasks or that explicit dimensionless-coordinate routing is required. [R3]

CSI-CLIP++ is a relevant paired-view precedent, but its implementation uses ideal simulated CSI and CIR constructed by IFFT, generally without SNR-dependent noise. This is narrower evidence than blind inference from legacy observations. The spec's bibliography also attributes the paper to Wang et al.; the checked paper is by Jun Jiang et al. [R2]

**Proposed amendment.** Compare deterministic features, independent models, a pooled model, and dense shared/private variants before optional routing. Start small self-supervised trials in parallel only after split and transform contracts exist. Record oracle, estimated, and empirical supervision distinctly; do not call estimated anchor targets ground truth.

## R06 — Uncertainty and forward validation need meaningful unavailable states

**Source position.** Every inverse question must return a posterior and every explanation must pass through forward checking, although forward/observation models can be absent. Uncertainty applicability is a Boolean. [TS lines 159–194, 268–285]

**Review.** A prior-conditioned posterior, a confidence interval, an ensemble summary, a deterministic calculation, and unavailable uncertainty are different outputs. Missing models cannot be replaced with an invented posterior or a fictitious successful check. SBI's diagnostic workflow is conditional on the simulator, prior, and chosen data representation. [R8]

**Proposed amendment.** Type uncertainty explicitly. Make applicability in-scope, out-of-scope, or unknown. Make forward checks passed, failed, unavailable, or not applicable. Propagate an anchor's uncertainty when it is used downstream; otherwise label the result as conditional on a plug-in estimate. Separate computational completion from scientific validity.

## R07 — Provenance is not a dependence model

**Source position.** Shared lineage and use of the same upstream model imply correlated results. [TS lines 153, 287]

**Review.** Provenance identifies derivation and reuse. It does not supply a covariance matrix or prove that distinct records are independent. Shared observations and shared model versions are different kinds of dependency. PROV-O describes provenance, not probabilistic combination rules. [R10]

**Proposed amendment.** Record evidence overlap separately from model-error dependency. Default to withholding numerical fusion when dependence is unknown. Keep same-event association separate from similarity or cross-domain analogy. Read-only comparison and duplicate-evidence warnings can ship well before quantitative fusion.

## R08 — Audit transformation semantics and numerical metadata

**Source position.** Resampling/window choice and carrier retuning are classified as convention changes; all evidence is xarray with units in attributes. [TS lines 143–150, 182, 192]

**Review.** A unit relabeling with a correct reversible conversion is not the same operation as discarding samples, changing the analysis window, or acquiring a different frequency band. Under the supplied generative model, a changed physical acquisition may change the observation operator. The transformations therefore need individual equivalence tests, not a global invariant designation.

Xarray does not enforce arbitrary attribute semantics. Attaching a units attribute does not itself validate dimensional compatibility or prevent an inappropriate alignment. [R9]

**Proposed amendment.** Separate exact convention changes, coordinate transformations, lossy processing, and physical interventions. Preserve normalization and processing parameters. Use validated array payloads where appropriate, structured records for C0, and an immutable raw-artifact layer for incomplete evidence awaiting metadata.

## R09 — Separate experiment completion from positive findings

**Source position.** A1 passes when H1 is supported and H2 is not violated; mappings have supported/unsupported verdicts. All baselines must match parameters, data, and compute simultaneously. [TS lines 289–345]

**Review.** The current gate can reject an unexpected successful transfer to a distant regime or treat an inconclusive trial as a negative finding. It also mixes target-data efficiency with end-to-end compute efficiency. A sparse model's active parameters are not its total parameters.

**Proposed amendment.** Complete the slice when a preregistered valid comparison produces a report. Promote the model only on its declared utility and uncertainty gates. Include supported, evidence-against, and inconclusive claim outcomes; keep invalid evaluation separate. Report adaptation-budget and total-cost comparisons separately, including unlabeled-data access, tuning effort, active parameters, and pretraining cost. Separate individual runs from comparison reports and transfer claims.

## R10 — Decouple useful integration from the research result

**Source position.** The workbench remains useful without transfer, but output-only integration is scheduled after simulation and reality gates. Public data is described generically and the schedule assumes a three-person team. [TS lines 9–15, 338–361]

**Proposed amendment.** Run a software workbench lane and a scientific-validation lane. A summary-only adapter can ship when its contract is tested; it need not wait for cross-domain transfer. Do not attach an unvalidated learned inference to that adapter. Replace calendar commitments with dependency gates until real data manifests, simulator access, staffing, and task scope are confirmed.

## What is ready to implement

S00, S01, S02, and S04 can be specified against a small synthetic fixture immediately. S03 requires a signed-off target quantity and approved domain reference operations. S05 and S06 require frozen splits and a feasible pairing/overlap protocol. S09 is optional. The scientific goal remains intact, while failed transfer no longer blocks a useful evidence-and-experiment platform.
