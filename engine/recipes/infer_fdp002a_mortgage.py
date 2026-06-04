"""FDP-002A (Foreclosure Diversion Program — Mortgage Information Worksheet)
recipe-3 inference.

Mortgage data worksheet with original / current loan stats. Reads
case.facts.mortgage_* + case.facts.property_*.

Form-gated to FDP-002A. AFTER K:V baseline.
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

    # Helpers
    def f(v): return f"{float(v):,.2f}"
    def pct(v): return f"{float(v):.3f}%"

    # Loan terms (original)
    original_amount = facts.get("original_loan_amount", "185,000.00")
    original_term_months = facts.get("original_amortization_term", "360")
    original_rate = facts.get("original_interest_rate", "6.250")
    for fid, val in [
        ("original_loan_amount", original_amount),
        ("original_amortization_term", original_term_months),
        ("original_interest_rate", f"{original_rate}%" if "%" not in original_rate else original_rate),
    ]:
        if _set(out, fid, val):
            changes.append((fid, val, "original-loan"))

    # Current balance + rate
    current_upb = facts.get("current_unpaid_balance", "162,450.00")
    current_rate = facts.get("current_interest_rate", "6.250")
    remaining_term = facts.get("remaining_mortgage_term", "298")
    months_past_due = facts.get("months_past_due", "4")
    for fid, val in [
        ("current_unpaid_balance", current_upb),
        ("current_interest_rate", f"{current_rate}%" if "%" not in current_rate else current_rate),
        ("remaining_mortgage_term", remaining_term),
        ("months_past_due", months_past_due),
    ]:
        if _set(out, fid, val):
            changes.append((fid, val, "current-loan"))

    # Payment breakdown
    payment_total = facts.get("current_mortgage_payment", "1,142.85")
    payment_interest = facts.get("current_interest_payment", "843.50")
    payment_principal = facts.get("current_principal_payment", "299.35")
    past_due_interest = facts.get("past_due_interest", "3,372.00")
    advances_escrow = facts.get("advances_escrow_past_due", "1,840.00")
    for fid, val in [
        ("current_mortgage_payment", payment_total),
        ("current_interest_payment", payment_interest),
        ("current_principal_payment", payment_principal),
        ("past_due_interest", past_due_interest),
        ("advances_escrow_past_due", advances_escrow),
    ]:
        if _set(out, fid, val):
            changes.append((fid, val, "payment-breakdown"))

    # Escrow components
    taxes = facts.get("property_taxes_monthly", "324.00")
    insurance = facts.get("property_insurance_monthly", "118.00")
    pmi = facts.get("pmi_monthly", "84.50")
    for fid, val in [
        ("current_escrow_payments", f"{float(taxes)+float(insurance)+float(pmi):,.2f}"),
        ("taxes", taxes), ("insurance", insurance), ("pmi", pmi),
    ]:
        if _set(out, fid, val):
            changes.append((fid, val, "escrow"))

    # Property value
    fmv = facts.get("current_fmv", "210,000.00")
    if _set(out, "current_fmv", fmv):
        changes.append(("current_fmv", fmv, "fmv"))

    # Action / proceeding type (checkboxes — defaults)
    plaintiff_party = parties.get("plaintiff") or {}
    defendant_party = parties.get("defendant") or {}
    if plaintiff_party.get("full_name"):
        for fid in ("action_1", "action_2", "undefined", "undefined_2"):
            if _set(out, fid, plaintiff_party.get("full_name", "")):
                changes.append((fid, plaintiff_party["full_name"], "plaintiff-mirror"))

    # Plan attendance Y/N (item: "Does plaintiff plan to attend by telephone?")
    for fid in ("checkbox1", "checkbox2", "checkbox3", "checkbox4"):
        if _set(out, fid, "No"):
            changes.append((fid, "No", "default-no-telephonic"))

    # ── Future Interest + Advanced Escrow combined currency ──
    # The form computes this as the sum of past-due interest and advances.
    fia = facts.get("future_interest_advanced_escrow")
    if fia is None:
        try:
            fia = f"{float(past_due_interest.replace(',', '')) + float(advances_escrow.replace(',', '')):,.2f}"
        except (ValueError, AttributeError):
            fia = ""
    if fia and _set(out, "future_interest_advanced_escrow", fia):
        changes.append(("future_interest_advanced_escrow", fia, "future-interest"))

    # ── Preparer block (printed name + name/title/phone narrative) ──
    # The mortgage worksheet is typically prepared by plaintiff (lender)
    # counsel or by the lender's loss-mitigation specialist.
    preparer_name = facts.get("fdp_preparer_name",
        plaintiff_party.get("full_name") or "Counsel for Plaintiff")
    preparer_title = facts.get("fdp_preparer_title",
        "Loss Mitigation Specialist")
    preparer_phone = facts.get("fdp_preparer_phone",
        plaintiff_party.get("phone", "207-555-0150"))
    preparer_firm = facts.get("fdp_preparer_firm",
        "Acme Loan Servicing, LLC")

    if _set(out, "printed_name", preparer_name):
        changes.append(("printed_name", preparer_name, "preparer-name"))

    # 3-line preparer narrative
    prep_lines = [
        preparer_name,
        f"{preparer_title}, {preparer_firm}",
        f"Telephone: {preparer_phone}",
    ]
    for i, line in enumerate(prep_lines, start=1):
        fid = f"name_title_and_telephone_number_of_person_who_prepared_this_form_{i}"
        if _set(out, fid, line):
            changes.append((fid, line, f"preparer-line-{i}"))

    # ── Investor identification (item D) ──
    investor = facts.get("fdp_investor",
        "Acme Mortgage Investment Trust 2018-3 "
        "(Acme Loan Servicing, LLC, master servicer)")
    if _set(out,
            "for_mediation_purposes_please_identify_the_investor_on_this_loan",
            investor):
        changes.append((
            "for_mediation_purposes_please_identify_the_investor_on_this_loan",
            investor, "investor-id"))

    return out, changes


if __name__ == "__main__":
    print("Use via fill_and_audit.py RECIPE3 dispatch")
    sys.exit(0)
