"""MJBVB family (Bureau of Highway Safety / Violations Bureau) recipe-3
inference.

Covers MJBVB-009 (Motion to Amend Civil Violation) and MJBVB-017
(Request for Fine Extension / Payment Plan).

Both share:
  - citation_no, v (vs.)
  - printed_name, mailing_address, phone, date
Different:
  - MJBVB-009: violations narrative + amendment narrative + reason +
    agency/department block (officer-side).
  - MJBVB-017: defendant identity (name + DOB year + DL number),
    employment/income status checkboxes, fine extension narrative.

MJBVB-010 (motion to continue) has its own existing script.
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

    defendant = (parties.get("defendant") or parties.get("respondent")
                  or {})
    officer = (parties.get("officer")
                or parties.get("law_enforcement")
                or {})

    # Captions used by both MJBVB-009 and MJBVB-017
    citation = (case.get("citation_no")
                or facts.get("citation_no")
                or case.get("docket_no", ""))
    if _set(out, "citation_no", citation):
        changes.append(("citation_no", citation, "citation"))
    if _set(out, "v", "v."):
        changes.append(("v", "v.", "v-sep"))

    # ---- MJBVB-009 (officer's motion to amend) ----
    # The charged violations, the requested amendment, and the reason are
    # the substance of the motion — fill ONLY when explicitly provided
    # (the old defaults invented a § 1303(1) charge and an exculpatory
    # records-check narrative).
    violations = facts.get("mjbvb_original_violations", "")
    if violations:
        if _set(out, "violations", violations):
            changes.append(("violations", violations, "violations"))
        if _set(out, "the_violations_iwish_to_amendare", violations):
            changes.append(("the_violations_iwish_to_amendare", violations,
                            "viol-to-amend"))

    amendment = facts.get("mjbvb_amendment", "")
    if amendment:
        if _set(out, "amendment", amendment):
            changes.append(("amendment", amendment, "amendment"))
        if _set(out, "iwouldlike_to_amendthe_violations_to_read", amendment):
            changes.append(("iwouldlike_to_amendthe_violations_to_read",
                            amendment, "amend-text"))

    reason = facts.get("mjbvb_amend_reason", "")
    if reason:
        if _set(out, "reason", reason):
            changes.append(("reason", reason, "reason"))
        if _set(out, "the_reason_for_this_requestis", reason):
            changes.append(("the_reason_for_this_requestis", reason,
                            "reason-narr"))

    # Officer / agency block on MJBVB-009 — ONLY from a real officer
    # party or explicit facts (the old defaults invented an officer,
    # agency, address, and phone).
    officer_name = (officer.get("full_name")
                     or facts.get("mjbvb_officer_name", ""))
    agency = (officer.get("agency")
              or facts.get("mjbvb_agency", ""))
    agency_addr = (officer.get("address")
                    or facts.get("mjbvb_agency_address", ""))
    officer_phone = (officer.get("phone")
                      or facts.get("mjbvb_officer_phone", ""))
    if officer_name and _set(out, "printed_name", officer_name):
        changes.append(("printed_name", officer_name, "off-name"))
    if agency and _set(out, "agency_department", agency):
        changes.append(("agency_department", agency, "agency"))
    if agency_addr and _set(out, "mailing_address", agency_addr):
        changes.append(("mailing_address", agency_addr, "agency-addr"))
    if officer_phone and _set(out, "phone", officer_phone):
        changes.append(("phone", officer_phone, "off-phone"))

    # ---- MJBVB-017 (defendant's fine-extension request) ----
    def_name = defendant.get("full_name", "")
    def_addr = defendant.get("address", "")
    def_phone = defendant.get("phone", "")
    if _set(out, "my_name_is", def_name):
        changes.append(("my_name_is", def_name, "def-name"))
    if _set(out, "my_currentmailingaddress_is", def_addr):
        changes.append(("my_currentmailingaddress_is", def_addr, "def-addr"))
    if _set(out, "my_telephone_number_is", def_phone):
        changes.append(("my_telephone_number_is", def_phone, "def-phone"))

    # Year of birth (just the year)
    dob = defendant.get("dob", "")
    yob = dob[:4] if dob and len(dob) >= 4 else ""
    if _set(out, "the_year_iwas_born_was", yob):
        changes.append(("the_year_iwas_born_was", yob, "yob"))

    # Fine amount + due date — ONLY when explicitly provided (the fine
    # total was a stock "240.00").
    fine = facts.get("mjbvb_fine_total", "")
    fine_due = facts.get("mjbvb_fine_due_date",
                            case.get("event_date", ""))
    if fine and _set(out, "totalamountoffines_owed", fine):
        changes.append(("totalamountoffines_owed", fine, "fine-total"))
    if fine_due and _set(out, "fine_due_date", fine_due):
        changes.append(("fine_due_date", fine_due, "fine-due"))

    # Reasons for extension narrative — ONLY when explicitly provided
    # (was a stock reduced-work-hours hardship narrative).
    ext_reason = facts.get("mjbvb_extension_reason", "")
    if ext_reason:
        # Schema has full `_as_follows_N` suffix (truncation only happens
        # in display); both `_isare_a` (legacy short) and
        # `_isare_as_follows_N` (current) variants tried so the script
        # covers both schemas.
        for fid in (
            "the_reasons_iam_requestinga_fine_extension_isare_as_follows_1",
            "the_reasons_iam_requestinga_fine_extension_isare_as_follows_2",
            "the_reasons_iam_requestinga_fine_extension_isare_a",
            "the_reasons_iam_requestinga_fine_extension_isare_a_2",
        ):
            if _set(out, fid, ext_reason):
                changes.append((fid, ext_reason, "ext-reason"))

    # Employment-status radios — ONLY when an employer is actually known
    # (the old default checked "employed" and invented an employer).
    employer = (defendant.get("employer")
                 or facts.get("mjbvb_defendant_employer", ""))
    if employer:
        if _set(out, "imake", "X"):
            changes.append(("imake", "X", "emp-yes"))
        if _set(out, "employedby", employer):
            changes.append(("employedby", employer, "employer"))

    # Request choice — check ONLY on an explicit boolean fact (was
    # auto-checked, choosing relief on the defendant's behalf).
    if (facts.get("mjbvb_request_payment_plan") is True
            and _set(out, "irequest_thatthe_courtgrantme", "X")):
        changes.append(("irequest_thatthe_courtgrantme", "X", "request"))

    # Date of signature (both MJBVB forms have `date` and `date1`)
    sig_date = (case.get("filing_date") or case.get("event_date", ""))
    if _set(out, "date", sig_date):
        changes.append(("date", sig_date, "date"))
    if _set(out, "date1", sig_date):
        changes.append(("date1", sig_date, "date1"))

    return out, changes


if __name__ == "__main__":
    print("Use via fill_and_audit.py RECIPE3 dispatch")
    sys.exit(0)
