<!-- Reused from prior skills stash; verify against schema.json. -->
# CR-011 — ☐ Unified Criminal Docket

**Form Number:** CR-011, Rev. 07/15
**Pages:** 1
**Fillable Fields:** 12
**Category:** Criminal
**Court:** Unified Criminal Docket / Superior Court / District Court

## Purpose

Form used in criminal proceedings in Maine court.

## Governing Law

- **17-A M.R.S. § 1176**

## Field Mappings

| Field Name | Type | Page | Notes |
|-----------|------|------|-------|
| `County` | Text | 1 | County name |
| `UNIFIED CRIMINAL DOCKET` | CheckBox | 1 | Court docket number |
| `SUPERIOR COURT` | CheckBox | 1 | Check if applicable |
| `DISTRICT COURT` | CheckBox | 1 | Check if applicable |
| `Location` | Text | 1 | Court location |
| `Docket No` | Text | 1 | Court docket number |
| `Bail ID Number` | Text | 1 |  |
| `Defendant` | Text | 1 |  |
| `Names DOBs and addresses of victims 1` | Text | 1 | Mailing/street address |
| `Names DOBs and addresses of victims 2` | Text | 1 | Mailing/street address |
| `Names DOBs and addresses of victims 3` | Text | 1 | Mailing/street address |
| `Date` | Text | 1 | MM/DD/YYYY format |

## AI Hints

- **Constitutional Rights**: Ensure defendant's rights are preserved (right to counsel, etc.).
- **Court Selection**: Criminal cases filed in Unified Criminal Docket (UCD) in most counties.
- **Bail/Bond**: Related bail forms may be needed.
- **Docket Number**: Leave blank for new filings; clerk assigns. Enter if responding to existing case.

## Validation Checklist

- [ ] All required party names are filled in
- [ ] Court location/county is correct for venue
- [ ] Docket number included (if existing case)
- [ ] All dates are in correct format (MM/DD/YYYY)
- [ ] Contact information is complete
- [ ] Defendant rights acknowledged

## Related Forms

- **CR-003** — TERMINATION OF SURETY AGREEMENT
- **CR-004** — Bail Lien
- **CR-006** — ORDER OF COURT
- **CR-009** — PETITION FOR DE NOVO
- **CR-010** — MOTION TO AMEND BAIL
- **CR-022** — Form CR-022
- **CR-030** — Form CR-030
- **CR-032** — Motion and Affidavit for Assignment of Counsel
- **CR-073** — Form CR-073
- **CR-076** — Affidavit and Request for Search Warrant

> **Note:** a dedicated fill recipe exists for this form in `engine/recipes/`. The recipe is the authoritative field mapping; this doc is the human-readable companion.
