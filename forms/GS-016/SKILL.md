<!-- Reused from prior skills stash; verify against schema.json. -->
# GS-016 — Child Support Affidavit

**Form Number:** GS-016, Rev. 10/19
**Pages:** 3
**Fillable Fields:** 90
**Category:** Guardianship
**Court:** Probate Court / District Court

## Purpose

Form used in guardianship proceedings in Maine court.

## Governing Law

- **18-C M.R.S. § 5**
- **19-A M.R.S. § 2004**

## Field Mappings

| Field Name | Type | Page | Notes |
|-----------|------|------|-------|
| `Location` | Text | 1 | Court location |
| `Docket No_2` | Text | 1 | Court docket number |
| `IN RE` | Text | 1 |  |
| `Name` | Text | 1 |  |
| `Date of birth` | Text | 1 | MM/DD/YYYY format |
| `Address` | Text | 1 | Mailing/street address |
| `Employer Name` | Text | 1 |  |
| `Selfemployed` | CheckBox | 1 | Check if applicable |
| `Address_2` | Text | 1 | Mailing/street address |
| `Required I have attached copies of my most recent W2 form and two 2 pay stubs or tax` | CheckBox | 1 | Check if applicable |
| `A How much did you earn last year` | Text | 1 |  |
| `Salary and wages gross pay` | Text | 1 |  |
| `every` | CheckBox | 1 | Check if applicable |
| `week` | CheckBox | 1 | Check if applicable |
| `biweekly` | CheckBox | 1 | Check if applicable |
| `month` | CheckBox | 1 | Check if applicable |
| `undefined` | CheckBox | 1 | Check if applicable |
| `other` | Text | 1 |  |
| `Hourly wage` | Text | 1 |  |
| `and number of hours worked` | Text | 1 |  |
| `week_2` | CheckBox | 1 | Check if applicable |
| `biweekly_2` | CheckBox | 1 | Check if applicable |
| `month_2` | CheckBox | 1 | Check if applicable |
| `undefined_2` | CheckBox | 1 | Check if applicable |
| `other_2` | Text | 1 |  |
| `1B` | Text | 1 |  |
| `undefined_3` | Text | 1 |  |
| `undefined_4` | Text | 1 |  |
| `undefined_5` | Text | 1 |  |
| `undefined_6` | Text | 1 |  |
| `undefined_7` | Text | 1 |  |
| `undefined_8` | Text | 1 |  |
| `undefined_9` | Text | 1 |  |
| `undefined_10` | Text | 1 |  |
| `undefined_11` | Text | 1 |  |
| `Other` | Text | 1 |  |
| `undefined_12` | Text | 1 |  |
| `2` | Text | 1 |  |
| `3` | Text | 1 |  |
| `4` | Text | 2 |  |
| `5` | Text | 2 |  |
| `Name of child 1` | Text | 2 |  |
| `Name of child 2` | Text | 2 |  |
| `To whom paid 1` | Text | 2 |  |
| `To whom paid 2` | Text | 2 |  |
| `Amount 1` | Text | 2 |  |
| `Amount 2` | Text | 2 |  |
| `Required I have attached a copy of my health insurance premium sheet` | CheckBox | 2 | Check if applicable |
| `A Cost of health insurance for yourself only` | Text | 2 |  |
| `6B` | Text | 2 |  |
| `Required I have attached a copy of documentation showing the cost of child care` | CheckBox | 2 | Check if applicable |
| `7` | Text | 2 |  |
| `8` | Text | 2 |  |
| `Name of child 1_2` | Text | 2 |  |
| `Name of child 2_2` | Text | 2 |  |
| `Reason for expense 1` | Text | 2 |  |
| `Reason for expense 2` | Text | 2 |  |
| `Amount 1_2` | Text | 2 |  |
| `Amount 2_2` | Text | 2 |  |
| `Name of child 1_3` | Text | 2 |  |

*... and 30 additional fields (see fields.json for complete list)*

## AI Hints

- **Background Check**: Guardian candidates require DHHS background checks.
- **Best Interest**: Court determines guardianship based on minor/incapacitated person's best interest.
- **Reporting**: Guardians must file annual reports with the court.
- **Docket Number**: Leave blank for new filings; clerk assigns. Enter if responding to existing case.

## Validation Checklist

- [ ] All required party names are filled in
- [ ] Court location/county is correct for venue
- [ ] Docket number included (if existing case)
- [ ] All dates are in correct format (MM/DD/YYYY)
- [ ] Signature lines are addressed (physical signature needed)
- [ ] Contact information is complete
- [ ] Background check documentation attached

## Related Forms

- **GS-001** — IN RE:
- **GS-002** — IN RE: ___________________________
- **GS-003** — IN RE:
- **GS-004** — IN RE: ___________________________
- **GS-006** — IN RE: ___________________________
- **GS-007** — IN RE:
- **GS-008** — IN RE: ____________________________
- **GS-009** — IN RE: _______________________________
- **GS-010** — IN RE: _______________________________
- **GS-012** — IN RE: ___________________________
