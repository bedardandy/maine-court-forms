"""Every recipe-dispatched form runs its `process()` without crashing.

PDF-free: exercises map_form + recipe.process over each form's committed
schema + sample case. This is the broad regression net — a recipe edit that
throws on any form (the kind of break the manual sweep used to catch) fails
here. Pairs with the targeted value checks in test_placement.py.
"""
import sys
import unittest
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from tests.helpers import recipe_dispatch, recipe_output, sample_case


class RecipeSmoke(unittest.TestCase):
    def test_every_recipe_form_fills_without_crash(self):
        forms = sorted(recipe_dispatch())
        self.assertGreater(len(forms), 50, "expected the full recipe table")
        failures = []
        filled = 0
        no_sample = []
        for fid in forms:
            if sample_case(fid) is None:
                no_sample.append(fid)
                continue
            with self.subTest(form=fid):
                try:
                    out = recipe_output(fid)
                    self.assertIsInstance(out, dict)
                    filled += 1
                except Exception as e:  # noqa: BLE001
                    failures.append((fid, repr(e)))
        self.assertEqual(failures, [], f"recipes crashed: {failures}")
        self.assertGreater(filled, 50, f"only {filled} filled; no_sample={no_sample}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
