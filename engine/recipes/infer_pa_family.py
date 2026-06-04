"""PA family (Protection From Abuse) recipe-3 inference.

Covers PA-005 (Plaintiff's affidavit — defendant identification),
PA-010 (Motion + Return of Service), and other PA forms.

Key insight: PFA forms need defendant identifying info (height, weight,
employer) that's NOT in the standard case dict. Stock defaults from
case.facts.pfa_*.

Reads:
  case.parties.plaintiff (protected person)
  case.parties.defendant (alleged abuser)
  case.facts.pfa_defendant_height, weight, employer, work_address
  case.facts.pfa_hearing_date, hearing_time, hearing_location
  case.facts.pfa_service_date, service_method
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

    # PFA "plaintiff" = protected person, "defendant" = alleged abuser
    plaintiff = (parties.get("plaintiff") or parties.get("petitioner")
                  or parties.get("protected_person") or {})
    defendant = (parties.get("defendant") or parties.get("respondent")
                  or parties.get("abuser") or {})
    attorney = parties.get("attorney") or {}

    # Captions
    if plaintiff.get("full_name"):
        for fid in ("plaintiff", "petitioner", "protected_person"):
            if _set(out, fid, plaintiff["full_name"]):
                changes.append((fid, plaintiff["full_name"], "plaintiff"))
    if defendant.get("full_name"):
        for fid in ("defendant", "respondent", "defendants_name"):
            if _set(out, fid, defendant["full_name"]):
                changes.append((fid, defendant["full_name"], "defendant"))

    # Defendant identifying info
    if defendant.get("address"):
        for fid in ("home_address", "defendants_home_address",
                     "defendant_address"):
            if _set(out, fid, defendant["address"]):
                changes.append((fid, defendant["address"], "def-home-addr"))

    # Phone — PA-005 has a single multi-phone widget
    # `telephone_homeworkcell`; other PA forms (PA-033, PA-010) have a
    # generic single-phone `telephone` widget in the attorney/contact
    # block which must NOT receive a long concatenated string (overflows
    # and triggers `truncated` audit).
    phones = []
    if defendant.get("phone_home"): phones.append(f"home: {defendant['phone_home']}")
    if defendant.get("phone_work"): phones.append(f"work: {defendant['phone_work']}")
    if defendant.get("phone_cell"): phones.append(f"cell: {defendant['phone_cell']}")
    if not phones and defendant.get("phone"):
        phones.append(defendant["phone"])
    phone_str_long = "; ".join(phones) or "Unknown"
    for fid in ("telephone_home_work_cell", "telephone_homeworkcell",
                 "defendant_phones"):
        if _set(out, fid, phone_str_long):
            changes.append((fid, phone_str_long, "def-phones"))

    # PA-005 plaintiff (protected person) caption fields
    if plaintiff.get("full_name"):
        if _set(out, "plaintiffs_name", plaintiff["full_name"]):
            changes.append(("plaintiffs_name", plaintiff["full_name"],
                            "pl-name-pa005"))
    pl_phones = []
    if plaintiff.get("phone_home"): pl_phones.append(f"home: {plaintiff['phone_home']}")
    if plaintiff.get("phone_work"): pl_phones.append(f"work: {plaintiff['phone_work']}")
    if plaintiff.get("phone_cell"): pl_phones.append(f"cell: {plaintiff['phone_cell']}")
    pl_phone_str = "; ".join(pl_phones) or plaintiff.get("phone","")
    if pl_phone_str and _set(out,
                                "telephone_homeworkcell_unless_confidential",
                                pl_phone_str):
        changes.append(("telephone_homeworkcell_unless_confidential",
                        pl_phone_str, "pl-phones-pa005"))
    if plaintiff.get("address") and _set(out, "address_unless_confidential",
                                            plaintiff["address"]):
        changes.append(("address_unless_confidential",
                        plaintiff["address"], "pl-addr-pa005"))

    # PA-005 defendant physical descriptors — fill ONLY when the case
    # explicitly provides them. This is a law-enforcement service form;
    # fabricating a description can misdirect the officer serving the
    # order, so a blank ("not provided") is always safer than a guess.
    pfa_facts = case.get("facts") or {}
    for fid, fact_key in [
        ("gender", "pfa_defendant_gender"),
        ("hair_color", "pfa_defendant_hair"),
        ("eye_color", "pfa_defendant_eyes"),
    ]:
        val = pfa_facts.get(fact_key)
        if val and _set(out, fid, val):
            changes.append((fid, val, f"pa005-{fid}"))

    # PA-005 firearm / violence / probation Y/N radios — default No
    for fid in ("does_the_defendant_own_a_firearm_or_other_weapon",
                 "does_the_defendant_have_a_history_of_violence"):
        if _set(out, fid, "No"):
            changes.append((fid, "No", "pa005-yn-default"))

    # PA-005 defendant vehicle — fill ONLY when explicitly provided.
    # Never fabricate a make/plate; a wrong vehicle misdirects service.
    for fid, fact_key, lbl in [
        ("make_and_year_yyyy", "pfa_defendant_vehicle_make", "veh-make"),
        ("typemodel", "pfa_defendant_vehicle_typemodel", "veh-type"),
        ("color", "pfa_defendant_vehicle_color", "veh-color"),
        ("registration_no_and_state_1",
         "pfa_defendant_vehicle_registration", "veh-reg-1"),
    ]:
        val = pfa_facts.get(fact_key)
        if val and _set(out, fid, val):
            changes.append((fid, val, lbl))

    # Employer + work address — fill ONLY when provided.
    employer = facts.get("pfa_defendant_employer")
    work_addr = facts.get("pfa_defendant_work_address")
    if employer and _set(out, "name_of_employer", employer):
        changes.append(("name_of_employer", employer, "employer"))
    if work_addr and _set(out, "work_address", work_addr):
        changes.append(("work_address", work_addr, "work-addr"))

    # Physical description (PA-005 specific) — fill ONLY when provided.
    height = facts.get("pfa_defendant_height")
    weight = facts.get("pfa_defendant_weight")
    if height and _set(out, "height", height):
        changes.append(("height", height, "height"))
    if weight and _set(out, "weight", weight):
        changes.append(("weight", weight, "weight"))

    # PA-010 motion narrative — generic fallback for any PA form that has
    # a singular "motion_request" widget (PA-010 itself is dispatched to
    # its own dedicated module).
    motion_request = facts.get("pfa_motion_request",
                                 "extend the existing Protection from Abuse Order "
                                 "for an additional one-year period, and to grant "
                                 "such further relief as the Court deems just and "
                                 "proper.")
    for fid in ("wherefore_defendant_asks_the_court_to",
                 "wherefore_plaintiff_asks_the_court_to",
                 "motion_request"):
        if _set(out, fid, motion_request):
            changes.append((fid, motion_request, "motion-request"))

    # Hearing block
    hearing_date = facts.get("pfa_hearing_date",
                                case.get("event_date") or "")
    hearing_time = facts.get("pfa_hearing_time", "9:00 AM")
    hearing_loc = facts.get("pfa_hearing_location",
                              f"{court.get('name','Maine District Court')}, "
                              f"{court.get('location','Portland')}")
    if hearing_date:
        for fid in ("at_am_pm_at_the_court_located_at",
                     "hearing_date_mmddyyyy"):
            if _set(out, fid, f"{hearing_time} at {hearing_loc}"):
                changes.append((fid, hearing_time, "hearing"))
        for fid in ("the_parties_are_hereby_notified_that_the_hearing_in_this_matter_i",
                     "hearing_notice"):
            if _set(out, fid, _iso_to_us(hearing_date)):
                changes.append((fid, _iso_to_us(hearing_date),
                                  "hearing-date"))

    # Return of Service block
    service_date = facts.get("pfa_service_date",
                               case.get("filing_date") or "")
    service_us = _iso_to_us(service_date)
    if service_date:
        for fid in ("on_mmddyyyy", "service_date_mmddyyyy", "date_mmddyyyy"):
            if _set(out, fid, service_us):
                changes.append((fid, service_us, "service-date"))
        for fid in ("at_am_pm_i_made_service_of_the_defen", "service_time"):
            if _set(out, fid, "10:30 AM"):
                changes.append((fid, "10:30 AM", "service-time"))
        for fid in ("by_delivering_a_copy_of_the_motion_and_notice_of_hearing_to_the_p",
                     "service_method"):
            if _set(out, fid, "in-hand personal service"):
                changes.append((fid, "in-hand personal service", "service-method"))

    # Law enforcement officer
    officer_name = facts.get("pfa_officer_name", "Deputy John C. Reynolds")
    officer_agency = facts.get("pfa_officer_agency",
                                  "Cumberland County Sheriff's Office")
    for fid in ("authorized_officer_printed_name",
                 "law_enforcement_officer"):
        if _set(out, fid, officer_name):
            changes.append((fid, officer_name, "officer-name"))
    for fid in ("law_enforcement_agency", "agency"):
        if _set(out, fid, officer_agency):
            changes.append((fid, officer_agency, "officer-agency"))

    # Captions used by PA-033 (foreign protection order registration)
    if plaintiff.get("full_name"):
        if _set(out, "plaintiffpetitioner", plaintiff["full_name"]):
            changes.append(("plaintiffpetitioner", plaintiff["full_name"],
                            "pl-pet-caption"))
    if defendant.get("full_name"):
        if _set(out, "defendantrespondent", defendant["full_name"]):
            changes.append(("defendantrespondent", defendant["full_name"],
                            "def-resp-caption"))

    # Docket
    if _set(out, "docket_no", case.get("docket_no", "")):
        changes.append(("docket_no", case.get("docket_no",""), "docket"))
    if _set(out, "location_town", court.get("location", "")):
        changes.append(("location_town", court.get("location",""), "loc-town"))

    # PA-024 / PA-025 have an INVERTED caption (no `docket_no` widget): the
    # widget named `undefined` is physically the Location (Town) line and the
    # one named `location_town` is physically the Docket No. line (offset auto-
    # naming). Re-place by position so court location and docket land correctly.
    if "location_town" in out and "docket_no" not in out and "undefined" in out:
        out["undefined"] = court.get("location", "")
        out["location_town"] = case.get("docket_no", "")
        changes.append(("undefined", court.get("location", ""), "pa024-loc"))
        changes.append(("location_town", case.get("docket_no", ""), "pa024-docket"))

    # PA-025 — defendant DOB + relinquished weapons narrative
    def_dob = defendant.get("dob", "")
    if _set(out, "defendant_date_of_birth_mmddyyyy", _iso_to_us(def_dob)):
        changes.append(("defendant_date_of_birth_mmddyyyy",
                        _iso_to_us(def_dob), "def-dob"))

    weapons_narrative = facts.get("pa_weapons_relinquished",
        "I relinquished all firearms and dangerous weapons in my "
        "possession to the Cumberland County Sheriff's Office on the "
        "date and at the location indicated above.")
    if _set(out, "i_relinquished_the_firearms_andor_dangerous_weapon",
            weapons_narrative):
        changes.append(("i_relinquished_the_firearms_andor_dangerous_weapon",
                        weapons_narrative, "weapons-narr"))

    weapon_list = facts.get("pa_weapon_list",
        "One (1) 12-gauge shotgun, serial number REDACTED; "
        "one (1) .22 caliber rifle, serial number REDACTED.")
    if _set(out, "the_description_of_each_weapon_relinquished_is_as_",
            weapon_list):
        changes.append(("the_description_of_each_weapon_relinquished_is_as_",
                        weapon_list, "weapons-desc"))

    # The "and address is" widget after agency name
    agency_addr = facts.get("pa_agency_address",
        "36 County Way, Portland, ME 04102")
    if _set(out, "and_address_is", agency_addr):
        changes.append(("and_address_is", agency_addr, "agency-addr"))

    # PA-025 — item 1 checkbox (I relinquished) is on by default unless
    # case.facts.pa_no_weapons is truthy
    no_weapons = facts.get("pa_no_weapons", False)
    if no_weapons:
        if _set(out, "i_have_no_firearms_or_dangerous_weapons_in_my_possessio", "X"):
            changes.append(("i_have_no_firearms_or_dangerous_weapons_in_my_possessio",
                            "X", "no-weapons"))
    else:
        for fid in ("i_relinquished_the_firearms_andor_dangerous_weapons_lis",
                     "i_have_attached_a_list_describing_each_weapon_relinquis"):
            if _set(out, fid, "X"):
                changes.append((fid, "X", "weapons-yes"))

    # PA-025 — relinquish date
    relinquish_date = facts.get("pa_relinquish_date",
                                   case.get("event_date", ""))
    if _set(out, "2_date_the_weapons_waswere_relinquished_mmddyyyy",
            _iso_to_us(relinquish_date)):
        changes.append(("2_date_the_weapons_waswere_relinquished_mmddyyyy",
                        _iso_to_us(relinquish_date), "relinq-date"))

    # PA-025 — weapons list table (3 rows at p0 y=430-457, 486px wide).
    # Field IDs `1_3`, `2_3`, `3` are the row narratives.
    weapons_rows = facts.get("pa_weapons_list_rows", [
        "(1) Mossberg Model 500 12-gauge shotgun — serial #SN1234567",
        "(1) Ruger 10/22 .22 caliber rifle — serial #SN7654321",
        "",
    ])
    if isinstance(weapons_rows, str):
        weapons_rows = [weapons_rows]
    for i, w in enumerate(weapons_rows[:3]):
        fid = "1_3" if i == 0 else "2_3" if i == 1 else "3"
        if w and _set(out, fid, w):
            changes.append((fid, w, f"pa025-weapon-row-{i+1}"))

    # PA-025 — weapon type (default Firearm)
    weapon_type = facts.get("pa_weapon_type", "firearm")
    type_map = {"firearm": "firearm",
                 "blunt": "blunt_weapon", "blunt_weapon": "blunt_weapon",
                 "edged": "edged_weapon", "edged_weapon": "edged_weapon"}
    wtype_fid = type_map.get(weapon_type, "firearm")
    if _set(out, wtype_fid, "X"):
        changes.append((wtype_fid, "X", "weapon-type"))

    # PA-025 — recipient of weapons (default: law enforcement agency)
    recipient = facts.get("pa_weapons_recipient", "agency")  # agency|court
    recip_fid = ("the_law_enforcement_agency_designated_on_the_order_with"
                  if recipient == "agency" else "the_court")
    if _set(out, recip_fid, "X"):
        changes.append((recip_fid, "X", "weapons-recipient"))

    # PA-025 — plaintiff caption + v_1/v_2 separators
    if plaintiff.get("full_name"):
        for fid in ("v_1", "v_2"):
            if _set(out, fid, "v."):
                changes.append((fid, "v.", "v-sep"))

    # Everything below is PA-033 (foreign protection order registration) only.
    # These assignments use generic field_ids (undefined, undefined_2,
    # date_mmddyyyy, mailing_address_*, address_*) that also exist in PA-005/024/
    # 025 at different positions, so running them ungated polluted those forms
    # (e.g. PA-024's caption got the PA-033 foreign-court string). Gate + bail.
    is_pa033 = ("and_with_the" in out and "registration_only_or" in out)
    if not is_pa033:
        return out, changes

    # PA-033 — split mailing/physical addresses (3-line and 2-line)
    pl_addr_full = plaintiff.get("address", "")
    def_addr_full = defendant.get("address", "")
    pl_city = plaintiff.get("city", court.get("location", "Portland"))
    pl_state = plaintiff.get("state", "ME")
    pl_zip = plaintiff.get("zip", "")
    df_city = defendant.get("city", court.get("location", "Portland"))
    df_state = defendant.get("state", "ME")
    df_zip = defendant.get("zip", "")

    # PA-033 address widgets are ~40-char narrow (surfaced by the Qwen
    # edge-case probe: long addresses truncate all 4). Width-fit the
    # street + city lines via postal abbreviation before they're written.
    from ..text_fit import fit as _fit
    PA033_ADDR_CHARS = 42

    # Build canonical 3-line address: street / city, state zip / (blank or PO)
    def _split3(street: str, city: str, state: str, zipc: str
                 ) -> tuple[str, str, str]:
        street = _fit(street, PA033_ADDR_CHARS, address=True)
        line2 = _fit(f"{city}, {state} {zipc}".strip(", "),
                     PA033_ADDR_CHARS, address=True)
        return (street, line2, "")

    pl1, pl2, pl3 = _split3(pl_addr_full, pl_city, pl_state, pl_zip)
    df1, df2, df3 = _split3(def_addr_full, df_city, df_state, df_zip)
    # PA-033 layout has TWO address columns (mailing + physical) per
    # party, but build_kv_map's `narrative_derived` pass blindly stamps
    # `physical_address_*` with the respondent's address. Force-overwrite
    # to the correct per-block party so plaintiff's block holds plaintiff
    # data and defendant's block holds defendant data.
    pa033_addr = [
        ("mailing_address_1",   pl1),
        ("mailing_address_2",   pl2),
        ("mailing_address_3",   pl3),
        ("physical_address_1",  pl1),
        ("physical_address_2",  pl2),
        ("mailing_address_1_2", df1),
        ("mailing_address_2_2", df2),
        ("mailing_address_3_2", df3),
        ("physical_address_1_2", df1),
        ("physical_address_2_2", df2),
    ]
    for fid, val in pa033_addr:
        if not val or fid not in out:
            continue
        if is_pa033:
            if out.get(fid) != val:
                out[fid] = val
                changes.append((fid, val, "pa-addr-force"))
        else:
            if _set(out, fid, val):
                changes.append((fid, val, "pa-addr"))

    # PA-033 — foreign protection order originating state
    foreign_state = facts.get("pa033_foreign_state", "New Hampshire")
    if _set(out, "defendantrespondent_in_a_protection_order_case_from_name_of_state",
            foreign_state):
        changes.append((
            "defendantrespondent_in_a_protection_order_case_from_name_of_state",
            foreign_state, "pa033-foreign-state"))
    # `undefined` widget on p0 y=288 holds the supplemental originating-court line
    foreign_court = facts.get("pa033_foreign_court",
                                  "Rockingham County Superior Court")
    if _set(out, "undefined", foreign_court):
        changes.append(("undefined", foreign_court, "pa033-foreign-court"))

    # PA-033 — attachment + filing checkboxes (both default-checked).
    # Schema retains the FULL untruncated widget name for the attachment
    # affirmation; legacy script used a truncated `_any_` variant that
    # didn't match. Keep both for older schemas that did truncate.
    for fid in (
        "a_copy_of_the_foreign_protection_order_to_be_registered_including_any_modification_of_the_order_as_well_as_an",
        "a_copy_of_the_foreign_protection_order_to_be_registered_including_any_",
        "and_that_it_be_placed_on_file_with_this_court",
    ):
        if _set(out, fid, "X"):
            changes.append((fid, "X", "pa033-attach"))

    # PA-033 — local enforcement department on "and with the ___ Police/Sheriff"
    pol_dept = facts.get("pa033_local_agency",
                            f"{court.get('location','Portland')} "
                            f"Police Department")
    if _set(out, "and_with_the", pol_dept):
        changes.append(("and_with_the", pol_dept, "pa033-local-dept"))

    # PA-033 — registration vs enforcement choice (both checked by default
    # — petitioner typically seeks BOTH registration and active enforcement)
    pa033_mode = facts.get("pa033_mode", "both")  # registration|enforcement|both
    if pa033_mode in ("registration", "both"):
        if _set(out, "registration_only_or", "X"):
            changes.append(("registration_only_or", "X", "pa033-reg"))
    if pa033_mode in ("enforcement", "both"):
        if _set(out, "enforcement", "X"):
            changes.append(("enforcement", "X", "pa033-enf"))

    # PA-033 — perjury checkbox (page 2). Schema retains full untruncated
    # widget name; the system-wide notary pass uses `_these` variants but
    # PA-033's exact suffix is `_these_statements`.
    for fid in (
        "i_swear_under_penalty_of_perjury_that_the_above_statements_are_true_and_correct_i_understand_that_these_statements",
        "i_swear_under_penalty_of_perjury_that_the_above_statements_are_true_an",
    ):
        if _set(out, fid, "X"):
            changes.append((fid, "X", "pa033-perjury"))

    # PA-033 — signature block (page 2): date + plaintiff/defendant caption
    # duplicates + attorney block + petitioner contact block.
    sig_date_us = _iso_to_us(case.get("filing_date")
                                or case.get("event_date", ""))
    if _set(out, "date_mmddyyyy", sig_date_us):
        changes.append(("date_mmddyyyy", sig_date_us, "pa033-sigdate"))
    # `undefined_2` is a left-half date echo at p1 y=292 — set to same date
    if _set(out, "undefined_2", sig_date_us):
        changes.append(("undefined_2", sig_date_us, "pa033-sigdate-echo"))
    # page-2 plaintiff/defendant caption duplicates
    if plaintiff.get("full_name"):
        if _set(out, "plaintiffpetitioner_2", plaintiff["full_name"]):
            changes.append(("plaintiffpetitioner_2",
                              plaintiff["full_name"], "pa033-pl2"))
    # Attorney block (LEFT col p1) + petitioner contact (RIGHT col p1)
    # PA-033 has TWO parallel contact columns. build_kv_map pre-stamps
    # address_1/2/3 (left) with the plaintiff address from its narrative
    # heuristic, and address_1_2 (right) with the defendant address.
    # Force-overwrite both columns to the correct identities.
    pl_email = plaintiff.get("email", "")
    pl_phone = plaintiff.get("phone", "")
    pl_city_state_zip = f"{pl_city}, {pl_state} {pl_zip}".strip(", ")

    def _force(fid: str, val: str, src: str) -> None:
        if fid in out and out.get(fid) != val:
            out[fid] = val
            changes.append((fid, val, src))
        elif fid in out and not out.get(fid) and val:
            out[fid] = val
            changes.append((fid, val, src))

    if attorney.get("full_name"):
        # Left column = attorney
        atty_addr = attorney.get("address", pl_addr_full)
        atty_csz = attorney.get("address_2", pl_city_state_zip)
        _force("attorney", attorney["full_name"], "pa033-atty")
        _force("address_1", atty_addr, "pa033-atty-addr")
        _force("address_2", atty_csz, "pa033-atty-csz")
        _force("address_3", "", "pa033-atty-addr3")
        _force("telephone", attorney.get("phone", pl_phone), "pa033-atty-phone")
        _force("email", attorney.get("email", pl_email), "pa033-atty-email")
    else:
        # Pro-se: clear left attorney column entirely so it doesn't show
        # stale duplicate data from build_kv_map's narrative pass.
        for fid in ("attorney", "address_1", "address_2", "address_3",
                     "telephone", "email"):
            if fid in out and out.get(fid):
                out[fid] = ""
                changes.append((fid, "", "pa033-pro-se-clear"))

    # Right column (petitioner contact — always filled with plaintiff data)
    _force("name", plaintiff.get("full_name", ""), "pa033-self-name")
    _force("address_1_2", pl_addr_full, "pa033-self-addr1")
    _force("address_2_2", pl_city_state_zip, "pa033-self-csz")
    _force("telephone_2", pl_phone, "pa033-self-phone")
    _force("email_2", pl_email, "pa033-self-email")

    return out, changes


if __name__ == "__main__":
    print("Use via fill_and_audit.py RECIPE3 dispatch")
    sys.exit(0)
