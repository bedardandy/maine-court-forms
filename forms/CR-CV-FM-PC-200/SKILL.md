<!-- Reused from prior skills stash; verify against schema.json. -->
# CR-CV-FM-PC-200 — Social Security Number Confidential Disclosure Form

**Form Number:** CR-CV-FM-PC-200
**Fillable Fields:** 31
**Category:** Cross-Category — Administrative
**Court:** Superior Court / District Court / Unified Criminal Docket

## Purpose

Confidentially discloses Social Security numbers to the court. Required in certain case types.

## Field Mapping Summary

### Page 0

| Field Name | Type | Source |
|-----------|------|--------|
| `Plaintiffs` | Text | From matter data |
| `undefined` | Text | From matter data |
| `SuperiorCourt` | CheckBox | `matter.court_type` |
| `District Court` | CheckBox | `matter.court_type` |
| `UnifiedCriminalDocket` | CheckBox | `matter.docket_number` |
| `County` | Text | `matter.court_county` |
| `CourtLocationTown` | Text | `matter.court_location` |
| `Docket No` | Text | `matter.docket_number` |
| `Defendants` | Text | From matter data |
| `undefined_2` | Text | From matter data |
| `MySocial Securityaccountnumberis` | Text | From matter data |
| `undefined_3` | Text | From matter data |
| `undefined_4` | Text | From matter data |
| `Date mmddyyyy` | Text | `today()` or relevant date |
| `undefined_5` | Text | From matter data |
| `Plaintiff` | CheckBox | From matter data |
| `Defendant` | CheckBox | From matter data |
| `Childs NameRow1` | Text | From matter data |
| `SocialSecurityNumberRow1` | Text | From matter data |
| `Childs NameRow2` | Text | From matter data |
| `SocialSecurityNumberRow2` | Text | From matter data |
| `Childs NameRow3` | Text | From matter data |
| `SocialSecurityNumberRow3` | Text | From matter data |
| `Childs NameRow4` | Text | From matter data |
| `SocialSecurityNumberRow4` | Text | From matter data |
| `Childs NameRow5` | Text | From matter data |
| `SocialSecurityNumberRow5` | Text | From matter data |
| `Childs NameRow6` | Text | From matter data |
| `SocialSecurityNumberRow6` | Text | From matter data |
| `A ProtectiveCustodycaseiscurrentlypending TheCourtDocketNumber` | CheckBox | `matter.docket_number` |
| *... +1 more fields* | | |


## AI Hints

Contains NONPUBLIC DIGITAL INFORMATION. SSN format: XXX-XX-XXXX. Family matter cases require disclosure of children's SSNs. Includes Protective Custody case pending indicator. Form is confidential and not disclosed unless court-ordered.

## Validation Checklist

- [ ] Case caption is complete (parties, court, docket number)
- [ ] Correct court type selected (Superior/District)
