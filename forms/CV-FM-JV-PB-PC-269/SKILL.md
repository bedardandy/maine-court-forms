# CV-FM-JV-PB-PC-269 — Guardian ad Litem's Motion for Pre-Approval to Exceed the Voucher Cap

**Form Number:** CV-FM-JV-PB-PC-269
**Fillable Fields:** 48
**Category:** Cross-Category — GAL Administration
**Court:** Superior Court / District Court
**Related Forms:** CV-FM-JV-PB-PC-024

## Purpose

GAL requests pre-approval to exceed the maximum billable hours set in JB-05-05 for a particular legal stage.

## Governing Law

- **Administrative Order JB-05-05**

## Field Mapping Summary

### Page 0

| Field Name | Type | Source |
|-----------|------|--------|
| `Check Box1` | CheckBox | From matter data |
| `PlaintiffPetitioner` | Text | From matter data |
| `DefendantRespondent` | Text | From matter data |
| `Other party` | Text | From matter data |
| `IN RE` | CheckBox | From matter data |
| `undefined_2` | Text | From matter data |
| `Superior Court` | CheckBox | `matter.court_type` |
| `District Court` | CheckBox | `matter.court_type` |
| `County` | Text | `matter.court_county` |
| `Location Town` | Text | `matter.court_location` |
| `Docket No` | Text | `matter.docket_number` |
| `Child Protection Please indicate the legal stage to which this motion applies` | CheckBox | From matter data |
| `Summary Preliminary Hearing` | CheckBox | From matter data |
| `Cease Reunification Hearing` | CheckBox | From matter data |
| `Jeopardy Hearing with or without JR andor PP` | CheckBox | From matter data |
| `Contested Perm Guardianship Hearing` | CheckBox | From matter data |
| `Judicial Rev andor Perm Planning Hearing` | CheckBox | From matter data |
| `Contested Child Placement Hearing` | CheckBox | From matter data |
| `Termination of Parental Rights Hearing` | CheckBox | From matter data |
| `Dismissal of Child Protection Action` | CheckBox | From matter data |
| `Release of a GAL from an Order of Appointment` | CheckBox | From matter data |
| `Law Court Appeal` | CheckBox | From matter data |
| `Family matter` | CheckBox | From matter data |
| `Guardianship of a Minor` | CheckBox | From matter data |
| `Adoption` | CheckBox | From matter data |
| `Termination of Parental Rights Title 19A` | CheckBox | From matter data |
| `Juvenile Matter` | CheckBox | From matter data |
| `Guardian for Minor or Incompetent Person MR Civ P 17b` | CheckBox | From matter data |
| `Child protection cases` | CheckBox | From matter data |
| `hours during this legal stage of the proceeding or` | Text | From matter data |
| *... +11 more fields* | | |

### Page 1

| Field Name | Type | Source |
|-----------|------|--------|
| `4 The circumstances supporting this request are please attach additional pages as needed 1` | Text | From matter data |
| `Date mmddyyyy` | Text | `today()` or relevant date |
| `undefined_3` | Text | From matter data |
| `Name` | Text | From matter data |
| `Bar No` | Text | `attorney.bar_number` |
| `Address` | Text | `party.address` |
| `ORDER OF COURT` | Text | From matter data |


## AI Hints

48 fields, 2 pages. Lists all case types and legal stages with applicable hour caps. GAL must state: current hours billed, additional hours requested, reasons for exceeding cap. Includes ORDER section for judge to grant/deny with modified hour limit.

## Validation Checklist

- [ ] Case caption is complete (parties, court, docket number)
- [ ] Date is filled in (mm/dd/yyyy format)
- [ ] Signature line identified (leave blank for physical signature)
- [ ] Correct court type selected (Superior/District)
- [ ] Related forms prepared if needed (CV-FM-JV-PB-PC-024)
