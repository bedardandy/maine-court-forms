#!/usr/bin/env python3
"""Derive a per-field *fill-value guidance* artifact for each form.

The repo already knows a field's *role* (schema.json category/subcategory),
*where its value comes from* (mapping.json), and *how the engine fills it*
(engine/build_kv_map.py token heuristics). What it has never written down is,
per field, **what kind of text a human/automation should put there** — a person
name vs a county vs a dollar amount vs a date in MM/DD/YYYY vs a checkbox — plus
whether the field is required and whether it is part of a one-of choice group.

This tool derives that, deterministically and offline (no PDF needed), into
``forms/<ID>/fill_guidance.json``. It is intentionally consistent with the fill
engine: it reuses ``engine.build_kv_map`` (``_PARTY_ATTR_MAP``,
``_date_format_hint``) and the canonical mapping keys so the *declared* type
matches the value the engine actually writes.

    facts.required (mapping.json)      -> required
    constraints.json mutually_exclusive -> conditional choice group
    constraints.json requires           -> conditional "only if"
    mapping.json map fact-key           -> value_type (most reliable signal)
    schema subcategory / field_id token -> value_type (fallback)

Result per field: {value_type, format?, required, conditional?, guidance}.
Warnings-only downstream: nothing here blocks a fill; preflight uses it to flag
a supplied value that doesn't look like its field's type.

CLI:
    python3 tools/derive_field_guidance.py --all
    python3 tools/derive_field_guidance.py --form CV-007 [--print]
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

OSS_ROOT = pathlib.Path(__file__).resolve().parent.parent
FORMS = OSS_ROOT / "forms"

# Allow `python3 tools/derive_field_guidance.py` (script dir, not repo root,
# is on sys.path when run directly) to import the engine helpers we reuse.
if str(OSS_ROOT) not in sys.path:
    sys.path.insert(0, str(OSS_ROOT))

from engine.build_kv_map import _PARTY_ATTR_MAP, _date_format_hint  # noqa: E402

# ---- value-type vocabulary -------------------------------------------------
# Keep this list closed; the eval validates field types against it.
VALUE_TYPES = {
    "person_name", "organization_name", "address", "city", "state", "zip",
    "phone", "email", "date", "time", "currency", "percent", "county",
    "court_location", "docket", "case_number", "bar_number", "checkbox",
    "signature", "free_text",
}

# Short human/agent instruction per value_type. Deliberately conservative about
# currency/$ and time because the offline deriver can't read the printed form
# (see --print note); it tells the user to verify rather than asserting.
GUIDANCE = {
    "person_name": "A person's name (the engine collapses to initials only if "
                   "it overflows the box).",
    "organization_name": "An organization / business / agency name.",
    "address": "A street address; include the street line. City/State/ZIP may "
               "belong in their own boxes — check the printed labels.",
    "city": "A city or town name only (no state or ZIP).",
    "state": "A US state — 'Maine' or the 2-letter 'ME'; match the box width.",
    "zip": "A 5-digit ZIP code (or ZIP+4).",
    "phone": "A telephone number.",
    "email": "An email address.",
    "date": "A calendar date.",
    "time": "A wall-clock time (e.g. 10:00). If the form pre-prints AM/PM, "
            "circle/strike the correct one by hand — the engine does not.",
    "currency": "A dollar amount as digits (e.g. 1,250.00). Many forms pre-"
                "print '$' next to the blank; if so, do NOT type a second '$' "
                "(the engine strips a leading '$'). Verify against the form.",
    "percent": "A percentage value. If the form pre-prints '%', enter digits "
               "only.",
    "county": "A Maine county name without the word 'County' (e.g. "
              "Cumberland).",
    "court_location": "The court division / town where the case is filed.",
    "docket": "The docket number (e.g. CV-2024-0099).",
    "case_number": "The case number.",
    "bar_number": "An attorney's Maine bar registration number.",
    "checkbox": "A checkbox: filled with 'X' only when the fact is explicitly "
                "true; never auto-checked.",
    "signature": "A signature blank — left empty for wet-ink signing.",
    "free_text": "Free-form narrative text specific to the situation.",
}

# canonical mapping suffix -> value_type (most reliable signal). Mirrors
# engine.build_kv_map._PARTY_ATTR_MAP semantics for party attrs.
_ATTR_TO_TYPE = {
    "full_name": "person_name", "first_name": "person_name",
    "middle_name": "person_name", "last_name": "person_name",
    "address": "address", "mailing_address": "address",
    "city": "city", "state": "state", "zip": "zip",
    "phone": "phone", "email": "email",
    "date_of_birth": "date", "dob": "date",
    "bar_number": "bar_number",
}
_MATTER_TO_TYPE = {
    "court_county": "county", "court_location": "court_location",
    "court_type": "free_text", "case_type": "free_text",
    "docket_number": "docket", "case_number": "case_number",
    "case_id": "case_number", "filing_date": "date", "event_date": "date",
}

# field_id / fact token fallbacks (engine-style token matching).
_CURRENCY_TOK = re.compile(
    r"amount|_pay\b|^pay\b|\bfee\b|income|wage|salary|\btax\b|cost|balance"
    r"|owed|arrears|deposit\b|dollar|gross|net_pay|disposable|total.*\$|\$"
    r"|expense|premium|withholding|retirement|deduction",
    re.I)
_PERCENT_TOK = re.compile(r"percent|_pct\b|share_of|%", re.I)
_TIME_TOK = re.compile(r"(?:^|_)time(?:_|$)|_am$|_pm$|oclock|o_clock", re.I)
_ORG_TOK = re.compile(
    r"business|company|employer|organization|agency|firm|\bllc\b|\binc\b"
    r"|corporation|landlord_business|creditor_name", re.I)
_NAME_TOK = re.compile(r"(?:^|_)name(?:_|$)|_name$", re.I)
_ADDR_TOK = re.compile(r"address|street", re.I)
_STATE_TOK = re.compile(r"(?:^|_)state(?:_|$)", re.I)
_CITY_TOK = re.compile(r"(?:^|_)(?:city|town)(?:_|$)", re.I)
_PHONE_TOK = re.compile(r"phone|tel(?:_no)?\b|telephone|fax", re.I)
_EMAIL_TOK = re.compile(r"email|e_mail", re.I)
_ZIP_TOK = re.compile(r"(?:^|_)zip(?:_|$)|postal", re.I)
_DATE_TOK = re.compile(r"(?:^|_)date(?:_|$)|mmddyyyy|_dated|dob", re.I)
_COUNTY_TOK = re.compile(r"county", re.I)
_LOCATION_TOK = re.compile(r"location|court_town|(?:^|_)town(?:_|$)", re.I)
_DOCKET_TOK = re.compile(r"docket", re.I)
_CASE_TOK = re.compile(r"case_no|case_number", re.I)


def _attr_type_from_field_id(field_id: str) -> str | None:
    """If a (possibly unmapped) field_id ends in a known party-attr token,
    return its value_type. Uses the engine's own attr vocabulary."""
    fid = field_id.lower()
    for tok, attr in _PARTY_ATTR_MAP.items():
        if re.search(rf"(?:^|_){re.escape(tok)}(?:_\d+)?$", fid):
            return _ATTR_TO_TYPE.get(attr)
    return None


