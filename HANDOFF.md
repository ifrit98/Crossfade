# Crossfade: cold-pickup handoff

*Written 2026-09-18 at the end of the first working session. Read this first in a new session. Everything below is verifiable in the repo, the shared docs, or the archive.*

---

## 1. What Crossfade is, in one paragraph

A capability-aware evidence and experiment platform for wave-propagation inference. It connects sonar, HF skywave radar and RF systems through a common channel vocabulary anchored on the channel spreading function, and it measures where learned structure transfers between domains instead of assuming it. The origin is a recorded conversation between the ML lead (Jason, the user) and the sonar/signals lead, in which the signals lead argued that the propagation channel's time-varying impulse response or scattering function is the common thread across all wave-sensing domains. Everything since has been about making that idea precise, finding what the physics actually supports, and building the smallest software that can test it honestly.

## 2. Where everything is

**GitHub:** `git@github.com:ifrit98/Crossfade.git`, user `ifrit98`, SSH auth works from this machine.

| Branch | Commits | Contents |
| --- | --- | --- |
| `main` | 3 (plus this handoff) | `README.md`, `docs/` (both documents), `docs/tex/` (LaTeX: the three-page math brief, the math sanity-check edition and the full thesis, sharing `math-core.tex` and `crossfade.bib`; `make -C docs/tex` with tectonic), `build_pack/` (v0.3), `archive/` (everything superseded), `HANDOFF.md` |
| `w0-workbench` | 1 ahead of main | The W0 code: `crossfade/`, `packs/`, `tasks/`, `tests/`, `fixtures/`, `pyproject.toml`, `crossfade.toml`. Not merged; waiting on the signals lead's review |

**Local:** `/Users/nuggylover1210/Projects/Crossfade`. A `.venv` (Python 3.14.7, pydantic 2.13, xarray 2026.7, zarr 3.4, numpy 2.5, pint, pyyaml, pytest, ruff) is present and gitignored. `.venv/bin/pytest` from the branch runs 39 tests green in about 3 seconds. `.venv/bin/ruff check crossfade packs tests` is clean.

