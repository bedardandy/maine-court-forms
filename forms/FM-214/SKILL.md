<!-- Reused from prior skills stash; verify against schema.json. -->
# FM-214 — Expedited Motion to Enforce Visitation

**Form Number:** FM-214, Rev. 08/20
**Pages:** 2
**Fillable Fields:** 48
**Category:** Family
**Court:** District Court / Family Division

## Purpose

This motion form is used in family cases in Maine court. Filed to request specific court action.

## Governing Law

- **19-A M.R.S. § 1768**

## Field Mappings

| Field Name | Type | Page | Notes |
|-----------|------|------|-------|
| `Plaintiff` | Text | 1 |  |
| `Location Town` | Text | 1 | Court location |
| `Docket No` | Text | 1 | Court docket number |
| `Defendant` | Text | 1 |  |
| `Other party if any` | Text | 1 |  |
| `plaintiff` | CheckBox | 1 | Check if applicable |
| `defendant in this case and hereby moves this Court for an emergency order to enforce` | CheckBox | 1 | Check if applicable |
| `plaintiff_2` | CheckBox | 1 | Check if applicable |
| `defendant in this case and I now reside in town` | CheckBox | 1 | Check if applicable |
| `town 1` | Text | 1 |  |
| `county 1` | Text | 1 | County name |
| `state 1` | Text | 1 |  |
| `The other party now resides in town` | CheckBox | 1 | Check if applicable |
| `town 2` | Text | 1 |  |
| `county 2` | Text | 1 | County name |
| `state 2` | Text | 1 |  |
| `Residence of the other party is unknown and I have used reasonable efforts and cannot locate the other` | CheckBox | 1 | Check if applicable |
| `I am subject to a child custody determination in name and location of the court that issued the order` | CheckBox | 1 | Check if applicable |
| `name and location of court` | Text | 1 |  |
| `dated` | Text | 1 | MM/DD/YYYY format |
| `I am a resident of the State of Maine` | CheckBox | 1 | Check if applicable |
| `I am on active duty serving in the United States Armed Forces or in the National Guard AND` | CheckBox | 1 | Check if applicable |
| `I am permanently stationed at a military naval or National Guard post station or base outside this` | CheckBox | 1 | Check if applicable |
| `Order More specifically 1` | Text | 1 |  |
| `Order More specifically 2` | Text | 1 |  |
| `I have provided at least two days notice to the custodial parent OR` | CheckBox | 1 | Check if applicable |
| `I have provided shorter notice to the` | CheckBox | 1 | Check if applicable |
| `by granting the following relief 1` | Text | 2 |  |
| `by granting the following relief 2` | Text | 2 |  |
| `I swear under penalty of perjury that the above statements are true and correct I understand that these statements` | CheckBox | 2 | Check if applicable |
| `Date mmddyyyy` | Text | 2 | MM/DD/YYYY format |
| `Signature electronic or actual` | Text | 2 | Physical signature required |
| `plaintiff_3` | CheckBox | 2 | Check if applicable |
| `defendant` | CheckBox | 2 | Check if applicable |
| `other party` | CheckBox | 2 | Check if applicable |
| `Attorney` | Text | 2 |  |
| `Name` | Text | 2 |  |
| `Address 1` | Text | 2 | Mailing/street address |
| `Address is confidential if so leave blank below` | CheckBox | 2 | Mailing/street address |
| `Address 2` | Text | 2 | Mailing/street address |
| `Address 1_2` | Text | 2 | Mailing/street address |
| `Address 3` | Text | 2 | Mailing/street address |
| `Address 2_2` | Text | 2 | Mailing/street address |
| `Telephone` | Text | 2 | Phone number |
| `Telephone_2` | Text | 2 | Phone number |
| `Email` | Text | 2 | Email address |
| `Email_2` | Text | 2 | Email address |
| `name of party` | Text | 2 |  |

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
- [ ] Signature lines are addressed (physical signature needed)
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

> **Note:** a dedicated fill recipe exists for this form in `engine/recipes/`. The recipe is the authoritative field mapping; this doc is the human-readable companion.
