"""Canonical-case preflight (tools/preflight.py +
catalog/canonical_case.schema.json).

The shipped sample cases must pass clean; the known silent-loss mistakes
(wrong role vocabulary, unknown top-level keys, engine-shape cases,
non-scalar values) must be flagged with machine-readable issues and
suggestions.
"""
import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.preflight import preflight_case  # noqa: E402


def _codes(issues):
    return {i["code"] for i in issues}


class TestPreflight(unittest.TestCase):
    def test_all_sample_cases_pass(self):
        """Every shipped examples/sample_case.json validates clean."""
        n = 0
        for p in sorted((ROOT / "forms").glob("*/examples/sample_case.json")):
            with self.subTest(form=p.parent.parent.name):
                res = preflight_case(json.loads(p.read_text()))
                self.assertTrue(res["ok"], res["errors"])
                self.assertEqual(res["warnings"], [])
                n += 1
        self.assertGreater(n, 300)

    def test_role_vocabulary_suggestion(self):
        res = preflight_case({"matter": {},
                              "parties": {"lawyer": {"full_name": "P L"}}})
        self.assertFalse(res["ok"])
        err = next(e for e in res["errors"]
                   if e["code"] == "unknown-party-role")
        self.assertEqual(err["suggestion"], "parties.attorney")
        # petitioner/respondent map to the caption roles this library uses
        res = preflight_case({"matter": {},
                              "parties": {"petitioner": {}, "respondent": {}}})
        sugs = {e.get("suggestion") for e in res["errors"]}
        self.assertIn("parties.plaintiff", sugs)
        self.assertIn("parties.defendant", sugs)

    def test_child_roles_are_valid(self):
        res = preflight_case({"matter": {},
                              "parties": {"child_1": {"full_name": "S D"},
                                          "child_12": {"full_name": "A D"}}})
        self.assertTrue(res["ok"], res["errors"])

    def test_unknown_top_level_key(self):
        res = preflight_case({"matter": {}, "extra_block": 1})
        self.assertIn("unknown-top-level-key", _codes(res["errors"]))

    def test_engine_shape_rejected(self):
        res = preflight_case({"court": {"county": "Cumberland"},
                              "docket_no": "CV-2024-1"})
        self.assertIn("engine-shape", _codes(res["errors"]))

    def test_unknown_attr_and_matter_key_warn(self):
        res = preflight_case({"matter": {"county": "Cumberland"},
                              "party": {"dob": "1990-01-01"}})
        self.assertTrue(res["ok"], "vocabulary slips warn, not fail")
        warn_codes = _codes(res["warnings"])
        self.assertIn("unknown-matter-key", warn_codes)
        self.assertIn("unknown-party-attr", warn_codes)
        sugs = {w.get("suggestion") for w in res["warnings"]}
        self.assertIn("matter.court_county", sugs)
        self.assertIn("$.party.date_of_birth", sugs)

    def test_non_scalar_value_is_error(self):
        res = preflight_case(
            {"matter": {}, "party": {"full_name": ["Jane", "Doe"]}})
        self.assertIn("non-scalar-value", _codes(res["errors"]))

    def test_form_required_facts_coverage(self):
        res = preflight_case({"matter": {}}, form_id="PA-001")
        self.assertIn("parties.plaintiff.full_name",
                      res["form"]["required_missing"])
        self.assertIn("required-facts-missing", _codes(res["warnings"]))
        full = json.loads(
            (ROOT / "forms/PA-001/examples/sample_case.json").read_text())
        res = preflight_case(full, form_id="PA-001")
        self.assertEqual(res["form"]["required_missing"], [])

    def test_schema_file_agrees_with_validator(self):
        """The JSON Schema contract stays in sync with the validator's
        vocabulary (spot checks; jsonschema isn't a dependency)."""
        schema = json.loads(
            (ROOT / "catalog/canonical_case.schema.json").read_text())
        from tools import preflight as pf
        for k in pf.TOP_KEYS + pf.TOP_KEYS_EXTRA:
            self.assertIn(k, schema["properties"], k)
        party_props = schema["$defs"]["party"]["properties"]
        self.assertEqual(set(party_props), set(pf.PARTY_ATTRS))
        matter_props = schema["properties"]["matter"]["properties"]
        self.assertEqual(set(matter_props), set(pf.MATTER_KEYS))
        pattern = schema["properties"]["parties"]["propertyNames"]["pattern"]
        for role in pf.PARTY_ROLES:
            self.assertIn(role, pattern)


if __name__ == "__main__":
    unittest.main()
