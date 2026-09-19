# Sources for build pack v0.3

## Project documents read in full

- `archive/context.md` — transcript of the sonar and ML leads' conversation
- `archive/plan1.md`, `archive/plan2.md` — the two original plans
- `archive/synthesis.md` — the referee document
- The Crossfade Technical Spec, v0.2 as of 2026-09-18 (shared doc)
- `archive/review/01_architecture_review.md`, `archive/review/02_contract_amendments.md` — the v0.2 review
- `archive/review/03_referee_response.md` — claim-by-claim response, adopted
- `archive/review/04_build_pack_assessment.md` — what to keep, merge and cut from v0.2
- `archive/crossfade_build_pack_v0_2/` — all files

## External checks performed for the spec and reviews (dates on each in the spec's section 13)

Verified against the source: Matz, Bölcskei, Hlawatsch 2013 (delay-Doppler generality, scaling parsimony, spreading versus scattering); Jiang et al. 2026 CSI-CLIP++ (authors, perfect ray-traced CSI, IFFT CIR, no SNR noise); Chu et al. 2026 (physics foundation models as conditional generalists); Sharma and Sharma 2026 (two-regime MoE routing); von Kügelgen et al. 2021 and Gresele et al. 2020 (multi-view identifiability conditions); Li, Lee, Bresler 2015 (blind deconvolution identifiability); Yuan and Lozano-Durán 2025 (IT-π); Sabra and Dowling 2004, 2010 (artificial time reversal, ray-based blind deconvolution); Zubow et al. 2026 (physics-informed transformer for CFR reconstruction); the waveguide-invariant ranging literature; Deistler et al. 2025 and Dax, Heimel, Louppe 2026 (SBI); Ovadia et al. 2019; Gulrajani and Lopez-Paz 2020.

## Not checked, and marked as such in `06_data_and_simulators.md`

Current hosting and terms of SWellEx-96; public availability of SBCEX17 raw recordings; license and callable form of any published ionospheric ray tracer; existence of a suitable public measured time-varying RF CIR dataset with session structure. Each is an open item with the slice it blocks.
