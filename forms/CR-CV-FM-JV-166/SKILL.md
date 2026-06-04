<!-- Reused from prior skills stash; verify against schema.json. -->
# CR-CV-FM-JV-166 — Motion for Transcript at State Expense

**Form Number:** CR-CV-FM-JV-166
**Fillable Fields:** 16
**Category:** Cross-Category — Procedural
**Court:** Superior Court / District Court / Unified Criminal Docket
**Related Forms:** CV-CR-JV-165

## Purpose

Requests preparation of a court transcript at state expense when the party cannot afford to pay.

## Field Mapping Summary

### Page 0

| Field Name | Type | Source |
|-----------|------|--------|
| `Check Box9` | CheckBox | From matter data |
| `PlaintiffPetitioner` | Text | From matter data |
| `DefendantRespondent` | Text | From matter data |
| `Other Party` | Text | From matter data |
| `IN RE` | CheckBox | From matter data |
| `MOTION FOR TRANSCRIPT AT STATE EXPENSE` | Text | From matter data |
| `Superior Court` | CheckBox | `matter.court_type` |
| `District Court` | CheckBox | `matter.court_type` |
| `Unified Criminal Docket` | CheckBox | `matter.docket_number` |
| `County` | Text | `matter.court_county` |
| `Location Town` | Text | `matter.court_location` |
| `Docket No` | Text | `matter.docket_number` |
| `I request preparation of a transcript at State expense for the following reasons 1` | Text | From matter data |
| `Date mmddyyyy` | Text | `today()` or relevant date |
| `undefined` | Text | From matter data |
| `Printed Name and Bar Number if applicable` | Text | `attorney.bar_number` |


## AI Hints

Must be filed with CV-CR-JV-165 (Transcript and Audio Order Form). Two pages — page 2 has additional space for reasons. Party must state reason for requesting state-funded transcript.

## Validation Checklist

- [ ] Case caption is complete (parties, court, docket number)
- [ ] Date is filled in (mm/dd/yyyy format)
- [ ] Signature line identified (leave blank for physical signature)
- [ ] Correct court type selected (Superior/District)
- [ ] Related forms prepared if needed (CV-CR-JV-165)
