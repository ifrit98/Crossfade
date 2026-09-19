# Crossfade

A capability-aware evidence and experiment platform for wave-propagation inference. Crossfade connects sonar, HF skywave radar and RF systems through a common channel vocabulary anchored on the channel spreading function, and it measures where learned structure transfers between domains instead of assuming it.

## Documents

| Document | Audience | What it is |
| --- | --- | --- |
| [Crossfade in Two Pages](docs/Crossfade-in-Two-Pages.md) | Signals experts | The physics, the choices, and how the ML and LLM pieces fit, in about 1,400 words |
| [Crossfade Technical Spec](docs/Crossfade-Technical-Spec.md) | Engineers and reviewers | v0.3 of the full specification: contracts, architecture, evaluation protocol, build slices, open questions, sources |
| [Build pack v0.3](build_pack/README.md) | Implementers | Meta-architecture, the five contracts, repo layout, evaluation protocol, slices W0 to W3, decision register, PRDs, templates |

## Layout

```
docs/          the two documents above
build_pack/    build pack v0.3, the implementation record for the spec
archive/       how we got here: the transcript, the two original plans, the synthesis,
               the v0.2 review and responses, the superseded v0.2 build pack, the v0.1 spec export
crossfade/     the package (W0 workbench, in progress on a branch)
```

## Status

Specification complete through v0.3. The W0 workbench slice is being drafted; the first scientific task (W1) is waiting on two answers from the sonar lead, listed at the end of both documents. Architecture may change after the signals lead's review.
