# Refereeing Plan 1 and Plan 2: Overlap, Disagreement, and a Synthesis

*Written 2026-09-17. Sources: `context.md` (transcript), `plan1.md` (first-principles), `plan2.md` (physics-informed framing), plus the literature below. Every paper cited in either plan was checked against arXiv or the publisher and exists as described.*

---

## 0. The short verdict

The two plans agree on roughly eighty percent of their content, and the agreement is on the things that matter most. Both reject a universal PINN. Both reject an LLM as the glue. Both convert the transcript's "shared spine" into a shared/private representation with domain-specific pathways. Both insist on an evidence contract with provenance, units, and coordinates. Both make transfer a measured property rather than an assumption. Both demote the LLM to an explanation and orchestration role over typed records.

Where they differ, the difference is in emphasis, and the emphases are complementary:

- **Plan 1 is stronger on the scientific core.** It writes down the generative structure, `y_d = M_d[F_d(θ_shared, θ_private; c_d)] + ε_d`, and derives the architecture from it. It handles blind-deconvolution identifiability, wideband versus narrowband channels, and the "same simulator twice" trap.
- **Plan 2 is stronger on the organizational core.** It gives you the representation atlas, the capability registry, the evidence graph, PROV-O and MLflow, and a workbench that stays useful when every transfer hypothesis fails.

The synthesis is not a compromise. It is Plan 1's physics as the semantic content of Plan 2's containers. The atlas's mappings become statements about `θ_shared` under declared observation models. The regime conditioning becomes a coordinate system, not a label.

Three things neither plan does, and which the literature now supports, are the actual contribution of this document:

1. **Name the anchor.** The transcript's own intuition, that the time-varying impulse response or scattering function is the common thread, should be made literal: the delay-Doppler (narrowband) or delay-scale (wideband) spreading function is the anchor representation that every domain pairs to. This is the ImageBind trick applied to wave physics, and there is now direct RF precedent (CSI-CLIP++).
2. **Make the regime a dimensionless coordinate.** Both plans say "condition on regime, not domain label." Neither says what a regime is. Dimensionless groups such as `v/c`, `B/f_c`, and delay-spread times bandwidth are the regime coordinates. That turns "does it transfer?" into a preregisterable hypothesis: transfer at matched dimensionless regime, no transfer at mismatched.
3. **Take self-supervised pretraining on paired views seriously.** The transcript asks what training objective would align the spaces "naturally." The RF and sonar literature of the last eighteen months has a partial empirical answer: masked modeling plus contrastive alignment of physically paired views of the same recording. That also supplies the "alignment basis" Plan 2 correctly demands.

---

## 1. Where the plans agree

| Theme | Plan 1 | Plan 2 | Shared source |
|---|---|---|---|
| Not a universal PINN, not LLM glue | §4 "Why I would not make a monolithic PINN the default" | Opening: "not a universal PINN" | Krishnapriyan et al. 2021 (PINN failure modes) |
| Shared + private representation | §3C partially shared backbone, private residual pathways | §3B three-part representation | Domain Separation Networks (Bousmalis 2016); Zhao et al. 2019 on the limits of invariance |
| Invariance is not the goal | §4 equivariance, not indiscriminate invariance | §3B conditional sharing; §5 geometric DL | Zhao et al. ICML 2019 |
| Identifiability | §2 correction three (blind deconvolution) | §3A alignment basis (latent identifiability) | Locatello et al. 2019; Li/Lee/Bresler 2015; Gresele et al. 2020 |
| Physical normalization before learning | §4 Buckingham Pi | §3C Buckingham Pi + IT-π | Bakarji et al. 2022; Yuan & Lozano-Durán 2025 |
| Information preservation | §2 correction two: archive raw, make shared latent task-sufficient | §3E evidence archive vs task representations | Tishby et al. information bottleneck |
| Uncertainty under shift | §3E calibration under held-out conditions | §3F validity scope on every uncertainty | Ovadia et al. 2019 |
| Simulation-based inference | §3D SBI engine, `sbi` library | §3F SBI as complementary direction | Deistler et al. 2025 guide; Dax/Heimel/Louppe 2026 |
| Neural operators / physics FMs are components | §4 FNO, Poseidon, Walrus, PROSE-PDE, CompNO | §3D Kovachki, UPT; §6 Walrus, GPhyT | Walrus (ICML 2026); Wiesner et al. 2026 |
| Evidence contract with provenance | §3A evidence layer, §3E lineage | Component 1, PROV-O | xarray |
| Domain packs / packages | §3B | Component 2 | — |
| LLM last, on typed records; feedback split by category | §3F | Component 7 | — |
| Two-domain pilot, strong baselines, held out by session/instrument/regime, negative transfer measured | §5 | §7 | DomainBed (Gulrajani & Lopez-Paz 2020) |
| Modular Python app, workers, relational metadata, not microservices | §6 | §8 | — |

