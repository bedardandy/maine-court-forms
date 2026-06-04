<!-- Reused from prior skills stash; verify against schema.json. -->
# CR-CV-FM-260 — Motion for Alternative Format for Court Proceeding

**Form Number:** CR-CV-FM-260
**Fillable Fields:** 41
**Category:** Cross-Category — Procedural
**Court:** Superior Court / District Court / Unified Criminal Docket

## Purpose

Requests to change the format of a scheduled court appearance (e.g., from in-person to video/telephone or vice versa).

## Field Mapping Summary

### Page 0

| Field Name | Type | Source |
|-----------|------|--------|
| `Plaintiff` | Text | From matter data |
| `Defendant` | Text | From matter data |
| `Superior Court` | CheckBox | `matter.court_type` |
| `District Court` | CheckBox | `matter.court_type` |
| `Unified Criminal Docket` | CheckBox | `matter.docket_number` |
| `County` | Text | `matter.court_county` |
| `Location Town` | Text | `matter.court_location` |
| `Docket No` | Text | `matter.docket_number` |
| `I name` | Text | From matter data |
| `plaintiff` | CheckBox | From matter data |
| `defendant` | CheckBox | From matter data |
| `other` | CheckBox | From matter data |
| `in this matter am scheduled to appear at a court` | Text | From matter data |
| `proceeding on mmddyyyy` | Text | From matter data |
| `at` | Text | From matter data |
| `am` | CheckBox | From matter data |
| `pm` | CheckBox | From matter data |
| `in person at a courthouse` | CheckBox | From matter data |
| `by video` | CheckBox | From matter data |
| `by telephone` | CheckBox | `party.phone` |
| `in person at a courthouse_2` | CheckBox | From matter data |
| `by video_2` | CheckBox | From matter data |
| `by telephone_2` | CheckBox | `party.phone` |
| `My email address is` | Text | `party.email` |
| `My phone number is` | Text | `party.phone` |
| `I am requesting to change the format because if you need more space to write please attach another page 1` | Text | From matter data |

### Page 1

| Field Name | Type | Source |
|-----------|------|--------|
| `I have checked with the other partyies and they` | CheckBox | From matter data |
| `do have` | CheckBox | From matter data |
| `do not have an objection to this` | CheckBox | From matter data |
| `I have not checked with the other partyies to ask if there is an objection to this motion because I do` | CheckBox | From matter data |
| `I have checked with the other partyies and they_2` | CheckBox | From matter data |
| `do have_2` | CheckBox | From matter data |
| `do not have an objection to this_2` | CheckBox | From matter data |
| `Date mmddyyyy` | Text | `today()` or relevant date |
| `undefined` | Text | From matter data |
| `Attorney for` | CheckBox | From matter data |
| `plaintiff_2` | CheckBox | From matter data |
| `defendant_2` | CheckBox | From matter data |
| `undefined_2` | CheckBox | From matter data |
| `other_2` | Text | From matter data |
| `Bar No if applicable` | Text | `attorney.bar_number` |


## AI Hints

Two pages. Party indicates current scheduled format and requested format. Must state reason for change. Includes section for opposing party's position (object/no objection). Confidentiality note for family/PFA cases — use FM-057 or PA-015 instead of providing contact info on this form. Includes ORDER section for judge.

## Validation Checklist

- [ ] Case caption is complete (parties, court, docket number)
- [ ] Date is filled in (mm/dd/yyyy format)
- [ ] Signature line identified (leave blank for physical signature)
- [ ] Correct court type selected (Superior/District)
