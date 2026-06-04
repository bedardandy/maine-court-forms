<!-- Reused from prior skills stash; verify against schema.json. -->
# PA-005 — Protection Order Service Information

**Form Number:** PA-005, Rev. 09/25
**Pages:** 1
**Fillable Fields:** 54
**Category:** Protection from Abuse/Harassment
**Court:** District Court

## Purpose

This is a court order form used in protection from abuse/harassment cases. Typically completed by the court or prepared by counsel for judicial signature.

## Governing Law

- **19-A M.R.S. §§ 4101-4116** — Primary statutory authority

## Field Mappings

| Field Name | Type | Page | Notes |
|-----------|------|------|-------|
| `Defendants Name` | Text | 1 | Defendant's name |
| `Home Address` | Text | 1 | Mailing/street address |
| `Apartment number andor floor` | Text | 1 |  |
| `Color of house or other description` | Text | 1 |  |
| `If living with another person other persons name` | Text | 1 |  |
| `Telephone homeworkcell` | Text | 1 | Phone number |
| `Hours defendant will most likely be at home` | Text | 1 |  |
| `Name of Employer` | Text | 1 |  |
| `Work Address` | Text | 1 | Mailing/street address |
| `Mon` | CheckBox | 1 | Check if applicable |
| `Tues` | CheckBox | 1 | Check if applicable |
| `Wed` | CheckBox | 1 | Check if applicable |
| `Thurs` | CheckBox | 1 | Check if applicable |
| `Fri` | CheckBox | 1 | Check if applicable |
| `Sat` | CheckBox | 1 | Check if applicable |
| `Sun` | CheckBox | 1 | Check if applicable |
| `Hours Worked` | Text | 1 |  |
| `AM` | CheckBox | 1 | Check if applicable |
| `PHYSICAL DESCRIPTION If known` | CheckBox | 1 | Check if applicable |
| `PM to` | Text | 1 |  |
| `AM_2` | CheckBox | 1 | Check if applicable |
| `PM` | CheckBox | 1 | Check if applicable |
| `Birth Date mmddyyyy or approximate age` | Text | 1 | MM/DD/YYYY format |
| `Height` | Text | 1 |  |
| `Weight` | Text | 1 |  |
| `Hair Color` | Text | 1 |  |
| `Eye Color` | Text | 1 |  |
| `Gender` | Text | 1 |  |
| `White` | CheckBox | 1 | Check if applicable |
| `Black` | CheckBox | 1 | Check if applicable |
| `Asian or Pacific Islander` | CheckBox | 1 | Check if applicable |
| `American IndianAlaskan Native` | CheckBox | 1 | Check if applicable |
| `Other` | CheckBox | 1 | Check if applicable |
| `Make and Year yyyy` | Text | 1 |  |
| `TypeModel` | Text | 1 |  |
| `Color` | Text | 1 |  |
| `Registration No and State 1` | Text | 1 |  |
| `Registration No and State 2` | Text | 1 |  |
| `anyone who can help the serving officer locate the defendant 1` | Text | 1 |  |
| `Does the defendant own a firearm or other weapon` | RadioButton | 1 |  |
| `Does the defendant own a firearm or other weapon` | RadioButton | 1 |  |
| `Describe the weapons` | Text | 1 |  |
| `describe the location of the weapons ie under the bed if known` | Text | 1 | Court location |
| `Text1` | Text | 1 |  |
| `Does the defendant have a history of violence` | Text | 1 |  |
| `Is there anything else the serving officer should know about the defendant 1` | Text | 1 |  |
| `Is there anything else the serving officer should know about the defendant 2` | Text | 1 |  |
| `No_2` | CheckBox | 1 | Check if applicable |
| `I do not know` | CheckBox | 1 | Check if applicable |
| `undefined` | CheckBox | 1 | Check if applicable |
| `undefined_2` | Text | 1 |  |
| `Plaintiffs Name` | Text | 1 | Plaintiff's name |
| `Address unless confidential` | Text | 1 | Mailing/street address |
| `Telephone homeworkcell unless confidential` | Text | 1 | Phone number |

## AI Hints

- **Safety First**: Protection orders are time-sensitive. Temporary orders may issue ex parte.
- **Confidentiality**: Plaintiff addresses may be kept confidential (safe address program).
- **Companion Forms**: PA-005 (Confidential Sheet) must be filed with complaint.

## Validation Checklist

- [ ] All required party names are filled in
- [ ] Court location/county is correct for venue
- [ ] All dates are in correct format (MM/DD/YYYY)
- [ ] Contact information is complete
- [ ] PA-005 Confidential Sheet attached
- [ ] Safety considerations documented

## Related Forms

- **PA-001** — Complaint for Protection from Abuse
- **PA-006** — Complaint for Protection from Harassment
- **PA-010** — Defendant’s Motion to Dissolve/Modify/Amend
- **PA-012** — Plaintiff’s Pre-Judgment Motion to
- **PA-013** — Plaintiff’s Motion to Extend Order for Protection
- **PA-015** — Affidavit of Confidential Address
- **PA-022** — Post-Judgment Motion to Modify/Extinguish
- **PA-024** — Notice of Relinquishment of Weapons to Be
- **PA-025** — Notice of Relinquishment to Be Completed by
- **PA-026** — Information Regarding the Relinquishment of

> **Note:** a dedicated fill recipe exists for this form in `engine/recipes/`. The recipe is the authoritative field mapping; this doc is the human-readable companion.