Read side by side, these are the same architecture described by two people who never spoke. That is a reasonably strong signal that the architecture is the right one, because it was reached from a first-principles route and from a physics-modeling route independently.

---

## 2. Where they differ, and who is right

### 2.1 Inference problem versus workbench

Plan 1 makes the forward model the organizing object. Every domain contributes `F_d` and `M_d`, the shared quantity is `θ_shared`, and "forward validation" (does the inferred explanation reproduce the observed evidence through the actual measurement chain?) is a standard operation.

Plan 2 makes the software the organizing object. Models are components with declared capabilities; representations and mappings live in an atlas; the evidence graph records support and contradiction.

**Referee call: Plan 1 is right about what the system *means*; Plan 2 is right about what the system *is*.** Without Plan 1's formulation, Plan 2's atlas has no criterion for what a mapping is a mapping *of*. Without Plan 2's containers, Plan 1's inference engine has nowhere to record why a result should be trusted six months later. Use Plan 1's equation as the type signature of every entry in Plan 2's atlas.

### 2.2 Regime conditioning versus representation atlas

Plan 1 conditions the model on "physical regime, not domain label," and lists candidates: bandwidth regime, phase availability, sampling structure, medium variability. Plan 2 builds an atlas of scoped mappings with semantic, task, and regime scope.

**Referee call: these are the same idea at two levels.** The atlas is the bookkeeping; regime conditioning is what the weights do. What both are missing is the coordinate system. See §3.2 below.

### 2.3 Two kinds of identifiability

Plan 1 treats identifiability as a property of the physical inverse problem: source and channel are only jointly recoverable under structural assumptions (sparsity, known array geometry, modal phase structure). Plan 2 treats it as a property of the learned representation: two autoencoders can reconstruct perfectly and organize their latents differently, so you need an alignment basis.

**Referee call: both are necessary and they compose.** The physics identifiability tells you which quantities *can* be in `θ_shared`. The representation identifiability tells you whether the learned encoder actually put them there. A useful reading of Gresele et al. (Incomplete Rosetta Stone) and von Kügelgen et al. (content isolated from style) is that shared content across sufficiently different views of the same latent *is* identifiable, and the way you get "sufficiently different views" in this project is by pairing raw I/Q, spectrogram, and estimated impulse response of the same recording. That is a labeled-data-free alignment basis.

### 2.4 The "same simulator twice" trap

Plan 1 §5 makes a point Plan 2 does not: transfer between two datasets generated by one channel model with different labels is not cross-domain transfer, it is learning one simulator twice. It insists on independently constructed acoustic and electromagnetic simulators.

**Referee call: Plan 1 wins outright, and this should be a hard rule in the benchmark.** Use an acoustic waveguide model (normal-mode or ray) and an HF ionospheric ray tracer that share no code. The 2025 open-source ionospheric propagation code and RTM-GD discretized-ionosphere ray tracing are candidates on the RF side; standard ocean acoustics toolboxes exist on the acoustic side.

### 2.5 Wideband versus narrowband

Plan 1 §2 notes in one sentence that "wideband effects may call for time scaling rather than simple frequency shifts." Plan 2 does not mention it.

**Referee call: this single sentence is the most important physics in either plan, and it deserves a section.** See §3.1.

### 2.6 What Plan 2 adds that Plan 1 lacks

