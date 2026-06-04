# Licensing

This repository mixes material with different appropriate licenses. The
blank-PDF question (the one blocker for publishing) is **resolved**; the
code/data license is still the maintainer's pick.

## 1. The blank PDF forms — RESOLVED: not redistributed

The blank forms are official **Maine Judicial Branch** documents and are
**not** this project's to relicense. Rather than redistribute them and depend
on permission, **this repo does not ship the PDFs at all.** They are excluded
from git (`.gitignore`: `forms/**/*.pdf`); each form instead carries its
official `source_url` (in `form.yaml`) plus a size + SHA-256 in
`catalog/pdf_manifest.json`.

Fetch the blanks on demand:

```bash
python3 tools/fetch_pdfs.py            # all forms (verifies each against the manifest)
python3 tools/fetch_pdfs.py --forms AD-001,AD-022
```

The download is deterministic (the portal's parametrized `DownloadForm`
endpoint) and verified byte-for-byte against the manifest SHA-256, so a fetched
blank is provably the same document the library was built against — with no
redistribution. This sidesteps the redistribution-permission question entirely.
A `NOTICE` attributing the forms to the Maine Judicial Branch is still
appropriate for any built artifacts that embed them.

## 2. Code + form metadata/schemas/skills/mappings — RESOLVED: Apache-2.0

The repository's own work — code (`engine/`, `tools/`) and the structured form
artifacts (`forms/*/` non-PDF, `catalog/`, `docs/`) — is licensed **Apache-2.0**
(see the `LICENSE` file). Permissive, with an explicit patent grant, so firms,
clinics, courts, and commercial tools can reuse it.

## Structure

```
LICENSE          -> Apache-2.0 (this project's code + metadata)
(blank PDFs are not in the repo — fetched from the MJB portal; see §1)
NOTICE           -> Maine Judicial Branch attribution (for built artifacts that embed the forms)
```

The repository's own code and metadata are Apache-2.0 (`LICENSE`). The official
blank PDFs remain Maine Judicial Branch documents and are not redistributed here
(fetched from the portal — see §1).
