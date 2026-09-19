# Sources and review scope

## Uploaded material

**TS — Crossfade Technical Spec:** uploaded as `Untitled.md`, dated September 17, 2026. Locations below use the line-numbered rendition supplied with the conversation.

- Lines 9–24: product contracts and non-goals.
- Lines 26–59: mandatory anchor and representation claims.
- Lines 63–85: regime coordinates and proposed interpretation.
- Lines 87–119: layers and runtime.
- Lines 121–155: object and evidence capability contracts.
- Lines 157–219: domain packs, estimators, and task scope.
- Lines 221–264: model architecture and training.
- Lines 266–287: uncertainty, forward checking, and fusion.
- Lines 289–336: evaluation and atlas.
- Lines 338–400: phases, data assumptions, staffing, and unresolved domain questions.
- Lines 402–473: bibliography and source-document references.

**SYN — Refereeing Plan 1 and Plan 2: Overlap, Disagreement, and a Synthesis:** uploaded as `synthesis.md`, dated September 17, 2026.

- Lines 7–22: synthesis position and three proposed contributions.
- Lines 49–103: disagreements and pilot scope alternative.
- Lines 109–191: anchor, regime, model, and training claims.
- Lines 195–262: architecture and sequencing recommendations.
- Lines 266–286: proposed experiment phases.

**CTX — Conversation transcript:** uploaded as `Pasted text(20260917-205110).txt`. Used as context for the wave-propagation focus and shared-spine objective, not as empirical validation.

The source files were left unchanged. `source_manifest.json` records their byte lengths and SHA-256 digests. The original plans referenced by the synthesis were not separately re-audited as independent source documents in this package.

## External checks performed September 17, 2026

This was a targeted check of load-bearing claims, not a reproduction of experiments or a complete bibliography audit. Existence of a paper, a reported empirical result, and support for a Crossfade-wide requirement are different evidence levels.

| Ref | Primary source | Inspected scope and relevance |
|---|---|---|
| R1 | Matz, Bölcskei, Hlawatsch, *Time-Frequency Foundations of Communications*, arXiv:1307.4790 (2013), §§II-B and II-C. | Full-text sections distinguish general operator representations, scaling compactness, and channel statistics. |
| R2 | **Jun Jiang et al.**, *CSI-CLIP++: A Scalable Channel Foundation Model for Wireless Communication via CIR-CSI Consistency*, arXiv:2606.25714v1, submitted June 24, 2026, especially §V-B. | Abstract and implementation details checked. Inputs are ideal simulated CSI with IFFT-derived CIR; this narrows applicability to the present proposal. The uploaded spec's “Wang et al.” attribution should be corrected. |
| R3 | Ellwil Sharma and Arastu Sharma, *Eradicating Negative Transfer in Multi-Physics Foundation Models via Sparse Mixture-of-Experts Routing*, arXiv:2605.15179v1 (2026), §§3–5. | Full-text setup, results, and discussion checked. A two-fluid-regime routing demonstration, not proof that Crossfade requires a routed backbone. |
| R4 | Chu et al., *Do Physics Foundation Models Learn Generalizable Physics? A Bias-Aware Benchmark Across Physical Regimes and Distribution Shifts*, arXiv:2605.29283v2, revised July 1, 2026. | Abstract checked; supports evaluating condition-dependent transfer rather than assuming universal utility. |
| R5 | Yuan Yuan and Adrián Lozano-Durán, *Dimensionless learning based on information*, arXiv:2504.03927v3, revised September 29, 2025. | Abstract and full-text page accessed; supports task/data-conditioned dimensionless-variable selection, not a proof of the proposed sonar/HF equivalence. |
| R6 | Li, Lee, Bresler, *Identifiability and Stability in Blind Deconvolution under Minimal Assumptions*, arXiv:1507.01308v2 (2015). | Abstract checked; identifiability depends on structural assumptions, not just possession of raw measurements. |
| R7 | von Kügelgen et al., *Self-Supervised Learning with Data Augmentations Provably Isolates Content from Style*, arXiv:2106.04619v4 (2022; NeurIPS 2021). | Abstract checked; sufficient conditions and identification up to an invertible mapping do not establish named physical coordinates automatically. |
| R8 | Deistler et al., *Simulation-Based Inference: A Practical Guide*, arXiv:2508.12939v1 (2025). | Abstract and workflow sections accessed; supports simulator/prior/diagnostic-aware inference rather than an unconditional posterior requirement. |
| R9 | Xarray documentation, *Data Structures*, stable documentation accessed September 17, 2026. | Coordinate/attribute behavior checked; semantic attribute validation remains an application responsibility. |
| R10 | W3C, *PROV-O: The PROV Ontology*, Recommendation. | Provenance vocabulary accessed; used for derivation semantics, not probabilistic independence. |
| R11 | Girdhar et al., *ImageBind: One Embedding Space To Bind Them All*, arXiv:2305.05665v2 (2023). | Abstract checked; hub-based pairing is an architectural precedent, not proof of universal transfer or elimination of scoped validation. |
| R12 | Zubow et al., *Physics-Informed Transformer for Multi-Band Channel Frequency Response Reconstruction*, arXiv:2604.01944v1 (2026). | Abstract checked; reported performance is tied to the stated reconstruction setup and classical comparison baselines. No Crossfade-wide numerical target is adopted from it. |

## Evidence classification used in this package

**Source-derived:** what TS, SYN, or CTX says, attributed to that source.

**Externally checked:** a specific statement supported by one of R1–R12, with its inspected scope.

**Review reasoning:** an internal inconsistency, a missing prerequisite, or a consequence of the proposed data flow.

**Proposed requirement:** an engineering/design choice for v0.2, not claimed as an empirical finding.

**Unresolved:** task-specific data, mathematics, thresholds, or resource choices not established by the uploaded material or this targeted review.
