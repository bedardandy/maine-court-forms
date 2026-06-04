<!-- Reused from prior skills stash; verify against schema.json. -->
# CV-267 — Affidavit and Request for Issuance of Subpoena Under UIDDA

**Form Number:** CV-267
**Fillable Fields:** 32
**Category:** Civil — Interstate Discovery
**Court:** Superior Court / District Court

## Purpose

Requests issuance of a Maine subpoena for use in an out-of-state case under the Uniform Interstate Depositions and Discovery Act.

## Governing Law

- **14 M.R.S. §§ 401-408 (UIDDA)**

## Field Mapping Summary

### Page 0

| Field Name | Type | Source |
|-----------|------|--------|
| `Plaintiff` | Text | From matter data |
| `Defendant` | Text | From matter data |
| `Superior Court` | CheckBox | `matter.court_type` |
| `District Court` | CheckBox | `matter.court_type` |
| `County` | Text | `matter.court_county` |
| `undefined` | Text | From matter data |
| `Location Town` | Text | `matter.court_location` |
| `I am a party or` | CheckBox | From matter data |
| `I represent a party in a case pending in a jurisdiction outside of the State of Maine I am` | CheckBox | From matter data |
| `Courtjurisdiction in which the underlying case is pending` | Text | From matter data |
| `Parties in underlying case` | Text | From matter data |
| `Docket Number of the underlying case` | Text | `matter.docket_number` |
| `needed list additional counsel and addresstelephone numbers on an attachment and note see attachment 1` | Text | `party.phone` |
| `counsel and addresstelephone numbers on an attachment and note see attachment 1` | Text | `party.phone` |

### Page 1

| Field Name | Type | Source |
|-----------|------|--------|
| `deposition` | CheckBox | From matter data |
| `inspection of documents andor` | CheckBox | From matter data |
| `inspection of premises` | CheckBox | From matter data |
| `Name of deponent andor custodian of the documents 1` | Text | From matter data |
| `Date mmddyyyy and time of the depositioninspection 1` | Text | `today()` or relevant date |
| `Location of depositioninspection 1` | Text | From matter data |
| `True` | CheckBox | From matter data |
| `False` | CheckBox | From matter data |

### Page 2

| Field Name | Type | Source |
|-----------|------|--------|
| `I swear under penalty of perjury that the above statements are true and correct I understand that these` | CheckBox | From matter data |
| `Date mmddyyyy` | Text | `today()` or relevant date |
| `undefined_2` | Text | From matter data |
| `Printed Name` | Text | `signer.full_name` |
| `Maine Bar No if applicable` | Text | `attorney.bar_number` |
| `Mailing Address 1` | Text | `party.address` |
| `Mailing Address 2` | Text | `party.address` |
| `Mailing Address 3` | Text | `party.address` |
| `County_2` | Text | `matter.court_county` |
| `Personally appeared the abovenamed` | Text | From matter data |


## AI Hints

32 fields, 3 pages. Filed by party or representative in out-of-state case. Specifies: originating court, parties, docket number, requesting counsel info, subpoena type (deposition, document inspection, premises inspection), deponent/custodian info. Includes sections for objection notice and issuance instructions per M.R. Civ. P. 45.

## Validation Checklist

- [ ] Case caption is complete (parties, court, docket number)
- [ ] Date is filled in (mm/dd/yyyy format)
- [ ] Signature line identified (leave blank for physical signature)
- [ ] Correct court type selected (Superior/District)
