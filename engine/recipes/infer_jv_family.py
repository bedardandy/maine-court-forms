"""JV family (Juvenile Court) recipe-3 inference.

Covers JV-006-W, JV-012, JV-017, JV-022, JV-040, JV-041, JV-043 —
juvenile-court forms that share the "STATE OF MAINE v. <Juvenile>"
caption, juvenile name + DOB, attorney bar block, and gender checkbox.

Reads case.parties.juvenile (or .minor) + case.facts.juvenile_*.
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

    juvenile = (parties.get("juvenile") or parties.get("minor")
                 or parties.get("respondent") or parties.get("defendant") or {})
    parent = (parties.get("parent") or parties.get("guardian")
               or parties.get("legal_custodian")
               or parties.get("petitioner") or {})
    court = case.get("court") or {}

    # JV-006-W (Order on Conditions of Release) — caption is offset-named and
    # gets polluted from two directions: build_kv_map's case_constant pass
    # stamps `location_town` (physically the Docket No. line) with the court
    # location, and the JV-022 community-service block below fills `undefined`
    # (physically the Location (Town) line) with the supervisor name via _set.
    # Force by true position, gated to JV-006-W via its unique release-
    # conditions field. Setting these early means the later JV-022
    # `_set(out, "undefined", sup)` sees a non-empty value and no-ops, so the
    # JV-022 supervisor-signature path is unaffected.
    is_jv006w = ("juvenile_is_released_pending_further_court_proceedings_on_the_condition_that_the_juvenile"
                 in kv_map)
    if is_jv006w:
        if court.get("location"):
            out["undefined"] = court.get("location", "")
            changes.append(("undefined", court.get("location", ""), "jv006w-loc"))
        if case.get("docket_no"):
            out["location_town"] = case.get("docket_no", "")
            changes.append(("location_town", case.get("docket_no", ""),
                            "jv006w-docket"))

    # JV-034 — Motion / Order regarding evaluation appointment for
    # juvenile in DOC custody (gated on `the_attorney_for_the_state`).
    is_jv034 = ("the_attorney_for_the_state" in kv_map
                 and "is_awaiting_hearing_on_mmddyyyy" in kv_map)
    if is_jv034:
        state_atty = (facts.get("jv_state_attorney_name")
                      or "Robert L. Marshall, ADA")
        state_atty_bar = facts.get("jv_state_attorney_bar",
                                       "Bar #5421")
        # `printed_name_and_bar_no` is 256 px wide — keep printed
        # name+bar concise so the row doesn't overflow into next column.
        state_atty_printed = f"{state_atty} ({state_atty_bar})"
        if _set(out, "the_attorney_for_the_state", state_atty):
            changes.append(("the_attorney_for_the_state", state_atty,
                              "jv034-state-atty"))
        custody_loc = facts.get("jv_custody_location",
            "the Long Creek Youth Development Center in South Portland, Maine")
        if _set(out,
                "is_currently_in_the_custody_of_the_department_of_corrections",
                custody_loc):
            changes.append((
                "is_currently_in_the_custody_of_the_department_of_corrections",
                custody_loc, "jv034-custody-loc"))
        hearing_date_us = _iso_to_us(
            facts.get("jv_hearing_date") or case.get("event_date", ""))
        if _set(out, "is_awaiting_hearing_on_mmddyyyy", hearing_date_us):
            changes.append(("is_awaiting_hearing_on_mmddyyyy",
                              hearing_date_us, "jv034-hearing-date"))
        # `into` widget — the evaluation/treatment program the juvenile
        # has an appointment for
        program = facts.get("jv_evaluation_program",
            "the Maine Department of Health and Human Services Division of "
            "Juvenile Mental Health Services Adolescent Diagnostic Program")
        if _set(out, "into", program):
            changes.append(("into", program, "jv034-program"))
        # Appointment date + 2 time/place rows
        appt_date_us = _iso_to_us(
            facts.get("jv_appointment_date") or case.get("event_date", ""))
        if _set(out, "date_mmddyyyy", appt_date_us):
            changes.append(("date_mmddyyyy", appt_date_us,
                              "jv034-appt-date"))
        if _set(out, "time_1", facts.get("jv_appointment_time_1", "10:00 a.m.")):
            changes.append(("time_1", facts.get("jv_appointment_time_1","10:00 a.m."),
                              "jv034-time-1"))
        # `place_1/2` widgets are 151 px wide — keep entries short.
        if _set(out, "place_1", facts.get("jv_appointment_place_1",
                                              "DHHS Bangor")):
            changes.append(("place_1", facts.get("jv_appointment_place_1",
                                                      "DHHS Bangor"),
                              "jv034-place-1"))
        if _set(out, "time_2", facts.get("jv_appointment_time_2", "1:00 p.m.")):
            changes.append(("time_2", facts.get("jv_appointment_time_2","1:00 p.m."),
                              "jv034-time-2"))
        if _set(out, "place_2", facts.get("jv_appointment_place_2",
                                              "DHHS Bangor")):
            changes.append(("place_2", facts.get("jv_appointment_place_2",
                                                      "DHHS Bangor"),
                              "jv034-place-2"))
        # Two signature rows (date + signer + printed name + bar)
        sig_date_us = _iso_to_us(case.get("filing_date") or "")
        for date_fid, name_fid, printed_fid, signer_printed in [
            ("date_mmddyyyy_2", "undefined", "printed_name_and_bar_no",
             state_atty_printed),
            ("date_mmddyyyy_3", "undefined_2", "printed_name_and_bar_no_2",
             state_atty_printed),
        ]:
            if _set(out, date_fid, sig_date_us):
                changes.append((date_fid, sig_date_us, "jv034-sig-date"))
            if _set(out, name_fid, state_atty):
                changes.append((name_fid, state_atty, "jv034-sig-name"))
            if _set(out, printed_fid, signer_printed):
                changes.append((printed_fid, signer_printed, "jv034-sig-printed"))

    # JV-044 — Motion to seal juvenile court record. Form has:
    # - `i` (movant name)
    # - narrative `to_public_inspection_for_the_following_reasons...`
    # - signer block (printed_name_and_bar_number_if_applicable,
    #   mailing_address_1/2, telephone, email)
    is_jv044 = "printed_name_and_bar_number_if_applicable" in kv_map
    if is_jv044:
        atty = parties.get("attorney") or {}
        if not atty.get("full_name"):
            atty = {
                "full_name": facts.get("jv044_attorney",
                                           "Robert L. Marshall, ADA"),
                "bar_number": "Bar #5421",
                "address": "97 Hammond Street",
                "city": court.get("location", "Bangor"),
                "state": "ME",
                "zip": "04401",
                "phone": "(207) 561-3000",
                "email": "rmarshall@maineda.gov",
            }
        atty_csz = f"{atty.get('city','')}, {atty.get('state','ME')} {atty.get('zip','')}".strip(', ')
        printed = f"{atty.get('full_name')}, {atty.get('bar_number','')}".strip(', ')
        if _set(out, "printed_name_and_bar_number_if_applicable", printed):
            changes.append(("printed_name_and_bar_number_if_applicable",
                              printed, "jv044-printed"))
        if _set(out, "mailing_address_1", atty.get("address", "")):
            changes.append(("mailing_address_1", atty.get("address",""),
                              "jv044-addr-1"))
        if _set(out, "mailing_address_2", atty_csz):
            changes.append(("mailing_address_2", atty_csz, "jv044-addr-2"))
        if _set(out, "telephone", atty.get("phone", "")):
            changes.append(("telephone", atty.get("phone",""), "jv044-phone"))
        if _set(out, "email", atty.get("email", "")):
            changes.append(("email", atty.get("email",""), "jv044-email"))
        # Movant identity (i)
        movant = atty.get("full_name", "")
        if _set(out, "i", movant):
            changes.append(("i", movant, "jv044-movant"))
        # Sealing-reasons narrative
        seal_reasons = facts.get("jv044_seal_reasons",
            f"the above-named juvenile, {juvenile.get('full_name','the juvenile')}, "
            "is now an adult; rehabilitation is complete; ongoing public access to the "
            "juvenile record poses a substantial risk of impairing future educational "
            "and employment opportunities; and sealing is consistent with the privacy "
            "policies underlying Maine's juvenile-court confidentiality framework.")
        if _set(out,
                "to_public_inspection_for_the_following_reasons_attach_additional_pages_if_necessary_1",
                seal_reasons):
            changes.append((
                "to_public_inspection_for_the_following_reasons_attach_additional_pages_if_necessary_1",
                seal_reasons, "jv044-reasons"))

    # JV-040 also has the DOB+gender header narrative widget
    is_jv040_header = "the_above_named_juvenile_whose_date_of_birth_is_mmddyyyy_and_gender_is" in kv_map
    if is_jv040_header and juvenile.get("dob"):
        dob_us = _iso_to_us(juvenile["dob"])
        gender = facts.get("juvenile_gender", "male")
        narrative = f"{dob_us} and {gender}"
        if _set(out,
                "the_above_named_juvenile_whose_date_of_birth_is_mmddyyyy_and_gender_is",
                narrative):
            changes.append((
                "the_above_named_juvenile_whose_date_of_birth_is_mmddyyyy_and_gender_is",
                narrative, "jv040-dob-gender"))

    # JV-040 — Juvenile Final Discharge Notice. Has gender_is widget +
    # discharge-type checkbox + "This notice is being filed by" narrative.
    is_jv040 = ("is_finally_discharged_from_the_disposition_imposed_for_a_juvenile_crime_other_than_murder_class_a_b_or_c"
                in kv_map
                or "is_finally_discharged_from_the_disposition_imposed" in kv_map)
    if is_jv040:
        # Gender — JV-040 uses bare `gender_is` widget (text), not radio.
        g_str = facts.get("juvenile_gender_text", "male")
        if _set(out, "gender_is", g_str):
            changes.append(("gender_is", g_str, "jv040-gender"))
        # Discharge-type checkbox (default: non-Class-A/B/C)
        for fid in (
            "is_finally_discharged_from_the_disposition_imposed_for_a_juvenile_crime_other_than_murder_class_a_b_or_c",
            "is_finally_discharged_from_the_disposition_imposed",
        ):
            if _set(out, fid, "X"):
                changes.append((fid, "X", "jv040-discharge"))
        # Filer ("This notice is being filed by")
        filer = facts.get("jv040_filer",
            "the Maine Department of Corrections, Juvenile Services Office, "
            f"Region 2 — {court.get('location','Bangor')} District")
        for fid in ("this_notice_of_discharge_is_being_filed_by",
                     "this_notice_is_being_filed_by",
                     "filed_by"):
            if _set(out, fid, filer):
                changes.append((fid, filer, "jv040-filer"))

    # JV-043 — Notice of Adjudication (juvenile crime). Schema has the
    # juvenile DOB, gender checkboxes (1=male, 2=female, 3=other), and
    # a signature/contact block (printed_name, mailing_address_1/2,
    # telephone, email) for the attorney/prosecutor filing.
    is_jv043 = ("the_abovenamed_juvenile_whose_date_of_birth_is_mmddyyyy"
                in kv_map and "printed_name" in kv_map
                and "mailing_address_1" in kv_map
                and len(kv_map) <= 20)  # JV-043 is small (~14 widgets)
    if is_jv043:
        gender = (facts.get("juvenile_gender") or "male").lower()
        gender_box = {"male":"check_box1", "female":"check_box2",
                       "other":"check_box3"}.get(gender, "check_box1")
        if _set(out, gender_box, "X"):
            changes.append((gender_box, "X", "jv043-gender"))
        # Signer/contact block — filing attorney (state) or pro-se
        signer_atty = (parties.get("attorney") or {}).get("full_name", "")
        signer_atty = (signer_atty
                        or facts.get("jv043_filing_attorney",
                                       "Hon. Robert L. Marshall, ADA"))
        atty_addr = (parties.get("attorney") or {}).get("address",
            facts.get("jv043_attorney_address",
                "97 Hammond Street"))
        atty_csz = facts.get("jv043_attorney_csz",
            f"{court.get('location','Bangor')}, ME 04401")
        atty_phone = (parties.get("attorney") or {}).get("phone",
            facts.get("jv043_attorney_phone", "(207) 561-3000"))
        atty_email = (parties.get("attorney") or {}).get("email",
            facts.get("jv043_attorney_email",
                        "robert.marshall@maineda.gov"))
        if _set(out, "printed_name", signer_atty):
            changes.append(("printed_name", signer_atty, "jv043-printed"))
        if _set(out, "mailing_address_1", atty_addr):
            changes.append(("mailing_address_1", atty_addr, "jv043-addr1"))
        if _set(out, "mailing_address_2", atty_csz):
            changes.append(("mailing_address_2", atty_csz, "jv043-addr2"))
        if _set(out, "telephone", atty_phone):
            changes.append(("telephone", atty_phone, "jv043-phone"))
        if _set(out, "email", atty_email):
            changes.append(("email", atty_email, "jv043-email"))

    # JV-017 — Waiver of Counsel (juvenile case).
    # Schema has hearing date + waiver-before-judge checkbox + 4 dated
    # signature rows for parent/guardian/legal custodian (rows 1+2).
    is_jv017 = ("this_waiver_was_executed_before_a_judge" in kv_map
                 and "date_of_the_hearing_is_mmddyyyy" in kv_map)
    if is_jv017:
        hearing_date_us = _iso_to_us(
            facts.get("jv_hearing_date")
            or case.get("event_date")
            or case.get("filing_date", ""))
        if _set(out, "date_of_the_hearing_is_mmddyyyy", hearing_date_us):
            changes.append(("date_of_the_hearing_is_mmddyyyy",
                              hearing_date_us, "jv017-hearing-date"))
        if _set(out, "this_waiver_was_executed_before_a_judge", "X"):
            changes.append(("this_waiver_was_executed_before_a_judge",
                              "X", "jv017-before-judge"))
        # Two parallel signature rows — juvenile signs first, then
        # parent/guardian/legal custodian signs. `date_mmddyyyy_2/4` hold
        # the date on each signature line; `undefined_2/4` hold the
        # printed name beside the signature.
        sig_date_us = _iso_to_us(
            case.get("filing_date") or case.get("event_date", ""))
        signer_blocks = [
            ("date_mmddyyyy_2", "undefined_2", juvenile.get("full_name", "")),
            ("date_mmddyyyy_3", "undefined_3", parent.get("full_name", "")),
            ("date_mmddyyyy_4", "undefined_4", parent.get("full_name", "")),
        ]
        for fid_d, fid_n, signer in signer_blocks:
            if signer and _set(out, fid_d, sig_date_us):
                changes.append((fid_d, sig_date_us, "jv017-sig-date"))
            if signer and _set(out, fid_n, signer):
                changes.append((fid_n, signer, "jv017-sig-name"))
        # Parent/Guardian/Legal Custodian checkbox (row 1 and row 2).
        role = facts.get("jv_signer_role", "parent")  # parent|guardian|legal_custodian
        role_map = {
            "parent":           ("parent", "parent_2"),
            "guardian":         ("guardian", "guardian_2"),
            "legal_custodian":  ("legal_custodian", "legal_custodian_2"),
        }
        for fid in role_map.get(role, ("parent", "parent_2")):
            if _set(out, fid, "X"):
                changes.append((fid, "X", "jv017-role"))

    # STATE OF MAINE caption — fixed
    for fid in ("state_of_maine", "state"):
        if _set(out, fid, "State of Maine"):
            changes.append((fid, "State of Maine", "state-caption"))

    # V. separator
    if _set(out, "v", "v."):
        changes.append(("v", "v.", "v-separator"))

    # Juvenile name (multiple variants)
    j_name = juvenile.get("full_name", "")
    if j_name:
        for fid in ("juvenile", "name_of_juvenile", "juveniles_name",
                     "the_above_named_juvenile_whose_date_of_birth"):
            if _set(out, fid, j_name):
                changes.append((fid, j_name, "juvenile-name"))

    # Juvenile DOB. JV-043 uses squashed `the_abovenamed_juvenile_whose_
    # date_of_birth_is_mmddyyyy` (no space-equivalent before "named",
    # with explicit `_is_mmddyyyy` suffix).
    if juvenile.get("dob"):
        dob_us = _iso_to_us(juvenile["dob"])
        for fid in ("date_of_birth", "juvenile_dob",
                     "the_above_named_juvenile_whose_date_of_birth",
                     "the_abovenamed_juvenile_whose_date_of_birth_is_mmddyyyy"):
            if _set(out, fid, dob_us):
                changes.append((fid, dob_us, "juvenile-dob"))

    # Juvenile gender (default per facts; many forms have male/female/other)
    gender = facts.get("juvenile_gender", "male")
    for fid in ("gender_is_male_female_other", "gender",
                 "juvenile_gender"):
        if _set(out, fid, gender):
            changes.append((fid, gender, "gender"))

    # Department of Corrections office (commonly a fixed Maine DOC field)
    doc_office = facts.get("juvenile_doc_office",
                              "Region 1 — Portland Juvenile Services Office")
    for fid in ("department_of_corrections_office_juvenile",
                 "doc_office", "department_of_corrections"):
        if _set(out, fid, doc_office):
            changes.append((fid, doc_office, "doc-office"))

    # Community service (JV-022 — Community Service Verification)
    org = facts.get("community_service_org",
                      "Portland Public Library — Volunteer Services")
    if _set(out, "organization_name", org):
        changes.append(("organization_name", org, "service-org"))

    sup = facts.get("community_service_supervisor", "Maria T. Hendricks")
    if _set(out, "supervisors_name", sup):
        changes.append(("supervisors_name", sup, "service-supervisor"))

    # Organization address (2 lines)
    org_addr1 = facts.get("community_service_address",
                            "5 Monument Square")
    org_addr2 = facts.get("community_service_address_2",
                            "Portland, ME 04101")
    if _set(out, "address_1", org_addr1):
        changes.append(("address_1", org_addr1, "service-addr1"))
    if _set(out, "address_2", org_addr2):
        changes.append(("address_2", org_addr2, "service-addr2"))

    # Telephone widgets — JV-022 has two (org phone, supervisor phone)
    org_phone = facts.get("community_service_phone", "(207) 871-1700")
    sup_phone = facts.get("community_service_supervisor_phone",
                            "(207) 871-1701")
    if _set(out, "telephone_number", org_phone):
        changes.append(("telephone_number", org_phone, "service-org-phone"))
    if _set(out, "telephone_number_2", sup_phone):
        changes.append(("telephone_number_2", sup_phone, "service-sup-phone"))

    # Total hours needed + required completion date (header line)
    hrs_total = facts.get("community_service_hours_total",
                            facts.get("community_service_hours", "24"))
    if _set(out, "total_number_of_hours_needed", hrs_total):
        changes.append(("total_number_of_hours_needed", hrs_total,
                        "total-hrs"))
    completion_date = (facts.get("community_service_completion_date")
                       or case.get("event_date", ""))
    completion_us = _iso_to_us(completion_date) if completion_date else ""
    if _set(out, "required_date_of_completion_mmddyyyy", completion_us):
        changes.append(("required_date_of_completion_mmddyyyy",
                        completion_us, "completion-date"))

    # Service log — 5 date+hours rows
    service_log = facts.get("community_service_log") or []
    if not service_log:
        # Build a stock 5-entry log totaling the required hours
        try:
            tot = int(hrs_total)
        except Exception:
            tot = 24
        per = max(1, tot // 5)
        base_date = (case.get("event_date", "") or "2026-04-15")[:10]
        try:
            from datetime import date, timedelta
            y, m, d = map(int, base_date.split("-"))
            d0 = date(y, m, d)
        except Exception:
            d0 = None
        service_log = []
        for i in range(5):
            if d0:
                di = d0.replace()
                from datetime import timedelta
                di = d0 + timedelta(days=i*7)
                ds = f"{di.month:02d}/{di.day:02d}/{di.year}"
            else:
                ds = ""
            hrs_i = per if i < 4 else (tot - per * 4)
            service_log.append((ds, str(hrs_i)))

    for i, (ds, hrs) in enumerate(service_log[:5], start=1):
        suf = "" if i == 1 else f"_{i}"
        if ds and _set(out, f"date_of_service_mmddyyyy{suf}", ds):
            changes.append((f"date_of_service_mmddyyyy{suf}", ds,
                            f"svc-date-{i}"))
        if hrs and _set(out, f"hours_completed{suf}", str(hrs)):
            changes.append((f"hours_completed{suf}", str(hrs),
                            f"svc-hrs-{i}"))

    # Performance rating — default Satisfactory
    perf = facts.get("community_service_rating", "satisfactory").lower()
    perf_map = {
        "highly_satisfactory": "highly_satisfactory",
        "highly":              "highly_satisfactory",
        "satisfactory":        "satisfactory",
        "unsatisfactory":      "unsatisfactory",
    }
    perf_fid = perf_map.get(perf, "satisfactory")
    if _set(out, perf_fid, "X"):
        changes.append((perf_fid, "X", "perf-rating"))

    # Comments (3 single-line widgets, ~540px wide — keep each ~85 chars)
    comments = facts.get("community_service_comments") or [
        "Participant arrived on time for each scheduled shift and "
        "followed all volunteer guidelines.",
        "Tasks completed: shelving returns, circulation-desk support, "
        "and literacy outreach assistance.",
        "All assigned hours completed in full as of the date of this "
        "report.",
    ]
    if isinstance(comments, str):
        comments = [comments]
    for i, line in enumerate(comments[:3], start=1):
        if line and _set(out, f"comments_{i}", line):
            changes.append((f"comments_{i}", line, f"comment-{i}"))

    # Signature block at bottom (supervisor signs)
    sig_date = (case.get("filing_date") or case.get("event_date") or "")
    sig_date_us = _iso_to_us(sig_date) if sig_date else ""
    if _set(out, "date_mmddyyyy", sig_date_us):
        changes.append(("date_mmddyyyy", sig_date_us, "sig-date"))
    if _set(out, "undefined", sup):
        changes.append(("undefined", sup, "sig-text"))
    if _set(out, "printed_name", sup):
        changes.append(("printed_name", sup, "sig-print"))

    # Notice is given / printed name + bar (JV-012, JV-043)
    notice = facts.get("notice_text",
                          "Notice is given pursuant to 15 M.R.S. § 3308 "
                          "that this matter is set for review hearing.")
    for fid in ("notice_is_given_that",):
        if _set(out, fid, notice):
            changes.append((fid, notice, "notice"))

    # Attorney printed name + bar (use case attorney)
    atty = parties.get("attorney") or {}
    if atty.get("full_name"):
        printed = atty["full_name"]
        if atty.get("bar_number"):
            printed = f"{atty['full_name']}, Bar #{atty['bar_number']}"
        for fid in ("printed_name_and_bar_number",
                     "printed_name_and_bar_number_if_applicable",
                     "printed_name"):
            if _set(out, fid, printed):
                changes.append((fid, printed, "atty-printed"))

    # "Signed by:" — typically wet-ink signature widget; leave empty per
    # audit convention (already in audit EXCLUSIONS for signatures).

    return out, changes


if __name__ == "__main__":
    print("Use via fill_and_audit.py RECIPE3 dispatch")
    sys.exit(0)
