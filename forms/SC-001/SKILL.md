# SC-001 — Statement of Claim

**Form Number:** SC-001, Rev. 10/21
**Pages:** 3
**Fillable Fields:** 29
**Category:** Small Claims
**Filing Fee:** $70.00
**Companion Forms:** SC-005 (Acknowledgment of Service), SC-006 (Affidavit and Request for Service), SC-009/SC-010 (Instructions)

## Purpose

This is the initial filing form for a small claims action in Maine District Court. The plaintiff describes their claim, specifies the amount sought (up to $6,000), and provides contact information for both parties. Small claims uses simplified procedures under the Maine Rules of Small Claims Procedure.

## Governing Law

- **M.R.S.C.P. 3(a)** — Statement of Claim
- **M.R.S.C.P. 4** — Service
- **14 M.R.S. § 7482** — Small claims jurisdiction (up to $6,000)

## Filing Requirements

1. Amount must not exceed $6,000
2. Must not be a debt collection action under Title 32
3. Must describe the claim with relevant dates
4. Filing fee: $70.00
5. Plaintiff must serve defendant (or request clerk service via SC-006)

## Field Mappings

### Page 1 — Claim

| Field Name | Type | Source | Notes |
|-----------|------|--------|-------|
| `Plaintiff` | Text | `matter.parties[role=plaintiff].full_name` | |
| `Location Town` | Text | `matter.court_location` | |
| `Docket No` | Text | `matter.docket_number` | Clerk assigns |
| `Defendant` | Text | `matter.parties[role=defendant].full_name` | |
| Claim description | Text | AI from matter notes | Brief description with dates |
| Amount requested ($) | Text | `matter.amount_claimed` | Up to $6,000 |
| Additional relief requested | Text | AI from matter notes | Repair, return, refund, etc. |
| `This is not a debt collection action` | Text | deterministic | Affirmation (pre-printed) |
| Date | Text | `today()` | |
| Signature | Text | *leave blank* | |
| Printed name | Text | `matter.parties[role=plaintiff].full_name` | |
| `Yes` (attorney representing) | CheckBox | `matter.has_attorney` | |
| `No` (no attorney) | CheckBox | `!matter.has_attorney` | |

### Page 2 — Contact Information

| Field Name | Type | Source | Notes |
|-----------|------|--------|-------|
| Attorney name | Text | `attorney.full_name` | If applicable |
| Bar number | Text | `attorney.bar_number` | |
| Attorney address | Text | `attorney.address` | |
| Attorney phone | Text | `attorney.phone` | |
| Attorney email | Text | `attorney.email` | |
| Plaintiff address | Text | `matter.parties[role=plaintiff].address` | |
| Plaintiff phone | Text | `matter.parties[role=plaintiff].phone` | |
| Plaintiff email | Text | `matter.parties[role=plaintiff].email` | |
| Defendant address | Text | `matter.parties[role=defendant].address` | |
| Defendant phone | Text | `matter.parties[role=defendant].phone` | |
| Defendant email | Text | `matter.parties[role=defendant].email` | |

## AI Hints

### Claim Description
- Be concise but include: what happened, when, how much is owed, why
- Example: "On 06/15/2025, I paid defendant $4,800 to repair my vehicle (2018 Honda Civic). Defendant failed to complete repairs and refused to return my vehicle for 3 weeks. Vehicle was returned with same problems unresolved."
- Include relevant dates and dollar amounts

### Amount Limits
- Maximum $6,000 for small claims
- If claim exceeds $6,000, must file regular civil action

## Validation Checklist

- [ ] Amount does not exceed $6,000
- [ ] Claim description is clear and includes dates
- [ ] Not a debt collection action
- [ ] Both plaintiff and defendant contact info provided
- [ ] Attorney status indicated (Yes/No)
- [ ] Date and signature present

## Related Forms Workflow

```
1. SC-001 (this form) — Statement of Claim
2. SC-005 — Acknowledgment of Service (mail to defendant)
3. SC-006 — Request for Service (if clerk serves)
4. SC-010 — Service Instructions (reference)
5. Hearing → Judgment
6. If judgment debtor doesn't pay:
   a. SC-003 — Request for Disclosure Hearing
7. If appealed:
   a. SC-007 — Notice of Small Claims Appeal
```
