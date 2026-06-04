<!-- Reused from prior skills stash; verify against schema.json. -->
# CV-FM-203 — Request for Hearing (Foreign Order Registration)

**Form Number:** CV-FM-203
**Fillable Fields:** 23
**Category:** Civil/Family — Interstate
**Court:** Superior Court / District Court

## Purpose

Non-registering party's request for hearing to contest the validity or enforcement of a registered foreign state order (support, custody, or judgment).

## Governing Law

- **19-A M.R.S. § 3201 (UIFSA — Uniform Interstate Family Support Act)**
- **19-A M.R.S. § 1765 (UCCJEA — Uniform Child Custody Jurisdiction and Enforcement Act)**
- **14 M.R.S. § 8004 (UEFJA)**

## Field Mapping Summary

### Page 0

| Field Name | Type | Source |
|-----------|------|--------|
| `PlaintiffPetitioner` | Text | From matter data |
| `Superior Court` | CheckBox | `matter.court_type` |
| `District Court` | CheckBox | `matter.court_type` |
| `County` | Text | `matter.court_county` |
| `undefined` | Text | From matter data |
| `Location Town` | Text | `matter.court_location` |
| `V` | Text | From matter data |
| `UIFSA  19A MRS  3201 UCCJEA  19A MRS  1765 UEFJA  14 MRS  8004` | Text | From matter data |
| `I wish to contest the validity andor enforcement of the Order including any alleged arrearages money owed and` | Text | From matter data |
| `request a hearing for the following reasons 1` | Text | From matter data |
| `request a hearing for the following reasons 2` | Text | From matter data |
| `request a hearing for the following reasons 3` | Text | From matter data |
| `request a hearing for the following reasons 4` | Text | From matter data |
| `I am requesting that I be allowed to participate in this matter` | CheckBox | From matter data |
| `by telephone` | CheckBox | `party.phone` |
| `by video conference because of` | CheckBox | From matter data |
| `undefined_2` | Text | From matter data |
| `the following reasons 1` | Text | From matter data |
| `the following reasons 2` | Text | From matter data |
| `Date mmddyyyy` | Text | `today()` or relevant date |
| `I understand that I must send a copy of this request to the party seeking to register the Order in the State of Maine` | Text | From matter data |
| `plaintiffpetitioner` | CheckBox | From matter data |
| `defendantrespondent` | CheckBox | From matter data |


## AI Hints

23 fields. Party contests registered order and requests hearing with reasons. Can request telephone or video participation. Must send copy to registering party. Includes ORDER section (grant/deny) with hearing date/time.

## Validation Checklist

- [ ] Case caption is complete (parties, court, docket number)
- [ ] Date is filled in (mm/dd/yyyy format)
- [ ] Signature line identified (leave blank for physical signature)
- [ ] Correct court type selected (Superior/District)
