"""FDP family (Foreclosure Diversion Program) recipe-3 inference.

Covers the mediation-procedure motions:
  FDP-003 — Motion to Waive Mediation (good-cause narrative)
  FDP-004 — Motion to Continue Mediation (reason narrative)
  FDP-010 — Joint Motion to Stay Action (days + signatures)

All share the plaintiff/defendant caption + a multi-line reason
narrative + printed-name signature block.

(FDP-002A mortgage info form has its own dedicated script.)
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

    # Foreclosure: plaintiff = lender/bank, defendant = homeowner.
    plaintiff = (parties.get("plaintiff") or parties.get("petitioner")
                  or {})
    defendant = (parties.get("defendant") or parties.get("respondent")
                  or {})
    pl_name = plaintiff.get("full_name", "") or facts.get("fdp_lender",
                                                              "Bank of Maine, N.A.")
    df_name = defendant.get("full_name", "")
    sig_date_us = _iso_to_us(case.get("filing_date") or case.get("event_date", ""))
    docket = case.get("docket_no", "")

    # Captions (shared)
    for fid, val in [
        ("plaintiff", pl_name),
        ("defendant", df_name),
        ("location", court.get("location", "")),
        ("location_town", court.get("location", "")),
        ("county", court.get("county", "Cumberland")),
        ("docket_no", docket),
        ("docket_no_2", docket),
    ]:
        if val and _set(out, fid, val):
            changes.append((fid, val, "caption"))

    # Court-type checkbox (foreclosure actions are in District Court)
    if _set(out, "district_court", "X"):
        changes.append(("district_court", "X", "court-type"))

    # The homeowner (defendant) is the moving party in waive/continue.
    signer = df_name or pl_name

    # FDP-003 — good cause to waive mediation (4-line narrative)
    waive_reason = facts.get("fdp_waive_reason",
        "The defendant has reached a loan-modification agreement directly "
        "with the plaintiff's servicer and the parties agree that further "
        "court-supervised mediation is unnecessary and would only delay "
        "resolution of this matter.")
    if "1_i_have_good_cause_to_waive_mediation_1" in kv_map:
        if _set(out, "1_i_have_good_cause_to_waive_mediation_1", waive_reason):
            changes.append(("1_i_have_good_cause_to_waive_mediation_1",
                              waive_reason, "fdp003-reason"))

    # FDP-004 — continue mediation (6-line narrative)
    continue_reason = facts.get("fdp_continue_reason",
        "The defendant requires additional time to gather and submit the "
        "financial documentation requested by the plaintiff's servicer, "
        "and a brief continuance will allow the parties to complete the "
        "loss-mitigation review before the next scheduled session.")
    if "plaintiffdefendant_is_asking_that_the_mediation_be_continued_because_1" in kv_map:
        if _set(out,
                "plaintiffdefendant_is_asking_that_the_mediation_be_continued_because_1",
                continue_reason):
            changes.append((
                "plaintiffdefendant_is_asking_that_the_mediation_be_continued_because_1",
                continue_reason, "fdp004-reason"))
        if _set(out, "text1", continue_reason):
            changes.append(("text1", continue_reason, "fdp004-text1"))

    # FDP-010 — motion to stay (days + reason radio)
    if "days_up_to_120_days" in kv_map:
        stay_days = facts.get("fdp_stay_days", "90")
        if _set(out, "days_up_to_120_days", stay_days):
            changes.append(("days_up_to_120_days", stay_days, "fdp010-days"))
        # group1 radio default — "to allow continued loss-mitigation review"
        if _set(out, "group1", "X"):
            changes.append(("group1", "X", "fdp010-reason-radio"))

    # Shared signature block
    for fid in ("print_name", "printed_name"):
        if _set(out, fid, signer):
            changes.append((fid, signer, "signer"))
    for fid in ("date_mmddyyyy", "date", "date_2", "date_3"):
        if _set(out, fid, sig_date_us):
            changes.append((fid, sig_date_us, "sig-date"))
    # `undefined` widgets — signer name echo / SS county
    if _set(out, "undefined", signer):
        changes.append(("undefined", signer, "signer-echo"))
    if _set(out, "ss", court.get("county", "Cumberland")):
        changes.append(("ss", court.get("county","Cumberland"), "ss-county"))

    # FDP-010 caption is offset-named and build_kv_map scrambles it: the
    # widget `docket_no` is physically the "<County>, ss" line, `docket_no_2`
    # is the Location line, `ss` is the left Docket No. line, and `undefined`
    # is the right Docket No. line. Force by true position (overrides the
    # shared/echo assignments above; gated to FDP-010 via its stay-days field).
    if "days_up_to_120_days" in kv_map:
        def _fdp010(fid, val, src):
            if fid in out and val and out.get(fid) != val:
                out[fid] = val
                changes.append((fid, val, src))
        _fdp010("docket_no", court.get("county", "Cumberland"), "fdp010-county")
        _fdp010("docket_no_2", court.get("location", ""), "fdp010-location")
        _fdp010("ss", docket, "fdp010-docket-left")
        _fdp010("undefined", docket, "fdp010-docket-right")

    return out, changes


if __name__ == "__main__":
    print("Use via fill_and_audit.py RECIPE3 dispatch (FDP-003/004/010)")
    sys.exit(0)
