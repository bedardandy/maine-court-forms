<!-- Reused from prior skills stash; verify against schema.json. -->
# CV-FM-JV-PB-PC-024 — Guardian ad Litem (GAL) Voucher

**Form Number:** CV-FM-JV-PB-PC-024
**Fillable Fields:** 86
**Category:** Cross-Category — GAL Administration
**Court:** District Court
**Related Forms:** CV-FM-JV-PB-PC-242, CV-FM-JV-PB-PC-269

## Purpose

Payment voucher for Guardian ad Litem services, documenting hours, fees, mileage, and expenses for reimbursement.

## Governing Law

- **Administrative Order JB-05-05 (GAL compensation)**

## Field Mapping Summary

### Page 0

| Field Name | Type | Source |
|-----------|------|--------|
| `undefined_2` | Text | From matter data |
| `Case` | CheckBox | From matter data |
| `v` | Text | From matter data |
| `DISTRICT COURT` | Text | `matter.court_type` |
| `INRE` | CheckBox | From matter data |
| `only one docket number per voucher` | Text | `matter.docket_number` |
| `DOCKET NUMBER` | Text | `matter.docket_number` |
| `Child Protection Please check applicable stage When a court appearance concludes more than one legal stage the GAL` | CheckBox | From matter data |
| `Summary Preliminary Hearing 10 hrs` | CheckBox | From matter data |
| `Jeopardy Hearing 20 hrs` | CheckBox | From matter data |
| `Judicial Review  Permanency Planning` | CheckBox | From matter data |
| `Termination of Parental Rights Hearing 20 hrs` | CheckBox | From matter data |
| `Cease Reunification Hearing 15 hrs` | CheckBox | From matter data |
| `Contested Permanency Guardianship Hearing` | CheckBox | From matter data |
| `Contested Child Placement Hearing 22 MRS` | CheckBox | From matter data |
| `Dismissal of Child Protection Action 15 hrs` | CheckBox | From matter data |
| `Release of a GAL from an Order of Appointment 15 hrs` | CheckBox | From matter data |
| `Law Court Appeal` | CheckBox | From matter data |
| `This voucher includes up to 10 additional hours for a summary` | CheckBox | From matter data |
| `Dismissal includes attendance at uncontested adoption` | CheckBox | From matter data |
| `hearing on mmddyyyy` | Text | From matter data |
| `DATE STAGE COMPLETED mmddyyyy` | Text | `today()` or relevant date |
| `Other Type of Case Please check the applicable type of case 20 hrs you must attach a copy of your appointment order` | CheckBox | From matter data |
| `Juvenile Matter` | CheckBox | From matter data |
| `Family Matter  Guardianship` | CheckBox | From matter data |
| `Family Matter  Adoption` | CheckBox | From matter data |
| `Family Matter  Termination of Parental Rights Title 19A` | CheckBox | From matter data |
| `Guardian for Minor or Incompetent Person MR Civ P 17b` | CheckBox | From matter data |
| `TOTAL HOURS` | Text | From matter data |
| `TotalHourlyFee` | Text | From matter data |
| *... +48 more fields* | | |

### Page 1

| Field Name | Type | Source |
|-----------|------|--------|
| `InvoicedHrs` | Text | From matter data |
| `CorrectedHr` | Text | From matter data |
| `InvoicedMileage` | Text | From matter data |
| `CorrectedMileage` | Text | From matter data |
| `InvoicedEx` | Text | From matter data |
| `CorrectedExpense` | Text | From matter data |
| `InvoicedTotal` | Text | From matter data |
| `CorrectedTotal` | Text | From matter data |


## AI Hints

86 fields, 2 pages. Complex voucher. Case types: Child Protection (with 10+ legal stages, each with hourly cap), Family Matter, Juvenile, Guardianship, Adoption, TPR. Hourly caps vary by stage (10-20 hrs). Rate and mileage table similar to CV-FM-291. Requires itemized billing, certification of accuracy, and supervisor/judge approval signature.

## Validation Checklist

- [ ] Case caption is complete (parties, court, docket number)
- [ ] Related forms prepared if needed (CV-FM-JV-PB-PC-242, CV-FM-JV-PB-PC-269)
