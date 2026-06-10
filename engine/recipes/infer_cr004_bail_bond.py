"""CR-004 (Bail Bond — Real Estate Lien) form-specific inference.

The form is one paragraph of legal text with each blank as a separate
widget: `i`, `of`, `street`, `county_maine_..._lien_on_the_real_estate_in_the_amount`,
`dollars`, `defendant`, `offense_of_reason`, `division_county`, `city_town`,
plus surety mailing block + notary jurat + Registry of Deeds recordation.

This script reads `case.parties.surety` and `case.facts` to fill all
the fragmented widgets in one pass. Form-gated to CR-004. Idempotent.

Run after K:V baseline (build_kv_map) — overrides only the blanks
that K:V couldn't resolve.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys


def _get(answers: dict, fid: str) -> str:
    a = answers.get(fid)
    if a is None: return ""
    return str(a).strip() if a else ""


def _set(answers: dict, fid: str, value: str) -> bool:
    if fid not in answers: return False
    if _get(answers, fid): return False
    answers[fid] = value
    return True


def process(kv_map: dict, case: dict) -> tuple[dict, list]:
    """Take a kv_map (from build_kv_map) and case dict, return augmented
    kv_map + list of (field_id, value, source) tuples."""
    out = dict(kv_map)
    changes = []
    parties = case.get("parties") or {}
    surety = (parties.get("surety") or parties.get("petitioner")
              or parties.get("plaintiff") or {})
    defendant = parties.get("defendant") or {}
    facts = case.get("facts") or {}
    court = case.get("court") or {}

    # CR-004 surety must own real estate to grant a lien. Build the
    # surety ONLY from explicit surety_* facts — never synthesize one
    # (was a stock "Margaret A. Thorne" with address; a fabricated surety
    # on a bail-lien bond is a material misstatement). When no surety is
    # known, the surety fields stay blank/unresolved.
    if not surety.get("full_name") and facts.get("surety_name"):
        surety = {
            "full_name": facts.get("surety_name", ""),
            "address": facts.get("surety_address", ""),
            "city": facts.get("surety_city", ""),
            "county": facts.get("surety_county", ""),
            "state": "ME",
            "zip": facts.get("surety_zip", ""),
        }

    # Surety identity widgets. NB: schema field_ids truncate raw
    # PDF widget names at ~55 chars — match exact truncations.
    surety_name = surety.get("full_name", "")
    if surety_name:
        for fid in ("i", "suretys_name_typed_or_printed",
                     "personally_appeared_the_above_named_surety_and_acknowledged_this"):
            if _set(out, fid, surety_name):
                changes.append((fid, surety_name, "surety-name"))

    # "of <town>" widget — surety city of residence
    surety_city = surety.get("city", "")
    if surety_city:
        for fid in ("of", "city_town", "of_2"):
            if _set(out, fid, surety_city):
                changes.append((fid, surety_city, "surety-city"))

    # Real estate town (where the lien attaches)
    real_estate_town = (facts.get("real_estate_town")
                        or surety.get("city", ""))
    if real_estate_town and _set(out, "interest_in_real_estate_in_the_town_of",
            real_estate_town):
        changes.append(("interest_in_real_estate_in_the_town_of",
                        real_estate_town, "real-estate-town"))

    # Real estate type / interest (text2 is the interest-type widget) —
    # ONLY when explicitly provided (was defaulted to "fee simple
    # ownership", asserting the surety's title).
    interest_type = facts.get("real_estate_interest", "")
    if interest_type and _set(out, "text2", interest_type):
        changes.append(("text2", interest_type, "interest-type"))

    # Street address
    real_estate_street = (facts.get("real_estate_street")
                          or surety.get("address", ""))
    if real_estate_street:
        for fid in ("street", "suretys_mailing_address"):
            if _set(out, fid, real_estate_street):
                changes.append((fid, real_estate_street, "real-estate-street"))

    # County of surety / county_2 / "County, Maine" — schema truncates
    # the long field_id at 55 chars: `..._lien_o`. Real data only (was
    # defaulted to "Cumberland", fabricating the lien county).
    county = court.get("county") or surety.get("county", "")
    if county:
        for fid in ("county", "county_2", "county_of",
                     "county_maine_and_i_grant_to_the_state_of_maine_a_lien_o",
                     "county_maine_and_i_grant_to_the_state_of_maine_a_lien_on_the_real_estate_in_the_amount",
                     "divisioncounty_in_citytown"):
            if _set(out, fid, county):
                changes.append((fid, county, "county"))

    # Bond amount — CR-004 uses `in_the_amount_of`, CR-003 uses
    # `in_the_amountvalue_of` (squashed amount/value variant for the
    # cash/real/property bail certificate).
    # Bond amount ONLY when explicitly provided (was a $5,000 default —
    # the bail amount is set by the court, never guessed).
    amount = facts.get("bond_amount") or facts.get("penal_sum") or ""
    if amount:
        for fid in ("dollars", "in_the_amount_of", "in_the_amountvalue_of"):
            if _set(out, fid, amount):
                changes.append((fid, amount, "bond-amount"))

    # Defendant + offense — schema truncates field_ids
    if defendant.get("full_name"):
        for fid in ("defendant", "given_for_the_release_of_defendant"):
            if _set(out, fid, defendant["full_name"]):
                changes.append((fid, defendant["full_name"], "defendant"))
    # Offense ONLY when explicitly provided (was defaulted to "operating
    # under the influence" — never invent the charge).
    offense = facts.get("offense") or ""
    if offense:
        for fid in ("who_is_was_being_held_in_custody_for_the_offense_of_reason",
                     "who_iswas_being_held_in_custody_for_the_offense_ofreason",
                     "offense_of_reason"):
            if _set(out, fid, offense):
                changes.append((fid, offense, "offense"))

    # Returnable-to-court narrative — compose only from real court data
    # (the location was previously defaulted to "Portland").
    return_court = facts.get("returnable_court", "")
    if not return_court and court.get("location"):
        return_court = (f"{court.get('name', 'Maine Unified Criminal Court')}, "
                         f"{court['location']}")
    if return_court:
        for fid in ("which_bail_is_returnable_to_the_unified_criminal_court_",
                     "which_bail_is_returnable_to_the_unified_criminal_court_of"):
            if _set(out, fid, return_court):
                changes.append((fid, return_court, "return-court"))

    # `undefined` widget at y=354 — left half of court-location line.
    # Holds the city/town within the division/county.
    if _set(out, "undefined", court.get("location", "")):
        changes.append(("undefined", court.get("location",""),
                        "undefined-loc"))

    # Date — bond date
    bond_date = case.get("event_date") or case.get("filing_date") or ""
    if bond_date:
        # Convert ISO to mm/dd/yyyy
        if "-" in bond_date and len(bond_date) >= 10:
            y, m, d = bond_date[:10].split("-")
            bond_date_us = f"{m}/{d}/{y}"
        else:
            bond_date_us = bond_date
        for fid in ("date_mmddyyyy", "date", "mmddyyyy",
                     "a_true_copy_of_the_bail_lien_recorded_on_mmddyyyy"):
            if _set(out, fid, bond_date_us):
                changes.append((fid, bond_date_us, "date"))

    # Registry of Deeds recordation — vol/page ONLY when explicitly
    # provided (were "1234"/"567" stock numbers; the recordation
    # reference identifies a real registry entry).
    vol = facts.get("registry_vol", "")
    page = facts.get("registry_page", "")
    if vol and _set(out, "at_vol", vol):
        changes.append(("at_vol", vol, "registry-vol"))
    if page and _set(out, "page", page):
        changes.append(("page", page, "registry-page"))
    if county and _set(out, "in_the_county_registry_of_deeds", county):
        changes.append(("in_the_county_registry_of_deeds", county,
                          "county-registry"))

    return out, changes


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--kv-json", type=pathlib.Path, required=True)
    ap.add_argument("--case-json", type=pathlib.Path, required=True)
    ap.add_argument("--out", type=pathlib.Path, required=True)
    args = ap.parse_args()

    kv_data = json.loads(args.kv_json.read_text())
    case = json.loads(args.case_json.read_text())
    kv_map = kv_data.get("kv") or kv_data
    new_kv, changes = process(kv_map, case)
    args.out.write_text(json.dumps({"kv": new_kv, "changes": changes},
                                     indent=2))
    print(f"infer_cr004_bail_bond: {len(changes)} field(s) populated")
    for fid, val, src in changes:
        print(f"  {fid:55s} = {val!r} ({src})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
