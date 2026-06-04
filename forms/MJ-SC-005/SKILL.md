<!-- Reused from prior skills stash; verify against schema.json. -->
# MJ-SC-005 — Motion for Contempt

**Form Number:** MJ-SC-005, Rev. 08/20
**Pages:** 1
**Fillable Fields:** 23
**Category:** Money Judgment
**Court:** District Court / Superior Court

## Purpose

This motion form is used in money judgment cases in Maine court. Filed to request specific court action.

## Governing Law

- **14 M.R.S. § 3134**
- **14 M.R.S. § 3136**
- **14 M.R.S. §§ 3134**

## Field Mappings

| Field Name | Type | Page | Notes |
|-----------|------|------|-------|
| `Judgment Creditor` | Text | 1 |  |
| `Location Town` | Text | 1 | Court location |
| `Docket No` | Text | 1 | Court docket number |
| `Judgment Debtor` | Text | 1 |  |
| `The judgment debtor presently resides at` | Text | 1 |  |
| `undefined` | Text | 1 |  |
| `On mmddyyyy` | Text | 1 |  |
| `plus costs of` | Text | 1 |  |
| `Text1` | Text | 1 |  |
| `Text2` | Text | 1 |  |
| `Check Box5` | CheckBox | 1 | Check if applicable |
| `On mmddyyyy_2` | Text | 1 |  |
| `creditor in installments of` | Text | 1 |  |
| `per` | Text | 1 |  |
| `Check Box6` | CheckBox | 1 | Check if applicable |
| `On mmddyyyy_3` | Text | 1 |  |
| `Check Box7` | CheckBox | 1 | Check if applicable |
| `Text4` | Text | 1 |  |
| `1` | Text | 1 |  |
| `2` | Text | 1 |  |
| `I swear under penalty of perjury that the above statements are true and correct I understand that these` | CheckBox | 1 | Check if applicable |
| `Date mmddyyyy` | Text | 1 | MM/DD/YYYY format |
| `undefined_2` | Text | 1 |  |

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
- **MJ-007** — ANSWER BY EMPLOYER TO “ORDER TO WITHHOLD AND DELIVER”
- **MJ-009** — MOTION AND AFFIDAVIT FOR ORDER TO WITHHOLD AND DELIVER
- **MJ-014** — REQUEST FOR RESTITUTION ORDER TO BE MADE A MONEY JUDGMENT
- **MJ-015** — MOTION, AFFIDAVIT AND ORDER TO DEPARTMENT OF LABOR
- **MJ-SC-001** — AFFIDAVIT AND AGREEMENT
- **MJ-SC-012** — AFFIDAVIT AND AGREEMENT

> **Note:** a dedicated fill recipe exists for this form in `engine/recipes/`. The recipe is the authoritative field mapping; this doc is the human-readable companion.
