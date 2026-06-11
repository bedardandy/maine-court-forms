# MJ-009 — Motion and Affidavit for Order to Withhold

**Form Number:** MJ-009, Rev. 08/20
**Pages:** 1
**Fillable Fields:** 18
**Category:** Money Judgment
**Court:** District Court / Superior Court

## Purpose

This motion form is used in money judgment cases in Maine court. Filed to request specific court action.

## Governing Law

- **14 M.R.S. § 3127-B**

## Computed lines (printed arithmetic)

Declared in `computations.json`. This form is recipe-tier (pointer-only mapping), so the shared engine evaluates the declaration on the recipe fill path: `fill_one` merges an omitted computed key (with its inputs supplied) into the case before the recipe runs and the recipe places it (`computed_fields` in the result); supply it and your value is written **as-is** — a contradiction only adds a `COMPUTATION_MISMATCH` warning under `computation_warnings`.

| computed key | printed instruction |
|---|---|
| `facts.mj009_total` = `facts.mj009_owed_amount` + `facts.mj009_interest` + `facts.mj009_costs` | The judgment debtor currently owes the judgment creditor $ (plus interest of $ ) plus costs of $ , for a total of $ . |

Note: the recipe writes $0.00 into the interest blank when only the owed amount is supplied (understates rather than invents). That is a widget default, not a fact — with `facts.mj009_interest` omitted the computation is skipped silently, so the total is computed only when all three component facts are supplied.

## Field Mappings

| Field Name | Type | Page | Notes |
|-----------|------|------|-------|
| `Judgment Creditor` | Text | 1 |  |
| `Location Town` | Text | 1 | Court location |
| `Docket No` | Text | 1 | Court docket number |
| `Judgment Debtor` | Text | 1 |  |
| `pursuant to 14 MRS  3127B to be served on` | Text | 1 |  |
| `Check Box1` | CheckBox | 1 | Check if applicable |
| `Courts installment order dated mmddyyyy` | Text | 1 | MM/DD/YYYY format |
| `pay` | Text | 1 |  |
| `per` | Text | 1 |  |
| `Check Box2` | CheckBox | 1 | Check if applicable |
| `The abovenamed Judgment Debtor failed to appear before this Court on mmddyyyy` | Text | 1 |  |
| `The judgment creditor currently owes the judgment creditor` | Text | 1 |  |
| `undefined_2` | Text | 1 |  |
| `plus costs of` | Text | 1 |  |
| `for a total of` | Text | 1 |  |
| `I swear under penalty of perjury that the above statements are true and correct I understand that these` | CheckBox | 1 | Check if applicable |
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

## Related Forms

- **MJ-002** — REQUEST FOR
- **MJ-005** — ANSWER TO THE “ORDER TO HOLD AND ANSWER”
- **MJ-007** — ANSWER BY EMPLOYER TO “ORDER TO WITHHOLD AND DELIVER”
- **MJ-014** — REQUEST FOR RESTITUTION ORDER TO BE MADE A MONEY JUDGMENT
- **MJ-015** — MOTION, AFFIDAVIT AND ORDER TO DEPARTMENT OF LABOR
- **MJ-SC-001** — AFFIDAVIT AND AGREEMENT
- **MJ-SC-005** — MOTION FOR CONTEMPT
- **MJ-SC-012** — AFFIDAVIT AND AGREEMENT

> **Note:** a dedicated fill recipe exists for this form in `engine/recipes/`. The recipe is the authoritative field mapping; this doc is the human-readable companion.