def _type_from_mapping_key(key: str) -> str | None:
    if key == "today()" or key.endswith("()") and "date" in key:
        return "date"
    if key.startswith("matter."):
        return _MATTER_TO_TYPE.get(key.split(".", 1)[1])
    if key.startswith(("parties.", "party.")):
        attr = key.rsplit(".", 1)[-1]
        return _ATTR_TO_TYPE.get(attr)
    if key.startswith("facts."):
        return _type_from_facts_leaf(key.split(".", 1)[1])
    return None


def _type_from_facts_leaf(leaf: str) -> str | None:
    """Type a ``facts.<leaf>`` key from the leaf name. The canonical key name
    is the author's stated intent, so it's a better signal than the (often
    auto-generated) field_id — and for a mapped field we trust it rather than
    guessing from the widget id."""
    low = leaf.lower()
    # A compound location blob (two+ of city/state/zip/address in one blank,
    # e.g. "city_state_zip", "town_state") is a composite — type it `address`,
    # not its trailing component.
    comps = sum(bool(p.search(low)) for p in
                (_CITY_TOK, _STATE_TOK, _ZIP_TOK, _ADDR_TOK))
    if comps >= 2:
        return "address"
    if _EMAIL_TOK.search(low):
        return "email"
    if _PHONE_TOK.search(low):
        return "phone"
    # Trailing intent: a `..._name` field is a name even if an earlier token
    # looks like money ("medical_expense_child_1_name"); name/org also win over
    # a stray `state` token ("state_agency_name").
    if _ORG_TOK.search(low):
        return "organization_name"
    if _NAME_TOK.search(low):
        return "person_name"
    if _PERCENT_TOK.search(low):  # percent before currency (share_of_% etc.)
        return "percent"
    if _CURRENCY_TOK.search(low):
        return "currency"
    # a duration ("time_spent", "..._duration_minutes") is free text, not a
    # wall-clock time.
    if re.search(r"duration|_spent|elapsed|_length", low):
        return None
    if _DATE_TOK.search(low):  # a "date_and_time" blob is primarily a date
        return "date"
    if _TIME_TOK.search(low):
        return "time"
    if _ZIP_TOK.search(low):
        return "zip"
    if _STATE_TOK.search(low) and "out_of_state" not in low:
        return "state"
    if _CITY_TOK.search(low):
        return "city"
    if _ADDR_TOK.search(low):
        return "address"
    return None


