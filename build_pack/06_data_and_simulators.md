# 06. Data and simulators

Nothing here is invented as available. Every candidate is marked with what must be verified before it is used. **[P]** throughout, with the independence and manifest requirements **[G]**.

## 1. Simulators

### W1: sonar, in-house image-source waveguide

**Proposal.** A Pekeris waveguide (isovelocity water column over a fluid half-space) solved by the method of images: the received pressure at a hydrophone is a sum of delayed, attenuated copies of the source waveform, one per image path, with surface reflection coefficient −1 and a bottom coefficient from the half-space impedance contrast at the grazing angle. Truth is the arrival list itself: delays, amplitudes, angles. The power-delay profile, RMS delay spread and resolvable-arrival count are exact functionals of that list.

**Why this first.** Truth is exact by construction, which is what W1 needs to characterize the classical estimators' error. It is a few hundred lines. It has no external dependency and no license question. Its limitation is that it has no refraction, so it cannot produce ducted or refracted paths.

**What the sonar lead must accept.** That an isovelocity image model is an adequate first generator for delay-spread and arrival-count descriptors, with a refraction-capable model (a normal-mode or ray code the lead already runs) as the second generator for W2's independence requirement and for the reality gate. This is question 2 in the spec's section 12.

**Parameters swept.** Water depth, source and receiver depths, range, bottom sound speed and density, source bandwidth and center frequency, SNR. The regime grid is designed so `Π_τ` and `Π_f` span the placeholder sonar ranges.

### W2: HF, in-house multimode skywave

**Proposal.** A discrete-mode model: for a given ground range and a Chapman-layer ionosphere, the propagating modes (1F, 2F, 1E, and their ordinary and extraordinary splits) are enumerated by hop geometry with group delay from the layer's virtual height and a per-mode gain from a simple absorption law. A slow multiplicative fading process models ionospheric motion. Truth is the mode list.

**Independence from the sonar generator.** Different physics (refraction in a plasma layer with ground hops versus boundary images in a fluid layer), different code, different scene distribution. Shared: the approximation family "discrete paths with per-path delay and gain," which is the anchor assumption. The independence statement must say so.

**What must be verified.** Whether a published ionospheric ray tracer (candidates: the 2025 open-source ionospheric propagation code, the discretized-ionosphere ray-tracing method) is available under a usable license and in a callable form, as the second HF generator for the reality gate. Not needed for W2's first trial.

### Independence statement

Required for every cross-domain claim from simulation. Template in `templates/independence_statement.md`. It names the two generators, their physics kernels, their scene distributions, their approximation families, how truth is constructed in each, and every shared element.

## 2. Public data candidates for the reality gate

| Domain | Candidate | Why | Must verify |
|---|---|---|---|
| Ocean acoustics | SWellEx-96 | Widely used; known towed-source tonals; measured sound-speed profile and bathymetry; vertical and horizontal arrays | Current hosting and terms; which arrays and events are public; whether source track is public at the needed resolution |
| Ocean acoustics | SBCEX17 ship-noise recordings | Used by the 2024 waveguide-invariant ranging paper; AIS-derived source tracks | Whether the recordings themselves are public or only derived products |
| RF channel | DeepMIMO | Public ray-traced CSI across scenarios and carriers; used by CSI-CLIP++ | It is simulated, not measured; it serves the E2 independent-generator check, not the reality gate |
| RF channel | Measured indoor or vehicular CIR datasets | Needed for a measured-data reality check | Identify a specific public set with time-varying CIR and enough sessions for grouped splits |

ADR-24 keeps the reality gate open until a named dataset's fields, truth and session structure are confirmed to support the split policy.

## 3. Program data

Enters only at W3 through the output-only adapter, at C0 or C1, unless C3 archives are already cleared for research use. Every record carries the owner's `data_use` label. Nothing in this pack assumes a new collection campaign.

## 4. Data manifest

Every dataset, simulated or measured, is described by one manifest record (`templates/data_manifest.md`) before any run consumes it: source, license or clearance, capability label and explicit capabilities, group id scheme, truth kind and error model, regime coverage as a list of cells, known gaps. The manifest is itself a `Record` of kind `summary` so it has an id, a hash, and lineage.

## 5. Regime coverage report

Before H1 runs, `bench` produces, from the manifests, the list of regime cells each dataset covers per descriptor's governing groups, and the intersection. That report is the "real support" the protocol requires and it replaces any assumption of overlap.
