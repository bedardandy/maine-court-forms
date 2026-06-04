<!-- Reused from prior skills stash; verify against schema.json. -->
# FM-057 — Affidavit of Confidential Address

**Form Number:** FM-057, Rev. 08/20
**Pages:** 1
**Fillable Fields:** 40
**Category:** Family
**Court:** District Court / Family Division

## Purpose

This affidavit form provides sworn testimony in support of a family matter.

## Governing Law

- **19-A M.R.S. § 1653**

## Field Mappings

| Field Name | Type | Page | Notes |
|-----------|------|------|-------|
| `Plaintiff` | Text | 1 |  |
| `Location Town` | Text | 1 | Court location |
| `Docket No` | Text | 1 | Court docket number |
| `Defendant` | Text | 1 |  |
| `Other party if any` | Text | 1 |  |
| `plaintiff` | CheckBox | 1 | Check if applicable |
| `defendant` | CheckBox | 1 | Check if applicable |
| `other party that party makes this request to keep the following` | CheckBox | 1 | Check if applicable |
| `Physical address` | CheckBox | 1 | Mailing/street address |
| `information confidential` | Text | 1 |  |
| `Mailing address` | CheckBox | 1 | Mailing/street address |
| `undefined` | Text | 1 |  |
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
| `plaintiff_2` | CheckBox | 1 | Check if applicable |
| `defendant_2` | CheckBox | 1 | Check if applicable |
| `other party states as follows under oath` | CheckBox | 1 | Check if applicable |
| `the following reasons 1` | Text | 1 |  |
| `the following reasons 2` | Text | 1 |  |
| `the following reasons 3` | Text | 1 |  |
| `the following reasons 4` | Text | 1 |  |
| `the following reasons 5` | Text | 1 |  |
| `the following reasons 6` | Text | 1 |  |
| `the following reasons 7` | Text | 1 |  |
| `the following reasons 8` | Text | 1 |  |
| `I swear under penalty of perjury that the above statements are true and correct I understand that these statements` | CheckBox | 1 | Check if applicable |
| `Date mmddyyyy` | Text | 1 | MM/DD/YYYY format |
| `undefined_7` | Text | 1 |  |
| `plaintiff_3` | CheckBox | 1 | Check if applicable |
| `defendant_3` | CheckBox | 1 | Check if applicable |
| `other party` | CheckBox | 1 | Check if applicable |

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

> **Note:** a dedicated fill recipe exists for this form in `engine/recipes/`. The recipe is the authoritative field mapping; this doc is the human-readable companion.
