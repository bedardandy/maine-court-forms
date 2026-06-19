"""EVAL — Assumption: the per-form logic.json artifacts are valid, drift-free,
reference real forms/fields, and the authored rules fire on the right cases and
stay silent otherwise (positive + negative controls).

Pass bar: zero violations; every control behaves as specified.
"""
from __future__ import annotations

import json
import unittest

from evals.common import FORMS, all_mappings
from tools.derive_logic import logic_for_form
from tools.logic_engine import evaluate_rules

_KINDS = {"conditional_required", "attachment", "companion_form",
          "incompatible", "value_inference", "note"}


def _logic(fid):
    return json.loads((FORMS / fid / "logic.json").read_text())


class TestArtifactValidity(unittest.TestCase):
    def test_every_form_has_logic(self):
        missing = [f for f in all_mappings()
                   if not (FORMS / f / "logic.json").exists()]
        self.assertEqual(missing, [], f"forms missing logic.json: {missing[:20]}")

    def test_rules_well_formed(self):
        bad = []
        for fid in all_mappings():
            for r in _logic(fid).get("rules", []):
                if not r.get("id") or r.get("kind") not in _KINDS:
                    bad.append((fid, r.get("id"), r.get("kind")))
        self.assertEqual(bad, [], f"malformed rules: {bad[:20]}")

    def test_no_drift_from_deriver(self):
        drift = [f for f in all_mappings()
                 if logic_for_form(f)["rules"] != _logic(f).get("rules")]
        self.assertEqual(
            drift, [],
            f"{len(drift)} logic.json drifted — re-run "
            f"tools/derive_logic.py --all: {drift[:20]}")

    def test_companion_and_field_refs_are_real(self):
        known = set(all_mappings())
        bad = []
        for fid in all_mappings():
            schema_fids = {f["field_id"] for f in
                           json.loads((FORMS / fid / "schema.json").read_text())
                           .get("fields", [])}
            for r in _logic(fid).get("rules", []):
                if r.get("kind") == "companion_form":
                    target = (r.get("then") or {}).get("form")
                    if target and target not in known:
                        bad.append((fid, r["id"], "unknown form", target))
                # any field:<id> operand must be a real field of this form
                for ref in _field_refs(r.get("when")):
                    if ref not in schema_fids:
                        bad.append((fid, r["id"], "unknown field", ref))
        self.assertEqual(bad, [], f"dangling references: {bad[:20]}")


class TestAuthoredControls(unittest.TestCase):
    """Positive + negative controls for the hand-authored seed rules."""

    def _fired(self, fid, case):
        return {w["rule_id"] for w in evaluate_rules(_logic(fid), case)}

    def test_pa001_confidential_and_relationship(self):
        fired = self._fired("PA-001", {"facts": {
            "confidential_address": True,
            "relationship_description": "my next-door neighbor"}})
        self.assertIn("pa001-companion-pa005", fired)        # always
        self.assertIn("pa001-companion-pa015-confidential", fired)
        self.assertIn("pa001-relationship-suggests-pfh", fired)
        # negative: a spouse with public address -> only the always-on PA-005
        fired2 = self._fired("PA-001", {"facts": {
            "relationship_description": "my former husband"}})
        self.assertEqual(fired2, {"pa001-companion-pa005"})

    def test_fm004_children_trigger_support_forms(self):
        fired = self._fired("FM-004", {"parties": {"child_1": {"full_name": "K"}}})
        self.assertEqual(
            fired, {"fm004-children-require-fm050", "fm004-children-require-fm040"})
        self.assertEqual(self._fired("FM-004", {"parties": {}}), set())

    def test_mj007_garnishment_cap(self):
        over = self._fired("MJ-007", {"facts": {
            "maximum_withholding_amount": "500",
            "twenty_five_percent_amount": "300",
            "disposable_earnings": "1200"}})
        self.assertIn("mj007-withholding-not-over-25pct", over)
        ok = self._fired("MJ-007", {"facts": {
            "maximum_withholding_amount": "300",
            "twenty_five_percent_amount": "300",
            "disposable_earnings": "1200"}})
        self.assertEqual(ok, set())

    def test_fm040_adjusted_not_over_gross(self):
        bad = self._fired("FM-040", {"facts": {
            "adjusted_gross_income_primary": "5000",
            "gross_income_primary": "4000"}})
        self.assertIn("fm040-adjusted-not-over-gross-primary", bad)
        good = self._fired("FM-040", {"facts": {
            "adjusted_gross_income_primary": "3500",
            "gross_income_primary": "4000"}})
        self.assertEqual(good, set())

    def test_cv287_documentation_attachments(self):
        fired = self._fired("CV-287", {"facts": {
            "current_owner_name": "Acme LLC", "date_assignment_2": "2023-01-01"}})
        self.assertIn("cv287-attach-debt-agreement", fired)
        self.assertIn("cv287-attach-chain-of-title", fired)
        self.assertIn("cv287-multiple-assignments-need-each", fired)

    def test_cr004_realestate_bond_needs_property(self):
        fired = self._fired("CR-004", {"facts": {"lien_amount_numeric": "10000"}})
        self.assertIn("cr004-realestate-bond-needs-property", fired)
        # negative: property supplied -> rule satisfied (silent)
        ok = self._fired("CR-004", {"facts": {
            "lien_amount_numeric": "10000", "property_street": "1 Main St",
            "property_town": "Portland", "property_county": "Cumberland"}})
        self.assertNotIn("cr004-realestate-bond-needs-property", ok)


class TestPreflightWiring(unittest.TestCase):
    def test_preflight_surfaces_logic_warnings(self):
        from tools.preflight import preflight_case
        res = preflight_case(
            {"matter": {}, "parties": {"plaintiff": {"full_name": "A"},
                                       "defendant": {"full_name": "B"},
                                       "child_1": {"full_name": "K"}}},
            form_id="FM-004")
        logic = [w for w in res["warnings"]
                 if str(w["code"]).startswith("logic-")]
        self.assertTrue(any("FM-050" in w["message"] for w in logic),
                        f"expected FM-050 companion warning; got {logic}")


def _field_refs(expr, acc=None):
    acc = acc if acc is not None else []
    if isinstance(expr, dict):
        for k, v in expr.items():
            if k == "var" and isinstance(v, str) and v.startswith("field:"):
                acc.append(v[6:])
            elif isinstance(v, str) and v.startswith("field:") \
                    and k in ("present", "absent", "truthy"):
                acc.append(v[6:])
            else:
                _field_refs(v, acc)
    elif isinstance(expr, list):
        for e in expr:
            _field_refs(e, acc)
    return acc


if __name__ == "__main__":
    unittest.main()
