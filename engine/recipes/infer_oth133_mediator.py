"""OTH-133 (GAL Mentor Request Form) recipe-3 inference.

The form (Administrative Order JB-25-01, "GAL Mentor Request Form") is
submitted by a Guardian ad Litem requesting a mentor. It carries:
  A. Date of Request
  B. GAL's Contact Information (Name / Business Mailing Address / City /
     State / Zip Code / Business Telephone / Business Email)
  C. Case Information (Docket Number(s) / Parties' Names /
     Names of Counsel)
  D. Brief Summary of Issue(s)
  E. History (prior mentor, if any)
  Date + Signature of GAL

OFF-BY-ONE SCHEMA BUG (geometry-verified via widget-rect overlay):
The schema generator assigned each fillable widget the printed label of
the line ABOVE it, from the Name line all the way down through Brief
Summary. Each `_set(out, <widget_field_id>, value)` below therefore
writes the TRUE-printed-label value into the mis-named widget. The
correction chain (verified field_id -> true printed label):

  a_date_of_request_mmddyyyy -> Date of Request            (CORRECT)
  business_mailing_address   -> Name
  state                      -> Business Mailing Address (street)
  business_telephone         -> City        (3-col row, left)
  zip_code                   -> State       (3-col row, middle)
  undefined                  -> Zip Code    (3-col row, right)
  undefined_2                -> Business Telephone
  c_case_information         -> Business Email
  parties_names              -> Docket Number(s)
  1                          -> Parties' Names           (multi-line)
  1_2                        -> Names of Counsel         (multi-line)
  1_3                        -> Brief Summary of Issue(s)(multi-line)
  prior_mentor_1             -> prior mentor (History E)  (CORRECT)
  date_mmddyyyy              -> Date                      (CORRECT)
  text25                     -> Signature of GAL (printed)(CORRECT)

Reads case.parties.attorney (the GAL/requester) + case.parties to
derive party names + court info. Stock-requester fallback fills the
contact block when no attorney/GAL record is present.
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

    attorney = parties.get("attorney") or {}
    petitioner = (parties.get("petitioner") or parties.get("plaintiff")
                   or {})
    respondent = (parties.get("respondent") or parties.get("defendant")
                   or {})
    # Requester is the GAL, typically captured in the attorney record.
    # Pro-se / self-filing GALs use the plaintiff/petitioner record.
    # ONLY real party data or explicit oth_requester_* facts — never a
    # stock identity (was "Eleanor M. Walsh, Esq. / Walsh & Associates"
    # with invented address, phone, and email).
    if not attorney.get("full_name"):
        attorney = {
            "full_name": facts.get("oth_requester_name",
                                       petitioner.get("full_name", "")),
            "address": facts.get("oth_requester_address",
                                     petitioner.get("address", "")),
            "city": facts.get("oth_requester_city",
                                  petitioner.get("city", "")),
            "state": "ME",
            "zip": facts.get("oth_requester_zip",
                                 petitioner.get("zip", "")),
            "phone": facts.get("oth_requester_phone",
                                   petitioner.get("phone", "")),
            "email": facts.get("oth_requester_email",
                                   petitioner.get("email", "")),
            "firm": facts.get("oth_requester_firm", ""),
        }

    # Section A — Date of request (CORRECT widget id)
    req_date = (facts.get("oth_request_date")
                 or case.get("filing_date")
                 or case.get("event_date") or "")
    if _set(out, "a_date_of_request_mmddyyyy", _iso_to_us(req_date)):
        changes.append(("a_date_of_request_mmddyyyy", _iso_to_us(req_date),
                        "request-date"))

    # Section B — GAL's Contact Information.
    # Structured fields preferred (case schemas store address as a bare
    # street; city/state/zip live in separate fields). Each value goes
    # to the off-by-one-shifted widget (true label in comment).
    business_addr = attorney.get("address", "")
    atty_city = attorney.get("city", "")
    atty_state = attorney.get("state", "ME")
    atty_zip = attorney.get("zip", "")
    atty_phone = attorney.get("phone", "")
    atty_email = attorney.get("email", "")
    requester_name = (attorney.get("full_name")
                       or facts.get("oth_requester_name", ""))

    if requester_name and _set(out, "business_mailing_address",
                                requester_name):
        changes.append(("business_mailing_address", requester_name,
                        "name(true)"))
    if business_addr and _set(out, "state", business_addr):
        changes.append(("state", business_addr, "street(true)"))
    if atty_city and _set(out, "business_telephone", atty_city):
        changes.append(("business_telephone", atty_city, "city(true)"))
    if atty_state and _set(out, "zip_code", atty_state):
        changes.append(("zip_code", atty_state, "state(true)"))
    if atty_zip and _set(out, "undefined", atty_zip):
        changes.append(("undefined", atty_zip, "zip(true)"))
    if atty_phone and _set(out, "undefined_2", atty_phone):
        changes.append(("undefined_2", atty_phone, "phone(true)"))
    if atty_email and _set(out, "c_case_information", atty_email):
        changes.append(("c_case_information", atty_email, "email(true)"))

    # Section C — Case Information.
    # Docket Number(s) -> parties_names widget (off-by-one).
    docket = (case.get("docket_no") or court.get("docket_no")
               or facts.get("docket_no", ""))
    if docket and _set(out, "parties_names", docket):
        changes.append(("parties_names", docket, "docket(true)"))

    # Parties' Names -> widget "1" (off-by-one). "Plaintiff v. Defendant".
    pl_name = petitioner.get("full_name", "")
    df_name = respondent.get("full_name", "")
    parties_caption = (f"{pl_name} v. {df_name}"
                        if pl_name and df_name else pl_name or df_name)
    if parties_caption and _set(out, "1", parties_caption):
        changes.append(("1", parties_caption, "parties(true)"))

    # Names of Counsel -> widget "1_2" (off-by-one).
    counsel = facts.get("oth_names_of_counsel", "")
    if not counsel:
        names = []
        if requester_name:
            names.append(f"{requester_name} (GAL)")
        # Counsel for each represented party, if present in the record.
        for role, rec in (("Plaintiff", petitioner),
                          ("Defendant", respondent)):
            c = (rec.get("attorney") or {}).get("full_name") if isinstance(
                rec.get("attorney"), dict) else rec.get("attorney")
            if c:
                names.append(f"{c} (counsel for {role})")
        # When no counsel is in the record, leave blank — never assert
        # the parties are pro se (was a stock "self-represented" line).
        counsel = "; ".join(names)
    if counsel and _set(out, "1_2", counsel):
        changes.append(("1_2", counsel, "counsel(true)"))

    # Section D — Brief Summary of Issue(s) -> widget "1_3" (off-by-one).
    summary = facts.get("oth_issue_summary") or facts.get("summary", "")
    if not summary:
        issues = facts.get("issues") or []
        if isinstance(issues, list) and issues:
            summary = ("Issues presented: " + "; ".join(issues) + ".")
        elif case.get("case_type") and court.get("name"):
            # Compose only from real case/court data (the old fallback
            # defaulted to "civil" + "Maine District Court").
            summary = (f"{case['case_type'].replace('_',' ').title()} "
                        f"matter pending in {court['name']}, "
                        f"{court.get('county') or court.get('location','')}.")
    if summary and _set(out, "1_3", summary):
        changes.append(("1_3", summary, "summary(true)"))

    # Section E — History (prior mentor) — ONLY when explicitly provided
    # (was defaulted to "No prior mentor services", a factual assertion).
    prior = facts.get("oth_prior_mentor", "")
    if prior and _set(out, "prior_mentor_1", prior):
        changes.append(("prior_mentor_1", prior, "prior-mentor"))

    # Signature date (CORRECT widget id).
    sig_date = (case.get("filing_date") or case.get("event_date") or "")
    if _set(out, "date_mmddyyyy", _iso_to_us(sig_date)):
        changes.append(("date_mmddyyyy", _iso_to_us(sig_date), "sig-date"))

    # Signature of GAL — printed signer name (CORRECT widget id).
    if _set(out, "text25", requester_name):
        changes.append(("text25", requester_name, "signer"))

    return out, changes


if __name__ == "__main__":
    print("Use via fill_and_audit.py RECIPE3 dispatch")
    sys.exit(0)
