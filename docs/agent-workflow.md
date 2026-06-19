# Agent workflow — "use this project to assist with: \<fact pattern\>"

This library is built to be driven by an agent (Claude Code, codex, or any
MCP client). Given a plain-language fact pattern, follow this protocol.

> **Not legal advice.** Output is a draft to be reviewed against the official
> form. Always surface uncertainty and what's missing.

## The 6 steps

**1. Route — which form(s)?**
```bash
python3 tools/find_forms.py "evict a tenant for nonpayment of rent"
```
Returns matching **workflows** (ordered form sequences for a matter, from
`catalog/workflows.json`) and top **forms** (`catalog/forms_index.json`). Pick
the form(s) the fact pattern requires.

**2. Understand the form — what facts are needed, and can I trust it?**
- Read `forms/<ID>/SKILL.md` (facts needed + field-by-field guide) and
  `forms/<ID>/form.yaml` (court, category, governing law).
- Check `forms/<ID>/mapping.json` `status` — the **trust tier**:
  - `recipe` → form-specific engine recipe (audit-verified)
  - `verified` / `opus-adjudicated` → reviewed mapping (render-verified /
    model-adjudicated) — still check the output before filing
  - `no-mappable-fields` → nothing to fill (informational form)
- `catalog/vision_audit.json` records which forms render clean.
- `forms/<ID>/fill_guidance.json` gives **per-field fill-value guidance** —
  what kind of text each blank wants (person name vs county vs dollar amount vs
  MM/DD/YYYY date vs checkbox), which fields are required, and which belong to a
  one-of choice group (`docs/field-guidance.md`; surfaced by MCP `get_form` as
  `field_guidance`). Preflight uses it to warn on a value that doesn't match its
  field's type.
- `forms/<ID>/logic.json` adds **if/then cross-field rules** (`docs/logic-rules.md`)
  — conditional-required fields, attachment & companion-form triggers, value
  incompatibilities, and value inferences (e.g. a 1:00 court time is PM).
  Preflight / `lint_case` evaluate them against your case and return `logic-*`
  warnings; MCP `get_form` lists the rules as `logic`.

**3. Extract — build the canonical fact object.**
Translate the fact pattern into the canonical shape (full spec in
`docs/integrations/README.md`; a worked example in `examples/`):
```jsonc
{ "matter":  { "docket_number", "court_county", "court_location", "case_type", "filing_date" },
  "parties": { "plaintiff": {...}, "defendant": {...}, "attorney": {...}, "child_1": {...} },
  "party":   { "full_name", "first_name", "last_name", "address", ... },
  "facts":   { /* form-specific */ } }
```
Leave a field out if the fact pattern doesn't supply it — don't invent values.

Then **preflight the case** before any fill — typo'd keys/roles resolve to
nothing and produce a near-blank PDF:
```bash
python3 tools/preflight.py case.json --form <ID>
```
It validates against the contract (`catalog/canonical_case.schema.json`) and
returns machine-readable issues with suggestions (unknown top-level keys,
wrong role vocabulary like `parties.lawyer` → `parties.attorney`, missing
required facts). The MCP `lint_case` tool is the same check; `fill_form`
runs it automatically and refuses on hard errors.

**4. Fetch the blank PDF** (not shipped — see `LICENSE.md`):
```bash
python3 tools/fetch_pdfs.py --forms <ID>
```

**5. Fill.**
```bash
python3 -m engine.fill_via_mapping --form <ID> --case case.json   # uses mapping.json
# recipe-tier forms: python3 -m engine.fill --form <ID> --case case.json
```
(The MCP `fill_form` tool picks the right path automatically.)

**6. Verify & report.** Run the deterministic post-fill check first:
```bash
python3 -m engine.verify_fill --form <ID> --pdf <out>/<ID>.filled.pdf \
    --intended <out>/<ID>.kv.json
```
It reopens the filled PDF and diffs widget values against the intended
fills (per-field placed/differs/missing/no-widget + a summary; the MCP
`fill_form` tool runs it automatically and returns `fill_verify`). Then
inspect the PDF (or run `tools/vision_audit.py` for placement-vs-label).
Report: what was filled, the trust tier, any **unresolved/missing facts**,
and that it must be verified before filing.

Example intake fact patterns (one realistic plain-language narrative per form
family, all fictional) live at `tools/smoke/fact_patterns.json` — useful as
routing/extraction test inputs and as worked examples of what the canonical
fact object is built from (`tools/smoke_fact_patterns.py` runs them end-to-end).

## MCP (recommended for agents)

Register the server so the agent calls tools directly:
```bash
claude mcp add maine-court-forms -- python3 tools/mcp_server.py
```
Tools: `find_forms(query)`, `get_form(form_id)`, `fill_form(form_id, facts)`.

## Two data shapes — don't confuse them
The **canonical fact object** above is what you build from the fact pattern and
what `mapping.json` targets. The reference engine has a separate internal case
shape; `engine/canonical.py` bridges them, and `engine/fill.py` auto-detects —
so always hand the agent the canonical object.
