"""EVAL — Assumption: the preflight gate (step 3) passes the exact cases the
fill paths consume.

Every form ships an ``examples/sample_case.json`` that the fill engine fills
from. If preflight would reject that same case, the documented flow is
self-contradictory (the gate blocks its own examples). This eval runs
``preflight_case`` over every shipped sample case and asserts it is clean,
which proves the extract -> preflight -> fill links are mutually consistent.

Metric:   count of sample cases with preflight errors.
Pass bar: zero.
"""
from __future__ import annotations

import json
import unittest

from evals.common import FORMS, all_mappings
from tools.preflight import preflight_case


class TestPreflightRoundtrip(unittest.TestCase):
    def test_every_sample_case_is_preflight_clean(self):
        failures = []
        for fid in all_mappings():
            sp = FORMS / fid / "examples" / "sample_case.json"
            if not sp.exists():
                continue
            case = json.loads(sp.read_text())
            res = preflight_case(case, form_id=fid)
            if not res["ok"]:
                failures.append((fid, [e["code"] for e in res["errors"]]))
        self.assertEqual(
            failures, [],
            f"{len(failures)} sample cases fail preflight: {failures[:20]}")

    def test_preflight_catches_a_seeded_role_typo(self):
        # Proves the gate actually bites: a wrong-vocab role must error with a
        # suggestion (the canonical silent-loss footgun).
        case = {"matter": {}, "parties": {"lawyer": {"full_name": "X"}}}
        res = preflight_case(case)
        self.assertFalse(res["ok"])
        codes = {e["code"] for e in res["errors"]}
        self.assertIn("unknown-party-role", codes)
        sugg = [e.get("suggestion") for e in res["errors"]
                if e["code"] == "unknown-party-role"]
        self.assertIn("parties.attorney", sugg)


if __name__ == "__main__":
    unittest.main()
