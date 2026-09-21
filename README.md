# Crossfade

A capability-aware evidence and experiment platform for wave-propagation inference. Crossfade connects sonar, HF skywave radar and RF systems through a common channel vocabulary anchored on the channel spreading function, and it measures where learned structure transfers between domains instead of assuming it.

## Documents

| Document | Audience | What it is |
| --- | --- | --- |
| [Crossfade in Two Pages](docs/Crossfade-in-Two-Pages.md) | Signals experts | The physics, the choices, and how the ML and LLM pieces fit, in about 1,400 words |
| [Crossfade Technical Spec](docs/Crossfade-Technical-Spec.md) | Engineers and reviewers | v0.3 of the full specification: contracts, architecture, evaluation protocol, build slices, open questions, sources |
| [Build pack v0.3](build_pack/README.md) | Implementers | Meta-architecture, the five contracts, repo layout, evaluation protocol, slices W0 to W3, decision register, PRDs, templates |
| [Crossfade: The Mathematics in Three Pages](docs/tex/crossfade-math-brief.tex) | The signals lead, first read | LaTeX. The math edition condensed to three pages with the same nine checks; PDF alongside |
| [Crossfade: The Mathematics to Check](docs/tex/crossfade-math.tex) | The signals lead | LaTeX. Every equation the platform relies on, with nine numbered checks; two are on the critical path. Build with `make -C docs/tex` (tectonic) |
| [Architecture diagram](docs/tex/figures/architecture-standalone.pdf) | Anyone | One page: layers L0 to L7, the five record types, the three execution paths and the ledger. TikZ source in `docs/tex/figures/architecture.tikz`, also Figure 1 of the full thesis |
| [Crossfade, full thesis](docs/tex/crossfade-full.tex) | Anyone who wants the whole argument in one document | LaTeX. Motivation, the mathematics, architecture and contracts, models, uncertainty, evaluation protocol, build plan, decision register, open questions |

## Layout

```
docs/          the two markdown documents above; docs/tex/ holds the LaTeX sources (math-core.tex is shared by both PDFs)
build_pack/    build pack v0.3, the implementation record for the spec
archive/       how we got here: the transcript, the two original plans, the synthesis,
               the v0.2 review and responses, the superseded v0.2 build pack, the v0.1 spec export
crossfade/     the package (W0 workbench, in progress on a branch)
```

## Status

Specification complete through v0.3. The W0 workbench slice is being drafted; the first scientific task (W1) is waiting on two answers from the sonar lead, listed at the end of both documents. Architecture may change after the signals lead's review.
