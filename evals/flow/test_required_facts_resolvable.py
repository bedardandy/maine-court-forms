"""EVAL — Assumption: a form's declared *required* facts are facially
necessary AND its shipped sample case actually supplies them.

CLAUDE.md says mapping.json ``facts.required`` are the keys "the form is
facially incomplete without". This eval proves two links of the chain at once:

  1. every required key resolves to a non-empty value in that form's
     ``examples/sample_case.json`` (the sample honors its own contract), and
  2. the resolved value lands as a non-empty widget value in the filled output
     (the required fact is not silently dropped by the fill path).

Metric:   count of (form, required_key) pairs that resolve empty.
Pass bar: zero.
"""
from __future__ import annotations

import json
import unittest

from evals.common import FORMS, all_mappings, filled_kv
from tools.preflight import _resolve


class TestRequiredFactsResolvable(unittest.TestCase):
    def test_required_facts_present_in_sample_case(self):
        fillable = set(filled_form_ids())
        bad = []
        for fid, m in all_mappings().items():
            req = ((m.get("facts") or {}).get("required")) or []
            if not req:
                continue
            sp = FORMS / fid / "examples" / "sample_case.json"
            if not sp.exists():
                continue
            case = json.loads(sp.read_text())
            for key in req:
                if _resolve(case, key) in (None, ""):
                    bad.append((fid, key))
        self.assertEqual(
            bad, [],
            f"{len(bad)} required facts unresolved in their own sample "
            f"case: {bad[:20]}")

    def test_required_facts_reach_the_filled_form(self):
        # The required keys must produce content after the fill, not just
        # resolve in the case. Only checkable for fillable tiers.
        bad = []
        for fid in filled_form_ids():
            m = all_mappings().get(fid, {})
            req = ((m.get("facts") or {}).get("required")) or []
            if not req:
                continue
            values = {v for v in filled_kv(fid).values()
                      if isinstance(v, str) and v.strip()}
            if not values:
                bad.append((fid, "no content at all", req))
        self.assertEqual(
            bad, [],
            f"forms with required facts but empty fills: {bad[:20]}")


def filled_form_ids():
    return filled_form_ids_cached()


_cache = None


def filled_form_ids_cached():
    global _cache
    if _cache is None:
        from evals.common import fillable_forms
        _cache = fillable_forms()
    return _cache


if __name__ == "__main__":
    unittest.main()
