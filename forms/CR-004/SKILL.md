# CR-004 — Bail Lien

**Form Number:** CR-004, Rev. 03/25
**Pages:** 1
**Fillable Fields:** 24
**Category:** Criminal
**Court:** Unified Criminal Docket / Superior Court / District Court

## Purpose

Form used in criminal proceedings in Maine court.

## Governing Law

- **15 M.R.S. § 1071**

## Field Mappings

| Field Name | Type | Page | Notes |
|-----------|------|------|-------|
| `Superior Court` | CheckBox | 1 | Check if applicable |
| `District Court` | CheckBox | 1 | Check if applicable |
| `Unified Criminal Docket` | CheckBox | 1 | Court docket number |
| `County` | Text | 1 | County name |
| `Location Town` | Text | 1 | Court location |
| `Docket No` | Text | 1 | Court docket number |
| `I` | Text | 1 |  |
| `of` | Text | 1 |  |
| `County_2` | Text | 1 | County name |
| `Text2` | Text | 1 |  |
| `interest in real estate in the town of` | Text | 1 |  |
| `street` | Text | 1 |  |
| `County Maine and I grant to the State of Maine a lien on the real estate in the amount` | Text | 1 | County name |
| `of_2` | Text | 1 |  |
| `Dollars` | Text | 1 |  |
| `mmddyyyy` | Text | 1 |  |
| `given for the release of defendant` | Text | 1 |  |
| `who iswas being held in custody for the offense ofreason` | Text | 1 |  |
| `which bail is returnable to the Unified Criminal Court of` | Text | 1 |  |
| `undefined` | Text | 1 |  |
| `DivisionCounty in citytown` | Text | 1 | County name |
| `Date mmddyyyy` | Text | 1 | MM/DD/YYYY format |
| `2` | Text | 1 |  |
| `1_2` | Text | 1 |  |

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
- [ ] Defendant rights acknowledged

## Related Forms

- **CR-003** — TERMINATION OF SURETY AGREEMENT
- **CR-006** — ORDER OF COURT
- **CR-009** — PETITION FOR DE NOVO
- **CR-010** — MOTION TO AMEND BAIL
- **CR-011** — Form CR-011
- **CR-022** — Form CR-022
- **CR-030** — Form CR-030
- **CR-032** — Motion and Affidavit for Assignment of Counsel
- **CR-073** — Form CR-073
- **CR-076** — Affidavit and Request for Search Warrant

> **Note:** this form was re-mapped from the current blank after upstream drift; `mapping.json` (status `opus-adjudicated`) is the authoritative fill path. The old `engine/recipes/` module targeted the superseded revision — do not prefer it over the mapping.