- **Normal-form autoencoders** (Kalia et al. 2021): learn a coordinate change that puts a system into canonical form. This is the most precise version of "find a simpler shared description while retaining domain-specific coordinates." Keep it as a research branch.
- **In-context operator learning** (ICON, Yang et al. 2023, PNAS): adapt to a new operator from a small context package without weight updates. Worth evaluating as the mechanism by which a new bathymetry or ionospheric state is absorbed at inference time rather than by retraining.
- **Model capability registry** answering "what question can this model answer from these inputs?" MLflow as the base.
- **Evidence graph is not a GNN.** A software requirement, not a modeling choice. Good discipline.
- **PROV-O** vocabulary for lineage.

### 2.7 What Plan 1 adds that Plan 2 lacks

- The explicit generative equation and the forward-validation loop.
- Blind-deconvolution identifiability with the scale-ambiguity example.
- PROSE-PDE and CompNO as evidence that symbolic structure and compositional operator libraries help multi-operator learning.
- The five capability gates (evidence, baseline, transfer, reality, integration). These are better sequencing than Plan 2's milestones because each gate names the claim it protects.
- DomainBed as the methodological warning: well-tuned empirical risk minimization is hard to beat, and model selection procedure changes conclusions.

### 2.8 Scope of the pilot

Plan 2 scoped its illustrative pilot to room acoustics and laboratory RF channel characterization, with reconstruction and uncertainty as tasks, and explicitly did not extend to detection or tracking. Plan 1 stayed with the transcript's application.

**Referee call: on the technical merits, Plan 2's choice is a legitimate de-risking move regardless of why it was made.** Open datasets with ground-truth channel measurements exist for both room acoustics and indoor RF, and a pilot on them tests the *transfer machinery* without any of the confounds of low-SNR operational data. The application-specific question is one for the team. The pilot design itself (two independent domains, matched regime, held-out sessions, negative transfer measured) is identical either way. Note also that the title of Plan 2 as "the PINN perspective" is a misnomer: Plan 2 spends less than a paragraph on PINNs and its actual center of gravity is identifiability and software contracts.

---

## 3. What neither plan says, and the literature now supports

### 3.1 The anchor is the spreading function, and its regime is set by `v/c` and `B/f_c`

The transcript's best moment is when the sonar engineer says the common thread is "the impulse response function of the channel or the scattering function of the channel," and that if you can estimate it "you've won." Both plans nod at this and then move to generic latent spaces. Make it literal.

**Narrowband regime (radar, HF, most comms).** Bello's WSSUS model characterizes the channel by a scattering function `C_H(τ, ν)` in delay and Doppler frequency. Matz and Hlawatsch's time-frequency channel framework extends this to non-WSSUS channels via a local scattering function. Doppler is a frequency shift because `v/c` is of order `1e-6`.

**Wideband regime (sonar, some UWB).** When `v/c` is of order `1e-3` to `1e-2` and the bandwidth is an octave, Doppler is a *time scaling* `t → (1 + v/c) t`, not a shift. The correct channel description is the wideband spreading function `h(τ, α)` in delay and scale. Altes (1971) and later work show that the wideband ambiguity function and the Mellin transform are the natural tools; the Fourier-Mellin transform is invariant to both delay and scale.

**The unification.** The delay-scale representation contains the delay-Doppler representation as the limit `α → 1`. So the anchor is the delay-scale spreading function, and the domain pack declares where on the `v/c`, `B/f_c` plane it lives. Whether a given radar task can use the narrowband approximation is then a *derived* property of its dimensionless coordinates, not a hand-written flag.

**Precedent that this works as an ML anchor.** CSI-CLIP++ (Wang et al., arXiv 2606.25714) pretrains an RF channel foundation model by treating frequency-domain channel state information and delay-domain channel impulse response as *paired views of the same propagation process*, aligns them contrastively, and transfers the encoder to channel identification, beam prediction, and positioning, with cross-simulator transfer. That is, in one RF sub-domain, exactly the mechanism proposed here. ImageBind (Girdhar et al. 2023) is the general lesson: you do not need pairwise alignment among all N modalities, you need each modality paired to one anchor.

