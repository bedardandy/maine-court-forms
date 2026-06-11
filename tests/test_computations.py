"""Computed fields (computations.json, yellow light): artifacts + wiring.

Offline parts validate the shipped ``forms/<ID>/computations.json`` files
(load through the shared engine, every key mapped, samples balance); the
verbatim and end-to-end parts are PDF-dependent and skip when the blank is
unfetched (CI).

Shipped surveys: MJ-007 (wage-withholding answer — deduction total,
disposable earnings, the printed .25 multiplier, minimum-wage excess, and
the least-of-three maximum), FM-040 (child support worksheet — combined
adjusted gross income, children x table amount, the three per-child column
totals, the line-14 adjustment subtraction down to "pays as support"), and
GS-017 (child support worksheet — children x table amount, health-insurance
/ child-care / extraordinary-medical column totals, the two parents'
printed line-14 adjustment subtractions down to "pays as support"). The
amount-from-table input on both worksheets is a SUPPLIED fact the filer
reads off the printed Child Support Table — the statutory table is never
embedded. The other printed math in the tree is conditional ("if biweekly,
multiply x 2"), not expressible without inventing a constant (both forms'
line-14 "(Multiply line 8a/8b by line 13)" — line 8 is a percent entry and
the implied divide-by-100 is not a printed literal; GS-017 additionally
prints "line 8b" under BOTH parents' obligations), has unmapped inputs
(GS-017's line-7 widgets are both labeled "b.", so 7c's "(Add lines 7a and
7b.)" has no 7a input), or sits on a recipe-tier pointer-only mapping
(MJ-009 / MJ-015 "for a total of $"), so it is deliberately not declared.
"""
import json
import pathlib
import re
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from maine_forms_engine.computations import (  # noqa: E402
    evaluate, load_computations)
from engine.fill_via_mapping import fill_via_mapping  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
FORMS = ROOT / "forms"


def _forms_with_computations():
    return sorted(d.parent.name for d in FORMS.glob("*/computations.json"))


def _norm(s: str) -> str:
    """Whitespace/leader-dot/fill-in-blank normalization for verbatim match."""
    s = s.replace("—", "-").replace("–", "-")
    s = re.sub(r"_{2,}", " ", s)
    s = re.sub(r"\.{3,}", " ", s)
    return re.sub(r"\s+", " ", s).strip()


class ComputationsArtifacts(unittest.TestCase):
    def test_surveyed_forms_present(self):
        self.assertEqual(_forms_with_computations(),
                         ["FM-040", "GS-017", "MJ-007"])

    def test_loads_and_keys_are_mapped(self):
        for fid in _forms_with_computations():
            with self.subTest(form=fid):
                comp = load_computations(FORMS / fid)  # validates ops/cycles
                mapping = json.loads((FORMS / fid / "mapping.json").read_text())
                mapped = set(mapping["map"].values())
                for key, spec in comp["computed"].items():
                    self.assertIn(key, mapped)
                    for raw in spec["inputs"]:
                        if isinstance(raw, str):
                            self.assertIn(raw.lstrip("-"), mapped)
                    self.assertTrue(spec.get("formula_text", "").strip())

    def test_sample_cases_balance(self):
        for fid in _forms_with_computations():
            with self.subTest(form=fid):
                comp = load_computations(FORMS / fid)
                case = json.loads(
                    (FORMS / fid / "examples" / "sample_case.json").read_text())
                r = evaluate(comp, case)
                self.assertEqual(r["warnings"], [])
                self.assertEqual(r["notes"], [])
                self.assertEqual(r["computed"], [])

    def test_formula_text_is_printed_verbatim(self):
        import fitz
        ran = 0
        for fid in _forms_with_computations():
            pdf = FORMS / fid / f"{fid}.pdf"
            if not pdf.exists():
                continue
            ran += 1
            doc = fitz.open(str(pdf))
            text = _norm(" ".join(p.get_text() for p in doc))
            doc.close()
            comp = load_computations(FORMS / fid)
            for key, spec in comp["computed"].items():
                with self.subTest(form=fid, key=key):
                    self.assertIn(_norm(spec["formula_text"]), text)
        if not ran:
            self.skipTest("no local blank PDFs (CI / unfetched)")


