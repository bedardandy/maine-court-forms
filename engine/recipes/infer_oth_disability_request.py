"""OTH disability / accommodation request recipe-3 inference.

Covers OTH-011 (Request for Accommodation, Title II ADA) and OTH-012
(Complaint About Accommodation Decision). Both forms have the same
basic content (requester contact + court info + disability narrative
+ accommodation request) but different widget naming:
  OTH-011 uses opaque `text1`-`text13` named by rect order.
  OTH-012 uses `text2`-`text9` plus semantic names for numbered items.

This script does per-form-id dispatch on the schema field-id pattern.

OTH-015 was previously mis-dispatched here; it's actually a language-
access form (check_box1-15 + country_region_or_dialect) and has its
own dedicated script.
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


def _gather_inputs(case: dict) -> dict:
    facts = case.get("facts") or {}
    parties = case.get("parties") or {}
    court = case.get("court") or {}
    requester = (parties.get("plaintiff") or parties.get("petitioner")
                  or parties.get("applicant")
                  or parties.get("defendant") or {})
    name = requester.get("full_name", "")
    phone = (requester.get("phone_cell") or requester.get("phone")
              or requester.get("phone_home") or "")
    addr = requester.get("address") or requester.get("mailing_address") or ""
    email = requester.get("email", "")
    courthouse = (facts.get("courthouse")
                    or f"{court.get('name','Maine District Court')}, "
                       f"{court.get('location','Portland')}")
    docket = case.get("docket_no") or case.get("case_no") or ""
    case_type = facts.get("court_case_type",
                            case.get("case_type", "Family Matters").title())
    court_date = facts.get("court_case_date",
                              case.get("event_date") or "")
    court_time = facts.get("court_case_time", "10:00 AM")
    disability = facts.get("disability_type",
                              "Mobility impairment requiring use of a "
                              "wheelchair and limited fine-motor control.")
    accommodation = facts.get("accommodation_request",
                                 "Wheelchair-accessible courtroom, "
                                 "accessible parking, large-print "
                                 "documents, and additional time for "
                                 "written responses.")
    decision = facts.get("court_decision",
                            "The court denied my prior accommodation "
                            "request without explanation of the basis "
                            "for the denial.")
    decision_date = facts.get("court_decision_date",
                                 case.get("event_date") or "")
    return {
        "name": name, "phone": phone, "addr": addr, "email": email,
        "courthouse": courthouse, "docket": docket,
        "case_type": case_type,
        "court_date": _iso_to_us(court_date) if court_date else "",
        "court_time": court_time,
        "disability": disability,
        "accommodation": accommodation,
        "decision": decision,
        "decision_date": _iso_to_us(decision_date) if decision_date else "",
    }


def _process_oth011(out: dict, ctx: dict, changes: list) -> None:
    """OTH-011: row-by-row mapping. Schema widgets are positionally named
    `text1..text13` + `phone` + `time` + `disability_or_disabilities`.
    Audit feedback fixed mapping:
      y=224: text1=Name | text2=Phone (label)
      y=248: phone=Address (wide single line)
      y=275: text3=Email | text4=Courthouse
      y=300: text5=Case# | text6=(continued)
      y=327: text7=Case Type | text8=Date
      y=351: time=Time (wide; reused for hearing time)
      y=377+: disability_or_disabilities + text9-13 accommodation lines"""
    fills = [
        ("text1",  ctx["name"]),
        ("text2",  ctx["phone"]),
        ("phone",  ctx["addr"]),
        ("text3",  ctx["email"]),
        ("text4",  ctx["courthouse"]),
        ("text5",  ctx["docket"]),
        # Sentinel render shows text6 is "Type of Case" (not a case-# cont.),
        # text7 is "Date of Court Case", text8 is "Time"; the old assignment
        # was shifted one slot early (case_type→Date, date→Time, time→
        # Disability). Re-align by position.
        ("text6",  ctx["case_type"]),   # Type of Case
        ("text7",  ctx["court_date"]),  # Date of Court Case
        ("text8",  ctx["court_time"]),  # Time
        ("disability_or_disabilities", ctx["disability"]),
        ("text9",  ctx["accommodation"]),
    ]
    # Force-overwrite: the `phone` widget is physically the (wide) Address line,
    # but build_kv_map's narrative pass stamps it with the phone number because
    # of its name, and fill-if-empty left that — so Address showed the phone.
    for fid, val in fills:
        if val and out.get(fid) != val:
            out[fid] = val
            changes.append((fid, val, f"011-{fid}"))


def _process_oth012(out: dict, ctx: dict, changes: list) -> None:
    """OTH-012: text2=name, text3=phone, text4=address, text5=email,
    text6=courthouse, text7=docket, text8=case-type, text9=date+time,
    nature_of_disability_or_disabilities, please_provide_...,
    1_what_was_the_decision, undefined=date (1's date?),
    2_what_date_was_the_decision_made, undefined_2=decision date alt,
    4_why_do_you_disagree_..._1-5=reasons."""
    fills = [
        ("text2", ctx["name"]),
        ("text3", ctx["phone"]),
        ("text4", ctx["addr"]),
        ("text5", ctx["email"]),
        # Sentinel render: Text6 is the Docket Number field and Text7 is the
        # Court Location field (the recipe had them swapped).
        ("text6", ctx["docket"]),
        ("text7", ctx["courthouse"]),
        # Sentinel render: text8 is "Date and Time of Court Case" (was wrongly
        # given case_type) and text9 sits at the "Nature of Disability" line
        # (was given date+time). OTH-012 has no Type-of-Case field, so case_type
        # is dropped.
        ("text8", f"{ctx['court_date']} at {ctx['court_time']}"
                     if ctx["court_date"] else ctx["court_time"]),
        ("text9", ctx["disability"]),
        ("nature_of_disability_or_disabilities", ctx["disability"]),
        ("please_provide_the_following_informationplease_be_specific_attach_additional_pages_if_necessary",
         "See answers below."),
        ("1_what_was_the_decision", ctx["decision"]),
        ("undefined", ctx["decision_date"]),
        ("2_what_date_was_the_decision_made", ctx["decision_date"]),
        ("undefined_2", ctx["decision_date"]),
    ]
    for fid, val in fills:
        if val and _set(out, fid, val):
            changes.append((fid, val, f"012-{fid}"))

    # 5-reason narrative for "why do you disagree"
    reasons = [
        "The decision did not provide written findings explaining how "
        "my requested accommodations would create an undue burden.",
        "Less-restrictive alternative accommodations were available and "
        "should have been considered.",
        "The denial conflicts with prior accommodations granted in "
        "comparable circumstances in this court.",
        "My disability documentation supports the accommodation request.",
        "Denial impairs my ability to meaningfully participate in the "
        "proceeding.",
    ]
    for i, r in enumerate(reasons, start=1):
        fid = f"4_why_do_you_disagree_with_the_decision_{i}"
        if _set(out, fid, r):
            changes.append((fid, r, f"012-reason-{i}"))


def process(kv_map: dict, case: dict) -> tuple[dict, list]:
    out = dict(kv_map)
    changes: list = []
    ctx = _gather_inputs(case)

    # Dispatch by schema field-id pattern: OTH-011 uses bare `text1`,
    # OTH-012 uses `text2` (no `text1`) plus `nature_of_disability...`.
    has_text1 = "text1" in out
    has_nature = "nature_of_disability_or_disabilities" in out
    if has_text1:
        _process_oth011(out, ctx, changes)
    elif has_nature:
        _process_oth012(out, ctx, changes)
    else:
        # Unknown variant — try a best-effort generic fill.
        for fid in ("name","phone","address","email","courthouse",
                     "docket_number","case_or_ticket_number"):
            val = ctx.get(fid) or ctx.get(fid.replace("docket_number","docket"))
            if val and _set(out, fid, val):
                changes.append((fid, val, f"gen-{fid}"))

    return out, changes


if __name__ == "__main__":
    print("Use via fill_and_audit.py RECIPE3 dispatch (OTH-011, OTH-012)")
    sys.exit(0)
