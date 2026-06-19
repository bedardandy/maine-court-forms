"""EVAL — Assumption: intended fills actually land in the PDF widgets (step 6).

The PDF-free golden eval proves the *resolution* layer; this proves the final
*write* layer with the real deterministic post-fill check
(``engine.verify_fill``). For each mapping-tier form with a blank PDF present,
it fills the sample case through the **real** mapping entrypoint
(``engine.fill_via_mapping.fill_via_mapping``), reopens the output, and asserts
every intended field is ``placed`` (multi-widget overflow groups legitimately
report ``no-widget``).

Scope note: this covers the mapping path, where the intended value
(``resolve_mapping``) is written verbatim, so a widget-value diff is exact.
Recipe-tier forms apply width-fit/name-collapse transforms at write time, so an
exact field-value oracle isn't meaningful there — recipe placement is covered
by the corpus golden (``test_fill_golden``) and the vision judge
(``evals/vision``) instead.

Blank PDFs are not shipped (see LICENSE), so this auto-skips offline — the same
contract as tests/test_fill_smoke.py. Run it after
``python3 tools/fetch_pdfs.py --all`` to exercise the write path end to end.

Metric:   intended fields not 'placed' (excluding no-widget overflow).
Pass bar: zero, over mapping-tier forms whose blank is available.
"""
from __future__ import annotations

import json
import pathlib
import tempfile
import unittest

# Import evals.common first — it puts tests/ on sys.path so `helpers` resolves.
from evals.common import fillable_forms, is_recipe
import helpers  # noqa: E402  (tests/helpers.py)


class TestVerifyFill(unittest.TestCase):
    def test_intended_fields_are_placed(self):
        available = [f for f in fillable_forms()
                     if not is_recipe(f) and helpers.has_pdf(f)]
        if not available:
            self.skipTest(
                "no mapping-tier blank PDFs present — run tools/fetch_pdfs.py")
        for fid in available:
            with self.subTest(form=fid):
                self._check_one(fid)

    def _check_one(self, fid: str):
        from engine.fill_via_mapping import fill_via_mapping
        from engine.verify_fill import verify_fill
        with tempfile.TemporaryDirectory() as td:
            # the mapping path takes the canonical fact object as-is.
            canonical = json.loads(
                (helpers.FORMS / fid / "examples" / "sample_case.json")
                .read_text())
            res = fill_via_mapping(fid, canonical, pathlib.Path(td))
            self.assertTrue(res.get("ok"),
                            f"{fid}: fill failed: {res.get('error')}")
            self.assertTrue(res.get("out_pdf"), f"{fid}: no out_pdf returned")
            intended = {k: str(v) for k, v in helpers.mapping_values(fid).items()}
            v = verify_fill(res["out_pdf"], intended)
            bad = {k: d for k, d in v.get("fields", {}).items()
                   if d.get("status") not in ("placed", "no-widget")}
            self.assertEqual(bad, {}, f"{fid}: not placed: {json.dumps(bad)}")


if __name__ == "__main__":
    unittest.main()
