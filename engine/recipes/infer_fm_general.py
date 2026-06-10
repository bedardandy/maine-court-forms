"""FM general family recipe-3 inference.

Covers FM-057, FM-214, FM-056, FM-071, FM-188 and other FM forms that
share: plaintiff/defendant captions, "I am the [petitioner/defendant]"
self-identification, "other party resides in town/county", paragraph-N
checkbox patterns, "objection to magistrate's order" narrative,
"type of action" + "property or credits" + plaintiff address.

Reads case.parties.plaintiff/defendant + case.facts.fm_*.
"""
from __future__ import annotations

import sys


def _iso_to_us(iso: str) -> str:
    if not iso or "-" not in iso: return iso
    y, m, d = iso[:10].split("-")
    return f"{m}/{d}/{y}"


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

    plaintiff = (parties.get("plaintiff") or parties.get("petitioner") or {})
    defendant = (parties.get("defendant") or parties.get("respondent") or {})

    # Self-identification: "I am the [petitioner / defendant]" — write
    # ONLY when explicitly provided (was defaulted to "petitioner",
    # asserting which party the filer is).
    self_role = facts.get("fm_self_role", "")  # petitioner|defendant
    if self_role:
        for fid in ("i_am_the_petitioner_defendant_in_this_case",
                     "i_am_the_plaintiff_defendant_in_the_above"):
            if _set(out, fid, self_role):
                changes.append((fid, self_role, "self-role"))

    # Other-party residence (town/county) — real data only (the old
    # defaults invented "Saco" / "Cumberland").
    other = (plaintiff if self_role.lower() == "defendant" else defendant)
    other_town = other.get("city", facts.get("other_party_town", ""))
    other_county = court.get("county", "")
    if other_town and other_county:
        for fid in ("the_other_party_now_resides_in_town_county",
                     "other_party_town"):
            if _set(out, fid, f"{other_town}, {other_county} County"):
                changes.append((fid, other_town, "other-residence"))
    if other_town:
        for fid in ("other_party_town_only",):
            if _set(out, fid, other_town):
                changes.append((fid, other_town, "other-town"))

    # Paragraph 3 checkboxes — select ONLY when explicitly provided (the
    # old default picked "A", choosing relief on the filer's behalf).
    para3 = facts.get("fm_paragraph3_choice", "")
    if para3:
        for fid in ("paragraph_3_checkboxes_a_b_c_d_e",
                     "paragraph_3_a", "paragraph_3"):
            if _set(out, fid, para3):
                changes.append((fid, para3, "para3"))

    # Magistrate-order objection narrative (FM-071) — the objection, the
    # requested modification, and the request are the substance of the
    # filing. Fill ONLY when explicitly provided (the old defaults
    # invented a child-support/income objection).
    objection = facts.get("magistrate_objection", "")
    if objection:
        for fid in (
            "defendant_in_the_above_captioned_matter_i_object_to_the_entry_of_the_magistrates_final_order",
            "i_object_to_the_entry_of_the_magistrates_final_or",
            "objection_narrative",
        ):
            if _set(out, fid, objection):
                changes.append((fid, objection, "objection"))

    # FM-071: "modify it as follows" narrative + "therefore I request"
    modify = facts.get("magistrate_modify", "")
    if modify and _set(out, "modify_it_as_follows", modify):
        changes.append(("modify_it_as_follows", modify, "modify"))
    request = facts.get("magistrate_request", "")
    if request and _set(out, "therefore_i_request_that_a_judge_1", request):
        changes.append(("therefore_i_request_that_a_judge_1", request,
                        "request"))
    # FM-071 acknowledgment checkboxes — ONLY on an explicit boolean fact
    # (were auto-answered "Yes" on the filer's behalf).
    if facts.get("fm071_acknowledgments") is True:
        for fid in (
            "i_understand_that_to_appeal_a_magistrates_final_order_i_must_file_an_objection_in_the_district_court_within_21_days",
            "i_understand_the_magistrates_order_is_effective_when_signed_and_remains_in_effect_despite_this_objection_until",
        ):
            if _set(out, fid, "Yes"):
                changes.append((fid, "Yes", "fm071-ack"))

    # FM-071 "v." caption widget — holds the defendant name after "v."
    if _set(out, "v", defendant.get("full_name", "")):
        changes.append(("v", defendant.get("full_name",""), "v-caption"))

    # FM-071 "adopted modified or rejected by a Judge" — date the
    # magistrate's order was issued (86-px short widget).
    order_date = (facts.get("fm071_order_date")
                    or case.get("event_date")
                    or case.get("filing_date") or "")
    order_date_us = _iso_to_us(order_date)
    if order_date_us and _set(out, "adopted_modified_or_rejected_by_a_judge",
                                 order_date_us):
        changes.append(("adopted_modified_or_rejected_by_a_judge",
                        order_date_us, "fm071-order-date"))

    # FM-171 — Notice of Name Change (post-divorce). Has divorce-final
    # date + plaintiff/defendant "name when divorce was filed" + name
    # "after divorce" widgets.
    is_fm171 = ("the_divorce_judgment_became_final_on_mmddyyyy" in kv_map
                 and "name_after_divorce" in kv_map)
    if is_fm171:
        fm171_pl_name = plaintiff.get("full_name", "")
        fm171_df_name = defendant.get("full_name", "")
        divorce_date = facts.get("fm171_divorce_final_date",
                                       case.get("filing_date", ""))
        if _set(out, "the_divorce_judgment_became_final_on_mmddyyyy",
                _iso_to_us(divorce_date)):
            changes.append(("the_divorce_judgment_became_final_on_mmddyyyy",
                              _iso_to_us(divorce_date), "fm171-divorce-date"))
        if _set(out, "name_when_divorce_was_filed", fm171_pl_name):
            changes.append(("name_when_divorce_was_filed", fm171_pl_name,
                              "fm171-pl-old"))
        pl_after = facts.get("fm171_plaintiff_name_after_divorce",
                                  plaintiff.get("maiden_name", fm171_pl_name))
        if _set(out, "name_after_divorce", pl_after):
            changes.append(("name_after_divorce", pl_after, "fm171-pl-new"))
        if _set(out, "defendant_name_when_divorce_was_filed", fm171_df_name):
            changes.append(("defendant_name_when_divorce_was_filed",
                              fm171_df_name, "fm171-df-old"))
        df_after = facts.get("fm171_defendant_name_after_divorce",
                                  fm171_df_name)
        if _set(out, "name_after_divorce_2", df_after):
            changes.append(("name_after_divorce_2", df_after, "fm171-df-new"))

    # FM-188: type of action — ONLY when explicitly provided (was a
    # stock divorce description).
    action_type = facts.get("fm_action_type", "")
    if action_type:
        for fid in ("the_type_of_action_is", "type_of_action",
                     "nature_of_action"):
            if _set(out, fid, action_type):
                changes.append((fid, action_type, "action-type"))

    # FM-188: property/credits narrative — schema field_id is the bare
    # `property_or_credits_of_the_defendant` (legacy `_will_not` suffix
    # variant was wrong; widget has no suffix on FM-188). ONLY when
    # explicitly provided — the old default invented a residence,
    # bank accounts, and a vehicle.
    property_text = facts.get("fm_property_credits", "")
    if property_text:
        for fid in ("property_or_credits_of_the_defendant",
                     "property_or_credits_of_the_defendant_will_not",
                     "property_credits_narrative"):
            if _set(out, fid, property_text):
                changes.append((fid, property_text, "property-credits"))

    # FM-188: plaintiff name+address narrative (split 2 lines).
    # Line 1 = full name; line 2 = full mailing address "street, city, ST zip".
    def _full_addr(p: dict) -> str:
        street = p.get("address") or p.get("mailing_address", "")
        city = p.get("city", "")
        state = p.get("state", "")
        zipc = p.get("zip", "")
        tail = ", ".join(x for x in (city, f"{state} {zipc}".strip()) if x)
        return ", ".join(x for x in (street, tail) if x)

    pl_name = plaintiff.get("full_name", "")
    pl_addr = _full_addr(plaintiff)
    df_name = defendant.get("full_name", "")
    df_addr = _full_addr(defendant)
    other = (case.get("parties") or {}).get("other_party") or {}
    other_name = other.get("full_name", "")
    other_addr = _full_addr(other)

    # Split each name/address into two lines (line 1: name, line 2: address)
    for prefix, name_v, addr_v in [
        ("plaintiff", pl_name, pl_addr),
        ("defendant", df_name, df_addr),
        ("other_party", other_name, other_addr),
    ]:
        fid_1 = f"the_name_and_address_of_the_{prefix}_or_attorney_if_known_1"
        fid_2 = f"the_name_and_address_of_the_{prefix}_or_attorney_if_known_2"
        if name_v:
            if _set(out, fid_1, name_v):
                changes.append((fid_1, name_v, f"{prefix}-name"))
            if _set(out, fid_2, addr_v):
                changes.append((fid_2, addr_v, f"{prefix}-addr"))

    # FM-188 "unknown_and_cannot_be_ascertained" (default not checked)
    # leave blank

    # FM-188 "will_not_be_affected" narrative — ONLY when explicitly
    # provided (was a stock property description); "may_be" checkbox
    # gated alongside it.
    affected_narr = facts.get("fm_will_not_be_affected", "")
    if affected_narr:
        if _set(out, "will_not_be_affected_which_include", affected_narr):
            changes.append(("will_not_be_affected_which_include",
                            affected_narr, "not-affected"))
        if _set(out, "may_be", "X"):
            changes.append(("may_be", "X", "may-be"))

    # FM-214 — emergency-order specifics — check ONLY on an explicit
    # boolean fact (was auto-checked, moving for emergency relief on the
    # filer's behalf).
    if (facts.get("fm214_emergency_order") is True
            and _set(out,
            "defendant_in_this_case_and_hereby_moves_this_court_for_an_emergency_order_to_enforce",
            "X")):
        changes.append((
            "defendant_in_this_case_and_hereby_moves_this_court_for_an_emergency_order_to_enforce",
            "X", "emergency"))

    # FM-214 "I now reside in town" split widgets — real data only (the
    # county was previously defaulted to "Cumberland").
    pl_city = plaintiff.get("city", "")
    pl_state = plaintiff.get("state", "ME")
    cur_county = court.get("county", "")
    if _set(out,
            "defendant_in_this_case_and_i_now_reside_in_town",
            pl_city):
        changes.append((
            "defendant_in_this_case_and_i_now_reside_in_town",
            pl_city, "self-town"))
    if _set(out, "town_1", pl_city):
        changes.append(("town_1", pl_city, "town1"))
    if cur_county and _set(out, "county_1", cur_county):
        changes.append(("county_1", cur_county, "county1"))
    if pl_city and _set(out, "state_1", pl_state):
        changes.append(("state_1", pl_state, "state1"))

    # "The other party now resides in town" — real data only
    if other_town and _set(out, "the_other_party_now_resides_in_town",
                             other_town):
        changes.append(("the_other_party_now_resides_in_town", other_town,
                        "other-town-narr"))
    if other_town and _set(out, "town_2", other_town):
        changes.append(("town_2", other_town, "town2"))
    if other_county and _set(out, "county_2", other_county):
        changes.append(("county_2", other_county, "county2"))
    if other_town and _set(out, "state_2", "ME"):
        changes.append(("state_2", "ME", "state2"))

    # FM-214 custody determination block — radio + court ONLY when the
    # case explicitly states a custody determination exists (was
    # auto-checked with a stock "Cumberland County Probate Court").
    custody_court = facts.get("fm_custody_court", "")
    if custody_court:
        if _set(out,
                "i_am_subject_to_a_child_custody_determination_in_name_and_location_of_the_court_that_issued_the_order",
                "X"):
            changes.append((
                "i_am_subject_to_a_child_custody_determination_in_name_and_location_of_the_court_that_issued_the_order",
                "X", "custody-radio"))
        if _set(out, "name_and_location_of_court", custody_court):
            changes.append(("name_and_location_of_court", custody_court,
                            "custody-court"))

    # FM-214 signature date
    sig_date = (case.get("filing_date") or case.get("event_date") or "")
    sig_date_us = _iso_to_us(sig_date)
    if _set(out, "dated", sig_date_us):
        changes.append(("dated", sig_date_us, "dated"))

    # FM-214 — resident-of-Maine radio — check only when the filer's
    # state is actually Maine (was auto-checked for every fill).
    if ((plaintiff.get("state") or "").upper() == "ME"
            and _set(out, "i_am_a_resident_of_the_state_of_maine", "X")):
        changes.append(("i_am_a_resident_of_the_state_of_maine", "X",
                        "fm214-resident"))

    # FM-214 — order more specifically (1+2 line narrative) — ONLY when
    # explicitly provided (the old default invented a visitation-denial
    # narrative).
    order_more = facts.get("fm214_order_more_specifically") or []
    if isinstance(order_more, str):
        order_more = [order_more, ""]
    for i, line in enumerate(order_more[:2], start=1):
        fid = f"order_more_specifically_{i}"
        if line and _set(out, fid, line):
            changes.append((fid, line, f"order-more-{i}"))

    # FM-214 — "I have provided at least two days notice" radio — ONLY
    # on an explicit boolean fact (was auto-checked, certifying notice).
    if (facts.get("fm214_notice_given") is True
            and _set(out, "i_have_provided_at_least_two_days_notice_to_the_custodial_parent_or", "X")):
        changes.append(("i_have_provided_at_least_two_days_notice_to_the_custodial_parent_or",
                        "X", "fm214-notice"))

    # FM-214 — WHEREFORE relief block (1+2 line narrative)
    relief = facts.get("fm214_relief", [
        "Enforce the visitation provisions of the existing Judgment by "
        "directing the defendant to permit the plaintiff make-up weekend "
        "visitation for the two weekends missed, on dates selected by the "
        "plaintiff with reasonable advance notice.",
        "Award the plaintiff reasonable attorney's fees and costs incurred "
        "in bringing this Motion, and grant such other and further relief "
        "as the Court deems just and proper.",
    ])
    if isinstance(relief, str):
        relief = [relief, ""]
    for i, line in enumerate(relief[:2], start=1):
        fid = f"by_granting_the_following_relief_{i}"
        if line and _set(out, fid, line):
            changes.append((fid, line, f"fm214-relief-{i}"))

    # FM-214 / FM-057 / PA — perjury swear radio (always Yes)
    for fid in (
        "i_swear_under_penalty_of_perjury_that_the_above_statements_are_true_and_correct_i_understand_that_these_statements",
        "i_swear_under_penalty_of_perjury_that_the_above_statements_are_true_and_correct_i_understand_that_these",
    ):
        if _set(out, fid, "X"):
            changes.append((fid, "X", "perjury-swear"))

    # FM-057 is dispatched to infer_fm057_keep_info_private (dedicated
    # module — widget-rect map required for confidentiality checkboxes
    # + generic-named text widgets).

    return out, changes


if __name__ == "__main__":
    print("Use via fill_and_audit.py RECIPE3 dispatch")
    sys.exit(0)
