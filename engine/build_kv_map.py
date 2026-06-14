"""K:V mapping engine — turn a case dict + form schema into a
{field_name: value} dict that form_filler can consume.

The mapping is purely deterministic on widget field_name + category +
subcategory. No LLM here. Form-specific narrative widgets are left
blank (they're recipe-3 territory — a per-form infer_*.py would fill).

Coverage on a typical form:
  - case_constant widgets:  county, docket_no, case_no, court        ~100%
  - party_attr widgets:     petitioner/respondent/.../attorney        ~80%
                            (only fields actually in case_dict)
  - signature widgets:      blank (wet-ink convention)                  0%
  - narrative_derived:      blank (LLM / form-specific fill)            0%

Run:
    python3 -m engine.build_kv_map --form FM-008 --case-json /tmp/c.json
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
from typing import Any

OSS_ROOT = pathlib.Path(__file__).resolve().parent.parent


def _get_field_id_aliases(field_id: str) -> set[str]:
    """A widget might be 'docket_no_2' or 'docket_no'; we want both to
    map to the case dict's docket_no. Strip trailing _N and _dup_N."""
    aliases = {field_id}
    s = re.sub(r"_dup\d+$", "", field_id)
    s = re.sub(r"_\d+$", "", s)
    aliases.add(s)
    return aliases


# --- Field-id → case-data resolvers ---

def _case_constant_value(field_id: str, case: dict) -> str | None:
    aliases = _get_field_id_aliases(field_id)
    court = case.get("court") or {}
    for a in aliases:
        # Court town/location: must NOT include `location` here — that's
        # the courthouse town, not the county. Split from county.
        if a in ("location", "location_town", "town",
                  "court_location", "court_town"):
            return court.get("location") or ""
        if a in ("county", "court_county"):
            return court.get("county") or ""
        if a in ("docket_no", "docket_number", "case_docket"):
            return case.get("docket_no") or case.get("case_no") or ""
        if a in ("case_no", "case_number"):
            return case.get("case_no") or case.get("docket_no") or ""
        if a in ("court_name", "court"):
            return court.get("name") or ""
        if a in ("notary_county", "notary_jurat_county",
                  "state_of_maine_county"):
            return case.get("notary_county") or court.get("county") or ""
    return None


# Contact-block resolver — signature blocks on family / guardianship /
# probate forms end with bare `name`, `address`, `phone`, `email` lines
# numbered by block (block 1 = petitioner, block 2 = co-petitioner /
# respondent, block 3 = attorney).
# Base token + any number of numeric suffixes. The block is the LAST
# numeric suffix when it is 2 or 3 (block 1 has no suffix). A single regex
# can't both swallow a line-index group and still capture the block, so we
# match the base token and then read the trailing suffix separately.
_CONTACT_RE = re.compile(
    r"^(name|address|phone(?:_number)?|tel(?:_no)?|email)(?:_\d+)*$"
)
_CONTACT_ATTR = {"name": "full_name", "address": "address",
                 "phone": "phone", "phone_number": "phone",
                 "tel": "phone", "tel_no": "phone",
                 "email": "email"}

