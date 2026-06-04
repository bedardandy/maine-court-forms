# Project status, assumptions & gaps

A living snapshot of where the library stands, the assumptions baked in, and the
known gaps. Pairs with `architecture.md` (how it fits together) and `KICKOFF.md`
(how it was bootstrapped).

## Overview

A form-by-form automation library for **350 Maine Judicial Branch forms**. Each
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
| `recipe` (engine recipe, vision-audit-verified upstream) | 71 | authoritative |
| `vision-mapped` (set-of-marks VL, reads visible labels) | 61 | drafted, partly audited |
| `ai-mapped` (text LLM over field labels) | 211 | drafted, partly audited |
| `draft-heuristic` (regex label match only) | 7 | weak (100+-field giants only) |

Verification ledger: `catalog/vision_audit.json` — 89 audited, 83 render clean.
A single-pass VL audit is **not** full verification.

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

- **Licensing unchosen** (`LICENSE.md`) — blocks any public release.
- **No adapter is built** — the portable-substrate premise is unproven; nothing
  consumes `mapping.json` in production (`fill_via_mapping.py` is a verify tool).
- **No tests / CI** — cheap wins available with no cluster/PDFs: validate every
  `mapping.json` key against the contract, run `map_form` over all schemas,
  confirm fixtures resolve.
- **7 forms (100+-field giants) remain draft-heuristic** — text mapping
  overflows the model context and vision set-of-marks overcrowds the page;
  field-list chunking would be the real fix.
- **LLM mappings are largely un-audited** — only ~140 of the ~272 ai/vision-
  mapped forms have been through the vision audit; the rest are drafts.
- **Provenance is split**: `form.yaml: automation_status` still reads
  `schema-only` for every LLM/vision-mapped form; nothing promotes clean-audited
  forms to a "verified" tier.
- **Audit is family-sample biased** and only renders the first 3–4 pages; the
  sample carries 2 children (forms with more child rows fill only those 2).
- **Carryovers:** an Opus re-run of the mappers is pending API auth; engine bug
  fixes are staged on a `backport/oss-review-fixes` branch in the upstream engine
  repo (un-merged, needs re-audit); engine internal test fixtures still contain
  fictional sample names (only matters if made public).
