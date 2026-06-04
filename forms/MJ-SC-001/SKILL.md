<!-- Reused from prior skills stash; verify against schema.json. -->
# MJ-SC-001 — Affidavit and Agreement

**Form Number:** MJ-SC-001, Rev. 08/20
**Pages:** 2
**Fillable Fields:** 55
**Category:** Money Judgment
**Court:** District Court / Superior Court

## Purpose

This affidavit form provides sworn testimony in support of a money judgment matter.

## Governing Law

- **14 M.R.S. § 3125**

## Field Mappings

| Field Name | Type | Page | Notes |
|-----------|------|------|-------|
| `Judgment Creditor` | Text | 1 |  |
| `Location Town` | Text | 1 | Court location |
| `Docket No` | Text | 1 | Court docket number |
| `Judgment Debtor` | Text | 1 |  |
| `I` | Text | 1 |  |
| `1 My address is` | Text | 1 | Mailing/street address |
| `2 I am employed by` | Text | 1 |  |
| `in the capacity of` | Text | 1 |  |
| `3 My gross pay is` | Text | 1 |  |
| `per` | Text | 1 |  |
| `a court or state agency is` | Text | 1 |  |
| `per_2` | Text | 1 |  |
| `ITEM 1` | Text | 1 |  |
| `undefined` | Text | 1 |  |
| `ITEM 2` | Text | 1 |  |
| `undefined_2` | Text | 1 |  |
| `ITEM 3` | Text | 1 |  |
| `undefined_3` | Text | 1 |  |
| `ITEM 4` | Text | 1 |  |
| `undefined_4` | Text | 1 |  |
| `undefined_5` | Text | 1 |  |
| `DEBT OWED TO 1` | Text | 1 |  |
| `undefined_6` | Text | 1 |  |
| `per_3` | Text | 1 |  |
| `undefined_7` | Text | 1 |  |
| `DEBT OWED TO 2` | Text | 1 |  |
| `undefined_8` | Text | 1 |  |
| `per_4` | Text | 1 |  |
| `undefined_9` | Text | 1 |  |
| `DEBT OWED TO 3` | Text | 1 |  |
| `undefined_10` | Text | 1 |  |
| `per_5` | Text | 1 |  |
| `undefined_11` | Text | 1 |  |
| `7 I have` | Text | 1 |  |
| `8 My spouse receives income of` | Text | 1 |  |
| `per_6` | Text | 1 |  |
| `from` | Text | 1 |  |
| `9 My necessary living expenses are` | Text | 1 |  |
| `per_7` | Text | 1 |  |
| `10 I agree to pay` | Text | 1 |  |
| `per_8` | Text | 1 |  |
| `I understand that if I fail to make two or more payments the creditor can obtain an order requiring my` | Text | 1 |  |
| `to` | Text | 1 |  |
| `The parties acknowledge that the balance due as of this date is` | Text | 1 | MM/DD/YYYY format |
| `I swear under penalty of perjury that the above statements are true and correct I understand that these` | CheckBox | 2 | Check if applicable |
| `Date mmddyyyy` | Text | 2 | MM/DD/YYYY format |
| `undefined_12` | Text | 2 |  |
| `Personally appeared the abovenamed` | Text | 2 |  |
| `payments of 1` | Text | 2 |  |
| `per_9` | Text | 2 |  |
| `payments of 2` | Text | 2 |  |
| `commencing mmddyyyy` | Text | 2 |  |
| `Date mmddyyyy_3` | Text | 2 | MM/DD/YYYY format |
| `undefined_14` | Text | 2 |  |
| `Attorney for Judgment Creditor` | CheckBox | 2 | Check if applicable |

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
- **MJ-014** — REQUEST FOR RESTITUTION ORDER TO BE MADE A MONEY JUDGMENT
- **MJ-015** — MOTION, AFFIDAVIT AND ORDER TO DEPARTMENT OF LABOR
- **MJ-SC-005** — MOTION FOR CONTEMPT
- **MJ-SC-012** — AFFIDAVIT AND AGREEMENT

> **Note:** a dedicated fill recipe exists for this form in `engine/recipes/`. The recipe is the authoritative field mapping; this doc is the human-readable companion.
