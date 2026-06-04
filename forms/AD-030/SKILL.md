<!-- Reused from prior skills stash; verify against schema.json. -->
# AD-030 — Notice of Intent to Adopt

**Form Number:** AD-030, Rev. 10/23
**Pages:** 2
**Fillable Fields:** 60
**Category:** Adoption
**Court:** Probate Court / District Court

## Purpose

Form used in adoption proceedings in Maine court.

## Governing Law

- **18-C M.R.S. § 9**

## Field Mappings

| Field Name | Type | Page | Notes |
|-----------|------|------|-------|
| `LOCATION` | Text | 1 | Court location |
| `Docket No_2` | Text | 1 | Court docket number |
| `Name of Adoptee` | Text | 1 |  |
| `Name` | Text | 1 |  |
| `Date of Birth` | Text | 1 | MM/DD/YYYY format |
| `Legal Residence` | Text | 1 |  |
| `Mailing Address` | Text | 1 | Mailing/street address |
| `Telephone` | Text | 1 | Phone number |
| `DatePlace of Marriage` | Text | 1 | MM/DD/YYYY format |
| `Name_2` | Text | 1 |  |
| `Date of Birth_2` | Text | 1 | MM/DD/YYYY format |
| `Legal Residence_2` | Text | 1 |  |
| `Mailing Address_2` | Text | 1 | Mailing/street address |
| `Telephone_2` | Text | 1 | Phone number |
| `DatePlace of Marriage_2` | Text | 1 | MM/DD/YYYY format |
| `Name_3` | Text | 1 |  |
| `Date of Birth_3` | Text | 1 | MM/DD/YYYY format |
| `Place of Birth` | Text | 1 |  |
| `Adoptee resides in this county andor` | CheckBox | 1 | County name |
| `Petitioners resides in this county` | CheckBox | 1 | County name |
| `adoptee was present 1` | Text | 1 |  |
| `adoptee was present 2` | Text | 1 |  |
| `adoptee was present 3` | Text | 1 |  |
| `adoptee was present 4` | Text | 1 |  |
| `adoptee was present 5` | Text | 1 |  |
| `havehas participated as a party witness or in some other capacity in other litigation concerning the custody` | CheckBox | 1 | Check if applicable |
| `havehas information of a custody proceeding concerning the adoptee pending in a court in Maine or some` | CheckBox | 1 | Check if applicable |
| `knows of a person not a party to this case who has physical custody of the adoptee or claims to have` | CheckBox | 1 | Check if applicable |
| `6 1` | Text | 2 |  |
| `Each petitioner consented to the childs birth through assisted reproduction and` | CheckBox | 2 | Check if applicable |
| `Other than this claim no competing claims of parentage of the child exist` | CheckBox | 2 | Check if applicable |
| `A copy of the childs birth certificate and` | CheckBox | 2 | Check if applicable |
| `A copy of the joint petitioners marriage certificate` | CheckBox | 2 | Check if applicable |
| `Not applicable because the joint petitioners are not married` | CheckBox | 2 | Check if applicable |
| `Not applicable because this petition is filed by a single petitioner` | CheckBox | 2 | Check if applicable |
| `Text1` | Text | 2 |  |
| `Date` | Text | 2 | MM/DD/YYYY format |
| `Name_4` | Text | 2 |  |
| `Address 1` | Text | 2 | Mailing/street address |
| `Address 2` | Text | 2 | Mailing/street address |
| `Phone Number` | Text | 2 | Phone number |
| `Attorney for Petitioners if any` | Text | 2 |  |
| `Text2` | Text | 2 |  |
| `Date_2` | Text | 2 | MM/DD/YYYY format |
| `Name_5` | Text | 2 |  |
| `Address 1_2` | Text | 2 | Mailing/street address |
| `Address 2_2` | Text | 2 | Mailing/street address |
| `Phone Number_2` | Text | 2 | Phone number |
| `undefined` | Text | 2 |  |
| `Text3` | Text | 2 |  |
| `Date_3` | Text | 2 | MM/DD/YYYY format |
| `Name_6` | Text | 2 |  |
| `Address 1_3` | Text | 2 | Mailing/street address |
| `Address 2_3` | Text | 2 | Mailing/street address |
| `Phone Number_3` | Text | 2 | Phone number |
| `Email` | Text | 2 | Email address |
| `COUNTY` | Text | 2 | County name |
| `Personally appeared the above named` | Text | 2 |  |
| `and made oath that the foregoing statements are true under penalty of` | Text | 2 |  |
| `Date_4` | Text | 2 | MM/DD/YYYY format |

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
- [ ] Contact information is complete
- [ ] ICWA determination documented
- [ ] Required consents attached

## Related Forms

- **AD-001** — LOCATION:
- **AD-003** — In the Matter of the Adoption Petition of:
- **AD-004** — In the Matter of the Adoption Petition of:
- **AD-005** — In the Matter of the Adoption Petition of:
- **AD-006** — In the Matter of the Adoption Petition of:
- **AD-007** — ACCOMPANY PETITION FOR ADOPTION
- **AD-008** — In the Matter of the Adoption Petition of:
- **AD-009** — In the Matter of the Adoption Petition of:
- **AD-012** — In the Matter of the Adoption Petition of:
- **AD-015** — ORDER OF APPROVAL

> **Note:** a dedicated fill recipe exists for this form in `engine/recipes/`. The recipe is the authoritative field mapping; this doc is the human-readable companion.
