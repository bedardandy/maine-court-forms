"""Pinned placement assertions — lock in render-verified fixes so they can't
silently regress (the GS-001 / #456 lesson: "verified once" is not a gate).

Each pin below was confirmed by rendering the real engine output during the
placement-defect campaign. PDF-free: recipe pins read the recipe's kv output;
mapping pins read resolve_mapping's resolved values. Add a pin whenever a new
fix is render-verified.
"""
import sys
import unittest
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from tests.helpers import recipe_output, mapping_values

# (form_id, field_id, expected_value, note) — recipe-tier (recipe kv output)
RECIPE_PINS = [
    # JV-006-W caption — offset-name pollution fixed (commit 1ae66d7)
    ("JV-006-W", "undefined", "Portland", "Location line"),
    ("JV-006-W", "location_town", "FM-2024-00000", "Docket line"),
    # NC-001 petitioner<->attorney page-2 columns (fa2523f)
    ("NC-001", "name", "Pat L. Lawyer, Esq.", "LEFT = Attorney for Petitioner(s)"),
    ("NC-001", "name_2", "Jane Q. Doe", "RIGHT = petitioner block"),
    ("NC-001", "email", "attorney@example.com", "LEFT attorney email"),
    ("NC-001", "email_2", "jane.doe@example.com", "RIGHT petitioner email"),
    # MJ-SC-012 notary affiant = debtor, not creditor (5eef458)
    ("MJ-SC-012", "personallyappearedtheabovenamed", "John R. Roe", "affiant = debtor"),
    # MJ-009 "(plus interest of $)" is a $ field, not a name (88ab496)
    ("MJ-009", "undefined_2", "$0.00", "interest amount, not affiant name"),
    ("MJ-009", "for_a_total_of", "$1,370.00", "total incl interest"),
    # PC-034 GAL signature block, not plaintiff (f6afcbf)
    ("PC-034", "name", "Margaret L. Holcomb, Esq.", "GAL printed name"),
    ("PC-034", "undefined", "Margaret L. Holcomb, Esq.", "GAL signature line"),
    # MJ-015 amount line — the principal belongs in the owed blank right
    # after "currently owes the judgment creditor $" (it was misplaced into
    # the interest blank `undefined`, which by rect is the "$" opening the
    # "plus interest of $ ___" line); the total is the printed sum, supplied
    # in the sample and computed via computations.json when omitted
    ("MJ-015", "the_judgment_debtor_currently_owes_the_judgment_creditor",
     "2,450.00", "principal in the owed blank"),
    ("MJ-015", "undefined", "35.00", "interest amount blank"),
    ("MJ-015", "for_a_total_of", "2,660.00",
     "printed total (principal + interest + costs)"),
    # --- sibling regression guards (shared modules must not regress) ---
    ("MJ-014", "undefined_2", "John R. Roe", "MJ-014 'Name of defendant' preserved"),
    ("JV-022", "undefined", "Maria T. Hendricks", "JV-022 supervisor signature preserved"),
]

# (form_id, field_id, expected_value, note) — mapping-tier (resolved values)
MAPPING_PINS = [
    # OTH-029 2_5 maps to child_2 DOB (the fill-path fan-out is tested in
    # test_fill_smoke; here we pin the mapping target itself).
    ("OTH-029", "2_5", "09/05/2018", "child_2 DOB cell (US-formatted)"),
]


class RecipePlacement(unittest.TestCase):
    def test_recipe_pins(self):
        cache = {}
        for form, fid, expected, note in RECIPE_PINS:
            with self.subTest(form=form, field=fid, note=note):
                out = cache.setdefault(form, recipe_output(form))
                self.assertEqual(
                    out.get(fid), expected,
                    f"{form}.{fid} ({note}): expected {expected!r}, "
                    f"got {out.get(fid)!r}")


class MappingPlacement(unittest.TestCase):
    def test_mapping_pins(self):
        cache = {}
        for form, fid, expected, note in MAPPING_PINS:
            with self.subTest(form=form, field=fid, note=note):
                vals = cache.setdefault(form, mapping_values(form))
                self.assertEqual(
                    vals.get(fid), expected,
                    f"{form}.{fid} ({note}): expected {expected!r}, "
                    f"got {vals.get(fid)!r}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
