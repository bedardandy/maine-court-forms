# CV-FM-273 — Notice Preserving Right to Object to Court-Paid Referee's Report

**Form Number:** CV-FM-273
**Fillable Fields:** 21
**Category:** Civil/Family — Referee Program
**Court:** Superior Court / District Court
**Related Forms:** CV-FM-270, CV-FM-275

## Purpose

Preserves a party's right to object to a court-paid referee's report when the referee was appointed without all parties' agreement.

## Governing Law

- **Administrative Order JB-22-03**

## Field Mapping Summary

### Page 0

| Field Name | Type | Source |
|-----------|------|--------|
| `Plaintiff` | Text | From matter data |
| `Defendant` | Text | From matter data |
| `Other party` | Text | From matter data |
| `Superior Court` | CheckBox | `matter.court_type` |
| `District Court` | CheckBox | `matter.court_type` |
| `County` | Text | `matter.court_county` |
| `Location Town` | Text | `matter.court_location` |
| `Docket No` | Text | `matter.docket_number` |
| `plaintiff` | CheckBox | From matter data |
| `defendant` | CheckBox | From matter data |
| `other party in this case` | CheckBox | From matter data |
| `2 The court appointed a referee paid for by the court to hear my case on mmddyyyy` | Text | From matter data |
| `Date mmddyyyy` | Text | `today()` or relevant date |
| `undefined` | Text | From matter data |
| `Plaintiff_2` | CheckBox | From matter data |
| `Plaintiffs Attorney` | CheckBox | From matter data |
| `Defendant_2` | CheckBox | From matter data |
| `Defendants Attorney` | CheckBox | From matter data |
| `Other` | CheckBox | From matter data |
| `undefined_2` | Text | From matter data |
| `Printed Name and Bar Number if applicable` | Text | `attorney.bar_number` |


## AI Hints

21 fields. Must be filed within 14 days of Order Appointing Court-Paid Referee. Only for use when appointment was made without all parties' agreement. Filing this notice means any party can object to referee's report, requiring judge to review before entering final order.

## Validation Checklist

- [ ] Case caption is complete (parties, court, docket number)
- [ ] Date is filled in (mm/dd/yyyy format)
- [ ] Signature line identified (leave blank for physical signature)
- [ ] Correct court type selected (Superior/District)
- [ ] Related forms prepared if needed (CV-FM-270, CV-FM-275)