# A field_id can contain "date" yet denote a substantive date (the party's
# date of birth, a marriage/service/death date) rather than the form's
# filing/signature date. Those must NOT be stamped with case.filing_date.
# Court-event dates are the same class: a blank asking when an ORDER /
# JUDGMENT / DECREE / HEARING was dated or entered states a fact about a
# real court act — stamping case.filing_date into MJ-009's "Court's
# installment order dated (mm/dd/yyyy)" asserts the court issued the order
# the day the motion was filed. (order|judgment|decree|hearing also covers
# "ordered by the court" / "orders issued" narrative widgets, where a bare
# date is just as wrong.) PA-022's continuation blanks name the same
# printed sentence — "the Order for Protection from Abuse/Harassment dated
# (mm/dd/yyyy)" — without the "order" token, hence the explicit
# abuseharassment_dated entry.
#
# Round 9 extends the guard to the remaining substantive-date families a
# full-corpus sweep found still auto-stamping (every token was verified
# against the form's printed text near the widget):
#   - decision / appeal / post-conviction-review dates: CR-140's "date of
#     that decision", "Date of Writ", "Date your appeal was decided",
#     "Date of any final administrative action", deportation-proceeding
#     dates, "more that 60-days after this date"; OTH-012's "What date was
#     the decision made?". appeals_dec covers CR-140's abbreviated
#     date_of_appeals_dec, recent_date its "most recent date listed by
#     you".
#   - trial / court-event dates: MJBVB-010 "print trial date", CV-223
#     "trial start date or trailing trial period", PC-034 "COURT DATE",
#     the continuance form's "change the date of my court event on";
#     dismissed covers "That case: Was dismissed on (date)".
#   - employment / attendance / residence history: "last date employed",
#     "Dates of employment/attendance", address-history "Date From" /
#     "Date To or Present", "date on which you started employment",
#     "expect to start working on".
#   - arrest / offense dates: "Date and time of arrest", "Date of
#     offense".
#   - due / payment / debt dates: "Date due", "Fine due date", "Final
#     payment date to SDU", "amount and date of the last payment",
#     charge-off and arrears blanks, "the balance due, as of this date,
#     is $" (an amount blank).
#   - other-lawsuit / property disclosure tables: "Date lawsuit or claim
#     filed", "Date acquired", "The Deed is dated ... recorded".
#   - travel dates: mileage-reimbursement Date|Origin|Destination rows
#     (daterow / date_mmddyyyyrow ids), "anticipated date" rows, expected
#     departure blanks, "Date I wish to leave/return".
#   - prior-act / prior-document dates: "my statement dated", "On ___
#     (date), I (name) motioned the court" (anchored date_i), ADR "on
#     (date)" (anchored on_date), "date of panel finding", "Date(s) of
#     ADR Conference(s)", "Date and time of the deposition/inspection",
#     "Date of Pairing", "date the case was initiated", "guardianship
#     ... was granted on", "Date of Admission" / "effective ___"
#     (eff_date), "Termination date".
#   - completion / coverage / status: "Required date of completion",
#     "DATE STAGE COMPLETED", "Date(s) of Coverage", "this year to
#     date: $" (an amount blank).
#   - widgets that merely CONTAIN "date": this_date / following_date /
#     home_state / notice sentence fragments, "Updated ..." checkbox
#     labels ("date" is a substring of "updated"), relevant_dates /
#     date_and_details narrative boxes, the weapons-relinquishment date.
# Bare `date`/`dated`/`date_mmddyyyy(_N)` signature-block widgets carry
# none of these tokens and keep the generic event/filing-date stamp.
_SUBSTANTIVE_DATE_RE = re.compile(
    r"birth|marriage|service|death|divorce|separation|deceased"
    r"|order|judgment|judgement|decree|hearing"
    r"|abuseharassment_dated"
    r"|decision|decided|appeals_dec|writ|result|recent_date"
    r"|new_law|new_facts|admin|proceeding|deport"
    r"|trial|court_date|court_event|dismissed"
    r"|employ|attendance|date_from|date_to"
    r"|arrest|offense"
    r"|due|payment|chargeoff|arrears|start"
    r"|lawsuit|acquired|deed"
    r"|notice|relinquish|contact|coverage|termination|complet"
    r"|updated|year_to_date|this_date|following_date|home_state"
    r"|wish|anticipated|departure|admission|eff_date"
    r"|panel|conference|deposition|guardianship|initiated"
    r"|relevant_dates|date_and_details|statement_dated|pairing"
    r"|date(?:_mmddyyyy)?row"
    r"|(?:^|_)on_date(?:_|$)"
    r"|(?:^|_)date_i(?:_|$)"
    r"|(?:^|_)dob(?:_|$)")


