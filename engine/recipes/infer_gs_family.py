"""GS family recipe-3 inference.

Covers GS-012 (Consent / Objection / Nomination to Guardian).
Reads case.parties.minor (or incapacitated_person) for the ward, and
case.parties.petitioner / copetitioner for the consenter/nominee, with
case.facts.gs_* overrides.
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

    ward = (parties.get("minor") or parties.get("incapacitated_person")
             or parties.get("respondent") or parties.get("child_1") or {})
    consenter = (parties.get("petitioner") or parties.get("copetitioner")
                 or parties.get("nominee") or parties.get("plaintiff") or {})
    alt = (parties.get("copetitioner") or parties.get("alternative_guardian")
           or parties.get("attorney") or {})

    docket = case.get("docket_no") or facts.get("docket_no", "")
    location = court.get("location", "")

    # Header. The field_id `docket_no_2` sits at DIFFERENT caption lines per
    # form (offset auto-naming): in GS-012 it is physically the Location line
    # and `undefined_2` is the Docket line; in GS-008/021 `docket_no_2` is the
    # Docket line and a separate `location` widget is the Location line. Wire
    # by form so docket/location don't swap.
    is_gs012 = "consent_to_guardian" in kv_map
    if is_gs012:
        if "docket_no_2" in out:
            out["docket_no_2"] = location
            changes.append(("docket_no_2", location, "loc-gs012"))
        if "undefined_2" in out:
            out["undefined_2"] = docket
            changes.append(("undefined_2", docket, "docket-gs012"))
    else:
        if _set(out, "docket_no_2", docket):
            changes.append(("docket_no_2", docket, "docket"))
        if _set(out, "undefined_2", location):
            changes.append(("undefined_2", location, "location"))

    # Caption — "IN RE: <ward>"
    ward_name = ward.get("full_name", "")
    if _set(out, "in_re", ward_name):
        changes.append(("in_re", ward_name, "in-re"))
    # GS-008 uses `location` for the caption town (not undefined_2)
    if _set(out, "location", location):
        changes.append(("location", location, "loc-gs008"))

    # GS-008 — movant/parent name ("My name is:")
    movant_name = (consenter.get("full_name")
                    or (parties.get("parent") or {}).get("full_name", ""))
    if _set(out, "my_name_is", movant_name):
        changes.append(("my_name_is", movant_name, "gs008-movant"))
    # GS-008 — guardianship duration + signer contact block
    if "guardian_of_minor_on_an_emergency_basis" in kv_map:
        # Default: standard (non-emergency) guardianship until majority
        duration = facts.get("gs008_duration", "until_majority")
        dur_map = {
            "emergency": "no_more_than_90_days_guardianship_on_an_emergency_basis",
            "interim":   "no_more_than_six_6_months_or_pending_the_courts_final_order_unless_agreed_to_by_the",
            "until_majority": "until_the_minor_child_reaches_majority_or_as_otherwise_specified_in_the_order_appointing",
        }
        type_map = {
            "emergency": "guardian_of_minor_on_an_emergency_basis",
            "interim":   "guardian_of_a_minor_on_an_interim_basis",
            "until_majority": "guardian_of_minor",
        }
        for fid in (type_map.get(duration, "guardian_of_minor"),
                     dur_map.get(duration, dur_map["until_majority"])):
            if _set(out, fid, "X"):
                changes.append((fid, "X", "gs008-duration"))
        # Signer contact block (name_1 = signer, address, name_2, phone, email).
        # build_kv_map's narrative pass stamps these with the wrong party (the
        # defendant), so force-overwrite to the signer/consenter.
        def _force(fid, val, src):
            if fid in out and val and out.get(fid) != val:
                out[fid] = val
                changes.append((fid, val, src))
        c_addr = consenter.get("address") or consenter.get("mailing_address", "")
        c_csz = f"{consenter.get('city','')}, {consenter.get('state','ME')} {consenter.get('zip','')}".strip(', ')
        _force("name_1", movant_name, "gs008-name1")
        _force("name_2", movant_name, "gs008-name2")
        _force("address", ", ".join(p for p in (c_addr, c_csz) if p), "gs008-addr")
        _force("phone_number", consenter.get("phone", ""), "gs008-phone")
        _force("email", consenter.get("email", ""), "gs008-email")
        sig_date = case.get("filing_date") or case.get("event_date", "")
        if "-" in str(sig_date):
            y,m,d = str(sig_date)[:10].split("-"); sig_date = f"{m}/{d}/{y}"
        if _set(out, "dated", sig_date):
            changes.append(("dated", sig_date, "gs008-date"))
        if _set(out, "text14", movant_name):
            changes.append(("text14", movant_name, "gs008-signer"))

    # Section radio — default to CONSENT TO GUARDIAN (positive)
    chosen_section = facts.get("gs_section", "consent")  # consent|objection|nomination
    section_map = {
        "consent":    "consent_to_guardian",
        "objection":  "objection_to_guardian",
        "nomination": "nomination_of_guardian",
    }
    sect_fid = section_map.get(chosen_section, "consent_to_guardian")
    if _set(out, sect_fid, "X"):
        changes.append((sect_fid, "X", "section"))

    # Sub-radio — "Consent to the / Object to the [petition]"
    sub_fid = ("consent_to_the" if chosen_section == "consent"
               else "object_to_the")
    if _set(out, sub_fid, "X"):
        changes.append((sub_fid, "X", "sub-section"))

    # Petition-type radio — default: final_appointment
    pet_type = facts.get("gs_petition_type", "final_appointment")
    pet_map = {
        "interim":               "interim",
        "modification":          "petition_for_modification",
        "termination":           "petition_for_termination",
        "removal":               "petition_for_removal",
        "resignation":           "petition_resignation",
        "final_appointment":     "final_appointment_of_the_proposed_guardian",
    }
    pt_fid = pet_map.get(pet_type, "final_appointment_of_the_proposed_guardian")
    if _set(out, pt_fid, "X"):
        changes.append((pt_fid, "X", "petition-type"))
    # _2 duplicate column
    pt_fid2 = pt_fid + "_2"
    if _set(out, pt_fid2, "X"):
        changes.append((pt_fid2, "X", "petition-type-2"))

    # "because" narrative reasons (numbered 1..3)
    reasons = facts.get("gs_reasons", [
        facts.get("reason_for_guardianship",
                  "The proposed guardian is the maternal grandmother who "
                  "has been the minor's primary caregiver for the past "
                  "three years and provides a stable, safe household."),
        ("The minor has lived continuously at the proposed guardian's "
         "residence and is enrolled in the local school district."),
        ("Both biological parents are presently unable to provide care "
         "and have signed written consent to the guardianship."),
    ])
    if isinstance(reasons, str):
        reasons = [reasons, "", ""]
    for i, r in enumerate(reasons[:3], start=1):
        if r and _set(out, f"because_{i}", r):
            changes.append((f"because_{i}", r, f"reason-{i}"))

    # "Request different person" narrative (only fill if section==nomination)
    if chosen_section == "nomination":
        nominee_reason = facts.get(
            "gs_nominee_reason",
            "I respectfully request that the Court appoint the alternative "
            "guardian named below, who is willing and able to serve and "
            "is more familiar with the minor's day-to-day needs."
        )
        if _set(out, "request_that_the_court_appoint_a_different_perso",
                nominee_reason):
            changes.append(("request_that_the_court_appoint_a_different_perso",
                            nominee_reason, "request-different"))

    # Consenter / signer identity block
    if consenter.get("full_name"):
        if _set(out, "name", consenter["full_name"]):
            changes.append(("name", consenter["full_name"], "consenter-name"))
    if consenter.get("address"):
        if _set(out, "mailing_address", consenter["address"]):
            changes.append(("mailing_address", consenter["address"], "mail"))
        if _set(out, "physical_address", consenter["address"]):
            changes.append(("physical_address", consenter["address"], "phys"))
    if consenter.get("dob"):
        if _set(out, "date_of_birth", consenter["dob"]):
            changes.append(("date_of_birth", consenter["dob"], "dob"))
    if consenter.get("phone"):
        if _set(out, "telephone", consenter["phone"]):
            changes.append(("telephone", consenter["phone"], "phone"))

    # Dated — filing date
    dated = case.get("filing_date") or case.get("event_date", "")
    if _set(out, "dated", dated):
        changes.append(("dated", dated, "dated"))

    # Alternative-guardian / attorney-for-minor block (GS-012 only — on GS-008
    # `name_2` is the signer, set above). Force-overwrite: build_kv_map stamps
    # the defendant's name here, and fill-if-empty left it.
    def _force2(fid, val, src):
        if fid in out and val and out.get(fid) != val:
            out[fid] = val
            changes.append((fid, val, src))
    if is_gs012:
        if alt.get("full_name"):
            _force2("name_2", alt["full_name"], "alt-name")
        if alt.get("address"):
            _force2("undefined_3", alt["address"], "alt-addr2")
        if alt.get("phone"):
            _force2("telephone_2", alt["phone"], "alt-phone")

    # GS-021 — minor's own consent (interim/final + tribal info + 1_i)
    if _set(out, "location", location):
        changes.append(("location", location, "gs21-location"))
    if _set(out, "1_i", consenter.get("full_name", "")):
        changes.append(("1_i", consenter.get("full_name",""), "gs21-1i"))

    pet_kind = facts.get("gs_petition_kind", "final")  # interim|final
    if pet_kind == "interim":
        if _set(out, "interim", "X"):
            changes.append(("interim", "X", "gs21-interim"))
    else:
        if _set(out, "final", "X"):
            changes.append(("final", "X", "gs21-final"))
        if _set(out, "final_appointment_of_the_proposed_guardian_and_sta", "X"):
            changes.append(("final_appointment_of_the_proposed_guardian_and_sta",
                            "X", "gs21-final-narr"))

    # Minor name + birthdate
    ward_dob = ward.get("dob", "")
    if ward_name and ward_dob:
        minor_block = f"{ward_name} (DOB {ward_dob})"
        if _set(out, "name_and_birthdate_of_the_minor_child", minor_block):
            changes.append(("name_and_birthdate_of_the_minor_child",
                            minor_block, "gs21-minor"))

    # Tribal info (default: not applicable)
    tribe = facts.get("gs_minor_tribe", "Not applicable")
    tribal_enroll = facts.get("gs_minor_tribal_enrollment", "N/A")
    if _set(out, "name_of_minor_childs_tribe_and_childs_enrollment_n", tribe):
        changes.append(("name_of_minor_childs_tribe_and_childs_enrollment_n",
                        tribe, "gs21-tribe"))
    if _set(out, "my_tribal_enrollment_number", tribal_enroll):
        changes.append(("my_tribal_enrollment_number", tribal_enroll,
                        "gs21-tribal-id"))

    # Consenter's split address ("my_address_1" / "my_address_2")
    consent_addr = consenter.get("address", "")
    if consent_addr:
        parts = [p.strip() for p in consent_addr.split(",")]
        line1 = parts[0]
        line2 = ", ".join(parts[1:])
        if _set(out, "my_address_1", line1):
            changes.append(("my_address_1", line1, "gs21-addr1"))
        if _set(out, "my_address_2", line2):
            changes.append(("my_address_2", line2, "gs21-addr2"))

    # Understanding-of-guardianship affirmation
    understand = ("I understand the nature of a minor guardianship and I "
                  "consent to the proposed guardian's appointment.")
    if _set(out, "i_understand_the_nature_of_a_minor_guardianship_an",
            understand):
        changes.append(("i_understand_the_nature_of_a_minor_guardianship_an",
                        understand, "gs21-understand"))

    return out, changes


if __name__ == "__main__":
    print("Use via fill_and_audit.py RECIPE3 dispatch")
    sys.exit(0)
