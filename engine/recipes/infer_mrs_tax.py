"""MRS (Maine Revenue Services) tax-form family recipe-3 inference.

Covers MRS-700SOV (Statement of Ownership of Vehicle for Use Tax) and
MRS-1099ME (Maine 1099 Information Return). Both have first/last name +
SSN/EIN + address + residency status. Reads case.parties.taxpayer or
defaults to plaintiff.
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

    taxpayer = (parties.get("taxpayer") or parties.get("plaintiff")
                 or parties.get("petitioner") or parties.get("applicant")
                 or parties.get("defendant") or {})

    # Split name into first/middle/last
    full = taxpayer.get("full_name", "")
    parts = full.split() if full else []
    first = parts[0] if parts else "Jane"
    middle = parts[1] if len(parts) >= 3 else ""
    last = parts[-1] if parts else "Doe"

    for fid_target, value, label in [
        # MRS-700SOV: estate-of split
        ("estate_of_first_name", first, "estate-first"),
        ("estate_of_m_i", middle[:1] if middle else "", "estate-mi"),
        ("estate_of_last_name", last, "estate-last"),
        # Generic
        ("first_name", first, "first"),
        ("last_name", last, "last"),
        ("middle_name", middle, "middle"),
        ("middle", middle, "middle"),
        ("first", first, "first"),
        ("last", last, "last"),
        # MRS-1099ME: 1099me_-prefixed
        ("1099me_name", full, "1099me-name"),
        ("name", full, "full-name"),
    ]:
        if _set(out, fid_target, value):
            changes.append((fid_target, value, label))

    # SSN — use case.facts.taxpayer_ssn if present, otherwise placeholder
    ssn = facts.get("taxpayer_ssn", "000-00-0000")
    for fid in ("ssn", "social_security_number", "taxpayer_ssn"):
        if _set(out, fid, ssn):
            changes.append((fid, ssn, "ssn"))

    # Address
    addr = taxpayer.get("address", "")
    if addr:
        for fid in ("address", "mailing_address",
                     "name_address_and_zip_code_member_recipient",
                     "address_first_middle_last",
                     "mailing_address_first_middle_last"):
            if _set(out, fid, addr):
                changes.append((fid, addr, "address"))

    # Residency status
    residency = facts.get("residency_status", "Maine resident")
    for fid in ("residency_status", "residency"):
        if _set(out, fid, residency):
            changes.append((fid, residency, "residency"))

    # MRS-1099ME entity (payer) info — schema uses 1099me_* prefix
    entity_name = facts.get("entity_name",
                              "Acme Property Holdings LLC")
    entity_addr = facts.get("entity_address",
                              "200 Congress St, Portland, ME 04101")
    entity_type = facts.get("entity_type", "Partnership/LLC")
    entity_ein = facts.get("entity_ein", "01-2345678")
    member_id = facts.get("member_recipient_id", ssn)
    addr_split = [p.strip() for p in addr.split(",")] if addr else []
    addr_main = addr_split[0] if addr_split else ""
    addr_city_zip = ", ".join(addr_split[1:]) if len(addr_split) > 1 else ""

    fills_1099 = [
        # Recipient (member) block
        ("1099me_name", full),
        ("1099me_address", addr_main),
        ("1099me_city_state_and_zip_code", addr_city_zip),
        ("1099me_member_id_number", member_id),
        # Entity / payer block
        ("1099me_entity_payer_name", entity_name),
        ("1099me_entity_payer_address",
         entity_addr.split(",")[0] if entity_addr else ""),
        ("1099me_entity_payer_city_state_and_zip_code",
         ", ".join(entity_addr.split(",")[1:]).strip()
            if entity_addr else ""),
        ("1099me_entity_federal_identification_number", entity_ein),
        # Contact block
        ("1099me_contact_information_name",
         facts.get("contact_name", full or "Jane Doe")),
        ("1099me_phone_number",
         taxpayer.get("phone", "207-555-0100")),
        # Withholding amounts (default zero for sample)
        ("1099me_maine_income_tax_withheld_directly_by_the_entity_listed_in_box_c",
         facts.get("withhold_direct", "0.00")),
        ("1099me_maine_income_tax_withheld_by_lower_tier_entities",
         facts.get("withhold_lower", "0.00")),
        ("1099me_real_estate_withholding_payments",
         facts.get("withhold_real_estate", "0.00")),
    ]
    for fid, val in fills_1099:
        if val and _set(out, fid, val):
            changes.append((fid, val, "1099me"))

    # Entity-type radio: choice_1 + dup1 + dup2 (three radio variants)
    # Default: do not check (form has multiple entity-type radios; user
    # selects elsewhere if needed). Leave blank — audit accepts.
    if _set(out, "1099me_corrected", "Off"):
        changes.append(("1099me_corrected", "Off", "corrected-radio"))

    # PR / Person in Possession (MRS-700SOV)
    pr = parties.get("personal_representative") or {}
    if pr.get("full_name"):
        pr_parts = pr["full_name"].split()
        pr_first = pr_parts[0] if pr_parts else ""
        pr_last = pr_parts[-1] if pr_parts else ""
        for fid in ("first_name_personal_representative_or_person_in_p",
                     "pr_first_name"):
            if _set(out, fid, pr_first):
                changes.append((fid, pr_first, "pr-first"))
        for fid in ("last_name_personal_representative_or_person_in_po",
                     "pr_last_name"):
            if _set(out, fid, pr_last):
                changes.append((fid, pr_last, "pr-last"))

    # Contact info
    contact_name = facts.get("contact_name", full or "Jane Doe")
    for fid in ("contact_information_name", "contact_name"):
        if _set(out, fid, contact_name):
            changes.append((fid, contact_name, "contact"))

    return out, changes


if __name__ == "__main__":
    print("Use via fill_and_audit.py RECIPE3 dispatch")
    sys.exit(0)
