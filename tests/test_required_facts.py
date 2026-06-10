"""Per-form required/used facts declaration (tools/derive_required_facts.py).

Every mapping.json carries a deterministic "facts" block; required is the
conservative caption-name subset; the committed blocks match a fresh
derivation (no drift).
"""
import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.derive_required_facts import (  # noqa: E402
    _REQUIRED_KEYS, derive_facts_block,
)

FORMS = sorted(p for p in (ROOT / "forms").iterdir()
               if (p / "mapping.json").exists())


class TestRequiredFacts(unittest.TestCase):
    def test_every_form_declares_facts(self):
        for fdir in FORMS:
            with self.subTest(form=fdir.name):
                mp = json.loads((fdir / "mapping.json").read_text())
                facts = mp.get("facts")
                self.assertIsInstance(facts, dict, "missing facts block")
                self.assertIn("required", facts)
                self.assertIn("used", facts)
                # required is a conservative subset of the caption-name keys
                # and of used
                for k in facts["required"]:
                    self.assertIn(k, _REQUIRED_KEYS)
                    self.assertIn(k, facts["used"])

    def test_committed_blocks_match_derivation(self):
        """The committed facts blocks are exactly what the tool derives —
        regenerating is a no-op (guards against hand-edits drifting)."""
        for fdir in FORMS:
            with self.subTest(form=fdir.name):
                mp = json.loads((fdir / "mapping.json").read_text())
                self.assertEqual(mp.get("facts"), derive_facts_block(fdir))

    def test_recipe_forms_harvest_recipe_keys(self):
        """Recipe-tier forms get their keys from the recipe source, not the
        (empty) map — e.g. CV-037's subpoena facts."""
        mp = json.loads((ROOT / "forms/CV-037/mapping.json").read_text())
        self.assertEqual(mp["status"], "recipe")
        self.assertIn("facts.witness_name", mp["facts"]["used"])
        self.assertEqual(mp["facts"]["required"], [],
                         "recipes are presence-gated; nothing is required")

    def test_mapping_form_requires_caption_names(self):
        mp = json.loads((ROOT / "forms/PA-001/mapping.json").read_text())
        self.assertIn("parties.plaintiff.full_name", mp["facts"]["required"])
        self.assertIn("parties.defendant.full_name", mp["facts"]["required"])
        self.assertNotIn("parties.child_1.full_name", mp["facts"]["required"],
                         "child rows are optional")


if __name__ == "__main__":
    unittest.main()
