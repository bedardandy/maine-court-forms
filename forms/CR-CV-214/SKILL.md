<!-- Reused from prior skills stash; verify against schema.json. -->
# CR-CV-214 — Request for Inclusion on Juror Source List

**Form Number:** CR-CV-214
**Fillable Fields:** 17
**Category:** Civil/Criminal — Jury
**Court:** Superior Court / Unified Criminal Docket

## Purpose

Allows a citizen to voluntarily request placement on the juror source list maintained by the Secretary of State for prospective juror selection.

## Governing Law

- **14 M.R.S. § 1252-A (juror source list)**
- **17-A M.R.S. § 453 (false statements penalty)**

## Field Mapping Summary

### Page 0

| Field Name | Type | Source |
|-----------|------|--------|
| `First` | Text | From matter data |
| `Middle` | Text | From matter data |
| `Last` | Text | From matter data |
| `Street or PO Box Number` | Text | From matter data |
| `City or Town` | Text | From matter data |
| `State` | Text | From matter data |
| `ZIP` | Text | From matter data |
| `Town` | Text | From matter data |
| `County` | Text | `matter.court_county` |
| `Month` | Text | From matter data |
| `Day` | Text | From matter data |
| `Year` | Text | From matter data |
| `Ft In` | Text | From matter data |
| `Lbs` | Text | From matter data |
| `Color` | Text | From matter data |
| `Color_2` | Text | From matter data |
| `Date mmddyyyy` | Text | `today()` or relevant date |


## AI Hints

Simple demographic form. No case caption needed. Physical characteristics (height, weight, hair, eyes) are collected for identification. Disqualification criteria: not a US citizen, under 18, not county resident, unable to read/speak/understand English.

## Validation Checklist

- [ ] Case caption is complete (parties, court, docket number)
- [ ] Date is filled in (mm/dd/yyyy format)
- [ ] Signature line identified (leave blank for physical signature)
- [ ] Correct court type selected (Superior/District)