**Shared docs (Claude Docs, private until shared from the page's Share menu):**

| Doc | URL | Connector ids | State |
| --- | --- | --- | --- |
| Crossfade Technical Spec | https://claude.ai/code/artifact/d86a57cf-f3a1-4751-b38c-c50529d799bb | project `d86a57cf-f3a1-4751-b38c-c50529d799bb`, prose node `3a47282b-e57d` | v0.3, rev 30, 13 sections. `docs/Crossfade-Technical-Spec.md` is an exact export |
| Crossfade in Two Pages | https://claude.ai/code/artifact/8b7c6549-4fac-4564-960d-c7040e49092c | project `8b7c6549-4fac-4564-960d-c7040e49092c`, prose node `3abb29d5-3be2` | rev 8, 6 sections. `docs/Crossfade-in-Two-Pages.md` is an exact export |

If either doc is edited by a person, the markdown export in `docs/` is stale until re-exported. Nobody had edited either as of the last check.

## 3. How we got here, in order

1. **Transcript** (`archive/context.md`): the sonar lead and ML lead conversation. Key ideas: channel impulse response as common thread; "ionosphere is the ocean flipped upside down"; striation patterns as physics features; cepstral and blind channel estimation; the Ninja overlapped-source association problem; a "shared spine" connecting domain-specific representations; LLM as translator with operator feedback via LoRA.
2. **Two independent plans** (`archive/plan1.md`, `archive/plan2.md`): plan 1 from first principles, plan 2 from a physics-modeling lens. They agreed on about eighty percent.
3. **Synthesis** (`archive/synthesis.md`): refereed the plans, verified all 30 citations, added three things neither plan had: name the anchor (spreading function), make regime a dimensionless coordinate, take self-supervised pretraining on paired views seriously. Also found 2026 literature on negative transfer in physics foundation models.
4. **Spec v0.1**: first shared doc, written for the sonar lead.
5. **External review** (`archive/review/01`, `02`, and `archive/crossfade_build_pack_v0_2/`): a separate session reviewed v0.1 and proposed thirteen record types, twelve slices, and contract amendments. Its factual checks were all correct.
6. **Referee response** (`archive/review/03_referee_response.md`): examined every claim from first principles. Accepted most. Pushed back on three: the anchor needs a canonical kind per regime; keep "no shared code" alongside documented independence; the T0 toy fixture cannot shape the contracts alone. Found that the review's overlap contradiction is a scientific result, not just a pilot bug (see section 4).
7. **Spec v0.2**: rewritten to match.
8. **Build pack assessment** (`archive/review/04_build_pack_assessment.md`): dissected the v0.2 pack for complexity. Cut thirteen record types to five, twelve slices to four now and three later, the `conditional` assessment state, the storage framework, the plugin system.
9. **Build pack v0.3** (`build_pack/`): the implementation record. Meta-architecture, five contracts, repo layout, evaluation protocol, slices W0 to W3, decision register, data and simulators, four PRDs, templates.
10. **Spec v0.3**: aligned with the pack (version history paragraph, W1 simulator decision, invariant ids).
11. **Two Pages explainer**: written to the sonar lead in second person, physics first.
12. **Repo created and pushed.** Archive organized.
13. **W0 workbench spine** written test-first on branch `w0-workbench`.

## 4. The decisions that matter, and why

Each has a tag: **[G]** guarantee the software enforces, **[P]** provisional and replaceable, **[H]** hypothesis to measure.

- **The anchor is a vocabulary, not a reconstruction [P].** Every quantity is a functional of a named channel representation (`canonical_kind` on every `TaskSpec` quantity, or `not_channel`). That one string is the whole cross-domain comparability mechanism. Packs need not reconstruct anything.
- **Delay-Doppler always exists; delay-scale is parsimonious for wideband [corrected fact].** v0.1 wrongly said one was "the" narrowband form and the other "the" wideband form. Matz, Bölcskei and Hlawatsch (2013) say any linear channel is a superposition of time-frequency shifts. What changes with `TB · (v/c)` is sparsity. Each pack declares a canonical kind per regime box with a tested threshold.
- **Regime coordinates are dimensionless groups, matched per descriptor [H].** The placeholder sonar and HF ranges are disjoint in `v/c` and `B/f_c` and overlap in `Π_τ`, `Π_ν`, `Π_f`, `Π_L`. So the hypothesis itself predicts Doppler structure does not transfer between sonar and HF and waveguide/arrival structure might. That is the "flipped ocean" made precise, and it is the most useful result of the session. The transfer surface is measured, not gated; a gain where none is predicted is a finding.
- **A learned model does not remove an identifiability limit; it hides it [G in spirit].** Every estimator declares assumptions, identifiable and ambiguous quantities. Capability labels (C0 to C3) never authorize; per-op preconditions do.
- **Paired deterministic views do not isolate physics [corrected claim].** A spectrogram is a function of the waveform; contrasting them gives consistency only. Content isolation needs views with independent nuisance variation: sub-arrays, time windows, different upstream chains, controlled simulation pairs. Losses L2a (consistency) and L2b (isolation) are split.
- **Baseline ladder before any network [G].** Classical → normalized features plus head → scratch → target SSL → pooled → dense shared/private → routed (optional ablation). Routing was demoted because its motivating paper covers two fluid regimes.
- **Five record types [P]:** `Record`, `TaskSpec`, `Operation`, `Run`, `Report`. No `conditional` state; an assumption is a parameter.
- **Five typed result states [G]:** execution, answer, applicability, forward check, uncertainty kind. Nothing defaults to a pass.
- **Three gates [G]:** delivery, scientific, promotion. H2 is a measurement, never a gate.
- **Simulator independence needs both [G]:** no shared physics kernel and a written independence statement. The two proposed in-house generators share exactly one approximation, "discrete paths with per-path delay and gain," which is the anchor assumption itself, and the statement must say so.
- **One Python package, five modules, files plus SQLite, no services, no plugin discovery, no workflow engine, no base classes, no state machines [P with G-level enforcement via size budgets].** The test: if it can be a Pydantic model, a function, or a pytest, it is not a service, a base class, a plugin system, or a state machine. Core budget 1500 lines at end of W0; review at 2500.
- **The LLM never touches a number [G].** It reads typed records, explains, retrieves, and drafts pack metadata for human approval. Operator feedback splits into presentation, metadata, adjudication; only adjudication is a training label, after versioning.

## 5. The W0 code as it stands

On branch `w0-workbench`. Written test-first against `build_pack/prds/PRD-W0-workbench.md`.

| File | Lines | Holds |
| --- | --- | --- |
| `crossfade/records.py` | ~250 | `Record` plus sub-models; `Store` with write-once blobs (zarr for arrays, canonical JSON for structured), identity over byte and manifest hashes, pint validation with quarantine, `verify()` reporting mismatches, orphan blobs, orphan outputs |
| `crossfade/tasks.py` | ~120 | `TaskSpec`; unknown fields rejected; `deploy_fields()` and `oracle_fields()` |
| `crossfade/packs.py` | ~110 | `Operation` protocol; `Assessment`; `RunContext`; `assess()` that validates params, checks quarantine and explicit capabilities, never opens the payload; `registry()` that fails whole |
| `crossfade/runs.py` | ~190 | `Run`, `Result`, `Quantity`, `ForwardCheck`, `Uncertainty`; `execute()` publishing outputs before the run; `replay()` comparing outputs under determinism |
| `crossfade/db.py` | ~30 | Three SQLite tables |
| `crossfade/cli.py` | ~100 | ingest, inspect, assess, run, replay, verify, export |
| `packs/profile_fixture/` | ~110 | T0 weighted RMS width; writes a `descriptors_only` anchor record |
| `packs/summary_fixture/` | ~45 | Output-only import with `upstream_asserted` origin |
| `tasks/*.yaml` | 2 files | T0 and summary.compare |
| `fixtures/t0_golden.json` | | Reference answers, independent of implementation |
| `tests/` | 559 | 39 tests named `test_w0_atNN_<slug>` mapping to PRD acceptance ids |

**Contract details settled in code and recorded in `build_pack/01_contracts.md` and PRD-W0:**
- AT-04/AT-05 value checks happen in `run` (answer `unsupported`, reasons in `diagnostics`), not `assess`, because `assess` never opens the payload. Negative `reference_time` is a param check and stays in `assess`.
- `Record.id = "rec_" + sha256(byte_hash + manifest_hash)[:16]`; the contract's original manifest-only derivation would collide.
- `produced_by_run` added, excluded from identity so a replay reuses the record it reproduces. `validation_notes` added.

**Known gaps, deliberate:** the worker runs in-process (subprocess isolation with a resource limit is the next increment; no contract changes). No `bench.py` yet beyond nothing; that is W1. No simulator, no estimator, no model. Nothing merged.

## 6. Critical path and open questions

**Blocking W1 (the first real task), two answers from the sonar lead:**
1. Is RMS delay spread plus resolvable-arrival count from beam time series the right first descriptor? If not, which functional of the PDP or scattering function?
2. Is an isovelocity image-source Pekeris waveguide an acceptable first generator (exact arrival-list truth, no refraction), with a refraction-capable code he already runs as the second generator?

**Shaping W2, over the next month:** program regime ranges to replace the placeholders; what breaks the cepstral method in the overlapped-source case and whether a source subspace makes it identifiable; whether a waveguide-invariant-like descriptor should exist in HF multimode returns; which C3 archives could be cleared for pretraining; which public datasets carry the environmental truth needed for the reality gate.

**Open ADRs** (`build_pack/05_decision_register.md`): ADR-10 first task, ADR-11 W1 simulator, ADR-24 reality-gate data, ADR-25 W3 target system, ADR-26 shared deployment (nonblocking).

The full list is section 12 of the spec and section 6 of the explainer.

## 7. Next steps, in order

1. Share "Crossfade in Two Pages" with the sonar lead (Share menu on the doc, or the GitHub link). His two answers unblock W1.
2. Meanwhile on `w0-workbench`: subprocess worker with resource limit; then merge to main once the sonar lead has not objected to the architecture.
3. W3 output-only adapter can start any time ADR-25 names the system and export format. It shares only `Record` and `Run`.
4. W1 the day the quantity is confirmed: `packs/sonar_sim/sim.py` (image-source Pekeris, arrival list as oracle record), `autocorr_pdp` and `cepstral_pdp` estimators with block bootstrap, `beamform_stft` with its transform test, then `bench.py` (splits, leakage checker, firewall, aggregate, report, claims). PRD-W1 has the 486-cell regime grid and ten acceptance tests.
5. Unlabeled pretraining may start as soon as W1's split policy is frozen and test membership hashed (CF-16).
6. The pitch to Tim (management/funding stakeholder) is one paragraph in `archive/synthesis.md` section 7 and durations are the labeled estimates in spec section 11.

## 8. Conventions to keep

- Every requirement carries [G], [P] or [H]. When something fails, the tag says what to do.
- Test names `test_<slice>_atNN_<slug>` map to PRD acceptance ids.
- `ruff check && ruff format --check && pytest -q` is the whole gate.
- Commits end with the Claude co-author trailer and session link (see git log for the format).
- Docs are living: edit the Claude Doc, then re-export to `docs/`. Never edit `docs/*.md` alone or the two diverge.
- The LaTeX documents in `docs/tex/` are written from the spec and build pack, not exported from a doc. When the spec changes, `math-core.tex` and `crossfade-full.tex` need the same change by hand. Every bib entry was checked against Crossref or arXiv on 2026-09-21; three citation errors in the spec were found that way (Tian et al. 2020 for the bilinear paper, Sabra, Song and Dowling 2010, Altes 1973).
- Never invent a dataset, a threshold, or a result. Mark it open with the slice it blocks.
- Bylines in the repo are date and first name only; no email.
- Archive, never delete. `archive/` exists so decisions can be traced.

## 9. Gotchas

- Claude Docs editing: replace whole sections by heading block id plus deletes of the section's other blocks; `dropped_with` notices on deletes are benign (the block was already removed with the replaced one). Always read with `sinceRev` before editing in a new turn. Block ids are in the ack of each write.
- zarr 3 writes are deterministic for identical data; the byte hash is over sorted relative paths plus file bytes. `consolidated=False` everywhere.
- `pint` unit strings: `"1"` is dimensionless; `"ms"`, `"s"`, `"km"` parse. A missing or unparseable unit quarantines the record.
- `packs.registry()` imports by module path; `crossfade.toml` lists `packs.profile_fixture` and `packs.summary_fixture`. Tests that need a bad pack write one into `tmp_path` and prepend it to `sys.path`.
- The transcript in `archive/context.md` names colleagues (Tim, Matt, Audrey) and programs (Ninja, TRACE, Front Row). The user chose to push it. Do not add more personal detail to the repo.
- The two Claude Docs are private until the user shares them. The GitHub repo visibility is whatever the user set; assume it may be public.

## 10. People and roles, as far as this session knows

- **Jason** (the user, `ifrit98` on GitHub): ML lead, drives the project, wants first-principles examination of every claim, dislikes complexity creep, prefers shareable docs and a repo he can hand to others.
- **The sonar lead / signals expert**: cross-domain signals expert (HF radar and sonar programs, ray tracing, cepstral work). Has not yet seen any of this. His two answers are the critical path.
- **Tim**: management and funding stakeholder; interested in C-UAS and command-and-control; the pitch paragraph is for him.
- **The external reviewer**: a separate session that produced the v0.2 review and pack; its work is in `archive/`.
