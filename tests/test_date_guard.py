"""Generic-date-fill guard: court-event dates are never auto-stamped.

map_form's narrative_derived fallback stamps case.event_date /
case.filing_date into generic `date`/`dated` widgets (signature-date
convention). A field_id that says when a court ORDER / JUDGMENT / DECREE /
HEARING was dated is NOT that widget — stamping the filing date there
asserts the court acted on the day the form was filed (the round-8 finding:
a minimal MJ-009 fill put filing_date into "Court's installment order dated
(mm/dd/yyyy)"). _SUBSTANTIVE_DATE_RE in engine/build_kv_map.py carries the
guard; this sweep locks the class across every shipped schema, PDF-free.

Recipes that place such dates from an EXPLICIT fact are unaffected (their
`_set` writes the now-empty slot) — see tests/test_mj_money_fields.py.
"""
import json
import re
import sys
import unittest
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from engine.build_kv_map import map_form  # noqa: E402

FORMS = pathlib.Path(__file__).resolve().parent.parent / "forms"

# The court-event tokens the guard must cover. abuseharassment_dated is
# PA-022's continuation widgets of the printed "the Order for Protection
# from Abuse/Harassment dated (mm/dd/yyyy)" sentence (no "order" token in
# the field_id).
_COURT_EVENT_RE = re.compile(
    r"order|judgment|judgement|decree|hearing|abuseharassment_dated")

# A date-only case: nothing but the dates the generic pass stamps from.
_DATE_ONLY_CASE = {"filing_date": "2025-04-01", "event_date": "2025-04-01"}


class CourtEventDateGuard(unittest.TestCase):
    def test_no_schema_lets_a_court_event_date_autostamp(self):
        swept = checked = 0
        for sp in sorted(FORMS.glob("*/schema.json")):
            form_id = sp.parent.name
            schema = json.loads(sp.read_text())
            kv, _ = map_form(schema, dict(_DATE_ONLY_CASE))
            swept += 1
            for f in schema.get("fields") or []:
                fid = f["field_id"]
                fl = fid.lower()
                if (f.get("category") != "narrative_derived"
                        or "date" not in fl
                        or not _COURT_EVENT_RE.search(fl)):
                    continue
                checked += 1
                with self.subTest(form=form_id, field=fid):
                    self.assertEqual(
                        kv.get(fid, ""), "",
                        f"{form_id}.{fid}: court-event date auto-stamped "
                        f"with the filing date")
        self.assertGreater(swept, 100, "expected the full form tree")
        # MJ-009/MJ-015 installment-order dates, CR-140 judgment dates,
        # JV hearing dates, PA-022 protection-order dates... — the sweep
        # must actually be exercising the class
        self.assertGreater(checked, 25, "sweep found too few class members")

    def test_signature_date_convention_still_stamps(self):
        # the guard must not eat the generic signature-date fill the
        # convention depends on (bare date_mmddyyyy widgets)
        schema = json.loads((FORMS / "MJ-009" / "schema.json").read_text())
        kv, _ = map_form(schema, dict(_DATE_ONLY_CASE))
        self.assertEqual(kv.get("date_mmddyyyy"), "04/01/2025")
        self.assertEqual(kv.get("courts_installment_order_dated_mmddyyyy"),
                         "")


if __name__ == "__main__":
    unittest.main(verbosity=2)
