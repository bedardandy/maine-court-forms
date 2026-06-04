<!-- Reused from prior skills stash; verify against schema.json. -->
# PA-015 — Affidavit of Confidential Address

**Form Number:** PA-015, Rev. 01/23
**Pages:** 2
**Fillable Fields:** 38
**Category:** Protection from Abuse/Harassment
**Court:** District Court

## Purpose

This affidavit form provides sworn testimony in support of a protection from abuse/harassment matter.

## Governing Law

- **19-A M.R.S. § 4112**
- **5 M.R.S. § 4656**

## Field Mappings

| Field Name | Type | Page | Notes |
|-----------|------|------|-------|
| `Plaintiff` | Text | 1 |  |
| `individually and on behalf of` | CheckBox | 1 | Check if applicable |
| `1` | Text | 1 |  |
| `2` | Text | 1 |  |
| `on behalf of` | CheckBox | 1 | Check if applicable |
| `1_2` | Text | 1 |  |
| `2_2` | Text | 1 |  |
| `Defendant` | Text | 1 |  |
| `on behalf of_2` | CheckBox | 1 | Check if applicable |
| `undefined` | Text | 1 |  |
| `Location Town` | Text | 1 | Court location |
| `Docket No` | Text | 1 | Court docket number |
| `plaintiff` | CheckBox | 1 | Check if applicable |
| `defendant in this case and I request that the court keep the following information confidential` | CheckBox | 1 | Check if applicable |
| `Physical address` | CheckBox | 1 | Mailing/street address |
| `1_3` | Text | 1 |  |
| `Mailing address` | CheckBox | 1 | Mailing/street address |
| `2_3` | Text | 1 |  |
| `Email address` | CheckBox | 1 | Email address |
| `Telephone number` | Text | 1 | Phone number |
| `Cell` | CheckBox | 1 | Check if applicable |
| `undefined_2` | Text | 1 |  |
| `Home` | CheckBox | 1 | Check if applicable |
| `undefined_3` | Text | 1 |  |
| `Work` | CheckBox | 1 | Check if applicable |
| `undefined_4` | Text | 1 |  |
| `Other` | CheckBox | 1 | Check if applicable |
| `undefined_5` | Text | 1 |  |
| `undefined_6` | Text | 1 |  |
| `information for the following reasons 1` | Text | 1 |  |
| `information for the following reasons 2` | Text | 1 |  |
| `information for the following reasons 3` | Text | 1 |  |
| `information for the following reasons 4` | Text | 1 |  |
| `I swear under penalty of perjury that the above statements are true and correct I understand that these statements are` | CheckBox | 1 | Check if applicable |
| `Date mmddyyyy` | Text | 1 | MM/DD/YYYY format |
| `undefined_7` | Text | 1 |  |
| `plaintiff_2` | CheckBox | 1 | Check if applicable |
| `defendant` | CheckBox | 1 | Check if applicable |

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
- **PA-022** — Post-Judgment Motion to Modify/Extinguish
- **PA-024** — Notice of Relinquishment of Weapons to Be
- **PA-025** — Notice of Relinquishment to Be Completed by
- **PA-026** — Information Regarding the Relinquishment of

> **Note:** a dedicated fill recipe exists for this form in `engine/recipes/`. The recipe is the authoritative field mapping; this doc is the human-readable companion.
