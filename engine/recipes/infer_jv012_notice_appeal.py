"""JV-012 (Notice of Appeal — juvenile case to Law Court) recipe-3.

Schema layout (sorted by rect y-coord):
  y= 78  undefined         (text 136w right)   LOCATION (schema swap)
  y= 93  location_town     (text 158w right)   DOCKET (schema swap)
  y=123  v                 (text 212w)         juvenile name
  y=192  mru_crim_p_36f... (text 372w)         "Notice is given that ___"
  y=208  juvenile_in_proceeding_or          (chk) who's appealing (juv)
  y=223  parentguardianlegal_custodian_or    (chk) who's appealing (P/G)
  y=237  assistant_district_attorney_or...   (chk) who's appealing (ADA)
  y=273  bindover_determination              (chk) appeal type
  y=273  adjudication_after_an_order_of_...  (chk) appeal type
  y=288  disposition                         (chk) appeal type
  y=288  disposition_modification            (chk) appeal type
  y=302  detention_order                     (chk) appeal type
  y=302  refusal_to_modify_detention_order   (chk) appeal type
  y=315  entered_on_mmddyyyy  (text 457w)    order-entered date
  y=317  other               (chk) appeal type "other"
  y=336  undefined_2         (text 123w)     "other" type description
  y=377  is_presently_in_custody_of_the_department_of_corre (chk)
  y=390  "1"                 (text 486w)     custody address line 1
  y=406  is_presently_in_custody_of_the_department_of_healt (chk)
  y=419  "2"                 (text 486w)     custody address line 2
  y=434  "1_2"               (text 486w)     additional address line
  y=450  is_not_presently_in_custody_..._address_is (chk)
  y=463  "2_2"               (text 486w)     juvenile's own address line
  y=478  undefined_3         (text 486w)     juvenile's own address line 2
  y=501  transcript_order_filed              (chk)
  y=516  appellant_has_filed_a_motion_with_the_district_cou  (chk)
  y=552  date_mmddyyyy + undefined_4 (signature date + signature text)
  y=567  appellant / appellants_attorney    (chk — who is signing)
  y=588  printed_name_and_bar_number_if_applicable (text)
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

    # Juvenile = the minor; default to defendant or first child party
    juvenile = (parties.get("juvenile") or parties.get("minor")
                 or parties.get("defendant") or parties.get("child_1")
                 or {})
    appellant_attorney = (parties.get("attorney")
                           or parties.get("appellants_attorney") or {})
    if not appellant_attorney and facts.get("attorney_name"):
        # Attorney block ONLY from explicit facts. Never invent counsel
        # (was a stock "Sarah J. Whitfield, Esq. / Maine Bar No. 12345"):
        # a fabricated attorney-of-record is a material misstatement.
        appellant_attorney = {
            "full_name": facts.get("attorney_name", ""),
            "bar_number": facts.get("attorney_bar", ""),
        }

    # Caption: docket/location (schema-swap, same as PA-010). Force over
    # build_kv_map pollution: `undefined`=Location (Town) line,
    # `location_town`=Docket No. line.
    if "undefined" in out and court.get("location"):
        out["undefined"] = court.get("location", "")
        changes.append(("undefined", court.get("location",""), "loc"))
    if "location_town" in out and case.get("docket_no"):
        out["location_town"] = case.get("docket_no", "")
        changes.append(("location_town", case.get("docket_no",""), "docket"))
    if _set(out, "v", juvenile.get("full_name", "")):
        changes.append(("v", juvenile.get("full_name",""), "juvenile"))

    # ── y=192 "Notice is given that ___" narrative ──
    # Composed ONLY when the appellant role is explicitly provided (the
    # role was previously defaulted to "juvenile", silently asserting who
    # is appealing). With no role and no explicit text, leave it blank.
    juv_name = juvenile.get("full_name") or "the juvenile"
    role = facts.get("jv012_appellant_role", "")
    notice_text = facts.get("jv012_notice_text", "")
    if not notice_text and role:
        notice_text = (f"{juv_name}, who is the {role} in the "
                        "above-captioned proceeding,")
    if notice_text and _set(out, "mru_crim_p_36f_15_mrs_3402", notice_text):
        changes.append(("mru_crim_p_36f_15_mrs_3402", notice_text,
                        "notice-narrative"))

    # ── y=208-237: who is appealing (3-way radio, single check) ──
    # Check ONLY when the role is explicitly provided and recognized.
    role_map = {
        "juvenile": "juvenile_in_the_proceeding_or",
        "parent": "parentguardianlegal_custodian_of_the_juvenile_or",
        "guardian": "parentguardianlegal_custodian_of_the_juvenile_or",
        "ada": "assistant_district_attorney_or_assistant_attorney_",
        "state": "assistant_district_attorney_or_assistant_attorney_",
    }
    role_fid = role_map.get(role.lower()) if role else None
    if role_fid and _set(out, role_fid, "X"):
        changes.append((role_fid, "X", "appellant-role"))

    # ── y=273-317: appeal-type checkbox (single check) ──
    appeal_type_map = {
        "bindover": "bindover_determination",
        "bind-over": "bindover_determination",
        "adjudication": "adjudication_after_an_order_of_disposition",
        "disposition": "disposition",
        "modification": "disposition_modification",
        "detention": "detention_order",
        "refusal": "refusal_to_modify_detention_order",
    }
    # Check ONLY when explicitly provided (was defaulted to "bindover"):
    # the appeal type defines the appeal and must never be guessed.
    appeal_type = facts.get("jv012_appeal_type", "").lower()
    appeal_fid = appeal_type_map.get(appeal_type) if appeal_type else None
    if appeal_fid and _set(out, appeal_fid, "X"):
        changes.append((appeal_fid, "X", "appeal-type"))

    # ── y=315 entered_on date ──
    entered_date = facts.get("jv012_entered_date",
                                case.get("event_date") or "")
    entered_us = _iso_to_us(entered_date)
    if _set(out, "entered_on_mmddyyyy", entered_us):
        changes.append(("entered_on_mmddyyyy", entered_us, "entered-date"))

    # ── y=377-478: custody disposition (3-way radio + address narrative) ──
    # Check ONLY when explicitly provided (was defaulted to "corrections",
    # asserting the juvenile is in DOC custody).
    custody_status = facts.get("jv012_custody_status", "").lower()
    custody_fid_map = {
        "corrections": "is_presently_in_custody_of_the_department_of_corre",
        "doc": "is_presently_in_custody_of_the_department_of_corre",
        "health": "is_presently_in_custody_of_the_department_of_healt",
        "hhs": "is_presently_in_custody_of_the_department_of_healt",
        "not": "is_not_presently_in_custody_the_juveniles_address_",
        "home": "is_not_presently_in_custody_the_juveniles_address_",
    }
    custody_fid = (custody_fid_map.get(custody_status)
                    if custody_status else None)
    if custody_fid and _set(out, custody_fid, "X"):
        changes.append((custody_fid, "X", "custody-status"))

    # Custody address — for DOC/HHS, the address is the agency's;
    # for "not in custody", the juvenile's home address.
    juv_addr = juvenile.get("address", "")
    if custody_status in ("not", "home") and juv_addr:
        # "2_2" / "undefined_3" hold juvenile's own address (lines 1+2)
        juv_city_state = ""
        if juvenile.get("city") or juvenile.get("state"):
            juv_city_state = (f"{juvenile.get('city','')}, "
                              f"{juvenile.get('state','ME')} "
                              f"{juvenile.get('zip','')}").strip(", ")
        if _set(out, "2_2", juv_addr):
            changes.append(("2_2", juv_addr, "juv-addr-1"))
        if _set(out, "undefined_3", juv_city_state):
            changes.append(("undefined_3", juv_city_state, "juv-addr-2"))
    elif custody_status:
        # DOC/HHS custody — agency address ONLY from explicit facts (was a
        # stock Long Creek address, wrong for HHS and unverified for DOC).
        agency_addr_1 = facts.get("jv012_agency_addr_1", "")
        agency_addr_2 = facts.get("jv012_agency_addr_2", "")
        if agency_addr_1 and _set(out, "1", agency_addr_1):
            changes.append(("1", agency_addr_1, "agency-addr-1"))
        if agency_addr_2 and _set(out, "2", agency_addr_2):
            changes.append(("2", agency_addr_2, "agency-addr-2"))

    # ── y=501 transcript order filed — check ONLY on an explicit boolean
    # fact (was auto-checked, asserting a transcript order that may not
    # have been filed). ──
    if (facts.get("jv012_transcript_ordered") is True
            and _set(out, "transcript_order_filed", "X")):
        changes.append(("transcript_order_filed", "X", "transcript"))

    # ── y=552 signature date + undefined_4 (printed signature) ──
    sig_date = case.get("filing_date") or case.get("event_date") or ""
    sig_date_us = _iso_to_us(sig_date)
    if _set(out, "date_mmddyyyy", sig_date_us):
        changes.append(("date_mmddyyyy", sig_date_us, "sig-date"))
    signer_name = appellant_attorney.get("full_name", "")
    if _set(out, "undefined_4", signer_name):
        changes.append(("undefined_4", signer_name, "sig-text"))

    # ── y=567 appellant / appellants_attorney radio ──
    is_attorney = bool(appellant_attorney.get("full_name"))
    sign_fid = "appellants_attorney" if is_attorney else "appellant"
    if _set(out, sign_fid, "X"):
        changes.append((sign_fid, "X", "sign-role"))

    # ── y=588 printed name + bar number ──
    printed = appellant_attorney.get("full_name", "")
    bar = appellant_attorney.get("bar_number", "")
    printed_combined = f"{printed} — {bar}" if (printed and bar) else printed
    if _set(out, "printed_name_and_bar_number_if_applicable", printed_combined):
        changes.append(("printed_name_and_bar_number_if_applicable",
                        printed_combined, "printed-name-bar"))

    return out, changes


if __name__ == "__main__":
    print("Use via fill_and_audit.py RECIPE3 dispatch")
    sys.exit(0)
