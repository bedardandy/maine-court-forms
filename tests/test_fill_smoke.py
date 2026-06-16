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

    def test_oth044_respondent_location_town_split_fires(self):
        """OTH-044 `Town` is one AcroForm field reused as the court-location
        caption (1-idx pp.4/7/11/12/15) AND the "Defendant/Respondent Location
        (Town)" caption (1-idx pp.13/14). mapping.json maps `town` ->
        `matter.court_location`, so without a split the courthouse town fans
        onto the two respondent-location boxes (a false statement). The split
        detaches + blanks those two appearances. Asserts both that the split
        fires and that, in the rendered fill, the pp.13/14 respondent Town
        boxes are blank while a court-location Town box (p4) still shows the
        court_location value.
        """
        if not has_pdf("OTH-044"):
            self.skipTest("OTH-044 blank PDF not present")
        import json
        import fitz
        from engine.fill_via_mapping import fill_via_mapping
        from tests.helpers import pdf_path

        # Fill from the raw CANONICAL fact object (the contract resolve_mapping
        # consumes — `matter.court_location` is a canonical path; the engine
        # case shape from sample_case() flattens `matter` away).
        case = json.loads(
            (pdf_path("OTH-044").parent / "examples" / "sample_case.json")
            .read_text())
        court_loc = case["matter"]["court_location"]  # 'Portland' in the sample

        # The two "Defendant/Respondent Location (Town)" appearances are the
        # `Town` kid widgets on 1-idx pp.13/14; locate every `Town` rect from
        # the BLANK so we can read the printed value inside each after the fill.
        town_rects = {}  # 1-idx page -> [fitz.Rect, ...]
        blank = fitz.open(str(pdf_path("OTH-044")))
        try:
            for pno, page in enumerate(blank):
                for w in page.widgets() or []:
                    if w.field_name == "Town":
                        town_rects.setdefault(pno + 1, []).append(
                            fitz.Rect(w.rect))
        finally:
            blank.close()
        # Sanity: the packet has the 7 Town widgets we split against.
        self.assertEqual(sorted(town_rects), [4, 7, 11, 12, 13, 14, 15])

        with tempfile.TemporaryDirectory() as td:
            r = fill_via_mapping("OTH-044", case, pathlib.Path(td))
            self.assertTrue(r.get("ok"))
            self.assertEqual(
                r.get("fields_split"), 2,
                "expected the two respondent-location Town splits to apply")

            def town_text(doc, page_1idx):
                """Words whose centre falls inside a Town rect on this page."""
                page = doc[page_1idx - 1]
                hits = []
                for rect in town_rects[page_1idx]:
                    for w in page.get_text("words"):
                        cx, cy = (w[0] + w[2]) / 2, (w[1] + w[3]) / 2
                        if rect.contains(fitz.Point(cx, cy)):
                            hits.append(w[4])
                return hits

            doc = fitz.open(r["out_pdf"])
            try:
                # The two "Defendant/Respondent Location" Town boxes are blank
                # (the courthouse town no longer fans onto the respondent).
                for p in (13, 14):
                    self.assertNotIn(
                        court_loc, town_text(doc, p),
                        f"p{p} respondent-location Town should be blank after "
                        "the split (court_location must not fan here)")
                # A court-location Town box still carries the court_location.
                self.assertIn(
                    court_loc, town_text(doc, 4),
                    "p4 court-location Town should still show court_location")
            finally:
                doc.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
