"""FM-233 (Response to Petition for De Facto Parentage) recipe-3
inference.

Companion form to FM-227 (grandparent visitation response) — same
structural pattern: respondent's denial response with statutory
citation + 2-paragraph fact narrative + denial checkboxes.

Reads case.parties.plaintiff (de facto parent claimant) +
case.parties.defendant (legal parent responding) + case.facts.fm233_*.
"""
from __future__ import annotations

import sys


def _set(answers: dict, fid: str, value: str) -> bool:
    if fid not in answers: return False
    if answers.get(fid): return False
    answers[fid] = value
    return True


def process(kv_map: dict, case: dict) -> tuple[dict, list]:
    out = dict(kv_map)
    changes = []
    facts = case.get("facts") or {}
    parties = case.get("parties") or {}
    court = case.get("court") or {}

    plaintiff = (parties.get("plaintiff") or parties.get("petitioner")
                  or {})
    defendant = (parties.get("defendant") or parties.get("respondent")
                  or {})

    # Caption
    if _set(out, "plaintiff", plaintiff.get("full_name", "")):
        changes.append(("plaintiff", plaintiff.get("full_name",""), "pl"))
    if _set(out, "v", "v."):
        changes.append(("v", "v.", "v"))
    # Offset caption (force over build_kv_map pollution): the `Text1` widget is
    # physically the Location (Town) line and `location_town` is physically the
    # Docket No. line.
    def _fc(fid, val, src):
        if fid in out and val and out.get(fid) != val:
            out[fid] = val
            changes.append((fid, val, src))
    _fc("text1", court.get("location", ""), "loc")
    _fc("location_town", case.get("docket_no", ""), "docket")

