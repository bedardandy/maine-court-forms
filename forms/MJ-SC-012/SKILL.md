<!-- Reused from prior skills stash; verify against schema.json. -->
# MJ-SC-012 — Affidavit and Agreement

**Form Number:** MJ-SC-012, Rev. 08/20
**Pages:** 1
**Fillable Fields:** 39
**Category:** Money Judgment
**Court:** District Court / Superior Court

## Purpose

This affidavit form provides sworn testimony in support of a money judgment matter.

## Governing Law

- **14 M.R.S. § 3125**

## Field Mappings

| Field Name | Type | Page | Notes |
|-----------|------|------|-------|
| `JudgmentCreditor` | Text | 1 |  |
| `LocationTown` | Text | 1 | Court location |
| `Docket No` | Text | 1 | Court docket number |
| `JudgmentDebtor` | Text | 1 |  |
| `I` | Text | 1 |  |
| `inthecapacityof` | Text | 1 |  |
| `theJudgmentDebtor` | Text | 1 |  |
| `Corporation` | CheckBox | 1 | Check if applicable |
| `LimitedLiabilityCompany` | CheckBox | 1 | Check if applicable |
| `LimitedLiabilityPartnership` | CheckBox | 1 | Check if applicable |
| `LimitedPartnership` | CheckBox | 1 | Check if applicable |
| `Nonprofit Corporation` | CheckBox | 1 | Check if applicable |
| `Other` | CheckBox | 1 | Check if applicable |
| `2 Judgment Debtorsgrossincome` | Text | 1 |  |
| `undefined` | Text | 1 |  |
| `per` | Text | 1 |  |
| `3 JudgmentDebtorsnetprofit` | Text | 1 |  |
| `per_2` | Text | 1 |  |
| `DEBT OWEDTO 1` | Text | 1 |  |
| `DEBT OWEDTO 2` | Text | 1 |  |
| `DEBT OWEDTO 3` | Text | 1 |  |
| `undefined_2` | Text | 1 |  |
| `per_3` | Text | 1 |  |
| `undefined_3` | Text | 1 |  |
| `undefined_4` | Text | 1 |  |
| `per_4` | Text | 1 |  |
| `undefined_5` | Text | 1 |  |
| `undefined_6` | Text | 1 |  |
| `per_5` | Text | 1 |  |
| `undefined_7` | Text | 1 |  |
| `5 JudgmentDebtoragreestopay` | Text | 1 |  |
| `per_6` | Text | 1 |  |
| `commencingmmddyyyy` | Text | 1 |  |
| `to` | Text | 1 |  |
| `I swearunderpenaltyofperjurythattheabove statementsaretrueandcorrect I understandthatthese` | CheckBox | 1 | Check if applicable |
| `Date mmddyyyy` | Text | 1 | MM/DD/YYYY format |
| `signature electronic or actual` | Text | 1 | Physical signature required |
| `Title` | Text | 1 |  |
| `Personallyappearedtheabovenamed` | Text | 1 |  |

## AI Hints

- **Deadlines**: Strict filing deadlines apply for post-judgment motions.
- **Service**: Proper service of judgment documents is required.
- **Docket Number**: Leave blank for new filings; clerk assigns. Enter if responding to existing case.

## Validation Checklist

- [ ] All required party names are filled in
- [ ] Court location/county is correct for venue
- [ ] Docket number included (if existing case)
- [ ] All dates are in correct format (MM/DD/YYYY)
- [ ] Signature lines are addressed (physical signature needed)

## Related Forms

- **MJ-002** — REQUEST FOR
- **MJ-005** — ANSWER TO THE “ORDER TO HOLD AND ANSWER”
- **MJ-007** — ANSWER BY EMPLOYER TO “ORDER TO WITHHOLD AND DELIVER”
- **MJ-009** — MOTION AND AFFIDAVIT FOR ORDER TO WITHHOLD AND DELIVER
- **MJ-014** — REQUEST FOR RESTITUTION ORDER TO BE MADE A MONEY JUDGMENT
- **MJ-015** — MOTION, AFFIDAVIT AND ORDER TO DEPARTMENT OF LABOR
- **MJ-SC-001** — AFFIDAVIT AND AGREEMENT
- **MJ-SC-005** — MOTION FOR CONTEMPT

> **Note:** a dedicated fill recipe exists for this form in `engine/recipes/`. The recipe is the authoritative field mapping; this doc is the human-readable companion.