class ComputationsEndToEnd(unittest.TestCase):
    """MJ-007: 'Total of lines 2(a)-(f)' computed vs supplied-contradiction."""

    FORM = "MJ-007"
    TOTAL_WIDGET = "2"  # line (2) total-deductions widget

    def setUp(self):
        if not (FORMS / self.FORM / f"{self.FORM}.pdf").exists():
            self.skipTest("blank not fetched")
        self.case = json.loads(
            (FORMS / self.FORM / "examples" / "sample_case.json").read_text())

    def _widget(self, pdf_path):
        import fitz
        doc = fitz.open(pdf_path)
        try:
            for page in doc:
                for w in page.widgets() or []:
                    if w.field_name == self.TOTAL_WIDGET:
                        return w.field_value
        finally:
            doc.close()
        return None

    def test_omitted_total_is_computed_and_filled(self):
        del self.case["facts"]["total_deductions"]
        # downstream lines that depend on the total stay supplied — they
        # must NOT warn, because the computed total feeds them topologically
        with tempfile.TemporaryDirectory() as td:
            r = fill_via_mapping(self.FORM, self.case, pathlib.Path(td))
            self.assertTrue(r["ok"])
            by_key = {e["key"]: e for e in r["computed_fields"]}
            self.assertEqual(by_key["facts.total_deductions"]["value"],
                             "300.00")
            self.assertEqual(by_key["facts.total_deductions"]["formula_text"],
                             "Total of lines 2(a)-(f)")
            self.assertEqual(r["computation_warnings"], [])
            self.assertEqual(self._widget(r["out_pdf"]), "300.00")

    def test_supplied_contradiction_written_as_is_with_warning(self):
        self.case["facts"]["total_deductions"] = "999.00"
        with tempfile.TemporaryDirectory() as td:
            r = fill_via_mapping(self.FORM, self.case, pathlib.Path(td))
            self.assertTrue(r["ok"])
            warns = {w["key"]: w for w in r["computation_warnings"]}
            w = warns["facts.total_deductions"]
            self.assertEqual(w["code"], "COMPUTATION_MISMATCH")
            self.assertEqual(w["supplied"], "999.00")
            self.assertEqual(w["computed"], "300.00")
            self.assertEqual(w["formula_text"], "Total of lines 2(a)-(f)")
            # supplied value wins in the PDF — never enforced/overridden;
            # and it feeds line (3) downstream, which then warns too
            self.assertEqual(self._widget(r["out_pdf"]), "999.00")
            self.assertIn("facts.disposable_earnings", warns)

    def test_na_court_ordered_payment_skips_least_of_with_note(self):
        # the form prints: line (7) may be N/A — then line (8) is the
        # filer's, with a report note instead of a guess
        self.case["facts"]["court_ordered_payment"] = "N/A"
        del self.case["facts"]["maximum_withholding_amount"]
        with tempfile.TemporaryDirectory() as td:
            r = fill_via_mapping(self.FORM, self.case, pathlib.Path(td))
            self.assertTrue(r["ok"])
            self.assertNotIn("facts.maximum_withholding_amount",
                             {e["key"] for e in r["computed_fields"]})
            self.assertTrue(any(
                n["key"] == "facts.maximum_withholding_amount"
                for n in r.get("computation_notes", [])))
            self.assertIsNone(self._widget(r["out_pdf"]) if
                              self.TOTAL_WIDGET == "8" else None)


class Gs017EndToEnd(unittest.TestCase):
    """GS-017: line 9c's children-x-table product, the 'Total: 10./11.'
    column sums, and the line-14 'pays as support' difference, computed vs
    supplied-contradiction."""

    FORM = "GS-017"

    def setUp(self):
        if not (FORMS / self.FORM / f"{self.FORM}.pdf").exists():
            self.skipTest("blank not fetched")
        self.case = json.loads(
            (FORMS / self.FORM / "examples" / "sample_case.json").read_text())

    def _widget(self, pdf_path, name):
        import fitz
        doc = fitz.open(pdf_path)
        try:
            for page in doc:
                for w in page.widgets() or []:
                    if w.field_name == name:
                        return w.field_value
        finally:
            doc.close()
        return None

    def test_omitted_totals_are_computed_and_filled(self):
        for k in ("child_care_total", "medical_expense_total",
                  "parent1_pays_as_support", "parent2_pays_as_support"):
            del self.case["facts"][k]
        with tempfile.TemporaryDirectory() as td:
            r = fill_via_mapping(self.FORM, self.case, pathlib.Path(td))
            self.assertTrue(r["ok"])
            by_key = {e["key"]: e["value"] for e in r["computed_fields"]}
            self.assertEqual(by_key["facts.child_care_total"], "600.00")
            self.assertEqual(by_key["facts.parent1_pays_as_support"],
                             "100.00")
            self.assertEqual(r["computation_warnings"], [])
            # widget 11 is the printed 'Total: 11.' box; undefined_26 is
            # the 'Parent 1 pays as support = $' box
            self.assertEqual(self._widget(r["out_pdf"], "11"), "600.00")
            self.assertEqual(self._widget(r["out_pdf"], "undefined_26"),
                             "100.00")

    def test_omitted_9c_and_insurance_total_are_computed_and_filled(self):
        # line 9c: children x amount-from-table (the table value is a
        # supplied fact, read off the printed Child Support Table); line
        # 10's printed 'Total: 10.' column sum
        for k in ("basic_weekly_support_total",
                  "total_weekly_health_insurance_cost"):
            del self.case["facts"][k]
        with tempfile.TemporaryDirectory() as td:
            r = fill_via_mapping(self.FORM, self.case, pathlib.Path(td))
            self.assertTrue(r["ok"])
            by_key = {e["key"]: e["value"] for e in r["computed_fields"]}
            self.assertEqual(by_key["facts.basic_weekly_support_total"],
                             "170.00")  # 2 children x 85.00 from table
            self.assertEqual(
                by_key["facts.total_weekly_health_insurance_cost"], "150.00")
            self.assertEqual(r["computation_warnings"], [])
            self.assertEqual(self._widget(r["out_pdf"], "9c"), "170.00")
            self.assertEqual(self._widget(r["out_pdf"], "10"), "150.00")

    def test_supplied_9c_contradiction_warns_supplied_wins(self):
        self.case["facts"]["basic_weekly_support_total"] = "999.00"
        with tempfile.TemporaryDirectory() as td:
            r = fill_via_mapping(self.FORM, self.case, pathlib.Path(td))
            self.assertTrue(r["ok"])
            warns = {w["key"]: w for w in r["computation_warnings"]}
            w = warns["facts.basic_weekly_support_total"]
            self.assertEqual(w["code"], "COMPUTATION_MISMATCH")
            self.assertEqual(w["supplied"], "999.00")
            self.assertEqual(w["computed"], "170.00")
            # supplied value wins in the PDF — never enforced/overridden
            self.assertEqual(self._widget(r["out_pdf"], "9c"), "999.00")

    def test_supplied_contradiction_written_as_is_with_warning(self):
        self.case["facts"]["child_care_total"] = "999.00"
        with tempfile.TemporaryDirectory() as td:
            r = fill_via_mapping(self.FORM, self.case, pathlib.Path(td))
            self.assertTrue(r["ok"])
            warns = {w["key"]: w for w in r["computation_warnings"]}
            w = warns["facts.child_care_total"]
            self.assertEqual(w["code"], "COMPUTATION_MISMATCH")
            self.assertEqual(w["supplied"], "999.00")
            self.assertEqual(w["computed"], "600.00")
            self.assertEqual(w["formula_text"], "Total: 11.")
            # supplied value wins in the PDF — never enforced/overridden
            self.assertEqual(self._widget(r["out_pdf"], "11"), "999.00")


