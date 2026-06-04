<!-- Reused from prior skills stash; verify against schema.json. -->
# CV-295 — Petition for Special Findings and Relief (SIJS)

**Form Number:** CV-295
**Fillable Fields:** 74
**Category:** Civil — Immigration/Child Welfare
**Court:** District Court

## Purpose

Petition for Special Immigrant Juvenile Status (SIJS) findings under Maine law, allowing at-risk noncitizen children to seek federal immigration relief.

## Governing Law

- **22 M.R.S. § 4099-I (special findings for at-risk noncitizen children)**

## Field Mapping Summary

### Page 0

| Field Name | Type | Source |
|-----------|------|--------|
| `IN RE` | Text | From matter data |
| `Location Town` | Text | `matter.court_location` |
| `PETITION FOR SPECIAL FINDINGS AND RELIEF` | Text | From matter data |
| `Address Street CityTown State Zip` | Text | `party.address` |
| `I am the` | Text | From matter data |
| `Parent` | CheckBox | From matter data |
| `Guardian` | CheckBox | From matter data |
| `Atrisk noncitizen child` | CheckBox | From matter data |
| `Other` | CheckBox | From matter data |
| `who is seeking court orders pursuant to 22 MRS  4099I` | Text | From matter data |
| `The child has also been known as list any additional or previously miswritten names for the child if` | Text | From matter data |
| `applicable 1` | Text | From matter data |
| `Physical Address Street CityTown State Zip` | Text | `party.address` |
| `Date of Birth mmddyyyy` | Text | `today()` or relevant date |
| `Please list any other docket number for any other court case that has involved the child` | Text | `matter.docket_number` |
| `3 Parent Information` | Text | From matter data |
| `The parent has also been known as list any additional or previously miswritten names for the parent if` | Text | From matter data |

### Page 1

| Field Name | Type | Source |
|-----------|------|--------|
| `Text1` | Text | From matter data |
| `Date of birth mmddyyyy` | Text | `today()` or relevant date |
| `Telephone number` | Text | `party.phone` |
| `Email address` | Text | `party.email` |
| `Name First Middle Last` | Text | From matter data |
| `Text2` | Text | From matter data |
| `Date of birth mmddyyyy_2` | Text | `today()` or relevant date |
| `Telephone number_2` | Text | `party.phone` |
| `Email address_2` | Text | `party.email` |
| `Parent 1 is not viable under Maine law because of` | CheckBox | From matter data |
| `Abuse as defined by 22 MRS  40021` | CheckBox | From matter data |
| `Neglect as defined by 22 MRS  40021` | CheckBox | From matter data |
| `Abandonment as defined by 22 MRS  40021A or` | CheckBox | From matter data |
| `Similar circumstances as defined by 22 MRS 4099I1F` | CheckBox | From matter data |
| `selected 1` | Text | From matter data |

### Page 2

| Field Name | Type | Source |
|-----------|------|--------|
| `Parent 2 is not viable under Maine law because of` | CheckBox | From matter data |
| `Abuse as defined by 22 MRS  40021_2` | CheckBox | From matter data |
| `Neglect as defined by 22 MRS  40021_2` | CheckBox | From matter data |
| `Abandonment as defined by 22 MRS  40021A or_2` | CheckBox | From matter data |
| `Similar circumstances as defined by 22 MRS 4099I1F_2` | CheckBox | From matter data |
| `selected 1_2` | Text | From matter data |
| `Pursuant to 22 MRS  40021C and 19A MRS  16533 it is not in the best interest of the` | CheckBox | From matter data |
| `undefined` | Text | From matter data |
| `the following reasons state the factual basis 1` | Text | From matter data |
| `Psychiatric` | CheckBox | From matter data |
| `Occupational` | CheckBox | From matter data |
| `Social Services` | CheckBox | From matter data |
| `Protection against human trafficking` | CheckBox | From matter data |
| `Other_2` | CheckBox | From matter data |
| `undefined_2` | Text | From matter data |
| `Psychological` | CheckBox | From matter data |
| `Medical` | CheckBox | From matter data |
| `Protection against domestic violence` | CheckBox | From matter data |
| `Educational` | CheckBox | From matter data |
| `Dental` | CheckBox | From matter data |
| `11 Additional findings of fact or rulings of law requested 1` | Text | From matter data |

### Page 3

| Field Name | Type | Source |
|-----------|------|--------|
| `I swear under penalty of perjury that the above statements are true and correct I understand that these` | CheckBox | From matter data |
| `Date mmddyyyy` | Text | `today()` or relevant date |
| `undefined_3` | Text | From matter data |
| `Mailing Address 1` | Text | `party.address` |
| `Mailing Address 2` | Text | `party.address` |
| `Phone Number` | Text | `party.phone` |
| `Email` | Text | `party.email` |
| `Date mmddyyyy_2` | Text | `today()` or relevant date |
| `undefined_4` | Text | From matter data |
| `Maine Bar No` | Text | `attorney.bar_number` |
| `Mailing Address 1_2` | Text | `party.address` |
| `Mailing Address 2_2` | Text | `party.address` |
| `Phone Number_2` | Text | `party.phone` |
| `Email_2` | Text | `party.email` |
| `COUNTY` | Text | `matter.court_county` |
| `Personally appeared the above named` | Text | From matter data |
| `and made oath that the` | Text | From matter data |
| `Date mmddyyyy_3` | Text | `today()` or relevant date |
| `Attorney at Law` | CheckBox | From matter data |
| `Notary Public` | CheckBox | From matter data |
| `Clerk` | CheckBox | From matter data |


## AI Hints

74 fields, 4 pages. Detailed petition covering: petitioner info (parent/guardian/child/other), child's info (name, aliases, DOB, prior cases), both parents' info with viability assessment (abuse/neglect/abandonment/similar basis), requested findings (reunification not viable, best interest, consent to SIJS), declarations about child welfare jurisdiction, and relief requested. Filed in District Court only.

## Validation Checklist

- [ ] Case caption is complete (parties, court, docket number)
- [ ] Date is filled in (mm/dd/yyyy format)
- [ ] Signature line identified (leave blank for physical signature)