**What this buys the architecture.** Plan 2's atlas gets a hub. Plan 1's `θ_shared` gets a concrete first member: the spreading function's structural descriptors (delay spread, scale/Doppler spread, arrival sparsity, modal interference structure). Every domain pack must supply an estimator to the anchor, classical or learned, with its identifiability assumptions stated. Domains that cannot reach the anchor (magnitude-only spectrograms from a legacy system) get a declared capability level, exactly as Plan 1 §3A requires.

### 3.2 Regime coordinates are dimensionless groups

Both plans invoke Buckingham Pi and IT-π (Yuan & Lozano-Durán, Nature Communications 2025) for normalization. Go one step further: the dimensionless groups *are* the regime coordinates.

Candidate groups for wave sensing:

| Group | Meaning | Sonar (typical) | HF radar (typical) |
|---|---|---|---|
| `v/c` | target or platform speed over propagation speed | `1e-3` to `1e-2` | `1e-6` |
| `B/f_c` | fractional bandwidth | up to 1 | `1e-2` |
| `τ_spread · B` | delay spread in resolution cells | large | moderate |
| `ν_spread · T` | Doppler spread over observation time | varies | varies |
| `L / λ` | array aperture in wavelengths | tens | tens to hundreds |
| `f / f_cutoff` | frequency relative to waveguide mode cutoff | order 1 to 10 | order 1 to 10 |

Two systems at the same point in this space should share `θ_shared` structure regardless of whether the medium is water or plasma. Two systems far apart should not, and a model that claims transfer between them is suspect. IT-π can rank which groups actually carry predictive information for a given task and identify regime boundaries from data. That is how the atlas gets its map.

This is also the answer to the transcript's practical-engineering question ("what do I set my FFT lengths to for HF versus sonar?"): the windowing choice is a function of `ν_spread · T` and `τ_spread · B`, and once expressed that way it is the same decision in both domains.

### 3.3 Waveguide invariant as the first "mechanism transfer" test

The transcript mentions striation patterns on spectrograms as a source of physics-based features (speed, approach versus recede). In ocean acoustics this is the waveguide invariant `β`, which summarizes the interference between propagating modes and produces range-frequency striations. It is a mature technique: waveguide-invariant ranging from ship noise in a 7 Hz band reached 45 km with under three percent error on SBCEX17 data (arXiv 2412.02201), and striation-based beamforming estimates `β` without range knowledge (Rouseff & Zurk 2011).

The engineer's "ionosphere is the ocean flipped upside down" is a real structural analogy: the Earth-ionosphere channel is a bounded dispersive waveguide with mode structure and interference fading. Whether an analog of `β` is observable in HF returns is a narrow, falsifiable, mechanism-level question. It is a far better first transfer experiment than "do the latents align," because success is defined by a physical quantity, and failure tells you precisely which assumption broke.

### 3.4 Negative transfer is now measured, and regime routing is the fix

Two 2026 papers should reshape the model design in both plans.

**Chu et al., "Do Physics Foundation Models Learn Generalizable Physics?" (arXiv 2605.29283).** Eight dynamics, twenty-five test regimes, sixty thousand measurements. Physics foundation models are "conditional rather than universal generalists"; a substantial fraction of architecture-PDE pairs show *negative* pretraining transfer; larger pretrained variants can be worse than small baselines; improving the data mixture only partially helps. The authors conclude that progress requires mechanisms that capture transferable structure across regimes, not more scale.

**Sharma & Sharma, "Eradicating Negative Transfer in Multi-Physics Foundation Models via Sparse MoE Routing" (arXiv 2605.15179).** Co-training incompatible regimes in a dense network causes gradient conflict and plasticity loss. A top-1 router assigning latent patches to expert subnetworks eliminated it; held-out tokens from each domain routed cleanly to their own expert, while *shared experts retained universal symmetries*.

Together these say: Plan 1's "partially shared backbone with private residual pathways" and Plan 2's "shared representation deliberately limited" are not just cautious, they are what the benchmarks demand. The concrete realization is a mixture-of-experts backbone whose router is conditioned on the dimensionless regime coordinates from §3.2, with shared experts for the anchor structure and routed experts for medium-specific physics. The atlas then has a direct readout: which experts fire for which regime.

