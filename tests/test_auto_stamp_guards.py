"""Round-11 auto-stamp guards: the generic narrative_derived mapper must
stop over-applying a party datum onto fields that belong to the notary's
oath certificate (branch 5) or to the wrong party / a child / an
old-new-address pair (branch 4).

Two engine paths were hardened:

  BRANCH 5 — notary name-stamp (REMOVED in both places):
    * engine/build_kv_map.py map_form: the narrative_derived
      "personally appeared / before me / appeared above named" branch is
      gone, so every "Personally appeared the above-named ___" jurat
      affiant blank (and FDP-006's "before mediation" substring
      false-positives) falls through to blank.
    * engine/fill_and_audit.py _apply_notary_block: the
      _NOTARY_SIGNER_FIDS fill loop is gone. The county / state fills and
      the explicitly-gated perjury checkbox stay.
    Repo doctrine: never auto-swear an oath on the affiant's behalf
    (round 10 stopped the cross-widget fanout; round 11 closes the engine
    paths). The FillBindingPins pin in tests/test_slug_collision_fix.py
    already pins FM-216's jurat blanks; this module locks the class
    corpus-wide and pins the _apply_notary_block removal on a non-recipe
    form (AD-012).

  BRANCH 4 — respondent/defendant address stamp (NARROWED):
    * the `presentaddress` token was dropped from the branch-4 trigger,
      neutralizing 78 children's-present-address table cells across 13
      forms (over-applications of the respondent's datum into a per-child
      address list).
    * a per-form _FORM_RESPADDR_STAMP_BLOCKLIST (21 forms / 48 field_ids)
      suppresses the wrong-block widgets the token still reaches
      (plaintiff/petitioner blocks, "Other Party" blocks, judgment-creditor
      / mover blocks, old/new change-of-address pairs, confidentiality
      checkboxes). 28 genuine defendant/respondent (and judgment-debtor)
      blocks keep the stamp.

The map_form-level tests need no PDF and are the CI regression gate. The
render pins guard at the top with the exact PDF-present idiom used by
tests/test_slug_collision_fix.py::FillBindingPins (form PDFs are gitignored
and absent in CI).
"""
import json
import pathlib
import re
import sys
import tempfile
import unittest

import fitz  # PyMuPDF

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from engine.build_kv_map import (  # noqa: E402
    map_form, _FORM_RESPADDR_STAMP_BLOCKLIST)
from engine.fill_and_audit import (  # noqa: E402
    fill_one, _apply_notary_block, _NOTARY_SIGNER_FIDS_LEAVE_BLANK,
    _NOTARY_COUNTY_FIDS, _NOTARY_STATE_FIDS, _PERJURY_SWEAR_FIDS)
from engine.case_template import pick_sample_case_for  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
FORMS = ROOT / "forms"


def _schema(form_id):
    return json.loads((FORMS / form_id / "schema.json").read_text())


def _sample_kv(form_id):
    """map_form output under the prefix's representative sample case
    (built the same way engine/fill_and_audit and the other tests do)."""
    case = pick_sample_case_for(form_id).to_dict()
    kv, _ = map_form(_schema(form_id), case)
    return kv


def _squash(s):
    return s.lower().replace("_", "")


# Branch-5 trigger tokens (the removed map_form branch matched these on the
# underscore-squashed field_id). The class is enumerated from the corpus so
# the test can't drift out of sync with the schemas.
_BRANCH5_TOKENS = ("personallyappeared", "beforeme", "appearedabovenamed")

# Branch-4 trigger tokens AFTER the round-11 `presentaddress` drop.
_BRANCH4_TOKENS = ("physicaladdress", "respondentaddress",
                   "defendantaddress", "addressofrespondent",
                   "addressofdefendant")

# The 13 forms carrying the children's-present-address table.
_CHILD_TABLE_FORMS = ("FM-004", "FM-006", "FM-062", "FM-068", "FM-070",
                      "FM-224", "FM-225", "FM-226", "FM-229",
                      "OTH-041", "OTH-042", "OTH-043", "OTH-044")

