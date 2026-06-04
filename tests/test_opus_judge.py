"""Opt-in semantic placement check: Claude Opus 4.8 judges sentinel renders.

Skipped by default — this costs tokens and needs the `claude` CLI + local
blank PDFs, so it never runs in CI. Enable explicitly:

    MCF_OPUS_JUDGE=1 python3 -m unittest tests.test_opus_judge

It renders the pinned forms, asks Opus 4.8 whether each value sits under a
label consistent with its meaning, and fails if any form comes back
"misplaced". This is the open-ended counterpart to the deterministic pins in
test_placement.py.
"""
import os
import sys
import unittest
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

JUDGE_FORMS = ["JV-006-W", "NC-001", "MJ-SC-012", "MJ-009", "PC-034", "OTH-029"]


@unittest.skipUnless(os.environ.get("MCF_OPUS_JUDGE") == "1",
                     "set MCF_OPUS_JUDGE=1 to run the Opus 4.8 placement judge")
class OpusPlacementJudge(unittest.TestCase):
    def test_pinned_forms_judged_clean(self):
        import shutil
        if not shutil.which("claude"):
            self.skipTest("claude CLI not on PATH")
        from tests.opus_judge import judge_form
        misplaced = []
        for fid in JUDGE_FORMS:
            with self.subTest(form=fid):
                r = judge_form(fid)
                if r["verdict"] == "skip":
                    self.skipTest(f"{fid}: {r.get('summary')}")
                    continue
                if r["verdict"] == "misplaced":
                    misplaced.append((fid, r.get("pages")))
        self.assertEqual(misplaced, [], f"Opus flagged misplacements: {misplaced}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
