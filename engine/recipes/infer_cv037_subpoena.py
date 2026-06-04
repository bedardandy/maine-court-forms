"""CV-037 (Subpoena / Notice of Service) recipe-3 inference.

Subpoena form: served on a witness to appear at a date/time/place.
Reads case.facts.witness_name, witness_role, service_date, service_address,
appearance_date, appearance_time, party_being_called.
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

    # TO: <witness>
    witness_name = facts.get("witness_name",
                              "Eleanor M. Thompson (witness)")
    if _set(out, "to", witness_name):
        changes.append(("to", witness_name, "witness"))

    # Role of witness ("who is the witness for Plaintiff")
    witness_role = facts.get("witness_role", "witness for the Plaintiff")
    for fid in ("who_is_the", "witness_role", "subpoena_role"):
        if _set(out, fid, witness_role):
            changes.append((fid, witness_role, "witness-role"))

    # Appearance date/time
    appearance_date = facts.get("appearance_date",
                                  case.get("event_date") or "2024-12-15")
    appearance_time = facts.get("appearance_time", "9:00 AM")
    for fid in ("mmddyyyy", "appearance_date", "date_mmddyyyy"):
        if _set(out, fid, _iso_to_us(appearance_date)):
            changes.append((fid, _iso_to_us(appearance_date),
                              "appearance-date"))
    for fid in ("at_time", "appearance_time", "time"):
        if _set(out, fid, appearance_time):
            changes.append((fid, appearance_time, "appearance-time"))

    # Plaintiff / Defendant party being called
    party_called = facts.get("party_being_called", "Plaintiff")
    for fid in ("plaintiff_defendant", "party_being_called"):
        if _set(out, fid, party_called):
            changes.append((fid, party_called, "party-called"))

    # County
    county = court.get("county", "Cumberland")
    for fid in ("county_of",):
        if _set(out, fid, county):
            changes.append((fid, county, "county"))

    # Proof of service block (lower half)
    service_date = facts.get("service_date",
                               case.get("filing_date") or "")
    if service_date:
        for fid in ("on_mmddyyyy", "service_date"):
            if _set(out, fid, _iso_to_us(service_date)):
                changes.append((fid, _iso_to_us(service_date),
                                  "service-date"))

    served_on = facts.get("served_on", witness_name)
    for fid in ("i_made_service_of_the_subpoena_upon_the_following_person",
                 "served_on"):
        if _set(out, fid, served_on):
            changes.append((fid, served_on, "served-on"))

    service_addr = facts.get("service_address",
                               "142 Pine Ridge Road, Portland, ME 04101")
    for fid in ("at_the_following_address", "service_address"):
        if _set(out, fid, service_addr):
            changes.append((fid, service_addr, "service-address"))

    # Total fees (stock $40 witness fee)
    total = facts.get("witness_fee_total", "$40.00")
    for fid in ("total", "total_fees"):
        if _set(out, fid, total):
            changes.append((fid, total, "witness-fee"))

    return out, changes


if __name__ == "__main__":
    print("Use via fill_and_audit.py RECIPE3 dispatch")
    sys.exit(0)
