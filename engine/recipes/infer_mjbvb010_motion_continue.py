"""MJBVB-010 (Motion to Continue Trial) recipe-3 inference.

Citation-based motion form for Violations Bureau (traffic) court.
Page 1: requester info + reason. Page 2: notice-of-filing block
with up to 10 numbered reason-rows for the served-on parties.

Reads case.facts:
  citation_no, continuance_days, continuance_reason, trial_date,
  medical_reasons (Yes/No), first_continuance (Yes/No)
plus defendant party for the affiant block.
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

    affiant = (parties.get("defendant") or parties.get("petitioner") or
               parties.get("plaintiff") or {})
    name = affiant.get("full_name", "")

    # Caption
    citation = (facts.get("citation_no")
                 or case.get("citation_no")
                 or case.get("docket_no", ""))
    if _set(out, "citation_no", citation):
        changes.append(("citation_no", citation, "citation"))

    # Affiant identity (page 1 affidavit + page 2 notice)
    if _set(out, "full_name", name):
        changes.append(("full_name", name, "full-name"))
    if _set(out, "name", name):
        changes.append(("name", name, "name"))

    # Trial date + continuance length
    trial_date = (facts.get("trial_date")
                   or facts.get("event_date")
                   or case.get("event_date", ""))
    if _set(out, "trial_date", _iso_to_us(trial_date)):
        changes.append(("trial_date", _iso_to_us(trial_date), "trial-date"))

    days = str(facts.get("continuance_days", "30"))
    if _set(out, "number_of_days", days):
        changes.append(("number_of_days", days, "days"))
    # Long squashed field_id used by the schema
    if _set(out,
            "how_longofa_continuance_are_you_askingfornumber_ofdays",
            days):
        changes.append((
            "how_longofa_continuance_are_you_askingfornumber_ofdays",
            days, "days-long"))

    # Medical-reasons radio (default "No"), affidavit reference radio
    medical = facts.get("medical_reasons", "No")
    if _set(out,
            "ifyou_answeredyes_on_the_previous_question_use_the_attachedconfidentialaffidavitpage_2to",
            medical):
        changes.append((
            "ifyou_answeredyes_on_the_previous_question_use_the_attachedconfidentialaffidavitpage_2to",
            medical, "medical"))

    # Reason narrative (page 1)
    reason = facts.get("continuance_reason",
        "I have a scheduled out-of-state work commitment on the trial "
        "date that cannot be rescheduled without significant cost.")
    if _set(out, "reason_for_request", reason):
        changes.append(("reason_for_request", reason, "reason"))
    if _set(out, "reason_for_request1", reason):
        changes.append(("reason_for_request1", reason, "reason-1"))

    # Court-presentation acknowledgments (radios; default "Yes")
    if _set(out,
            "i_understand_thatthisrequestwillbepresentedtothecourt_for",
            "Yes"):
        changes.append((
            "i_understand_thatthisrequestwillbepresentedtothecourt_for",
            "Yes", "ack-court"))
    if _set(out,
            "i_certify_thatallnamed_parties_have_been_notifiedof_this_filing",
            "Yes"):
        changes.append((
            "i_certify_thatallnamed_parties_have_been_notifiedof_this_filing",
            "Yes", "ack-notified"))

    # Movant address/phone — page 1 movant block. Schema has BOTH
    # underscored and squashed variants of mailing-address widgets.
    addr_street = affiant.get("address", "")
    addr_city = affiant.get("city", "")
    addr_state = affiant.get("state", "ME")
    addr_zip = affiant.get("zip", "")
    full_addr = ", ".join(p for p in (
        addr_street, addr_city, f"{addr_state} {addr_zip}".strip())
        if p)
    phone = affiant.get("phone", "")
    if _set(out, "mailingaddress", full_addr):
        changes.append(("mailingaddress", full_addr, "addr"))
    if _set(out, "phone_number", phone):
        changes.append(("phone_number", phone, "phone"))
    if _set(out, "printedname", name):
        changes.append(("printedname", name, "printedname"))
    if _set(out, "printed_name", name):
        changes.append(("printed_name", name, "printed-name"))
    # Movant role/agency (default "Self-represented (Pro se)")
    role = facts.get("movant_agency", "Self-represented (pro se)")
    if _set(out, "agencydepartment", role):
        changes.append(("agencydepartment", role, "agency-dept"))
    # First-request Yes/No (default "Yes")
    first_req = facts.get("first_continuance", "Yes")
    for fid in ("first_request_yes_no", "first_request",
                 "is_this_the_first_request"):
        if _set(out, fid, first_req):
            changes.append((fid, first_req, "first-req"))
    # "Medical reasons" Yes/No (separate from the affidavit-reference radio).
    # Schema doesn't have a dedicated checkbox; the answer goes into the
    # page-2 medical narrative `reasons_are_as_follows_1`.

    # Date of signature
    sig_date = (case.get("filing_date") or case.get("event_date", ""))
    if _set(out, "date", _iso_to_us(sig_date)):
        changes.append(("date", _iso_to_us(sig_date), "date"))
    if _set(out, "date_2", _iso_to_us(sig_date)):
        changes.append(("date_2", _iso_to_us(sig_date), "date2"))

    # Page 2 'v.' separator
    if _set(out, "v", "v."):
        changes.append(("v", "v.", "v"))

    # Page-2 reasons-are-as-follows lines (first row populated)
    if _set(out, "reasons_are_as_follows_1", reason):
        changes.append(("reasons_are_as_follows_1", reason, "reasons-1"))

    # Additional names / additional names1/2 — leave blank if no
    # co-movants (audit accepts).

    return out, changes


if __name__ == "__main__":
    print("Use via fill_and_audit.py RECIPE3 dispatch")
    sys.exit(0)
