#!/usr/bin/env python3
"""Minimal fill entrypoint for the form-by-form library.

Fills a single form's blank PDF from a case object, resolving the form's
``schema.json`` and blank ``<FORM_ID>.pdf`` from ``forms/<FORM_ID>/`` in this
repo and reusing the reference engine's ``fill_one`` orchestration (generic
field map + recipe-3 inference + notary block + width-fit).

    python3 -m engine.fill --form AD-022 \
        --case engine/examples/case.fami.json --out /tmp/oss_fill

Accepts either case shape. A canonical fact object
(``{matter, parties, party, facts}`` — e.g. a form's ``examples/sample_case.json``)
is auto-detected and translated to the engine case shape via
``engine.canonical.to_engine_case``; an engine-shape case
(``court``/``docket_no``/``parties``/...) passes through unchanged.
"""
from __future__ import annotations

import argparse
import json
import pathlib

from .canonical import is_canonical, to_engine_case
from .fill_and_audit import fill_one

OSS_ROOT = pathlib.Path(__file__).resolve().parent.parent


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--form", required=True, help="form id, e.g. AD-022")
    ap.add_argument("--case", required=True, type=pathlib.Path,
                    help="path to an engine-shape case JSON")
    ap.add_argument("--out", type=pathlib.Path,
                    default=pathlib.Path("/tmp/oss_fill"),
                    help="output dir for the filled PDF + kv artifact")
    args = ap.parse_args()

    fdir = OSS_ROOT / "forms" / args.form
    if not fdir.exists():
        print(f"no such form folder: {fdir}")
        return 2
    case = json.loads(args.case.read_text())
    # Accept either shape: a canonical fact object (e.g. examples/sample_case.json)
    # is translated to the engine case shape; an engine case passes through.
    if is_canonical(case):
        print(f"  (translating canonical fact object -> engine case)")
        case = to_engine_case(case)
    res = fill_one(args.form, case, args.out,
                   schema_path=fdir / "schema.json",
                   pdf_path=fdir / f"{args.form}.pdf")
    print(json.dumps(res, indent=2))
    return 0 if res.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