# Per-form date-stamp blocklist (round 10).
# -----------------------------------------------------------------------
# Consulted in the same generic-date elif that consults
# _SUBSTANTIVE_DATE_RE, keyed by the schema's form_id. These widgets carry
# a date the form's filing/signature date must NEVER auto-fill, but their
# field_id is too generic (bare `date`/`dated`/`date_mmddyyyy(_N)`) for the
# token regex to catch — the *form* is what disambiguates them. Every
# entry below was verified against the form's printed PDF text by reading
# the words on the widget's own rect-row.
#
# Three member classes:
#
#   1. Substantive prior-order / GAL-contact dates whose printed sentence
#      names a real court act or event but whose field_id has no regex
#      token. FM-132 `dated_mmddyyyy` / GS-018 `dated` / FM-136 `date`
#      print "... of this date dated (mm/dd/yyyy)" referencing a PRIOR
#      order/judgment; FM-222 / PC-034 `date_mmddyyyy*` print "I met with
#      the child(ren) on the following dates and locations: Date
#      (mm/dd/yyyy): at ..." — the GAL's contact-event date, not the
#      filing date.
#
#   2. The AD-FM-GS-JV-PA-PC-292 service-block column clone. The PDF
#      author copied the "Date (mm/dd/yyyy):" widget straight down the
#      Date/Name/Address/Phone column, so the suffixed copies sit on the
#      Name:/Address:/Phone: lines (verified by exact left-label rect
#      alignment: the `_2` row prints "Name:", `_3` "Address:", `_4` the
#      "Phone Number:" line; the page-3 `*_2` twins repeat the same
#      column). The `date_mmddyyyy_1` / `_1_2` widgets are the real "Date
#      (mm/dd/yyyy):" lines and KEEP stamping — they are deliberately
#      absent from the blocklist.
#
#   3. Judicial-officer signature dates (round-8 order-date doctrine,
#      extended). A date on a judge / magistrate / justice / issuing-
#      official signature line asserts when the JUDICIAL OFFICER acted —
#      never the day the filer prepared the form. Each printed text reads
#      "Date (mm/dd/yyyy): [►] Judge/Magistrate/Justice, Maine ... Court"
#      (or "Title of Judge/Issuing Official: Date of Signature:" on
#      OMB-097).
#
# NOT blocked here: notary-jurat dates (CV-061 date_mmddyyyy_2, GS-006
# date_3, GS-009 date_3, GS-007 date). Those sit on a
# "Date: ... Before me, ... Notary Public / Attorney at Law / Clerk" line
# and are handled by a SEPARATE convention in
# engine/fill_and_audit.py::_apply_notary_block, which fills only the
# jurat county / state from real case data (round 11 removed the
# "personally appeared" signer fill — that affiant line is the notary's to
# complete and is never auto-sworn; see _NOTARY_SIGNER_FIDS_LEAVE_BLANK).
# It leaves the jurat DATE for the notary to complete and never defaults
# a county. The notary block neither reads nor writes these date fields,
# so the generic stamp would still reach them — but the round-10 verdict
# keeps them in scope of the notary convention (a notary stamps the day
# they administer the oath, which can legitimately equal the fill date)
# and explicitly OUT of scope for this date-guard round. Left untouched
# on purpose; revisit alongside the notary-block convention.
_FORM_DATE_STAMP_BLOCKLIST: dict[str, frozenset[str]] = {
    # class 1 — substantive prior-order / GAL-contact dates
    "FM-132": frozenset({"dated_mmddyyyy", "date_mmddyyyy"}),
    "GS-018": frozenset({"dated", "date"}),
    "FM-136": frozenset({"date", "datemmddyyyy"}),
    "FM-222": frozenset({"date_mmddyyyy"}),
    "PC-034": frozenset({"date_mmddyyyy", "date_mmddyyyy_3"}),
    # class 2 — AD-FM-GS-JV-PA-PC-292 service-block column clone
    # (Name/Address/Phone rows). `date_mmddyyyy_1` / `_1_2` deliberately
    # excluded — they are the genuine date lines.
    "AD-FM-GS-JV-PA-PC-292": frozenset({
        "date_mmddyyyy_2", "date_mmddyyyy_3", "date_mmddyyyy_4",
        "date_mmddyyyy_2_2", "date_mmddyyyy_3_2", "date_mmddyyyy_4_2",
    }),
    # class 3 — judicial-officer signature dates
    "CV-FM-PA-PB-PC-268": frozenset({"date_mmddyyyy"}),
    "FM-137": frozenset({"dated_mmddyyyy"}),
    "FM-PB-125": frozenset({"date_mmddyyyy"}),
    "GS-002": frozenset({"dated"}),
    "GS-004": frozenset({"dated"}),
    "JV-006-W": frozenset({"date_mmddyyyy"}),
    "JV-017": frozenset({"date_mmddyyyy"}),
    "MJBVB-017": frozenset({"date_2"}),
    "MJBVB-018": frozenset({"date_1"}),
    "OMB-097": frozenset({"dateofsigniture"}),
}


