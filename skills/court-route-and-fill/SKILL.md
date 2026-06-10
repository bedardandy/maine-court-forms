---
name: court-route-and-fill
description: Go from a plain-language fact pattern to a filled Maine Judicial Branch court form. Use when the user describes a court situation (eviction, divorce/parental rights, small claims, protection from abuse, a civil or criminal matter) and wants the right form selected and filled. Routes to the form(s), reads the form's skill + trust tier, builds a canonical fact object, fetches the official blank PDF on demand, and fills it via the deterministic engine/ path.
---

# Route and fill a Maine court form

This repository maps Maine Judicial Branch **court** forms (the unified-court
portal). Those PDFs already carry AcroForm fields, so the work is *mapping* them
to a canonical fact object — and, where a form's field **names are misleading**,
trusting the audited recipe over the raw labels. The fill path is deterministic;
follow it directly.

> **Not legal advice.** Filled output is a draft. Always surface the trust tier,
> what's missing, and that it must be verified against the official form before
> filing.

## Use these

- The `tools/` and `engine/` directories and the catalogs under `catalog/` and
  `forms/<ID>/`. To drive the library over MCP, run `tools/mcp_server.py`
  (`find_forms` / `get_form` / `fill_form`).
- Blank PDFs are **not shipped**. Fetch on demand with `tools/fetch_pdfs.py`
  (each download is verified byte-for-byte against `catalog/pdf_manifest.json`).

## Workflow

1. **Route** the situation to candidate forms:
   ```bash
   python3 tools/find_forms.py "evict a tenant for nonpayment of rent"
   ```
   Returns matching **workflows** (ordered form sequences for a matter) and top
   **forms**. If the pick is ambiguous, confirm with the user.

2. **Understand & check trust.** Read `forms/<ID>/SKILL.md` (facts needed,
   field-by-field guide) and `forms/<ID>/form.yaml` (court, category, governing
   law). Read `forms/<ID>/mapping.json` `status` — the **trust tier**:
   - `recipe` → form-specific engine recipe (audit-verified).
   - `verified` / `opus-adjudicated` → reviewed mapping — still tell the user
     to check field placement before filing.
   - `no-mappable-fields` → nothing to fill (informational form).

3. **Build the canonical fact object** from the fact pattern (full spec in
   `docs/integrations/README.md`, worked example in `examples/`). Save as
   `case.json`:
   ```jsonc
   { "matter":  { "docket_number", "court_county", "court_location", "case_type", "filing_date" },
     "parties": { "plaintiff": {...}, "defendant": {...}, "attorney": {...}, "child_1": {...} },
     "party":   { "full_name", "first_name", "last_name", "address", ... },
     "facts":   { /* form-specific */ } }
   ```
   Omit anything the fact pattern doesn't supply — never invent values.

4. **Fetch the blank PDF:**
   ```bash
   python3 tools/fetch_pdfs.py --forms <ID>
   ```

5. **Fill:**
   ```bash
   python3 -m engine.fill_via_mapping --form <ID> --case case.json
   # recipe-tier forms: python3 -m engine.fill --form <ID> --case case.json
   ```
   (The MCP `fill_form` tool picks the right path automatically.)

6. **Verify & report.** Inspect the filled PDF (or run `tools/vision_audit.py`).
   Report what was filled, the trust tier, any **unresolved/missing facts**, and
   that it must be verified before filing.

## Notes

- The canonical fact object is what `mapping.json` targets; `engine/canonical.py`
  bridges it to the engine's internal case shape (`engine/fill.py` auto-detects),
  so always build the canonical object.
- The plan/fill layer is a pure function of the case object: same case in → same
  output. Good for golden-testing or mapping `resolved` values to template tokens.
