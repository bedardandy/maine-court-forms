"""EVAL — Assumption: routing maps a plain-language situation to the right form.

Step 1 of the agent workflow is ``tools/find_forms.py``. This eval drives it
with every narrative in ``tools/smoke/fact_patterns.json`` and measures
top-k recall against each pattern's ``expect_forms`` hint.

find_forms is deterministic keyword routing, so this needs no model — it
falsifies the routing claim directly.

FINDINGS (2026-06-19, what this eval surfaced):
  * 14 ``expect_forms`` ids in fact_patterns.json reference forms that do NOT
    exist in the corpus (see KNOWN_PHANTOM_FORMS). Recall is measured only over
    expected forms that exist — you cannot route to a form that isn't there.
  * Over the existing expected forms, the deterministic router lands a hit in
    the top-5 ~0.69 of the time. MIN_RECALL is set as a *regression floor* at
    the current baseline, not an aspiration — raise it as routing improves.

Metric:   fraction of patterns (with >=1 existing expected form) whose expected
          form appears in find_forms' top-K results.
Pass bar: recall >= MIN_RECALL (regression floor).
"""
from __future__ import annotations

import json
import unittest

from evals.common import FORMS, REPO

TOP_K = 5
MIN_RECALL = 0.60  # current baseline ~0.69; floor against regression

# fact_patterns.json references these ids but no forms/<ID>/ dir exists. Locked
# so a NEW phantom reference fails (the repo's known-orphans pattern); prune or
# repoint these in fact_patterns.json to clear them.
KNOWN_PHANTOM_FORMS = {
    "CR-016", "CR-028", "CR-039", "CR-040", "CV-021", "CV-035", "CV-160",
    "CV-168", "CV-169", "FM-030", "FM-058", "FM-059", "PA-009", "PC-160",
}

PATTERNS = json.loads(
    (REPO / "tools" / "smoke" / "fact_patterns.json").read_text()
)["patterns"]


def _exists(form_id: str) -> bool:
    return (FORMS / form_id).is_dir()


def _topk_ids(query: str, k: int) -> list[str]:
    from tools.find_forms import find_forms
    res = find_forms(query)
    ids = [f["form"] for f in res.get("forms", [])][:k]
    # workflows also surface ordered form sequences — count their members too,
    # since an agent reads both.
    for wf in res.get("workflows", []):
        ids.extend(wf.get("forms", []))
    return ids


class TestRoutingRecall(unittest.TestCase):
    def test_topk_recall_meets_bar(self):
        hits = 0
        scored = 0
        misses = []
        for p in PATTERNS:
            # Only score expected forms that actually exist in the corpus.
            expect = [e for e in (p.get("expect_forms") or []) if _exists(e)]
            if not expect:
                continue
            scored += 1
            found = set(_topk_ids(p["narrative"], TOP_K))
            if any(e in found for e in expect):
                hits += 1
            else:
                misses.append((p["id"], expect, sorted(found)[:TOP_K]))
        recall = hits / scored if scored else 1.0
        msg = (f"top-{TOP_K} routing recall {recall:.2f} < {MIN_RECALL} "
               f"({hits}/{scored}); misses: {misses}")
        self.assertGreaterEqual(recall, MIN_RECALL, msg)

    def test_no_new_phantom_expected_forms(self):
        # A routing hint pointing at a non-existent form id is a broken fixture,
        # not a routing failure. The current phantom set is locked; a NEW one
        # fails so the fixture can't rot further.
        phantom = {e for p in PATTERNS for e in (p.get("expect_forms") or [])
                   if not _exists(e)}
        new = sorted(phantom - KNOWN_PHANTOM_FORMS)
        stale = sorted(KNOWN_PHANTOM_FORMS - phantom)
        self.assertEqual(new, [],
                         f"new phantom expect_forms (add a forms/<ID>/ or "
                         f"repoint the pattern): {new}")
        self.assertEqual(stale, [],
                         f"these phantoms were fixed — drop from "
                         f"KNOWN_PHANTOM_FORMS: {stale}")


if __name__ == "__main__":
    unittest.main()
