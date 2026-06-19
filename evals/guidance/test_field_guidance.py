"""EVAL — Assumption: every fillable field carries correct, consistent
fill-value guidance (what kind of text belongs there, required-ness, choice
conditionals).

The deriver (tools/derive_field_guidance.py) writes forms/<ID>/fill_guidance.json
from schema/mapping/constraints, consistent with the fill engine. These evals
prove the artifact is complete, in-vocabulary, drift-free, and — crucially —
that the declared value_type agrees with the value the engine actually resolves
(counter-assertions: a field mapped to a `.zip` key must be typed `zip`, etc.).

Metrics: per-field coverage, vocabulary, mapping/type agreement, required and
conditional agreement, date-format correctness.
Pass bar: zero violations.
"""
from __future__ import annotations

import json
import unittest

from evals.common import FORMS, all_mappings
from tools.derive_field_guidance import (VALUE_TYPES, _ATTR_TO_TYPE,
                                         guidance_for_form)


def _guidance(form_id: str) -> dict:
    p = FORMS / form_id / "fill_guidance.json"
    return json.loads(p.read_text())


def _schema(form_id: str) -> dict:
    return json.loads((FORMS / form_id / "schema.json").read_text())


class TestCoverageAndVocabulary(unittest.TestCase):
    def test_every_form_has_guidance(self):
        missing = [fid for fid in all_mappings()
                   if not (FORMS / fid / "fill_guidance.json").exists()]
        self.assertEqual(missing, [],
                         f"forms missing fill_guidance.json: {missing[:20]}")

    def test_every_field_has_in_vocab_entry(self):
        bad = []
        for fid in all_mappings():
            g = _guidance(fid)["fields"]
            for f in _schema(fid).get("fields", []):
                e = g.get(f["field_id"])
                if e is None:
                    bad.append((fid, f["field_id"], "no entry"))
                elif e["value_type"] not in VALUE_TYPES:
                    bad.append((fid, f["field_id"], e["value_type"]))
                elif not e.get("guidance"):
                    bad.append((fid, f["field_id"], "no guidance text"))
        self.assertEqual(bad, [], f"coverage/vocab violations: {bad[:20]}")

    def test_no_drift_from_deriver(self):
        # Committed artifact must equal a fresh derivation (re-run the deriver
        # to adopt intended changes).
        drift = []
        for fid in all_mappings():
            fresh = guidance_for_form(fid)
            committed = _guidance(fid)
            if fresh["fields"] != committed["fields"]:
                drift.append(fid)
        self.assertEqual(
            drift, [],
            f"{len(drift)} guidance artifacts drifted — re-run "
            f"tools/derive_field_guidance.py --all: {drift[:20]}")


class TestTypeConsistency(unittest.TestCase):
    def test_mapped_field_type_matches_canonical_key(self):
        # Counter-assertion: where a field is mapped to a canonical key with an
        # unambiguous type, the guidance must agree (no zip typed as phone).
        bad = []
        for fid in all_mappings():
            m = all_mappings()[fid].get("map") or {}
            g = _guidance(fid)["fields"]
            for field_id, key in m.items():
                expected = _expected_type_for_key(key)
                if expected is None or field_id not in g:
                    continue
                got = g[field_id]["value_type"]
                if got != expected:
                    bad.append((fid, field_id, key, expected, got))
        self.assertEqual(bad, [], f"type/key mismatches: {bad[:20]}")

    def test_checkbox_fields_typed_checkbox(self):
        bad = []
        for fid in all_mappings():
            g = _guidance(fid)["fields"]
            for f in _schema(fid).get("fields", []):
                if f.get("type") == "checkbox" \
                        and g.get(f["field_id"], {}).get("value_type") \
                        != "checkbox":
                    bad.append((fid, f["field_id"]))
        self.assertEqual(bad, [], f"checkbox not typed checkbox: {bad[:20]}")

    def test_signature_blanks_are_wetink(self):
        # A field typed `signature` is a wet-ink/electronic signature blank:
        # never required, and if mapped at all only to a `.signature` key.
        # (A signature-block subfield the engine fills with a date or a typed
        # name is classified by its mapping instead and may be required.)
        bad = []
        for fid in all_mappings():
            m = all_mappings()[fid].get("map") or {}
            for field_id, e in _guidance(fid)["fields"].items():
                if e["value_type"] != "signature":
                    continue
                mapped = m.get(field_id)
                if e.get("required") or (mapped
                                         and not mapped.endswith(".signature")):
                    bad.append((fid, field_id, e.get("required"), mapped))
        self.assertEqual(bad, [], f"signature wet-ink violations: {bad[:20]}")

    def test_unmapped_signature_category_stays_signature(self):
        bad = []
        for fid in all_mappings():
            m = all_mappings()[fid].get("map") or {}
            g = _guidance(fid)["fields"]
            for f in _schema(fid).get("fields", []):
                if f.get("category") == "signature" \
                        and f["field_id"] not in m \
                        and g.get(f["field_id"], {}).get("value_type") \
                        != "signature":
                    bad.append((fid, f["field_id"]))
        self.assertEqual(bad, [], f"unmapped signature mis-typed: {bad[:20]}")

    def test_date_format_is_valid_and_minimal(self):
        # Every date field carries a format; us_slash only when the field_id
        # signals mm/dd/yyyy (mirrors engine _date_format_hint).
        bad = []
        for fid in all_mappings():
            for field_id, e in _guidance(fid)["fields"].items():
                if e["value_type"] != "date":
                    continue
                fmt = e.get("format")
                if fmt not in ("us_slash", "iso"):
                    bad.append((fid, field_id, fmt))
                elif fmt == "us_slash" and "mmddyyyy" not in field_id.lower() \
                        and "mm_dd" not in field_id.lower() \
                        and "mm/dd" not in field_id.lower():
                    bad.append((fid, field_id, "us_slash w/o mmddyyyy token"))
        self.assertEqual(bad, [], f"date-format violations: {bad[:20]}")


