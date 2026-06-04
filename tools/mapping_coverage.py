#!/usr/bin/env python3
"""Report mapping.json coverage across the form library.

For each schema-only form, resolves its ``mapping.json`` against a canonical
fact object (each form's ``examples/sample_case.json`` by default) and reports
how complete the mapping is (mapped fields / total fields). This is triage for
the per-form verification work (KICKOFF task 4): the lowest-coverage forms are
where a human/agent has the most to add. Needs no PDFs.

    python3 tools/mapping_coverage.py            # summary
    python3 tools/mapping_coverage.py --list     # per-form table, worst first
"""
from __future__ import annotations

import argparse
import json
import pathlib
import statistics
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from engine.fill_via_mapping import resolve_mapping  # noqa: E402

OSS_ROOT = pathlib.Path(__file__).resolve().parent.parent


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--list", action="store_true",
                    help="print a per-form table (lowest coverage first)")
    args = ap.parse_args()

    rows, recipe = [], 0
    for fdir in sorted((OSS_ROOT / "forms").iterdir()):
        if not fdir.is_dir():
            continue
        facts = json.loads((fdir / "examples" / "sample_case.json").read_text())
        r = resolve_mapping(fdir.name, facts)
        if r.get("skipped"):
            recipe += 1
            continue
        tot = r["total_fields"]
        cov = (r["mapped_keys"] / tot) if tot else None  # None = flat PDF
        rows.append((fdir.name, tot, r["mapped_keys"], r["resolved"], cov))

    fillable = [r for r in rows if r[4] is not None]
    covs = [r[4] for r in fillable]
    print(f"schema-only forms: {len(rows)} ({len(rows) - len(fillable)} flat/"
          f"0-field) | recipe forms skipped: {recipe}")
    print(f"mapping completeness (fillable forms): mean {statistics.mean(covs):.0%}"
          f" | median {statistics.median(covs):.0%}")
    real_gaps = [r for r in fillable if r[2] == 0]
    print(f"forms with fields but 0 mapped (real gaps): {len(real_gaps)}"
          + (f" -> {', '.join(r[0] for r in real_gaps)}" if real_gaps else ""))

    if args.list:
        print(f"\n{'form':14} {'fields':>7} {'mapped':>7} {'cov':>6}")
        for fid, tot, mk, _res, cov in sorted(
                fillable, key=lambda r: (r[4], -r[1])):
            print(f"{fid:14} {tot:7d} {mk:7d} {cov:6.0%}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
