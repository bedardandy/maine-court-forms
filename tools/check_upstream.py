#!/usr/bin/env python3
"""Detect when the Judicial Branch has revised a blank form out from under us.

Shim over the shared ``maine-forms-engine``
(``maine_forms_engine.drift.check_upstream``; this repo was the extraction
donor); the CLI is unchanged, with this repo's ``catalog/pdf_manifest.json``
as the default manifest. The portal's DownloadForm endpoint serves the
*current* revision at a stable URL — so when a form is updated, the URL is
unchanged but the bytes (and often the widget layout) are not, and a fill
built on the old mapping can land values in the wrong place. Read-only by
default; exit code is non-zero if any form is CHANGED or GONE, so it gates a
pipeline.

Usage:
    python3 tools/check_upstream.py                      # check every form
    python3 tools/check_upstream.py --forms AD-001,CV-FM-288
    python3 tools/check_upstream.py --json               # machine-readable report
    python3 tools/check_upstream.py --update-manifest    # after re-mapping: adopt new hashes
"""
import pathlib
import sys

from maine_forms_engine.drift import check_upstream as _cu

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from tools.fetch_pdfs import _download  # noqa: E402,F401 — kept patchable for tests

ROOT = pathlib.Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "catalog" / "pdf_manifest.json"


def check_one(fid: str, entry: dict, timeout: int, retries: int) -> dict:
    """Probe one form's official URL and classify it against the manifest."""
    return _cu.check_one(fid, entry, timeout, retries,
                         downloader=lambda u, t, r: _download(u, t, r))


def main() -> int:
    return _cu.main(default_manifest=MANIFEST,
                    downloader=lambda u, t, r: _download(u, t, r))


if __name__ == "__main__":
    sys.exit(main())
