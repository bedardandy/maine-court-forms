#!/usr/bin/env python3
"""Scaffold self-contained per-form folders for the open-source release.

For each form it assembles a folder under forms/<FORM_ID>/ containing the
full artifact set:

    <FORM_ID>.pdf       blank fillable source form (from the PDF stash)
    schema.json         AcroForm field schema (id, type, rect, page, label)
    fields.csv          human-friendly field listing
    form.yaml           machine metadata (title/category/court/law/tags/...)
    README.md           human doc: purpose, who files, related, source URL
    SKILL.md            agent skill: facts needed + field-by-field fill guide
    mapping.json        canonical fact-key -> field_id map (draft unless a
                        recipe is present, in which case it is marked recipe)
    examples/sample_case.json   a representative fact pattern (if available)

Sources (all read-only; nothing in them is modified):
  --engine-repo   the mature engine repo (schemas, fields.csv, recipes)
  --pdf-stash     dir of blank source PDFs (<FORM_ID>.pdf)
  --skills-stash  prior per-form SKILL.md tree (optional, reused if present)

Idempotent: re-running overwrites generated artifacts but never edits the
source repos. Use --forms to limit to a subset (comma list) for a template
run; omit to scaffold every form that has a schema.
"""
from __future__ import annotations

import argparse
import csv
import json
import pathlib
import re
import shutil
import sys

import yaml

OSS_ROOT = pathlib.Path(__file__).resolve().parent.parent

# Federal IRS forms live in the engine repo but are out of scope for this
# Maine Judicial Branch library (the Maine-court mapping heuristic can't map
# them, and they aren't court forms). Skip them during auto-discovery.
# Maine Revenue Service forms (MRS-*) are kept.
EXCLUDE_PREFIXES = ("IRS-",)


def _load_json(p: pathlib.Path):
    try:
        return json.loads(p.read_text())
    except Exception:
        return None


def _index_by(items, key):
    out = {}
    for it in items or []:
        k = it.get(key)
        if k:
            out[k] = it
    return out


def _recipe_forms(engine_repo: pathlib.Path) -> set[str]:
    """Form ids that have a dedicated fill recipe (RECIPE3 dispatch)."""
    fa = engine_repo / "scripts" / "fill_and_audit.py"
    if not fa.exists():
        return set()
    m = re.search(r"RECIPE3\s*=\s*\{(.*?)\n\}", fa.read_text(), re.S)
    if not m:
        return set()
    return set(re.findall(r"[\"']([A-Z][A-Z0-9-]+)[\"']\s*:", m.group(1)))


def _governing_law_list(raw: str) -> list[str]:
    if not raw:
        return []
    parts = re.split(r"\s*-\s*\*\*|\*\*", raw)
    laws, seen = [], set()
    for p in parts:
        s = p.strip(" -*—")
        if s and re.search(r"\d", s) and s not in seen:
            seen.add(s)
            laws.append(s)
    return laws


def build_form_yaml(form_id, idx, inv, schema, has_recipe):
    meta = {
        "form_id": form_id,
        "title": (idx or {}).get("title", form_id).replace(f"{form_id} — ", ""),
        "category": (idx or {}).get("category", ""),
        "court": (idx or {}).get("court", ""),
        "jurisdiction": "Maine",
        "pages": int((schema or {}).get("n_pages")
                     or (inv or {}).get("page_count") or 0),
        "field_count": int((schema or {}).get("n_fields")
                           or len((inv or {}).get("fields") or [])),
        "fillable": bool((inv or {}).get("is_fillable", True)),
        "revision_date": (inv or {}).get("revision_date", "") or None,
        "source_url": (inv or {}).get("download_url", "") or None,
        "governing_law": _governing_law_list((idx or {}).get("governing_law", "")),
        "field_categories": (schema or {}).get("by_category", {}),
        "risk_tiers": (schema or {}).get("by_risk_tier", {}),
        "has_fill_recipe": has_recipe,
        "automation_status": "recipe" if has_recipe else "schema-only",
    }
    return meta


