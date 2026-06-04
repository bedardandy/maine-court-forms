<!-- Reused from prior skills stash; verify against schema.json. -->
# FM-284 — Affidavit and Request to Register

**Form Number:** FM-284, Rev. 01/23
**Pages:** 5
**Fillable Fields:** 84
**Category:** Family
**Court:** District Court / Family Division

## Purpose

This is a court order form used in family cases. Typically completed by the court or prepared by counsel for judicial signature.

## Governing Law

- **19-A M.R.S. §  3253**
- **19-A M.R.S. § 3253**
- **19-A M.R.S. § 3255**
- **19-A M.R.S. § 3261**
- **19-A M.R.S. § 3312**
- **19-A M.R.S. § 3321**
- **19-A M.R.S. §§ 2801**

## Field Mappings

| Field Name | Type | Page | Notes |
|-----------|------|------|-------|
| `PlaintiffPetitioner` | Text | 1 |  |
| `DefendantRespondent` | Text | 1 |  |
| `Location Town` | Text | 1 | Court location |
| `Docket No` | Text | 1 | Court docket number |
| `plaintiffpetitioner` | CheckBox | 1 | Check if applicable |
| `defendantrespondent in a case from name the state or foreign country` | CheckBox | 1 | Defendant's name |
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
| `Two copies including one certified copy of the foreign support order to be registered including any` | CheckBox | 1 | Check if applicable |
| `Was NOT issued by a Hague Convention foreign country or` | CheckBox | 2 | Check if applicable |
| `Was issued by a Hague Convention foreign country The nonregistering party` | CheckBox | 2 | Check if applicable |
| `resides` | CheckBox | 2 | Check if applicable |
| `does` | CheckBox | 2 | Check if applicable |
| `A complete text of the support order or an abstract or extract of the support order drawn up by` | CheckBox | 2 | Check if applicable |
| `A record stating that the support order is enforceable in the issuing country` | CheckBox | 2 | Check if applicable |
| `If the respondent did not appear and was not represented in the proceedings in the issuing` | CheckBox | 2 | Check if applicable |
| `A record showing the amount of arrears if any and the date the amount was calculated` | CheckBox | 2 | MM/DD/YYYY format |
| `A record showing a requirement for automatic adjustment of the amount of support if any and` | CheckBox | 2 | Check if applicable |
| `If necessary a record showing the extent to which the applicant received free legal assistance in` | CheckBox | 2 | Check if applicable |
| `undefined_2` | Text | 2 |  |
| `I know the obligors social security number Complete and attach the UIFSA` | CheckBox | 2 | Check if applicable |
| `I do not know the obligors social security number` | CheckBox | 2 | Check if applicable |
| `Employer Name` | Text | 3 |  |
| `Employer Address` | Text | 3 | Mailing/street address |
| `D Any other source of income` | Text | 3 |  |
| `Property description 1` | Text | 3 |  |
| `Location of property 1` | Text | 3 | Court location |
| `Property description 2` | Text | 3 |  |
| `Location of property 2` | Text | 3 | Court location |
| `Property description 3` | Text | 3 |  |
| `Location of property 3` | Text | 3 | Court location |
| `Property description 4` | Text | 3 |  |
| `Location of property 4` | Text | 3 | Court location |
| `Property description 5` | Text | 3 |  |
| `Location of property 5` | Text | 3 | Court location |
| `Registration only` | CheckBox | 3 | Check if applicable |
| `Enforcement` | CheckBox | 3 | Check if applicable |
| `of child support If this is the only box you check as the purpose of registration the court will forward` | CheckBox | 3 | Check if applicable |
| `of spousal support complete and serve form FM068 Motion for Contempt` | CheckBox | 3 | Check if applicable |
| `Contempt complete and serve form FM068 Motion for Contempt` | CheckBox | 3 | Check if applicable |
| `Modification modification is an option for child support only modification of foreign spousal support` | CheckBox | 3 | Check if applicable |
| `CHILD SUPPORT ORDER OF ANOTHER STATE` | CheckBox | 4 | Check if applicable |
| `All Parties Reside in Maine All of the parties who are individuals reside in Maine and the children` | CheckBox | 4 | Check if applicable |
| `Not All Parties Reside in Maine You must select one of the following` | CheckBox | 4 | Check if applicable |
| `1 Neither the children nor the obligee the person to whom support is paid who is an` | CheckBox | 4 | Check if applicable |
| `All of the parties who are individuals have filed consents in the court that issued the child` | CheckBox | 4 | Check if applicable |
| `Maine is the residence of the children or` | CheckBox | 4 | Check if applicable |
| `A party who is an individual is subject to the personal jurisdiction of the Maine court` | CheckBox | 4 | Check if applicable |
| `I certify that I have attached copies of all the consents filed by the parties in` | CheckBox | 4 | Check if applicable |

*... and 24 additional fields (see fields.json for complete list)*

## AI Hints

- **Service Requirements**: Ensure proper service on all parties.
- **Financial Disclosure**: If financial issues involved, FM-043 Financial Statement may be required.
- **Child-Related**: If children involved, parenting plan and child support worksheets may be needed.
- **Docket Number**: Leave blank for new filings; clerk assigns. Enter if responding to existing case.

## Validation Checklist

- [ ] All required party names are filled in
- [ ] Court location/county is correct for venue
- [ ] Docket number included (if existing case)
- [ ] All dates are in correct format (MM/DD/YYYY)
- [ ] Contact information is complete
- [ ] Service of process addressed
- [ ] Financial disclosures attached if required

## Related Forms

- **FM-002** — Family and Probate Matter Summary Sheet
- **FM-004** — COMPLAINT FOR DIVORCE
- **FM-006** — COMPLAINT FOR DETERMINATION OF PARENTAGE,
- **FM-008** — PETITION FOR EXPEDITED ENFORCEMENT
- **FM-020** — ENTRY OF APPEARANCE
- **FM-040** — Child Support Worksheet
- **FM-040-A** — SUPPLEMENTAL CHILD SUPPORT WORKSHEET
- **FM-042** — CERTIFICATE IN LIEU OF FINANCIAL STATEMENT
- **FM-043** — FINANCIAL STATEMENT
- **FM-050** — CHILD SUPPORT AFFIDAVIT
