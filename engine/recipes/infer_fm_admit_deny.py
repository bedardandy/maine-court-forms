"""FM admit/deny family recipe-3 inference.

Covers FM-227 (Respondent's Answer), FM-233 (Defendant's Answer to
Complaint). Both are response forms with admit/deny paragraph numbers,
affirmative defenses, counterclaims.

Reads case.parties + case.facts.admit_paragraphs / deny_paragraphs /
affirmative_defenses / counterclaim.
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

    # Captions: petitioner(s) + respondent(s) on FM-227,
    # plaintiff(s) + defendant(s) on FM-233.
    pet = (parties.get("petitioner") or parties.get("plaintiff") or {})
    resp = (parties.get("respondent") or parties.get("defendant") or {})
    if pet.get("full_name"):
        for fid in ("petitioners", "petitioner", "plaintiffs", "plaintiff"):
            if _set(out, fid, pet["full_name"]):
                changes.append((fid, pet["full_name"], "petitioner"))
    if resp.get("full_name"):
        for fid in ("respondents", "respondent",
                     "defendants", "defendant"):
            if _set(out, fid, resp["full_name"]):
                changes.append((fid, resp["full_name"], "respondent"))

    # admit / deny paragraph numbers
    admit_paras = facts.get("admit_paragraphs", "1, 2, 4")
    deny_paras = facts.get("deny_paragraphs", "3, 5")
    insuff_paras = facts.get("insufficient_info_paragraphs", "6")
    for fid in ("1_respondent_admits_paragraphs",
                 "1_defendant_admits_paragraphs",
                 "admit_paragraphs",
                 "respondent_admits", "defendant_admits"):
        if _set(out, fid, admit_paras):
            changes.append((fid, admit_paras, "admit"))
    for fid in ("2_respondent_denies_paragraphs",
                 "2_defendant_denies_paragraphs",
                 "deny_paragraphs",
                 "respondent_denies", "defendant_denies"):
        if _set(out, fid, deny_paras):
            changes.append((fid, deny_paras, "deny"))
    for fid in ("3_insufficient_information",
                 "insufficient_information_paragraphs",
                 "insufficient_info"):
        if _set(out, fid, insuff_paras):
            changes.append((fid, insuff_paras, "insuff-info"))

    # Affirmative defenses
    defenses = facts.get("affirmative_defenses",
                            "No affirmative defenses asserted.")
    for fid in ("affirmative_defenses", "defenses",
                 "4_affirmative_defenses"):
        if _set(out, fid, defenses):
            changes.append((fid, defenses, "defenses"))

    # Counterclaim
    counterclaim = facts.get("counterclaim",
                                "No counterclaim asserted.")
    for fid in ("counterclaim", "counterclaim_text",
                 "5_counterclaim"):
        if _set(out, fid, counterclaim):
            changes.append((fid, counterclaim, "counterclaim"))

    return out, changes


if __name__ == "__main__":
    print("Use via fill_and_audit.py RECIPE3 dispatch")
    sys.exit(0)
