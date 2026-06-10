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

    # Every dollar figure / rate / term on this worksheet is a factual
    # statement about the borrower's mortgage — fill ONLY when explicitly
    # provided in case.facts. The old code shipped a full set of invented
    # loan numbers (amounts, rates, arrears, escrow, FMV).

    # Loan terms (original)
    original_amount = facts.get("original_loan_amount", "")
    original_term_months = facts.get("original_amortization_term", "")
    original_rate = facts.get("original_interest_rate", "")
    for fid, val in [
        ("original_loan_amount", original_amount),
        ("original_amortization_term", original_term_months),
        ("original_interest_rate",
         (f"{original_rate}%" if original_rate and "%" not in original_rate
          else original_rate)),
    ]:
        if val and _set(out, fid, val):
            changes.append((fid, val, "original-loan"))

    # Current balance + rate
    current_upb = facts.get("current_unpaid_balance", "")
    current_rate = facts.get("current_interest_rate", "")
    remaining_term = facts.get("remaining_mortgage_term", "")
    months_past_due = facts.get("months_past_due", "")
    for fid, val in [
        ("current_unpaid_balance", current_upb),
        ("current_interest_rate",
         (f"{current_rate}%" if current_rate and "%" not in current_rate
          else current_rate)),
        ("remaining_mortgage_term", remaining_term),
        ("months_past_due", months_past_due),
    ]:
        if val and _set(out, fid, val):
            changes.append((fid, val, "current-loan"))

    # Payment breakdown
    payment_total = facts.get("current_mortgage_payment", "")
    payment_interest = facts.get("current_interest_payment", "")
    payment_principal = facts.get("current_principal_payment", "")
    past_due_interest = facts.get("past_due_interest", "")
    advances_escrow = facts.get("advances_escrow_past_due", "")
    for fid, val in [
        ("current_mortgage_payment", payment_total),
        ("current_interest_payment", payment_interest),
        ("current_principal_payment", payment_principal),
        ("past_due_interest", past_due_interest),
        ("advances_escrow_past_due", advances_escrow),
    ]:
        if val and _set(out, fid, val):
            changes.append((fid, val, "payment-breakdown"))

    # Escrow components — fill what is provided; total only when all
    # three components are known (a partial sum would misstate the escrow
    # payment) or explicitly given.
    taxes = facts.get("property_taxes_monthly", "")
    insurance = facts.get("property_insurance_monthly", "")
    pmi = facts.get("pmi_monthly", "")
    escrow_total = facts.get("current_escrow_payments", "")
    if not escrow_total and taxes and insurance and pmi:
        try:
            escrow_total = f"{float(taxes.replace(',', '')) + float(insurance.replace(',', '')) + float(pmi.replace(',', '')):,.2f}"
        except (ValueError, AttributeError):
            escrow_total = ""
    for fid, val in [
        ("current_escrow_payments", escrow_total),
        ("taxes", taxes), ("insurance", insurance), ("pmi", pmi),
    ]:
        if val and _set(out, fid, val):
            changes.append((fid, val, "escrow"))

    # Property value
    fmv = facts.get("current_fmv", "")
    if fmv and _set(out, "current_fmv", fmv):
        changes.append(("current_fmv", fmv, "fmv"))

    # Action / proceeding type (checkboxes — defaults)
    plaintiff_party = parties.get("plaintiff") or {}
    defendant_party = parties.get("defendant") or {}
    if plaintiff_party.get("full_name"):
        for fid in ("action_1", "action_2", "undefined", "undefined_2"):
            if _set(out, fid, plaintiff_party.get("full_name", "")):
                changes.append((fid, plaintiff_party["full_name"], "plaintiff-mirror"))

    # Plan attendance Y/N ("Does plaintiff plan to attend by telephone?")
    # Answer ONLY on an explicit fact — was defaulted to "No" for all four
    # boxes, asserting the plaintiff's attendance plans.
    attend_phone = facts.get("fdp_attend_by_telephone")
    if attend_phone in (True, False, "yes", "no", "Yes", "No"):
        val = "Yes" if attend_phone in (True, "yes", "Yes") else "No"
        for fid in ("checkbox1", "checkbox2", "checkbox3", "checkbox4"):
            if _set(out, fid, val):
                changes.append((fid, val, "telephonic"))

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
    # ONLY from explicit fdp_preparer_* facts or real plaintiff data —
    # the old defaults invented a title, firm ("Acme Loan Servicing"),
    # and a 555 phone number.
    preparer_name = facts.get("fdp_preparer_name",
        plaintiff_party.get("full_name", ""))
    preparer_title = facts.get("fdp_preparer_title", "")
    preparer_phone = facts.get("fdp_preparer_phone",
        plaintiff_party.get("phone", ""))
    preparer_firm = facts.get("fdp_preparer_firm", "")

    if preparer_name and _set(out, "printed_name", preparer_name):
        changes.append(("printed_name", preparer_name, "preparer-name"))

    # 3-line preparer narrative — compose only from known parts
    title_firm = ", ".join(p for p in (preparer_title, preparer_firm) if p)
    prep_lines = [
        preparer_name,
        title_firm,
        f"Telephone: {preparer_phone}" if preparer_phone else "",
    ]
    for i, line in enumerate(prep_lines, start=1):
        fid = f"name_title_and_telephone_number_of_person_who_prepared_this_form_{i}"
        if line and _set(out, fid, line):
            changes.append((fid, line, f"preparer-line-{i}"))

    # ── Investor identification (item D) — ONLY when explicitly provided
    # (was a stock "Acme Mortgage Investment Trust"). ──
    investor = facts.get("fdp_investor", "")
    if investor and _set(out,
            "for_mediation_purposes_please_identify_the_investor_on_this_loan",
            investor):
        changes.append((
            "for_mediation_purposes_please_identify_the_investor_on_this_loan",
            investor, "investor-id"))

    return out, changes


if __name__ == "__main__":
    print("Use via fill_and_audit.py RECIPE3 dispatch")
    sys.exit(0)
