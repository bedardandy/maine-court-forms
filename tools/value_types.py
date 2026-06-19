#!/usr/bin/env python3
"""Conservative value-type validators for the fill-guidance layer.

Given a field's declared ``value_type`` (see tools/derive_field_guidance.py)
and a supplied value, return a short human-readable problem string when the
value *clearly* doesn't look like that type, else None. These power
preflight's type warnings — they are deliberately lenient (only high-confidence
mismatches) so they never false-positive on legitimate input. Warnings only;
nothing here blocks a fill.

The checks intentionally accept a wide range of valid formats (a date may be
ISO or MM/DD/YYYY; currency may carry '$' and commas; a state may be a name or
a 2-letter code) — the goal is to catch "a phone number typed into the ZIP
box", not to enforce one canonical format.
"""
from __future__ import annotations

import re

MAINE_COUNTIES = {
    "androscoggin", "aroostook", "cumberland", "franklin", "hancock",
    "kennebec", "knox", "lincoln", "oxford", "penobscot", "piscataquis",
    "sagadahoc", "somerset", "waldo", "washington", "york",
}

US_STATE_ABBR = {
    "al", "ak", "az", "ar", "ca", "co", "ct", "de", "fl", "ga", "hi", "id",
    "il", "in", "ia", "ks", "ky", "la", "me", "md", "ma", "mi", "mn", "ms",
    "mo", "mt", "ne", "nv", "nh", "nj", "nm", "ny", "nc", "nd", "oh", "ok",
    "or", "pa", "ri", "sc", "sd", "tn", "tx", "ut", "vt", "va", "wa", "wv",
    "wi", "wy", "dc",
}
US_STATE_NAMES = {
    "alabama", "alaska", "arizona", "arkansas", "california", "colorado",
    "connecticut", "delaware", "florida", "georgia", "hawaii", "idaho",
    "illinois", "indiana", "iowa", "kansas", "kentucky", "louisiana",
    "maine", "maryland", "massachusetts", "michigan", "minnesota",
    "mississippi", "missouri", "montana", "nebraska", "nevada",
    "new hampshire", "new jersey", "new mexico", "new york",
    "north carolina", "north dakota", "ohio", "oklahoma", "oregon",
    "pennsylvania", "rhode island", "south carolina", "south dakota",
    "tennessee", "texas", "utah", "vermont", "virginia", "washington",
    "west virginia", "wisconsin", "wyoming",
}

_ZIP_RE = re.compile(r"^\d{5}(?:-\d{4})?$")
_CURRENCY_RE = re.compile(r"^\$?\s*-?[\d,]+(?:\.\d{1,2})?$")
_DATE_ISO_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_DATE_US_RE = re.compile(r"^\d{1,2}/\d{1,2}/\d{2,4}$")
_TIME_RE = re.compile(r"^\d{1,2}(?::\d{2})?\s*(?:[ap]\.?m\.?)?$", re.I)


def _digits(s: str) -> str:
    return re.sub(r"\D", "", s)


def validate_value(value_type: str, value) -> str | None:
    """Return a problem message if ``value`` clearly mismatches
    ``value_type``, else None. Non-string scalars are stringified; empty
    values pass (presence is preflight's separate concern)."""
    if value is None:
        return None
    v = str(value).strip()
    if not v:
        return None

    if value_type == "zip":
        if not _ZIP_RE.match(v):
            return f"'{v}' is not a 5-digit ZIP (or ZIP+4)"
    elif value_type == "currency":
        if not _CURRENCY_RE.match(v):
            return f"'{v}' is not a dollar amount (digits, optional $ , .)"
    elif value_type == "percent":
        if not re.match(r"^\d+(?:\.\d+)?\s*%?$", v):
            return f"'{v}' is not a percentage"
    elif value_type == "email":
        if "@" not in v or "." not in v.split("@")[-1]:
            return f"'{v}' is not an email address"
    elif value_type == "phone":
        if len(_digits(v)) < 7:
            return f"'{v}' is not a phone number (too few digits)"
    elif value_type == "state":
        if v.lower() not in US_STATE_ABBR and v.lower() not in US_STATE_NAMES:
            return f"'{v}' is not a US state name or 2-letter code"
    elif value_type == "county":
        low = v.lower().replace(" county", "").strip()
        if any(ch.isdigit() for ch in v):
            return f"'{v}' has digits — a county is a name (e.g. Cumberland)"
        if low not in MAINE_COUNTIES:
            return (f"'{v}' is not a Maine county name "
                    "(expected one of the 16 counties)")
    elif value_type == "date":
        if not (_DATE_ISO_RE.match(v) or _DATE_US_RE.match(v)):
            return f"'{v}' is not a date (YYYY-MM-DD or MM/DD/YYYY)"
    elif value_type == "time":
        if not _TIME_RE.match(v):
            return f"'{v}' is not a wall-clock time (e.g. 10:00 or 10:00 AM)"
    elif value_type == "person_name":
        if not any(c.isalpha() for c in v):
            return f"'{v}' has no letters — not a person's name"
    return None
