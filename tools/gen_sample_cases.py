#!/usr/bin/env python3
"""Generate a per-form examples/sample_case.json from the form's own keys.

Historically 332/342 forms shipped the same generic Doe-v-Roe family-matters
sample, so MCP get_form returned a "sample" that didn't exercise the form's
own canonical keys (criminal/eviction/probate forms showed marriage facts).

This tool derives each form's sample from its declared key set
(``mapping.json: facts.used`` — see tools/derive_required_facts.py):

* mapping-tier forms get a minimal case carrying exactly the matter /
  parties / party keys the mapping resolves, plus a synthesized fictional
  value for every ``facts.*`` key (checkbox-only keys get "yes").
* recipe-tier forms keep the full generic base (the generic engine field
  map consumes the standard basics) and add synthesized values for the
  fact keys their recipe reads. The enriched sample is accepted only if
  the recipe (a) still runs and (b) fills a superset of what it filled
  from the base sample without changing any previously-filled value —
  recipes parse typed fact formats ("$1,234.00", "Name (Role)") that a
  generic placeholder string would crash or skew. Otherwise the form
  keeps the generic sample (marked "generic": true).
* forms with nothing to exercise (``no-mappable-fields`` / empty key set)
  keep the generic sample with ``"generic": true`` so get_form can say so.

All values are clearly fictional placeholders, same convention as the
generic sample (Doe/Roe/Sample names, example.com, 207-555-01xx phones,
"00000" numbers) — never realistic-looking real-person data, and never a
claimed legal fact. Every generated sample is preflight-validated
(tools/preflight.py) before writing.

Hand-built samples are preserved: the tool only rewrites a sample that is
(semantically) the shared generic copy. Re-runnable / idempotent.

    python3 tools/gen_sample_cases.py            # all forms
    python3 tools/gen_sample_cases.py --forms PA-001 --dry-run
"""
from __future__ import annotations

import argparse
import copy
import json
import pathlib
import sys

OSS_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(OSS_ROOT))

from tools.preflight import preflight_case  # noqa: E402

BASE_PATH = OSS_ROOT / "tools" / "canonical_sample_case.json"

SUMMARY = ("Sample fact pattern for testing form fills. All names, contacts, "
           "dates, and amounts here are fictitious placeholders (Doe/Roe, "
           "example.com, 555 phone range).")

# Roster for roles the generic base doesn't carry.
EXTRA_PARTIES = {
    "other_party": {
        "full_name": "John R. Roe",
        "address": "456 Oak Avenue",
        "city": "Portland", "state": "ME", "zip": "04101",
        "phone": "207-555-0102", "email": "john.roe@example.com",
        "date_of_birth": "1983-06-20",
    },
}
# Numbered children beyond the base's child_1/child_2 (all fictional).
CHILD_NAMES = ["Sam Doe", "Alex Doe", "Riley Doe", "Casey Doe", "Jordan Doe",
               "Quinn Doe", "Avery Doe", "Rowan Doe", "Sage Doe", "Remy Doe",
               "Blake Doe", "Drew Doe"]
CHILD_DOBS = ["2015-04-10", "2018-09-05", "2012-02-14", "2010-07-22",
              "2016-11-03", "2014-05-30", "2019-08-17", "2011-01-25",
              "2013-10-09", "2017-03-12", "2009-12-01", "2020-06-18"]


def _party_for_role(base: dict, role: str) -> dict:
    parties = base.get("parties") or {}
    if role in parties:
        return copy.deepcopy(parties[role])
    if role in EXTRA_PARTIES:
        return copy.deepcopy(EXTRA_PARTIES[role])
    if role.startswith("child_") and role[6:].isdigit():
        i = int(role[6:]) - 1
        return {"full_name": CHILD_NAMES[i % len(CHILD_NAMES)],
                "date_of_birth": CHILD_DOBS[i % len(CHILD_DOBS)],
                "address": "123 Main Street", "city": "Portland",
                "state": "ME", "zip": "04101"}
    # Unknown role (shouldn't ship — preflight would flag it).
    return {"full_name": "Riley T. Doe"}


def synth_fact_value(key: str, checkbox_only: bool = False) -> str:
    """Deterministic clearly-fictional placeholder for a facts.* key."""
    k = key.lower()
    if checkbox_only:
        return "yes"
    if k == "summary":
        return SUMMARY
    if "spent" in k or "duration" in k:
        return "2 hours"
    if "date" in k or k.endswith("_dob"):
        return "2024-03-15"
    if "time" in k:
        return "9:00 AM"
    if "phone" in k or "telephone" in k:
        return "207-555-0199"
    if "email" in k:
        return "sample@example.com"
    if "address" in k:
        return "789 Pine Street, Portland, ME 04101"
    if "county" in k:
        return "Cumberland"
    if "city" in k or "town" in k:
        return "Portland"
    if k.endswith("state"):
        return "ME"
    if "zip" in k:
        return "04101"
    if ("amount" in k or "fee" in k or "total" in k or "wage" in k
            or "income" in k or "balance" in k or "principal" in k
            or "interest" in k or "payment" in k or "value" in k
            or k.endswith("_sum")):
        return "100.00"
    if "age" in k and "page" not in k:
        return "10"
    if ("employer" in k or "company" in k or "business" in k
            or "organization" in k) and "name" in k:
        return "Acme Example Company"
    if "docket" in k or "number" in k or k.endswith("_no"):
        return "2024-00000"
    if "name" in k:
        return "Riley T. Doe"
    if ("description" in k or "explanation" in k or "details" in k
            or "reason" in k or "grounds" in k or "statement" in k
            or "summary" in k or "other" in k or "issue" in k):
        return "Fictional sample text for testing this form's fill."
    return "Sample (fictional)."


