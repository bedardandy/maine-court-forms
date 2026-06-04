<!-- Reused from prior skills stash; verify against schema.json. -->
# PA-033 — Affidavit and Request to Register a Foreign

**Form Number:** PA-033, Rev. 01/23
**Pages:** 2
**Fillable Fields:** 42
**Category:** Protection from Abuse/Harassment
**Court:** District Court

## Purpose

This is a court order form used in protection from abuse/harassment cases. Typically completed by the court or prepared by counsel for judicial signature.

## Governing Law

- **14 M.R.S. §§ 8001**

## Field Mappings

| Field Name | Type | Page | Notes |
|-----------|------|------|-------|
| `PlaintiffPetitioner` | Text | 1 |  |
| `DefendantRespondent` | Text | 1 |  |
| `Location Town` | Text | 1 | Court location |
| `Docket No` | Text | 1 | Court docket number |
| `plaintiffpetitioner` | CheckBox | 1 | Check if applicable |
| `defendantrespondent in a protection order case from name of state` | CheckBox | 1 | Defendant's name |
| `undefined` | Text | 1 |  |
| `Mailing Address 1` | Text | 1 | Mailing/street address |
| `Mailing Address 2` | Text | 1 | Mailing/street address |
| `Mailing Address 3` | Text | 1 | Mailing/street address |
| `Physical Address 1` | Text | 1 | Mailing/street address |
| `if different` | Text | 1 |  |
| `Physical Address 2` | Text | 1 | Mailing/street address |
| `Mailing Address 1_2` | Text | 1 | Mailing/street address |
| `Mailing Address 2_2` | Text | 1 | Mailing/street address |
| `Mailing Address 3_2` | Text | 1 | Mailing/street address |
| `Physical Address 1_2` | Text | 1 | Mailing/street address |
| `if different_2` | Text | 1 |  |
| `Physical Address 2_2` | Text | 1 | Mailing/street address |
| `A copy of the foreign protection order to be registered including any modification of the order as well as an` | CheckBox | 1 | Check if applicable |
| `and that it be placed on file with this Court` | CheckBox | 2 | Check if applicable |
| `and with the` | Text | 2 |  |
| `Registration only or` | CheckBox | 2 | Check if applicable |
| `Enforcement` | CheckBox | 2 | Check if applicable |
| `I swear under penalty of perjury that the above statements are true and correct I understand that these statements` | CheckBox | 2 | Check if applicable |
| `Date mmddyyyy` | Text | 2 | MM/DD/YYYY format |
| `undefined_2` | Text | 2 |  |
| `plaintiffpetitioner_2` | CheckBox | 2 | Check if applicable |
| `defendantrespondent` | CheckBox | 2 | Check if applicable |
| `Attorney` | Text | 2 |  |
| `Address 1` | Text | 2 | Mailing/street address |
| `Address 2` | Text | 2 | Mailing/street address |
| `Address 3` | Text | 2 | Mailing/street address |
| `Telephone` | Text | 2 | Phone number |
| `Email` | Text | 2 | Email address |
| `Name` | Text | 2 |  |
| `Address is confidential if so leave blank below` | CheckBox | 2 | Mailing/street address |
| `Address 1_2` | Text | 2 | Mailing/street address |
| `Address 2_2` | Text | 2 | Mailing/street address |
| `Telephone_2` | Text | 2 | Phone number |
| `Email_2` | Text | 2 | Email address |
| `Personally appeared the abovenamed` | Text | 2 |  |

## AI Hints

- **Safety First**: Protection orders are time-sensitive. Temporary orders may issue ex parte.
- **Confidentiality**: Plaintiff addresses may be kept confidential (safe address program).
- **Companion Forms**: PA-005 (Confidential Sheet) must be filed with complaint.
- **Docket Number**: Leave blank for new filings; clerk assigns. Enter if responding to existing case.

## Validation Checklist

- [ ] All required party names are filled in
- [ ] Court location/county is correct for venue
- [ ] Docket number included (if existing case)
- [ ] All dates are in correct format (MM/DD/YYYY)
- [ ] Contact information is complete
- [ ] PA-005 Confidential Sheet attached
- [ ] Safety considerations documented

## Related Forms

- **PA-001** — Complaint for Protection from Abuse
- **PA-005** — Protection Order Service Information
- **PA-006** — Complaint for Protection from Harassment
- **PA-010** — Defendant’s Motion to Dissolve/Modify/Amend
- **PA-012** — Plaintiff’s Pre-Judgment Motion to
- **PA-013** — Plaintiff’s Motion to Extend Order for Protection
- **PA-015** — Affidavit of Confidential Address
- **PA-022** — Post-Judgment Motion to Modify/Extinguish
- **PA-024** — Notice of Relinquishment of Weapons to Be
- **PA-025** — Notice of Relinquishment to Be Completed by

> **Note:** a dedicated fill recipe exists for this form in `engine/recipes/`. The recipe is the authoritative field mapping; this doc is the human-readable companion.