# 28 genuine defendant/respondent (and judgment-debtor) address blocks the
# fix must NOT over-correct: the respondent address must still stamp.
# (round-11 verdicts branch4.keep_correct_detail, expanded to field_ids.)
_KEEP_CORRECT = {
    "CV-266": ("physical_address_1_2", "physical_address_2_2"),
    "FM-002": ("physical_address_3", "physical_address_4"),
    "FM-283": ("physical_address_1_2", "physical_address_2_2"),
    "FM-284": ("physical_address_1_2", "physical_address_2_2"),
    "OTH-039": ("physical_address_3", "physical_address_4"),
    "OTH-040": ("physical_address_3", "physical_address_4"),
    "OTH-041": ("physical_address_3", "physical_address_4"),
    "OTH-042": ("physical_address_3", "physical_address_4"),
    "OTH-043": ("physical_address_3", "physical_address_4"),
    "OTH-044": ("physical_address_3", "physical_address_4"),
    "FM-008": (
        "thepresentphysicaladdresslocation_of_the_respondentandtheminor_"
        "childrenis_1",
        "thepresentphysicaladdresslocation_of_the_respondentandtheminor_"
        "childrenis_2"),
    "FM-181": (
        "the_present_physical_addresslocation_ofrespondentandminor_"
        "childrenis_1",
        "the_present_physical_addresslocation_ofrespondentandminor_"
        "childrenis_2"),
    "CV-281": ("physical_address_1_3", "physical_address_2_3"),
    "CV-282": ("physical_address_1_3", "physical_address_2_3"),
}


class Branch5NotaryNameStamp(unittest.TestCase):
    """Every notary affiant blank (and the FDP-006 substring FPs) renders
    blank from map_form — the name-stamp branch is gone."""

    def test_no_branch5_field_autostamps_corpus_wide(self):
        swept = checked = 0
        for sp in sorted(FORMS.glob("*/schema.json")):
            form_id = sp.parent.name
            schema = json.loads(sp.read_text())
            kv = _sample_kv(form_id)
            swept += 1
            for f in schema.get("fields") or []:
                if f.get("category") != "narrative_derived":
                    continue
                fid = f["field_id"]
                if not any(t in _squash(fid) for t in _BRANCH5_TOKENS):
                    continue
                checked += 1
                with self.subTest(form=form_id, field=fid):
                    self.assertEqual(
                        kv.get(fid, ""), "",
                        f"{form_id}.{fid}: notary affiant name auto-stamped")
        self.assertGreater(swept, 100, "expected the full form tree")
        # 38 jurat blanks + 5 FDP-006 "before mediation" FPs across the tree
        self.assertGreater(checked, 35, "sweep found too few class members")

    def test_fdp006_before_mediation_substring_fp_blank(self):
        # The branch-5 trigger 'beforeme' used to match the substring in
        # 'before mediation'; these are narrative mediation-exchange boxes.
        kv = _sample_kv("FDP-006")
        for n in range(1, 6):
            fid = f"information_with_the_court_and_parties_before_mediation_{n}"
            with self.subTest(field=fid):
                self.assertIn(fid, kv, "FDP-006 field vanished — update test")
                self.assertEqual(kv[fid], "")


