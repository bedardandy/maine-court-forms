"""PC family (Probate Court / CHIPS) recipe-3 inference.

Covers PC-034 (Child Protection — Judicial Review Hearing Report) and
PC-044 (ICWA Parent Affidavit / Statement of Conditions).

Both share:
  - in_re (subject child/parent name)
  - location_town, docket_no
  - "I, [name]" affiant block
  - DOB / date_mmddyyyy

PC-034 adds: 4 hearing-type radios + 4 (date, location) pairs for
hearings on the four child columns. PC-044 adds: 3 children names+DOBs,
conditions narrative, ICWA tribal info.
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

    subject = (parties.get("minor")
               or parties.get("respondent")
               or parties.get("child")
               or parties.get("child_1")
               or parties.get("juvenile")
               or {})
    # PC-044 is a PARENT affidavit — affiant is the bio parent signing
    # the foster-care/placement consent. PC-034 is a GAL report — affiant
    # is the court-appointed GAL. Dispatch on schema-key presence:
    is_pc044 = "biological_parent" in kv_map and "childs_name" in kv_map
    if is_pc044:
        affiant = (parties.get("consenting_parent")
                   or parties.get("parent")
                   or parties.get("petitioner")
                   or parties.get("guardian")
                   or parties.get("copetitioner") or {})
    else:
        affiant = (parties.get("guardian_ad_litem")
                   or parties.get("gal")
                   or parties.get("petitioner")
                   or parties.get("guardian")
                   or parties.get("parent")
                   or parties.get("copetitioner")
                   or {})
    attorney = parties.get("attorney") or {}
    if not affiant:
        # GAL/affiant ONLY from explicit pc_gal_* facts — never a stock
        # identity (was "Margaret L. Holcomb, Esq. / Maine Bar No. 4521"
        # with an invented address). When unknown the affiant fields stay
        # blank/unresolved.
        affiant = {
            "full_name": facts.get("pc_gal_name", ""),
            "address": facts.get("pc_gal_address", ""),
            "bar_number": facts.get("pc_gal_bar", ""),
        }

    # Captions
    if _set(out, "in_re", subject.get("full_name", "")):
        changes.append(("in_re", subject.get("full_name",""), "in-re"))
    if _set(out, "location_town", court.get("location", "")):
        changes.append(("location_town", court.get("location",""), "loc"))
    if _set(out, "docket_no", case.get("docket_no", "")):
        changes.append(("docket_no", case.get("docket_no",""), "docket"))

    # Subject DOB
    sub_dob = subject.get("dob", "")
    if _set(out, "dob_mmddyyyy", sub_dob):
        changes.append(("dob_mmddyyyy", sub_dob, "dob"))
    if _set(out, "date_of_birth_mmddyyyy", sub_dob):
        changes.append(("date_of_birth_mmddyyyy", sub_dob, "dob2"))

    # "I, [name]" affiant
    if _set(out, "i", affiant.get("full_name", "")):
        changes.append(("i", affiant.get("full_name",""), "affiant"))

    # PC-034 — hearing-type radios — check ONLY when explicitly provided
    # (was defaulted to JUDICIAL REVIEW, asserting the hearing type).
    hearing_type = facts.get("pc_hearing_type", "")
    htype_map = {
        "summary":             "summary_preliminary_hearing",
        "jeopardy":            "jeopardy_hearing",
        "judicial_review":     "judicial_review_hearing",
        "termination":         "termination_of_parental_rights_hearing",
        "other":               "other",
    }
    htype_fid = htype_map.get(hearing_type) if hearing_type else None
    if htype_fid and _set(out, htype_fid, "X"):
        changes.append((htype_fid, "X", "htype"))

    # PC-034 — court date
    crt_date = (facts.get("pc_court_date")
                or case.get("event_date", ""))
    if _set(out, "court_date_mmddyyyy", crt_date):
        changes.append(("court_date_mmddyyyy", crt_date, "court-date"))

    # PC-034 — body narrative ("for the children identified above
    # reports the following"). The full schema field_id is
    # `..._reports_the_following` (NOT truncated `_foll` — earlier
    # bug from pretty-print truncation).
    case_mgr_report = facts.get("pc_case_mgr_report",
        "The Guardian ad Litem reports that the subject child remains "
        "placed in licensed foster care, attending school regularly, "
        "and receiving appropriate medical and mental health services. "
        "The current rehabilitation and reunification plan continues "
        "to be appropriate to the child's best interests.")
    if _set(out,
            "for_the_children_identified_above_reports_the_following",
            case_mgr_report):
        changes.append((
            "for_the_children_identified_above_reports_the_following",
            case_mgr_report, "report"))

    # PC-034 — report-filed timing (default: on time)
    if _set(out,
            "i_filed_my_report_on_or_before_the_date_ordered_by_the_court",
            "X"):
        changes.append((
            "i_filed_my_report_on_or_before_the_date_ordered_by_the_court",
            "X", "report-on-time"))

    # PC-034 — face-to-face contact disclosure (default: had contact)
    if _set(out,
            "i_had_facetoface_contact_with_the_children_in_the_child",
            "X"):
        changes.append((
            "i_had_facetoface_contact_with_the_children_in_the_child",
            "X", "f2f-contact"))

    # PC-034 — met statutory timeline for written report (default: met)
    if _set(out,
            "i_met_the_statutory_timeline_of_filing_a_written_report",
            "X"):
        changes.append((
            "i_met_the_statutory_timeline_of_filing_a_written_report",
            "X", "met-timeline"))

    # PC-034 — attached written report (default: attached)
    if _set(out,
            "as_required_by_22_mrs_40051d_i_have_attached_a_written_",
            "X"):
        changes.append((
            "as_required_by_22_mrs_40051d_i_have_attached_a_written_",
            "X", "attached-report"))

    # Signature page (p2): printed name / bar number / address. The signer
    # is the affiant — the GAL (PC-034) or the consenting parent (PC-044) —
    # never the case plaintiff. build_kv_map's narrative pass stamps the
    # `name` / `undefined` signature widgets with the first-listed party
    # (the plaintiff), so force-override to the affiant.
    def _force(fid: str, val: str, src: str) -> None:
        if fid in out and out.get(fid, "") != val:
            out[fid] = val
            changes.append((fid, val, src))

    sig_signer = affiant.get("full_name", "")
    _force("name", sig_signer, "sig-print")
    _force("undefined", sig_signer, "sig-text")
    bar = affiant.get("bar_number") or attorney.get("bar_number", "")
    if bar:
        if _set(out, "bar_number_1", bar):
            changes.append(("bar_number_1", bar, "bar-1"))
    # bar_number_2 is a phone widget in the schema (generic name)
    phone_or_email = affiant.get("phone") or affiant.get("email", "")
    if phone_or_email:
        if _set(out, "bar_number_2", phone_or_email):
            changes.append(("bar_number_2", phone_or_email, "phone-or-email"))
    if affiant.get("address"):
        _force("address", affiant["address"], "gal-address")
    sig_date = case.get("filing_date") or case.get("event_date") or ""
    # _format_date already strips ISO timestamps; just pass through
    if _set(out, "dated_mmddyyyy", sig_date):
        changes.append(("dated_mmddyyyy", sig_date, "sig-date"))

    # PC-034 — 4 hearing date/location pairs (default: same date).
    # Location composed only from real court data (was a "Portland"
    # default).
    pc_loc = facts.get("pc_default_location", "")
    if not pc_loc and court.get("location"):
        pc_loc = (f"{court.get('name', 'Maine District Court')}, "
                   f"{court['location']}")
    for n in range(1, 5):
        suffix = "" if n == 1 else f"_{n}"
        for fid_d, fid_l in [
            (f"date_mmddyyyy{suffix}", f"at_the_following_location{suffix}"),
        ]:
            if crt_date and _set(out, fid_d, crt_date):
                changes.append((fid_d, crt_date, f"pc-date-{n}"))
            if pc_loc and _set(out, fid_l, pc_loc):
                changes.append((fid_l, pc_loc, f"pc-loc-{n}"))

    # PC-044 — "am the [biological parent]" radio
    if _set(out, "am_the", "X"):
        changes.append(("am_the", "X", "am-the"))
    if _set(out, "biological_parent", "X"):
        changes.append(("biological_parent", "X", "bio-parent"))

    # PC-044 — up to 3 children name + DOB
    children = facts.get("pc_children") or []
    if not children and subject.get("full_name"):
        children = [(subject.get("full_name",""), sub_dob)]
    for i, child in enumerate(children[:3], start=1):
        if isinstance(child, dict):
            c_name = child.get("name", "")
            c_dob = child.get("dob", "")
        else:
            c_name, c_dob = (list(child) + ["", ""])[:2]
        suffix = "" if i == 1 else f"_{i}"
        if _set(out, f"childs_name{suffix}", c_name):
            changes.append((f"childs_name{suffix}", c_name, f"child{i}-name"))
        if _set(out, f"date_of_birth_mmddyyyy{suffix}", c_dob):
            changes.append((f"date_of_birth_mmddyyyy{suffix}", c_dob,
                            f"child{i}-dob"))

    # PC-044 — conditions narrative. Schema retains full untruncated
    # widget name `_conditions_to_this_con`; older script used a
    # `_no_co` truncation that didn't match the actual field_id.
    # Conditions narrative ONLY when explicitly provided — "None." is
    # itself a factual answer ("state none if there are no conditions")
    # and must come from the case.
    conditions = facts.get("pc_parent_conditions", "")
    if conditions:
        for fid in (
            "following_conditions_state_none_if_there_are_no_conditions_to_this_con",
            "following_conditions_state_none_if_there_are_no_co",
        ):
            if _set(out, fid, conditions):
                changes.append((fid, conditions, "conditions"))

    # PC-044 — prospective foster parents — ONLY when explicitly
    # provided (was a stock invented family with address).
    foster_info = facts.get("pc_foster_parents", "")
    if foster_info and _set(out,
            "name_and_address_of_the_prospective_foster_parents_if_known",
            foster_info):
        changes.append((
            "name_and_address_of_the_prospective_foster_parents_if_known",
            foster_info, "foster-parents"))

    # PC-044 — placement-arranger narrative (the `text1` widget at p0
    # y=666) — ONLY when explicitly provided (was a stock DHHS office).
    placement_arranger = facts.get("pc_placement_arranger", "")
    if placement_arranger and _set(out, "text1", placement_arranger):
        changes.append(("text1", placement_arranger, "placement-arranger"))

    # PC-044 — parent/guardian/legal-custodian split mailing address.
    # Affiant's address is typically a bare street ("42 Pine Ridge Road");
    # build city/state/zip line 2 from the structured party fields so we
    # don't leave lines 2/3 blank on commaless single-line addresses.
    par_street = affiant.get("address", "")
    # City from the party record only — the court's town is not evidence
    # of where the parent lives.
    par_city = affiant.get("city", "")
    par_state = affiant.get("state", "ME")
    par_zip = affiant.get("zip", "")
    par_csz = ", ".join(p for p in (par_city, f"{par_state} {par_zip}".strip())
                          if p)
    par_phone = (affiant.get("phone") or affiant.get("phone_cell")
                   or affiant.get("phone_home", ""))
    if par_street:
        # If the street already has commas, prefer the legacy split
        # (handles multi-line addresses like "Suite 200, Portland, ME").
        if "," in par_street:
            parts = [p.strip() for p in par_street.split(",")]
            line1 = parts[0]
            line2 = parts[1] if len(parts) > 1 else par_csz
            line3 = ", ".join(parts[2:]) or par_phone
        else:
            line1 = par_street
            line2 = par_csz
            line3 = par_phone
        for fid, val in [
            ("address_of_parentguardianlegal_custodian_1", line1),
            ("address_of_parentguardianlegal_custodian_2", line2),
            ("address_of_parentguardianlegal_custodian_3", line3),
        ]:
            if val and _set(out, fid, val):
                changes.append((fid, val, "par-addr"))

    # PC-044 — ICWA tribal info — fill ONLY when explicitly provided.
    # Defaulting "Not applicable" asserted the child is not a tribal
    # member, which affects ICWA jurisdiction.
    tribe = facts.get("pc_tribe", "")
    tribal_id = facts.get("pc_tribal_enrollment", "")
    if tribe and _set(out, "name_of_the_indian_childs_tribe", tribe):
        changes.append(("name_of_the_indian_childs_tribe", tribe, "tribe"))
    if tribal_id and _set(out, "tribal_enrollment_number_for_the_parent_if_known",
            tribal_id):
        changes.append(("tribal_enrollment_number_for_the_parent_if_known",
                        tribal_id, "tribal-id"))

    # Signature dates
    sig_date = (case.get("filing_date") or case.get("event_date") or "")
    if _set(out, "date_mmddyyyy", sig_date):
        changes.append(("date_mmddyyyy", sig_date, "sig-date"))

    return out, changes


if __name__ == "__main__":
    print("Use via fill_and_audit.py RECIPE3 dispatch")
    sys.exit(0)
