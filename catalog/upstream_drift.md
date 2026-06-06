# Upstream drift worklist

Forms whose official PDF on `courts.maine.gov` no longer matches the revision
the mapping was built against, found by `tools/check_upstream.py`. The manifest
is **left unchanged on purpose** — adopting the new bytes without re-mapping
would make the fill-time guard falsely report "verified." Each form here fills
with a `BlankRevisionWarning` until it is re-mapped and its manifest hash
refreshed.

Reproduce:

```bash
python3 tools/check_upstream.py            # full probe (CHANGED / GONE)
```

Last full probe: 2026-06-06 — 350 checked, 328 ok, 14 CHANGED, 8 GONE.

## Resolution (2026-06-06)

All 14 CHANGED forms reconciled; the 8 GONE (MRS-*) removed. Re-probe of the 14
is now clean (`ok=14`).

- **Re-mapped from the current blank** (vision-grounded, `tools/remap_from_pdf.py`
  + Qwen-VL): CR-006, CR-009, CR-198, CR-228, CR-004, MJ-007. These carry
  `status: vision-mapped` — a **draft tier; review before production use**, not
  `verified`. They fix the broken state (were filling renamed/absent widgets).
  **CR-004 needs review:** it is a bail *surety* bond whose surety block does not
  fit the plaintiff/defendant/party canonical roles, so the VL mapped surety
  name/residence onto `parties.plaintiff.*` (e.g. `city_town_of_residence` →
  `last_name`). Re-map with a surety-aware model/role before trusting it.
- **Patched** (label rename only): CR-234 (`Docket Number and Charge 1/2` →
  `Charges 1/2`). FM-043 needed no patch (re-probe showed 0 drift).
- **Hash refreshed only** (cosmetic re-save, mappings held): CR-153,
  CV-FM-PB-299, OTH-012, CR-010, CR-030, OTH-019.

Manifest hashes refreshed for all 14 via `check_upstream --update-manifest`.

## CHANGED — re-issued by the courts (14)

Impact below is from comparing each revised PDF's actual AcroForm widget names
against the widget names the mapping writes to (the `label` column in
`fields.csv`). "survived" = mapped widgets still present; "broken" = mapped
widgets no longer in the PDF.

| Form | tier | mapped | broken | action |
|---|---|---|---|---|
| CR-006 | verified | 14 | 11 | **re-map** (re-authored field names) |
| CR-009 | verified | 28 | 25 | **re-map** |
| CR-198 | recipe | 21 | 19 | **re-map** |
| CR-228 | verified | 56 | 24 | **re-map** (≈half) |
| CR-004 | recipe | 24 | 7 | **re-map** |
| MJ-007 | recipe | 29 | 6 | **re-map** |
| CR-234 | verified | 31 | 2 | patch 2 fields (`Docket Number and Charge 1/2`) |
| FM-043 | verified | 679 | 5 | patch 5 fields (`of Ownership1..5`) |
| CR-153 | verified | 14 | 0 | refresh hash only (cosmetic re-save) |
| CV-FM-PB-299 | verified | 55 | 0 | refresh hash only |
| OTH-012 | recipe | 19 | 0 | refresh hash only |
| CR-010 | no-mappable-fields | 0 | 0 | refresh hash only |
| CR-030 | no-mappable-fields | 0 | 0 | refresh hash only |
| OTH-019 | no-mappable-fields | 0 | 0 | refresh hash only |

Refresh a form's hash **after** its mapping is re-verified:

```bash
python3 tools/fetch_pdfs.py --forms <ID> --force        # pull the new revision
python3 tools/check_upstream.py --forms <ID> --update-manifest
```

## GONE — HTTP 500 on the court portal (8)

All eight were `MRS-*` Maine Revenue Service **tax** forms (estate, withholding,
income), a different agency than the Judicial Branch, and the court portal's
`DownloadForm` endpoint no longer serves them. **They have been removed from this
library** (folders, manifest, and vision_audit) — this library is Judicial Branch
forms only. The seven still published by Maine Revenue Services moved to the
`transactional-tax-forms` library (fetched from maine.gov); MRS-1099ME was
discontinued upstream after TY2023 and dropped.

Removed: `MRS-1041ME, MRS-1099ME, MRS-1120ME, MRS-700SOV, MRS-706ME, MRS-900ME, MRS-941ME, MRS-W4ME`
