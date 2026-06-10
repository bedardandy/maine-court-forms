"""Blank-revision pinning — shim over the shared ``maine-forms-engine``.

The implementation lives in ``maine_forms_engine.fill.verify`` (this repo was
the extraction donor); this module keeps the repo's ``engine.verify`` API
stable and re-anchors the default manifest / forms tree to THIS repo's layout
(the package defaults are cwd-relative).
"""
from pathlib import Path

from maine_forms_engine.fill.verify import (  # noqa: F401
    BlankRevisionError,
    BlankRevisionWarning,
    guard_blank as _pkg_guard_blank,
    load_manifest as _pkg_load_manifest,
    manifest_entry as _pkg_manifest_entry,
    sha256_bytes,
    verify_blank as _pkg_verify_blank,
)

_ROOT = Path(__file__).resolve().parent.parent
_MANIFEST = _ROOT / "catalog" / "pdf_manifest.json"


def load_manifest(manifest_path=None) -> dict:
    return _pkg_load_manifest(manifest_path or _MANIFEST)


def manifest_entry(form_id: str, manifest=None):
    """Return the manifest record for ``form_id`` (or ``None``)."""
    return _pkg_manifest_entry(
        form_id, manifest if manifest is not None else load_manifest())


def verify_blank(form_id, forms_root=None, manifest=None):
    return _pkg_verify_blank(
        form_id, forms_root or _ROOT / "forms",
        manifest if manifest is not None else load_manifest())


def guard_blank(form_id, forms_root=None, mode="warn", manifest=None) -> bool:
    return _pkg_guard_blank(
        form_id, forms_root or _ROOT / "forms", mode=mode,
        manifest=manifest if manifest is not None else load_manifest())
