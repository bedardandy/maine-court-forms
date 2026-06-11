#!/usr/bin/env python3
"""Harvest checkbox-paradox constraints into per-form ``constraints.json``.

Reproducible (re-run instead of hand-editing): scans every form's
``schema.json`` checkbox inventory (and the local blank's printed text, when
fetched) and emits the optional ``forms/<ID>/constraints.json`` that the
shared engine's constraints layer (``maine_forms_engine.constraints``)
surfaces as **warnings-only** fill diagnostics. A paradoxical selection never
blocks a fill — it gets a yellow light in the report.

Keys are schema ``field_id``s: the recipe fill path evaluates them against
its resolved ``kv`` and the mapping path's flat lookup handles them the same
way.

DELIBERATELY CONSERVATIVE. Label-similarity inference historically ran ~84%
false-positive in this codebase (the placement-sentinel finding), so only
closed, structurally-certain checkbox sets are emitted — and everything is
marked ``"inferred": true`` unless the printed form literally instructs a
single selection:

  A. The criminal-caption court selector (superior_court / district_court /
     unified_criminal_docket): a filing is made in exactly one court. When
     the local blank prints the literal single-selection instruction
     ('"X" the court for filing'), the group is certain (the note quotes
     it); without a local blank it is emitted as inferred.
  B. The AM/PM pair on a hearing time (``am`` + ``pm*``): one clock time.
  C. The community-service rating set (highly_satisfactory / satisfactory /
     unsatisfactory): one rating per evaluation.
  D. The payment-frequency set (weekly / biweekly / monthly): one frequency
     per payment plan.
  E. The fine-payment request pair (i_request_that_the_court_grant_me /
     i_request_a_new_payment_plan_of): more days to pay in full or a new
     payment plan. When the local blank prints the literal single-selection
     instruction ('Choose one:'), the group is certain (the note quotes it);
     without a local blank it is emitted as inferred.
  F. The new-payment-plan frequency selector printed as '$ ... every week /
     two weeks / month beginning (mm/dd/yyyy)' (week_3 / two_weeks_2 /
     month_beginning, only alongside class E): one frequency per plan.

Open-ended clusters (bail conditions, income-source lists, "check all that
apply") are never emitted.

    python3 tools/harvest_constraints.py            # write/refresh
    python3 tools/harvest_constraints.py --check    # verify, write nothing
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
FORMS = ROOT / "forms"

GENERATED_BY = "tools/harvest_constraints.py"

_COURT_SELECTOR = ("superior_court", "district_court",
                   "unified_criminal_docket")
_COURT_LITERAL = re.compile(r"[“\"]X[”\"]\s+the\s+court\s+for\s+filing", re.I)
_RATING_SET = ("highly_satisfactory", "satisfactory", "unsatisfactory")
_FREQUENCY_SET = ("weekly", "biweekly", "monthly")
_FINE_REQUEST_PAIR = ("i_request_that_the_court_grant_me",
                      "i_request_a_new_payment_plan_of")
_CHOOSE_ONE_LITERAL = re.compile(r"Choose\s+one\s*:", re.I)
_PLAN_FREQUENCY_SET = ("week_3", "two_weeks_2", "month_beginning")


def _checkbox_fids(fdir: pathlib.Path) -> set[str]:
    sp = fdir / "schema.json"
    if not sp.exists():
        return set()
    schema = json.loads(sp.read_text())
    return {f["field_id"] for f in schema.get("fields", [])
            if f.get("type") == "checkbox"}


def _page_text(fdir: pathlib.Path) -> str:
    pdf = fdir / f"{fdir.name}.pdf"
    if not pdf.exists():
        return ""
    import fitz
    doc = fitz.open(str(pdf))
    txt = " ".join(p.get_text() for p in doc)
    doc.close()
    return re.sub(r"\s+", " ", txt)


def harvest_form(fdir: pathlib.Path) -> dict | None:
    cbs = _checkbox_fids(fdir)
    if not cbs:
        return None
    groups: list[dict] = []

    # A — court selector
    if all(f in cbs for f in _COURT_SELECTOR):
        text = _page_text(fdir)
        m = _COURT_LITERAL.search(text)
        g = {"keys": list(_COURT_SELECTOR),
             "note": "A filing is captioned in exactly one court."}
        if m:
            g["note"] = (f"The form says '{m.group(0)}' — exactly one "
                         "court box.")
        else:
            g["inferred"] = True
            if not text:
                g["note"] += (" (no local blank to confirm the printed "
                              "single-selection instruction)")
        groups.append(g)

    # B — AM/PM hearing-time pair
    if "am" in cbs:
        pm = sorted(f for f in cbs if f == "pm" or f.startswith("pm_"))
        if len(pm) == 1:
            groups.append({"keys": ["am", pm[0]], "inferred": True,
                           "note": "A hearing time is AM or PM, not both."})

    # C — rating set
    if all(f in cbs for f in _RATING_SET):
        groups.append({"keys": list(_RATING_SET), "inferred": True,
                       "note": "One performance rating per evaluation."})

    # D — payment-frequency set
    if all(f in cbs for f in _FREQUENCY_SET):
        groups.append({"keys": list(_FREQUENCY_SET), "inferred": True,
                       "note": "One payment frequency per plan."})

    # E — fine-payment request pair (more time vs new payment plan)
    if all(f in cbs for f in _FINE_REQUEST_PAIR):
        m = _CHOOSE_ONE_LITERAL.search(_page_text(fdir))
        g = {"keys": list(_FINE_REQUEST_PAIR),
             "note": "One request per filing: more days to pay in full or "
                     "a new payment plan."}
        if m:
            g["note"] = (f"The form says '{m.group(0)}' — more days to pay "
                         "in full or a new payment plan, not both.")
        else:
            g["inferred"] = True
        groups.append(g)

        # F — the plan's printed frequency selector ('$ ... every week /
        # two weeks / month beginning'); only meaningful next to class E
        if all(f in cbs for f in _PLAN_FREQUENCY_SET):
            groups.append({"keys": list(_PLAN_FREQUENCY_SET),
                           "inferred": True,
                           "note": "A new payment plan names one frequency: "
                                   "every week, two weeks, or month."})

    if not groups:
        return None
    return {
        "form_id": fdir.name,
        "generated_by": GENERATED_BY,
        "note": ("Warnings-only paradox constraints over schema field_ids "
                 "(see the shared engine's constraints layer); a firing "
                 "constraint never blocks or alters a fill."),
        "mutually_exclusive": groups,
    }


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true",
                    help="verify shipped constraints.json files match a fresh "
                         "harvest; write nothing")
    args = ap.parse_args()
    stale = []
    n_written = n_groups = 0
    for fdir in sorted(p for p in FORMS.iterdir() if p.is_dir()):
        want = harvest_form(fdir)
        out = fdir / "constraints.json"
        have = json.loads(out.read_text()) if out.exists() else None
        if want is None:
            if have is not None and have.get("generated_by") == GENERATED_BY:
                stale.append(f"{fdir.name}: harvester no longer emits this file")
            continue
        n_groups += len(want["mutually_exclusive"])
        if have == want:
            continue
        if args.check:
            stale.append(f"{fdir.name}: constraints.json out of date "
                         "(run tools/harvest_constraints.py)")
            continue
        out.write_text(json.dumps(want, indent=2, ensure_ascii=False) + "\n")
        n_written += 1
        print(f"  {fdir.name}: wrote {out.relative_to(ROOT)} "
              f"({len(want['mutually_exclusive'])} groups)")
    if stale:
        print("\n".join(stale))
        return 1
    print(f"done — {n_groups} groups across the tree"
          + (f", {n_written} files (re)written" if not args.check else ", all current"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
