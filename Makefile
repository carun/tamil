SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
BUILDDIR      = _build

BOOKS = mastering-the-core-teachings-of-the-buddha process-of-insight-meditation

.PHONY: html clean help $(BOOKS)

help:
	@echo "Usage:"
	@echo "  make html          - Build the unified site"
	@echo "  make <book-name>   - Build a single book standalone"
	@echo "  make clean         - Clean all build artifacts"

# Build the unified site from the top-level conf.py
html:
	@$(SPHINXBUILD) -M html "." "$(BUILDDIR)" $(SPHINXOPTS)

# Build individual books using their own conf.py
$(BOOKS):
	$(MAKE) -C $@ html

clean:
	@rm -rf $(BUILDDIR)
	@for book in $(BOOKS); do \
		rm -rf $$book/$(BUILDDIR); \
	done
