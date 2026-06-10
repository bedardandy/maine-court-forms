"""The lean/audit schema split (tools/split_schema.py) invariants.

schema.json must stay lean (no build-time research keys); schema.audit.json
must carry them, parallel to the lean fields; merge_audit() must reconstruct
the full record; and the splitter must be idempotent on lean schemas.
"""
import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.split_schema import (  # noqa: E402
    AUDIT_FIELD_KEYS, AUDIT_TOP_KEYS, load_full_schema, merge_audit,
    split_schema,
)

FORMS = sorted(p for p in (ROOT / "forms").iterdir()
               if (p / "schema.json").exists())


class TestSchemaSplit(unittest.TestCase):
    def test_all_schemas_are_lean(self):
        """No tracked schema.json carries research keys (they live in
        schema.audit.json)."""
        for fdir in FORMS:
            with self.subTest(form=fdir.name):
                schema = json.loads((fdir / "schema.json").read_text())
                for k in AUDIT_TOP_KEYS:
                    self.assertNotIn(k, schema)
                for f in schema.get("fields", []):
                    leaked = set(f) & set(AUDIT_FIELD_KEYS)
                    self.assertFalse(leaked, f"{fdir.name}: {leaked}")

    def test_audit_parallel_and_mergeable(self):
        """Audit entries point at valid field indices and merge_audit
        restores the research keys onto the right field."""
        checked = 0
        for fdir in FORMS:
            ap = fdir / "schema.audit.json"
            if not ap.exists():
                continue
            lean = json.loads((fdir / "schema.json").read_text())
            audit = json.loads(ap.read_text())
            n = len(lean.get("fields", []))
            full = merge_audit(lean, audit)
            for entry in audit.get("fields", []):
                i = entry["i"]
                self.assertTrue(0 <= i < n, f"{fdir.name}: index {i} out of range")
                self.assertEqual(entry.get("field_id"),
                                 lean["fields"][i].get("field_id"),
                                 f"{fdir.name}: audit/lean field_id mismatch at {i}")
                for k in entry:
                    if k in AUDIT_FIELD_KEYS:
                        self.assertEqual(full["fields"][i][k], entry[k])
            checked += 1
        self.assertGreater(checked, 300, "expected audit files for most forms")

    def test_split_idempotent_on_lean(self):
        schema = json.loads((FORMS[0] / "schema.json").read_text())
        lean, audit = split_schema(schema)
        self.assertIsNone(audit, "splitting a lean schema must be a no-op")
        self.assertEqual(json.dumps(lean, sort_keys=True),
                         json.dumps(schema, sort_keys=True))

    def test_load_full_schema_roundtrip(self):
        """load_full_schema returns the merged record build tools expect."""
        fdir = next(f for f in FORMS if (f / "schema.audit.json").exists())
        full = load_full_schema(fdir)
        audited = [f for f in full["fields"]
                   if set(f) & set(AUDIT_FIELD_KEYS)]
        self.assertTrue(audited, f"{fdir.name}: merge restored no research keys")


if __name__ == "__main__":
    unittest.main()
