"""Per-form sample cases (tools/gen_sample_cases.py).

Generated samples must exercise the form's own canonical keys (resolve the
full mapping), generic placeholders must be flagged, and every sample stays
preflight-clean (also asserted from test_preflight).
"""
import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

FORMS = sorted(p for p in (ROOT / "forms").iterdir()
               if (p / "mapping.json").exists())


def _sample(fdir):
    return json.loads((fdir / "examples" / "sample_case.json").read_text())


class TestSampleCases(unittest.TestCase):
    def test_samples_are_per_form(self):
        """Most forms carry a tailored (non-generic) sample now."""
        tailored = [f.name for f in FORMS if not _sample(f).get("generic")]
        self.assertGreater(len(tailored), 240,
                           f"only {len(tailored)} tailored samples")

    def test_no_mappable_forms_are_marked_generic(self):
        for fdir in FORMS:
            mp = json.loads((fdir / "mapping.json").read_text())
            if mp.get("status") != "no-mappable-fields":
                continue
            with self.subTest(form=fdir.name):
                self.assertTrue(_sample(fdir).get("generic"),
                                "nothing to tailor -> must be flagged generic")

    def test_generated_samples_resolve_their_mapping(self):
        """A tailored mapping-tier sample must resolve every mapped key —
        that's the point of tailoring (hand-built samples are exempt)."""
        from engine.fill_via_mapping import resolve_mapping
        HAND_BUILT = {"FM-062", "FM-068", "FM-070", "CV-256", "OTH-045",
                      "CR-CV-FM-JV-PA-PC-286"}
        checked = 0
        for fdir in FORMS:
            mp = json.loads((fdir / "mapping.json").read_text())
            if mp.get("status") not in ("verified", "opus-adjudicated"):
                continue
            if fdir.name in HAND_BUILT:
                continue
            case = _sample(fdir)
            if case.get("generic"):
                continue
            with self.subTest(form=fdir.name):
                res = resolve_mapping(fdir.name, case)
                self.assertEqual(res["unresolved"], [],
                                 f"{fdir.name}: sample misses mapped keys")
                checked += 1
        self.assertGreater(checked, 180)

    def test_samples_are_clearly_fictional(self):
        """Every tailored sample keeps the fictional-placeholder summary
        disclaimer (never realistic-looking real-person data)."""
        for fdir in FORMS:
            case = _sample(fdir)
            if case.get("generic"):
                continue
            with self.subTest(form=fdir.name):
                summary = (case.get("facts") or {}).get("summary", "")
                self.assertIn("fictitious", summary)


if __name__ == "__main__":
    unittest.main()
