# Project status, assumptions & gaps

A living snapshot of where the library stands, the assumptions baked in, and the
known gaps. Pairs with `architecture.md` (how it fits together).

## Overview

A form-by-form automation library for **342 Maine Judicial Branch forms**. Each
`forms/<ID>/` is self-contained (schema, mapping, metadata, agent skill, README,
sample case). A shared, optional `engine/` (filler + 42 recipes + vision audit)
consumes those folders; five integration adapters are *specified* in
`docs/integrations/` but **not yet built**. Blank PDFs are **not** redistributed
— `tools/fetch_pdfs.py` pulls them from the official portal, verified against
`catalog/pdf_manifest.json`.

## Mapping maturity (the real signal)

`mapping.json` `status` per form:

| Tier | Count | Trust |
|---|---|---|
| `recipe` (engine recipe, vision-audit-verified upstream) | 66 | audit-verified fill code |
| `verified` (mapping render-verified by the audit loop) | 208 | reviewed mapping |
| `opus-adjudicated` (model-adjudicated mapping) | 6 | reviewed mapping |
| `no-mappable-fields` (informational form, nothing to fill) | 62 | n/a |

Intermediate pipeline statuses (`draft-heuristic`, `ai-mapped`,
`vision-mapped`, `opus-reviewed`) are written by `tools/` during remapping
and no longer appear in the shipped `forms/` tree.

Verification ledger: `catalog/vision_audit.json`. "Verified" means
machine-reviewed (render + audit loop), **not** attorney-reviewed.

## Pipeline (built & demonstrated)

scaffold (`tools/scaffold_forms.py`) → heuristic map → LLM text-map
(`tools/ai_map_forms.py`) → fill (`engine/fill_via_mapping.py`) → vision audit
(`tools/vision_audit.py`) → vision re-map of failures (`tools/vision_map_forms.py`).
The canonical fact object was extended with `first/middle/last` name and numbered
minor-child roles; width-fit is wired into the mapping fill path.

> **Running the LLM/vision tools** needs a local OpenAI-compatible endpoint. Set
> `MCF_LLM_ENDPOINTS` (comma-separated, defaults to `http://localhost:8080/v1`).

## Load-bearing assumptions

1. **The canonical fact object is the contract.** Roles are limited to
   `plaintiff`/`defendant`/`attorney` + numbered `child_N`. No `witness`,
   `guardian`, `decedent`/`estate`, or third-party roles — probate/multi-party
   forms will hit this.
2. **A field's AcroForm name reflects its purpose.** False on merged/poorly-
   authored forms. NB: the schema's `label` field is the AcroForm field *name*,
   not the printed text (despite `architecture.md`'s wording) — which is why
   vision mapping exists.
3. **One family-shaped sample represents all forms.** `examples/sample_case.json`
   is a generic `Doe v. Roe` family case; criminal/tax/probate forms' real fields
   are barely exercised, so coverage/audit numbers skew family-law.
4. **LLM drafts are good-enough starting points**, not verified mappings.
5. **MJB portal URLs are stable** (the fetch manifest depends on it).

## Gaps & open items

- **Adapters**: the MCP server and codex plugin are built; the remaining
  `docs/integrations/` adapters (docassemble, LangChain/LangGraph, PandaDoc,
  Pi harness) are specified but not built.
- **Provenance is split**: `form.yaml: automation_status` is coarse —
  `schema-only` (276) / `recipe` (66), now reconciled to the 66 forms whose
  `mapping.json` status is `recipe` (CR-004/CR-198/MJ-007 were re-mapped
  after upstream drift and no longer count). The finer-grained
  `mapping.json` status remains the real signal.
- **Audit is family-sample biased** and only renders the first 3–4 pages; the
  sample carries 2 children (forms with more child rows fill only those 2).
- **Carryovers:** an Opus re-run of the mappers is pending API auth; engine bug
  fixes are staged on a `backport/oss-review-fixes` branch in the upstream engine
  repo (un-merged, needs re-audit); engine internal test fixtures still contain
  fictional sample names (only matters if made public).
