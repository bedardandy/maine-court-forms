<!-- Reused from prior skills stash; verify against schema.json. -->
# FM-188 — Order for Service by Alternate Means

**Form Number:** FM-188, Rev. 02/20
**Pages:** 2
**Fillable Fields:** 39
**Category:** Family
**Court:** District Court / Family Division

## Purpose

This is a court order form used in family cases. Typically completed by the court or prepared by counsel for judicial signature.

## Governing Law

- **19-A M.R.S.** — Primary statutory authority

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
| `other party for service by alternate` | CheckBox | 1 | Check if applicable |
| `The type of action is` | Text | 1 |  |
| `may be` | CheckBox | 1 | Check if applicable |
| `will not be affected which include` | CheckBox | 1 | Check if applicable |
| `undefined` | Text | 1 |  |
| `Property or credits of the defendant` | Text | 1 |  |
| `The name and address of the plaintiff or attorney if known 1` | Text | 1 | Mailing/street address |
| `The name and address of the plaintiff or attorney if known 2` | Text | 1 | Mailing/street address |
| `The name and address of the defendant or attorney if known 1` | Text | 1 | Mailing/street address |
| `The name and address of the defendant or attorney if known 2` | Text | 1 | Mailing/street address |
| `The name and address of the other party or attorney if known 1` | Text | 1 | Mailing/street address |
| `The name and address of the other party or attorney if known 2` | Text | 1 | Mailing/street address |
| `unknown and cannot be ascertained by reasonable` | CheckBox | 1 | Check if applicable |
| `known but it appears the person is evading process` | CheckBox | 1 | Check if applicable |
| `Leaving a copy of this Order and` | CheckBox | 1 | Check if applicable |
| `summons and complaint` | CheckBox | 1 | Check if applicable |
| `postjudgment motion at the` | CheckBox | 1 | Check if applicable |
| `defendants dwelling house or usual place of abode located at` | Text | 1 |  |
| `Publishing a copy of this Order once a week for three 3 consecutive weeks in the` | CheckBox | 1 | Check if applicable |
| `a newspaper of general circulation in the county or municipality` | Text | 1 | County name |
| `most reasonably calculated to provide actual notice of the pendency of the action` | Text | 1 |  |
| `AND if the defendants address is known mailing a copy of this Order as published to that address` | CheckBox | 1 | Mailing/street address |
| `Other alternate means` | CheckBox | 1 | Check if applicable |
| `undefined_2` | Text | 1 |  |
| `1` | Text | 1 |  |
| `2` | Text | 1 |  |
| `received intact with all relevant documents and information including 1` | Text | 2 |  |
| `received intact with all relevant documents and information including 2` | Text | 2 |  |
| `received intact with all relevant documents and information including 3` | Text | 2 |  |
| `Date mmddyyyy` | Text | 2 | MM/DD/YYYY format |
| `Magistrate` | CheckBox | 2 | Check if applicable |
| `Judge Maine District Court` | CheckBox | 2 | Check if applicable |

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
