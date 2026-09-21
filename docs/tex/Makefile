# Build the Crossfade LaTeX documents with tectonic (brew install tectonic).
# `make` builds both PDFs; `make clean` removes them.
DOCS = crossfade-math crossfade-math-brief crossfade-full
all: $(addsuffix .pdf,$(DOCS))
%.pdf: %.tex math-core.tex macros.tex crossfade.bib
	tectonic $<
clean:
	rm -f $(addsuffix .pdf,$(DOCS))
.PHONY: all clean