def _checkbox_only_keys(fdir: pathlib.Path, mapping: dict) -> set[str]:
    """facts.* keys whose every mapped widget is a checkbox -> fill 'yes'."""
    try:
        schema = json.loads((fdir / "schema.json").read_text())
    except Exception:  # noqa: BLE001
        return set()
    type_by_fid: dict[str, set[str]] = {}
    for f in schema.get("fields", []):
        type_by_fid.setdefault(f.get("field_id"), set()).add(
            (f.get("type") or "").lower())
    key_types: dict[str, set[str]] = {}
    for fid, key in (mapping.get("map") or {}).items():
        key_types.setdefault(key, set()).update(
            type_by_fid.get(fid, {"?"}))
    return {k for k, ts in key_types.items() if ts == {"checkbox"}}


def _recipe_run(form_id: str, case: dict) -> dict:
    """Run a form's registered recipe over a case (PDF-free), as the recipe
    smoke test does: map_form + recipe.process."""
    import importlib

    from engine.build_kv_map import map_form
    from engine.fill_and_audit import RECIPE3
    schema = json.loads(
        (OSS_ROOT / "forms" / form_id / "schema.json").read_text())
    kv, _ = map_form(schema, case)
    mod = importlib.import_module(f"engine.recipes.{RECIPE3[form_id]}")
    out, _changes = mod.process(kv, case)
    return out


def _recipe_accepts(form_id: str, base: dict, enriched: dict) -> bool:
    """True iff the recipe runs on the enriched sample and only ADDS fills
    relative to the base sample (never crashes, never changes a value the
    base already produced)."""
    try:
        base_out = _recipe_run(form_id, base)
        new_out = _recipe_run(form_id, enriched)
    except Exception:  # noqa: BLE001 — synthesized value broke the recipe
        return False
    for k, v in base_out.items():
        if v and new_out.get(k) != v:
            return False
    return True


def build_sample(fdir: pathlib.Path, base: dict) -> tuple[dict, str]:
    """Return (sample_case, kind) — kind in generated-mapping /
    generated-recipe / generic."""
    mapping = json.loads((fdir / "mapping.json").read_text())
    status = mapping.get("status")
    facts_block = mapping.get("facts") or {}
    used = facts_block.get("used") or []
    checkbox_only = _checkbox_only_keys(fdir, mapping)

    if not used:  # no-mappable-fields or nothing derivable
        case = copy.deepcopy(base)
        case["generic"] = True
        return case, "generic"

    if status == "recipe":
        # Recipes run on top of the generic engine field map, which consumes
        # the standard base; enrich it with the recipe's own fact keys.
        case = copy.deepcopy(base)
        for key in used:
            if key.startswith("facts."):
                fk = key.split(".", 1)[1]
                case.setdefault("facts", {}).setdefault(
                    fk, synth_fact_value(fk, fk in checkbox_only))
        case["facts"]["summary"] = SUMMARY
        if not _recipe_accepts(fdir.name, base, case):
            case = copy.deepcopy(base)
            case["generic"] = True
            return case, "generic"
        return case, "generated-recipe"

    # Mapping-tier: carry exactly the keys this form's mapping resolves.
    case: dict = {"matter": {}}
    base_matter = base.get("matter") or {}
    for key in used:
        parts = key.split(".")
        if parts[0] == "matter" and len(parts) == 2:
            case["matter"][parts[1]] = base_matter.get(
                parts[1], synth_fact_value(parts[1]))
        elif parts[0] == "party" and len(parts) == 2:
            case.setdefault("party", {})[parts[1]] = (
                base.get("party") or {}).get(parts[1],
                                             synth_fact_value(parts[1]))
        elif parts[0] == "parties" and len(parts) == 3:
            role, attr = parts[1], parts[2]
            roster = _party_for_role(base, role)
            case.setdefault("parties", {}).setdefault(role, {})[attr] = \
                roster.get(attr, synth_fact_value(attr))
        elif parts[0] == "facts" and len(parts) == 2:
            fk = parts[1]
            case.setdefault("facts", {})[fk] = synth_fact_value(
                fk, key in checkbox_only)
    case.setdefault("facts", {})["summary"] = SUMMARY
    return case, "generated-mapping"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--forms", default="", help="comma list; omit for all")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true",
                    help="also overwrite hand-built (non-generic) samples")
    args = ap.parse_args()
    base = json.loads(BASE_PATH.read_text())
    if args.forms:
        dirs = [OSS_ROOT / "forms" / f.strip()
                for f in args.forms.split(",") if f.strip()]
    else:
        dirs = sorted(p for p in (OSS_ROOT / "forms").iterdir() if p.is_dir())
    counts: dict[str, int] = {}
    failures = []
    for fdir in dirs:
        sp = fdir / "examples" / "sample_case.json"
        if not (fdir / "mapping.json").exists():
            continue
        if sp.exists() and not args.force:
            current = json.loads(sp.read_text())
            cur_nogen = {k: v for k, v in current.items() if k != "generic"}
            if cur_nogen != base:
                counts["kept-hand-built"] = counts.get("kept-hand-built", 0) + 1
                continue
        sample, kind = build_sample(fdir, base)
        pre = preflight_case(sample)
        if not pre["ok"] or pre["warnings"]:
            failures.append((fdir.name, pre["errors"] + pre["warnings"]))
            continue
        counts[kind] = counts.get(kind, 0) + 1
        if args.dry_run:
            continue
        sp.parent.mkdir(exist_ok=True)
        sp.write_text(json.dumps(sample, indent=2) + "\n")
    print(json.dumps(counts))
    if failures:
        for name, issues in failures:
            print(f"PREFLIGHT FAIL {name}: {issues}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