def build_readme(form_id, meta, idx, has_pdf=True):
    purpose = (idx or {}).get("purpose", "") or \
        f"Maine court form {form_id}."
    laws = meta["governing_law"]
    lines = [
        f"# {form_id} — {meta['title']}",
        "",
        f"- **Category:** {meta['category'] or 'Uncategorized'}",
        f"- **Court:** {meta['court'] or 'Maine Judicial Branch'}",
        f"- **Pages:** {meta['pages']}  |  **Fillable fields:** "
        f"{meta['field_count']}",
        f"- **Revision:** {meta['revision_date'] or 'unknown'}",
        f"- **Automation:** {meta['automation_status']}",
        "",
        "## Purpose",
        "",
        purpose,
        "",
    ]
    if laws:
        lines += ["## Governing law", ""]
        lines += [f"- {l}" for l in laws]
        lines += [""]
    if meta["source_url"]:
        lines += ["## Source", "",
                  f"Official blank form: [{form_id}]({meta['source_url']}) "
                  "(Maine Judicial Branch forms portal).", ""]
    lines += [
        "## Files in this folder",
        "",
        f"| File | What it is |",
        "|---|---|",
    ]
    if has_pdf:
        lines.append(f"| `{form_id}.pdf` | Blank fillable source form |")
    else:
        lines.append(
            f"| _(no `{form_id}.pdf`)_ | Blank form not bundled — fetch from "
            "the source URL above |")
    lines += [
        "| `schema.json` | AcroForm field schema (id, type, rect, page, "
        "label) |",
        "| `fields.csv` | Human-friendly field listing |",
        "| `form.yaml` | Machine-readable metadata |",
        "| `SKILL.md` | Agent fill guide (facts needed, field mapping) |",
        "| `mapping.json` | Canonical fact-key → field_id map |",
        "| `examples/` | Sample fact pattern(s) |",
        "",
        "## Disclaimer",
        "",
        "This is an automation artifact, not legal advice. The blank form is "
        "an official Maine Judicial Branch document; the surrounding metadata "
        "and fill guidance are community-maintained and may lag form "
        "revisions. Always verify against the official source before filing.",
        "",
    ]
    return "\n".join(lines)


def build_skill(form_id, meta, fields, prior_skill, has_recipe):
    if prior_skill and prior_skill.strip():
        header = (f"<!-- Reused from prior skills stash; verify against "
                  f"schema.json. -->\n")
        recipe_note = ""
        if has_recipe:
            recipe_note = (
                "\n> **Note:** a dedicated fill recipe exists for this form "
                f"in `engine/recipes/`. The recipe is the authoritative "
                "field mapping; this doc is the human-readable companion.\n")
        return header + prior_skill.rstrip() + "\n" + recipe_note

    lines = [
        f"# {form_id} — {meta['title']}",
        "",
        f"**Category:** {meta['category']}  |  **Court:** {meta['court']}",
        f"**Fields:** {meta['field_count']}  |  **Automation:** "
        f"{meta['automation_status']}",
        "",
        "## What an agent needs to fill this form",
        "",
        "Provide a matter/case object with party names, court (county + "
        "location + docket), and any form-specific facts. The field table "
        "below lists every fillable widget; map your case data to each "
        "`field_id`.",
        "",
    ]
    if has_recipe:
        lines += [
            "> A dedicated fill recipe exists in `engine/recipes/` and "
            "encodes the authoritative, audit-verified mapping (including "
            "non-obvious widget quirks). Prefer it over the raw table below.",
            "",
        ]
    lines += ["## Field map", "",
              "| field_id | type | page | printed label |",
              "|---|---|---|---|"]
    for f in fields[:200]:
        lab = (f.get("label") or "").replace("|", "\\|")[:60]
        lines.append(f"| `{f.get('field_id', f.get('name', ''))}` | "
                     f"{f.get('type', '')} | {f.get('page', '')} | {lab} |")
    if len(fields) > 200:
        lines.append(f"| ... | | | ({len(fields) - 200} more in "
                     "schema.json) |")
    lines.append("")
    return "\n".join(lines)


def build_mapping(form_id, fields, has_recipe):
    """Best-effort canonical-key -> field_id draft. Recipe forms get a
    pointer to the authoritative recipe instead of a guessed map."""
    if has_recipe:
        return {
            "form_id": form_id,
            "status": "recipe",
            "note": "Authoritative mapping lives in engine/recipes/"
                    f"infer_*{form_id.lower().replace('-', '')}*.py "
                    "(RECIPE3 dispatch). This file is a placeholder; do not "
                    "hand-edit — regenerate from the recipe.",
            "map": {},
        }
    # Heuristic label -> canonical key for common court-form fields.
    HINTS = [
        (r"docket", "matter.docket_number"),
        (r"county", "matter.court_county"),
        (r"location|division", "matter.court_location"),
        # Attorney fields (before the party-role hints so "attorney for the
        # petitioner" routes to the attorney, not the petitioner). The bar hint
        # precedes the name hint so "attorney bar number" -> bar_number. The
        # name hint requires "name" to co-occur so it never clobbers an
        # attorney address/phone widget.
        (r"\bbar\b|bar_?no\b", "parties.attorney.bar_number"),
        (r"(?:attorney|counsel).*name|name.*(?:attorney|counsel)",
         "parties.attorney.full_name"),
        (r"\bdob\b|date[ _]of[ _]birth", "party.date_of_birth"),
        (r"plaintiff|petitioner", "parties.plaintiff.full_name"),
        (r"defendant|respondent", "parties.defendant.full_name"),
        (r"signature|signed", "party.signature"),
        (r"\bdate\b", "today()"),
        (r"address", "party.address"),
        (r"phone|telephone", "party.phone"),
        (r"email", "party.email"),
        (r"\bzip\b", "party.zip"),
        (r"\bcity\b|\btown\b", "party.city"),
        (r"\bstate\b", "party.state"),
    ]
    m = {}
    for f in fields:
        fid = f.get("field_id", f.get("name", ""))
        lab = (f.get("label") or fid or "").lower()
        for pat, key in HINTS:
            if re.search(pat, lab):
                m[fid] = key
                break
    return {
        "form_id": form_id,
        "status": "draft-heuristic",
        "note": "Auto-derived from field labels. Unmapped fields need "
                "human/agent review. Not audit-verified.",
        "map": m,
    }


