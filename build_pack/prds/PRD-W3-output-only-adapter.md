# PRD-W3 — Output-only adapter for an existing system

**Status:** Ready pending ADR-25: which system and which export format.
**Owner:** Core engineer. **Reviewers:** The owning program's engineer, sonar lead.
**Dependencies:** W0 `Record` and `Run`. Independent of W1 and W2; runs in parallel.
**Contracts:** No new types. Adds `packs/<system>_export`.
**Invariants:** CF-13, CF-20, CF-21.
**Size budget:** 400 lines.

## Outcome

An analyst imports one existing system's summary export (detections, tracks, scalar features, with whatever confidence the system reports), sees it as records with lineage and origin `upstream_asserted`, compares two exports of the same interval, and is warned when two records derive from the same underlying observation. Nothing is written back and nothing is re-estimated.

## Scope

One pack with two operations: `import_summary` (parses the export into `summary` records with the system's assertions, its confidence field kept in `diagnostics`, and `group_ids` from whatever session or file identifiers the export carries) and `compare_summaries` (aligns two summary records on time and declared keys, lists agreements and disagreements, and emits a duplicate-evidence warning when both resolve to the same `parents`).

**Non-goals.** Any estimate; any anchor; any learned op; any numerical fusion; any write to the upstream system; any live connection. The adapter reads files the system already produces.

## Functional requirements

| Id | Requirement | Invariant |
|---|---|---|
| W3-F01 | Every imported quantity has `origin = upstream_asserted`; upstream confidence never appears under `uncertainty` | CF-13 |
| W3-F02 | The adapter has no code path that writes to any location the upstream system reads | CF-21 |
| W3-F03 | `compare_summaries` treats two records with a common parent as one piece of evidence and says so | CF-20 |
| W3-F04 | Any request on a summary record for an op with a channel precondition is `unsupported` | CF-04 |
| W3-F05 | Missing calibration or timing in the export is recorded as a missing capability, visible in `inspect` | CF-03 |
| W3-F06 | `data_use` from the export's owner is carried on every record | — |

## Acceptance tests

| Id | Given | When | Then |
|---|---|---|---|
| W3-AT-01 | A sample export | `import_summary` | Records of kind `summary`; quantities `upstream_asserted`; confidence in `diagnostics` |
| W3-AT-02 | Two exports of one interval | `compare_summaries` | Agreements and disagreements listed; no combined number produced |
| W3-AT-03 | Two records derived from one import | Compare | Duplicate-evidence warning; counted once |
| W3-AT-04 | An export lacking timing | Import | Record stored; `has_timing` absent; `inspect` shows it |
| W3-AT-05 | The adapter's source | Static check | No file writes outside the store |
| W3-AT-06 | A summary record | Assess `autocorr_pdp` | `unsupported`, `missing = ["has_phase", "has_timing"]` or the applicable subset |

## Definition of done

Six tests green on a sample export supplied by the owning program. A demo showing import, inspect, compare, and the refusal. A note to the program engineer listing which capabilities the export lacks and what adding each would enable, with no obligation attached.
