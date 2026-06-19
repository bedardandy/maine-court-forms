"""Generate / refresh the completed-form golden snapshots.

For every fillable form, run the PDF-free fill (recipe or mapping) over its
sample case and write the resolved ``field_id -> value`` map to
``evals/fill/golden/<ID>.kv.json``. These goldens are committed and
human-reviewable; ``test_fill_golden.py`` diffs live fills against them so any
content drift is caught at corpus scale.

Today's-date fields are normalized to a ``<TODAY:...>`` token so goldens stay
stable across days (see ``evals/common.normalize``).

Usage:
    python3 -m evals.fill.gen_golden --all
    python3 -m evals.fill.gen_golden --form CV-007
"""
from __future__ import annotations

import argparse
import json
import pathlib

from evals.common import fillable_forms, filled_kv, normalize

GOLDEN = pathlib.Path(__file__).resolve().parent / "golden"


def write_one(form_id: str) -> int:
    kv = normalize(filled_kv(form_id))
    GOLDEN.mkdir(exist_ok=True)
    out = GOLDEN / f"{form_id}.kv.json"
    out.write_text(json.dumps(kv, indent=2, sort_keys=True, ensure_ascii=False)
                   + "\n")
    return len(kv)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--all", action="store_true")
    g.add_argument("--form")
    args = ap.parse_args()

    forms = fillable_forms() if args.all else [args.form]
    total = 0
    failed = []
    for fid in forms:
        try:
            n = write_one(fid)
            total += 1
            if args.form:
                print(f"{fid}: {n} fields -> {GOLDEN / (fid + '.kv.json')}")
        except Exception as e:  # noqa: BLE001
            failed.append((fid, str(e)))
    if args.all:
        print(f"wrote {total} goldens to {GOLDEN}")
        if failed:
            print(f"FAILED {len(failed)}: {failed[:10]}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