### 3.5 What actually transfers today in these exact domains

Neither plan cites the recent applied evidence. It is instructive because it separates shallow from deep transfer.

- **Mohammadi et al. 2024 (arXiv 2409.13878), MIT Lincoln Laboratory.** ImageNet-pretrained *vision* models slightly beat audio-pretrained PANNs on passive sonar target recognition. What transferred was generic spectrogram texture, not acoustics. This is exactly the "similar-looking grams" level both plans warn about. It is real but shallow, and it says nothing about channel physics.
- **Huang et al. 2025 (arXiv 2501.03461).** Masked-autoencoder pretraining on *communications* I/Q transferred to radar signal recognition with a 16.3 percent one-shot gain, nearly matching in-domain radar pretraining at 17.5 percent. Within RF, cross-sub-domain self-supervised transfer on raw signals works.
- **CSI-CLIP++ 2026.** Contrastive CIR-CSI pretraining transferred across three tasks and across simulators. Deep transfer, anchored on the impulse response.
- **Zubow et al. 2026 (arXiv 2604.01944), "Physics-Informed Transformer for Multi-Band Channel Frequency Response Reconstruction."** This appears to be the "physics-informed transformer with axial attention" the transcript refers to. Factored time-axis and frequency-axis attention, a holomorphic complex linear layer preserving phase, and a composite loss combining spectral fidelity, power-delay-profile reconstruction, CIR sparsity, and temporal smoothness. Power-delay-profile similarity of 0.82 versus 0.62 for the best baseline at fifty percent interference occupancy.
- **RF foundation models now exist:** Radio-FM (2608.05793), EMind (2508.18785), SpectrumFM (IEEE JSAC 2026), LWM-spectro (2026), masked spectrogram modeling (2411.09849). **An underwater acoustic foundation model is being built** by NEC under contract, targeted for fiscal 2027.

The pattern: shallow transfer from generic image pretraining is easy and weak; deep transfer appears when the pretraining objective is built on paired physical views of the channel. And the "domain expert model" tier of the transcript's architecture is being built by others. The differentiated contribution is the anchor, the regime atlas, and the evidence layer.

### 3.6 What "physics-informed" should mean here

