"""OTH-015 (Language Access — Interpreter Request) recipe-3 inference.

23-widget form for requesting court interpreter. Layout (verified
against schema rects):
  y=133  names                         — party name(s)
  y=153  check_box1..4 + other         — ROLE checkboxes
                                         (Party / Witness / Parent / Other / Attorney)
  y=176  text16                        — Courthouse
  y=205  text17 / text18               — Date / Time
  y=235  text19                        — Docket (Case) Number
  y=289+ check_box5..15                — language radio
                                         (Spanish/French/ASL/Vietnamese/...)
  y=522  undefined                     — Signature line
  y=551  country_region_or_dialect     — Dialect text

Reads case.parties + case.facts.interpreter_*.
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


# Schema check_box1..4 are the ROLE checkboxes (Party/Witness/Parent/Other).
# check_box5..15 are the LANGUAGE checkboxes.
ROLE_BOX = {
    "party":    "check_box1",
    "witness":  "check_box2",
    "parent":   "check_box3",
    "other":    "check_box4",
}
LANG_BOX = {
    "spanish":      "check_box5",
    "french":       "check_box6",
    "asl":          "check_box7",
    "deaf":         "check_box7",
    "portuguese":   "check_box8",
    "somali":       "check_box9",
    "arabic":       "check_box10",
    "vietnamese":   "check_box11",
    "russian":      "check_box12",
    "chinese":      "check_box13",
    "haitian_creole": "check_box14",
    "amharic":      "check_box15",
}


def process(kv_map: dict, case: dict) -> tuple[dict, list]:
    out = dict(kv_map)
    changes: list = []
    facts = case.get("facts") or {}
    parties = case.get("parties") or {}
    court = case.get("court") or {}

    applicant = (parties.get("applicant") or parties.get("plaintiff")
                  or parties.get("petitioner")
                  or parties.get("defendant")
                  or parties.get("respondent") or {})

    # Party name(s)
    name = applicant.get("full_name", "")
    if _set(out, "names", name):
        changes.append(("names", name, "names"))

    # Role checkbox (default: Party)
    role = facts.get("interpreter_role", "party").lower()
    role_box = ROLE_BOX.get(role, "check_box1")
    if _set(out, role_box, "X"):
        changes.append((role_box, "X", f"role-{role}"))

    # Courthouse + Date/Time + Docket (page-1 caption row)
    courthouse = (facts.get("courthouse")
                   or f"{court.get('name','Maine District Court')}, "
                      f"{court.get('location','Portland')}")
    if _set(out, "text16", courthouse):
        changes.append(("text16", courthouse, "courthouse"))
    court_date = facts.get("court_case_date",
                              case.get("event_date") or "")
    if court_date:
        if _set(out, "text17", _iso_to_us(court_date)):
            changes.append(("text17", _iso_to_us(court_date), "date"))
    court_time = facts.get("court_case_time", "10:00 AM")
    if _set(out, "text18", court_time):
        changes.append(("text18", court_time, "time"))
    docket = case.get("docket_no") or case.get("case_no", "")
    if _set(out, "text19", docket):
        changes.append(("text19", docket, "docket"))

    # Language preference — default to Spanish.
    language = facts.get("interpreter_language", "spanish").lower()
    box = LANG_BOX.get(language)
    if box and _set(out, box, "X"):
        changes.append((box, "X", f"lang-{language}"))

    # Country / region / dialect
    region = facts.get("interpreter_region", "Spain (Castilian Spanish)")
    if _set(out, "country_region_or_dialect", region):
        changes.append(("country_region_or_dialect", region, "region"))

    # Signature line
    if _set(out, "undefined", name):
        changes.append(("undefined", name, "signer"))

    return out, changes


if __name__ == "__main__":
    print("Use via fill_and_audit.py RECIPE3 dispatch")
    sys.exit(0)
