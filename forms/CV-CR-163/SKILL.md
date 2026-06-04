<!-- Reused from prior skills stash; verify against schema.json. -->
# CV-CR-163 — Request for Protection on Trial List

**Form Number:** CV-CR-163
**Fillable Fields:** 34
**Category:** Civil/Criminal — Trial Scheduling
**Court:** Superior Court / District Court

## Purpose

Requests specific dates be protected (excluded) from the trial list due to scheduling conflicts.

## Field Mapping Summary

### Page 0

| Field Name | Type | Source |
|-----------|------|--------|
| `Name and Address of Court 1` | Text | `party.address` |
| `Name and Address of Court 2` | Text | `party.address` |
| `Name and Address of Court 3` | Text | `party.address` |
| `Name and Address of Court 4` | Text | `party.address` |
| `Text1` | Text | From matter data |
| `Text2` | Text | From matter data |
| `Plaintiff` | CheckBox | From matter data |
| `Defendant` | CheckBox | From matter data |
| `This case is scheduled for trial list beginning mmddyyyy` | Text | From matter data |
| `The parties good faith credible estimate of the time required for the trial is` | Text | From matter data |
| `Check Box3` | CheckBox | From matter data |
| `1` | Text | From matter data |
| `Reasons 1` | Text | From matter data |
| `Check Box4` | CheckBox | From matter data |
| `2` | Text | From matter data |
| `Reasons 2` | Text | From matter data |
| `Check Box5` | CheckBox | From matter data |
| `3` | Text | From matter data |
| `Reasons 3` | Text | From matter data |
| `Check Box6` | CheckBox | From matter data |
| `4` | Text | From matter data |
| `Reasons 4` | Text | From matter data |
| `Check Box7` | CheckBox | From matter data |
| `5` | Text | From matter data |
| `Reasons 5` | Text | From matter data |
| `Check Box8` | CheckBox | From matter data |
| `6` | Text | From matter data |
| `Reasons 6` | Text | From matter data |
| `Date mmddyyyy` | Text | `today()` or relevant date |
| `undefined_7` | Text | From matter data |
| *... +4 more fields* | | |


## AI Hints

34 fields. Up to 6 date/reason pairs for protection requests. Each request must be checked to be allowed. Court may reconsider disallowed requests if scheduling conflict becomes certain. Includes sections for attorney/party signature and judge's ruling. "DO NOT DOCKET" notice at bottom with court address for forwarding.

## Validation Checklist

- [ ] Case caption is complete (parties, court, docket number)
- [ ] Date is filled in (mm/dd/yyyy format)
- [ ] Signature line identified (leave blank for physical signature)
- [ ] Correct court type selected (Superior/District)
