"""BCCP family (Business and Consumer Court / Consumer Protection)
recipe-3 inference.

Covers:
  BCCP-2010 — Plaintiff statement of claim (small claims)
  BCCP-2021 — Defendant answer (small claims)

Both forms share caption + party contact block + narrative response.
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
    court = case.get("court") or {}

    plaintiff = parties.get("plaintiff") or parties.get("petitioner") or {}
    defendant = parties.get("defendant") or parties.get("respondent") or {}

    # Caption (both forms)
    if _set(out, "plaintiff", plaintiff.get("full_name", "")):
        changes.append(("plaintiff", plaintiff.get("full_name",""), "pl"))
    if _set(out, "defendant", defendant.get("full_name", "")):
        changes.append(("defendant", defendant.get("full_name",""), "df"))
    if _set(out, "location", court.get("location", "")):
        changes.append(("location", court.get("location",""), "loc"))
    docket = case.get("docket_no", "")
    if _set(out, "docket_no", docket):
        changes.append(("docket_no", docket, "docket"))
    # BCCP-2021 offset caption (force over build_kv_map pollution): the widget
    # `docket_no_if_listed` is physically the Location line and `undefined` is
    # the Docket No. (if listed) line — so they were swapped (Location showed
    # the docket, Docket showed the location).
    def _fc(fid, val, src):
        if fid in out and val and out.get(fid) != val:
            out[fid] = val
            changes.append((fid, val, src))
    if "undefined" in out:  # BCCP-2021 only
        _fc("docket_no_if_listed", court.get("location", ""), "loc-2021")
        _fc("undefined", docket, "docket-2021")
    elif _set(out, "docket_no_if_listed", docket):
        changes.append(("docket_no_if_listed", docket, "docket"))

    # ----- BCCP-2010 (Plaintiff statement) -----
    is_2010 = "city_state_zip" in out and "text1" in out and "text5" in out
    if is_2010:
        # text1=plaintiff name, text2=plaintiff address line 1
        # text3=phone, text4=email, text5=street addr, text6=phone (dup)
        # city_state_zip = combined CSZ
        pl_addr = plaintiff.get("address", "")
        pl_csz = ""
        if plaintiff.get("city") or plaintiff.get("zip"):
            pl_csz = (f"{plaintiff.get('city','')}, "
                        f"{plaintiff.get('state','ME')} "
                        f"{plaintiff.get('zip','')}".strip(", "))
        pl_phone = plaintiff.get("phone", "")
        pl_email = plaintiff.get("email", "")
        fills_2010 = [
            ("text1", plaintiff.get("full_name", "")),
            ("text2", pl_addr),
            ("text3", pl_phone),
            ("text4", pl_email),
            ("text5", pl_addr),
            ("text6", pl_phone),
            # Claim narrative ONLY when explicitly provided — the old
            # default invented a $4,500 claim and a March 1, 2024
            # contract, i.e. the entire substance of the lawsuit.
            ("text7", facts.get("bccp_claim_narrative", "")),
            ("city_state_zip", pl_csz),
            ("phone_number", pl_phone),
            # Acknowledgment boxes ONLY on an explicit boolean fact —
            # they are the filer's sworn acknowledgments.
            ("check_box8",
             "X" if facts.get("bccp_acknowledgment") is True else ""),
            ("check_box9",
             "X" if facts.get("bccp_acknowledgment") is True else ""),
        ]
        for fid, val in fills_2010:
            if val and _set(out, fid, val):
                changes.append((fid, val, f"2010-{fid}"))

    # ----- BCCP-2021 (Defendant answer) -----
    is_2021 = "your_mailing_address" in out and "your_printed_name" in out
    if is_2021:
        df_addr = defendant.get("address", "")
        df_csz = ""
        if defendant.get("city") or defendant.get("zip"):
            df_csz = (f"{defendant.get('city','')}, "
                        f"{defendant.get('state','ME')} "
                        f"{defendant.get('zip','')}".strip(", "))
        df_full_addr = ", ".join(p for p in (df_addr, df_csz) if p)
        df_phone = defendant.get("phone", "")
        df_email = defendant.get("email", "")
        df_phone_email = (f"{df_phone} / {df_email}"
                            if df_phone and df_email
                            else (df_phone or df_email))
        fills_2021 = [
            ("undefined", court.get("location", "")),
            # Deny checkbox + answer narrative ONLY when the case actually
            # provides the defendant's answer — the old default fabricated
            # a denial referencing an invented March 1, 2024 contract.
            ("on_some_or_all_of_the_claims_raised_by_the_plaintiff_i_deny_at_least_some_of_the_plaintiffs_statements_in_the",
             "X" if facts.get("bccp_defendant_answer") else ""),
            ("text1", facts.get("bccp_defendant_answer", "")),
            ("your_printed_name", defendant.get("full_name", "")),
            ("your_mailing_address", df_full_addr),
            ("your_phone_and_email_address", df_phone_email),
        ]
        for fid, val in fills_2021:
            if val and _set(out, fid, val):
                changes.append((fid, val, f"2021-{fid}"))

    return out, changes


if __name__ == "__main__":
    print("Use via fill_and_audit.py RECIPE3 dispatch (BCCP-2010, BCCP-2021)")
    sys.exit(0)
