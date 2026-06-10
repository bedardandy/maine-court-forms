#!/usr/bin/env python3
"""Fill a form directly from its ``mapping.json`` + a canonical fact object.

Shim over the shared ``maine-forms-engine``
(``maine_forms_engine.fill.fill_via_mapping``) — this repo was the extraction
donor, so the package defaults ARE this repo's policy and the shim only
re-anchors the default forms tree. The CLI and the ``resolve_mapping`` /
``fill_via_mapping`` APIs are unchanged.

This is the **mapping.json-driven** fill path, and it is deliberately separate
from ``engine/fill.py``:

- ``engine/fill.py`` runs the generic ``map_form`` + form recipes from an
  engine-shape case. It never reads ``mapping.json``.
- this module resolves each canonical fact-key in a form's ``mapping.json``
  against a canonical fact object and writes the result to the mapped widget.

So this is what an external adapter (docassemble, LangChain, ...) conceptually
does, and it's how you *verify* a `mapping.json`: fill from it, then check the
output. Recipe-tier forms have a pointer-only ``mapping.json`` (empty ``map``)
and are skipped — use ``engine/fill.py`` for those. The fill-time blank guard
reads ``MCF_VERIFY_BLANK`` (warn|strict|off), and results carry the coverage
ratio + ``blank_verify`` dict; a zero-resolved fill fails loudly.
"""
from __future__ import annotations

import argparse
import json
import pathlib

from maine_forms_engine.fill.fill_via_mapping import (  # noqa: F401
    _resolve_key,
    _split_name,
    _width_fit,
    fill_via_mapping as _pkg_fill_via_mapping,
    resolve_mapping as _pkg_resolve_mapping,
)

OSS_ROOT = pathlib.Path(__file__).resolve().parent.parent


def resolve_mapping(form_id: str, facts: dict,
                    forms_root: pathlib.Path = OSS_ROOT / "forms") -> dict:
    """Resolve a form's mapping.json against a canonical fact object.

    Pure (no PDF needed): returns coverage stats + the field_id->value map.
    """
    return _pkg_resolve_mapping(form_id, facts, forms_root)


def fill_via_mapping(form_id: str, facts: dict, out_dir: pathlib.Path,
                     forms_root: pathlib.Path = OSS_ROOT / "forms") -> dict:
    """Resolve mapping.json and write a filled PDF."""
    return _pkg_fill_via_mapping(form_id, facts, out_dir, forms_root)


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--form", required=True)
    ap.add_argument("--case", type=pathlib.Path,
                    help="canonical fact object JSON "
                         "(default: the form's examples/sample_case.json)")
    ap.add_argument("--out", type=pathlib.Path,
                    default=pathlib.Path("/tmp/mapping_fill"))
    args = ap.parse_args()
    fdir = OSS_ROOT / "forms" / args.form
    case_path = args.case or (fdir / "examples" / "sample_case.json")
    facts = json.loads(case_path.read_text())
    res = fill_via_mapping(args.form, facts, args.out)
    print(json.dumps(res, indent=2))
    return 0 if res.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
