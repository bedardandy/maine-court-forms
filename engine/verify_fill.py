#!/usr/bin/env python3
"""Deterministic post-fill verification — shim over the shared
``maine-forms-engine`` (``maine_forms_engine.fill.verify_fill``; this repo was
the extraction donor).

Reopens a filled PDF, reads every widget value, and diffs them against the
intended ``field_id -> value`` dict. No model involved — this is the cheap,
machine-checkable half of verification (the vision audit judges *placement
against the printed label*; this checks *presence and value*). Per-field
statuses: ``placed`` / ``differs`` / ``missing`` / ``no-widget`` (the last is
expected for multi-widget overflow groups — see the package docstring).

CLI:
    python3 -m engine.verify_fill --form AD-001 --pdf /tmp/out/AD-001.filled.pdf \
        --intended intended.json
"""
from __future__ import annotations

import argparse
import json
import pathlib

from maine_forms_engine.fill.verify_fill import (  # noqa: F401
    _fid_labels,
    _widget_values,
    verify_fill,
)

OSS_ROOT = pathlib.Path(__file__).resolve().parent.parent


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--form", help="form id (loads forms/<ID>/schema.json)")
    ap.add_argument("--pdf", type=pathlib.Path, required=True,
                    help="the filled PDF to verify")
    ap.add_argument("--intended", type=pathlib.Path, required=True,
                    help="JSON file: {field_id: intended value, ...} "
                         "(e.g. the kv from <ID>.kv.json, or "
                         "resolve_mapping's fid_value)")
    args = ap.parse_args()
    intended = json.loads(args.intended.read_text())
    if isinstance(intended, dict) and "kv" in intended:
        intended = intended["kv"]
    schema = None
    if args.form:
        sp = OSS_ROOT / "forms" / args.form / "schema.json"
        if sp.exists():
            schema = json.loads(sp.read_text())
    res = verify_fill(args.pdf, intended, schema)
    print(json.dumps(res, indent=2))
    return 0 if res["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
