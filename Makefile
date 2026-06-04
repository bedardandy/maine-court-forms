# Maine Court Forms — developer entry points.
.PHONY: help test route fetch coverage mcp

help:
	@echo "make test             run the deterministic regression suite (same gate as CI)"
	@echo "make route Q='...'    route a fact pattern to candidate forms + workflows"
	@echo "make fetch FORMS=...  download blank PDFs from the official portal (verified;"
	@echo "                      omit FORMS to fetch all)"
	@echo "make coverage         mapping-coverage report across all forms"
	@echo "make mcp              run the MCP server (find_forms / get_form / fill_form)"

test:
	python3 -m pytest tests/ -v --ignore=tests/test_opus_judge.py

route:
	python3 tools/find_forms.py "$(Q)"

fetch:
	python3 tools/fetch_pdfs.py $(if $(FORMS),--forms $(FORMS),)

coverage:
	python3 tools/mapping_coverage.py --list

mcp:
	python3 tools/mcp_server.py
