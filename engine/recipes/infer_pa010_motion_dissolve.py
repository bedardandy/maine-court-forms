"""PA-010 (Motion to Dissolve/Modify Temporary Order for Protection)
recipe-3 inference.

The schema is full of generic-named widgets (`1`, `2`, `1_2`, `2_2`,
`v_1`, `v_2`, `undefined`, `undefined_2`) — these are PDF-source
artifacts from a form whose original widget names were stripped.
Mapped by rect y-coordinate:

  y= 51  plaintiff       (text, 212w)   plaintiff name (line 1)
  y= 66  undefined       (text, 131w)   docket_no
  y= 68  individually_and_on_behalf_of (chk)  on-behalf-of toggle (pl)
  y= 81  1               (text, 212w)   plaintiff address line 1
  y= 81  location_town   (text, 158w)   court location (right)
  y= 96  2               (text, 212w)   plaintiff address line 2
  y=106  date_mmddyyyy / undefined_2     order date + reference
  y=113  on_behalf_of    (chk)           on-behalf-of toggle (df)
  y=126  1_2             (text, 212w)   defendant name line 1
  y=141  2_2             (text, 212w)   defendant address line 1
  y=186  v_1             (text, 213w)   defendant address line 2
  y=216  v_2             (text, 213w)   defendant continuation
  y=273  dissolve_temporary_order_for_protection         (chk) — DISSOLVE
  y=287  modifyamend_temporary_order_for_protection      (chk) — MODIFY
  y=329  be_dissolved_because_..._that          (text, 86w)  short narr
  y=331  the_defendant_hereby_requests_..._mmddyyyy       (chk)
  y=387  the_plaintiff_or_minor_child_is_in_immediate... (text, 86w)
  y=390  the_defendant_hereby_requests_..._mmddyyyy_2    (chk)
  y=418-527 be_modifiedamended_for_the_reasons_provided_below_1..6
  y=570-635 wherefore_defendant_asks_the_court_to_1..4
  y=48 (p2) i_swear_under_penalty_of_perjury... (chk)
  y=106 (p2) date_mmddyyyy / undefined_2 (sign date + sig text)
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

    plaintiff = (parties.get("plaintiff") or parties.get("petitioner") or {})
    defendant = (parties.get("defendant") or parties.get("respondent") or {})

    # ── Caption: plaintiff name + address (2 lines) ──
    if _set(out, "plaintiff", plaintiff.get("full_name", "")):
        changes.append(("plaintiff", plaintiff.get("full_name",""), "pl-name"))
    pl_addr = plaintiff.get("address", "")
    pl_city_state_zip = ""
    if plaintiff.get("city") or plaintiff.get("state") or plaintiff.get("zip"):
        pl_city_state_zip = (
            f"{plaintiff.get('city','')}, "
            f"{plaintiff.get('state','ME')} "
            f"{plaintiff.get('zip','')}"
        ).strip(", ")
    if _set(out, "1", pl_addr):
        changes.append(("1", pl_addr, "pl-addr1"))
    if _set(out, "2", pl_city_state_zip):
        changes.append(("2", pl_city_state_zip, "pl-addr2"))

    # ── Caption: defendant ──
    if _set(out, "1_2", defendant.get("full_name", "")):
        changes.append(("1_2", defendant.get("full_name",""), "df-name"))
    df_addr = defendant.get("address", "")
    df_city_state_zip = ""
    if defendant.get("city") or defendant.get("state") or defendant.get("zip"):
        df_city_state_zip = (
            f"{defendant.get('city','')}, "
            f"{defendant.get('state','ME')} "
            f"{defendant.get('zip','')}"
        ).strip(", ")
    if _set(out, "2_2", df_addr):
        changes.append(("2_2", df_addr, "df-addr1"))
    if _set(out, "v_1", df_city_state_zip):
        changes.append(("v_1", df_city_state_zip, "df-addr2"))
    if _set(out, "v_2", defendant.get("phone", "")):
        changes.append(("v_2", defendant.get("phone",""), "df-phone"))

    # Docket / location (right-side caption) — schema field NAMES are
    # SWAPPED relative to the rendered form. The widget at y=66 named
    # `undefined` sits next to "Location (Town):" on the page; the
    # widget at y=81 named `location_town` sits next to "Docket No:".
    # Schema bug — fill by rendered label, not by schema name.
    if _set(out, "undefined", court.get("location", "")):
        changes.append(("undefined", court.get("location",""), "loc"))
    if _set(out, "location_town", case.get("docket_no", "")):
        changes.append(("location_town", case.get("docket_no",""), "docket"))

    # ── y=273/287 top-level action checkboxes ──
    # ONLY when explicitly provided (was defaulted to "dissolved",
    # choosing the requested relief on the movant's behalf).
    pa010_action = (facts.get("pa010_action") or "").lower()
    if pa010_action.startswith("diss"):
        if _set(out, "dissolve_temporary_order_for_protection", "X"):
            changes.append(("dissolve_temporary_order_for_protection",
                            "X", "dissolve-top"))
    elif pa010_action.startswith("modif"):
        if _set(out, "modifyamend_temporary_order_for_protection", "X"):
            changes.append(("modifyamend_temporary_order_for_protection",
                            "X", "modify-top"))

    # ── y=331/390 sub-checkboxes (request-to-dissolve / request-to-modify) ──
    if pa010_action.startswith("diss"):
        if _set(out,
                "the_defendant_hereby_requests_the_temporary_order_for_protection_dated_mmddyyyy",
                "X"):
            changes.append((
                "the_defendant_hereby_requests_the_temporary_order_for_protection_dated_mmddyyyy",
                "X", "request-dissolve"))
    elif pa010_action.startswith("modif"):
        if _set(out,
                "the_defendant_hereby_requests_the_temporary_order_for_protection_dated_mmddyyyy_2",
                "X"):
            changes.append((
                "the_defendant_hereby_requests_the_temporary_order_for_protection_dated_mmddyyyy_2",
                "X", "request-modify"))

    # ── y=329/387 narrow continuation narratives (86-px wide) ──
    # These are 86px short widgets at right margin — likely short fragments
    # like "the alleged abuse occurred" or "the order should not stand".
    if pa010_action.startswith("diss"):
        # 86-px wide widget — must fit short string (≤ ~14 chars).
        # ONLY when explicitly provided (was a stock "abuse occurred").
        diss_short = facts.get("pa010_dissolve_short", "")
        if diss_short and _set(out,
                "be_dissolved_because_the_allegations_in_plaintiffs_sworn_complaint_are_insufficient_to_support_a_finding_that",
                diss_short):
            changes.append((
                "be_dissolved_because_the_allegations_in_plaintiffs_sworn_complaint_are_insufficient_to_support_a_finding_that",
                diss_short, "dissolve-short"))

    if pa010_action.startswith("modif"):
        modif_short = facts.get("pa010_modify_short", "")
        if modif_short and _set(out,
                "the_plaintiff_or_minor_child_is_in_immediate_and_present_danger_of_abuse_for_the_following_reasons",
                modif_short):
            changes.append((
                "the_plaintiff_or_minor_child_is_in_immediate_and_present_danger_of_abuse_for_the_following_reasons",
                modif_short, "modify-short"))

    # ── y=418-527 modify reasons block (6 lines) — only fill if modifying ──
    if pa010_action.startswith("modif"):
        # ONLY when explicitly provided — the old default invented the
        # grounds for modification.
        modify_reasons = facts.get("pa010_modify_reasons") or []
        if isinstance(modify_reasons, str):
            modify_reasons = [modify_reasons]
        for i, line in enumerate(modify_reasons[:6], start=1):
            fid = f"be_modifiedamended_for_the_reasons_provided_below_{i}"
            if line and _set(out, fid, line):
                changes.append((fid, line, f"modify-reason-{i}"))

    # ── y=570-635 WHEREFORE relief (4 lines) — ONLY when explicitly
    # provided (the old default requested fees and return of property on
    # the movant's behalf). ──
    relief = facts.get("pa010_relief_items") or []
    if isinstance(relief, str):
        relief = [relief]
    for i, line in enumerate(relief[:4], start=1):
        fid = f"wherefore_defendant_asks_the_court_to_{i}"
        if line and _set(out, fid, line):
            changes.append((fid, line, f"wherefore-{i}"))

    # ── Page 2 signature block ──
    sig_date = case.get("filing_date") or case.get("event_date") or ""
    sig_date_us = _iso_to_us(sig_date)
    if _set(out, "date_mmddyyyy", sig_date_us):
        changes.append(("date_mmddyyyy", sig_date_us, "sig-date"))
    if _set(out, "undefined_2", defendant.get("full_name", "")):
        changes.append(("undefined_2", defendant.get("full_name",""),
                        "sig-text"))

    # Perjury swear — check ONLY on an explicit boolean fact; never
    # auto-swear an oath on the movant's behalf.
    if facts.get("perjury_acknowledged") is True:
        for fid in (
            "i_swear_under_penalty_of_perjury_that_the_above_statements_are_true_and_correct_i_understand_that_these",
            "i_swear_under_penalty_of_perjury_that_the_above_statements_are_true_and_correct_i_understand_that_these_statements",
        ):
            if _set(out, fid, "X"):
                changes.append((fid, "X", "perjury"))

    return out, changes


if __name__ == "__main__":
    print("Use via fill_and_audit.py RECIPE3 dispatch")
    sys.exit(0)