# Per-form respondent-address-stamp blocklist (round 11).
# -----------------------------------------------------------------------
# Consulted in the same narrative_derived branch that calls
# _respondent_address(case), keyed by the schema's form_id (mirrors
# _FORM_DATE_STAMP_BLOCKLIST exactly: keyed on form_id, frozenset of
# field_ids, checked with `fid not in ...get(form_id, ())`). The generic
# `physicaladdress`/`addressof(defendant|respondent)` trigger correctly
# fills genuine defendant/respondent blocks, but WRONG-vs-CORRECT here is
# POSITIONAL within each form (physical_address/_1/_2 = the first /
# plaintiff block; physical_address_3/_4 or _1_2/_2_2 = the
# defendant/respondent block) and is not derivable from a token. The
# widgets below print a label that is NOT the respondent's address line, so
# stamping the respondent's address into them is a cross-party
# over-application. Each entry was printed-text verified against its PDF
# widget rect (round-11 adjudication).
#
# Member classes (why each is blocked):
#   - plaintiff / petitioner address blocks ("Address of
#     plaintiff/petitioner:", "Plaintiff/Petitioner Information:") — the
#     respondent's address belongs in the defendant block, not here:
#     CV-266 physical_address_1/_2, FM-002 / OTH-039..044 physical_address
#     /_2, FM-283 physical_address_1/_2 + the mis-slugged
#     address_of_defendantrespondent widget that actually sits in the
#     plaintiff block, FM-284 physical_address_1/_2.
#   - "Other Party Information (if applicable):" blocks — a generic
#     third-party block, NOT the Defendant/Respondent block (which is
#     physical_address_3/_4): FM-002 / OTH-039..044 physical_address_5.
#   - judgment-creditor / mover blocks on the foreign/Canadian-judgment
#     recognition forms ("in whose favor ... was entered" / "seeking
#     recognition of the judgment") — the judgment DEBTOR block
#     (physical_address_1_3/_2_3, "against whom ... was entered") keeps the
#     stamp and is deliberately absent here: CV-281 / CV-282
#     physical_address_1/_2 (CV-282 only) and physical_address_1_2/_2_2.
#   - old/new change-of-address pairs (neither is the current respondent
#     address): CR-CV-FM-199 old_/new_physical_address_1/_2.
#   - the child's-address block on the SIJS petition (not the respondent):
#     CV-295 physical_address_street_citytown_state_zip.
#   - confidentiality-REQUEST checkboxes ("... request that the court keep
#     the following information confidential: [ ] Physical address:") —
#     small square checkbox widgets, not address-value fields, so stamping
#     an address into them is doubly wrong: FM-057 / OTH-029..034
#     physical_address.
_FORM_RESPADDR_STAMP_BLOCKLIST: dict[str, frozenset[str]] = {
    "CR-CV-FM-199": frozenset({
        "old_physical_address_1", "old_physical_address_2",
        "new_physical_address_1", "new_physical_address_2",
    }),
    "CV-266": frozenset({"physical_address_1", "physical_address_2"}),
    "CV-281": frozenset({
        "physical_address_1", "physical_address_2", "physical_address_1_2",
        "physical_address_2_2",
    }),
    "CV-282": frozenset({
        "physical_address_1", "physical_address_2", "physical_address_1_2",
        "physical_address_2_2",
    }),
    "CV-295": frozenset({"physical_address_street_citytown_state_zip"}),
    "FM-002": frozenset({
        "physical_address", "physical_address_2", "physical_address_5",
    }),
    "FM-057": frozenset({"physical_address"}),
    "FM-283": frozenset({
        "address_of_defendantrespondent", "physical_address_1",
        "physical_address_2",
    }),
    "FM-284": frozenset({"physical_address_1", "physical_address_2"}),
    "OTH-029": frozenset({"physical_address"}),
    "OTH-030": frozenset({"physical_address"}),
    "OTH-031": frozenset({"physical_address"}),
    "OTH-032": frozenset({"physical_address"}),
    "OTH-033": frozenset({"physical_address"}),
    "OTH-034": frozenset({"physical_address"}),
    "OTH-039": frozenset({
        "physical_address", "physical_address_2", "physical_address_5",
    }),
    "OTH-040": frozenset({
        "physical_address", "physical_address_2", "physical_address_5",
    }),
    "OTH-041": frozenset({
        "physical_address", "physical_address_2", "physical_address_5",
    }),
    "OTH-042": frozenset({
        "physical_address", "physical_address_2", "physical_address_5",
    }),
    "OTH-043": frozenset({
        "physical_address", "physical_address_2", "physical_address_5",
    }),
    "OTH-044": frozenset({
        "physical_address", "physical_address_2", "physical_address_5",
    }),
}


