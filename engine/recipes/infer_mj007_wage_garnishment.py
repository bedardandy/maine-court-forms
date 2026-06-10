"""MJ-007 (Wage Garnishment Affidavit) recipe-3 inference.

Worksheet: affiant's name + employer + Judgment Creditor/Debtor names +
pay/deduction lines + computed disposable earnings + garnishable amount.

Reads case.facts:
  judgment_creditor, judgment_debtor — names
  affiant_name, employer_name, employer_capacity
  gross_pay, federal_tax, fica, state_tax, medicare, retirement,
  court_withholding, court_order_amount, federal_min_wage
"""
from __future__ import annotations

import sys
import json


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

    # Captions
    creditor = (facts.get("judgment_creditor")
                  or (parties.get("plaintiff") or {}).get("full_name", ""))
    debtor = (facts.get("judgment_debtor")
                or (parties.get("defendant") or {}).get("full_name", ""))
    if _set(out, "judgment_creditor", creditor):
        changes.append(("judgment_creditor", creditor, "creditor"))
    if _set(out, "judgment_debtor", debtor):
        changes.append(("judgment_debtor", debtor, "debtor"))

    # Affiant identity — schema has TWO affiant-name widgets
    # (my_name_is_1 in the body, my_name_is_2 in the jurat block).
    # ONLY from explicit facts: the old defaults invented the affiant
    # ("Lisa M. Carmichael"), employer, and job title.
    affiant = facts.get("affiant_name", "")
    employer = facts.get("employer_name", "")
    capacity = facts.get("employer_capacity", "")
    if affiant:
        for fid in ("my_name_is_1", "my_name_is_2", "my_name_is"):
            if _set(out, fid, affiant):
                changes.append((fid, affiant, "affiant"))
    if employer and _set(out, "i_am_employed_by", employer):
        changes.append(("i_am_employed_by", employer, "employer"))
    if capacity and _set(out, "in_the_capacity_of", capacity):
        changes.append(("in_the_capacity_of", capacity, "capacity"))

    # Pay frequency — ONLY when explicitly provided (was defaulted to
    # "biweekly", asserting the debtor's pay schedule).
    pay_freq = facts.get("pay_frequency", "")
    for fid in ("weekly", "biweekly", "monthly"):
        if fid == pay_freq:
            if _set(out, fid, "X"):
                changes.append((fid, "X", "pay-freq"))

    # Pay-stub line items — compute ONLY when the gross pay is explicitly
    # provided (the old defaults invented a full fictional pay stub).
    # Unstated deduction lines are treated as zero for the arithmetic but
    # are only written to the form when explicitly provided.
    def F(v): return f"{float(v):,.2f}"
    if facts.get("gross_pay"):
        gross = F(facts["gross_pay"])
        ded_items = {
            "undefined":    facts.get("federal_tax"),
            "text2":        facts.get("fica"),
            "undefined_3":  facts.get("state_tax"),
            "undefined_4":  facts.get("medicare"),
            "undefined_5":  facts.get("retirement"),
            "undefined_6":  facts.get("court_withholding"),
        }
        total_ded = sum(float(str(v).replace(",", ""))
                        for v in ded_items.values() if v)
        disposable = float(gross.replace(",", "")) - total_ded
        line4 = disposable * 0.25

        # Schema-derived widget mapping (verified by rect y-coords):
        #   Item 1 → "1"
        #   Item 2a-f (federal/FICA/state/Medicare/retirement/withholding)
        #            → "undefined", "text2", "undefined_3", "undefined_4",
        #              "undefined_5", "undefined_6"
        #   Total of 2a-f → "2"
        #   Item 3-8 → "3" through "8"
        #   Signature → "undefined_7"
        line_map = {
            "1":  gross,
            "2":  F(total_ded),
            "3":  F(disposable),
            "4":  F(line4),
        }
        for fid, v in ded_items.items():
            if v:
                line_map[fid] = F(v)
        # Lines 5-8 need the protected floor + court-order amount — both
        # ONLY when explicitly provided (were $290 / $100 defaults).
        if facts.get("federal_min_wage"):
            fed_min = float(facts["federal_min_wage"])
            line6 = max(0.0, disposable - fed_min)
            line_map["5"] = F(fed_min)
            line_map["6"] = F(line6)
            if facts.get("court_order_amount"):
                line7 = float(facts["court_order_amount"])
                line_map["7"] = F(line7)
                line_map["8"] = F(min(line4, line6, line7))
        for fid, val in line_map.items():
            if _set(out, fid, val):
                changes.append((fid, val, f"line-{fid}"))

    # Page-2 jurat — signer name on undefined_7
    if affiant and _set(out, "undefined_7", affiant):
        changes.append(("undefined_7", affiant, "sig-name"))

    # Page-2 — date + perjury checkbox + personally appeared
    sig_date = case.get("filing_date") or case.get("event_date", "")
    sig_date_us = sig_date
    if "-" in sig_date_us and len(sig_date_us) >= 10:
        y, m, d = sig_date_us[:10].split("-")
        sig_date_us = f"{m}/{d}/{y}"
    if _set(out, "date_mmddyyyy", sig_date_us):
        changes.append(("date_mmddyyyy", sig_date_us, "sig-date"))
    # Perjury swear checkbox — check ONLY on an explicit boolean fact;
    # never auto-swear an oath on the affiant's behalf.
    if facts.get("perjury_acknowledged") is True:
        for fid in (
            "i_swear_under_penalty_of_perjury_that_the_above_statements_are_true_an",
            "i_swear_under_penalty_of_perjury_that_the_above_statements_are_true_and_correct_i_understand_that_these_statements",
        ):
            if _set(out, fid, "X"):
                changes.append((fid, "X", "perjury"))
    # Notary "personally appeared" — variant names
    if affiant:
        for fid in ("personally_appeared_the_above_named",
                     "personally_appeared_the_abovenamed",
                     "personallyappearedtheabovenamed"):
            if _set(out, fid, affiant):
                changes.append((fid, affiant, "notary-affiant"))

    return out, changes


if __name__ == "__main__":
    print("Use via fill_and_audit.py RECIPE3 dispatch")
    sys.exit(0)
