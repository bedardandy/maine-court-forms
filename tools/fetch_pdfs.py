#!/usr/bin/env python3
"""Fetch blank source PDFs from the official Maine Judicial Branch portal.

Shim over the shared ``maine-forms-engine`` (``maine_forms_engine.drift.
fetch_pdfs``; this repo was the extraction donor); the CLI is unchanged, with
this repo's manifest / forms tree as the defaults:

    # fetch everything (skips files already present and valid)
    python3 tools/fetch_pdfs.py

    # fetch a subset, re-downloading even if present
    python3 tools/fetch_pdfs.py --forms AD-001,CV-FM-288 --force

Each download is deterministic: the URL is the per-form entry in
``catalog/pdf_manifest.json``, and the bytes are checked against the recorded
SHA-256, so a fetched file is provably the same blank the mapping was built
against — without the repo ever shipping the PDF.
"""
from __future__ import annotations

import pathlib
import sys

from maine_forms_engine.drift import fetch_pdfs as _fp
from maine_forms_engine.drift.fetch_pdfs import _verify  # noqa: F401

ROOT = pathlib.Path(__file__).resolve().parent.parent
USER_AGENT = "maine-court-forms/fetch_pdfs (+https://courts.maine.gov)"
_fp.USER_AGENT = USER_AGENT  # downloads announce this repo, not the package


def _download(url: str, timeout: int, retries: int) -> bytes:
    return _fp._download(url, timeout, retries)


def main() -> int:
    return _fp.main(default_manifest=ROOT / "catalog" / "pdf_manifest.json",
                    default_forms_root=ROOT / "forms")


if __name__ == "__main__":
    sys.exit(main())
