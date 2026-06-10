# CV-060 — Request for Withdrawal (Minor’s Settlement)

**Form Number:** CV-060, Rev. 06/14
**Pages:** 1
**Fillable Fields:** 25
**Category:** Civil — Minor's Settlement
**Filing Fee:** None
**Companion Forms:** None specific

## Purpose

This form requests court approval to withdraw funds from a minor's settlement account. When a minor receives a settlement, funds are typically deposited in a protected account. This form is used by the next friend or petitioner to request withdrawal, which requires court approval under M.R. Civ. P. 17A(b)(5).

## Governing Law

- **M.R. Civ. P. 17A(b)(5)** — Minor settlements, withdrawal of funds

## Filing Requirements

1. Must state the specific amount requested for withdrawal
2. Must identify the account and financial institution
3. Must provide reasons for the withdrawal
4. Court will issue an order approving or denying

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
| `Justice Superior Court` | CheckBox | `matter.court_type == "Superior"` | |
| `Judge District Court` | CheckBox | `matter.court_type == "District"` | |
| Withdrawal amount ($) | Text | AI from matter notes | Amount to withdraw |
| Account number | Text | `matter.settlement_account_number` | |
| Account name | Text | `matter.minor.full_name` | Minor's name |
| Financial institution | Text | `matter.settlement_bank_name` | |
| Bank location | Text | `matter.settlement_bank_location` | |
| Reason(s) for withdrawal | Text | AI from matter notes | Explain need |
| Date | Text | `today()` | |
| Signature | Text | *leave blank* | Physical signature |
| `Next Friend` | CheckBox | `matter.filing_role == "next_friend"` | |
| `Petitioner` | CheckBox | `matter.filing_role == "petitioner"` | |

### Order of Court (bottom section — court fills)

| Field Name | Type | Source | Notes |
|-----------|------|--------|-------|
| Approved amount | Text | *leave blank* | Court fills |
| Condition text | Text | *leave blank* | Court fills |
| Not approved reason | Text | *leave blank* | Court fills |
| Judge signature/date | Text | *leave blank* | Court fills |

## AI Hints

- Withdrawal reasons should be specific and relate to the minor's welfare (education, medical, living expenses)
- The court will scrutinize whether the withdrawal benefits the minor
- Include supporting documentation references if available

## Validation Checklist

- [ ] Withdrawal amount is specified
- [ ] Account information is complete
- [ ] Financial institution identified
- [ ] Reason for withdrawal is provided
- [ ] Either "Next Friend" or "Petitioner" is checked
- [ ] Court order section left blank (court completes)

## Related Forms Workflow

```
1. Original minor settlement approval
2. CV-060 (this form) — Withdrawal request
3. Court hearing (if required)
4. Court order (bottom of this form)
```
