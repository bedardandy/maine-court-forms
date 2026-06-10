#!/usr/bin/env python3
"""Split each form's schema.json into a lean runtime schema + a research file.

Historically ``forms/<ID>/schema.json`` carried both the AcroForm field
inventory (what the fill engine, MCP server, and agents read) and the
build-time research metadata produced by the mapping/eval toolchain
(``risk_score``/``risk_tier``/``risk_breakdown``/``eval_evidence``/
``hand_review``/``fill_strategy``/...). The research keys were ~71% of the
bytes and were consumed only by build tools, so agents following "verify
against schema.json" paid a ~5x token tax.

This tool splits each schema in place:

  schema.json        lean, agent/runtime-facing: field inventory only
                     (field_id, widget_id, label, type, data_type, page,
                     rect, category, subcategory, party) + form-level counts.
  schema.audit.json  everything else (research/build metadata), keyed by
                     field index + field_id, parallel to schema.json fields.

``merge_audit(lean, audit)`` reconstructs the original shape for the build
tools that still want the full record. The split is verified lossless before
anything is written. Idempotent: re-running on an already-split schema is a
no-op.

Usage:
    python3 tools/split_schema.py                # all forms, split in place
    python3 tools/split_schema.py --forms PA-001,AD-001
    python3 tools/split_schema.py --check        # verify only, write nothing
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

OSS_ROOT = pathlib.Path(__file__).resolve().parent.parent

# Field keys the runtime fill path / MCP server / agents read. Everything
# else found on a field record moves to schema.audit.json.
LEAN_FIELD_KEYS = (
    "field_id", "widget_id", "label", "type", "data_type", "page", "rect",
    "category", "subcategory", "party",
)

# Known research/build-time field keys (documented set; any *unknown* key is
# conservatively kept in the lean schema rather than hidden in the audit file).
AUDIT_FIELD_KEYS = (
    "data_constraints", "writable_when", "required_when", "choice_group",
    "choice_value", "formula", "depends_on", "validators", "fill_strategy",
    "risk_score", "risk_tier", "risk_breakdown", "hand_review",
    "eval_evidence",
)

# Top-level keys that move to schema.audit.json (research aggregates).
AUDIT_TOP_KEYS = ("by_risk_tier", "by_data_type")

AUDIT_DOC = (
    "Build-time research metadata split out of schema.json by "
    "tools/split_schema.py. Runtime fill / MCP / agents never need this "
    "file; it feeds the mapping/eval build tools. fields[] is parallel to "
    "schema.json fields[] (same order; i = index)."
)


def split_schema(schema: dict) -> tuple[dict, dict | None]:
    """Split a full schema dict -> (lean, audit). audit is None if there is
    nothing to move (already-lean schema)."""
    lean: dict = {}
    audit: dict = {"_doc": AUDIT_DOC}
    moved = False
    for k, v in schema.items():
        if k in AUDIT_TOP_KEYS:
            audit[k] = v
            moved = True
        elif k != "fields":
            lean[k] = v
    for k in ("form_id", "schema_version"):
        if k in schema:
            audit.setdefault(k, schema[k])

    lean_fields, audit_fields = [], []
    for i, f in enumerate(schema.get("fields", [])):
        lf = {k: v for k, v in f.items() if k not in AUDIT_FIELD_KEYS}
        af = {k: v for k, v in f.items() if k in AUDIT_FIELD_KEYS}
        lean_fields.append(lf)
        if af:
            moved = True
            entry = {"i": i, "field_id": f.get("field_id")}
            entry.update(af)
            audit_fields.append(entry)
    lean["fields"] = lean_fields
    audit["fields"] = audit_fields
    return lean, (audit if moved else None)


def merge_audit(lean: dict, audit: dict | None) -> dict:
    """Reconstruct the pre-split schema shape from (lean, audit)."""
    if not audit:
        return lean
    full = {k: v for k, v in lean.items() if k != "fields"}
    for k in AUDIT_TOP_KEYS:
        if k in audit:
            full[k] = audit[k]
    fields = [dict(f) for f in lean.get("fields", [])]
    for entry in audit.get("fields", []):
        i = entry.get("i")
        if not isinstance(i, int) or not 0 <= i < len(fields):
            continue
        for k, v in entry.items():
            if k in AUDIT_FIELD_KEYS:
                fields[i][k] = v
    full["fields"] = fields
    return full


def load_full_schema(fdir: pathlib.Path) -> dict:
    """Load a form's schema with research metadata re-merged if present.

    Build tools that want the full pre-split record should use this instead
    of reading schema.json directly.
    """
    schema = json.loads((fdir / "schema.json").read_text())
    ap = fdir / "schema.audit.json"
    if ap.exists():
        schema = merge_audit(schema, json.loads(ap.read_text()))
    return schema


def _canon(obj) -> str:
    return json.dumps(obj, sort_keys=True)


def split_one(fdir: pathlib.Path, check_only: bool = False) -> str:
    sp = fdir / "schema.json"
    if not sp.exists():
        return "no-schema"
    original = json.loads(sp.read_text())
    lean, audit = split_schema(original)
    if audit is None:
        return "already-lean"
    # lossless check: lean + audit must reconstruct the original exactly
    if _canon(merge_audit(lean, audit)) != _canon(original):
        return "LOSSY — refused"
    if check_only:
        return "would-split"
    sp.write_text(json.dumps(lean, indent=2) + "\n")
    (fdir / "schema.audit.json").write_text(
        json.dumps(audit, indent=2) + "\n")
    before = len(_canon(original))
    after = len(_canon(lean))
    return f"split ({before // 1024}KB -> {after // 1024}KB lean)"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--forms", default="",
                    help="comma list of form ids; omit for all")
    ap.add_argument("--check", action="store_true",
                    help="verify the split is lossless; write nothing")
    args = ap.parse_args()
    if args.forms:
        dirs = [OSS_ROOT / "forms" / f.strip()
                for f in args.forms.split(",") if f.strip()]
    else:
        dirs = sorted(p for p in (OSS_ROOT / "forms").iterdir() if p.is_dir())
    counts: dict[str, int] = {}
    bad = 0
    for fdir in dirs:
        msg = split_one(fdir, check_only=args.check)
        tag = msg.split(" ")[0]
        counts[tag] = counts.get(tag, 0) + 1
        if "LOSSY" in msg or msg == "no-schema":
            bad += 1
            print(f"  {fdir.name}: {msg}")
    print(json.dumps(counts))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
