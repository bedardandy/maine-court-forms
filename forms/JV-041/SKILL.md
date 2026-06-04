<!-- Reused from prior skills stash; verify against schema.json. -->
# JV-041 — Notice to Individual Inspecting a Juvenile

**Form Number:** JV-041, Rev. 12/21
**Pages:** 1
**Fillable Fields:** 6
**Category:** Juvenile
**Court:** District Court / Juvenile Division

## Purpose

This notice form provides required notification in juvenile proceedings.

## Governing Law

- **15 M.R.S. § 3308-C**
- **15 M.R.S. §§ 3308-C**

## Field Mappings

| Field Name | Type | Page | Notes |
|-----------|------|------|-------|
| `Juvenile` | Text | 1 |  |
| `Location Town` | Text | 1 | Court location |
| `Docket No` | Text | 1 | Court docket number |
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
