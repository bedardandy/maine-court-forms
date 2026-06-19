# Maine Court Forms — agent guide

This repo is a form-by-form automation library for Maine Judicial Branch court
forms. You can drive it to **fill forms from a plain-language fact pattern**.

When the user says *"use this project to assist with: \<situation\>"*, follow
the protocol in **`docs/agent-workflow.md`**. In short:

1. **Route:** `python3 tools/find_forms.py "<the situation>"` → candidate forms +
   matter workflows (`catalog/workflows.json`, `catalog/forms_index.json`).
2. **Understand:** read `forms/<ID>/SKILL.md` (facts needed) + `form.yaml`;
   `forms/<ID>/mapping.json` `facts` declares which canonical keys are
   **required** (caption party names — the form is facially incomplete
   without them) vs merely **used**, so you can ask targeted intake
   questions; check `mapping.json` `status` for the **trust tier**
   (`recipe` = form-specific engine code; `verified`/`opus-adjudicated` =
   reviewed mapping; `no-mappable-fields` = nothing to fill).
3. **Extract:** build the **canonical fact object** (`{matter, parties, party,
   facts}` — spec in `docs/integrations/README.md` + JSON Schema in
   `catalog/canonical_case.schema.json`, example in `examples/`) from
   the fact pattern. Don't invent values; omit unknowns. Then preflight it:
   `python3 tools/preflight.py case.json --form <ID>` (MCP: `lint_case`)
   catches typo'd keys/roles (e.g. `parties.lawyer` → `parties.attorney`)
   that would otherwise fill nothing, and emits `value-type` warnings when a
   supplied value doesn't match a field's declared type (per-field value
   semantics live in `forms/<ID>/fill_guidance.json` —
   `tools/derive_field_guidance.py`, `docs/field-guidance.md`: `value_type`
   person_name/county/currency/date+format/time/address/zip/checkbox/signature,
   plus `required` and `conditional` one-of groups; MCP `get_form` returns it as
   `field_guidance`). Preflight also evaluates `forms/<ID>/logic.json` — **if/then
   cross-field rules** (`tools/derive_logic.py` + hand-authored
   `logic.authored.json`, engine `tools/logic_engine.py`,
   `docs/logic-rules.md`): conditional-required fields, attachment / companion-
   form triggers (e.g. minor children → FM-050/FM-040; confidential address →
   PA-015; debt-buyer chain-of-title per 32 M.R.S. §11019), value
   incompatibilities (garnishment > 25% disposable, 14 M.R.S. §3127), and value
   inferences (a court time H:MM without AM/PM is almost certainly PM) — all
   warnings-only, surfaced as `logic-*` warnings and via MCP `get_form` `logic`.
4. **Fetch the PDF:** `python3 tools/fetch_pdfs.py --forms <ID>` (blank PDFs are
   not shipped; fetched from the official portal).
5. **Fill:** `python3 -m engine.fill_via_mapping --form <ID> --case case.json`
   (recipe-tier forms: `python3 -m engine.fill ...`).
6. **Verify & report:** run the deterministic post-fill check
   (`python3 -m engine.verify_fill --form <ID> --pdf <filled.pdf> --intended
   <kv.json>` — diffs widget values against the intended fills; the MCP
   `fill_form` tool runs it automatically and returns `fill_verify`), then
   inspect output; surface the trust tier, **any unresolved/missing facts**,
   and that it needs review.

**Or use the MCP server** (preferred): `python3 tools/mcp_server.py` exposes
`find_forms` / `get_form` / `lint_case` / `fill_form` as tools — register with
`claude mcp add maine-court-forms -- python3 tools/mcp_server.py`.

Example intake fact patterns (one realistic plain-language narrative per form
family, all fictional) live at `tools/smoke/fact_patterns.json` — useful as
routing/extraction test inputs and as worked examples of what the canonical
fact object is built from (`tools/smoke_fact_patterns.py` runs them end-to-end).

## Shared engine

`engine/` core, the drift tools (`tools/{check_upstream,fetch_pdfs}.py`), and
`tools/accessibility/` are thin shims over the
[`maine-forms-engine`](https://github.com/bedardandy/maine-forms-engine)
package (in `requirements.txt`; **required**) — this repo was the extraction
donor, so the package defaults ARE this repo's behavior. The shims keep every
documented `engine.*` / `tools/*` command and import path working unchanged;
the recipes, `fill_and_audit`, the addendum renderer, and the rich MCP server
(`tools/mcp_server.py`) stay in this repo.

## Rules
- **Not legal advice.** Filled output is a draft; it must be verified against the
  official form before filing. Always say so.
- **Respect the trust tier.** Even `verified`/`opus-adjudicated` mappings are
  machine-reviewed, not attorney-reviewed — tell the user to check field
  placement before filing.
- **Yellow lights are warnings, never blocks.** Fill results (engine + MCP
  `fill_form`) may carry `constraint_warnings` — paradoxical selections per
  the form's optional `constraints.json` (e.g. two court-caption boxes
  checked at once; harvested conservatively by
  `tools/harvest_constraints.py`, keys are schema field_ids) — and
  `radio_groups` on the mapping path (radio groups the engine never writes;
  each entry suggests an option to select by hand). Both fill paths also
  evaluate the form's optional `computations.json` — arithmetic printed
  verbatim on the form ("Total of lines 2(a)-(f)", "for a total of $"): a
  target the case omits is computed and filled (`computed_fields`), a
  supplied value is always written as-is, and a contradiction only adds a
  `COMPUTATION_MISMATCH` entry under `computation_warnings`. The mapping
  path routes computed values into widgets directly; recipe-tier forms
  (pointer-only mappings) get the engine's facts-only evaluation in
  `fill_one`, which merges omitted targets into the case before the recipe
  runs — same evaluator, same result keys. They list problems for a
  human to resolve; they never fail or alter a fill.
- **Never invent canonical fact-keys** — reuse the shape in
  `docs/integrations/README.md`.
- **Schemas are split lean/audit.** `forms/<ID>/schema.json` is the lean
  field inventory (field_id/type/page/rect/label/category) — cheap to read.
  `forms/<ID>/schema.audit.json` holds build-time research metadata
  (risk/eval scores, fill strategies) for the mapping toolchain; you never
  need it to route, extract, or fill (`tools/split_schema.py` maintains the
  split).
- Blank PDFs and run artifacts stay out of git (see `.gitignore`).
- Licensed Apache-2.0 (`LICENSE`).