def scaffold_one(form_id, ctx):
    engine, pdf_stash, skills_stash = (ctx["engine"], ctx["pdf_stash"],
                                       ctx["skills_stash"])
    out = OSS_ROOT / "forms" / form_id
    schema = _load_json(engine / "repo" / "forms" / form_id / "schema.json")
    if schema is None:
        return f"SKIP {form_id}: no schema.json"
    fields = schema.get("fields", [])
    idx = ctx["idx"].get(form_id)
    inv = ctx["inv"].get(form_id)
    has_recipe = form_id in ctx["recipe_forms"]

    out.mkdir(parents=True, exist_ok=True)
    (out / "examples").mkdir(exist_ok=True)

    # 1. schema.json + fields.csv (copy verbatim from engine repo)
    shutil.copyfile(engine / "repo" / "forms" / form_id / "schema.json",
                    out / "schema.json")
    fcsv = engine / "repo" / "forms" / form_id / "fields.csv"
    if fcsv.exists():
        shutil.copyfile(fcsv, out / "fields.csv")

    # 2. PDF
    pdf_src = pdf_stash / f"{form_id}.pdf"
    pdf_status = "no-pdf"
    if pdf_src.exists():
        shutil.copyfile(pdf_src, out / f"{form_id}.pdf")
        pdf_status = "pdf"

    # 3. metadata + docs
    meta = build_form_yaml(form_id, idx, inv, schema, has_recipe)
    (out / "form.yaml").write_text(
        yaml.safe_dump(meta, sort_keys=False, allow_unicode=True))
    (out / "README.md").write_text(
        build_readme(form_id, meta, idx, has_pdf=(pdf_status == "pdf")))

    prior = ""
    ps = skills_stash / form_id / "SKILL.md" if skills_stash else None
    if ps and ps.exists():
        prior = ps.read_text()
    (out / "SKILL.md").write_text(
        build_skill(form_id, meta, fields, prior, has_recipe))

    (out / "mapping.json").write_text(
        json.dumps(build_mapping(form_id, fields, has_recipe), indent=2))

    # 4. example fact pattern (reuse a family probe case if present)
    ex = ctx["example_case"]
    if ex and not (out / "examples" / "sample_case.json").exists():
        (out / "examples" / "sample_case.json").write_text(
            json.dumps(ex, indent=2))

    return f"OK   {form_id}: {pdf_status}, {len(fields)} fields, " + \
           ("recipe" if has_recipe else "schema-only")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--engine-repo", required=True, type=pathlib.Path)
    ap.add_argument("--pdf-stash", required=True, type=pathlib.Path)
    ap.add_argument("--skills-stash", type=pathlib.Path, default=None)
    ap.add_argument("--forms", default="",
                    help="comma list to limit; omit for all schemas")
    args = ap.parse_args()

    engine = args.engine_repo
    idx = _index_by(_load_json(engine / "catalog" / "forms_index.json"),
                    "form")
    inv = _index_by(_load_json(engine / "catalog" / "inventory.json"),
                    "form_number")
    recipe_forms = _recipe_forms(engine)

    # Canonical fact object seeded into every form's examples/. It uses the
    # {matter, parties, party, facts} shape documented in
    # docs/integrations/README.md so its keys resolve against mapping.json.
    example_case = _load_json(OSS_ROOT / "tools" / "canonical_sample_case.json")

    ctx = {"engine": engine, "pdf_stash": args.pdf_stash,
           "skills_stash": args.skills_stash, "idx": idx, "inv": inv,
           "recipe_forms": recipe_forms, "example_case": example_case}

    if args.forms:
        forms = [f.strip() for f in args.forms.split(",") if f.strip()]
    else:
        forms = sorted(p.name for p in (engine / "repo" / "forms").iterdir()
                       if (p / "schema.json").exists()
                       and not p.name.startswith(EXCLUDE_PREFIXES))

    n_ok = n_pdf = 0
    for fid in forms:
        msg = scaffold_one(fid, ctx)
        print(" ", msg)
        if msg.startswith("OK"):
            n_ok += 1
            if ": pdf," in msg:
                n_pdf += 1
    print(f"\nscaffolded {n_ok}/{len(forms)} forms ({n_pdf} with PDF, "
          f"{len(recipe_forms)} recipe forms total)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
