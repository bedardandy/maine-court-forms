# CV-208 — Request to Schedule Expedited Final Hearing (Foreclosure)

**Form Number:** CV-208
**Fillable Fields:** 12
**Category:** Civil — Foreclosure
**Court:** Superior Court / District Court
**Related Forms:** CV-207

## Purpose

Plaintiff's request to schedule an expedited final hearing in a residential foreclosure case after meeting statutory conditions.

## Governing Law

- **14 M.R.S. § 6321-B (expedited final hearing)**
- **14 M.R.S. § 6321-A (mediation in foreclosure)**
- **14 M.R.S. § 6322 (consent to expedited hearing)**

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
| `Mediation conducted pursuant to 14 MRS  6321A did not result in the settlement or dismissal` | CheckBox | From matter data |
| `The Defendant has not filed an answer to the complaint as provided by the Maine Rules of Civil` | CheckBox | From matter data |
| `Date mmddyyyy` | Text | `today()` or relevant date |
| `undefined` | Text | From matter data |
| `Print Name` | Text | `signer.full_name` |


## AI Hints

Two conditions (select one): (1) mediation didn't settle AND all appearing defendants consented (submit CV-207 with this form), or (2) defendant hasn't filed answer AND all appearing parties consented. Filed by plaintiff with CV-207 consent forms.

## Validation Checklist

- [ ] Case caption is complete (parties, court, docket number)
- [ ] Date is filled in (mm/dd/yyyy format)
- [ ] Signature line identified (leave blank for physical signature)
- [ ] Correct court type selected (Superior/District)
- [ ] Related forms prepared if needed (CV-207)
