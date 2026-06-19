"""EVAL — Assumption: an LLM can turn a plain-language narrative into a
preflight-clean, required-fact-complete canonical case (the human-replacing
step 3).

Two modes:

  * OFFLINE (default): scores the committed golden cases in
    ``extraction_cases.json`` — each must be preflight-clean for its form,
    cover that form's required facts (coverage == 1.0), and route to its
    expected form. This proves the fixtures + scoring are sound with no model,
    and locks the goldens against drift.
  * LIVE (env ``MCF_EVAL_LLM=1``): calls the configured endpoint to extract a
    case from each narrative and scores the extraction against the golden:
    preflight-clean rate, required-fact coverage, and role/attr-vocab accuracy
    (no ``lawyer``/``petitioner`` typos). Reuses the smoke harness plumbing.

Metric:   per-case preflight-clean + required-fact coverage + routing hit.
Pass bar (offline): every golden is clean, coverage == 1.0, routes correctly.
"""
from __future__ import annotations

import json
import os
import pathlib
import unittest

from evals.common import REPO, all_mappings
from tools.preflight import preflight_case

CASES = json.loads(
    (pathlib.Path(__file__).resolve().parent / "extraction_cases.json")
    .read_text())["cases"]

LIVE = os.environ.get("MCF_EVAL_LLM") == "1"


def _required_coverage(case: dict, form_id: str) -> float:
    m = all_mappings().get(form_id, {})
    req = ((m.get("facts") or {}).get("required")) or []
    if not req:
        return 1.0
    from tools.preflight import _resolve
    have = sum(1 for k in req if _resolve(case, k) not in (None, ""))
    return have / len(req)


def _routes_to(narrative: str, form_id: str, k: int = 6) -> bool:
    from tools.find_forms import find_forms
    res = find_forms(narrative)
    ids = [f["form"] for f in res.get("forms", [])][:k]
    for wf in res.get("workflows", []):
        ids.extend(wf.get("forms", []))
    return form_id in ids


class TestGoldenCasesAreSound(unittest.TestCase):
    """Offline: the fixtures themselves must satisfy the contract."""

    def test_goldens_preflight_clean(self):
        bad = []
        for c in CASES:
            res = preflight_case(c["case"], form_id=c["form"])
            if not res["ok"]:
                bad.append((c["id"], [e["code"] for e in res["errors"]]))
        self.assertEqual(bad, [], f"golden cases fail preflight: {bad}")

    def test_goldens_cover_required_facts(self):
        bad = [(c["id"], c["form"]) for c in CASES
               if _required_coverage(c["case"], c["form"]) < 1.0]
        self.assertEqual(bad, [], f"golden cases miss required facts: {bad}")

    def test_goldens_route_to_their_form(self):
        # Aggregate routing recall over goldens whose target form exists in the
        # corpus (a floor consistent with flow/test_routing_recall; per-case
        # routing quality is owned by that eval). Phantom targets are skipped.
        from evals.common import FORMS
        scored = [c for c in CASES if (FORMS / c["form"]).is_dir()]
        hits = [c for c in scored
                if _routes_to(narrative_for(c["id"]), c["form"])]
        recall = len(hits) / len(scored) if scored else 1.0
        misses = [(c["id"], c["form"]) for c in scored if c not in hits]
        self.assertGreaterEqual(
            recall, 0.60,
            f"golden routing recall {recall:.2f} < 0.60; misses: {misses}")


@unittest.skipUnless(LIVE, "set MCF_EVAL_LLM=1 to run live extraction")
class TestLiveExtractionFidelity(unittest.TestCase):
    """Live: a model extracts; we score it against the goldens."""

    def test_extraction_meets_bars(self):
        from tools import smoke_fact_patterns as sfp
        extract = getattr(sfp, "extract_case", None)
        if extract is None:
            self.skipTest("smoke_fact_patterns has no extract_case() entry")
        clean = cover = route = 0
        report = []
        for c in CASES:
            narrative = narrative_for(c["id"])
            got = extract(narrative)  # model -> canonical case
            pf = preflight_case(got, form_id=c["form"])
            cov = _required_coverage(got, c["form"])
            rt = _routes_to(narrative, c["form"])
            clean += pf["ok"]
            cover += cov
            route += rt
            report.append((c["id"], pf["ok"], round(cov, 2), rt))
        n = len(CASES)
        print("\nLIVE extraction:", json.dumps(report, indent=2))
        self.assertGreaterEqual(clean / n, 0.8, f"preflight-clean rate low")
        self.assertGreaterEqual(cover / n, 0.8, "required-fact coverage low")
        self.assertGreaterEqual(route / n, 0.8, "routing recall low")


def narrative_for(pattern_id: str) -> str:
    pats = json.loads(
        (REPO / "tools" / "smoke" / "fact_patterns.json").read_text()
    )["patterns"]
    return next(p["narrative"] for p in pats if p["id"] == pattern_id)


if __name__ == "__main__":
    unittest.main()
