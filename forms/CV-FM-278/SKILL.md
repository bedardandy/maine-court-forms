<!-- Reused from prior skills stash; verify against schema.json. -->
# CV-FM-278 — Report of Court-Paid Referee After Settlement Conference

**Form Number:** CV-FM-278
**Fillable Fields:** 16
**Category:** Civil/Family — Referee Program
**Court:** Superior Court / District Court
**Related Forms:** CV-FM-270

## Purpose

Referee's report after a settlement conference that did not result in agreement, recommending next steps.

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
| `On mmddyyyy` | Text | From matter data |
| `Other 1` | Text | From matter data |
| `Other 2` | Text | From matter data |
| `Other 3` | Text | From matter data |
| `Other 4` | Text | From matter data |
| `Other 5` | Text | From matter data |
| `Date mmddyyyy` | Text | `today()` or relevant date |
| `undefined` | Text | From matter data |


## AI Hints

16 fields. Simple one-page form completed by referee. States that settlement conference occurred but no agreement was reached. Matter should be presented to judicial officer for next steps (pretrial conference, etc.). Space for additional notes.

## Validation Checklist

- [ ] Case caption is complete (parties, court, docket number)
- [ ] Correct court type selected (Superior/District)
- [ ] Related forms prepared if needed (CV-FM-270)
