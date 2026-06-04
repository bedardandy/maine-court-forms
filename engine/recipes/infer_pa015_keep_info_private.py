"""PA-015 (PFA Motion to Keep Information Private) recipe-3.

Sibling of FM-057 (same confidentiality-flag-plus-wide-text pattern)
but with PFA-specific caption layout and different generic widget
names. Mapped by rect y-coord:

Caption (y < 200):
  y= 49  plaintiff (211w)            plaintiff name
  y= 62  individually_and_on_behalf_of (chk) + location_town
  y= 75  "1" (plaintiff addr 1)       + docket_no
  y= 89  "2" (plaintiff addr 2)
  y=115  "1_2" (defendant name)
  y=128  "2_2" (defendant addr 1)
  y=167  defendant (caption second line)
  y=193  undefined (defendant addr 2)

Movant identity radio (y=327, two checkboxes):
  plaintiff (chk)
  defendant_in_this_case_and_i_request_that_the_court_kee (chk)

Confidentiality flags + wide text widgets (y=343-408):
  y=343  "1_3"          (443w)  physical address text
  y=344  physical_address (chk)
  y=355  "2_3"          (446w)  mailing address text
  y=357  mailing_address (chk)
  y=368  telephone_number (454w) email address text (schema lies)
  y=370  email_address  (chk)
  y=381  undefined_2 / undefined_3  cell / home phone numbers
  y=383  cell / home    (chk)
  y=394  undefined_4    (175w)  work phone
  y=396  work           (chk)
  y=407  undefined_5 / undefined_6   other type + value
  y=408  other          (chk)

Reasons (y=455-493):
  information_for_the_following_reasons_1..4 (wide narrative lines)

Signature (y=567-580):
  date_mmddyyyy / undefined_7 (sig text)
  plaintiff_2 / defendant (who-signs radio)
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

    plaintiff = (parties.get("plaintiff") or parties.get("petitioner") or {})
    defendant = (parties.get("defendant") or parties.get("respondent") or {})

    # Movant defaults to plaintiff (PFA "protected person").
    movant_role = facts.get("pa015_movant_role", "plaintiff").lower()
    movant = plaintiff if movant_role == "plaintiff" else defendant

    # ── Caption ──
    if _set(out, "plaintiff", plaintiff.get("full_name", "")):
        changes.append(("plaintiff", plaintiff.get("full_name",""), "pl"))
    if _set(out, "defendant", defendant.get("full_name", "")):
        changes.append(("defendant", defendant.get("full_name",""), "df"))
    if _set(out, "docket_no", case.get("docket_no", "")):
        changes.append(("docket_no", case.get("docket_no",""), "docket"))
    if _set(out, "location_town", court.get("location", "")):
        changes.append(("location_town", court.get("location",""), "loc"))

    # Plaintiff address lines ("1", "2")
    pl_addr = plaintiff.get("address", "")
    pl_city_state_zip = ""
    if plaintiff.get("city") or plaintiff.get("state"):
        pl_city_state_zip = (
            f"{plaintiff.get('city','')}, "
            f"{plaintiff.get('state','ME')} "
            f"{plaintiff.get('zip','')}").strip(", ")
    if _set(out, "1", pl_addr):
        changes.append(("1", pl_addr, "pl-addr-1"))
    if _set(out, "2", pl_city_state_zip):
        changes.append(("2", pl_city_state_zip, "pl-addr-2"))

    # Defendant address lines ("1_2", "2_2", "undefined")
    df_addr = defendant.get("address", "")
    df_city_state_zip = ""
    if defendant.get("city") or defendant.get("state"):
        df_city_state_zip = (
            f"{defendant.get('city','')}, "
            f"{defendant.get('state','ME')} "
            f"{defendant.get('zip','')}").strip(", ")
    if _set(out, "1_2", defendant.get("full_name", "")):
        changes.append(("1_2", defendant.get("full_name",""), "df-name"))
    if _set(out, "2_2", df_addr):
        changes.append(("2_2", df_addr, "df-addr-1"))
    if _set(out, "undefined", df_city_state_zip):
        changes.append(("undefined", df_city_state_zip, "df-addr-2"))

    # ── Movant radio (y=327) ──
    if movant_role == "plaintiff":
        # Already filled by caption (plaintiff text); the 11-px
        # checkbox at y=327 needs the X.
        # NOTE: same field_id `plaintiff` as the caption — schema
        # collision; dup-fid fan-out routes to both.
        pass  # leave for the caption to drive
    else:
        if _set(out,
                "defendant_in_this_case_and_i_request_that_the_court_kee",
                "X"):
            changes.append((
                "defendant_in_this_case_and_i_request_that_the_court_kee",
                "X", "movant-df"))

    # ── Confidentiality flag checkboxes + paired text widgets ──
    addr = movant.get("address") or movant.get("mailing_address") or ""
    mail_addr = movant.get("mailing_address") or addr
    email = movant.get("email", "")
    phone_cell = movant.get("phone_cell", "")
    phone_home = movant.get("phone_home", "")
    phone_work = movant.get("phone_work", "")

    if addr:
        if _set(out, "physical_address", "X"):
            changes.append(("physical_address", "X", "phys-flag"))
        if _set(out, "1_3", addr):
            changes.append(("1_3", addr, "phys-text"))
    if mail_addr:
        if _set(out, "mailing_address", "X"):
            changes.append(("mailing_address", "X", "mail-flag"))
        if _set(out, "2_3", mail_addr):
            changes.append(("2_3", mail_addr, "mail-text"))
    if email:
        if _set(out, "email_address", "X"):
            changes.append(("email_address", "X", "email-flag"))
        # Wide text widget at y=368 named `telephone_number` actually
        # holds the email address (schema-name drift, same as FM-057).
        if _set(out, "telephone_number", email):
            changes.append(("telephone_number", email, "email-text"))

    # Phone rows
    if phone_cell:
        if _set(out, "cell", "X"):
            changes.append(("cell", "X", "cell-flag"))
        if _set(out, "undefined_2", phone_cell):
            changes.append(("undefined_2", phone_cell, "cell"))
    if phone_home:
        if _set(out, "home", "X"):
            changes.append(("home", "X", "home-flag"))
        if _set(out, "undefined_3", phone_home):
            changes.append(("undefined_3", phone_home, "home"))
    if phone_work:
        if _set(out, "work", "X"):
            changes.append(("work", "X", "work-flag"))
        if _set(out, "undefined_4", phone_work):
            changes.append(("undefined_4", phone_work, "work"))

    # "Other" contact — left blank unless fact present
    other_type = facts.get("pa015_other_type", "")
    other_value = facts.get("pa015_other_value", "")
    if other_type and other_value:
        if _set(out, "other", "X"):
            changes.append(("other", "X", "other-flag"))
        if _set(out, "undefined_5", other_type):
            changes.append(("undefined_5", other_type, "other-type"))
        if _set(out, "undefined_6", other_value):
            changes.append(("undefined_6", other_value, "other-val"))

    # ── y=455-493 reasons narrative (4 lines) ──
    reasons = facts.get("pa015_reasons", [
        "Disclosure of the requested information would create a "
        f"substantial risk to the health, safety, or liberty of the "
        f"{movant_role} and/or the children of the parties.",
        "The other party has engaged in a documented pattern of "
        "threatening behavior and prior abusive conduct directed "
        "at the petitioner.",
        f"The {movant_role} has obtained an active Protection from "
        "Abuse Order and disclosure of the protected address "
        "would defeat the purpose of that Order.",
        "Maintaining confidentiality is necessary to preserve "
        "the safety of the household and to comply with the "
        "existing protective order.",
    ])
    if isinstance(reasons, str):
        reasons = [reasons]
    for i, line in enumerate(reasons[:4], start=1):
        fid = f"information_for_the_following_reasons_{i}"
        if line and _set(out, fid, line):
            changes.append((fid, line, f"reason-{i}"))

    # ── y=567 signature block ──
    sig_date = case.get("filing_date") or case.get("event_date") or ""
    sig_date_us = _iso_to_us(sig_date)
    if _set(out, "date_mmddyyyy", sig_date_us):
        changes.append(("date_mmddyyyy", sig_date_us, "sig-date"))
    if _set(out, "undefined_7", movant.get("full_name", "")):
        changes.append(("undefined_7", movant.get("full_name",""),
                        "sig-text"))

    # ── y=580 who-signs radio ──
    if movant_role == "plaintiff":
        if _set(out, "plaintiff_2", "X"):
            changes.append(("plaintiff_2", "X", "sign-pl"))

    return out, changes


if __name__ == "__main__":
    print("Use via fill_and_audit.py RECIPE3 dispatch")
    sys.exit(0)
