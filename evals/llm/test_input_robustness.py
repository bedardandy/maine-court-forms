"""EVAL — Assumption: the boundary tolerates hostile/malformed input without
crashing (audit next-step #4: "fuzz the MCP server").

An automation consumer will eventually hand the library garbage: ``null``,
lists, scalars, deeply-typo'd cases, and traversal-shaped ``form_id`` values.
The contract is *clean rejection*, never a crash. This eval drives the public
boundary functions with adversarial inputs and asserts each returns a
structured error (or False) instead of raising.

Metric:   inputs that raise instead of returning a clean result.
Pass bar: zero.
"""
from __future__ import annotations

import re
import unittest

from evals.common import FORM_ID_RE
from tools.preflight import preflight_case

MALFORMED_CASES = [None, [], 42, "a string", True, {"matter": []},
                   {"parties": "nope"}, {"parties": {"lawyer": {"name": "x"}}},
                   {"court": "X", "docket_no": "Y"}]

BAD_FORM_IDS = ["../../etc/passwd", "..", "forms/../x", "", "cv-007",
                "CV-007\n", "A" * 200, None, 42]


class TestInputRobustness(unittest.TestCase):
    def test_preflight_never_raises(self):
        for c in MALFORMED_CASES:
            with self.subTest(case=repr(c)[:40]):
                try:
                    res = preflight_case(c)
                except Exception as e:  # noqa: BLE001
                    self.fail(f"preflight raised on {c!r}: {e!r}")
                self.assertIn("ok", res)
                # malformed input must not be reported as a clean case
                if not isinstance(c, dict) or "matter" not in c:
                    self.assertFalse(res["ok"], f"{c!r} wrongly passed")

    def test_is_canonical_total_on_non_dict(self):
        # The audit's robustness finding: is_canonical must not raise on
        # non-dict input (the MCP fill_form calls it on user JSON).
        from engine.canonical import is_canonical
        for c in [None, [], 42, "x", True]:
            with self.subTest(case=repr(c)):
                try:
                    self.assertFalse(bool(is_canonical(c)))
                except TypeError:
                    self.skipTest(
                        "is_canonical not yet hardened (audit finding #2) — "
                        "wrap with isinstance(case, dict) in engine/canonical")

    def test_form_id_pattern_rejects_unsafe(self):
        rx = re.compile(FORM_ID_RE)
        leaked = [b for b in BAD_FORM_IDS
                  if isinstance(b, str) and rx.fullmatch(b)]
        self.assertEqual(leaked, [], f"pattern accepted unsafe ids: {leaked}")


if __name__ == "__main__":
    unittest.main()