def _type_from_subcategory(sub: str) -> str | None:
    return {
        "county": "county", "docket_no": "docket", "date": "date",
        "signature": "signature", "plaintiff": "person_name",
        "defendant": "person_name", "attorney": "person_name",
        "minor": "person_name",
    }.get(sub)


def _type_from_field_id_tokens(field_id: str) -> str:
    fid = field_id.lower()
    # order matters: most specific first
    if _EMAIL_TOK.search(fid):
        return "email"
    if _PHONE_TOK.search(fid):
        return "phone"
    if _ZIP_TOK.search(fid):
        return "zip"
    if _COUNTY_TOK.search(fid):
        return "county"
    if _DOCKET_TOK.search(fid):
        return "docket"
    if _CASE_TOK.search(fid):
        return "case_number"
    if _LOCATION_TOK.search(fid):
        return "court_location"
    if _TIME_TOK.search(fid):
        return "time"
    if _PERCENT_TOK.search(fid):
        return "percent"
    if _CURRENCY_TOK.search(fid):
        return "currency"
    if _DATE_TOK.search(fid):
        return "date"
    attr = _attr_type_from_field_id(field_id)
    if attr:
        return attr
    return "free_text"


def classify(field: dict, mapped_key: str | None) -> tuple[str, str | None]:
    """Return (value_type, format) for one schema field.

    Precedence: widget kind > signature > mapping fact-key > subcategory >
    field_id tokens. The mapping key is the most reliable because it is the
    value the engine actually resolves into the widget.
    """
    fid = field["field_id"]
    if field.get("type") == "checkbox":
        return "checkbox", None
    cat = field.get("category")
    sub = field.get("subcategory") or ""

    # An explicit mapping is ground truth — the engine resolves a value into
    # this widget, so trust the canonical key (even inside a signature block: a
    # date-of-signing mapped to today() is a date; an electronic-signature line
    # mapped to a name is a name). For a MAPPED field we never fall back to
    # field_id tokens — the (often auto-generated) widget id would contaminate
    # the type (e.g. an address widget named "..._date_...").
    if mapped_key:
        vtype = _type_from_mapping_key(mapped_key)
        if vtype is None and (cat == "signature" or sub == "signature"
                              or field.get("data_type") == "signature"):
            return "signature", None
        if vtype is None:
            vtype = "free_text"
    else:
        if cat == "signature" or sub == "signature" \
                or field.get("data_type") == "signature":
            return "signature", None
        vtype = _type_from_subcategory(sub) or _type_from_field_id_tokens(fid)

    fmt = None
    if vtype == "date":
        fmt = _date_format_hint(fid)  # "us_slash" | "iso"
    return vtype, fmt


