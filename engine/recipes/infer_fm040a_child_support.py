"""FM-040-A (Child Support Worksheet) recipe-3 inference.

Pure numeric worksheet with 22+ calculation rows. Most residuals are
either narrative inputs (lines 1-4, items 15-22) or unfilled
computed cells. K:V fills caption + parties; this script populates the
financial inputs and computes the per-row outputs.

Form-gated to FM-040-A. Reads case.facts.income_*, child_support_inputs.
"""
from __future__ import annotations

import json
import pathlib
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

    # Caption widgets — FM-040-A schema uses no-underscore variants
    # `locationtown` / `docketno` (not `location_town` / `docket_no`).
    if _set(out, "locationtown", court.get("location", "")):
        changes.append(("locationtown", court.get("location",""), "caption-loc"))
    if _set(out, "docketno", case.get("docket_no", "")):
        changes.append(("docketno", case.get("docket_no",""), "caption-docket"))

    # Higher / lower income parent identification — ONLY when explicitly
    # provided (was defaulted to "Plaintiff", asserting which parent earns
    # more).
    higher_parent = facts.get("higher_income_parent", "")
    if higher_parent:
        # Form has "Higher income parent is the Plaintiff/Defendant" widget
        for fid in ("higher_income_parent_is_the_plaintiff_defendant",
                     "higher_income_parent"):
            if _set(out, fid, higher_parent):
                changes.append((fid, higher_parent, "higher-parent-choice"))

    # Income / computation rows — the entire worksheet derives from the
    # parents' incomes and the child count. Compute ONLY when all three
    # inputs are explicitly provided (the old defaults invented $1200/$650
    # weekly incomes, 2 children, and $75 of expenses, producing an
    # entirely fabricated support obligation).
    if not (facts.get("higher_income_gross_weekly")
            and facts.get("lower_income_gross_weekly")
            and facts.get("children_count")):
        return out, changes

    income_hip = float(facts["higher_income_gross_weekly"])
    income_lip = float(facts["lower_income_gross_weekly"])
    children_n = int(facts["children_count"])

    line_data = [
        ("1", f"{income_hip:,.2f}", "HIP gross weekly income"),
        ("2", f"{income_lip:,.2f}", "LIP gross weekly income"),
        ("3", f"{income_hip + income_lip:,.2f}", "combined gross"),
        ("4_hip", f"{income_hip/(income_hip+income_lip):.4f}",
         "HIP proportional share"),
        ("4_lip", f"{income_lip/(income_hip+income_lip):.4f}",
         "LIP proportional share"),
    ]
    for fid_suffix, value, src in line_data:
        for fid in (f"line_{fid_suffix}", f"{fid_suffix}",
                     f"item_{fid_suffix}"):
            if _set(out, fid, value):
                changes.append((fid, value, src))

    # Basic weekly support obligation (per Maine schedule — stub)
    basic_support = 240 + (children_n - 1) * 80  # rough lookup proxy
    for fid in ("9", "line_9", "basic_weekly_support",
                 "9_basic_weekly_support_obligation"):
        if _set(out, fid, f"{basic_support:,.2f}"):
            changes.append((fid, f"{basic_support:,.2f}",
                              "basic-support-stub"))

    # HIP / LIP share of basic support (line 10, 11)
    hip_share = basic_support * income_hip / (income_hip + income_lip)
    lip_share = basic_support * income_lip / (income_hip + income_lip)
    for fid in ("10", "line_10", "10_lower_income_parents_share_of_basic_weekly_support"):
        if _set(out, fid, f"{lip_share:,.2f}"):
            changes.append((fid, f"{lip_share:,.2f}", "lip-share"))
    for fid in ("15", "line_15", "15_higher_income_parents_share_of_basic_weekly_support"):
        if _set(out, fid, f"{hip_share:,.2f}"):
            changes.append((fid, f"{hip_share:,.2f}", "hip-share"))

    # Enhanced support (line 16 = line 9 × 1.5)
    enhanced = basic_support * 1.5
    for fid in ("16", "line_16", "16_enhanced_weekly_support_entitlement"):
        if _set(out, fid, f"{enhanced:,.2f}"):
            changes.append((fid, f"{enhanced:,.2f}", "enhanced"))

    # Line 17/18 enhanced shares
    enhanced_hip = enhanced * income_hip / (income_hip + income_lip)
    enhanced_lip = enhanced * income_lip / (income_hip + income_lip)
    for fid in ("17", "line_17"):
        if _set(out, fid, f"{enhanced_lip:,.2f}"):
            changes.append((fid, f"{enhanced_lip:,.2f}", "enhanced-lip"))
    for fid in ("18", "line_18"):
        if _set(out, fid, f"{enhanced_hip:,.2f}"):
            changes.append((fid, f"{enhanced_hip:,.2f}", "enhanced-hip"))

    # Lines 19-22 (presumptive obligation, additional expenses, total).
    # Additional expenses ONLY when explicitly provided (was a $75
    # default); the total row needs that input.
    presumptive = enhanced_hip  # simplified
    for fid in ("19", "line_19", "20", "line_20",
                 "20_presumptive_parental_support_obligation"):
        if _set(out, fid, f"{presumptive:,.2f}"):
            changes.append((fid, f"{presumptive:,.2f}", "presumptive"))
    if facts.get("additional_expenses"):
        additional = float(facts["additional_expenses"])
        total = presumptive + additional
        for fid in ("21", "line_21",
                     "21_additional_expenses_to_be_shared_by_parents_in_proportio"):
            if _set(out, fid, f"{additional:,.2f}"):
                changes.append((fid, f"{additional:,.2f}", "additional"))
        for fid in ("22", "line_22",
                     "22_total_weekly_support_obligation_of_hip_to_be_paid_to_lip"):
            if _set(out, fid, f"{total:,.2f}"):
                changes.append((fid, f"{total:,.2f}", "total"))

    return out, changes


if __name__ == "__main__":
    print("Use via fill_and_audit.py RECIPE3 dispatch")
    sys.exit(0)
