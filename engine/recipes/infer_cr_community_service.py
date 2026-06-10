"""CR community-service family recipe-3 inference.

Covers CR-198 (Community Service Hours), CR-239 (Drug Court Phase
Tracking). Both are case-tracking forms with participant name + DOB +
hours/days + program info.

Reads case.parties.defendant + case.facts.community_service_* /
drug_court_*.
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

    # Participant: defendant in criminal forms
    participant = (parties.get("defendant") or parties.get("respondent")
                    or parties.get("petitioner") or {})

    name = participant.get("full_name", "")
    if name:
        for fid in ("name", "participant_name", "defendant_name"):
            if _set(out, fid, name):
                changes.append((fid, name, "participant-name"))

    if participant.get("dob"):
        dob_us = _iso_to_us(participant["dob"])
        for fid in ("date_of_birth", "dob", "participants_dob"):
            if _set(out, fid, dob_us):
                changes.append((fid, dob_us, "dob"))

    # CR-198: total community service hours needed — fill ONLY when
    # explicitly provided (was a hardcoded "40"); the hour count is a
    # court-ordered term and must never be invented.
    hours_needed = facts.get("community_service_hours_required", "")
    if hours_needed:
        for fid in ("total_number_of_hours_needed",
                     "hours_required", "hours_needed"):
            if _set(out, fid, hours_needed):
                changes.append((fid, hours_needed, "hours-required"))

    # CR-239 is actually the DRUG COURT TRAVEL REQUEST form, not phase
    # tracking. The participant must request approval to travel and
    # provide a comprehensive itinerary.
    is_cr239 = ("date_i_wish_to_leave" in kv_map
                 and "reason_for_travel" in kv_map)

    # CR-239 / CR-198 — phase tracking still applies (CR-239 has a phase
    # gate to determine if travel is allowed under the program rules).
    # Program status numbers — fill ONLY when explicitly provided (were
    # hardcoded "Phase 3"/"63"/"18"); these are factual treatment-court
    # records and fabricating them misstates the participant's standing.
    phase = facts.get("drug_court_phase", "")
    if phase:
        for fid in ("phase", "drug_court_phase", "current_phase"):
            if _set(out, fid, phase):
                changes.append((fid, phase, "phase"))

    negative_days = facts.get("drug_court_negative_days", "")
    if negative_days:
        for fid in ("documented_negative_testing_days",
                     "negative_testing_days", "clean_days"):
            if _set(out, fid, negative_days):
                changes.append((fid, negative_days, "negative-days"))

    # Hours completed (CR-198, CR-239 status reporting)
    hours_completed = facts.get("community_service_hours_completed", "")
    if hours_completed:
        for fid in ("hours_completed", "hours_to_date"):
            if _set(out, fid, hours_completed):
                changes.append((fid, hours_completed, "hours-completed"))

    # CR-011 — Victim notification list (up to 3 victims). Fill ONLY from
    # facts.victims or explicit victim_* facts. Never invent a stock victim
    # (was "Jane M. Doe, DOB 01/15/1985, 127 Maple Avenue..."): a fabricated
    # victim identity on a notification list is a serious misstatement.
    victims = facts.get("victims") or []
    if (not victims and "names_dobs_and_addresses_of_victims_1" in kv_map
            and facts.get("victim_name")):
        victims = [{
            "full_name": facts.get("victim_name", ""),
            "dob": facts.get("victim_dob", ""),
            "address": facts.get("victim_address", ""),
        }]
    for i, v in enumerate(victims[:3], start=1):
        if isinstance(v, dict):
            parts = [v.get("full_name", "")]
            if v.get("dob"):
                parts.append(f"(DOB {v['dob']})")
            if v.get("address"):
                parts.append(f"— {v['address']}")
            line = " ".join(p for p in parts if p)
        else:
            line = str(v)
        if line and _set(out, f"names_dobs_and_addresses_of_victims_{i}",
                            line):
            changes.append((f"names_dobs_and_addresses_of_victims_{i}",
                              line, f"cr011-victim-{i}"))

    if is_cr239:
        # Filing date echo + travel window
        today_us = _iso_to_us(case.get("filing_date")
                                or case.get("event_date", ""))
        if _set(out, "todays_date", today_us):
            changes.append(("todays_date", today_us, "cr239-today"))
        # Travel window — ONLY when explicitly provided. Do not borrow
        # case.event_date or echo the leave date as the return date; the
        # requested window is the substance of the request.
        leave_us = _iso_to_us(facts.get("travel_leave_date", ""))
        return_us = _iso_to_us(facts.get("travel_return_date", ""))
        if leave_us and _set(out, "date_i_wish_to_leave", leave_us):
            changes.append(("date_i_wish_to_leave", leave_us, "cr239-leave"))
        if return_us and _set(out, "date_i_wish_to_return", return_us):
            changes.append(("date_i_wish_to_return", return_us, "cr239-return"))

        # Travel narrative blanks — fill ONLY when explicitly provided.
        # Never fabricate a travel reason / mode / companions (was a stock
        # birthday-trip narrative with invented family members).
        reason = facts.get("travel_reason", "")
        if reason and _set(out, "reason_for_travel", reason):
            changes.append(("reason_for_travel", reason, "cr239-reason"))
        mode = facts.get("travel_mode", "")
        if mode and _set(out, "mode_of_travel", mode):
            changes.append(("mode_of_travel", mode, "cr239-mode"))
        companions = facts.get("travel_companions", "")
        if companions and _set(out, "traveling_with", companions):
            changes.append(("traveling_with", companions, "cr239-companions"))

        # Participant DOB split: month / day / year (3-col widget set).
        # ONLY when the case provides a DOB (was a hardcoded 1985-06-15).
        dob = participant.get("dob", "")
        if dob and "-" in dob:
            y, m, d = dob[:10].split("-")
            if _set(out, "month", m):
                changes.append(("month", m, "cr239-dob-mo"))
            if _set(out, "day", d):
                changes.append(("day", d, "cr239-dob-day"))
            if _set(out, "year", y):
                changes.append(("year", y, "cr239-dob-yr"))

        # Contact info (two cellphone widgets — one for participant, one
        # alternate emergency contact). ONLY when provided — never invent
        # phone numbers (were hardcoded 555 numbers).
        cell = (participant.get("phone_cell")
                  or participant.get("phone", ""))
        cell_alt = facts.get("travel_alt_contact_phone", "")
        if cell and _set(out, "contact_information_cellphone", cell):
            changes.append(("contact_information_cellphone", cell,
                              "cr239-cell"))
        if cell_alt and _set(out, "contact_information_cellphone_2",
                                cell_alt):
            changes.append(("contact_information_cellphone_2", cell_alt,
                              "cr239-cell-2"))

        # Destination — ONLY when provided (was a hardcoded Kennebunkport
        # address); a wrong destination misstates where the participant
        # will be.
        dest = facts.get("travel_to_address", "")
        dest_csz = facts.get("travel_to_citystate", "")
        if dest and _set(out, "traveling_to_address", dest):
            changes.append(("traveling_to_address", dest, "cr239-dest"))
        if dest_csz and _set(out, "citystate", dest_csz):
            changes.append(("citystate", dest_csz, "cr239-csz"))

        # If driving — vehicle info. ONLY when provided (was a hardcoded
        # Toyota Camry + plate); a wrong vehicle misleads supervision.
        make = facts.get("travel_vehicle_make", "")
        if make and _set(out, "if_driving_make", make):
            changes.append(("if_driving_make", make, "cr239-make"))
        model = facts.get("travel_vehicle_model", "")
        if model and _set(out, "model", model):
            changes.append(("model", model, "cr239-model"))
        tag = facts.get("travel_vehicle_tag", "")
        if tag and _set(out, "tag_number", tag):
            changes.append(("tag_number", tag, "cr239-tag"))

        # Recommendation / approval checkboxes belong to program staff and
        # the court. Check ONLY on an explicit boolean fact — never default
        # to approved (these were auto-checked for every fill).
        approve_map = (("recommend_approval", "cr239_recommend_approval"),
                        ("recommend_approval_2", "cr239_recommend_approval_2"),
                        ("approved", "cr239_approved"))
        for fid, key in approve_map:
            if facts.get(key) is True and _set(out, fid, "X"):
                changes.append((fid, "X", "cr239-approve"))

    return out, changes


if __name__ == "__main__":
    print("Use via fill_and_audit.py RECIPE3 dispatch")
    sys.exit(0)
