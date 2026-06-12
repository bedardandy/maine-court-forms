"""MJ-009 / MJ-015 money-line + signature regressions (round-8 fixes).

PDF-free (map_form + recipe.process, like tests/test_placement.py); the
printed-text claims below were render-verified against the blank PDFs:

  - Both forms PRINT the "$" before every amount blank (MJ-009: "pay $ ___
    per ___", "...owes the judgment creditor $ ___ (plus interest of $___)
    plus costs of $ ___, for a total of $ ___"; MJ-015: "...owes the
    judgment creditor $ ___ plus interest of $ ___ plus costs of $ ___,
    for a total of $ ___"), so the recipe writes amounts BARE and strips a
    supplied leading "$" ("$ $1,250.00" regression).
  - MJ-009's interest blank has NO widget default: $0.00 asserted a figure
    nobody supplied while the (correctly) skipped computation left the
    total empty — an inconsistent render.
  - MJ-015's signature line (`undefined_2`) is the CREDITOR's affidavit
    signature; it must never default to the judgment debtor's name.
  - MJ-005 is the contrast case: there the debtor IS the disclosing
    affiant ("I, <debtor>, having been served..."), so its debt_name
    fallback stays.
"""
import importlib
import sys
import unittest
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from tests.helpers import recipe_dispatch, schema  # noqa: E402


def _recipe_kv(form_id: str, case: dict) -> dict:
    """map_form + recipe.process over a custom case (PDF-free)."""
    from engine.build_kv_map import map_form
    kv, _ = map_form(schema(form_id), case)
    mod = importlib.import_module(
        "engine.recipes." + recipe_dispatch()[form_id])
    out, _changes = mod.process(kv, case)
    return out


def _case(facts: dict, filing_date: str = "2025-04-01") -> dict:
    """Minimal engine-shape case: creditor v. debtor, no extras."""
    return {
        "docket_no": "PORDC-CV-2025-00000",
        "filing_date": filing_date,
        "court": {"name": "District Court",
                  "location": "Portland", "county": "Cumberland"},
        "parties": {
            "plaintiff": {"full_name": "Acme Credit LLC"},
            "defendant": {"full_name": "John R. Roe"},
        },
        "facts": dict(facts),
    }


class Mj009MoneyLine(unittest.TestCase):
    def test_amounts_bare_and_supplied_dollar_stripped(self):
        # facts arrive with a "$" (common in real cases) — widgets must
        # not double it against the printed "$" on the line
        out = _recipe_kv("MJ-009", _case({
            "mj009_pay_amount": "$75.00",
            "mj009_pay_period": "month",
            "mj009_owed_amount": "$1,250.00",
            "mj009_interest": "15.00",
            "mj009_costs": "$120.00",
            "mj009_total": "$1,385.00",
        }))
        self.assertEqual(out["pay"], "75.00")
        self.assertEqual(
            out["the_judgment_creditor_currently_owes_the_judgment_creditor"],
            "1,250.00")
        self.assertEqual(out["undefined_2"], "15.00")
        self.assertEqual(out["plus_costs_of"], "120.00")
        self.assertEqual(out["for_a_total_of"], "1,385.00")
        for fid, val in out.items():
            self.assertFalse(str(val).startswith("$"),
                             f"{fid} carries a '$' the form already prints")

    def test_interest_blank_has_no_widget_default(self):
        # owed + costs only: interest stays EMPTY (the old $0.00 default
        # asserted a fact nobody supplied) and so does the total (the
        # engine skips the sum on the missing input)
        out = _recipe_kv("MJ-009", _case({
            "mj009_owed_amount": "1,250.00",
            "mj009_costs": "120.00",
        }))
        self.assertEqual(out["undefined_2"], "")
        self.assertEqual(out["for_a_total_of"], "")
        self.assertEqual(
            out["the_judgment_creditor_currently_owes_the_judgment_creditor"],
            "1,250.00")
        self.assertEqual(out["plus_costs_of"], "120.00")

    def test_order_date_only_from_explicit_fact(self):
        # no fact → the court-order date stays empty (never the filing
        # date — see test_date_guard); explicit fact → placed, US format
        self.assertEqual(
            _recipe_kv("MJ-009", _case({}))[
                "courts_installment_order_dated_mmddyyyy"], "")
        self.assertEqual(
            _recipe_kv("MJ-009", _case(
                {"mj009_installment_order_date": "2025-02-14"}))[
                "courts_installment_order_dated_mmddyyyy"], "02/14/2025")


class Mj015SignatureAndMoneyLine(unittest.TestCase):
    def test_signature_never_defaults_to_debtor(self):
        # the affidavit is filed AGAINST the debtor — without an explicit
        # affiant_name the signature line stays empty
        out = _recipe_kv("MJ-015", _case({
            "mj_principal": "2,450.00",
            "mj_interest": "35.00",
            "mj_costs": "175.00",
        }))
        self.assertEqual(out["undefined_2"], "")

    def test_signature_from_explicit_affiant(self):
        out = _recipe_kv("MJ-015", _case({
            "affiant_name": "Pat L. Lawyer, Esq.",
        }))
        self.assertEqual(out["undefined_2"], "Pat L. Lawyer, Esq.")

    def test_order_date_iso_converted_like_mj009(self):
        # the blank prints "(mm/dd/yyyy)"; an ISO fact must render US,
        # exactly as MJ-009's installment-order date does
        self.assertEqual(
            _recipe_kv("MJ-015", _case(
                {"installment_order_date": "2025-02-14"}))[
                "installment_order_dated_mmddyyyy"], "02/14/2025")

    def test_order_date_us_passes_through(self):
        self.assertEqual(
            _recipe_kv("MJ-015", _case(
                {"installment_order_date": "02/14/2025"}))[
                "installment_order_dated_mmddyyyy"], "02/14/2025")

    def test_amounts_supplied_dollar_stripped(self):
        out = _recipe_kv("MJ-015", _case({
            "mj_principal": "$2,450.00",
            "mj_interest": "$35.00",
            "mj_costs": "$175.00",
            "mj_total": "$2,660.00",
        }))
        self.assertEqual(
            out["the_judgment_debtor_currently_owes_the_judgment_creditor"],
            "2,450.00")
        self.assertEqual(out["undefined"], "35.00")
        self.assertEqual(out["plus_costs_of"], "175.00")
        self.assertEqual(out["for_a_total_of"], "2,660.00")


class Mj005AffiantContrast(unittest.TestCase):
    def test_mj005_debtor_affiant_default_preserved(self):
        # MJ-005's disclosing affiant IS the debtor — the fallback there
        # is correct and must not regress with the MJ-015 signature fix
        out = _recipe_kv("MJ-005", _case({}))
        self.assertEqual(out["i"], "John R. Roe")
        self.assertEqual(out["text5"], "John R. Roe")


if __name__ == "__main__":
    unittest.main(verbosity=2)
