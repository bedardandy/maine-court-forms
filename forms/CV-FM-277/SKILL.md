# CV-FM-277 — Zoom Participant List

**Form Number:** CV-FM-277
**Fillable Fields:** 39
**Category:** Civil/Family — Referee Program
**Court:** Superior Court / District Court
**Related Forms:** CV-FM-270, CV-FM-288

## Purpose

Provides contact information to the Zoom hosting service for remote court-paid referee hearings or settlement conferences.

## Governing Law

- **Administrative Orders JB-22-03, JB-23-04**

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
| `Party name` | Text | From matter data |
| `Email address` | Text | `party.email` |
| `Phone number` | Text | `party.phone` |
| `Attorney name` | Text | From matter data |
| `Email address_2` | Text | `party.email` |
| `Phone number_2` | Text | `party.phone` |
| `1 Witness name` | Text | From matter data |
| `Email address_3` | Text | `party.email` |
| `Phone number_3` | Text | `party.phone` |
| `2 Witness name` | Text | From matter data |
| `Email address_4` | Text | `party.email` |
| `Phone number_4` | Text | `party.phone` |

### Page 1

| Field Name | Type | Source |
|-----------|------|--------|
| `3 Witness name` | Text | From matter data |
| `Email address_5` | Text | `party.email` |
| `Phone number_5` | Text | `party.phone` |
| `4 Witness name` | Text | From matter data |
| `Email address_6` | Text | `party.email` |
| `Phone number_6` | Text | `party.phone` |
| `Additional pages are attached` | CheckBox | From matter data |
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

39 fields, 2 pages. Must be emailed to MaineRCA@courtscribes.com at least 7 days before hearing. Collects party, attorney, and witness contact info (up to 8 witnesses per party). Not sent to referee or opposing party. Used for technical support purposes.

## Validation Checklist

- [ ] Case caption is complete (parties, court, docket number)
- [ ] Correct court type selected (Superior/District)
- [ ] Related forms prepared if needed (CV-FM-270, CV-FM-288)
