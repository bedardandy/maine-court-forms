"""EVAL — Assumption: intended fills actually land in the PDF widgets (step 6).

The PDF-free golden eval proves the *resolution* layer; this proves the final
*write* layer with the real deterministic post-fill check
(``engine.verify_fill``). For each fillable form with a blank PDF present, it
fills the sample case, reopens the output, and asserts every intended field is
``placed`` (multi-widget overflow groups legitimately report ``no-widget``).

Blank PDFs are not shipped (see LICENSE), so this auto-skips offline — the same
contract as tests/test_fill_smoke.py. Run it after
``python3 tools/fetch_pdfs.py --all`` to exercise the write path end to end.

Metric:   intended fields not 'placed' (excluding no-widget overflow).
Pass bar: zero, over forms whose blank is available.
"""
from __future__ import annotations

import json
import tempfile
import unittest

import helpers  # tests/helpers.py (on path via evals.common)

from evals.common import fillable_forms, is_recipe


class TestVerifyFill(unittest.TestCase):
    def test_intended_fields_are_placed(self):
        available = [f for f in fillable_forms() if helpers.has_pdf(f)]
        if not available:
            self.skipTest("no blank PDFs present — run tools/fetch_pdfs.py")
        for fid in available:
            with self.subTest(form=fid):
                self._check_one(fid)

    def _check_one(self, fid: str):
        from engine.verify_fill import verify_fill
        with tempfile.TemporaryDirectory() as td:
            if is_recipe(fid):
                from engine import fill as fill_mod
                res = fill_mod.fill_one_to_dir(fid, out_dir=td) \
                    if hasattr(fill_mod, "fill_one_to_dir") else None
            else:
                from engine import fill_via_mapping as fvm
                res = fvm.fill_form(fid, helpers.sample_case(fid), out_dir=td) \
                    if hasattr(fvm, "fill_form") else None
            if not res or not res.get("out_pdf"):
                self.skipTest(f"{fid}: no programmatic fill entrypoint")
            intended = {k: str(v) for k, v in
                        (res.get("fields_written_to_pdf")
                         or helpers.mapping_values(fid)).items()}
            v = verify_fill(res["out_pdf"], intended)
            bad = {k: d for k, d in v.get("fields", {}).items()
                   if d.get("status") not in ("placed", "no-widget")}
            self.assertEqual(bad, {}, f"{fid}: not placed: {json.dumps(bad)}")


if __name__ == "__main__":
    unittest.main()
