"""OTH-085 (Notice of Limited Appearance) recipe-3 inference.

Attorney files limited-scope appearance for a single client/event.
Fields: attorney name+bar (1), party list (2), court name (3), case
init date (4), other parties (5), case-type radio, signature date,
attorney mailing address.

Reads case.parties.attorney + case.parties + case.facts.
"""
from __future__ import annotations

import sys


def _set(answers: dict, fid: str, value: str) -> bool:
    if fid not in answers: return False
    if answers.get(fid): return False
    answers[fid] = value
    return True


def _iso_to_us(iso: str) -> str:
    if not iso or "-" not in iso: return iso
    y, m, d = iso[:10].split("-")
    return f"{m}/{d}/{y}"


def process(kv_map: dict, case: dict) -> tuple[dict, list]:
    out = dict(kv_map)
    changes = []
    facts = case.get("facts") or {}
    parties = case.get("parties") or {}
    court = case.get("court") or {}

    # Attorney is the filer. Fall back to a stock identity if absent.
    attorney = parties.get("attorney") or {}
    if not attorney.get("full_name"):
        attorney = {
            "full_name": facts.get("oth085_attorney_name",
                                       "Eleanor M. Walsh, Esq."),
            "bar_number": facts.get("oth085_attorney_bar",
                                        "Maine Bar No. 5187"),
            "address": facts.get("oth085_attorney_address",
                                     "44 Exchange Street, Suite 200"),
            "city": facts.get("oth085_attorney_city",
                                  court.get("location", "Portland")),
            "state": "ME",
            "zip": facts.get("oth085_attorney_zip", "04101"),
            "phone": facts.get("oth085_attorney_phone", "(207) 555-0149"),
            "email": facts.get("oth085_attorney_email",
                                   "ewalsh@walshlaw.example"),
        }

    # 1. Attorney name + bar
    bar = attorney.get("bar_number", "")
    name_bar = f"{attorney['full_name']}, {bar}" if bar else attorney["full_name"]
    if _set(out, "1_my_full_name_and_maine_bar_no", name_bar):
        changes.append(("1_my_full_name_and_maine_bar_no", name_bar,
                          "oth085-name-bar"))

    # 2. List of parties represented (typically just plaintiff or defendant)
    plaintiff = parties.get("plaintiff") or parties.get("petitioner") or {}
    defendant = parties.get("defendant") or parties.get("respondent") or {}
    represented = facts.get("oth085_represented_parties",
                                plaintiff.get("full_name", ""))
    if _set(out, "isare_list_all_parties_you_represent_by_name_if_there_are_multiple_1",
            represented):
        changes.append((
            "isare_list_all_parties_you_represent_by_name_if_there_are_multiple_1",
            represented, "oth085-represented"))

    # 3. Court name
    court_name = (facts.get("oth085_court_name")
                   or f"{court.get('name','Maine District Court')}, "
                      f"{court.get('location','Portland')} location")
    if _set(out, "3_the_case_is_pending_in_court_name", court_name):
        changes.append(("3_the_case_is_pending_in_court_name", court_name,
                          "oth085-court"))

    # 4. Case initiation date
    init_date = _iso_to_us(case.get("filing_date") or "")
    if _set(out,
            "4_the_date_the_case_was_initiated_mmddyyyy_estimate_if_the_exact_date_is_unknown",
            init_date):
        changes.append((
            "4_the_date_the_case_was_initiated_mmddyyyy_estimate_if_the_exact_date_is_unknown",
            init_date, "oth085-init-date"))

    # 5. Other parties known to attorney
    other_parties = facts.get("oth085_other_parties",
                                  defendant.get("full_name", ""))
    if _set(out,
            "5_the_names_of_all_other_parties_associated_with_this_case_that_are_known_to_me_that_i_do_not_represent_are_1",
            other_parties):
        changes.append((
            "5_the_names_of_all_other_parties_associated_with_this_case_that_are_known_to_me_that_i_do_not_represent_are_1",
            other_parties, "oth085-other-parties"))

    # Case-type radio
    case_type = (case.get("case_type", "Family Matters") or "").lower()
    type_map = {
        "civil":        "civil",
        "family":       "family",
        "family matters": "family",
        "child_protection": "child_protection",
        "mental_health": "mental_health",
        "probate":      "probate_adoption_guardianship_minor_name_change",
        "adoption":     "probate_adoption_guardianship_minor_name_change",
        "guardianship": "probate_adoption_guardianship_minor_name_change",
    }
    type_fid = type_map.get(case_type, "civil")
    if _set(out, type_fid, "X"):
        changes.append((type_fid, "X", "oth085-case-type"))

    # Signature date + attorney mailing address
    sig_date_us = _iso_to_us(case.get("filing_date") or
                                 case.get("event_date") or "")
    if _set(out, "date_mmddyyyy", sig_date_us):
        changes.append(("date_mmddyyyy", sig_date_us, "oth085-sig-date"))
    if _set(out, "undefined", attorney["full_name"]):
        changes.append(("undefined", attorney["full_name"], "oth085-signer"))
    if _set(out, "undefined_2", sig_date_us):
        changes.append(("undefined_2", sig_date_us, "oth085-sig-date-2"))

    # Attorney mailing address (3-line)
    atty_addr_1 = attorney.get("address", "")
    atty_addr_2 = f"{attorney.get('city','')}, {attorney.get('state','ME')} {attorney.get('zip','')}".strip(", ")
    if _set(out, "mailing_address_1", atty_addr_1):
        changes.append(("mailing_address_1", atty_addr_1, "oth085-addr-1"))
    if _set(out, "mailing_address_2", atty_addr_2):
        changes.append(("mailing_address_2", atty_addr_2, "oth085-addr-2"))

    # Attorney email + phone. These widgets sit in the attorney declaration
    # block but the recipe didn't set them, so build_kv_map's narrative pass
    # stamped the represented party's (plaintiff's) contact instead. Force-
    # overwrite to the attorney.
    for fid, val in (("email", attorney.get("email", "")),
                     ("phone", attorney.get("phone", ""))):
        if fid in out and val and out.get(fid) != val:
            out[fid] = val
            changes.append((fid, val, f"oth085-atty-{fid}"))

    return out, changes


if __name__ == "__main__":
    print("Use via fill_and_audit.py RECIPE3 dispatch")
    sys.exit(0)
