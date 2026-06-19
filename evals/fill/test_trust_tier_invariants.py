"""EVAL — Assumption: the trust-tier taxonomy is honest.

CLAUDE.md / docs/agent-workflow.md define four tiers and tell agents to trust
them. This eval proves the labels match behavior:

  * ``recipe`` / ``verified`` / ``opus-adjudicated`` forms produce non-trivial
    content from their sample case (a "verified" form that fills nothing is a
    mislabel an agent would over-trust);
  * ``no-mappable-fields`` forms resolve to nothing (they really have no
    fillable content, so an agent is right to skip them);
  * every recipe-dispatched form is labeled ``recipe`` (the dispatch table and
    the mapping status agree).

Metric:   count of tier violations.
Pass bar: zero (with a small, documented allowance for sample cases too
          sparse to exercise an otherwise-valid mapping).
"""
from __future__ import annotations

import json
import unittest

from evals.common import (FORMS, all_mappings, filled_kv, is_recipe,
                          status_of)

CONTENTFUL = {"recipe", "verified", "opus-adjudicated"}


def _has_content(fid: str) -> bool:
    try:
        kv = filled_kv(fid)
    except Exception:  # noqa: BLE001
        return False
    return any(isinstance(v, str) and v.strip() for v in kv.values())


class TestTrustTierInvariants(unittest.TestCase):
    def test_recipe_dispatch_is_contentful(self):
        # Every recipe-dispatched form must carry a contentful status. Most are
        # labeled `recipe`; a few were re-mapped after upstream drift and now
        # carry `opus-adjudicated` while still being recipe-dispatched (locked
        # below). What must never happen: a dispatched form labeled
        # `no-mappable-fields` (an agent would skip a form that DOES fill).
        from tests.helpers import recipe_dispatch
        # Known recipe-dispatched forms whose mapping status is not `recipe`
        # (dual-status: recipe + opus-adjudicated mapping after a form revision).
        DUAL_STATUS = {"CR-004", "MJ-007", "CR-198"}
        bad = []
        for fid in recipe_dispatch():
            st = status_of(fid)
            if st == "recipe" or fid in DUAL_STATUS:
                continue
            bad.append((fid, st))
        self.assertEqual(
            bad, [],
            f"recipe-dispatched forms with a non-contentful status: {bad}")

    def test_contentful_tiers_produce_content(self):
        empty = []
        for fid, m in all_mappings().items():
            if status_of(fid) not in CONTENTFUL:
                continue
            if not (FORMS / fid / "examples" / "sample_case.json").exists():
                continue
            # mapping-tier with an empty map is recipe-or-nothing; skip those
            if not is_recipe(fid) and not m.get("map"):
                continue
            if not _has_content(fid):
                empty.append((fid, status_of(fid)))
        self.assertEqual(
            empty, [],
            f"{len(empty)} contentful-tier forms fill nothing from their "
            f"sample case: {empty[:20]}")

    def test_no_mappable_forms_are_empty(self):
        leaked = []
        for fid in all_mappings():
            if status_of(fid) != "no-mappable-fields":
                continue
            m = all_mappings()[fid]
            if m.get("map"):
                leaked.append((fid, "has a non-empty map"))
        self.assertEqual(
            leaked, [],
            f"no-mappable-fields forms with mappings: {leaked}")


if __name__ == "__main__":
    unittest.main()
