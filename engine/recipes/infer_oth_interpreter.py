"""OTH interpreter-service reimbursement family recipe-3 inference.

Covers OTH-017, OTH-131 — interpreter service reimbursement claim
forms. Vendor + payment address + tier + LEP (Limited English
Proficiency) party info.

Reads case.facts.interpreter_* with sensible defaults.
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

    # Interpreter / vendor info — ONLY when explicitly provided. The old
    # defaults invented a vendor, vendor code, payment address, and
    # certification tier on a reimbursement claim.
    vendor = facts.get("interpreter_vendor", "")
    vendor_code = facts.get("interpreter_vendor_code", "")
    payment_addr = facts.get("interpreter_payment_address", "")
    tier = facts.get("interpreter_tier", "")
    for fid, val in [
        ("services_provided_by", vendor),
        ("vendor_code", vendor_code),
        ("payment_address", payment_addr),
        ("tier", tier),
    ]:
        if val and _set(out, fid, val):
            changes.append((fid, val, "interpreter-meta"))

    # LEP party: usually a non-English-speaking litigant
    lep = (parties.get("petitioner") or parties.get("plaintiff")
            or parties.get("defendant") or parties.get("respondent") or {})
    lep_name = lep.get("full_name", "")
    if lep_name:
        for fid in ("lep_party_name", "lep_party_name_row_1",
                     "limited_english_proficiency_party_name"):
            if _set(out, fid, lep_name):
                changes.append((fid, lep_name, "lep-party"))

    # Service date / hours / amount
    service_date = facts.get("interpreter_service_date",
                                case.get("event_date") or "")
    if service_date:
        for fid in ("service_date_mmddyyyy", "service_date",
                     "date_of_service"):
            if _set(out, fid, _iso_to_us(service_date)):
                changes.append((fid, _iso_to_us(service_date),
                                  "service-date"))

    # Hours / rate / total — billing facts; ONLY when explicitly provided
    # (were 2.5h × $75 defaults).
    hours = facts.get("interpreter_hours", "")
    rate = facts.get("interpreter_rate", "")
    total = facts.get("interpreter_total", "")
    if not total and hours and rate:
        try:
            total = f"{float(hours)*float(rate):,.2f}"
        except ValueError:
            total = ""
    if hours:
        for fid in ("hours", "service_hours"):
            if _set(out, fid, hours):
                changes.append((fid, hours, "hours"))
    if rate:
        for fid in ("hourly_rate", "rate"):
            if _set(out, fid, f"${rate}"):
                changes.append((fid, f"${rate}", "rate"))
    if total:
        for fid in ("total_amount", "total"):
            if _set(out, fid, f"${total}"):
                changes.append((fid, f"${total}", "total"))

    # Language pair — ONLY when explicitly provided (was defaulted to
    # "Spanish ↔ English", asserting the party's language).
    language = facts.get("interpreter_language", "")
    if language:
        for fid in ("language_pair", "language", "languages"):
            if _set(out, fid, language):
                changes.append((fid, language, "language"))

    return out, changes


if __name__ == "__main__":
    print("Use via fill_and_audit.py RECIPE3 dispatch")
    sys.exit(0)
