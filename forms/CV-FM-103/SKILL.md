<!-- Reused from prior skills stash; verify against schema.json. -->
# CV-FM-103 — Notice of Hearing

**Form Number:** CV-FM-103
**Fillable Fields:** 15
**Category:** Civil/Family — Procedural
**Court:** Superior Court / District Court

## Purpose

Formal notice that a hearing has been scheduled in a case, informing parties of the date, time, and location.

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
| `This is to notify you that the above matter has been scheduled for` | Text | From matter data |
| `on mmddyyyy` | Text | From matter data |
| `at` | Text | From matter data |
| `am` | CheckBox | From matter data |
| `pm at the above named court` | CheckBox | From matter data |
| `undefined` | Text | From matter data |
| `Date mmddyyyy` | Text | `today()` or relevant date |
| `undefined_2` | Text | From matter data |


## AI Hints

Simple one-page form, 15 fields. Clerk-completed form notifying parties of hearing type, date, time (AM/PM), and court location. Party must appear in person or by counsel to be heard.

## Validation Checklist

- [ ] Case caption is complete (parties, court, docket number)
- [ ] Date is filled in (mm/dd/yyyy format)
- [ ] Signature line identified (leave blank for physical signature)
- [ ] Correct court type selected (Superior/District)
