# Maine Court Forms — Open Automation Library

[![tests](https://github.com/bedardandy/maine-court-forms/actions/workflows/ci.yml/badge.svg)](https://github.com/bedardandy/maine-court-forms/actions/workflows/ci.yml)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

A community-maintained, **form-by-form** library of **342 Maine Judicial Branch
court forms** structured for programmatic filling. Every form is a self-contained
folder — machine-readable metadata, an AcroForm field schema, an agent fill-guide
("skill"), and a canonical fact→field mapping — so any automation layer can fill a
form without re-deriving its field structure. The blank PDFs themselves are
**fetched on demand from the official portal and never redistributed** (see
[Getting the blank PDFs](#getting-the-blank-pdfs)).

It's built to be **driven by an LLM harness** — Claude Code, codex, Hermes,
openclaw, or any MCP client (see [Point any LLM harness at it](#point-any-llm-harness-at-it))
— and works just as well under a [docassemble](https://docassemble.org) interview,
a LangGraph node, a PandaDoc template sync, or a custom pipeline.

> **Not legal advice.** Blank forms are official Maine Judicial Branch
> documents. The surrounding metadata, skills, and mappings are
> community-maintained and may lag form revisions. Always verify against the
> [official source](https://www.courts.maine.gov/forms-fees-fines/forms.html)
> before filing.

## Scope & related work

This library covers **Maine Judicial Branch court forms** from the unified-court
forms portal. Those PDFs already ship with AcroForm fields, so the work here is
*mapping* them (and, where the field **names** are misleading, re-reading the
form visually).

**Maine probate forms are intentionally out of scope here.** Maine probate is
administered by the county Probate Courts, a separate source whose PDFs are
typically **flat** (no AcroForm fields) and need fields *created*, not just
mapped — a different technique. That work lives in a companion project,
[**`maine-probate-forms`**](https://github.com/bedardandy/maine-probate-forms)
(field detection + VLM validation + widget injection). The split is
deliberate: court forms → field mapping; probate forms → field creation.

## Point any LLM harness at it

This library is meant to be **driven by an agent** — Claude Code, codex, Hermes,
openclaw, or any MCP client. Point one at the repo and say *"use this project to
assist with: \<your situation\>"*. There are two on-ramps:

- **MCP server (recommended).** `tools/mcp_server.py` exposes `find_forms` /
  `get_form` / `fill_form` so the agent calls tools instead of reading docs. It's
  pre-registered via **`.mcp.json`**, or add it manually:
  ```bash
  claude mcp add maine-court-forms -- python3 tools/mcp_server.py
  ```
  A **`.codex-plugin/`** manifest and a top-level **`skills/route-and-fill/`**
  skill ship for harnesses that consume those.
- **Plain CLI workflow.** Route (`tools/find_forms.py`) → read the form's
  `SKILL.md` + trust tier → build a canonical fact object → fetch the PDF
  (`tools/fetch_pdfs.py`) → fill (`engine/fill_via_mapping.py`) → verify. The full
  protocol is in **`AGENTS.md`** / **`docs/agent-workflow.md`**, with a worked
  example in **`examples/fact_pattern_example.md`**.

Every fill is a **draft to be verified** before filing, and each form carries a
**trust tier** (see [Two tiers of automation](#two-tiers-of-automation)) the agent
should surface along with any missing facts.

## Layout

```
forms/<FORM_ID>/        one self-contained folder per form
  <FORM_ID>.pdf         blank source form — fetched on demand, not in git
  schema.json           AcroForm field schema (id, type, rect, page, label)
  fields.csv            human-friendly field listing
  form.yaml             metadata: title, category, court, governing law, tags
  README.md             human doc: purpose, who files, related forms, source
  SKILL.md              agent fill-guide: facts needed + field-by-field map
  mapping.json          canonical fact-key -> field_id map
  examples/             sample fact pattern(s)

catalog/                cross-form indices (families, workflows, courts)
  pdf_manifest.json     per-form source URL + size + SHA-256 for fetching blanks
engine/                 reference fill + audit engine (optional to use)
  recipes/              per-form fill recipes for the trickier forms
docs/
  architecture.md       how the pieces fit together
  integrations/         adapter specs (docassemble, LangChain, PandaDoc, ...)
tools/
  find_forms.py         route a fact pattern -> candidate forms + workflows
  fetch_pdfs.py         downloads blank PDFs from the official portal (verified)
  check_upstream.py     re-probe official URLs; flag forms the courts have revised
  mcp_server.py         MCP server: find_forms / get_form / fill_form
  scaffold_forms.py     regenerates the per-form folders from source data
skills/route-and-fill/  top-level agent skill (the route -> fill protocol)
.mcp.json               MCP registration; .codex-plugin/ — codex/openclaw manifest
Makefile                dev entry points: test / route / fetch / coverage / mcp
NOTICE                  Maine Judicial Branch attribution for the blank forms
```

## Getting the blank PDFs

The official blank forms are **not redistributed** here (they belong to the
Maine Judicial Branch — see `LICENSE.md`). Fetch them on demand; each download
is verified byte-for-byte against `catalog/pdf_manifest.json`:

```bash
python3 tools/fetch_pdfs.py                      # all forms
python3 tools/fetch_pdfs.py --forms AD-001,AD-022 # a subset
```

You only need this to *fill* a form (the schema/metadata work without it).

### Staying current — detecting a revised form

Every mapping was enriched against one specific revision of the blank, pinned by
SHA-256 in `catalog/pdf_manifest.json`. The portal serves the *current* revision
at a stable URL, so when the courts update a form the bytes change while the URL
does not — and a fill built on the old mapping can land values in shifted
widgets. Two guards catch this:

```bash
python3 tools/check_upstream.py            # re-probe official URLs; flag CHANGED / GONE
```

`check_upstream` re-downloads each blank, hashes it, and reports any form whose
bytes no longer match the manifest. It is read-only and exits non-zero on any
change, so it runs as a scheduled early-warning (`.github/workflows/drift.yml`,
weekly). When it flags a form, re-map it, then `--update-manifest` to adopt the
new hash. At **fill time**, `fill_via_mapping` checks the on-disk blank against
the manifest first — `MCF_VERIFY_BLANK=warn` (default), `strict`, or `off` — so a
blank swapped on disk cannot be filled unnoticed.

## Two tiers of automation

Each form's `form.yaml` carries an `automation_status`:

- **`recipe`** — a dedicated, audit-verified fill recipe exists in
  `engine/recipes/`. These forms handle non-obvious widget quirks (column
  splits, off-by-one labels, narrative blanks) and have been visually
  verified. `mapping.json` points at the recipe.
- **`schema-only`** — the form has a complete field schema and a
  *draft-heuristic* `mapping.json` derived from field labels. Good enough to
  start; needs review before production use.

## Quickstart (reading a form)

```python
import json, yaml, pathlib
form = pathlib.Path("forms/AD-001")
meta   = yaml.safe_load((form / "form.yaml").read_text())
schema = json.loads((form / "schema.json").read_text())
mapping= json.loads((form / "mapping.json").read_text())
print(meta["title"], "—", meta["field_count"], "fields")
```

## Status

Field schemas are complete for all **342 forms**. Of those, **71 are recipe-tier**
(dedicated, audit-verified fill recipes) and **279 are schema-only** (draft-heuristic
mappings — good to start, verify before production use). The `docs/integrations/`
adapter specs (docassemble, LangChain/LangGraph, PandaDoc, Pi harness, MCP) are
**specified, and not all are built yet** — contributions welcome.
