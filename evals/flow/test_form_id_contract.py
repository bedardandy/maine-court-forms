"""EVAL — Assumption: form_id is a well-formed, trusted-path identifier.

Every entrypoint (MCP, CLI) turns ``form_id`` into a filesystem path
(``forms/<ID>/...``). The catalog convention is the strict pattern
``^[A-Z]+(?:-[A-Z0-9]+)+$``, but (per the audit) nothing enforces it. This
eval locks the contract from the data side: every id that ships in the
catalog / workflows / mapping files matches the pattern, and routing only
ever emits ids that match.

It also exercises the pattern as a would-be validator against known
path-traversal payloads, so the security contract is testable even before a
``validate_form_id`` helper lands (audit finding #1).
"""
from __future__ import annotations

import json
import re
import unittest

from evals.common import FORM_ID_RE, REPO, all_mappings

_RE = re.compile(FORM_ID_RE)

TRAVERSAL = [
    "../../etc/passwd", "..", "forms/../x", "CV-007/../../x",
    "cv-007", "CV_007", "CV007", "", "CV-007\n", " CV-007", "A" * 100,
]


class TestFormIdContract(unittest.TestCase):
    def test_catalog_ids_match_pattern(self):
        bad = [fid for fid in all_mappings() if not _RE.fullmatch(fid)]
        self.assertEqual(bad, [], f"mapping ids violate pattern: {bad}")

    def test_forms_index_ids_match_pattern(self):
        idx = json.loads(
            (REPO / "catalog" / "forms_index.json").read_text())
        forms = idx.get("forms", idx) if isinstance(idx, dict) else idx
        ids = [f.get("form") or f.get("id") or f.get("form_id")
               for f in forms] if isinstance(forms, list) \
            else list(forms.keys())
        bad = [i for i in ids if i and not _RE.fullmatch(i)]
        self.assertEqual(bad, [], f"forms_index ids violate pattern: {bad}")

    def test_workflow_member_ids_match_pattern(self):
        wf = json.loads((REPO / "catalog" / "workflows.json").read_text())
        flows = wf.get("workflows", wf) if isinstance(wf, dict) else wf
        members = []
        for f in (flows.values() if isinstance(flows, dict) else flows):
            if not isinstance(f, dict):
                continue
            # workflows.json carries members under steps[].form; tolerate a
            # legacy top-level `forms` list too.
            members.extend(s["form"] for s in (f.get("steps") or [])
                           if isinstance(s, dict) and s.get("form"))
            members.extend(f.get("forms") or [])
        self.assertTrue(members, "no workflow member form ids found to check")
        bad = [m for m in members if not _RE.fullmatch(m)]
        self.assertEqual(bad, [], f"workflow members violate pattern: {bad}")

    def test_pattern_rejects_traversal_payloads(self):
        # fullmatch (not match+$) so a trailing newline can't sneak through.
        leaked = [p for p in TRAVERSAL if _RE.fullmatch(p)]
        self.assertEqual(leaked, [],
                         f"pattern accepted unsafe form_id(s): {leaked}")

    def test_routing_emits_only_valid_ids(self):
        from tools.find_forms import find_forms
        res = find_forms("divorce with children and child support")
        ids = [f["form"] for f in res.get("forms", [])]
        for wf in res.get("workflows", []):
            ids.extend(wf.get("forms", []))
        bad = [i for i in ids if not _RE.fullmatch(i)]
        self.assertEqual(bad, [], f"router emitted invalid ids: {bad}")


if __name__ == "__main__":
    unittest.main()
