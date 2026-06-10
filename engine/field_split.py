#!/usr/bin/env python3
"""Shared-AcroForm-field split — shim over the shared ``maine-forms-engine``.

The implementation lives in ``maine_forms_engine.fill.field_split`` (this repo
was the extraction donor); this module keeps the repo's ``engine.field_split``
API stable and re-anchors the default forms tree to THIS repo's layout. See
the package docstring for the fan-out problem (one field, semantically
different boxes — e.g. OTH-029 ``2_5``) this solves.
"""
import pathlib

from maine_forms_engine.fill.field_split import (  # noqa: F401
    specs_for as _pkg_specs_for,
    split,
    split_to_copy as _pkg_split_to_copy,
)

OSS_ROOT = pathlib.Path(__file__).resolve().parent.parent


def specs_for(form_id: str, forms_root: pathlib.Path | None = None) -> list[dict]:
    return _pkg_specs_for(form_id, forms_root or OSS_ROOT / "forms")


def split_to_copy(src_pdf: pathlib.Path, dst_pdf: pathlib.Path,
                  form_id: str, forms_root: pathlib.Path | None = None) -> int:
    return _pkg_split_to_copy(src_pdf, dst_pdf, form_id,
                              forms_root or OSS_ROOT / "forms")
