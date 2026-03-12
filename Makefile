SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
BUILDDIR      = _build

BOOKS = mastering-the-core-teachings-of-the-buddha process-of-insight-meditation

.PHONY: html clean help $(BOOKS) pdf pdf-mctb pdf-pim pdf-glossary

help:
	@echo "Usage:"
	@echo "  make html          - Build the unified site"
	@echo "  make <book-name>   - Build a single book standalone"
	@echo "  make clean         - Clean all build artifacts"
	@echo "  make pdf           - Build all PDFs"
	@echo "  make pdf-mctb      - Build MCTB PDF"
	@echo "  make pdf-pim       - Build PIM PDF"
	@echo "  make pdf-glossary  - Build glossary PDF"

# Build the unified site from the top-level conf.py
html:
	@$(SPHINXBUILD) -M html "." "$(BUILDDIR)" $(SPHINXOPTS)

# Build individual books using their own conf.py
$(BOOKS):
	$(MAKE) -C $@ html

# Build PDFs via pandoc + typst
pdf: pdf-mctb pdf-pim pdf-glossary

pdf-mctb:
	python3 scripts/build_pdf.py mastering-the-core-teachings-of-the-buddha \
		--title "புத்தரின் மைய போதனைகளை முழுமையாகக் கற்றறிதல்" \
		--author "Dr. Daniel M. Ingram" \
		--output $(BUILDDIR)/pdf/mctb.pdf

pdf-pim:
	python3 scripts/build_pdf.py process-of-insight-meditation \
		--title "விபஸ்ஸனா தியானத்தின் செயல்முறை" \
		--author "Sayadaw Janakābhivamsa" \
		--output $(BUILDDIR)/pdf/pim.pdf

pdf-glossary:
	python3 scripts/build_pdf.py glossary \
		--title "சொல்லாய்வு" \
		--output $(BUILDDIR)/pdf/glossary.pdf

clean:
	@rm -rf $(BUILDDIR)
	@for book in $(BOOKS); do \
		rm -rf $$book/$(BUILDDIR); \
	done
