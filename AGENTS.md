# Maine Court Forms — agent guide (AGENTS.md; same as CLAUDE.md)

This repo is a form-by-form automation library for Maine Judicial Branch court
forms. You can drive it to **fill forms from a plain-language fact pattern**.

When the user says *"use this project to assist with: \<situation\>"*, follow
the protocol in **`docs/agent-workflow.md`**. In short:

1. **Route:** `python3 tools/find_forms.py "<the situation>"` → candidate forms +
   matter workflows (`catalog/workflows.json`, `catalog/forms_index.json`).
2. **Understand:** read `forms/<ID>/SKILL.md` (facts needed) + `form.yaml`;
   check `forms/<ID>/mapping.json` `status` for the **trust tier**
   (`recipe` = form-specific engine code; `verified`/`opus-adjudicated` =
   reviewed mapping; `no-mappable-fields` = nothing to fill).
3. **Extract:** build the **canonical fact object** (`{matter, parties, party,
   facts}` — spec in `docs/integrations/README.md`, example in `examples/`) from
   the fact pattern. Don't invent values; omit unknowns.
4. **Fetch the PDF:** `python3 tools/fetch_pdfs.py --forms <ID>` (blank PDFs are
   not shipped; fetched from the official portal).
5. **Fill:** `python3 -m engine.fill_via_mapping --form <ID> --case case.json`
   (recipe-tier forms: `python3 -m engine.fill ...`).
6. **Verify & report:** inspect output (or `tools/vision_audit.py`); surface the
   trust tier, **any unresolved/missing facts**, and that it needs review.

**Or use the MCP server** (preferred): `python3 tools/mcp_server.py` exposes
`find_forms` / `get_form` / `fill_form` as tools — register with
`claude mcp add maine-court-forms -- python3 tools/mcp_server.py`.

## Rules
- **Not legal advice.** Filled output is a draft; it must be verified against the
  official form before filing. Always say so.
- **Respect the trust tier.** Even `verified`/`opus-adjudicated` mappings are
  machine-reviewed, not attorney-reviewed — tell the user to check field
  placement before filing.
- **Never invent canonical fact-keys** — reuse the shape in
  `docs/integrations/README.md`.
- Blank PDFs and run artifacts stay out of git (see `.gitignore`).
- Licensed Apache-2.0 (`LICENSE`).
