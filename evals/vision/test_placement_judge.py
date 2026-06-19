"""EVAL — Assumption: filled values land in the *right* widget visually
(value-vs-label alignment) — the claim the trust tiers ultimately rest on.

Deterministic evals prove a value resolved and was written; only a vision
judge proves it landed next to the correct printed label. This eval is a thin
wrapper over the existing semantic-placement oracle (tests/opus_judge.py,
which already does render -> Opus 4.8 judge -> parse). It fills the sample case
for a small pinned form set, renders, judges, and asserts zero high-severity
misplacement findings.

Opt-in via ``MCF_EVAL_VISION=1`` (needs blank PDFs + a model endpoint and
costs tokens); skipped by default, mirroring tests/test_opus_judge.py.

Metric:   high-severity placement findings across the pinned set.
Pass bar: zero.
"""
from __future__ import annotations

import os
import unittest

import helpers  # tests/helpers.py (on path via evals.common)

VISION = os.environ.get("MCF_EVAL_VISION") == "1"

# Small, representative pinned set spanning a recipe form, a high-field
# mapping form, and a money/worksheet form.
PINNED = ["CV-007", "FM-004", "MJ-009"]


@unittest.skipUnless(VISION, "set MCF_EVAL_VISION=1 to run the vision judge")
class TestPlacementJudge(unittest.TestCase):
    def test_no_high_severity_misplacement(self):
        try:
            import opus_judge  # tests/opus_judge.py
        except Exception as e:  # noqa: BLE001
            self.skipTest(f"opus_judge unavailable: {e}")
        for fid in PINNED:
            if not helpers.has_pdf(fid):
                continue
            with self.subTest(form=fid):
                verdict = opus_judge.judge_form(fid)
                findings = []
                for page in (verdict.get("pages") or {}).values():
                    findings += [f for f in (page.get("findings") or [])
                                 if str(f.get("severity", "")).lower()
                                 in ("high", "critical")]
                self.assertEqual(
                    findings, [],
                    f"{fid}: high-severity placement findings: {findings}")


if __name__ == "__main__":
    unittest.main()
