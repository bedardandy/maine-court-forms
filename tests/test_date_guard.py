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

Round 9 widens the guard from court-event dates to every substantive-date
family a full-corpus sweep found still auto-stamping (decision/appeal,
trial, employment/attendance, arrest/offense, due/payment, other-lawsuit
disclosure, travel/mileage rows, prior-act dates, ...); the
SubstantiveDateFamilies cases pin one representative per family and the
full-corpus invariant locks the whole class via the engine's own regex.
"""
import json
import re
import sys
import unittest
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from engine.build_kv_map import (  # noqa: E402
    map_form, _SUBSTANTIVE_DATE_RE, _FORM_DATE_STAMP_BLOCKLIST)

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


# Round-9 families: one representative widget per token family, each
# printed-text-verified (the blank asks for a real fact — a decision /
# trial / employment / arrest / due / disclosure / travel / prior-act
# date — never the form's own signature or filing date).
_BLOCKED = [
    # (form, field_id) — must render blank under a date-only case
    ("CR-140", "the_date_of_that_decision_1"),          # decision
    ("CR-140", "date_of_writ"),                         # writ
    ("CR-140", "date_of_appeals_dec"),                  # appeals_dec
    ("CR-140", "date_of_final_admin_action"),           # admin
    ("CR-140", "date_of_dep_proceeding"),               # proceeding
    ("OTH-012", "2_what_date_was_the_decision_made"),   # decision
    ("MJBVB-010", "trial_date"),                        # trial
    ("PC-034", "court_date_mmddyyyy"),                  # court_date
    ("FM-186", "was_dismissed_on_date_mmddyyyy"),       # dismissed
    ("CR-032", "if_unemployed_last_date_employed_mmyyyy"),   # employ
    ("CR-287", "dates_of_employment_mmddyyyy"),         # employ
    ("CR-287", "dates_of_attendance_mmyyyy"),           # attendance
    ("CR-287", "date_from_mmddyyyy"),                   # date_from
    ("JV-005", "date_and_time_of_arrest_mmddyyyy"),     # arrest
    ("JV-046", "3_date_of_offense_mmddyyyy"),           # offense
    ("MJBVB-017", "due_date"),                          # due
    ("MJBVB-017", "fine_due_date"),                     # due
    ("CV-CR-JV-165", "if_yes_date_due_mmddyyyy"),       # due
    ("OMB-097", "datefinalpaymenttosdu"),               # payment
    ("OMB-097", "terminationdate"),                     # termination
    ("CV-287",
     "the_amount_and_date_of_the_last_payment_or_allegation_that_no_payment_has_been_made"),
    ("FM-043", "date_lawsuit_or_claim_filed_mmddyyyy1"),     # lawsuit
    ("FM-043", "date_acquired_mmddyyyy1"),              # acquired
    ("FM-056", "the_deed_is_dated_mmddyyyy"),           # deed
    ("PA-025", "2_date_the_weapons_waswere_relinquished_mmddyyyy"),
    ("CV-FM-291", "date_mmddyyyyrow1"),                 # mileage row
    ("CV-FM-JV-PB-PC-024", "daterow1"),                 # mileage row
    ("CV-FM-JV-PB-PC-242", "anticipated_date_mmddyyyyrow1"),  # travel
    ("CR-239", "date_i_wish_to_leave"),                 # wish
    ("FM-055", "date_of_contact_mmddyyyy"),             # contact
    ("OTH-007", "dates_of_coverage_mmddyyyy"),          # coverage
    ("JV-022", "required_date_of_completion_mmddyyyy"),  # complet
    ("CR-076",
     "under_oathaffirmation_i_state_that_the_information_in_my_statement_dated_mmddyyyy"),
    ("GS-006", "date_i"),                               # anchored date_i
    ("CV-001", "on_date_mmddyyyy"),                     # anchored on_date
    ("CV-001", "that_concluded_on_date_of_panel_finding_mmddyyyy"),
    ("CV-145", "dates_of_adr_conferences_mmddyyyy"),    # conference
    ("CV-223",
     "if_yes_state_the_trial_start_date_or_trailing_trial_period_mmddyyyy"),
    ("CV-267", "date_mmddyyyy_and_time_of_the_depositioninspection_1"),
    ("OTH-134", "a_date_of_pairing_mmddyyyy"),          # pairing
    ("OTH-085",
     "4_the_date_the_case_was_initiated_mmddyyyy_estimate_if_the_exact_date_is_unknown"),
    ("GS-014", "date_of_guardianship"),                 # guardianship
    ("CR-243", "date_of_admission"),                    # admission
    ("CR-243", "eff_date"),                             # eff_date
    ("OTH-013", "date_on_which_you_started_employment_with_present_employer"),
    ("MJBVB-017", "start_date"),                        # start
    ("MJBVB-018", "date_ofoffense"),                    # offense
    ("FM-PC-003", "this_year_to_date"),                 # year_to_date
    ("SC-001", "briefly_describe_your_claim_including_relevant_dates_1"),
    ("CR-CV-FM-JV-PA-PC-286",
     "4_i_found_out_i_needed_to_change_the_date_of_my_court_event_on_mmddyyyy"),
    # GS-006 notice rows / PA-024's relinquish date are not
    # narrative_derived (case_constant / party_attr) so they never reach
    # the date stamp — pinned here so a recategorization can't regress
    # them either.
    ("GS-006", "date_time_and_location_of_noticerow1"),  # notice
    ("PA-024",
     "date_the_weapons_waswere_relinquished_to_law_enforcement_by_the_defendant_mmddyyyy"),
]

# Bare signature/filing-date widgets that MUST keep stamping.
_STILL_STAMPED = [
    ("MJ-009", "date_mmddyyyy", "04/01/2025"),
    ("AD-003", "dated", "04/01/2025"),
    ("AD-001", "date", "04/01/2025"),
    ("AD-001", "date_2", "2025-04-01"),
    ("CR-127", "date_1", "2025-04-01"),
    ("CR-239", "todays_date", "2025-04-01"),       # today's date = fill date
    ("OTH-133", "a_date_of_request_mmddyyyy", "04/01/2025"),  # made now
    ("OMB-097", "documentdate", "2025-04-01"),     # the form's own date
    ("CV-FM-PB-299", "date_submitted_mmddyyyy", "04/01/2025"),
]


class SubstantiveDateFamilies(unittest.TestCase):
    def _kv(self, form_id):
        schema = json.loads((FORMS / form_id / "schema.json").read_text())
        kv, _ = map_form(schema, dict(_DATE_ONLY_CASE))
        return kv

    def test_substantive_date_families_never_autostamp(self):
        for form_id, fid in _BLOCKED:
            with self.subTest(form=form_id, field=fid):
                kv = self._kv(form_id)
                self.assertIn(fid, kv, "representative field vanished "
                              "from the schema — update the test")
                self.assertEqual(
                    kv[fid], "",
                    f"{form_id}.{fid}: substantive date auto-stamped "
                    f"with the filing date")

    def test_bare_signature_date_widgets_still_stamp(self):
        for form_id, fid, want in _STILL_STAMPED:
            with self.subTest(form=form_id, field=fid):
                self.assertEqual(self._kv(form_id).get(fid), want)

    def test_full_corpus_guard_invariant(self):
        # The engine's own regex is the oracle: under a date-only case NO
        # field whose id matches _SUBSTANTIVE_DATE_RE may come back
        # non-empty from map_form, in any category, on any shipped form.
        swept = checked = 0
        for sp in sorted(FORMS.glob("*/schema.json")):
            form_id = sp.parent.name
            schema = json.loads(sp.read_text())
            kv, _ = map_form(schema, dict(_DATE_ONLY_CASE))
            swept += 1
            for f in schema.get("fields") or []:
                fid = f["field_id"]
                fl = fid.lower()
                if "date" not in fl or not _SUBSTANTIVE_DATE_RE.search(fl):
                    continue
                checked += 1
                with self.subTest(form=form_id, field=fid):
                    self.assertEqual(
                        kv.get(fid, ""), "",
                        f"{form_id}.{fid}: guard-matching date field "
                        f"auto-stamped with the filing date")
        self.assertGreater(swept, 100, "expected the full form tree")
        self.assertGreater(checked, 200, "sweep found too few class members")


class PerFormDateStampBlocklist(unittest.TestCase):
    """Round-10 per-form blocklist: bare date widgets whose field_id is too
    generic for _SUBSTANTIVE_DATE_RE but which the *form* identifies as a
    substantive prior-order/GAL-contact date (class 1), a service-block
    column clone sitting on a Name/Address/Phone line (class 2), or a
    judicial-officer signature date (class 3). Each representative was
    printed-text verified against its PDF widget rect."""

    def _kv(self, form_id):
        schema = json.loads((FORMS / form_id / "schema.json").read_text())
        kv, _ = map_form(schema, dict(_DATE_ONLY_CASE))
        return kv

    # class 1 — substantive prior-order / GAL-contact dates
    def test_class1_fm136_prior_divorce_judgment_order_date(self):
        # "... is incorporated in, and is a part of, the Divorce Judgment
        # Order of this Court dated (mm/dd/yyyy)" — a prior order's date.
        self.assertEqual(self._kv("FM-136").get("date"), "")

    def test_class1_fm132_interim_order_of_this_date(self):
        # "interim order / other: ... of this date dated (mm/dd/yyyy)"
        self.assertEqual(self._kv("FM-132").get("dated_mmddyyyy"), "")

    def test_class1_pc034_met_with_children_contact_date(self):
        # "I met with the child(ren) on the following dates and locations:
        # Date (mm/dd/yyyy): at the following location" — GAL contact event.
        self.assertEqual(self._kv("PC-034").get("date_mmddyyyy"), "")
        self.assertEqual(self._kv("PC-034").get("date_mmddyyyy_3"), "")

    # class 2 — AD-FM-GS-JV-PA-PC-292 service-block column clone
    def test_class2_292_name_address_phone_clones_blocked(self):
        kv = self._kv("AD-FM-GS-JV-PA-PC-292")
        # _2 prints "Name:", _3 "Address:", _4 the "Phone Number:" line;
        # the page-3 *_2 twins repeat the column. None may stamp.
        for fid in ("date_mmddyyyy_2", "date_mmddyyyy_3", "date_mmddyyyy_4",
                    "date_mmddyyyy_2_2", "date_mmddyyyy_3_2",
                    "date_mmddyyyy_4_2"):
            with self.subTest(field=fid):
                self.assertEqual(kv.get(fid), "")

    def test_class2_292_genuine_date_lines_still_stamp(self):
        # The `_1` / `_1_2` widgets ARE the real "Date (mm/dd/yyyy):" lines.
        kv = self._kv("AD-FM-GS-JV-PA-PC-292")
        self.assertEqual(kv.get("date_mmddyyyy_1"), "04/01/2025")
        self.assertEqual(kv.get("date_mmddyyyy_1_2"), "04/01/2025")

    # class 3 — judicial-officer signature dates
    def test_class3_gs004_judge_signature_date(self):
        # "Dated: ___ Judge, Probate Court / District Court"
        self.assertEqual(self._kv("GS-004").get("dated"), "")

    def test_class3_mjbvb018_judge_signature_date(self):
        # "Date ___ Judge, District Court"
        self.assertEqual(self._kv("MJBVB-018").get("date_1"), "")

    def test_blocklist_keys_are_real_schema_fields(self):
        # every (form, field_id) in the blocklist must exist in that
        # schema, else the guard is silently dead.
        for form_id, fields in _FORM_DATE_STAMP_BLOCKLIST.items():
            schema = json.loads(
                (FORMS / form_id / "schema.json").read_text())
            ids = {f["field_id"] for f in schema.get("fields") or []}
            for fid in fields:
                with self.subTest(form=form_id, field=fid):
                    self.assertIn(fid, ids)

    def test_every_blocklist_entry_renders_blank(self):
        for form_id, fields in _FORM_DATE_STAMP_BLOCKLIST.items():
            kv = self._kv(form_id)
            for fid in fields:
                with self.subTest(form=form_id, field=fid):
                    self.assertEqual(
                        kv.get(fid, ""), "",
                        f"{form_id}.{fid}: blocklisted date auto-stamped")


if __name__ == "__main__":
    unittest.main(verbosity=2)
