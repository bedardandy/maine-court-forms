# CV-261 — Please check the appropriate box for the case being filed and follow instructions

**Form Number:** CV-261, Rev. 08/24
**Pages:** 1
**Fillable Fields:** 16
**Category:** Civil — Contract
**Filing Fee:** Standard filing fee + $127 surcharge for debt collection cases (4 M.R.S. § 18-A(3-A))
**Companion Forms:** CV-001 (Civil Summary Sheet), Complaint

## Purpose

Required cover sheet for all contract cases filed in Maine courts. Distinguishes between general contract actions and debt collection actions, which have different fee structures and requirements under 32 M.R.S. Chapter 109-A (Fair Debt Collection Practices).

## Governing Law

- **4 M.R.S. § 18-A(3-A)** — Debt collection surcharge
- **32 M.R.S. § 11002** — Definitions (debt collector)
- **32 M.R.S. § 11020** — Attorney debt collectors

## Filing Requirements

1. Required for ALL contract case filings
2. Must select A (general contract) or B (debt collection)
3. Debt collection requires additional $127 surcharge
4. Must be signed under penalty of perjury

## Field Mappings

| Field Name | Type | Source | Notes |
|-----------|------|--------|-------|
| `Plaintiff` | Text | `matter.parties[role=plaintiff].full_name` | |
| `Superior Court` | CheckBox | `matter.court_type == "Superior"` | |
| `District Court` | CheckBox | `matter.court_type == "District"` | |
| `County` | Text | `matter.court_county` | |
| `Location Town` | Text | `matter.court_location` | |
| `Defendant` | Text | `matter.parties[role=defendant].full_name` | |
| `Docket No` | Text | `matter.docket_number` | |
| `A General Other Contract` | CheckBox | `matter.case_subtype == "contract"` | Breach of contract |
| `B Debt Collection` | CheckBox | `matter.case_subtype == "debt_collection"` | |
| `Credit Card Debt` | CheckBox | AI from matter notes | Sub-type if debt collection |
| `Student Loan Debt` | CheckBox | AI from matter notes | Sub-type if debt collection |
| Date | Text | `today()` | |
| Signature | Text | *leave blank* | |
| `Attorney for` checkbox | CheckBox | `matter.has_attorney` | |
| Printed name and bar number | Text | `attorney.full_name` + `attorney.bar_number` | |

## AI Hints

### Contract vs. Debt Collection
- **General contract (A)**: Breach of contract, construction disputes, business-to-business, etc.
- **Debt collection (B)**: Collecting consumer debts (credit cards, student loans, medical bills, etc.)
- Key test: Is the plaintiff or plaintiff's counsel a "debt collector" as defined in 32 M.R.S. § 11002(5-A) or (6)?
- Attorney debt collectors filing on behalf of banks for credit card/student loan debt → Section B

## Validation Checklist

- [ ] Exactly ONE of A or B is checked
- [ ] If B, determine if credit card or student loan sub-type applies
- [ ] Date and signature present
- [ ] Accompanying CV-001 has matching nature of action
- [ ] If debt collection, $127 surcharge noted

## Related Forms Workflow

```
1. CV-001 — Civil Summary Sheet (select "Debt Collection" or "Other Contract")
2. CV-261 (this form) — Contract Cover Sheet
3. Complaint
4. Summons and service
```
