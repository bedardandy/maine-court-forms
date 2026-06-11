#!/usr/bin/env python3
"""Preflight-validate a canonical fact object before any fill.

The fill paths silently resolve nothing for typo'd keys (``parties.lawyer``
instead of ``parties.attorney``, ``dob`` instead of ``date_of_birth``), so a
malformed case produces a near-blank PDF with no explanation. This boundary
check catches that BEFORE the fill and returns machine-readable issues with
suggestions.

The contract is ``catalog/canonical_case.schema.json`` (JSON Schema for
external validators); this module implements the same rules deterministically
with no dependencies, plus suggestion-bearing vocabulary checks JSON Schema
can't express.

Library:    from tools.preflight import preflight_case
MCP:        the lint_case tool; fill_form also runs it on canonical input
CLI:        python3 tools/preflight.py case.json [--form PA-001]

Result: {"ok": bool, "errors": [...], "warnings": [...]} — each issue is
{"code", "path", "message", "suggestion"?}. Errors mean the fill would
silently lose data; warnings are probably-fine-but-check.

With --form (or form_id=), also reports which of that form's required /
used canonical keys (mapping.json "facts") the case doesn't satisfy.
"""
from __future__ import annotations

import argparse
import difflib
import json
import pathlib
import sys

OSS_ROOT = pathlib.Path(__file__).resolve().parent.parent

SCHEMA_PATH = OSS_ROOT / "catalog" / "canonical_case.schema.json"

TOP_KEYS = ("matter", "parties", "party", "facts")
# Deprecated-but-accepted top-level fallbacks (engine/canonical.py reads
# them) and sample-case metadata.
TOP_KEYS_EXTRA = ("case_id", "filing_date", "event_date", "generic",
                  "generic_reason")

MATTER_KEYS = ("docket_number", "case_number", "case_id", "court_county",
               "court_location", "court_type", "case_type", "filing_date",
               "event_date")

PARTY_ROLES = ("plaintiff", "defendant", "attorney", "other_party")
# child_1..child_N are valid numbered roles (checked by pattern).

PARTY_ATTRS = ("full_name", "first_name", "middle_name", "last_name",
               "address", "city", "state", "zip", "phone", "email",
               "date_of_birth", "signature", "bar_number")

# Common wrong-vocabulary spellings -> the canonical token. Suggestions
# only — preflight never rewrites the case.
ROLE_ALIASES = {
    "lawyer": "attorney", "counsel": "attorney", "atty": "attorney",
    "petitioner": "plaintiff", "respondent": "defendant",
    "applicant": "plaintiff", "appellant": "plaintiff",
    "appellee": "defendant", "opposing_party": "other_party",
    "child": "child_1", "minor": "child_1",
}
ATTR_ALIASES = {
    "dob": "date_of_birth", "birth_date": "date_of_birth",
    "birthdate": "date_of_birth", "name": "full_name",
    "zip_code": "zip", "zipcode": "zip", "postal_code": "zip",
    "telephone": "phone", "phone_number": "phone",
    "email_address": "email", "street_address": "address",
    "bar_no": "bar_number", "bar": "bar_number",
}
MATTER_ALIASES = {
    "docket": "docket_number", "docket_no": "docket_number",
    "case_no": "case_number", "county": "court_county",
    "location": "court_location", "court": "court_type",
    "date_filed": "filing_date",
}

ENGINE_SHAPE_MARKERS = ("court", "docket_no", "citation_no", "case_no")


def _suggest(key: str, vocab, aliases: dict) -> str | None:
    if key in aliases:
        return aliases[key]
    close = difflib.get_close_matches(key, vocab, n=1, cutoff=0.75)
    return close[0] if close else None


def _issue(code: str, path: str, message: str,
           suggestion: str | None = None) -> dict:
    out = {"code": code, "path": path, "message": message}
    if suggestion:
        out["suggestion"] = suggestion
    return out


def _is_child_role(role: str) -> bool:
    return role.startswith("child_") and role[6:].isdigit()


def _check_party(role_path: str, p, errors: list, warnings: list) -> None:
    if not isinstance(p, dict):
        errors.append(_issue("party-not-object", role_path,
                             f"{role_path} must be an object of party "
                             f"attributes, got {type(p).__name__}"))
        return
    for attr, v in p.items():
        if attr not in PARTY_ATTRS:
            sug = _suggest(attr, PARTY_ATTRS, ATTR_ALIASES)
            warnings.append(_issue(
                "unknown-party-attr", f"{role_path}.{attr}",
                f"'{attr}' is not a canonical party attribute — no mapping "
                "resolves it, so it fills nothing",
                f"{role_path}.{sug}" if sug else None))
        elif v is not None and not isinstance(v, (str, int, float)):
            errors.append(_issue(
                "non-scalar-value", f"{role_path}.{attr}",
                f"party attribute values must be scalars; got "
                f"{type(v).__name__} (non-scalars resolve to nothing)"))


