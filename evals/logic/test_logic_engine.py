"""EVAL — Assumption: the if/then expression engine is correct and total.

The logic layer's warnings are only trustworthy if the evaluator is right and
never crashes on malformed input. These are adversarial unit tests of every
operator plus malformed-expression safety.

Pass bar: every case matches its expected truth value; no input raises.
"""
from __future__ import annotations

import unittest

from tools.logic_engine import evaluate, evaluate_rules

CTX = {
    "case": {
        "facts": {"rel": "spouse", "kids": True, "amt": "30,000",
                  "t": "1:00", "pct": "25%", "empty": ""},
        "matter": {"court_county": "York"},
        "parties": {"child_1": {"full_name": "Kid"}},
    },
    "fields": {"superior_court": "X", "district_court": "X", "blank": ""},
}

CASES = [
    ({"==": [{"var": "facts.rel"}, "spouse"]}, True),
    ({"==": [{"var": "facts.rel"}, "Spouse"]}, True),       # case-insensitive
    ({"!=": [{"var": "facts.rel"}, "dating"]}, True),
    ({"in": [{"var": "facts.rel"}, ["spouse", "ex"]]}, True),
    ({"in": [{"var": "facts.rel"}, ["ex"]]}, False),
    ({"and": [{"truthy": "facts.kids"}, {"present": "facts.amt"}]}, True),
    ({"or": [{"truthy": "facts.missing"}, {"truthy": "facts.kids"}]}, True),
    ({"not": {"present": "facts.missing"}}, True),
    ({"present": "facts.empty"}, False),                    # "" is absent
    ({"absent": "facts.empty"}, True),
    ({"truthy": "fields.blank"}, False),
    ({">": [{"var": "facts.amt"}, 20000]}, True),           # strips comma
    ({"<": [{"var": "facts.amt"}, 20000]}, False),
    ({">=": [{"var": "facts.pct"}, 25]}, True),             # strips %
    ({"matches": [{"var": "facts.t"}, r"^\d{1,2}:\d{2}$"]}, True),
    ({"contains": [{"var": "facts.rel"}, "ous"]}, True),
    ({"and": [{"truthy": "field:superior_court"},
              {"truthy": "field:district_court"}]}, True),
    ({"==": [{"var": "facts.missing"}, "x"]}, False),       # missing -> falsy
    ({">": [{"var": "facts.rel"}, 5]}, False),              # non-numeric cmp
]


class TestEvaluator(unittest.TestCase):
    def test_operators(self):
        for expr, expected in CASES:
            with self.subTest(expr=expr):
                self.assertEqual(evaluate(expr, CTX), expected)

    def test_malformed_never_raises(self):
        for junk in [None, {}, [], "x", 42, {"bogus_op": [1, 2]},
                     {"==": [1]}, {"and": "notalist"}, {"<": ["a", "b"]},
                     {"matches": [None, None]}]:
            with self.subTest(junk=junk):
                try:
                    evaluate(junk, CTX)
                except Exception as e:  # noqa: BLE001
                    self.fail(f"evaluate raised on {junk!r}: {e!r}")

    def test_evaluate_rules_total_on_bad_input(self):
        for bad in [None, {}, {"rules": None}, {"rules": [{"kind": "x"}]},
                    {"rules": [{"kind": "conditional_required"}]}]:
            self.assertIsInstance(evaluate_rules(bad, {}, {}), list)


if __name__ == "__main__":
    unittest.main()