class TestRequiredAndConditional(unittest.TestCase):
    def test_required_fields_match_facts_required(self):
        # A field is required iff it is mapped to one of the form's
        # facts.required keys. Both directions.
        bad = []
        for fid in all_mappings():
            mp = all_mappings()[fid]
            req_keys = set(((mp.get("facts") or {}).get("required")) or [])
            m = mp.get("map") or {}
            g = _guidance(fid)["fields"]
            for field_id, e in g.items():
                mapped = m.get(field_id)
                should = bool(mapped and mapped in req_keys)
                if bool(e.get("required")) != should:
                    bad.append((fid, field_id, mapped, e.get("required"),
                                should))
        self.assertEqual(bad, [], f"required mismatches: {bad[:20]}")

    def test_conditional_covers_constraint_members(self):
        # Every mutually_exclusive member in constraints.json must be flagged
        # conditional in the guidance with the same group.
        bad = []
        for fid in all_mappings():
            cpath = FORMS / fid / "constraints.json"
            if not cpath.exists():
                continue
            cfg = json.loads(cpath.read_text())
            g = _guidance(fid)["fields"]
            for grp in cfg.get("mutually_exclusive") or []:
                keys = grp["keys"] if isinstance(grp, dict) else grp
                for k in keys:
                    cond = g.get(k, {}).get("conditional")
                    if not cond or cond.get("rule") != "exactly_one_of":
                        bad.append((fid, k, cond))
        self.assertEqual(bad, [], f"conditional coverage gaps: {bad[:20]}")


class TestPreflightTypeWarnings(unittest.TestCase):
    """The guidance feeds preflight: a value that mismatches its field's type
    is flagged (warning, never error), and a good value is silent."""

    def test_bad_value_flagged(self):
        from tools.preflight import preflight_case
        # CV-007 maps parties.plaintiff.zip -> a zip field; feed a phone number.
        case = {
            "matter": {"court_county": "Cumberland"},
            "parties": {
                "plaintiff": {"full_name": "Susan Pelletier",
                              "zip": "207-555-0142"},
                "defendant": {"full_name": "Carl Whitman"},
            },
        }
        res = preflight_case(case, form_id="CV-007")
        self.assertTrue(res["ok"], "type issues must be warnings, not errors")
        vt = [w for w in res["warnings"] if w["code"] == "value-type"]
        self.assertTrue(
            any("zip" in w["message"] for w in vt),
            f"expected a zip value-type warning; got {vt}")

    def test_good_value_silent(self):
        from tools.preflight import preflight_case
        case = {
            "matter": {"court_county": "Cumberland"},
            "parties": {
                "plaintiff": {"full_name": "Susan Pelletier", "zip": "04240"},
                "defendant": {"full_name": "Carl Whitman"},
            },
        }
        res = preflight_case(case, form_id="CV-007")
        vt = [w for w in res["warnings"] if w["code"] == "value-type"]
        self.assertEqual(vt, [], f"unexpected value-type warnings: {vt}")


def _expected_type_for_key(key: str):
    """The unambiguous expected value_type for a canonical mapping key, or
    None if the key's type is not strict enough to assert."""
    if key == "today()":
        return "date"
    if key.startswith(("parties.", "party.")):
        return _ATTR_TO_TYPE.get(key.rsplit(".", 1)[-1])
    if key.startswith("matter."):
        return {"court_county": "county", "court_location": "court_location",
                "docket_number": "docket", "case_number": "case_number",
                "filing_date": "date", "event_date": "date"}.get(
                    key.split(".", 1)[1])
    return None  # facts.* are heuristic, not strict — don't assert


if __name__ == "__main__":
    unittest.main()
