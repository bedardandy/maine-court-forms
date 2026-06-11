#!/usr/bin/env python3
"""Re-verify each mapping.json against the pinned blank, then stamp it.

Thin shim over the shared engine's ``maine_forms_engine.verify_mapping``
(v0.4.0) — this repo speaks the module's default (donor) dialect exactly:
``catalog/pdf_manifest.json`` is ``{"forms": {<id>: {"sha256": ...}}}``,
blanks live at ``forms/<ID>/<ID>.pdf``, ``mapping.map`` keys are
``schema.json`` field_ids that resolve via their ``label`` to the live
AcroForm widget name, and ``field_splits.json`` new_names count as present.
So no format hooks are overridden; the shim only

1. anchors ``--forms-root`` / ``--manifest`` to this repo's tree (so the
   tool runs from anywhere), and
2. defaults ``--forms`` to mappings that actually carry a non-empty ``map``.
   Pointer-only mappings (the recipe tier and ``no-mappable-fields`` forms,
   131 today) have nothing to verify or stamp — ``engine/fill_via_mapping.py``
   already refuses them — and would otherwise drown the report / force a
   non-zero exit. Pass ``--forms`` explicitly to inspect one anyway.

``built_against_sha256`` is the staleness gate: a mapping may only carry it
after an honest re-verification against the very revision the manifest pins
(blank byte-identity + every mapped field_id resolving to a surviving
widget). ``--stamp`` writes it only for forms that fully verify; a failing
form stays unstamped and the tool exits non-zero, so it gates a pipeline.

Usage:
    python3 tools/verify_mapping_fields.py                   # verify all mapped
    python3 tools/verify_mapping_fields.py --forms MJ-007
    python3 tools/verify_mapping_fields.py --json            # machine report
    python3 tools/verify_mapping_fields.py --stamp           # verify + stamp
"""
import json
import pathlib
import sys

from maine_forms_engine.verify_mapping import main as _main, verify_form  # noqa: F401

ROOT = pathlib.Path(__file__).resolve().parent.parent
FORMS = ROOT / "forms"
MANIFEST = ROOT / "catalog" / "pdf_manifest.json"


def _mapped_form_ids() -> list:
    """Form ids whose mapping.json carries a non-empty ``map``."""
    out = []
    for p in sorted(FORMS.glob("*/mapping.json")):
        if json.loads(p.read_text()).get("map"):
            out.append(p.parent.name)
    return out


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--forms" not in argv and not any(a.startswith("--forms=")
                                         for a in argv):
        argv += ["--forms", ",".join(_mapped_form_ids())]
    return _main(argv, default_forms_root=FORMS, default_manifest=MANIFEST)


if __name__ == "__main__":
    sys.exit(main())
