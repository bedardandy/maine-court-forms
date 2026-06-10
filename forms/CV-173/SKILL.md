# CV-173 — Verification (of Publication)

**Form Number:** CV-173
**Fillable Fields:** 19
**Category:** Civil — Service of Process
**Court:** Superior Court / District Court
**Related Forms:** CV-172

## Purpose

Newspaper employee's sworn verification that service by publication was completed as ordered — published once a week for three successive weeks.

## Governing Law

- **M.R. Civ. P. 4(g)(3) (verification of publication)**

## Field Mapping Summary

### Page 0

| Field Name | Type | Source |
|-----------|------|--------|
| `Plaintiff` | Text | From matter data |
| `Superior Court` | CheckBox | `matter.court_type` |
| `District Court` | CheckBox | `matter.court_type` |
| `County` | Text | `matter.court_county` |
| `Location Town` | Text | `matter.court_location` |
| `Defendant` | Text | From matter data |
| `Docket No` | Text | `matter.docket_number` |
| `County_2` | Text | `matter.court_county` |
| `I` | Text | From matter data |
| `employee of the` | Text | From matter data |
| `daily` | CheckBox | From matter data |
| `weekly newspaper of general circulation in` | CheckBox | From matter data |
| `County Maine that the Order of Service by publication in the matter of` | Text | `matter.court_county` |
| `of which the attached copy is a clipping was published in said newspaper once a week for three successive` | Text | From matter data |
| `V` | Text | From matter data |
| `weeks and that the first publication was made on mmddyyyy` | Text | From matter data |
| `I swear under penalty of perjury that the above statements are true and correct I understand that these` | CheckBox | From matter data |
| `Date mmddyyyy` | Text | `today()` or relevant date |
| `Printed Name` | Text | `signer.full_name` |


## AI Hints

Completed by newspaper employee, not party. Includes notary/oath section. Specifies daily vs weekly newspaper, county of circulation, date of first publication. Perjury warning included.

## Validation Checklist

- [ ] Case caption is complete (parties, court, docket number)
- [ ] Correct court type selected (Superior/District)
- [ ] Related forms prepared if needed (CV-172)
