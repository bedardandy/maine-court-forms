"""Full-fill smoke over mapping-tier forms that have a local blank PDF.

PDF-DEPENDENT: blank PDFs are not shipped (fetched from the official portal),
so each case skips when its blank is absent — i.e. this runs in full locally
and no-ops in CI. Catches writer/engine crashes that the recipe-level smoke
(PDF-free) can't see, and pins the OTH-029 runtime field-split.
"""
import sys
import unittest
import pathlib
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from tests.helpers import mapping_forms, sample_case, has_pdf


class FillSmoke(unittest.TestCase):
    def test_mapping_forms_fill_without_crash(self):
        from engine.fill_via_mapping import fill_via_mapping
        forms = [f for f in mapping_forms() if has_pdf(f)]
        if not forms:
            self.skipTest("no local blank PDFs (CI / unfetched)")
        failures = []
        with tempfile.TemporaryDirectory() as td:
            out = pathlib.Path(td)
            for fid in forms:
                with self.subTest(form=fid):
                    try:
                        r = fill_via_mapping(fid, sample_case(fid), out / fid)
                        if not r.get("ok"):
                            failures.append((fid, r.get("error")))
                    except Exception as e:  # noqa: BLE001
                        failures.append((fid, repr(e)))
        self.assertEqual(failures, [], f"fills crashed/failed: {failures}")

    def test_oth029_shared_field_split_fires(self):
        """OTH-029 `2_5`/`2_6` are split so child data doesn't fan to pg12/14."""
        if not has_pdf("OTH-029"):
            self.skipTest("OTH-029 blank PDF not present")
        from engine.fill_via_mapping import fill_via_mapping
        with tempfile.TemporaryDirectory() as td:
            r = fill_via_mapping("OTH-029", sample_case("OTH-029"),
                                 pathlib.Path(td))
        self.assertTrue(r.get("ok"))
        self.assertEqual(r.get("fields_split"), 2,
                         "expected the 2_5 + 2_6 field splits to apply")


if __name__ == "__main__":
    unittest.main(verbosity=2)
