#!/usr/bin/env python3
"""Derive each form's required/used canonical fact keys -> mapping.json "facts".

``canonical_keys_used`` (the values of ``mapping.json: map``) tells an intake
agent which facts a form *can* consume, but nothing said which facts it
actually *needs*, so intake couldn't ask targeted questions. This tool derives
a per-form declaration deterministically and writes it into ``mapping.json``:

    "facts": {
      "required": [...],   # conservative: blank here = facially incomplete
      "used":     [...],   # every canonical key the fill path can consume
      "note":     "...",   # how to read the lists (recipe forms)
      "derived_by": "tools/derive_required_facts.py"
    }

Derivation rules (deterministic; when unsure a key is "used", not "required"):

* mapping-tier forms (``verified`` / ``opus-adjudicated`` / drafts):
  - used = sorted set of map values, minus computed keys (``today()``).
  - required = the primary party-name keys (``parties.plaintiff.full_name``,
    ``parties.defendant.full_name``, ``party.full_name``) that feed at least
    one **text** widget. A court filing whose caption party names are blank
    is facially incomplete; every other key is left optional — child rows
    and attorney blocks are legitimately blank (no children / self-
    represented), and addresses, dates, checkboxes, and narrative facts are
    routinely filed blank or N/A.
* recipe-tier forms: the registered recipe modules (RECIPE3) are statically
  scanned for the fact keys they read (``facts.get("...")`` /
  ``facts["..."]``) plus the engine basics they consult (court / docket /
  filing-date / party roles), all translated to canonical keys. Recipes are
  presence-gated by design (they fill only from explicit facts), so
  required = [] and everything is "used".
* no-mappable-fields forms: empty lists + explanatory note.

Re-runnable: regenerates the block in place. Run after any mapping or
recipe change:

    python3 tools/derive_required_facts.py            # all forms
    python3 tools/derive_required_facts.py --forms PA-001 --dry-run
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

OSS_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(OSS_ROOT))

from engine.fill_and_audit import RECIPE3  # noqa: E402

DERIVED_BY = "tools/derive_required_facts.py"

# Engine-shape accesses inside recipes -> canonical fact keys.
_ENGINE_TO_CANONICAL = {
    ("court", "county"): "matter.court_county",
    ("court", "location"): "matter.court_location",
    ("court", "name"): "matter.court_type",
    ("case", "docket_no"): "matter.docket_number",
    ("case", "case_no"): "matter.docket_number",
    ("case", "filing_date"): "matter.filing_date",
    # the engine derives event_date from matter.filing_date (engine/canonical)
    ("case", "event_date"): "matter.filing_date",
    ("case", "case_type"): "matter.case_type",
}

_RX_FACTS = re.compile(r"\bfacts(?:\.get\(\s*|\[\s*)[\"']([A-Za-z0-9_]+)[\"']")
_RX_PARTIES = re.compile(r"\bparties(?:\.get\(\s*|\[\s*)[\"']([A-Za-z0-9_]+)[\"']")
_RX_COURT = re.compile(r"\bcourt(?:\.get\(\s*|\[\s*)[\"']([A-Za-z0-9_]+)[\"']")
_RX_CASE = re.compile(r"\bcase(?:\.get\(\s*|\[\s*)[\"']([A-Za-z0-9_]+)[\"']")


def _scan_recipe_module(mod: str) -> set[str]:
    """Statically harvest the canonical keys a recipe module can consume."""
    src_path = OSS_ROOT / "engine" / "recipes" / f"{mod}.py"
    if not src_path.exists():
        return set()
    src = src_path.read_text()
    keys: set[str] = set()
    for k in _RX_FACTS.findall(src):
        keys.add(f"facts.{k}")
    for role in _RX_PARTIES.findall(src):
        # role-level: the recipe may read any attr of this party block
        keys.add(f"parties.{role}")
    for k in _RX_COURT.findall(src):
        canon = _ENGINE_TO_CANONICAL.get(("court", k))
        if canon:
            keys.add(canon)
    for k in _RX_CASE.findall(src):
        canon = _ENGINE_TO_CANONICAL.get(("case", k))
        if canon:
            keys.add(canon)
    return keys


def _text_fids(schema: dict) -> set[str]:
    return {f.get("field_id") for f in schema.get("fields", [])
            if (f.get("type") or "").lower() == "text"}


# Only the caption party names are ever marked required. Numbered child
# roles, the attorney block, and the role-neutral other_party are optional
# on real filings (no children / self-represented / role varies).
_REQUIRED_KEYS = ("parties.plaintiff.full_name",
                  "parties.defendant.full_name",
                  "party.full_name")


def derive_facts_block(fdir: pathlib.Path) -> dict:
    mapping = json.loads((fdir / "mapping.json").read_text())
    schema = json.loads((fdir / "schema.json").read_text())
    return facts_block_from_mapping(mapping, schema, form_id=fdir.name)


def facts_block_from_mapping(mapping: dict, schema: dict,
                             form_id: str = "") -> dict:
    """Pure derivation: mapping.json dict + schema dict -> "facts" block."""
    status = mapping.get("status")
    m = mapping.get("map") or {}
    form_id = form_id or mapping.get("form_id", "")

    if status == "no-mappable-fields":
        return {"required": [], "used": [],
                "note": "Informational/court-completed form — nothing for an "
                        "intake agent to collect.",
                "derived_by": DERIVED_BY}

    if status == "recipe":
        mods = {RECIPE3[fid] for fid in RECIPE3 if fid == form_id}
        used: set[str] = set()
        for mod in sorted(mods):
            used |= _scan_recipe_module(mod)
        return {"required": [],
                "used": sorted(used),
                "note": "Recipe-tier form: keys harvested statically from the "
                        "registered engine recipe, which is presence-gated "
                        "(fills only from facts you supply — nothing "
                        "hard-fails, so nothing is marked required). A bare "
                        "parties.<role> entry means the recipe may read any "
                        "attribute of that party. The generic engine field "
                        "map also consumes the standard basics (docket, "
                        "court, party names) where the form has those "
                        "widgets.",
                "derived_by": DERIVED_BY}

    # mapping-tier (verified / opus-adjudicated / any draft)
    used = sorted({v for v in m.values() if v != "today()"})
    text_fids = _text_fids(schema)
    required = sorted({
        key for fid, key in m.items()
        if key in _REQUIRED_KEYS and fid in text_fids
    })
    return {"required": required, "used": used, "derived_by": DERIVED_BY}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--forms", default="", help="comma list; omit for all")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if args.forms:
        dirs = [OSS_ROOT / "forms" / f.strip()
                for f in args.forms.split(",") if f.strip()]
    else:
        dirs = sorted(p for p in (OSS_ROOT / "forms").iterdir() if p.is_dir())
    n = changed = 0
    for fdir in dirs:
        mp_path = fdir / "mapping.json"
        if not mp_path.exists():
            continue
        block = derive_facts_block(fdir)
        mapping = json.loads(mp_path.read_text())
        n += 1
        if mapping.get("facts") == block:
            continue
        changed += 1
        if args.dry_run:
            print(f"  {fdir.name}: required={block['required']}")
            continue
        mapping["facts"] = block
        mp_path.write_text(json.dumps(mapping, indent=2) + "\n")
    print(f"{n} forms, {changed} updated" + (" (dry-run)" if args.dry_run else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
