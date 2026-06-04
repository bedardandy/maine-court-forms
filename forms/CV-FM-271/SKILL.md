<!-- Reused from prior skills stash; verify against schema.json. -->
# CV-FM-271 — Consent or Objection to Appointment of Court-Paid Referee

**Form Number:** CV-FM-271
**Fillable Fields:** 19
**Category:** Civil/Family — Referee Program
**Court:** Superior Court / District Court
**Related Forms:** CV-FM-270

## Purpose

Party's consent to or objection against appointment of a court-paid referee under JB-22-03.

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
| `Consent to Appointment of Referee I consent to the appointment of a referee paid for by the court to hear my` | CheckBox | From matter data |
| `Objection to Appointment of Referee I object to the appointment of a referee paid for by the court to hear my` | CheckBox | From matter data |
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

19 fields. Binary choice: consent or objection. Consent means court adopts referee's report as final order (appealable to SJC). Objection means court may still appoint referee but party preserves objection rights.

## Validation Checklist

- [ ] Case caption is complete (parties, court, docket number)
- [ ] Date is filled in (mm/dd/yyyy format)
- [ ] Signature line identified (leave blank for physical signature)
- [ ] Correct court type selected (Superior/District)
- [ ] Related forms prepared if needed (CV-FM-270)
