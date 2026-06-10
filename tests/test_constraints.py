"""Checkbox-paradox constraints (yellow light): shipped artifacts + wiring.

Offline parts validate every shipped ``forms/<ID>/constraints.json`` against
its schema and exercise the evaluator; the fill_one wiring test is
PDF-dependent and skips when the blank is unfetched (CI)."""
import json
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from maine_forms_engine.constraints import evaluate, load_constraints  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
FORMS = ROOT / "forms"


def _forms_with_constraints():
    return sorted(d.name for d in FORMS.iterdir()
                  if d.is_dir() and (d / "constraints.json").exists())


class ConstraintsArtifacts(unittest.TestCase):
    def test_harvested_forms_present(self):
        # the criminal-caption court selector is the anchor class
        found = _forms_with_constraints()
        for fid in ("CR-006", "CR-009", "CR-198", "CR-228"):
            self.assertIn(fid, found)

    def test_keys_are_real_checkbox_field_ids(self):
        for fid in _forms_with_constraints():
            cons = load_constraints(FORMS / fid)
            schema = json.loads((FORMS / fid / "schema.json").read_text())
            checkboxes = {f["field_id"] for f in schema.get("fields", [])
                          if f.get("type") == "checkbox"}
            for group in cons.get("mutually_exclusive", []):
                keys = group["keys"] if isinstance(group, dict) else group
                with self.subTest(form=fid, keys=keys):
                    self.assertGreaterEqual(len(keys), 2)
                    for k in keys:
                        self.assertIn(k, checkboxes,
                                      f"{fid}: {k} is not a schema checkbox")

    def test_severity_is_always_warning(self):
        for fid in _forms_with_constraints():
            cons = load_constraints(FORMS / fid)
            w = evaluate(cons, {k: "X"
                                for g in cons["mutually_exclusive"]
                                for k in (g["keys"] if isinstance(g, dict)
                                          else g)})
            self.assertTrue(w, fid)  # everything checked at once must fire
            for x in w:
                self.assertEqual(x["severity"], "warning")
                self.assertEqual(x["code"], "MUTUALLY_EXCLUSIVE")

    def test_court_selector_fires_and_single_court_is_clean(self):
        cons = load_constraints(FORMS / "CR-228")
        both = {"superior_court": "X", "district_court": "X"}
        w = evaluate(cons, both)
        self.assertEqual(len(w), 1)
        self.assertEqual(sorted(w[0]["keys"]),
                         ["district_court", "superior_court"])
        self.assertEqual(evaluate(cons, {"superior_court": "X"}), [])
        # negative tokens are not selections
        self.assertEqual(evaluate(cons, {"superior_court": "X",
                                         "district_court": "no"}), [])


class FillOneWiring(unittest.TestCase):
    """PDF-dependent: skips when the CR-228 blank is unfetched (CI)."""

    def test_fill_one_surfaces_constraint_warnings_key(self):
        pdf = FORMS / "CR-228" / "CR-228.pdf"
        if not pdf.exists():
            self.skipTest("CR-228 blank PDF not present (CI / unfetched)")
        from engine.fill_and_audit import fill_one
        with tempfile.TemporaryDirectory() as td:
            r = fill_one("CR-228", {"court": {"type": "superior"}},
                         pathlib.Path(td),
                         schema_path=FORMS / "CR-228" / "schema.json",
                         pdf_path=pdf)
            self.assertTrue(r["ok"], r)
            # constraints.json exists -> the key is present; a single court
            # selection is clean (warnings only, never blocking)
            self.assertIn("constraint_warnings", r)
            self.assertEqual(r["constraint_warnings"], [])
            kv_art = json.loads(
                (pathlib.Path(td) / "CR-228.kv.json").read_text())
            self.assertIn("constraint_warnings", kv_art)


if __name__ == "__main__":
    unittest.main(verbosity=2)