The Zubow paper is the right model for "physics-informed" in this project: not a PDE residual, but *structural priors on the channel* used as losses and architectural constraints. Sparsity of arrivals in delay. Smoothness in time. Linear modal phase versus frequency (the assumption that makes Sabra and Dowling's artificial time reversal and ray-based blind deconvolution work). Known array geometry.

This is also how physics supplies the identifiability that Plan 1 §2 says a learned model cannot manufacture. Sabra and Dowling's blind deconvolution recovers both the source waveform and the source-to-array impulse response from an unknown multipath channel, using only generic ray or mode features and elementary array knowledge. The bilinear channel model work on sources of opportunity (2020) extends it. That is the acoustic template for the Ninja overlapping-source association problem the transcript describes, which is a blind multichannel separation problem; the domain pack supplies the structural assumption that makes it well posed, and the learned component operates inside that structure.

The PINN literature that *is* relevant is the failure-mode literature: spectral bias makes PINNs unreliable for high-wavenumber Helmholtz problems, which is exactly the regime of wave propagation. Where a forward surrogate is needed, the working tools are neural operators and hybrid learned solvers, for example the FNO-enhanced parabolic-equation framework for underwater acoustic field prediction (Frontiers in Marine Science 2025) and learned Helmholtz preconditioners. Both plans already lean this way; the synthesis makes it a rule.

### 3.7 The training objective the transcript asked for

The transcript asks: "what goal and what thing are you either classifying or trying to reproduce that aligns all of these spaces naturally without carving something up?"

The synthesis answer, assembled from the evidence above:

1. **Per-domain self-supervised pretraining** on unlabeled operational recordings via masked modeling (spectrogram or I/Q). This is what Radio-FM, MSM, and the NEC effort do. No labels, uses the data you already have.
2. **Multi-view contrastive alignment within each domain** among raw signal, time-frequency view, and estimated spreading function of the *same* recording. By von Kügelgen et al. and Gresele et al., content shared across sufficiently different views of one latent is identifiable. This is the alignment basis Plan 2 demands, and it costs no labels.
3. **Cross-domain alignment only through the anchor** and only at matched dimensionless regime. Never align acoustic and RF datasets wholesale (Zhao et al.).
4. **Structural physics losses** on the anchor estimate: arrival sparsity, temporal smoothness, forward consistency through `M_d` (Zubow; Plan 1 §3D).
5. **Regime-routed shared/private backbone** (Shodh-MoE) with shared experts for anchor structure.
6. **Task heads with SBI-style posteriors** rather than point estimates, calibrated under held-out regime.

Each of these is individually validated in the literature. Their composition is the research claim.

---

## 4. The synthesized architecture

```
Existing system outputs, archives, simulators
              │
  ┌───────────▼────────────────────────────────────────────┐
  │ 0. Evidence archive        labeled arrays (xarray) +   │
  │    provenance sidecar (PROV-O), capability level       │
  └───────────┬────────────────────────────────────────────┘
              │
  ┌───────────▼────────────────────────────────────────────┐
  │ 1. Domain pack             M_d, F_d or surrogate,      │
  │    structural priors, dimensionless regime descriptor, │
  │    admissible transformations, tests, known failures   │
  └───────────┬────────────────────────────────────────────┘
              │
  ┌───────────▼────────────────────────────────────────────┐
  │ 2. Anchor estimator        delay-scale spreading       │
  │    function (delay-Doppler as limit), with declared    │
  │    identifiability assumptions; classical or learned   │
  └───────────┬────────────────────────────────────────────┘
              │
  ┌───────────▼────────────────────────────────────────────┐
  │ 3. Shared/private encoder  SSL pretrained per domain;  │
  │    multi-view contrastive to anchor; regime-routed MoE │
  │    backbone; private residual pathways                 │
  └───────────┬────────────────────────────────────────────┘
              │
  ┌───────────▼────────────────────────────────────────────┐
  │ 4. Inference               SBI / posterior heads;      │
  │    forward validation through M_d; alternatives kept   │
  └───────────┬────────────────────────────────────────────┘
              │
  ┌───────────▼────────────────────────────────────────────┐
  │ 5. Structured results      quantities, uncertainty     │
  │    with validity scope, evidence graph, lineage        │
  └───────────┬────────────────────────────────────────────┘
              │
  ┌───────────▼────────────────────────────────────────────┐
  │ 6. Atlas + experiment runner   scoped mappings,        │
  │    DomainBed-style baselines, negative transfer logged │
  └───────────┬────────────────────────────────────────────┘
              │
  ┌───────────▼────────────────────────────────────────────┐
  │ 7. LLM interface           over typed records only;    │
  │    authors domain-pack drafts from expert conversation │
  └────────────────────────────────────────────────────────┘
```

Layers 0, 1, 5, 6 are Plan 2. Layers 2, 4 and the forward-validation loop are Plan 1. Layer 3's specifics and the regime coordinates in layer 1 are the additions from §3.

One concrete role for the LLM that neither plan proposes: it is good at turning conversations like `context.md` into domain-pack drafts, meaning structured lists of assumptions, admissible transformations, and test cases. That is where operator and expert feedback belongs early: on the metadata, not the weights. LoRA fine-tuning on operator judgments (the transcript's idea) comes after the evidence layer can label which judgments were scientific adjudication versus presentation preference, as both plans note.

---

## 5. Where I would push back on both plans

**Both are heavy on governance and light on the first model.** Read literally, either plan spends the first several months on contracts, registries, and gates before any scientific result. The gates are right; the sequencing is too conservative. Build a thin vertical slice first: a minimal evidence record (an xarray dataset plus a JSON sidecar), one anchor estimator per domain, one shared/private encoder, one preregistered transfer test. Let the contract grow from what the experiment actually needed. Plan 1's evidence gate should not require the full domain-pack specification.

**Both under-weight unlabeled data.** The single most reliable result in the 2025 and 2026 applied literature is that self-supervised pretraining on unlabeled operational signals transfers within and across RF sub-domains. Both plans treat representation learning as something to introduce "only after the benchmarks can tell whether it improves anything." Pretraining is cheap, label-free, and is what the domain-expert tier will be built on anyway. Start it in parallel with the contract work.

**Both stop at "regime" without defining it.** §3.2 is the fix.

**Both treat the anchor as an open question.** The transcript already answered it. §3.1 is the fix.

**Plan 1's forward-model formulation needs a caveat for legacy systems.** For an upstream system whose processing chain is opaque, `M_d` is unknown and cannot be invented. Plan 1 says this in §3A and §3B, but the equation in §2 reads as if `M_d` is always available. The capability-level declaration should be a first-class field, and the inference engine should degrade to "retrieval and comparison" rather than "posterior inference" when it is absent.

**Plan 2's atlas needs a hub or it becomes N-squared.** Without an anchor, every pair of domains needs its own validated mapping. With the anchor, each domain needs one.

---

## 6. A pilot that tests the central hypothesis

Sequenced by Plan 1's gates, sized as a thin slice.

**Phase A: simulation, independent generators (weeks).**
Two independently written simulators: a normal-mode or ray ocean-acoustic model, and an HF ionospheric ray tracer. Each produces recordings with ground-truth spreading functions across a designed grid of dimensionless regime coordinates. Train the anchor estimator and shared/private encoder on one, evaluate few-shot anchor estimation on the other.

Preregistered hypotheses:
- H1: at matched `(v/c, B/f_c, τ_spread·B)`, a frozen shared encoder plus small target head beats a from-scratch target model at equal data budget.
- H2: at mismatched regime, the gain is zero or negative.
- H3: the regime router's expert assignment tracks the dimensionless coordinates, not the domain label.

Baselines per DomainBed: independent per-domain models, pooled model with domain token, shared/private without routing, physically normalized features with a linear head. Match parameters, data, and compute.

**Phase B: reality gate with open ground-truth data.**
Ocean acoustics has public experiments with known sources and measured environments; indoor and outdoor RF has public measured-channel datasets. Repeat Phase A's tests. Add held-out sessions, held-out instruments, and calibration under shift. Test the waveguide-invariant mechanism question from §3.3 as the first named-quantity transfer.

**Phase C: integration.**
Only now attach an existing system's outputs through an output-only domain pack, and only now build the operator-facing explanation layer.

Every failure in A or B is written to the atlas as a scoped negative result. That is Plan 2's best idea and it should survive.

---

## 7. The pitch, synthesized

> We are building a reusable inference layer that connects existing sensing systems through a common physical anchor: the channel's spreading function, which every wave-propagation domain already estimates in its own way. Each domain keeps its own models and processing. The platform records what each system observed, under which assumptions, and with what uncertainty, and it tests where learned structure actually transfers across domains at matched physical regime. The immediate deliverable is consistent integration and traceable, uncertainty-aware analysis. The research upside is that each new domain or environment needs less bespoke data and modeling, because the parts of the physics that are shared are learned once.

---

## 8. Reading list, grouped by what it settles

**The anchor and its regimes**
- Bello (1963); Matz & Hlawatsch, "Fundamentals of Time-Varying Communication Channels" (2011); Matz, Bölcskei, Hlawatsch, IEEE SPM (2013). Scattering function, WSSUS, local scattering function.
- Altes, "Some invariance properties of the wide-band ambiguity function" (1971); Fourier-Mellin transform literature. Wideband Doppler as time scaling.
- CSI-CLIP++, arXiv 2606.25714 (2026). CIR and CSI as paired views; the anchor works as an ML pretraining target.
- ImageBind, Girdhar et al., CVPR 2023, arXiv 2305.05665. One anchor modality suffices.

**Regime coordinates**
- Bakarji et al., "Dimensionally Consistent Learning with Buckingham Pi," arXiv 2202.04643.
- Yuan & Lozano-Durán, "Dimensionless learning based on information," Nature Communications 2025, arXiv 2504.03927.

**Negative transfer and routing**
- Chu et al., "Do Physics Foundation Models Learn Generalizable Physics?" arXiv 2605.29283 (2026).
- Sharma & Sharma, "Eradicating Negative Transfer ... Sparse MoE Routing," arXiv 2605.15179 (2026).
- Gulrajani & Lopez-Paz, "In Search of Lost Domain Generalization," arXiv 2007.01434.
- Zhao et al., "On Learning Invariant Representations for Domain Adaptation," ICML 2019.

**Identifiability and alignment basis**
- Locatello et al., ICML 2019 (unsupervised disentanglement is not identifiable without inductive bias).
- Gresele et al., "The Incomplete Rosetta Stone Problem," UAI 2020, arXiv 1905.06642.
- von Kügelgen et al., "Self-Supervised Learning with Data Augmentations Provably Isolates Content from Style," NeurIPS 2021, arXiv 2106.04619.
- Li, Lee, Bresler, "Identifiability and Stability in Blind Deconvolution under Minimal Assumptions," arXiv 1507.01308.
- Bousmalis et al., "Domain Separation Networks," arXiv 1608.06019.

**Physics-structured priors and blind channel estimation**
- Sabra & Dowling, "Blind deconvolution in ocean waveguides using artificial time reversal," JASA 2004; Sabra et al., "Ray-based blind deconvolution in ocean sound channels," JASA 2010; Byun et al., bilinear channel models for sources of opportunity, JASA 2020.
- Zubow et al., "Physics-Informed Transformer for Multi-Band Channel Frequency Response Reconstruction," arXiv 2604.01944 (2026).
- Waveguide invariant: Rouseff & Zurk, JASA 2011; Cockrell & Schmidt, JASA 2010; arXiv 2412.02201 (2024).
- Cepstral multipath work: arXiv 2512.11165 (adaptive cepstral filtering); Toeplitz-based blind deconvolution with wideband dictionaries.

**Applied transfer evidence in sonar and RF**
- Mohammadi et al., "Cross-Domain Knowledge Transfer for Underwater Acoustic Classification Using Pre-trained Models," arXiv 2409.13878.
- Huang et al., "Few-Shot Radar Signal Recognition through SSL and RF Domain Adaptation," arXiv 2501.03461.
- Radio-FM, arXiv 2608.05793; EMind, arXiv 2508.18785; SpectrumFM, IEEE JSAC 2026; masked spectrogram modeling, arXiv 2411.09849.
- NEC self-supervised underwater acoustic foundation model, contract announced 2026, target fiscal 2027.

**Forward surrogates and operator learning**
- Kovachki et al., "Neural Operator," JMLR 2023; Li et al., FNO, arXiv 2010.08895.
- Alkin et al., "Universal Physics Transformers," NeurIPS 2024, arXiv 2402.12365.
- Herde et al., "Poseidon," NeurIPS 2024, arXiv 2405.19101.
- McCabe et al., "Walrus," ICML 2026, arXiv 2511.15684 (acoustics among 19 pretraining scenarios).
- Wiesner et al., "Towards a Physics Foundation Model," arXiv 2509.13805 v4 (2026).
- Sun et al., PROSE-PDE, arXiv 2404.12355; Hmida et al., CompNO, arXiv 2601.07384 (2026).
- Yang et al., ICON, arXiv 2304.07993, PNAS.
- Kalia et al., normal-form autoencoders, arXiv 2106.05102.
- FNO-enhanced parabolic equation for underwater acoustics, Frontiers in Marine Science 2025.
- Krishnapriyan et al., PINN failure modes, NeurIPS 2021, arXiv 2109.01050.

**Inference and uncertainty**
- Deistler et al., "Simulation-Based Inference: A Practical Guide," arXiv 2508.12939; Dax, Heimel, Louppe, arXiv 2607.21702 (2026); the `sbi` library.
- Ovadia et al., "Can You Trust Your Model's Uncertainty?" arXiv 1906.02530.
- Tishby, Pereira, Bialek, "The information bottleneck method," arXiv physics/0004057.

**Infrastructure**
- xarray; MLflow model registry; W3C PROV-O.