def _contact_block_value(field_id: str, case: dict) -> str | None:
    m = _CONTACT_RE.match(field_id)
    if not m:
        return None
    # Derive the block from the final numeric suffix (e.g. name_2 -> block 2,
    # address_2_3 -> block 3). Anything else is block 1.
    nums = re.findall(r"_(\d+)", field_id)
    blk = nums[-1] if (nums and nums[-1] in ("2", "3")) else "1"
    party_order = {
        "1": ("petitioner", "plaintiff", "applicant"),
        "2": ("copetitioner", "co_petitioner",
              "respondent", "defendant"),
        "3": ("attorney",),
    }.get(blk, ())
    parties = case.get("parties") or {}
    for k in party_order:
        p = parties.get(k)
        if isinstance(p, dict) and p.get("full_name"):
            attr = _CONTACT_ATTR.get(m.group(1))
            if attr:
                return p.get(attr) or ""
    return None


def _format_date(iso_date: str, target: str) -> str:
    """Convert YYYY-MM-DD (or full ISO timestamp) → target format.
    Accepted target hints:
        "us_slash"  → MM/DD/YYYY
        "us_dash"   → MM-DD-YYYY
        "iso"       → YYYY-MM-DD (date-only, strips any time suffix)
        "spelled"   → "January 15, 2024"
    """
    if not iso_date or "-" not in iso_date:
        return iso_date
    import datetime as _dt
    try:
        d = _dt.date.fromisoformat(iso_date[:10])
    except ValueError:
        return iso_date
    if target == "us_slash":
        return f"{d.month:02d}/{d.day:02d}/{d.year}"
    if target == "us_dash":
        return f"{d.month:02d}-{d.day:02d}-{d.year}"
    if target == "spelled":
        return d.strftime("%B %-d, %Y")
    return d.isoformat()  # strip any "T..." timestamp suffix


def _date_format_hint(field_id: str) -> str:
    """Detect mm/dd/yyyy expected format from the field_id."""
    fid = field_id.lower()
    if "mmddyyyy" in fid or "mm_dd_yyyy" in fid or "mm/dd/yyyy" in fid:
        return "us_slash"
    if "mm_dd_yy" in fid:
        return "us_slash"
    return "iso"


_PARTY_PREFIXES = (
    "petitioner", "respondent", "plaintiff", "defendant",
    "decedent", "applicant", "minor", "guardian", "conservator",
    "attorney", "informant", "father", "mother", "spouse",
    "juvenile", "adoptee",
)
_ATTR_KEYWORDS = ("relationship", "dob", "date_of_birth", "phone",
                   "telephone", "email", "address", "city", "zip",
                   "bar_number", "bar_no",
                   "name", "full_name")


