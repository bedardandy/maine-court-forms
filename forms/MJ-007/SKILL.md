<!-- Reused from prior skills stash; verify against schema.json. -->
# MJ-007 — Answer by Employer to “Order to Withhold

**Form Number:** MJ-007, Rev. 08/20
**Pages:** 2
**Fillable Fields:** 29
**Category:** Money Judgment
**Court:** District Court / Superior Court

## Purpose

This is a court order form used in money judgment cases. Typically completed by the court or prepared by counsel for judicial signature.

## Governing Law

- **14 M.R.S. § 3127-B**

## Field Mappings

| Field Name | Type | Page | Notes |
|-----------|------|------|-------|
| `Judgment Creditor` | Text | 1 |  |
| `Location Town` | Text | 1 | Court location |
| `Docket No` | Text | 1 | Court docket number |
| `Judgment Debtor` | Text | 1 |  |
| `My name is 1` | Text | 1 |  |
| `I am employed by` | Text | 1 |  |
| `My name is 2` | Text | 1 |  |
| `in the capacity of` | Text | 1 |  |
| `weekly` | CheckBox | 1 | Check if applicable |
| `biweekly` | CheckBox | 1 | Check if applicable |
| `monthly` | CheckBox | 1 | Check if applicable |
| `1` | Text | 1 |  |
| `undefined` | Text | 1 |  |
| `Text1` | Text | 1 |  |
| `Text2` | Text | 1 |  |
| `undefined_3` | Text | 1 |  |
| `undefined_4` | Text | 1 |  |
| `undefined_5` | Text | 1 |  |
| `undefined_6` | Text | 1 |  |
| `2` | Text | 1 |  |
| `3` | Text | 1 |  |
| `4` | Text | 1 |  |
| `5` | Text | 1 |  |
| `6` | Text | 1 |  |
| `7` | Text | 1 |  |
| `8` | Text | 1 |  |
| `I swear under penalty of perjury that the above statements are true and correct I understand that these` | CheckBox | 2 | Check if applicable |
| `Date mmddyyyy` | Text | 2 | MM/DD/YYYY format |
| `undefined_7` | Text | 2 |  |

## AI Hints

- **Deadlines**: Strict filing deadlines apply for post-judgment motions.
- **Service**: Proper service of judgment documents is required.
- **Docket Number**: Leave blank for new filings; clerk assigns. Enter if responding to existing case.

## Validation Checklist

- [ ] All required party names are filled in
- [ ] Court location/county is correct for venue
- [ ] Docket number included (if existing case)
- [ ] All dates are in correct format (MM/DD/YYYY)

## Related Forms

- **MJ-002** — REQUEST FOR
- **MJ-005** — ANSWER TO THE “ORDER TO HOLD AND ANSWER”
- **MJ-009** — MOTION AND AFFIDAVIT FOR ORDER TO WITHHOLD AND DELIVER
- **MJ-014** — REQUEST FOR RESTITUTION ORDER TO BE MADE A MONEY JUDGMENT
- **MJ-015** — MOTION, AFFIDAVIT AND ORDER TO DEPARTMENT OF LABOR
- **MJ-SC-001** — AFFIDAVIT AND AGREEMENT
- **MJ-SC-005** — MOTION FOR CONTEMPT
- **MJ-SC-012** — AFFIDAVIT AND AGREEMENT

> **Note:** a dedicated fill recipe exists for this form in `engine/recipes/`. The recipe is the authoritative field mapping; this doc is the human-readable companion.