# Defendant's admit/deny paragraphs — these ARE the answer's legal
    # positions. Fill ONLY when explicitly provided (were defaulted to
    # "None" admitted / "1, 2, 3, 4, 5, 6, 7, 8" denied).
    admit = facts.get("admit_paragraphs", "")
    if admit and _set(out, "1_defendant_admits_paragraphs", admit):
        changes.append(("1_defendant_admits_paragraphs", admit, "admit"))
    # Item 2 "denies paragraphs for determination of de facto parentage"
    # is a 241px NARRATIVE widget (not a checkbox). Set to the paragraph
    # numbers being denied.
    deny_paragraphs = facts.get("deny_paragraphs", "")
    # Force-override since an earlier pass set it to "X" (checkbox-style)
    if (deny_paragraphs
            and out.get("for_determination_of_de_facto_parentage")
                in ("", "X", None)):
        out["for_determination_of_de_facto_parentage"] = deny_paragraphs
        changes.append(("for_determination_of_de_facto_parentage",
                          deny_paragraphs, "deny-paragraphs"))

    # Attached affidavit + deny order + attorney fees radios — check ONLY
    # on explicit boolean facts (were auto-checked, asserting an affidavit
    # was attached and requesting relief on the defendant's behalf).
    deny_branch = (
        ("i_have_attached_an_affidavit_describing_the_specific_facts_addressing_whether_the_plaintiff_has_a_de",
         "fm233_affidavit_attached"),
        ("enter_an_order_denying_plaintiffs_complaint_to_be_adjudicated_de_facto_parent",
         "fm233_request_denial"),
        ("award_reasonable_attorney_fees_andor",
         "fm233_request_fees"),
    )
    for fid, key in deny_branch:
        if facts.get(key) is True and _set(out, fid, "X"):
            changes.append((fid, "X", "deny-branch"))

    # "Other" radio + narrative — ONLY when explicitly provided
    other_text = facts.get("fm233_other_relief", "")
    if other_text:
        if _set(out, "other", "X"):
            changes.append(("other", "X", "other"))
        if _set(out, "undefined", other_text):
            changes.append(("undefined", other_text, "other-text"))

    # Fact paragraphs 1 + 2 — ONLY when explicitly provided (the old
    # default invented the defendant's factual contentions).
    facts_list = facts.get("fm233_facts") or []
    if isinstance(facts_list, str):
        facts_list = [facts_list, ""]
    for i, p in enumerate(facts_list[:2], start=1):
        if p and _set(out, str(i), p):
            changes.append((str(i), p, f"para-{i}"))

    # Declaration block — ONLY on an explicit boolean fact; never declare
    # truthfulness on the filer's behalf.
    if facts.get("fm233_declaration") is True:
        if _set(out,
                "i_hereby_declare_that_the_above_statements_are_true_to_the_best_of_my_knowledge_and_belief_i",
                "X"):
            changes.append((
                "i_hereby_declare_that_the_above_statements_are_true_to_the_best_of_my_knowledge_and_belief_i",
                "X", "declare"))
        if _set(out, "information_to_the_court",
                "I have not provided false information to the Court."):
            changes.append(("information_to_the_court",
                            "I have not provided false information to the Court.",
                            "info-court"))

    # Signature date + signer
    sig_date_us = case.get("filing_date") or case.get("event_date", "")
    if "-" in sig_date_us and len(sig_date_us) >= 10:
        y, m, d = sig_date_us[:10].split("-")
        sig_date_us = f"{m}/{d}/{y}"
    if _set(out, "undefined_2", sig_date_us):
        changes.append(("undefined_2", sig_date_us, "sig-date"))
    if _set(out, "text1", defendant.get("full_name", "")):
        changes.append(("text1", defendant.get("full_name",""), "signer"))

    # Page-2 signature/contact block. FM-233 has TWO columns:
    # LEFT = defendant attorney block (`defendant_attorney`, address_1/2/3,
    # telephone, email); RIGHT = defendant pro-se block (`defendant`,
    # address_1_2/2_2, telephone_2, email_2). build_kv_map's narrative
    # pass stamps address_1/2/3 with plaintiff stuff and address_1_2/2_2
    # with defendant's bare street — both must be force-overridden.
    attorney = parties.get("attorney") or {}

    def _force(fid: str, val: str, src: str) -> None:
        if fid in out and out.get(fid, "") != val:
            out[fid] = val
            changes.append((fid, val, src))

    # Right column — always pro-se defendant identity
    _force("defendant", defendant.get("full_name", ""), "p2-defendant")
    def_street = defendant.get("address", "")
    def_city = defendant.get("city", court.get("location", ""))
    def_state = defendant.get("state", "ME")
    def_zip = defendant.get("zip", "")
    def_csz = ", ".join(p for p in (def_city, f"{def_state} {def_zip}".strip())
                          if p)
    _force("address_1_2", def_street, "def-addr-street")
    _force("address_2_2", def_csz, "def-addr-csz")
    _force("telephone_2", defendant.get("phone", ""), "def-phone")
    _force("email_2", defendant.get("email", ""), "def-email")

    # Left column — attorney if present, else clear stale build_kv_map
    # narrative stamps (plaintiff data over-applied via address_N pattern).
    if attorney.get("full_name"):
        atty_street = attorney.get("address", "")
        atty_csz = attorney.get("address_2", "")
        _force("defendant_attorney", attorney["full_name"], "p2-def-atty")
        _force("address_1", atty_street, "atty-addr-street")
        _force("address_2", atty_csz, "atty-addr-csz")
        _force("address_3", "", "atty-addr-3-blank")
        _force("telephone", attorney.get("phone", ""), "atty-phone")
        _force("email", attorney.get("email", ""), "atty-email")
    else:
        for fid in ("defendant_attorney", "address_1", "address_2",
                     "address_3", "telephone", "email"):
            if out.get(fid):
                out[fid] = ""
                changes.append((fid, "", "atty-col-clear"))

    return out, changes


if __name__ == "__main__":
    print("Use via fill_and_audit.py RECIPE3 dispatch")
    sys.exit(0)
