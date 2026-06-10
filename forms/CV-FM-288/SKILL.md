# CV-FM-288 — Motion for Appointment of Court-Paid Attorney Referee

**Form Number:** CV-FM-288
**Fillable Fields:** 25
**Category:** Civil/Family — Attorney Referee Program
**Court:** Superior Court / District Court
**Related Forms:** CV-FM-289, CV-FM-277, CV-FM-291

## Purpose

Requests appointment of a specific licensed attorney as court-paid referee under JB-23-04 (attorney referee program, distinct from JB-22-03).

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
| `IN RE` | CheckBox | From matter data |
| `undefined_2` | Text | From matter data |
| `Superior Court` | CheckBox | `matter.court_type` |
| `District Court` | CheckBox | `matter.court_type` |
| `County` | Text | `matter.court_county` |
| `Location Town` | Text | `matter.court_location` |
| `Docket No` | Text | `matter.docket_number` |
| `plaintiff` | CheckBox | From matter data |
| `defendant` | CheckBox | From matter data |
| `other party in this case and I ask that the` | CheckBox | From matter data |
| `court appoint attorneys name` | Text | From matter data |
| `I request access to CourtScribes Services each party must complete and email CVFM277 Zoom` | CheckBox | `party.email` |
| `Date mmddyyyy` | Text | `today()` or relevant date |
| `undefined_3` | Text | From matter data |
| `Plaintiff_2` | CheckBox | From matter data |
| `Plaintiffs Attorney` | CheckBox | From matter data |
| `Defendant_2` | CheckBox | From matter data |
| `Defendants Attorney` | CheckBox | From matter data |
| `Other` | CheckBox | From matter data |
| `undefined_4` | Text | From matter data |
| `Bar No if applicable` | Text | `attorney.bar_number` |


## AI Hints

25 fields. Names a specific attorney for appointment. Requires agreement of all parties (each must file CV-FM-289). Option to request CourtScribes/Zoom services (requires CV-FM-277). Different from CV-FM-270 which is for the general referee program under JB-22-03.

## Validation Checklist

- [ ] Case caption is complete (parties, court, docket number)
- [ ] Date is filled in (mm/dd/yyyy format)
- [ ] Signature line identified (leave blank for physical signature)
- [ ] Correct court type selected (Superior/District)
- [ ] Related forms prepared if needed (CV-FM-289, CV-FM-277, CV-FM-291)