def _party_field_value(field_id: str, party: dict) -> str | None:
    """Extract a party sub-attribute from the field_id.

    Recognized shapes:
      <party>                  → party.full_name  (bare label widget)
      <party>_<attr>           → _party_attr_value(attr)
      <party>_<attr>_N         → ignore index, same as <party>_<attr>
      <N>_<party>_<attr>...    → strip leading "N_" item number
      <text>_<attr>_<1|2>      → 1=name/address, 2=continuation/phone
      <something containing one of attr keywords>  → resolve that attr
    Returns None when nothing matches (caller leaves widget blank — no
    silent full_name fallback that mis-stamps narrative widgets).
    """
    s = re.sub(r"_dup\d+$", "", field_id)
    # Capture trailing line suffix (_1 = primary, _2 = continuation)
    line_m = re.search(r"_([12])$", s)
    line_suffix = line_m.group(1) if line_m else None
    if line_suffix:
        s = s[:line_m.start()]
    # Strip any remaining trailing _N (multi-row index)
    s = re.sub(r"_\d+$", "", s)
    # Strip leading item number ("3_..." → "...")
    s = re.sub(r"^\d+_+", "", s)

    # Exact bare-prefix widget → full_name
    if s in _PARTY_PREFIXES:
        return party.get("full_name") or None

    def _scan_attr(text: str) -> str | None:
        """Find the most likely attr keyword in `text`.

        Gate: the FIRST token of the residual must be (a) exactly an attr
        keyword, or (b) lead-into one (e.g., "address_and_telephone..." →
        first token "address" qualifies). This rejects narrative widgets
        like "wishes_to_change_the_minors_name_..." where `name` appears
        mid-string but the first token is unrelated.
        """
        tokens = text.split("_") if text else []
        if not tokens:
            return None
        first = tokens[0]
        if first not in _ATTR_KEYWORDS:
            return None
        # Leftmost match wins (so "address_and_telephone" → address,
        # not telephone).
        hits = [(text.find(kw), kw) for kw in _ATTR_KEYWORDS
                if kw in tokens]
        hits = [(p, k) for (p, k) in hits if p >= 0]
        if not hits:
            return None
        hits.sort()
        return hits[0][1]

    # <party>_<attr>...
    for prefix in _PARTY_PREFIXES:
        if s.startswith(prefix + "_"):
            attr = s[len(prefix) + 1:]
            v = _party_attr_value(attr, party)
            if v: return v
            kw = _scan_attr(attr)
            if kw:
                if line_suffix == "2" and kw == "address":
                    return _party_attr_value("phone", party)
                return _party_attr_value(kw, party)
            return None

    # Bare scan (no party prefix): same first-token-must-be-attr gate.
    kw = _scan_attr(s)
    if kw:
        if line_suffix == "2" and kw == "address":
            return _party_attr_value("phone", party)
        return _party_attr_value(kw, party)

    return None


def _respondent_address(case: dict) -> str:
    """Item-2-style 'respondent physical address' resolver — try the
    respondent / defendant party's address."""
    parties = case.get("parties") or {}
    for k in ("respondent", "defendant", "individual_under_protection"):
        p = parties.get(k) or {}
        if isinstance(p, dict) and p.get("address"):
            return p["address"]
    return ""


_PARTY_ATTR_MAP = {
    "name": "full_name", "full_name": "full_name",
    "first_name": "first_name", "first": "first_name",
    "middle_name": "middle_name", "middle": "middle_name",
    "last_name": "last_name", "last": "last_name", "surname": "last_name",
    "address": "address",
    "physical_address": "address",
    "mailing_address": "mailing_address",
    "legal_residence": "address",
    "residence": "address",
    "addr": "address",
    "street": "address",                # full address used as fallback
    "street_address": "address",
    "city": "city", "town": "city",
    "state": "state",
    "zip": "zip", "zip_code": "zip", "zipcode": "zip",
    "phone": "phone", "phone_number": "phone", "telephone": "phone",
    "tel": "phone", "tel_no": "phone",
    "phone_cell": "phone_cell", "telephone_cell": "phone_cell", "cell": "phone_cell",
    "phone_home": "phone_home", "telephone_home": "phone_home", "home": "phone_home",
    "phone_work": "phone_work", "telephone_work": "phone_work", "work": "phone_work",
    "email": "email", "email_address": "email",
    "dob": "dob", "date_of_birth": "dob", "birth_date": "dob",
    "bar_number": "bar_number", "bar_no": "bar_number",
    "maine_bar_number": "bar_number",
    "firm": "firm", "law_firm": "firm",
    "relationship": "relationship",
    "role": "role",
}


def _party_attr_value(attr: str, party: dict) -> str | None:
    key = _PARTY_ATTR_MAP.get(attr)
    if key is None:
        return None
    return party.get(key) or ""


