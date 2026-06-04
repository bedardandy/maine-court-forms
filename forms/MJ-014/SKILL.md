<!-- Reused from prior skills stash; verify against schema.json. -->
# MJ-014 — Request for Restitution Order to be Made

**Form Number:** MJ-014, Rev. 06/22
**Pages:** 1
**Fillable Fields:** 14
**Category:** Money Judgment
**Court:** District Court / Superior Court

## Purpose

This is a court order form used in money judgment cases. Typically completed by the court or prepared by counsel for judicial signature.

## Governing Law

- **17-A M.R.S. § 2019**

## Field Mappings

| Field Name | Type | Page | Notes |
|-----------|------|------|-------|
| `CreditorVictim` | Text | 1 |  |
| `DebtorDefendant` | Text | 1 |  |
| `Location Town` | Text | 1 | Court location |
| `Docket No` | Text | 1 | Court docket number |
| `NOW COMES` | Text | 1 |  |
| `Mailing Address of CreditorVictim 1` | Text | 1 | Mailing/street address |
| `Mailing Address of CreditorVictim 2` | Text | 1 | Mailing/street address |
| `Mailing Address of CreditorVictim 3` | Text | 1 | Mailing/street address |
| `undefined` | Text | 1 |  |
| `Docket Number of the underlying criminal matter` | Text | 1 | Court docket number |
| `undefined_2` | Text | 1 |  |
| `Defendants date of birth mmddyyyy` | Text | 1 | MM/DD/YYYY format |
| `Date mmddyyyy` | Text | 1 | MM/DD/YYYY format |
| `undefined_3` | Text | 1 |  |

## AI Hints

- **Deadlines**: Strict filing deadlines apply for post-judgment motions.
- **Service**: Proper service of judgment documents is required.
- **Docket Number**: Leave blank for new filings; clerk assigns. Enter if responding to existing case.

## Validation Checklist

- [ ] All required party names are filled in
- [ ] Court location/county is correct for venue
- [ ] Docket number included (if existing case)
- [ ] All dates are in correct format (MM/DD/YYYY)
- [ ] Contact information is complete

## Related Forms

- **MJ-002** — REQUEST FOR
- **MJ-005** — ANSWER TO THE “ORDER TO HOLD AND ANSWER”
- **MJ-007** — ANSWER BY EMPLOYER TO “ORDER TO WITHHOLD AND DELIVER”
- **MJ-009** — MOTION AND AFFIDAVIT FOR ORDER TO WITHHOLD AND DELIVER
- **MJ-015** — MOTION, AFFIDAVIT AND ORDER TO DEPARTMENT OF LABOR
- **MJ-SC-001** — AFFIDAVIT AND AGREEMENT
- **MJ-SC-005** — MOTION FOR CONTEMPT
- **MJ-SC-012** — AFFIDAVIT AND AGREEMENT

> **Note:** a dedicated fill recipe exists for this form in `engine/recipes/`. The recipe is the authoritative field mapping; this doc is the human-readable companion.