class NotaryBlockSignerLoopGone(unittest.TestCase):
    """_apply_notary_block no longer fills the affiant signer line; the
    county / state fills and the gated perjury checkbox are intact."""

    def test_signer_line_not_filled_even_when_widget_present(self):
        # Build a kv where every notary signer widget exists and is blank,
        # plus a county/state widget and the perjury box, then run the block.
        signer_fids = list(_NOTARY_SIGNER_FIDS_LEAVE_BLANK)
        kv = {fid: "" for fid in signer_fids}
        kv["county"] = ""                 # a county widget present
        kv["state_of"] = ""               # a state widget present
        kv[_PERJURY_SWEAR_FIDS[0]] = ""   # a perjury box present
        case = {
            "notary_county": "Cumberland",
            "court": {"county": "Cumberland"},
            "parties": {"plaintiff": {"full_name": "Jordan Q. Filer"}},
            # perjury NOT acknowledged -> box must stay blank
            "facts": {},
        }
        _apply_notary_block(kv, case)
        for fid in signer_fids:
            with self.subTest(field=fid):
                self.assertEqual(
                    kv[fid], "",
                    f"_apply_notary_block re-stamped signer {fid!r}")

    def test_county_state_still_fill(self):
        kv = {"county": "", "state_of": ""}
        case = {"notary_county": "York", "court": {"county": "York"},
                "facts": {}}
        added = _apply_notary_block(kv, case)
        self.assertEqual(kv["county"], "York")
        self.assertEqual(kv["state_of"], "Maine")
        self.assertEqual(added, 2)

    def test_perjury_checkbox_only_on_explicit_ack(self):
        box = _PERJURY_SWEAR_FIDS[0]
        # not acknowledged -> blank
        kv = {box: ""}
        _apply_notary_block(kv, {"facts": {}})
        self.assertEqual(kv[box], "")
        # explicitly acknowledged -> checked
        kv = {box: ""}
        _apply_notary_block(kv, {"facts": {"perjury_acknowledged": True}})
        self.assertEqual(kv[box], "X")

    def test_county_state_perjury_constants_intact(self):
        # The kept tuples must not have been emptied along with the signer.
        self.assertTrue(_NOTARY_COUNTY_FIDS)
        self.assertTrue(_NOTARY_STATE_FIDS)
        self.assertTrue(_PERJURY_SWEAR_FIDS)


class Branch4RespondentAddressOverApplication(unittest.TestCase):
    """The respondent-address stamp is narrowed: the `presentaddress` token
    is dropped and a per-form blocklist suppresses wrong-block widgets,
    while genuine respondent blocks keep the stamp."""

    def test_blocklist_is_21_forms_48_fields(self):
        self.assertEqual(len(_FORM_RESPADDR_STAMP_BLOCKLIST), 21)
        self.assertEqual(
            sum(len(v) for v in _FORM_RESPADDR_STAMP_BLOCKLIST.values()), 48)

    def test_presentaddress_token_dropped_from_engine(self):
        # The live branch-4 trigger (squashed) must no longer carry the
        # presentaddress token. Read the engine source to assert the drop.
        src = (ROOT / "engine" / "build_kv_map.py").read_text()
        # find the _respondent_address call site's `any(k in fid_squashed`
        m = re.search(
            r"if \(any\(k in fid_squashed for k in \((.*?)\)\)",
            src, re.S)
        self.assertIsNotNone(m, "branch-4 trigger tuple not found")
        trigger = m.group(1)
        self.assertNotIn("presentaddress", trigger,
                         "presentaddress token was not dropped")
        self.assertIn("physicaladdress", trigger)

    def test_blocklist_keys_are_real_schema_fields(self):
        for form_id, fields in _FORM_RESPADDR_STAMP_BLOCKLIST.items():
            ids = {f["field_id"] for f in _schema(form_id).get("fields") or []}
            for fid in fields:
                with self.subTest(form=form_id, field=fid):
                    self.assertIn(fid, ids)

    def test_every_blocklist_entry_renders_blank(self):
        for form_id, fields in _FORM_RESPADDR_STAMP_BLOCKLIST.items():
            kv = _sample_kv(form_id)
            for fid in fields:
                with self.subTest(form=form_id, field=fid):
                    self.assertEqual(
                        kv.get(fid, ""), "",
                        f"{form_id}.{fid}: blocklisted respondent address "
                        f"auto-stamped")

    def test_present_address_child_table_cells_blank(self):
        # All 78 children's-present-address table cells across 13 forms must
        # render blank now that `presentaddress` is dropped from the trigger.
        swept_forms = checked = 0
        for form_id in _CHILD_TABLE_FORMS:
            kv = _sample_kv(form_id)
            schema = _schema(form_id)
            swept_forms += 1
            for f in schema.get("fields") or []:
                fid = f["field_id"]
                if ("present_address" in fid and "do_not_list" in fid):
                    checked += 1
                    with self.subTest(form=form_id, field=fid):
                        self.assertEqual(
                            kv.get(fid, ""), "",
                            f"{form_id}.{fid}: child present-address cell "
                            f"auto-stamped with the respondent's address")
        self.assertEqual(swept_forms, 13)
        # 78 cells across the 13 forms
        self.assertGreaterEqual(checked, 70,
                                "child-table sweep found too few cells")

    def test_genuine_respondent_blocks_still_stamp(self):
        # The fix must not over-correct: where the sample case actually has a
        # respondent/defendant address, the genuine block keeps the stamp.
        asserted = 0
        for form_id, fields in _KEEP_CORRECT.items():
            case = pick_sample_case_for(form_id).to_dict()
            parties = case.get("parties") or {}
            has_resp_addr = any(
                (parties.get(k) or {}).get("address")
                for k in ("respondent", "defendant",
                          "individual_under_protection"))
            kv, _ = map_form(_schema(form_id), case)
            for fid in fields:
                with self.subTest(form=form_id, field=fid):
                    self.assertIn(fid, kv,
                                  f"{form_id}.{fid} vanished — update test")
                    if not has_resp_addr:
                        self.skipTest(
                            f"{form_id} sample case has no respondent "
                            f"address to stamp")
                    self.assertTrue(
                        kv.get(fid, ""),
                        f"{form_id}.{fid}: genuine respondent block lost its "
                        f"stamp (over-correction)")
                    asserted += 1
        self.assertGreater(asserted, 20, "kept-block coverage too thin")