def map_form(schema: dict, case: dict) -> tuple[dict[str, str], dict]:
    """Returns (kv_map, stats) where kv_map is field_id → value."""
    kv: dict[str, str] = {}
    n_filled = n_blank = n_skipped = 0
    by_cat = {"case_constant": 0, "party_attr": 0,
              "narrative_derived": 0, "signature": 0, "system": 0,
              "override": 0}
    parties = case.get("parties") or {}
    form_id = schema.get("form_id") or ""
    overrides_all = case.get("field_overrides") or {}
    overrides = overrides_all.get(form_id) or {}

    for f in schema.get("fields") or []:
        fid = f["field_id"]
        cat = f.get("category")
        sub = f.get("subcategory") or ""
        if cat == "system":
            n_skipped += 1
            continue
        if cat == "signature":
            kv[fid] = ""
            by_cat[cat] += 0
            n_skipped += 1
            continue

        # 1) Explicit per-form override always wins.
        if fid in overrides:
            kv[fid] = str(overrides[fid])
            n_filled += 1
            by_cat["override"] = by_cat.get("override", 0) + 1
            continue

        value: str | None = None
        if cat == "case_constant":
            value = _case_constant_value(fid, case)
        elif cat == "party_attr":
            # Match subcategory (= party key) to case's parties dict.
            # Some forms call the lead party "petitioner" while others
            # call them "plaintiff" — alias both ways so a case dict with
            # plaintiff/defendant fills a petitioner/respondent form.
            ALIASES = {
                "petitioner": ("petitioner", "plaintiff", "applicant"),
                "plaintiff":  ("plaintiff", "petitioner", "applicant"),
                "respondent": ("respondent", "defendant"),
                "defendant":  ("defendant", "respondent"),
            }
            party = parties.get(sub) or {}
            if not party:
                for alt in ALIASES.get(sub, ()):
                    if parties.get(alt):
                        party = parties[alt]
                        break
            if isinstance(party, dict):
                value = _party_field_value(fid, party)
            # Fallback: bare contact-block widgets (`name`, `address_2`, ...)
            if not value:
                value = _contact_block_value(fid, case)
        elif cat == "narrative_derived":
            # Caption-style "subject of the action" widgets (minor /
            # adoptee / juvenile / In Re widgets that hold the
            # primary party name on AD / GS / JV / NC forms).
            fid_squashed_ = fid.lower().replace("_", "")
            if fid_squashed_ in (
                    "inre", "nameofadoptee", "nameofminor",
                    "juvenilesname", "nameofjuvenile",
                    "nameofward", "nameofrespondent"):
                for k in ("minor", "adoptee", "juvenile", "decedent",
                          "ward", "child", "respondent"):
                    p = parties.get(k) or {}
                    if isinstance(p, dict) and p.get("full_name"):
                        value = p["full_name"]
                        break
            # Contact-block widgets misclassified as narrative_derived
            # (the inventory regex doesn't catch bare `name`/`address`/etc.)
            if not value:
                cb = _contact_block_value(fid, case)
                if cb is not None:
                    value = cb
            fid_lower = fid.lower()
            # Strip underscores once for fuzzier matching against slugified
            # PDF widget names like 'thepresentphysicaladdresslocation...'.
            fid_squashed = fid_lower.replace("_", "")
            # Respondent / defendant physical address — common Item 2 pattern.
            # Round 11: the `presentaddress` token was DROPPED from this
            # trigger — it matched exactly the 78 children's-present-address
            # table cells (present_addresses_do_not_list_if_confidential_to_
            # other_party_* across 13 forms), an over-application of the
            # respondent's datum into a per-child address list. The genuine
            # respondent blocks (FM-008/FM-181 etc.) fire on
            # `physicaladdress`, not `presentaddress`, so they are unaffected.
            # The per-form _FORM_RESPADDR_STAMP_BLOCKLIST then suppresses the
            # remaining wrong-block widgets the token still reaches (see its
            # docstring for the cross-party / Other-Party / judgment-creditor
            # / change-of-address / confidentiality-checkbox classes).
            if (any(k in fid_squashed for k in (
                        "physicaladdress", "respondentaddress",
                        "defendantaddress",
                        "addressofrespondent", "addressofdefendant"))
                    and fid not in _FORM_RESPADDR_STAMP_BLOCKLIST.get(
                        form_id, ())):
                value = _respondent_address(case)
            # Round 11: the notary name-stamp branch was REMOVED. Its trigger
            # ("personallyappeared"/"beforeme"/"appearedabovenamed") matched
            # only oath-certificate affiant blanks ("Personally appeared the
            # above-named ___, made oath / affirmed ... true under penalty of
            # perjury") plus FDP-006's "before mediation" substring
            # false-positives. Auto-stamping the filer's name pre-swears the
            # notary's oath on the affiant's behalf, so these fields are now
            # DELIBERATELY left blank (round-10 doctrine; round-11 closes the
            # engine path here AND in fill_and_audit._apply_notary_block —
            # never re-add a signer fill). See tests/test_auto_stamp_guards.py.
            # `date`/`dated` widgets → event_date or filing_date,
            # formatted to match the widget's expected format hint.
            # Bare "dated" widgets default to us_slash (the rendered
            # form usually shows "mm/dd/yyyy" even when the schema
            # field_id doesn't carry that hint).
            elif ("date" in fid_lower and "signed" not in fid_lower
                    and not _SUBSTANTIVE_DATE_RE.search(fid_lower)
                    and fid not in _FORM_DATE_STAMP_BLOCKLIST.get(
                        form_id, ())):
                raw = case.get("event_date") or case.get("filing_date") or ""
                if raw:
                    fmt = _date_format_hint(fid)
                    if fmt == "iso" and fid_lower in ("dated", "date"):
                        fmt = "us_slash"
                    value = _format_date(raw, fmt)

        if value:
            kv[fid] = str(value)
            n_filled += 1
            by_cat[cat] = by_cat.get(cat, 0) + 1
        else:
            kv[fid] = ""
            n_blank += 1

    # Post-process: propagate filled values to their _dup1/_dup2 siblings.
    # The schema generator emits one entry per widget; widgets that share
    # a PDF widget name get suffixed `_dup1`, `_dup2`... If `line_16` was
    # resolved, propagate the same value to `line_16_dup1`, `line_16_dup2`.
    dup_propagated = 0
    for fid in list(kv):
        if "_dup" in fid: continue
        if not kv.get(fid): continue
        for suffix in ("_dup1", "_dup2", "_dup3", "_dup4"):
            dup_fid = fid + suffix
            if dup_fid in kv and not kv[dup_fid]:
                kv[dup_fid] = kv[fid]
                dup_propagated += 1
    if dup_propagated:
        n_filled += dup_propagated
        n_blank -= dup_propagated
        by_cat["dup_propagated"] = dup_propagated

    stats = {
        "total_fields": len(schema.get("fields") or []),
        "filled": n_filled, "blank": n_blank, "skipped": n_skipped,
        "by_category_filled": by_cat,
    }
    return kv, stats


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--form", required=True, help="Form ID like FM-008")
    ap.add_argument("--case-json", type=pathlib.Path,
                    help="Path to a case dict JSON. If omitted, uses a "
                         "sample case based on form prefix.")
    ap.add_argument("--out", type=pathlib.Path,
                    help="Where to write the K:V JSON")
    args = ap.parse_args()

    schema_path = OSS_ROOT / "forms" / args.form / "schema.json"
    if not schema_path.exists():
        print(f"no schema: {schema_path}", file=sys.stderr)
        return 1
    schema = json.loads(schema_path.read_text())

    if args.case_json:
        case = json.loads(args.case_json.read_text())
    else:
        from .case_template import pick_sample_case_for
        case = pick_sample_case_for(args.form).to_dict()

    kv, stats = map_form(schema, case)
    out = args.out or pathlib.Path("intermediate") / f"{args.form}.kv.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"kv": kv, "stats": stats,
                                "case_id": case.get("case_id")}, indent=2))
    print(f"{args.form}: {stats['filled']}/{stats['total_fields']} "
          f"filled, {stats['blank']} blank, {stats['skipped']} skipped")
    print(f"  by category: {stats['by_category_filled']}")
    print(f"  wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
