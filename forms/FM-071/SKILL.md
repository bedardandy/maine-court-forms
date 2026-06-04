<!-- Reused from prior skills stash; verify against schema.json. -->
# FM-071 — Objection to Final Order of a Magistrate

**Form Number:** FM-071, Rev. 02/20
**Pages:** 1
**Fillable Fields:** 16
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
| `DISTRICT COURT` | Text | 1 |  |
| `Docket No` | Text | 1 | Court docket number |
| `v` | Text | 1 |  |
| `plaintiff` | CheckBox | 1 | Check if applicable |
| `defendant in the above captioned matter  I object to the entry of the Magistrates Final Order` | CheckBox | 1 | Check if applicable |
| `reject the Order or` | CheckBox | 1 | Check if applicable |
| `modify it as follows` | CheckBox | 1 | Check if applicable |
| `Therefore I request that a Judge 1` | Text | 1 |  |
| `I understand that to appeal a Magistrates final order I must file an objection in the District Court within 21 days` | CheckBox | 1 | Check if applicable |
| `I understand the Magistrates Order is effective when signed and remains in effect despite this objection until` | CheckBox | 1 | Check if applicable |
| `adopted modified or rejected by a Judge` | Text | 1 |  |
| `undefined` | Text | 1 |  |
| `plaintiff_2` | CheckBox | 1 | Check if applicable |
| `defendant` | CheckBox | 1 | Check if applicable |
| `Text1` | Text | 1 |  |

## AI Hints

- **Service Requirements**: Ensure proper service on all parties.
- **Financial Disclosure**: If financial issues involved, FM-043 Financial Statement may be required.
- **Child-Related**: If children involved, parenting plan and child support worksheets may be needed.
- **Docket Number**: Leave blank for new filings; clerk assigns. Enter if responding to existing case.

## Validation Checklist

- [ ] All required party names are filled in
- [ ] Court location/county is correct for venue
- [ ] Docket number included (if existing case)
- [ ] Signature lines are addressed (physical signature needed)
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