def preflight_case(case, form_id: str | None = None,
                   forms_root: pathlib.Path | None = None) -> dict:
    """Validate a canonical fact object. Returns
    {"ok", "errors", "warnings"} (+ form-specific facts coverage when
    form_id is given)."""
    errors: list[dict] = []
    warnings: list[dict] = []

    if not isinstance(case, dict):
        return {"ok": False, "warnings": [], "errors": [_issue(
            "case-not-object", "$",
            f"case must be a JSON object, got {type(case).__name__}")]}

    # Engine-shape detection first: the most common total-loss mistake.
    markers = set(ENGINE_SHAPE_MARKERS) & set(case)
    if markers and "matter" not in case:
        errors.append(_issue(
            "engine-shape", "$",
            f"top-level {sorted(markers)} look like the engine case shape; "
            "the canonical fact object is {matter, parties, party, facts} "
            "(docs/integrations/README.md) — a mapping fill would resolve "
            "almost nothing",
            "wrap the case: court/docket fields go under 'matter' "
            "(matter.court_county, matter.docket_number, ...)"))

    known_top = set(TOP_KEYS) | set(TOP_KEYS_EXTRA)
    for k in case:
        if k in known_top or k.startswith("_"):
            continue
        if k in ENGINE_SHAPE_MARKERS and "matter" not in case:
            continue  # already reported as engine-shape
        sug = _suggest(k, TOP_KEYS, {"people": "parties", "person": "party",
                                     "matters": "matter", "fact": "facts",
                                     "case": "matter"})
        errors.append(_issue(
            "unknown-top-level-key", f"$.{k}",
            f"'{k}' is not part of the canonical fact object "
            "({matter, parties, party, facts}) — nothing reads it", sug))

    if "matter" not in case:
        errors.append(_issue(
            "missing-matter", "$.matter",
            "the canonical fact object needs a top-level 'matter' block "
            "(docket/court context); use an empty object if truly unknown"))

    matter = case.get("matter")
    if matter is not None:
        if not isinstance(matter, dict):
            errors.append(_issue("matter-not-object", "$.matter",
                                 f"'matter' must be an object, got "
                                 f"{type(matter).__name__}"))
        else:
            for k, v in matter.items():
                if k not in MATTER_KEYS:
                    sug = _suggest(k, MATTER_KEYS, MATTER_ALIASES)
                    warnings.append(_issue(
                        "unknown-matter-key", f"$.matter.{k}",
                        f"'matter.{k}' is not a canonical matter key",
                        f"matter.{sug}" if sug else None))
                elif v is not None and not isinstance(v, (str, int, float)):
                    errors.append(_issue(
                        "non-scalar-value", f"$.matter.{k}",
                        f"matter values must be scalars; got "
                        f"{type(v).__name__}"))

    parties = case.get("parties")
    if parties is not None:
        if not isinstance(parties, dict):
            errors.append(_issue("parties-not-object", "$.parties",
                                 "'parties' must be an object mapping role "
                                 "-> party attributes"))
        else:
            role_vocab = list(PARTY_ROLES) + ["child_1", "child_2"]
            for role, p in parties.items():
                if role in PARTY_ROLES or _is_child_role(role):
                    _check_party(f"$.parties.{role}", p, errors, warnings)
                else:
                    sug = _suggest(role, role_vocab, ROLE_ALIASES)
                    errors.append(_issue(
                        "unknown-party-role", f"$.parties.{role}",
                        f"'{role}' is not a known party role "
                        f"(known: {', '.join(PARTY_ROLES)}, child_1..N) — "
                        "no mapping resolves it, so this party fills "
                        "nothing",
                        f"parties.{sug}" if sug else None))

    if "party" in case:
        _check_party("$.party", case["party"], errors, warnings)

    facts = case.get("facts")
    if facts is not None and not isinstance(facts, dict):
        errors.append(_issue("facts-not-object", "$.facts",
                             "'facts' must be an object of form-specific "
                             "keys"))

    result = {"ok": not errors, "errors": errors, "warnings": warnings}

    # Optional per-form coverage: which declared keys does this case satisfy?
    if form_id:
        froot = forms_root or (OSS_ROOT / "forms")
        mp_path = froot / form_id / "mapping.json"
        if not mp_path.exists():
            result["form"] = {"form_id": form_id, "error": "unknown form"}
        else:
            facts_block = (json.loads(mp_path.read_text()).get("facts")
                           or {"required": [], "used": []})
            missing_req = [k for k in facts_block.get("required", [])
                           if _resolve(case, k) in (None, "")]
            unused = [k for k in facts_block.get("used", [])
                      if _resolve(case, k) in (None, "")]
            result["form"] = {"form_id": form_id,
                              "required_missing": missing_req,
                              "used_unsatisfied": unused}
            if missing_req:
                result["warnings"] = result["warnings"] + [_issue(
                    "required-facts-missing", "$",
                    f"{form_id} declares required facts the case doesn't "
                    f"provide: {missing_req} — the filled form would be "
                    "facially incomplete")]
    return result


def _resolve(case: dict, key: str):
    cur: object = case
    for part in key.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur if isinstance(cur, (str, int, float)) else (cur or None)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("case", type=pathlib.Path,
                    help="canonical fact object JSON")
    ap.add_argument("--form", default=None,
                    help="also check the case against this form's "
                         "required/used facts")
    args = ap.parse_args()
    case = json.loads(args.case.read_text())
    res = preflight_case(case, form_id=args.form)
    print(json.dumps(res, indent=2))
    return 0 if res["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
