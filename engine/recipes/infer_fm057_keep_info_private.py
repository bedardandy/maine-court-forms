"""FM-057 (Motion to Keep Information Private/Confidential) recipe-3.

The schema's "named" widgets at x=35 are 12-px confidentiality CHECKBOXES;
the actual address/phone TEXT lives in widgets named `information_confidential`,
`undefined`, `telephone_number`, `undefined_2..6` — discovered by rect.

Layout (y-coord ascending):
  y=173:  movant radio    [plaintiff | defendant | other_party_makes_request]
  y=204:  □ Physical address  →  information_confidential (wide)
  y=218:  □ Mailing address   →  undefined (wide)
  y=231:  □ Email address     →  telephone_number (wide, schema name lies)
  y=245:  □ Cell  →  undefined_2     □ Home  →  undefined_3
  y=258:  □ Work  →  undefined_4
  y=271:  □ Other →  undefined_5 (type) + undefined_6 (value)
  y=300:  movant signing oath radio  [plaintiff_2 | defendant_2 | other_oath]
  y=345-438:  reasons 1..8 narrative
  y=466:  perjury swear radio
  y=516:  date_mmddyyyy + undefined_7 (signature text)
  y=531:  who's signing  [plaintiff_3 | defendant_3 | other_party]

Reads case.parties + case.facts.fm057_* with sensible defaults.
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

    # Movant: who is requesting confidentiality. Default = plaintiff.
    movant_role = facts.get("fm057_movant_role", "plaintiff").lower()
    movant = plaintiff if movant_role == "plaintiff" else defendant

    # Caption
    if _set(out, "plaintiff", plaintiff.get("full_name", "")):
        changes.append(("plaintiff", plaintiff.get("full_name",""), "pl"))
    if _set(out, "defendant", defendant.get("full_name", "")):
        changes.append(("defendant", defendant.get("full_name",""), "df"))
    if _set(out, "docket_no", case.get("docket_no", "")):
        changes.append(("docket_no", case.get("docket_no",""), "docket"))
    if _set(out, "location_town", court.get("location", "")):
        changes.append(("location_town", court.get("location",""), "loc"))

    # y=173 request-by radio — three duplicate fids `plaintiff` /
    # `defendant` are actual schema entries here as 12-px checkboxes;
    # the caption widgets already consumed the named slots, so only
    # the "other_party..." third one is reachable in kv.
    if movant_role == "plaintiff":
        # Already covered by `plaintiff` field above (fan-out via dup_fid).
        pass
    elif movant_role == "defendant":
        # Already covered by `defendant`.
        pass
    else:
        # Third movant box keyed by the very long fid
        if _set(out,
                "other_party_that_party_makes_this_request_to_keep_the_following",
                "X"):
            changes.append((
                "other_party_that_party_makes_this_request_to_keep_the_following",
                "X", "fm057-movant-other"))

    # ── Confidentiality flag checkboxes + paired text widgets ──
    addr = movant.get("address") or movant.get("mailing_address") or ""
    mail_addr = movant.get("mailing_address") or addr
    email = movant.get("email", "")
    phone_cell = movant.get("phone_cell", "")
    phone_home = movant.get("phone_home", "")
    phone_work = movant.get("phone_work", "")

    # Physical address row (check + text)
    if addr:
        if _set(out, "physical_address", "X"):
            changes.append(("physical_address", "X", "fm057-phys-flag"))
        if _set(out, "information_confidential", addr):
            changes.append(("information_confidential", addr, "fm057-phys-text"))

    # Mailing address row
    if mail_addr:
        if _set(out, "mailing_address", "X"):
            changes.append(("mailing_address", "X", "fm057-mail-flag"))
        if _set(out, "undefined", mail_addr):
            changes.append(("undefined", mail_addr, "fm057-mail-text"))

    # Email address row — schema names the wide text widget
    # `telephone_number` here (schema artifact, not a typo).
    if email:
        if _set(out, "email_address", "X"):
            changes.append(("email_address", "X", "fm057-email-flag"))
        if _set(out, "telephone_number", email):
            changes.append(("telephone_number", email, "fm057-email-text"))

    # Cell / Home / Work phone rows
    if phone_cell:
        if _set(out, "cell", "X"):
            changes.append(("cell", "X", "fm057-cell-flag"))
        if _set(out, "undefined_2", phone_cell):
            changes.append(("undefined_2", phone_cell, "fm057-cell"))
    if phone_home:
        if _set(out, "home", "X"):
            changes.append(("home", "X", "fm057-home-flag"))
        if _set(out, "undefined_3", phone_home):
            changes.append(("undefined_3", phone_home, "fm057-home"))
    if phone_work:
        if _set(out, "work", "X"):
            changes.append(("work", "X", "fm057-work-flag"))
        if _set(out, "undefined_4", phone_work):
            changes.append(("undefined_4", phone_work, "fm057-work"))

    # "Other" contact (e.g., fax, alt email) — left blank unless fact present
    other_type = facts.get("fm057_other_type", "")
    other_value = facts.get("fm057_other_value", "")
    if other_type and other_value:
        if _set(out, "other", "X"):
            changes.append(("other", "X", "fm057-other-flag"))
        if _set(out, "undefined_5", other_type):
            changes.append(("undefined_5", other_type, "fm057-other-type"))
        if _set(out, "undefined_6", other_value):
            changes.append(("undefined_6", other_value, "fm057-other-val"))

    # ── y=300 oath-intro radio (which movant is swearing) ──
    if movant_role == "plaintiff":
        if _set(out, "plaintiff_2", "X"):
            changes.append(("plaintiff_2", "X", "fm057-oath-pl"))
    elif movant_role == "defendant":
        if _set(out, "defendant_2", "X"):
            changes.append(("defendant_2", "X", "fm057-oath-df"))
    if _set(out, "other_party_states_as_follows_under_oath",
            "X" if movant_role not in ("plaintiff", "defendant") else ""):
        # Only check this if movant is "other"; otherwise leave blank.
        if movant_role not in ("plaintiff", "defendant"):
            changes.append(("other_party_states_as_follows_under_oath",
                            "X", "fm057-oath-other"))

    # ── y=345-438 reasons narrative (8 lines) ──
    reasons = facts.get("fm057_reasons", [
        "Disclosure of the requested information would create a "
        "substantial risk to the health, safety or liberty of the "
        f"{movant_role} and/or the children of the parties.",
        f"The other party has engaged in a documented pattern of "
        "threatening communications directed at the petitioner.",
        f"The {movant_role} has obtained protective orders against the "
        "other party that remain in effect.",
        f"Public disclosure of the {movant_role}'s contact information "
        "would defeat the purpose of those protective orders by exposing "
        "the protected location.",
    ])
    if isinstance(reasons, str):
        reasons = [reasons]
    for i, line in enumerate(reasons[:8], start=1):
        fid = f"the_following_reasons_{i}"
        if line and _set(out, fid, line):
            changes.append((fid, line, f"fm057-reason-{i}"))

    # ── y=466 perjury swear ── (now handled systemically by
    # _apply_notary_block; left here as a no-op safety net)

    # ── y=516 signature date + signature text ──
    sig_date = case.get("filing_date") or case.get("event_date") or ""
    sig_date_us = _iso_to_us(sig_date)
    if _set(out, "date_mmddyyyy", sig_date_us):
        changes.append(("date_mmddyyyy", sig_date_us, "fm057-sigdate"))
    # The signature TEXT widget undefined_7 is the printed-name signature.
    if _set(out, "undefined_7", movant.get("full_name", "")):
        changes.append(("undefined_7", movant.get("full_name",""),
                        "fm057-sigtext"))

    # ── y=531 who is signing radio ──
    if movant_role == "plaintiff":
        if _set(out, "plaintiff_3", "X"):
            changes.append(("plaintiff_3", "X", "fm057-sign-pl"))
    elif movant_role == "defendant":
        if _set(out, "defendant_3", "X"):
            changes.append(("defendant_3", "X", "fm057-sign-df"))
    else:
        if _set(out, "other_party", "X"):
            changes.append(("other_party", "X", "fm057-sign-other"))

    return out, changes


if __name__ == "__main__":
    print("Use via fill_and_audit.py RECIPE3 dispatch")
    sys.exit(0)
