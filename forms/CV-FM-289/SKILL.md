# CV-FM-289 — Agreement to Appointment of Court-Paid Attorney Referee

**Form Number:** CV-FM-289
**Fillable Fields:** 20
**Category:** Civil/Family — Attorney Referee Program
**Court:** Superior Court / District Court
**Related Forms:** CV-FM-288

## Purpose

Party's agreement to appointment of a court-paid attorney referee under JB-23-04.

## Governing Law

- **Administrative Order JB-23-04**

## Field Mapping Summary

### Page 0

| Field Name | Type | Source |
|-----------|------|--------|
| `Check Box1` | CheckBox | From matter data |
| `Plaintiff` | Text | From matter data |
| `Defendant` | Text | From matter data |
| `Other party` | Text | From matter data |
| `OR` | CheckBox | From matter data |
| `IN RE` | Text | From matter data |
| `Superior Court` | CheckBox | `matter.court_type` |
| `District Court` | CheckBox | `matter.court_type` |
| `County` | Text | `matter.court_county` |
| `Location Town` | Text | `matter.court_location` |
| `Docket No` | Text | `matter.docket_number` |
| `Date mmddyyyy` | Text | `today()` or relevant date |
| `undefined_2` | Text | From matter data |
| `Plaintiff_2` | CheckBox | From matter data |
| `Plaintiffs Attorney` | CheckBox | From matter data |
| `Defendant_2` | CheckBox | From matter data |
| `Defendants Attorney` | CheckBox | From matter data |
| `undefined_3` | CheckBox | From matter data |
| `Other` | Text | From matter data |
| `Bar No if applicable` | Text | `attorney.bar_number` |


## AI Hints

20 fields. Consent form — party agrees to attorney referee appointment. Understands court will adopt referee's report as final order, appealable to SJC.

## Validation Checklist

- [ ] Case caption is complete (parties, court, docket number)
- [ ] Correct court type selected (Superior/District)
- [ ] Related forms prepared if needed (CV-FM-288)
