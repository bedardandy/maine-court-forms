# CV-207 — Consent for Expedited Final Hearing (Foreclosure)

**Form Number:** CV-207
**Fillable Fields:** 24
**Category:** Civil — Foreclosure
**Court:** Superior Court / District Court
**Related Forms:** CV-208

## Purpose

Defendant's consent to scheduling an expedited final hearing in a residential foreclosure case.

## Governing Law

- **14 M.R.S. § 6321-B (expedited final hearing in foreclosure)**

## Field Mapping Summary

### Page 0

| Field Name | Type | Source |
|-----------|------|--------|
| `Plaintiff` | Text | From matter data |
| `Superior Court` | CheckBox | `matter.court_type` |
| `District Court` | CheckBox | `matter.court_type` |
| `County` | Text | `matter.court_county` |
| `Defendant` | Text | From matter data |
| `Location Town` | Text | `matter.court_location` |
| `Docket No` | Text | `matter.docket_number` |
| `Iwe have consulted` | CheckBox | From matter data |
| `Iwe choose not to consult with an attorney or a housing counselor` | CheckBox | From matter data |
| `Date mmddyyyy` | Text | `today()` or relevant date |
| `undefined` | Text | From matter data |
| `Print Name` | Text | `signer.full_name` |
| `Date mmddyyyy_2` | Text | `today()` or relevant date |
| `undefined_2` | Text | From matter data |
| `Print Name_2` | Text | `signer.full_name` |
| `Date mmddyyyy_3` | Text | `today()` or relevant date |
| `undefined_3` | Text | From matter data |
| `Print Name_3` | Text | `signer.full_name` |
| `Date mmddyyyy_4` | Text | `today()` or relevant date |
| `undefined_4` | Text | From matter data |
| `Print Name_4` | Text | `signer.full_name` |
| `Date mmddyyyy_5` | Text | `today()` or relevant date |
| `undefined_5` | Text | From matter data |
| `Print Name_5` | Text | `signer.full_name` |


## AI Hints

Defendant signs to consent. Must indicate whether they consulted an attorney/housing counselor or chose not to. Space for up to 2 defendant signatures and 3 party-in-interest/plaintiff signatures with dates and printed names.

## Validation Checklist

- [ ] Case caption is complete (parties, court, docket number)
- [ ] Correct court type selected (Superior/District)
- [ ] Related forms prepared if needed (CV-208)
