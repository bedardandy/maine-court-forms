# CV-266 — Affidavit and Request to Register a Foreign State Money Judgment Under UEFJA

**Form Number:** CV-266
**Fillable Fields:** 40
**Category:** Civil — Foreign Judgments
**Court:** Superior Court / District Court

## Purpose

Registers a money judgment from another US state in Maine under the Uniform Enforcement of Foreign Judgments Act.

## Governing Law

- **14 M.R.S. §§ 8001-8008 (UEFJA)**

## Field Mapping Summary

### Page 0

| Field Name | Type | Source |
|-----------|------|--------|
| `PlaintiffPetitioner` | Text | From matter data |
| `DefendantPetitioner` | Text | From matter data |
| `Superior Court` | CheckBox | `matter.court_type` |
| `District Court` | CheckBox | `matter.court_type` |
| `County` | Text | `matter.court_county` |
| `Location Town` | Text | `matter.court_location` |
| `Docket No` | Text | `matter.docket_number` |
| `This is a request to register a judgment in a case from name of state` | Text | From matter data |
| `The judgment is a money judgment or` | CheckBox | From matter data |
| `The judgment is not a money judgment Type of case` | CheckBox | From matter data |
| `undefined` | Text | From matter data |
| `Mailing Address 1` | Text | `party.address` |
| `Mailing Address 2` | Text | `party.address` |
| `Mailing Address 3` | Text | `party.address` |
| `Phone Number` | Text | `party.phone` |
| `Physical Address 1` | Text | `party.address` |
| `if different` | Text | From matter data |
| `Physical Address 2` | Text | `party.address` |
| `Email` | Text | `party.email` |
| `Mailing Address 1_2` | Text | `party.address` |
| `Mailing Address 2_2` | Text | `party.address` |
| `Mailing Address 3_2` | Text | `party.address` |
| `Phone Number_2` | Text | `party.phone` |
| `Physical Address 1_2` | Text | `party.address` |
| `if different_2` | Text | From matter data |
| `Physical Address 2_2` | Text | `party.address` |
| `Email_2` | Text | `party.email` |
| `Two copies of the foreign judgment to be registered are attached I certify that the attached foreign` | CheckBox | From matter data |

### Page 1

| Field Name | Type | Source |
|-----------|------|--------|
| `I swear under penalty of perjury that the above statements are true and correct I understand that these` | CheckBox | From matter data |
| `Date mmddyyyy` | Text | `today()` or relevant date |
| `undefined_2` | Text | From matter data |
| `attorney for` | CheckBox | From matter data |
| `plaintiffpetitioner` | CheckBox | From matter data |
| `defendantrespondent` | CheckBox | From matter data |
| `Printed Name and Maine Bar No if applicable` | Text | `attorney.bar_number` |
| `County_2` | Text | `matter.court_county` |
| `Personally appeared the abovenamed` | Text | From matter data |
| `Attorney at Law` | CheckBox | From matter data |
| `Notary Public` | CheckBox | From matter data |
| `Clerk` | CheckBox | From matter data |


## AI Hints

40 fields, 2 pages. Party maintains same role as in original case. Must provide addresses for both parties. Requires 2 certified copies of foreign judgment. Sworn affidavit with perjury warning. Includes ORDER section for court clerk to set hearing date and notice requirements.

## Validation Checklist

- [ ] Case caption is complete (parties, court, docket number)
- [ ] Date is filled in (mm/dd/yyyy format)
- [ ] Signature line identified (leave blank for physical signature)
- [ ] Correct court type selected (Superior/District)
