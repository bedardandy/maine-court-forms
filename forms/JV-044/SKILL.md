<!-- Reused from prior skills stash; verify against schema.json. -->
# JV-044 — Request to Make a Public Juvenile Petition

**Form Number:** JV-044, Rev. 12/21
**Pages:** 1
**Fillable Fields:** 12
**Category:** Juvenile
**Court:** District Court / Juvenile Division

## Purpose

This petition form initiates or requests action in a juvenile matter in Maine court.

## Governing Law

- **15 M.R.S. § 3308-C**
- **15 M.R.S. § 3318-A**

## Field Mappings

| Field Name | Type | Page | Notes |
|-----------|------|------|-------|
| `Juvenile` | Text | 1 |  |
| `Location Town` | Text | 1 | Court location |
| `Docket No` | Text | 1 | Court docket number |
| `I` | Text | 1 |  |
| `to public inspection for the following reasons attach additional pages if necessary 1` | Text | 1 |  |
| `Date mmddyyyy` | Text | 1 | MM/DD/YYYY format |
| `undefined` | Text | 1 |  |
| `Printed Name and Bar Number if applicable` | Text | 1 | Attorney bar number |
| `Mailing Address 1` | Text | 1 | Mailing/street address |
| `Mailing Address 2` | Text | 1 | Mailing/street address |
| `Telephone` | Text | 1 | Phone number |
| `Email` | Text | 1 | Email address |

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
