<!-- Reused from prior skills stash; verify against schema.json. -->
# CV-067 — Application to Proceed Without Payment of Fees

**Form Number:** CV-067
**Fillable Fields:** 148
**Category:** Civil — Fee Waiver
**Court:** Superior Court / District Court

## Purpose

Requests waiver of court fees (filing, service, mediation, jury, appeal) based on financial inability to pay.

## Governing Law

- **M.R. Civ. P. 91 (proceedings in forma pauperis)**

## Field Mapping Summary

### Page 0

| Field Name | Type | Source |
|-----------|------|--------|
| `Plaintiff` | Text | From matter data |
| `undefined` | Text | From matter data |
| `V 1` | Text | From matter data |
| `V 2` | Text | From matter data |
| `Superior Court` | CheckBox | `matter.court_type` |
| `District Court` | CheckBox | `matter.court_type` |
| `undefined_2` | Text | From matter data |
| `Text1` | Text | From matter data |
| `Docket` | Text | `matter.docket_number` |
| `PLAINTIFF` | CheckBox | From matter data |
| `DEFENDANT` | CheckBox | From matter data |
| `filing fee` | CheckBox | From matter data |
| `service costs` | CheckBox | From matter data |
| `mediation fee` | CheckBox | From matter data |
| `jury fee` | CheckBox | From matter data |
| `appeal fee or` | CheckBox | From matter data |
| `other` | CheckBox | From matter data |
| `I am without funds to pay the X all that apply` | Text | From matter data |
| `I request that service costs be paid without first attempting service by mail because` | CheckBox | From matter data |
| `1` | Text | From matter data |
| `Date mmddyyyy` | Text | `today()` or relevant date |
| `undefined_3` | Text | From matter data |
| `Text2` | Text | From matter data |
| `Address` | Text | `party.address` |
| `Text3` | Text | From matter data |
| `Text4` | Text | From matter data |

### Page 2

| Field Name | Type | Source |
|-----------|------|--------|
| `Plaintiff` | Text | From matter data |
| `undefined` | Text | From matter data |
| `V 1` | Text | From matter data |
| `V 2` | Text | From matter data |
| `Superior Court` | CheckBox | `matter.court_type` |
| `District Court` | CheckBox | `matter.court_type` |
| `Unified Criminal Docket` | CheckBox | `matter.docket_number` |
| `undefined_2` | Text | From matter data |
| `Text1` | Text | From matter data |
| `Docket` | Text | `matter.docket_number` |
| `Name of person whose financial information appears on this affidavit` | Text | From matter data |
| `My application to proceed without payment of fees` | CheckBox | From matter data |
| `Other` | CheckBox | From matter data |
| `other reason` | Text | From matter data |
| `Mailing Address` | Text | `party.address` |
| `Date of Birth mmddyyyy` | Text | `today()` or relevant date |
| `Home Phone` | Text | `party.phone` |
| `Cell Phone` | Text | `party.phone` |
| `Work Phone` | Text | `party.phone` |
| `Email` | Text | `party.email` |
| `Employment Employer is name and address` | CheckBox | `party.address` |
| `undefined_4` | Text | From matter data |
| `every` | Text | From matter data |
| `Salary and wages gross pay` | CheckBox | From matter data |
| `undefined_5` | Text | From matter data |
| `week` | CheckBox | From matter data |
| `biweekly` | CheckBox | From matter data |
| `month` | CheckBox | From matter data |
| `Other income type` | CheckBox | From matter data |
| `undefined_6` | Text | From matter data |
| *... +41 more fields* | | |

### Page 3

| Field Name | Type | Source |
|-----------|------|--------|
| `Mortgage` | CheckBox | From matter data |
| `EXPENSES Monthly` | Text | From matter data |
| `Child Support` | CheckBox | From matter data |
| `undefined_18` | Text | From matter data |
| `Utilities` | CheckBox | From matter data |
| `undefined_19` | Text | From matter data |
| `Food` | CheckBox | From matter data |
| `undefined_20` | Text | From matter data |
| `Cable` | CheckBox | From matter data |
| `undefined_21` | Text | From matter data |
| `Credit Card` | CheckBox | From matter data |
| `undefined_22` | Text | From matter data |
| `Loans` | CheckBox | From matter data |
| `undefined_23` | Text | From matter data |
| `Heat` | CheckBox | From matter data |
| `Heat cost` | Text | From matter data |
| `Rent` | CheckBox | From matter data |
| `undefined_25` | Text | From matter data |
| `Cell Phone_2` | CheckBox | `party.phone` |
| `undefined_24` | Text | From matter data |
| `Other_4` | CheckBox | From matter data |
| `2` | Text | From matter data |
| `undefined_26` | Text | From matter data |
| `Check Box1` | CheckBox | From matter data |
| `I have` | Text | From matter data |
| `Check Box2` | CheckBox | From matter data |
| `I have_2` | Text | From matter data |
| `number of children for whom I pay support of` | Text | From matter data |
| `week_4` | CheckBox | From matter data |
| `biweekly_4` | CheckBox | From matter data |
| *... +21 more fields* | | |


## AI Hints

148 fields — very complex form. Two pages with detailed financial affidavit. Page 1: fee type selection, applicant info. Page 2: sworn affidavit with income, assets, expenses, dependents. Includes employment info, public assistance, monthly income/expenses breakdown. Applicant agrees to pay if situation changes or receives settlement.

## Validation Checklist

- [ ] Case caption is complete (parties, court, docket number)
- [ ] Correct court type selected (Superior/District)
