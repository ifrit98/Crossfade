# PRD-S00 — Task semantics and contract fixture

**Status:** Draft, ready for engineering review.  
**Owner:** Technical lead.  
**Reviewers:** Numerical/domain reviewer and platform engineer.  
**Dependencies:** None.  
**Requirements:** CF-003, CF-006, CF-009.  
**Source basis:** TS §§4–5, 7–10; proposed amendments R02, R03, R06.

## Outcome

An engineer can define an executable task, identify precisely which inputs it may use, and verify a result against an independent expected answer before any learned model is introduced.

## Scope

Implement a versioned TaskSpec, minimum Result/Uncertainty/Applicability states, a deterministic profile-width task, and a structured-output comparison task. Define fixture records that subsequent storage and pack SDK slices reuse.

Non-goals: unknown-channel estimation, simulator integration, training, regime inference, cross-domain performance, user interface, numerical evidence fusion.

## Task T0

`task_id`: `profile.weighted_rms_width`  
`task_kind`: deterministic transform  
`version`: `0.1`

Input: an explicitly declared set of delay coordinates and nonnegative **point weights**, a supported time unit, an optional mask, and an explicit positive reference time with a unit for normalized width. A point-weight profile is distinct from a continuous density or bin-integrated profile; unsupported conventions must be rejected rather than guessed.

Output: weighted mean delay, weighted RMS width about that mean, normalized RMS width, used-sample count, excluded-sample count, and the applicable convention. This is a calculation conditional on the supplied profile, not an uncertainty estimate of the physical channel that produced it.

Golden case: coordinates `[0, 2]` milliseconds and point weights `[1, 1]` produce mean `1` millisecond and RMS width `1` millisecond. Reference time `2` milliseconds produces normalized width `0.5`. The same record expressed as `[0, 0.002]` seconds with reference time `0.002` seconds yields the same physical result.

Reject zero total included weight, negative included weights, nonfinite included values, a nonpositive normalization reference, inconsistent coordinate lengths, or unspecified physical units. An intentionally masked entry is excluded and counted. Values outside the mask must not be silently used.

If normalization reference is absent, the task may return the unnormalized quantities as a partial result only when the TaskSpec explicitly permits that behavior. It must not invent a reference time.

## Output-only comparison task

A second fixture is a structured upstream summary with no complex signal or channel payload. It supports listing its assertions and provenance. A request for a phase-sensitive or full-channel operation on that input yields unsupported, naming missing capabilities.

This fixture exists to make the architecture's bypass path testable immediately.

## Functional requirements

| ID | Requirement |
|---|---|
| S00-F01 | Task identity includes version and the definitions/units of all quantities. |
| S00-F02 | Allowed prediction inputs and evaluation truth are distinct fields. |
| S00-F03 | Normalization reference and profile convention are explicit. |
| S00-F04 | Result states distinguish computation, scientific applicability, and uncertainty. |
| S00-F05 | Deterministic arithmetic uses uncertainty kind `not-applicable` for the computation; it does not assert noiseless physical measurements. |
| S00-F06 | Missing input requirements produce typed reasons, not fabricated default physics. |
| S00-F07 | The reference answer is stored independently of the implementation under test. |

## Acceptance tests

**AT-01:** Given the golden profile, when T0 runs, then the mean, width, and normalized width match the stated answers within a declared floating-point tolerance.

**AT-02:** Given equivalent coordinates in seconds and milliseconds, when both records run, then physical outputs agree after unit conversion and both original units remain recoverable.

**AT-03:** Given a masked invalid entry, when T0 runs, then that entry is excluded and the exclusion count is correct. Given an unmasked invalid entry, the task fails explicitly.

**AT-04:** Given zero total weight or a nonpositive reference scale, when validation runs, then the result is rejected with the appropriate reason code.

**AT-05:** Given a C0 summary, when a reconstruction task is requested, then the request is unsupported; when comparison is requested, the original assertions can be returned with origin `upstream-asserted`.

**AT-06:** Given a result without uncertainty or forward checking requirements, then the serialized record uses explicit not-applicable states, not a confidence value of one.

## Implementation increments

First define and test TaskSpec and Result schemas. Next implement the independent golden fixtures and arithmetic operation. Then add invalid/masked cases and the output-only fixture. Finally publish the fixtures and conformance expectations for S01/S02/S04.

## Definition of done

Schema documentation, serialized fixtures, reference answers, automated positive/negative tests, and a command/API-level demonstration of both supported calculation and unsupported reconstruction. All outputs state that this is an engineering fixture rather than a validated scientific estimator.
