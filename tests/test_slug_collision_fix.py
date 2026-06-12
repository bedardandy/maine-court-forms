"""Round-10 cross-semantic slug-collision fixes.

Distinct PDF widget names can slug to one schema field_id (e.g. "Name_2"
and "Name 2" -> name_2). map_form then resolves ONE value for that id and
fill_one fans it out to EVERY widget sharing the id (engine/fill_and_audit
fid_to_widgets). When the two widgets mean different things, that fanout
writes the wrong datum into the off-semantic widget — on FM-216 it swore
the attorney's name into a jurat affiant blank ("Personally appeared the
above named, <attorney>, and made oath ...").

The fix renames the off-semantic schema entry's field_id to a descriptive
slug so each entry binds to only its own widget. The 24 adjudicated groups
(printed-text verified) are pinned below: after the fix no schema may hold
two entries sharing the group's field_id with distinct labels. A behavioral
pin re-renders FM-216 and asserts every jurat affiant blank comes out blank
(repo doctrine: never auto-swear an oath on the affiant's behalf).
"""
import json
import pathlib
import sys
import tempfile
import unittest

import fitz  # PyMuPDF

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from engine.fill_and_audit import fill_one  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
FORMS = ROOT / "forms"

# The 24 adjudicated cross-semantic collision groups: (form, field_id) that
# previously held two distinct-label widgets and must now hold at most one
# label per field_id.
FIXED_GROUPS = [
    ("AD-012", "name_2"),
    ("CR-032", "other"),
    ("CR-287", "to_mmddyyyy_4"),
    ("CV-007", "mailing_address_2"),
    ("FM-043", "other"),
    ("FM-132", "when"),
    ("FM-216", "name_2"),
    ("FM-216", "name_3"),
    ("FM-216", "name_4"),
    ("FM-PC-003", "other"),
    ("GS-009", "name_2"),
    ("GS-016", "other"),
    ("GS-016", "other_2"),
    ("OTH-039", "other_3"),
    ("OTH-039", "other_4"),
    ("OTH-041", "mailing_address_2"),
    ("OTH-041", "mailing_address_3"),
    ("OTH-041", "other_2"),
    ("OTH-042", "county"),
    ("OTH-043", "county"),
    ("OTH-043", "other_2"),
    ("OTH-044", "county"),
    ("OTH-044", "town"),
    ("OTH-045", "mailing_address_2"),
]


def _schema(form_id):
    return json.loads((FORMS / form_id / "schema.json").read_text())


class SlugCollisionDecoupled(unittest.TestCase):
    def test_24_groups_no_dup_field_id_with_distinct_labels(self):
        self.assertEqual(len(FIXED_GROUPS), 24)
        for form_id, fid in FIXED_GROUPS:
            schema = _schema(form_id)
            labels = {f["label"] for f in schema["fields"]
                      if f["field_id"] == fid}
            with self.subTest(form=form_id, field=fid):
                self.assertLessEqual(
                    len(labels), 1,
                    f"{form_id}.{fid} still fans out across distinct "
                    f"widgets {sorted(labels)}")

    def test_renamed_offsemantic_entries_bind_to_one_widget(self):
        # The new descriptive ids each appear exactly once (one widget).
        renamed = {
            "AD-012": "service_block_address_line_2",
            "GS-009": "service_block_address_line_2",
            "FM-216": "jurat_affiant_block2_1",   # one of the jurat ids
            "OTH-042": "other_party_county",
            "OTH-043": "other_party_county",
            "OTH-044": "defendant_residence_town",
            "CV-007": "defendant_attorney_address_line_2",
            "OTH-045": "defendant_attorney_address_line_2",
            "OTH-041": "attorney_address_line_2",
        }
        for form_id, new_id in renamed.items():
            schema = _schema(form_id)
            n = sum(1 for f in schema["fields"]
                    if f["field_id"] == new_id)
            with self.subTest(form=form_id, field=new_id):
                self.assertEqual(n, 1, f"{form_id}.{new_id} count={n}")


class FillBindingPins(unittest.TestCase):
    """Re-render the LIVE_FANOUT forms and read back widget values: the
    canonical widget keeps its value, the off-semantic widget is blank."""

    def _render(self, form_id):
        if not (FORMS / form_id / f"{form_id}.pdf").exists():
            self.skipTest(f"{form_id}.pdf not fetched")
        case = json.loads(
            (FORMS / form_id / "examples" / "sample_case.json").read_text())
        out = pathlib.Path(tempfile.mkdtemp())
        res = fill_one(
            form_id, case, out,
            pdf_path=FORMS / form_id / f"{form_id}.pdf")
        self.assertTrue(res.get("ok"), res.get("error"))
        pdfs = list(out.glob("*.pdf"))
        self.assertTrue(pdfs, "fill produced no PDF")
        doc = fitz.open(pdfs[0])
        vals = {}
        for pg in doc:
            for w in pg.widgets() or []:
                vals[(pg.number, w.field_name)] = w.field_value or ""
        return vals

    def test_ad012_service_block_line_blank_petitioner_name_kept(self):
        vals = self._render("AD-012")
        # p0 petitioner "Name_2" keeps its value; p2 service-block "Name 2"
        # (address-continuation line) is blank.
        self.assertTrue(vals.get((0, "Name_2")),
                        "petitioner name should be filled")
        self.assertEqual(vals.get((2, "Name 2"), ""), "",
                         "service-block line must be blank, not fanned out")

    def test_fm216_jurat_affiant_blanks_render_blank(self):
        vals = self._render("FM-216")
        # the four jurat affiant blanks (lowercase "name 1".."name 4")
        # must never be auto-sworn.
        for pg, nm in [(3, "name 1"), (3, "name 2"),
                       (4, "name 3"), (4, "name 4")]:
            with self.subTest(widget=nm):
                self.assertEqual(
                    vals.get((pg, nm), ""), "",
                    f"FM-216 jurat blank {nm!r} was auto-sworn")
        # sanity: the canonical signatory/attorney name lines still fill.
        self.assertTrue(vals.get((2, "Name_2")))
        self.assertTrue(vals.get((3, "Name_3")))


if __name__ == "__main__":
    unittest.main(verbosity=2)
