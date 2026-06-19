"""EVAL — Assumption: completed-form content is stable and correct.

This is the corpus-scale regression oracle the suite otherwise lacks (today
only ~17 fields are pinned in tests/test_placement.py). For every fillable
form it recomputes the PDF-free fill from the sample case and diffs it against
the committed golden in ``golden/<ID>.kv.json``.

A failure means the completed form's content changed: a mapping edit, a recipe
change, or an engine regression silently altered what an LLM consumer would
file. Intentional changes are adopted by re-running ``gen_golden.py --all`` and
reviewing the diff.

Metric:   per-field added / removed / changed across all forms.
Pass bar: zero drift against committed goldens.
"""
from __future__ import annotations

import json
import pathlib
import unittest

from evals.common import fillable_forms, filled_kv, normalize

GOLDEN = pathlib.Path(__file__).resolve().parent / "golden"


def _diff(golden: dict, live: dict):
    added = {k: live[k] for k in live.keys() - golden.keys()}
    removed = {k: golden[k] for k in golden.keys() - live.keys()}
    changed = {k: (golden[k], live[k]) for k in golden.keys() & live.keys()
               if golden[k] != live[k]}
    return added, removed, changed


class TestFillGolden(unittest.TestCase):
    def test_goldens_exist(self):
        missing = [fid for fid in fillable_forms()
                   if not (GOLDEN / f"{fid}.kv.json").exists()]
        self.assertEqual(
            missing, [],
            f"{len(missing)} fillable forms have no golden — run "
            f"`python3 -m evals.fill.gen_golden --all`: {missing[:20]}")

    def test_no_drift_against_golden(self):
        for fid in fillable_forms():
            gp = GOLDEN / f"{fid}.kv.json"
            if not gp.exists():
                continue  # reported by test_goldens_exist
            with self.subTest(form=fid):
                golden = json.loads(gp.read_text())
                live = normalize(filled_kv(fid))
                added, removed, changed = _diff(golden, live)
                self.assertEqual(
                    (added, removed, changed), ({}, {}, {}),
                    f"{fid} drifted from golden — "
                    f"added={added} removed={removed} changed={changed}; "
                    f"re-run gen_golden.py if intended")


if __name__ == "__main__":
    unittest.main()
