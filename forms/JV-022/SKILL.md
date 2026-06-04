<!-- Reused from prior skills stash; verify against schema.json. -->
# JV-022 — Proof of Community Service/Public Service Performed

**Form Number:** JV-022, Rev. 10/21
**Pages:** 1
**Fillable Fields:** 32
**Category:** Juvenile
**Court:** District Court / Juvenile Division

## Purpose

Form used in juvenile proceedings in Maine court.

## Governing Law

- **15 M.R.S. § 3001 et seq.** — Primary statutory authority

## Field Mappings

| Field Name | Type | Page | Notes |
|-----------|------|------|-------|
| `Juvenile` | Text | 1 |  |
| `Location Town` | Text | 1 | Court location |
| `Docket No` | Text | 1 | Court docket number |
| `Juveniles Name` | Text | 1 |  |
| `Date of Birth mmddyyyy` | Text | 1 | MM/DD/YYYY format |
| `Total number of hours needed` | Text | 1 |  |
| `Required date of completion mmddyyyy` | Text | 1 | MM/DD/YYYY format |
| `Organization name` | Text | 1 |  |
| `Address 1` | Text | 1 | Mailing/street address |
| `Address 2` | Text | 1 | Mailing/street address |
| `Telephone number` | Text | 1 | Phone number |
| `Supervisors name` | Text | 1 |  |
| `Telephone number_2` | Text | 1 | Phone number |
| `Date of service mmddyyyy` | Text | 1 | MM/DD/YYYY format |
| `Hours Completed` | Text | 1 |  |
| `Date of service mmddyyyy_2` | Text | 1 | MM/DD/YYYY format |
| `Hours Completed_2` | Text | 1 |  |
| `Date of service mmddyyyy_3` | Text | 1 | MM/DD/YYYY format |
| `Hours Completed_3` | Text | 1 |  |
| `Date of service mmddyyyy_4` | Text | 1 | MM/DD/YYYY format |
| `Hours Completed_4` | Text | 1 |  |
| `Date of service mmddyyyy_5` | Text | 1 | MM/DD/YYYY format |
| `Hours Completed_5` | Text | 1 |  |
| `Highly Satisfactory` | CheckBox | 1 | Check if applicable |
| `Satisfactory` | CheckBox | 1 | Check if applicable |
| `Unsatisfactory` | CheckBox | 1 | Check if applicable |
| `Comments 1` | Text | 1 |  |
| `Comments 2` | Text | 1 |  |
| `Comments 3` | Text | 1 |  |
| `Date mmddyyyy` | Text | 1 | MM/DD/YYYY format |
| `undefined` | Text | 1 |  |
| `Printed Name` | Text | 1 |  |

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
- [ ] Contact information is complete

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