def _conditional_index(form_dir: pathlib.Path) -> dict:
    """field_id -> conditional descriptor, from constraints.json."""
    cpath = form_dir / "constraints.json"
    if not cpath.exists():
        return {}
    cfg = json.loads(cpath.read_text())
    out: dict[str, dict] = {}
    for grp in cfg.get("mutually_exclusive") or []:
        keys = grp["keys"] if isinstance(grp, dict) else grp
        note = grp.get("note") if isinstance(grp, dict) else None
        for k in keys:
            out[k] = {"rule": "exactly_one_of", "group": list(keys),
                      "note": note}
    for key, grp in (cfg.get("requires") or {}).items():
        needed = grp["keys"] if isinstance(grp, dict) else grp
        for k in needed:
            out[k] = {"rule": "required_if", "trigger": key}
    return out


def guidance_for_form(form_id: str,
                      forms_root: pathlib.Path = FORMS) -> dict:
    fdir = forms_root / form_id
    schema = json.loads((fdir / "schema.json").read_text())
    mapping = json.loads((fdir / "mapping.json").read_text())
    fid_to_key = mapping.get("map") or {}
    required_keys = set(((mapping.get("facts") or {}).get("required")) or [])
    cond_idx = _conditional_index(fdir)

    fields: dict[str, dict] = {}
    for f in schema.get("fields", []):
        fid = f["field_id"]
        mapped_key = fid_to_key.get(fid)
        vtype, fmt = classify(f, mapped_key)
        entry: dict = {"value_type": vtype}
        if fmt:
            entry["format"] = fmt
        entry["required"] = bool(mapped_key and mapped_key in required_keys)
        if fid in cond_idx:
            entry["conditional"] = cond_idx[fid]
        entry["guidance"] = GUIDANCE[vtype]
        fields[fid] = entry

    return {
        "form_id": form_id,
        "generated_by": "tools/derive_field_guidance.py",
        "note": ("Per-field fill-value guidance (value type, required-ness, "
                 "choice-group conditionals). Derived offline from "
                 "schema/mapping/constraints; consistent with the fill engine. "
                 "Not legal advice — verify against the official form before "
                 "filing. Currency/time guidance is conservative because the "
                 "printed '$'/AM-PM are not read here."),
        "value_types": sorted(VALUE_TYPES),
        "fields": fields,
    }


def write_one(form_id: str, forms_root: pathlib.Path = FORMS) -> int:
    g = guidance_for_form(form_id, forms_root)
    out = forms_root / form_id / "fill_guidance.json"
    out.write_text(json.dumps(g, indent=2, ensure_ascii=False) + "\n")
    return len(g["fields"])


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    grp = ap.add_mutually_exclusive_group(required=True)
    grp.add_argument("--all", action="store_true")
    grp.add_argument("--form")
    ap.add_argument("--print", dest="show", action="store_true",
                    help="print the artifact instead of writing it")
    args = ap.parse_args()

    if args.form and args.show:
        print(json.dumps(guidance_for_form(args.form), indent=2,
                         ensure_ascii=False))
        return 0

    forms = (sorted(p.parent.name for p in FORMS.glob("*/schema.json"))
             if args.all else [args.form])
    total = 0
    for fid in forms:
        if not (FORMS / fid / "mapping.json").exists():
            continue
        n = write_one(fid)
        total += 1
        if args.form:
            print(f"{fid}: {n} fields -> "
                  f"{FORMS / fid / 'fill_guidance.json'}")
    if args.all:
        print(f"wrote {total} fill_guidance.json artifacts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
