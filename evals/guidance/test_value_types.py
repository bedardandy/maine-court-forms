"""EVAL — Assumption: the value-type validators are sound — they flag clear
mismatches and (critically) never false-positive on legitimate values.

These power preflight's type warnings, so a false positive trains agents to
ignore the signal. The tests are deliberately adversarial: valid values across
the many accepted formats must pass, and obvious cross-type swaps (a phone in a
ZIP box, a name in a currency box) must be flagged.

Pass bar: every "should pass" case returns None; every "should flag" case
returns a message.
"""
from __future__ import annotations

import unittest

from tools.value_types import validate_value

# value_type -> values that MUST validate clean (None).
VALID = {
    "zip": ["04101", "04101-1234"],
    "currency": ["1250", "1,250.00", "$1,250.00", "$0", "0.00", "-50.00"],
    "percent": ["0", "50", "100", "12.5", "50%"],
    "email": ["a@b.com", "first.last@court.maine.gov"],
    "phone": ["207-555-0142", "(207) 555-0142", "2075550142"],
    "state": ["ME", "Maine", "ny", "New Hampshire"],
    "county": ["Cumberland", "york", "Penobscot County", "Aroostook"],
    "date": ["2026-06-19", "06/19/2026", "6/9/26"],
    "time": ["10:00", "10:00 AM", "9:30 p.m.", "9"],
    "person_name": ["Maria Elena Vasquez", "O'Donnell", "Jon Pierce Rivers"],
    # free-form / non-strict types must never flag.
    "free_text": ["anything at all 123 $%", ""],
    "court_location": ["Portland District Court"],
    "docket": ["CV-2024-0099"],
    "checkbox": ["X"],
    "signature": [""],
    "organization_name": ["Acme Example Company"],
    "address": ["58 Granite Street"],
    "city": ["Portland"],
    "bar_number": ["1234"],
}

# (value_type, value) pairs that MUST be flagged (cross-type swaps + junk).
SHOULD_FLAG = [
    ("zip", "207-555-0142"),      # phone in ZIP
    ("zip", "Portland"),
    ("currency", "Acme Company"),  # name in currency
    ("currency", "two hundred"),
    ("email", "not-an-email"),
    ("phone", "abc"),
    ("state", "Portland"),         # city in state
    ("state", "100.00"),
    ("county", "Cumberland County 12"),  # digits in county
    ("county", "Suffolk"),         # not a Maine county
    ("date", "Sample text"),
    ("date", "100.00"),
    ("time", "2 hours"),
    ("person_name", "100.00"),
]


class TestValidatorsNoFalsePositives(unittest.TestCase):
    def test_valid_values_pass(self):
        bad = []
        for vt, values in VALID.items():
            for v in values:
                if validate_value(vt, v) is not None:
                    bad.append((vt, v, validate_value(vt, v)))
        self.assertEqual(bad, [], f"false positives: {bad}")

    def test_none_and_empty_always_pass(self):
        for vt in VALID:
            self.assertIsNone(validate_value(vt, None))
            self.assertIsNone(validate_value(vt, ""))
            self.assertIsNone(validate_value(vt, "   "))


class TestValidatorsCatchMismatches(unittest.TestCase):
    def test_clear_mismatches_flagged(self):
        missed = [(vt, v) for vt, v in SHOULD_FLAG
                  if validate_value(vt, v) is None]
        self.assertEqual(missed, [], f"missed mismatches: {missed}")

    def test_unknown_value_type_is_lenient(self):
        # An unrecognized type must never flag (forward-compat).
        self.assertIsNone(validate_value("brand_new_type", "whatever"))


if __name__ == "__main__":
    unittest.main()
