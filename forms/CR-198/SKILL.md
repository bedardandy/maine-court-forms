# CR-198 — ☐ Unified Criminal Docket

**Form Number:** CR-198, Rev. Unknown
**Pages:** 1
**Fillable Fields:** 23
**Category:** Criminal
**Court:** Unified Criminal Docket / Superior Court / District Court

## Purpose

Form used in criminal proceedings in Maine court.

## Governing Law

- **15 M.R.S. / 17-A M.R.S.** — Primary statutory authority

## Field Mappings

| Field Name | Type | Page | Notes |
|-----------|------|------|-------|
| `UNIFIED CRIMINAL DOCKET` | CheckBox | 1 | Court docket number |
| `SUPERIOR COURT` | CheckBox | 1 | Check if applicable |
| `DISTRICT COURT` | CheckBox | 1 | Check if applicable |
| `county` | Text | 1 | County name |
| `location` | Text | 1 | Court location |
| `docket no` | Text | 1 | Court docket number |
| `Defendant` | Text | 1 |  |
| `name` | Text | 1 |  |
| `DOB` | Text | 1 | MM/DD/YYYY format |
| `# hrs` | Text | 1 |  |
| `completed by date` | Text | 1 | MM/DD/YYYY format |
| `Organization Name Address  Telephone 1` | Text | 1 | Phone number |
| `supervisor name/tel` | Text | 1 |  |
| `days/hours` | Text | 1 |  |
| `days/hours` | Text | 1 |  |
| `days/hours` | Text | 1 |  |
| `HSat` | CheckBox | 1 | Check if applicable |
| `Sat` | CheckBox | 1 | Check if applicable |
| `Unsat` | CheckBox | 1 | Check if applicable |
| `Comments` | Text | 1 |  |
| `comments` | Text | 1 |  |
| `Date` | Text | 1 | MM/DD/YYYY format |
| `Printed Name` | Text | 1 |  |

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
- **CR-011** — Form CR-011
- **CR-022** — Form CR-022
- **CR-030** — Form CR-030
- **CR-032** — Motion and Affidavit for Assignment of Counsel
- **CR-073** — Form CR-073

> **Note:** a dedicated fill recipe exists for this form in `engine/recipes/`. The recipe is the authoritative field mapping; this doc is the human-readable companion.
