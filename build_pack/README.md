# Crossfade Build Pack v0.3

**Date:** 2026-09-18
**Status:** Implementation-ready for W0 and W3. W1 is ready pending one sign-off from the sonar lead (the target quantity). W2 is a research charter whose data and simulator inputs are listed as open.
**Supersedes:** `archive/crossfade_build_pack_v0_2/`. Nothing in v0.2 is deleted; this pack records what was kept, merged and cut, and why.
**Basis:** the Crossfade Technical Spec v0.2 (the shared doc), `archive/synthesis.md`, `archive/review/01` through `archive/review/04`, and the transcript.

## What this pack is

A set of contracts, a repository layout, an evaluation protocol, four build slices with acceptance tests, and the open questions that block each slice. It is written so that an engineer can start W0 on Monday without a design meeting, and so that a reviewer can tell, for any requirement, whether it is a software guarantee, a provisional choice, or a scientific hypothesis.

## The one decision everything else follows from

Crossfade is **one Python package with five modules, files plus SQLite for storage, and no services, no plugin discovery, no workflow engine, no base-class hierarchies, and no state machines beyond the enums on a run record.** Every requirement from the v0.2 review survives that constraint. Most of the v0.2 pack's apparent size does not. `00_meta_architecture.md` states the decision, what it rejects, and the size budgets that enforce it.

The test for any proposed component is one sentence: **if it can be a Pydantic model, a function, or a pytest, it is not a service, a base class, a plugin system, or a state machine.**

## Contents

| File | Purpose |
|---|---|
| `00_meta_architecture.md` | The decision, the rejected alternatives, the size budgets, the three-tag rule |
| `01_contracts.md` | The five record types, every field, every state enum, the invariants |
| `02_repo_layout.md` | Package layout, module responsibilities, dependencies, CLI, test layout |
| `03_evaluation_protocol.md` | Firewall, splits, pairing, budgets, hypotheses, gates, decision rule |
| `04_slices.md` | W0 to W3 now, three later; dependencies, gates, estimates |
| `05_decision_register.md` | ADRs with status and what each blocks |
| `06_data_and_simulators.md` | Simulator candidates, data candidates, independence statement, data manifest, what is open |
| `prds/PRD-W0-workbench.md` | Ingest, compute T0, replay, refuse. One demo, one test suite |
| `prds/PRD-W1-first-task.md` | RMS delay spread and arrival count from simulated beam time series, classical estimators, benchmark |
| `prds/PRD-W2-transfer-charter.md` | HF pack, SSL arm, preregistered transfer trial, typed uncertainty |
| `prds/PRD-W3-output-only-adapter.md` | Read-only import of an existing system's summaries, comparison, duplicate warnings |
| `templates/` | PRD checklist, research charter, task spec YAML, pack manifest, data manifest, independence statement |
| `sources.md` | What was read and what was checked |

## How to read the requirements

Every requirement carries one of three tags. **[G]** is a guarantee the software enforces; failure is a bug. **[P]** is a provisional choice, replaceable without changing contracts. **[H]** is a hypothesis to be measured; failure is a result, recorded in the atlas, and the platform is unaffected.

"MUST" describes a proposed implementation contract. It does not establish that any hypothesis is true. No dataset, simulator, threshold, or model result has been invented; where one is needed and not yet available, it is listed as open with the slice it blocks.

## Sequence

1. Start W0 and W3 now. They share the `Record` and `Run` contracts and nothing else; two people can run them in parallel.
2. Put the W1 target-quantity question to the sonar lead this week. W1's PRD is written against the proposed answer so a yes is enough to start.
3. W1 starts the day the quantity is confirmed. Its packs shape the contracts alongside W0's fixtures.
4. W2's charter is filled in as its open items (section 6) are resolved. Unlabeled pretraining may begin as soon as W1's split policy is frozen.
5. Routing, explanations and fusion wait for a reason to exist.
