"""FM-227 (Response to Petition for Grandparent / Great-Grandparent
Visitation) recipe-3 inference.

Distinct fact pattern from the standard admit/deny family — the
respondent (typically the parent) is opposing a grandparent's
visitation petition. Defaults select the "deny petition" branch.

Reads case.parties.petitioner (the grandparent) + case.parties.respondent
(the parent), plus case.facts.fm227_* overrides.
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

    petitioner = (parties.get("petitioner") or parties.get("plaintiff")
                   or {})
    respondent = (parties.get("respondent") or parties.get("defendant")
                   or {})
    attorney = parties.get("attorney") or {}

    # Caption
    if _set(out, "petitioners", petitioner.get("full_name", "")):
        changes.append(("petitioners", petitioner.get("full_name",""),
                        "petitioners"))
    if _set(out, "respondent", respondent.get("full_name", "")):
        changes.append(("respondent", respondent.get("full_name",""),
                        "respondent"))
    # Offset caption (force over build_kv_map pollution): `undefined_2` is
    # physically the Location (Town) line and `location_town` is physically the
    # Docket No. line. (`undefined`->docket previously bled the docket number
    # into the petitioner caption, so it is dropped.)
    def _fc(fid, val, src):
        if fid in out and val and out.get(fid) != val:
            out[fid] = val
            changes.append((fid, val, src))
    _fc("undefined_2", court.get("location", ""), "loc")
    _fc("location_town", case.get("docket_no", ""), "docket")
    if _set(out, "v_1", "v."):
        changes.append(("v_1", "v.", "v1"))
    if _set(out, "v_2", "v."):
        changes.append(("v_2", "v.", "v2"))

    # Statutory citation (19-A M.R.S. § 1801-1805 — grandparent visitation)
    if _set(out, "19a_mrs_18011805", "19-A M.R.S. §§ 1801-1805"):
        changes.append(("19a_mrs_18011805",
                        "19-A M.R.S. §§ 1801-1805", "statute"))

    # Affidavit-attached + deny-petition checkboxes — check ONLY on
    # explicit boolean facts (were auto-checked, asserting an affidavit
    # was attached and requesting denial on the respondent's behalf).
    deny_branch = (
        ("i_have_attached_an_affidavit_with_the_specific_facts_addressing_whether_the_petitioners_should_be",
         "fm227_affidavit_attached"),
        ("enter_an_order_denying_petitioners_petition_for_grandparent_or_greatgrandparent_visitation",
         "fm227_request_denial"),
    )
    for fid, key in deny_branch:
        if facts.get(key) is True and _set(out, fid, "X"):
            changes.append((fid, "X", "deny-branch"))

    # Petition-type radio — check ONLY when explicitly provided (was
    # auto-checked "grandparent visitation").
    if (facts.get("fm227_petition_type")
            and _set(out,
                "petition_for_grandparent_or_greatgrandparent_visitation",
                "X")):
        changes.append((
            "petition_for_grandparent_or_greatgrandparent_visitation",
            "X", "petition-type"))

    # Numbered fact paragraphs 1-4 (respondent's facts supporting denial)
    # — ONLY when explicitly provided (the old default invented the
    # respondent's factual contentions). Each widget is 496 px wide;
    # keep each ~80 chars to fit one line.
    fact_paragraphs = facts.get("fm227_facts") or []
    if isinstance(fact_paragraphs, str):
        fact_paragraphs = [fact_paragraphs, "", "", ""]
    for i, p in enumerate(fact_paragraphs[:4], start=1):
        if p and _set(out, str(i), p):
            changes.append((str(i), p, f"para-{i}"))

    # Affirmation block — check ONLY on an explicit boolean fact; never
    # auto-swear an oath on the respondent's behalf.
    if (facts.get("perjury_acknowledged") is True
            and _set(out,
            "i_swear_under_penalty_of_perjury_that_the_above_statements_are_true_and_correct_i_understand_that_these",
            "X")):
        changes.append((
            "i_swear_under_penalty_of_perjury_that_the_above_statements_are_true_and_correct_i_understand_that_these",
            "X", "swear"))

    # Signature date
    sig_date = (case.get("filing_date") or case.get("event_date") or "")
    if _set(out, "undefined_3", _iso_to_us(sig_date)):
        changes.append(("undefined_3", _iso_to_us(sig_date), "date"))
    if _set(out, "undefined_4", respondent.get("full_name","")):
        changes.append(("undefined_4", respondent.get("full_name",""),
                        "signer"))

    # Respondent attorney + contact block — TWO-column signature page.
    # LEFT = attorney; RIGHT = pro-se respondent. build_kv_map's
    # narrative pass mis-stamps both blocks with party data via the
    # `_2`→respondent heuristic; force-override is required.
    def _force(fid: str, val: str, src: str) -> None:
        if fid in out and out.get(fid, "") != val:
            out[fid] = val
            changes.append((fid, val, src))

    resp_street = respondent.get("address", "")
    resp_city = respondent.get("city", court.get("location", ""))
    resp_state = respondent.get("state", "ME")
    resp_zip = respondent.get("zip", "")
    resp_csz = ", ".join(p for p in (resp_city, f"{resp_state} {resp_zip}".strip())
                          if p)
    # Right column — pro-se respondent
    _force("address_1_2", resp_street, "resp-addr-street")
    _force("address_2_2", resp_csz, "resp-addr-csz")
    _force("telephone_2", respondent.get("phone", ""), "resp-phone")
    _force("email_2", respondent.get("email", ""), "resp-email")

    # Left column — attorney if present, else clear stale data
    if attorney.get("full_name"):
        _force("respondent_attorney", attorney["full_name"], "atty")
        _force("address_1", attorney.get("address", ""), "atty-addr-street")
        _force("address_2", attorney.get("address_2", ""), "atty-addr-csz")
        _force("address_3", "", "atty-addr-3-blank")
        _force("telephone", attorney.get("phone", ""), "atty-phone")
        _force("email", attorney.get("email", ""), "atty-email")
    else:
        for fid in ("respondent_attorney", "address_1", "address_2",
                     "address_3", "telephone", "email"):
            if out.get(fid):
                out[fid] = ""
                changes.append((fid, "", "atty-col-clear"))

    # Notary jurat — "Personally appeared the above named respondent"
    if _set(out, "personally_appeared_the_above_named_respondent",
            respondent.get("full_name","")):
        changes.append(("personally_appeared_the_above_named_respondent",
                        respondent.get("full_name",""), "notary"))

    return out, changes


if __name__ == "__main__":
    print("Use via fill_and_audit.py RECIPE3 dispatch")
    sys.exit(0)
