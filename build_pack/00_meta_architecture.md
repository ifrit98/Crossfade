# 00. Meta-architecture

## The decision

Crossfade v0.3 is one Python package, `crossfade`, with five modules, a directory of domain packs that are ordinary Python packages, a store that is a directory of content-hashed files plus a SQLite index, and a small CLI. **[P]** for the module boundaries; **[G]** for the constraints that follow.

| Constraint | Meaning | Why |
|---|---|---|
| No services | Everything runs in one process or one subprocess per numerical worker | Single-user local use is the whole of W0 to W3; ADR-015 defers shared deployment until concurrency exists |
| No plugin discovery | Packs are listed by import path in `crossfade.toml` | Discovery mechanisms are the first thing that silently loads untrusted code; an explicit list is also the trust boundary |
| No workflow engine | A run is one operation on one record; the "operation graph" is the list of runs a task produced | A DAG scheduler for a fixture that computes an RMS width is the canonical example of premature framework |
| No base-class hierarchies | `Operation` is a `Protocol`; packs implement it with plain classes; there is no `BaseOperation` | Inheritance trees are where behavior hides; a protocol is a checkable shape |
| No state machines beyond run status | `Run.status` and the five result-state enums are the only states; there is no assessment state machine, no approval flow | The review's `conditional` assessment state was a small state machine with an authorization step; an assumption is a parameter |
| Storage is files plus SQLite | Payloads at `store/blobs/<sha256>`; records, runs and reports as JSON files and rows in three tables | Immutable by construction: there is no update API |
| Five record types | `Record`, `TaskSpec`, `Operation`, `Run`, `Report` | The v0.2 review's thirteen carry the same information; the extra eight are ways to store half of something |
| Physics lives in packs | The core never branches on a domain name, a representation kind, or a regime coordinate | The core is a ledger and a bench; packs are the science |

## What was rejected, and where it came from

| Rejected | Origin | Reason |
|---|---|---|
| Regime-routed mixture-of-experts as the architecture | Spec v0.1 §8 | The motivating result covers two fluid regimes; routing is arm 7 of the baseline ladder and an ablation, not the model |
| Mandatory full-grid anchor payload from every pack | Spec v0.1 §2 | Contradicted the output-only pack; anchor is now a typed family with optional payload and a canonical kind per regime |
| Universal PINN or PDE-residual losses | Transcript, plan 2 framing | Spectral bias at high wavenumber; physics enters as structural priors and forward models |
| LLM inside the numerical path | Transcript | It reads records and writes drafts, never quantities or verdicts |
| Thirteen record types with a `conditional` assessment state | Review v0.2 | Collapsed to five; assumptions are parameters |
| Twelve slices with uncertainty as its own slice | Review v0.2 | Uncertainty is a property of every estimator; slices are user-visible deliverables |
| "No shared code" replaced by documented independence | Review v0.2 | Kept both; code independence is the auditable proxy, assumption independence is the target |
| Calendar commitments removed entirely | Review v0.2 | Dependency gates for engineering; planning estimates kept, labeled, for the funding conversation |
| xarray attributes as the unit system | Spec v0.1 §5 | Attributes are labels; pint validates at ingest |
| Resampling, windowing, retune as "conventions" | Spec v0.1 §6 | They are lossy processing or physical intervention; four-class transform taxonomy with per-transform tests |
| Paired deterministic views as an identifiability basis | Spec v0.1 §8 | A spectrogram is a function of the waveform; only views with independent nuisance variation isolate content |
| Every experiment writes a `Mapping` | Spec v0.1 §10 | A mapping is an implemented correspondence; a claim is a section of a report |
| H2 as a gate | Spec v0.1 §10 | A preregistered null that fails the pilot on an unexpected discovery is backwards |
| Microservices, graph database, GNN evidence graph, model registry service | Plan 2, spec v0.1 | None needed before concurrency; PROV-compatible lineage is a `parents` list |

## Size budgets

Budgets are the enforcement mechanism for the constraints above. They are counted with `cloc` on Python source including tests, excluding fixtures data.

| Scope | Budget | Review trigger |
|---|---|---|
| `crossfade/` core (five modules, db, cli) at end of W0 | 1500 lines | 2500 lines: stop and find the framework |
| `packs/profile_fixture` + `packs/summary_fixture` | 300 lines | 600 |
| `packs/sonar_sim` including the in-house simulator | 1200 lines | 2000 |
| `packs/hf_sim` | 1000 lines | 1800 |
| `crossfade/bench.py` at end of W1 | 500 lines | 900 |
| Models for W2 (encoders, heads, training loop) | 2000 lines | 3500 |
| Any single function | 60 lines | 100 |

A budget overrun is not a failure; it is a mandatory review that asks what became a framework and whether it needed to.

## The three tags

Every requirement in this pack is tagged.

- **[G] Guarantee.** The software enforces it. A violation is a bug and a test exists or must be written for it. Examples: immutability, typed states, leakage checks, no fabricated defaults.
- **[P] Provisional.** A choice made now, replaceable without changing a contract. Examples: zarr for arrays, the canonical anchor kind per regime, the dense shared/private encoder as the first learned arm.
- **[H] Hypothesis.** A scientific claim the bench measures. A negative or inconclusive result is a valid outcome recorded in the atlas. Examples: transfer at matched regime per descriptor, usefulness of a regime coordinate, routing beating dense.

## Three execution paths, one ledger

A run follows one of three paths, chosen by `Operation.assess`, never by a planner and never by an LLM.

```
record ──▶ assess(task, record)
             │ supported, op has no model   ──▶ reference path: classical op → Run
             │ supported, op is a model     ──▶ learned path: model op → Run (inputs limited to prediction-time fields)
             │ record is a summary          ──▶ output-only path: import_summary op → Run with upstream_asserted quantities
             └ unsupported / unknown        ──▶ no run; the assessment is returned with reasons and missing items
```

All three write the same `Run`. The bench reads runs and writes reports. Nothing else exists in the core.

## Where the science is

The core is deliberately empty of physics. The science lives in:

1. **Pack operations** (section 01, `Operation`): estimators, transforms, forward models, each with preconditions, assumptions, and a transform class.
2. **Pack regime declarations**: dimensionless coordinates with placeholder or measured ranges, and the canonical anchor kind per regime box.
3. **TaskSpecs**: what may be seen, what must be returned, how truth is obtained.
4. **The evaluation protocol** (section 03): firewall, splits, pairing, budgets, hypotheses, gates.

The anchor concept from the spec, a common channel vocabulary with descriptors defined as functionals of a canonical representation, is enforced by one field: every quantity in a `TaskSpec` names its `canonical_kind` or is tagged `not_channel`. That is the entire mechanism by which two packs' descriptors become comparable, and it costs one string per quantity.
