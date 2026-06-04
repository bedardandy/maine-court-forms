<!-- Reused from prior skills stash; verify against schema.json. -->
# JV-006-W — Conditions of Release

**Form Number:** JV-006-W, Rev. 10/21
**Pages:** 2
**Fillable Fields:** 60
**Category:** Juvenile
**Court:** District Court / Juvenile Division

## Purpose

Form used in juvenile proceedings in Maine court.

## Governing Law

- **15 M.R.S. § 3203-A**

## Field Mappings

| Field Name | Type | Page | Notes |
|-----------|------|------|-------|
| `V` | Text | 1 |  |
| `undefined` | Text | 1 |  |
| `Location Town` | Text | 1 | Court location |
| `at any time required by court` | CheckBox | 1 | Check if applicable |
| `on mmddyyyy` | CheckBox | 1 | Check if applicable |
| `juvenile is released pending further court proceedings on the condition that the juvenile` | Text | 1 |  |
| `Appear in court` | Text | 1 |  |
| `am` | CheckBox | 1 | Check if applicable |
| `pm and commit no illegal act whatsoever including but not limited to the use or` | CheckBox | 1 | Check if applicable |
| `Reside with parentsguardianlegal custodian and abide by all rules of that residence` | CheckBox | 1 | Check if applicable |
| `Reside with` | CheckBox | 1 | Check if applicable |
| `at` | Text | 1 |  |
| `and abide by` | Text | 1 |  |
| `Child support order attached` | CheckBox | 1 | Check if applicable |
| `Abide by curfew` | CheckBox | 1 | Check if applicable |
| `Everyday` | CheckBox | 1 | Check if applicable |
| `Weekdays from` | CheckBox | 1 | Check if applicable |
| `pm until` | Text | 1 |  |
| `am_2` | Text | 1 |  |
| `Fridays and Saturdays from` | CheckBox | 1 | Check if applicable |
| `undefined_2` | Text | 1 |  |
| `pm until_2` | Text | 1 |  |
| `accompanied by a parent or other legallyappointed supervisor` | CheckBox | 1 | Check if applicable |
| `attending a school function` | CheckBox | 1 | Check if applicable |
| `at employment or in transit to or from employment` | CheckBox | 1 | Check if applicable |
| `Or as set or modified by the juveniles JCCO` | CheckBox | 1 | Check if applicable |
| `House Arrest May not be away from home without parentsguardianlegal custodian or` | CheckBox | 1 | Check if applicable |
| `except` | Text | 1 |  |
| `to go directly to and from school` | CheckBox | 1 | Check if applicable |
| `to go directly to and from employment` | CheckBox | 1 | Check if applicable |
| `24hour adult supervision both in and outside of the home by` | CheckBox | 1 | Check if applicable |
| `1` | Text | 1 |  |
| `Other` | CheckBox | 1 | Check if applicable |
| `2` | Text | 1 |  |
| `Attend school regularly or pursue school or alternative education enrollment and attend school program` | CheckBox | 2 | Check if applicable |
| `Maintain regular employment or regularly pursue employment` | CheckBox | 2 | Check if applicable |
| `Submit to any request for any personal search or test for possession or use of drugs or alcohol` | CheckBox | 2 | Check if applicable |
| `Have no contact of any kind with` | CheckBox | 2 | Check if applicable |
| `undefined_3` | Text | 2 |  |
| `1_2` | Text | 2 |  |
| `except incidental contact at` | CheckBox | 2 | Check if applicable |
| `school` | CheckBox | 2 | Check if applicable |
| `work` | CheckBox | 2 | Check if applicable |
| `other as may be necessary to` | CheckBox | 2 | Check if applicable |
| `undefined_4` | Text | 2 |  |
| `2_2` | Text | 2 |  |
| `When available participate in regular` | CheckBox | 2 | Check if applicable |
| `medical treatment` | CheckBox | 2 | Check if applicable |
| `counseling with` | CheckBox | 2 | Check if applicable |
| `undefined_5` | Text | 2 |  |
| `Text1` | Text | 2 |  |
| `outpatient` | CheckBox | 2 | Check if applicable |
| `inpatient at` | CheckBox | 2 | Check if applicable |
| `and take all prescribed medication` | Text | 2 |  |
| `Do not use or possess any dangerous weapons or firearms` | CheckBox | 2 | Check if applicable |
| `Report to JCCO as directed by the JCCO or Court` | CheckBox | 2 | Check if applicable |
| `Consent to electronic monitoring by cell phone` | CheckBox | 2 | Phone number |
| `Other_2` | CheckBox | 2 | Check if applicable |
| `1_3` | Text | 2 |  |
| `Date mmddyyyy` | Text | 2 | MM/DD/YYYY format |

## AI Hints

- **Confidentiality**: Juvenile records are confidential. Use initials only.
- **Diversion**: Consider whether diversion programs apply before formal proceedings.
- **Guardian ad Litem**: Court may appoint GAL for the juvenile.

## Validation Checklist

- [ ] All required party names are filled in
- [ ] Court location/county is correct for venue
- [ ] All dates are in correct format (MM/DD/YYYY)

## Related Forms

- **JV-002-W** — Juvenile Summons
- **JV-005** — PETITION FOR REVIEW OF DETENTION OF JUVENILE AND ORDER
- **JV-008-W** — ORDERED: These conditions are made part of the judgment
- **JV-009-W** — Notice to Parents and Legal Guardians
- **JV-010-W** — Notice to Juvenile of Right to Appeal to the Law Court
- **JV-011-W** — Notice to Parent, Guardian, or Legal Custodian
- **JV-012** — Notice of Appeal to the Law Court
- **JV-016-W** — HEARING NOTICE TO PARENTS/GUARDIAN/LEGAL CUSTODIAN
- **JV-017** — Waiver of Notice
- **JV-020** — Important Notice

> **Note:** a dedicated fill recipe exists for this form in `engine/recipes/`. The recipe is the authoritative field mapping; this doc is the human-readable companion.