class Fm040EndToEnd(unittest.TestCase):
    """FM-040: the three 'Total: 10./11./12.' column sums and the line-14
    'Non-Primary Care Provider pays as support' difference, computed vs
    supplied-contradiction."""

    FORM = "FM-040"

    def setUp(self):
        if not (FORMS / self.FORM / f"{self.FORM}.pdf").exists():
            self.skipTest("blank not fetched")
        self.case = json.loads(
            (FORMS / self.FORM / "examples" / "sample_case.json").read_text())

    def _widget(self, pdf_path, name):
        import fitz
        doc = fitz.open(pdf_path)
        try:
            for page in doc:
                for w in page.widgets() or []:
                    if w.field_name == name:
                        return w.field_value
        finally:
            doc.close()
        return None

    def test_omitted_totals_are_computed_and_filled(self):
        for k in ("total_weekly_health_insurance_cost", "child_care_total",
                  "total_extraordinary_medical_expenses",
                  "non_primary_pays_as_support"):
            del self.case["facts"][k]
        with tempfile.TemporaryDirectory() as td:
            r = fill_via_mapping(self.FORM, self.case, pathlib.Path(td))
            self.assertTrue(r["ok"])
            by_key = {e["key"]: e["value"] for e in r["computed_fields"]}
            self.assertEqual(
                by_key["facts.total_weekly_health_insurance_cost"], "150.00")
            self.assertEqual(by_key["facts.child_care_total"], "600.00")
            self.assertEqual(
                by_key["facts.total_extraordinary_medical_expenses"],
                "600.00")
            self.assertEqual(by_key["facts.non_primary_pays_as_support"],
                             "200.00")  # 300 - 30 - 60 - 10
            self.assertEqual(r["computation_warnings"], [])
            # 'Total 12' is the printed 'Total: 12.' box; 'support' is the
            # 'Non-Primary Care Provider pays as support = $' box
            self.assertEqual(self._widget(r["out_pdf"], "10"), "150.00")
            self.assertEqual(self._widget(r["out_pdf"], "11"), "600.00")
            self.assertEqual(self._widget(r["out_pdf"], "Total 12"),
                             "600.00")
            self.assertEqual(self._widget(r["out_pdf"], "support"), "200.00")

    def test_supplied_contradiction_written_as_is_with_warning(self):
        self.case["facts"]["non_primary_pays_as_support"] = "999.00"
        with tempfile.TemporaryDirectory() as td:
            r = fill_via_mapping(self.FORM, self.case, pathlib.Path(td))
            self.assertTrue(r["ok"])
            warns = {w["key"]: w for w in r["computation_warnings"]}
            w = warns["facts.non_primary_pays_as_support"]
            self.assertEqual(w["code"], "COMPUTATION_MISMATCH")
            self.assertEqual(w["supplied"], "999.00")
            self.assertEqual(w["computed"], "200.00")
            # supplied value wins in the PDF — never enforced/overridden
            self.assertEqual(self._widget(r["out_pdf"], "support"), "999.00")


if __name__ == "__main__":
    unittest.main()