class RenderPins(unittest.TestCase):
    """Full-fill render pins (need the blank PDF, gitignored / absent in CI
    -> auto-skip). Follows the exact PDF-present idiom in
    tests/test_slug_collision_fix.py::FillBindingPins._render."""

    def _render(self, form_id, *, case=None, pdf_path=None):
        if not (FORMS / form_id / f"{form_id}.pdf").exists():
            self.skipTest(f"{form_id}.pdf not fetched")
        if case is None:
            case = json.loads(
                (FORMS / form_id / "examples"
                 / "sample_case.json").read_text())
        out = pathlib.Path(tempfile.mkdtemp())
        res = fill_one(form_id, case, out,
                       pdf_path=pdf_path or (FORMS / form_id
                                             / f"{form_id}.pdf"))
        self.assertTrue(res.get("ok"), res.get("error"))
        pdfs = list(out.glob("*.pdf"))
        self.assertTrue(pdfs, "fill produced no PDF")
        doc = fitz.open(pdfs[0])
        vals = {}
        for pg in doc:
            for w in pg.widgets() or []:
                vals[(pg.number, w.field_name)] = w.field_value or ""
        doc.close()
        return vals

    def test_ad012_notary_signer_line_renders_blank(self):
        # AD-012 is NOT a recipe form, so the only thing that could have
        # filled its "Personally appeared the above named" line was the now
        # removed _apply_notary_block signer loop. It must render blank.
        vals = self._render("AD-012")
        self.assertEqual(
            vals.get((2, "Personally appeared the above named"), ""), "",
            "AD-012 jurat affiant line was auto-sworn")

    def test_fm283_plaintiff_block_blank_defendant_block_kept(self):
        # branch-4 both directions: the plaintiff-block physical_address_1/_2
        # (blocklisted) render blank; the defendant-block _1_2/_2_2 (kept)
        # render filled.
        vals = self._render("FM-283")
        self.assertEqual(vals.get((0, "Physical Address 1"), ""), "",
                         "FM-283 plaintiff-block address was stamped")
        self.assertEqual(vals.get((0, "Physical Address 2"), ""), "",
                         "FM-283 plaintiff-block address was stamped")
        self.assertTrue(
            vals.get((0, "Physical Address 1_2")),
            "FM-283 defendant-block address lost its stamp")

    def test_fm008_respondent_block_renders_filled(self):
        # branch-4 keep: the genuine respondent present-location block fills.
        vals = self._render("FM-008")
        nm = ("Thepresentphysicaladdresslocation of the "
              "respondentandtheminor childrenis 1")
        self.assertTrue(vals.get((0, nm)),
                        "FM-008 respondent block lost its stamp")


if __name__ == "__main__":
    unittest.main(verbosity=2)
