<!-- Reused from prior skills stash; verify against schema.json. -->
# CR-CV-FM-JV-PA-PC-286 — Motion to Continue

**Form Number:** CR-CV-FM-JV-PA-PC-286
**Fillable Fields:** 54
**Category:** Cross-Category — Procedural
**Court:** Superior Court / District Court / Unified Criminal Docket

## Purpose

Requests postponement (continuance) of a scheduled court event to a later date.

## Governing Law

- **M.R. Civ. P. 40 (assignment of cases)**
- **M.R.U. Crim. P. 25A (continuances)**

## Field Mapping Summary

### Page 0

| Field Name | Type | Source |
|-----------|------|--------|
| `Plaintiff` | Text | From matter data |
| `Defendant` | Text | From matter data |
| `Other Party if any` | Text | From matter data |
| `Superior Court` | CheckBox | `matter.court_type` |
| `District Court` | CheckBox | `matter.court_type` |
| `Unified Criminal Docket` | CheckBox | `matter.docket_number` |
| `County` | Text | `matter.court_county` |
| `Location Town` | Text | `matter.court_location` |
| `Docket No` | Text | `matter.docket_number` |
| `plaintiffpetitioner` | CheckBox | From matter data |
| `defendantrespondent` | CheckBox | From matter data |
| `other name` | CheckBox | From matter data |
| `and I ask the court to continue postpone or change to a later date the following court event` | Text | From matter data |
| `Type of court event for example arraignment case management conference motion hearing etc` | Text | From matter data |
| `b Scheduled for mmddyyyy` | Text | From matter data |
| `at` | Text | From matter data |
| `am` | CheckBox | From matter data |
| `pm` | CheckBox | From matter data |
| `Check Box2` | CheckBox | From matter data |
| `weeks` | Text | From matter data |
| `Check Box3` | CheckBox | From matter data |
| `months` | Text | From matter data |
| `other` | CheckBox | From matter data |
| `undefined_2` | Text | From matter data |
| `I am asking for a continuance for medical reasons I have attached a separate sheet explaining the` | CheckBox | From matter data |
| `I am not asking for a continuance for medical reasons I am asking because attach more pages if` | CheckBox | From matter data |
| `needed 1` | Text | From matter data |
| `needed 2` | Text | From matter data |
| `needed 3` | Text | From matter data |
| `needed 4` | Text | From matter data |
| *... +4 more fields* | | |

### Page 1

| Field Name | Type | Source |
|-----------|------|--------|
| `I was able to find out if the other partyparties object` | CheckBox | From matter data |
| `Name` | Text | From matter data |
| `does not` | CheckBox | From matter data |
| `does object to this motion` | CheckBox | From matter data |
| `Name_2` | Text | From matter data |
| `does not_2` | CheckBox | From matter data |
| `does object to this motion_2` | CheckBox | From matter data |
| `I was not able to find out if the other party name` | CheckBox | From matter data |
| `undefined_3` | Text | From matter data |
| `objects or not because 1` | Text | From matter data |
| `objects or not because 2` | Text | From matter data |
| `objects or not because 3` | Text | From matter data |
| `Date mmddyyyy` | Text | `today()` or relevant date |
| `undefined_4` | Text | From matter data |
| `attorney for` | CheckBox | From matter data |
| `plaintiff` | CheckBox | From matter data |
| `defendant` | CheckBox | From matter data |
| `other_2` | CheckBox | From matter data |
| `undefined_5` | Text | From matter data |
| `Printed name and Bar No if applicable` | Text | `attorney.bar_number` |


## AI Hints

Two-page form. Specifies type of court event, scheduled date, requested delay (weeks/months/other). Reasons: medical (kept confidential) or non-medical. Must indicate whether opposing party objects. Includes certificate of service and ORDER section. Page 2 has additional space and opposing party response section.

## Validation Checklist

- [ ] Case caption is complete (parties, court, docket number)
- [ ] Date is filled in (mm/dd/yyyy format)
- [ ] Signature line identified (leave blank for physical signature)
- [ ] Correct court type selected (Superior/District)
