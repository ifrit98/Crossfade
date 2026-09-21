# Build the Crossfade LaTeX documents with tectonic (brew install tectonic).
# `make` builds both PDFs; `make clean` removes them.
DOCS = crossfade-math crossfade-math-brief crossfade-full
all: $(addsuffix .pdf,$(DOCS)) figures/architecture-standalone.pdf
%.pdf: %.tex math-core.tex macros.tex crossfade.bib figures/architecture.tikz
	tectonic $<
figures/architecture-standalone.pdf: figures/architecture-standalone.tex figures/architecture.tikz
	cd figures && tectonic architecture-standalone.tex
clean:
	rm -f $(addsuffix .pdf,$(DOCS)) figures/architecture-standalone.pdf
.PHONY: all clean
