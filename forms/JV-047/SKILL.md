<!-- Reused from prior skills stash; verify against schema.json. -->
# JV-047 — Request for Abstract to the Secretary of State

**Form Number:** JV-047, Rev. 09/22
**Pages:** 2
**Fillable Fields:** 25
**Category:** Juvenile
**Court:** District Court / Juvenile Division

## Purpose

Form used in juvenile proceedings in Maine court.

## Governing Law

- **15 M.R.S. § 3308-C**
- **29-A  M.R.S. § 2463**
- **29-A M.R.S. § 2458**
- **29-A M.R.S. § 2463**

## Field Mappings

| Field Name | Type | Page | Notes |
|-----------|------|------|-------|
| `Juvenile` | Text | 1 |  |
| `Location Town` | Text | 1 | Court location |
| `Docket No` | Text | 1 | Court docket number |
| `Now comes the State of Maine by and through counsel namely` | Text | 1 |  |
| `Date mmddyyyy` | Text | 1 | MM/DD/YYYY format |
| `undefined` | Text | 1 |  |
| `Printed name and bar number` | Text | 1 | Attorney bar number |
| `assault` | CheckBox | 2 | Check if applicable |
| `aggravated assault` | CheckBox | 2 | Check if applicable |
| `elevated aggravated assault` | CheckBox | 2 | Check if applicable |
| `criminal threatening` | CheckBox | 2 | Check if applicable |
| `reckless conduct` | CheckBox | 2 | Check if applicable |
| `Caused bodily injury` | CheckBox | 2 | Check if applicable |
| `Caused serious bodily injury to another person` | CheckBox | 2 | Check if applicable |
| `Created a substantial risk of serious bodily injury andor` | CheckBox | 2 | Check if applicable |
| `Placed another person in fear of imminent bodily injury` | CheckBox | 2 | Check if applicable |
| `The above adjudication is for a juvenile crime that would constitute a Class` | Text | 2 |  |
| `a` | CheckBox | 2 | Check if applicable |
| `used in the transport of hazardous materials andor` | CheckBox | 2 | Check if applicable |
| `a bus carrying 15` | CheckBox | 2 | Check if applicable |
| `3 Date of offense mmddyyyy` | Text | 2 | MM/DD/YYYY format |
| `4 Date of adjudicatory hearing mmddyyyy` | Text | 2 | MM/DD/YYYY format |
| `plea` | CheckBox | 2 | Check if applicable |
| `court finding` | CheckBox | 2 | Check if applicable |
| `6 Juveniles date of birth mmddyyyy` | Text | 2 | MM/DD/YYYY format |

## AI Hints

- **Confidentiality**: Juvenile records are confidential. Use initials only.
- **Diversion**: Consider whether diversion programs apply before formal proceedings.
- **Guardian ad Litem**: Court may appoint GAL for the juvenile.
- **Docket Number**: Leave blank for new filings; clerk assigns. Enter if responding to existing case.

## Validation Checklist

- [ ] All required party names are filled in
- [ ] Court location/county is correct for venue
- [ ] Docket number included (if existing case)
- [ ] All dates are in correct format (MM/DD/YYYY)
- [ ] Attorney bar number included (if represented)

## Related Forms

- **JV-002-W** — Juvenile Summons
- **JV-005** — PETITION FOR REVIEW OF DETENTION OF JUVENILE AND ORDER
- **JV-006-W** — Conditions of Release
- **JV-008-W** — ORDERED: These conditions are made part of the judgment
- **JV-009-W** — Notice to Parents and Legal Guardians
- **JV-010-W** — Notice to Juvenile of Right to Appeal to the Law Court
- **JV-011-W** — Notice to Parent, Guardian, or Legal Custodian
- **JV-012** — Notice of Appeal to the Law Court
- **JV-016-W** — HEARING NOTICE TO PARENTS/GUARDIAN/LEGAL CUSTODIAN
- **JV-017** — Waiver of Notice

> **Note:** a dedicated fill recipe exists for this form in `engine/recipes/`. The recipe is the authoritative field mapping; this doc is the human-readable companion.
