<!-- Reused from prior skills stash; verify against schema.json. -->
# AD-003 — Consent of Other Than Parent or Minor

**Form Number:** AD-003, Rev. 02/20
**Pages:** 1
**Fillable Fields:** 17
**Category:** Adoption
**Court:** Probate Court / District Court

## Purpose

This petition form initiates or requests action in a adoption matter in Maine court.

## Governing Law

- **18-C M.R.S. § 9**

## Field Mappings

| Field Name | Type | Page | Notes |
|-----------|------|------|-------|
| `County` | Text | 1 | County name |
| `Location` | Text | 1 | Court location |
| `Docket No` | Text | 1 | Court docket number |
| `Docket No_2` | Text | 1 | Court docket number |
| `Name of Adoptee` | Text | 1 |  |
| `I` | Text | 1 |  |
| `an officer of the Maine Department of Health and Human Services` | CheckBox | 1 | Check if applicable |
| `an officer of` | CheckBox | 1 | Check if applicable |
| `a duly licensed child` | Text | 1 |  |
| `placement agency in` | Text | 1 |  |
| `the legal guardian of the abovenamed adoptee` | CheckBox | 1 | Check if applicable |
| `the legal custodian of the abovenamed adoptee` | CheckBox | 1 | Check if applicable |
| `named adoptee by` | Text | 1 |  |
| `name` | Text | 1 |  |
| `Dated` | Text | 1 | MM/DD/YYYY format |
| `Personally appeared the abovenamed` | Text | 1 |  |
| `Text1` | Text | 1 |  |

## AI Hints

- **ICWA Compliance**: Check if the Indian Child Welfare Act applies. Form may require notice to tribes.
- **Consent Requirements**: Verify all required consents are obtained per 18-C M.R.S. § 9-302.
- **Background Check**: Petitioners typically need DHHS background checks.
- **Docket Number**: Leave blank for new filings; clerk assigns. Enter if responding to existing case.

## Validation Checklist

- [ ] All required party names are filled in
- [ ] Court location/county is correct for venue
- [ ] Docket number included (if existing case)
- [ ] All dates are in correct format (MM/DD/YYYY)
- [ ] ICWA determination documented
- [ ] Required consents attached

## Related Forms

- **AD-001** — LOCATION:
- **AD-004** — In the Matter of the Adoption Petition of:
- **AD-005** — In the Matter of the Adoption Petition of:
- **AD-006** — In the Matter of the Adoption Petition of:
- **AD-007** — ACCOMPANY PETITION FOR ADOPTION
- **AD-008** — In the Matter of the Adoption Petition of:
- **AD-009** — In the Matter of the Adoption Petition of:
- **AD-012** — In the Matter of the Adoption Petition of:
- **AD-015** — ORDER OF APPROVAL
- **AD-017** — In the Matter of the Adoption Petition of:

> **Note:** a dedicated fill recipe exists for this form in `engine/recipes/`. The recipe is the authoritative field mapping; this doc is the human-readable companion.
