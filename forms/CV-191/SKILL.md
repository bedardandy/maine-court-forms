<!-- Reused from prior skills stash; verify against schema.json. -->
# CV-191 — Financial Affidavit

**Form Number:** CV-191, Rev. 06/20
**Pages:** 2
**Fillable Fields:** 122
**Category:** Civil / Criminal — Fee Waiver
**Filing Fee:** None (this IS the fee waiver support)
**Companion Forms:** Motion to Proceed Without Payment of Fees

## Purpose

This financial affidavit supports a request to proceed without payment of court fees (in forma pauperis) or other financial-related motions. It requires detailed disclosure of income, assets, expenses, and dependents.

## Governing Law

- **M.R. Civ. P. 91** — Proceedings in forma pauperis
- Court fee waiver policies

## Field Mappings

### Page 1 — Personal Info & Income

| Field Name | Type | Source | Notes |
|-----------|------|--------|-------|
| `Plaintiff` | Text | `matter.parties[role=plaintiff].full_name` | |
| `Superior Court` | CheckBox | `matter.court_type == "Superior"` | |
| `District Court` | CheckBox | `matter.court_type == "District"` | |
| `Unified Criminal Docket` | CheckBox | `matter.court_type == "UCD"` | |
| `County` | Text | `matter.court_county` | |
| `Location Town` | Text | `matter.court_location` | |
| `Defendant` | Text | `matter.parties[role=defendant].full_name` | |
| `Docket No` | Text | `matter.docket_number` | |
| Affiant name | Text | `matter.parties[role=affiant].full_name` | Person filing |
| `My application to proceed without payment` | CheckBox | deterministic | Most common use |
| `Other` checkbox + text | CheckBox/Text | AI | Other purpose |
| Mailing address | Text | `affiant.address` | |
| Date of birth | Text | `affiant.dob` | |
| Phone numbers (home/cell/work) | Text | `affiant.phone_*` | |
| Email | Text | `affiant.email` | |
| Employment checkbox + employer info | CheckBox/Text | `affiant.employer` | |
| Salary/wages amount | Text | `affiant.income_gross` | |
| Pay frequency checkboxes | CheckBox | `affiant.pay_frequency` | |
| Hourly wage + hours | Text | `affiant.hourly_rate` | Alternative to salary |
| Benefits checkboxes (unemployment, SS, TANF, etc.) | CheckBox | `affiant.benefits_types` | |
| Benefits total | Text | `affiant.benefits_total` | |

### Page 1 — Assets

| Field Name | Type | Source | Notes |
|-----------|------|--------|-------|
| Cash bail posted | Text | `affiant.cash_bail` | |
| Cash on hand | Text | `affiant.cash_on_hand` | |
| Cash in bank | Text | `affiant.bank_balance` | |
| Money owed to me | Text | `affiant.receivables` | |
| House value / amount owed | Text | `affiant.house_value` / `affiant.mortgage` | |
| Vehicle value | Text | `affiant.vehicle_value` | |
| Stocks value | Text | `affiant.stocks_value` | |
| Recreational vehicles | Text | `affiant.rec_vehicle_value` | |
| Other property | Text | `affiant.other_property` | |

### Page 2 — Expenses & Dependents

| Field Name | Type | Source | Notes |
|-----------|------|--------|-------|
| Monthly expenses (rent, food, utilities, etc.) | Text | `affiant.expenses.*` | Multiple fields |
| Number of dependents | Text | `affiant.num_dependents` | |
| Dependent names/ages | Text | `affiant.dependents` | |
| Total monthly expenses | Text | `affiant.total_expenses` | |
| Oath/signature | Text | *leave blank* | |
| Date | Text | `today()` | |

## AI Hints

- All financial figures should be consistent (income - expenses should roughly match available cash)
- If client has no income, explain source of support
- Benefits should be listed individually with amounts
- Vehicle value is fair market value, not purchase price

## Validation Checklist

- [ ] At least one income source or benefit identified (or explained why none)
- [ ] Asset values are realistic
- [ ] Expenses are itemized
- [ ] Total income vs total expenses relationship makes sense
- [ ] Date and signature present
- [ ] Purpose of affidavit is checked

## Related Forms Workflow

```
1. Motion to Proceed Without Payment of Fees
2. CV-191 (this form) — Financial Affidavit
3. Court ruling on fee waiver
```
