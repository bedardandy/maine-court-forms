<!-- Reused from prior skills stash; verify against schema.json. -->
# FDP-010 — Joint Motion to Stay

**Form Number:** FDP-010, Rev. 06/13
**Pages:** 1
**Fillable Fields:** 14
**Category:** Foreclosure Diversion
**Court:** Superior Court / District Court

## Purpose

Form used in foreclosure diversion proceedings in Maine court.

## Governing Law

- **14 M.R.S. § 6321-A** — Primary statutory authority

## Field Mappings

| Field Name | Type | Page | Notes |
|-----------|------|------|-------|
| `Docket No` | Text | 1 | Court docket number |
| `ss` | Text | 1 |  |
| `Docket No_2` | Text | 1 | Court docket number |
| `undefined` | Text | 1 |  |
| `Plaintiff` | Text | 1 |  |
| `Defendant` | Text | 1 |  |
| `days up to 120 days` | Text | 1 |  |
| `Group1` | RadioButton | 1 |  |
| `Group1` | RadioButton | 1 |  |
| `Group1` | RadioButton | 1 |  |
| `Other` | Text | 1 |  |
| `Date` | Text | 1 | MM/DD/YYYY format |
| `Date_2` | Text | 1 | MM/DD/YYYY format |
| `Date_3` | Text | 1 | MM/DD/YYYY format |

## AI Hints

- **Mediation**: Maine requires foreclosure mediation for owner-occupied residential properties.
- **FDP Program**: Foreclosure Diversion Program forms must be filed timely.
- **Docket Number**: Leave blank for new filings; clerk assigns. Enter if responding to existing case.

## Validation Checklist

- [ ] All required party names are filled in
- [ ] Court location/county is correct for venue
- [ ] Docket number included (if existing case)
- [ ] All dates are in correct format (MM/DD/YYYY)

## Related Forms

- **FDP-002A** — DATE PROVIDED IN THE COURT’S SCHEDULING ORDER FOR INFORMATIONAL
- **FDP-002B** — Defendant’s Foreclosure Mediation Information
- **FDP-003** — MOTION TO WAIVE MEDIATION IN FORECLOSURE ACTION
- **FDP-004** — SUPERIOR COURT
- **FDP-006** — REQUEST TO INCLUDE IN FORECLOSURE MEDIATION
- **FDP-007** — SUPERIOR COURT

> **Note:** a dedicated fill recipe exists for this form in `engine/recipes/`. The recipe is the authoritative field mapping; this doc is the human-readable companion.
