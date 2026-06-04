#!/usr/bin/env python3
"""Split a shared AcroForm field into one field per appearance (the Phase-2 fix).

Some court source PDFs reuse ONE field across semantically different boxes (the
shared_field_report worklist) — e.g. OTH-029 field `2_5` is a child-DOB table
cell on pg4 AND the confidential-address "Mailing address" line on pg12. Because
they are kid widgets of one field, they always hold the same value and a screen
reader can name the field only once. This detaches a named appearance into its
OWN terminal field so it can carry its own value and its own `/TU`.

Driven by a per-form spec at ``forms/<ID>/field_splits.json``:

    {"splits": [
      {"field": "2_5", "page": 12, "new_name": "confidential_mailing_address",
       "clear": true}
    ]}

``clear`` (default true) blanks the detached widget's value — showing a blank is
correct when, as here, no distinct fact feeds that box (better blank than the
other appearance's wrong value). A future ``key`` could re-fill it instead.

Runs on a working copy (pikepdf); the repo blank is never modified. Used as a
pre-remediate step by make_accessible, or standalone:

    python3 tools/accessibility/split_shared_fields.py in.pdf out.pdf --form OTH-029
"""
from __future__ import annotations

import argparse
import pathlib
import sys

import pikepdf

# Shared core lives in the engine layer (engine/field_split.py) so the FILL
# path and this ACCESSIBILITY path apply identical splits. tools/ -> engine/
# is the allowed dependency direction.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent.parent))
from engine.field_split import split, specs_for  # noqa: E402,F401


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pdf")
    ap.add_argument("out")
    ap.add_argument("--form", required=True)
    a = ap.parse_args()
    if pathlib.Path(a.out).resolve() == pathlib.Path(a.pdf).resolve():
        print("refusing to overwrite the original", file=sys.stderr)
        return 2
    specs = specs_for(a.form)
    if not specs:
        print(f"no forms/{a.form}/field_splits.json — nothing to split")
    pdf = pikepdf.open(a.pdf)
    n = split(pdf, specs)
    pdf.save(a.out)
    print(f"split {n} shared field(s) -> {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
