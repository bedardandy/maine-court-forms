# CV-FM-270 — Motion for Appointment of Court-Paid Referee

**Form Number:** CV-FM-270
**Fillable Fields:** 30
**Category:** Civil/Family — Referee Program
**Court:** Superior Court / District Court
**Related Forms:** CV-FM-271, CV-FM-273, CV-FM-274, CV-FM-275, CV-FM-278, CV-FM-280

## Purpose

Requests appointment of a court-paid referee to hold a settlement conference or hearing on contested issues.

## Governing Law

- **Administrative Order JB-22-03 (court-paid referee program)**

## Field Mapping Summary

### Page 0

| Field Name | Type | Source |
|-----------|------|--------|
| `Plaintiff` | Text | From matter data |
| `Defendant` | Text | From matter data |
| `Other party` | Text | From matter data |
| `Superior Court` | CheckBox | `matter.court_type` |
| `District Court` | CheckBox | `matter.court_type` |
| `Location Town` | Text | `matter.court_location` |
| `undefined` | Text | From matter data |
| `Docket No` | Text | `matter.docket_number` |
| `plaintiff` | CheckBox | From matter data |
| `defendant` | CheckBox | From matter data |
| `other party in this case and am requesting` | CheckBox | From matter data |
| `Hold a settlement conference on all the contested issues in this case OR` | CheckBox | From matter data |
| `Hold a hearing to determine all contested issues in this case` | CheckBox | From matter data |
| `I have notified the other parties of my intent to file this request` | CheckBox | From matter data |
| `opposing partys name` | Text | From matter data |
| `objects` | CheckBox | From matter data |
| `does not object to the request` | CheckBox | From matter data |
| `opposing partys name_2` | Text | From matter data |
| `objects_2` | CheckBox | From matter data |
| `does not object to the request_2` | CheckBox | From matter data |
| `I have made reasonable and good faith efforts to notify the other party or parties of this motion but` | CheckBox | From matter data |
| `Date mmddyyyy` | Text | `today()` or relevant date |
| `Text1` | Text | From matter data |
| `Plaintiff_2` | CheckBox | From matter data |
| `Plaintiffs Attorney` | CheckBox | From matter data |
| `Defendant_2` | CheckBox | From matter data |
| `Defendants Attorney` | CheckBox | From matter data |
| `Other` | CheckBox | From matter data |
| `undefined_2` | Text | From matter data |
| `Printed Name and Bar Number if applicable` | Text | `attorney.bar_number` |


## AI Hints

30 fields. Part of the JB-22-03 court-paid referee program. Party selects: settlement conference OR hearing. Must indicate opposing party's position (object/no objection) for up to 2 opposing parties. If unable to notify opposing party, must explain why. Signature block for plaintiff, defendant, or other party.

## Validation Checklist

- [ ] Case caption is complete (parties, court, docket number)
- [ ] Date is filled in (mm/dd/yyyy format)
- [ ] Signature line identified (leave blank for physical signature)
- [ ] Correct court type selected (Superior/District)
- [ ] Related forms prepared if needed (CV-FM-271, CV-FM-273, CV-FM-274, CV-FM-275, CV-FM-278, CV-FM-280)
