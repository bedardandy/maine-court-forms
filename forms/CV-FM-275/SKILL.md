<!-- Reused from prior skills stash; verify against schema.json. -->
# CV-FM-275 — Objection to Court-Paid Referee's Report

**Form Number:** CV-FM-275
**Fillable Fields:** 23
**Category:** Civil/Family — Referee Program
**Court:** Superior Court / District Court
**Related Forms:** CV-FM-273

## Purpose

Files specific objections to a court-paid referee's report, requesting judge review before final order.

## Governing Law

- **Administrative Order JB-22-03**

## Field Mapping Summary

### Page 0

| Field Name | Type | Source |
|-----------|------|--------|
| `Plaintiff` | Text | From matter data |
| `V` | Text | From matter data |
| `Other party` | Text | From matter data |
| `Superior Court` | CheckBox | `matter.court_type` |
| `District Court` | CheckBox | `matter.court_type` |
| `County` | Text | `matter.court_county` |
| `undefined` | Text | From matter data |
| `plaintiff` | CheckBox | From matter data |
| `defendant` | CheckBox | From matter data |
| `other party in this case` | CheckBox | From matter data |
| `2 The appointment of a courtpaid referee in this case was not done by the agreement of the parties` | Text | From matter data |
| `My objections are as follows please be specific 1` | Text | From matter data |
| `Additional pages are attached` | CheckBox | From matter data |
| `4 I have sent a copy of this objection to the other party or parties in my case` | Text | From matter data |
| `Text1` | Text | From matter data |
| `Plaintiff_2` | CheckBox | From matter data |
| `Plaintiffs Attorney` | CheckBox | From matter data |
| `Defendant` | CheckBox | From matter data |
| `Defendants Attorney` | CheckBox | From matter data |
| `Other` | CheckBox | From matter data |
| `undefined_2` | Text | From matter data |
| `Printed Name and Bar Number if applicable` | Text | `attorney.bar_number` |
| `Text2` | Text | From matter data |


## AI Hints

23 fields. Only available when referee appointment was not by agreement. Must be specific about objections. Must confirm copy sent to opposing party. Additional pages can be attached.

## Validation Checklist

- [ ] Case caption is complete (parties, court, docket number)
- [ ] Date is filled in (mm/dd/yyyy format)
- [ ] Signature line identified (leave blank for physical signature)
- [ ] Correct court type selected (Superior/District)
- [ ] Related forms prepared if needed (CV-FM-273)
