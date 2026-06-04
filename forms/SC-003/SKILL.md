<!-- Reused from prior skills stash; verify against schema.json. -->
# SC-003 — Request for SC Disclosure Hearing

**Form Number:** SC-003, Rev. 02/20
**Pages:** 1
**Fillable Fields:** 19
**Category:** Small Claims — Post-Judgment Enforcement
**Filing Fee:** May apply
**Companion Forms:** SC-006 (Affidavit and Request for Service), SC-001 (original Statement of Claim)

## Purpose

After obtaining a small claims judgment that the debtor has not paid (30+ days), the judgment creditor uses this form to request a disclosure hearing. The debtor must appear and disclose assets and income under oath to determine ability to pay.

## Governing Law

- **M.R.S.C.P. 12(a)** — Disclosure hearings in small claims

## Filing Requirements

1. At least 30 days must have passed since judgment
2. Judgment debtor has not paid or arranged to pay
3. Must send copy to judgment debtor
4. May file with SC-006 for clerk-arranged service

## Field Mappings

| Field Name | Type | Source | Notes |
|-----------|------|--------|-------|
| `Judgment Creditor` | Text | `matter.parties[role=judgment_creditor].full_name` | |
| `Location Town` | Text | `matter.court_location` | |
| `Docket No` | Text | `matter.docket_number` | |
| `Judgment Debtor` | Text | `matter.parties[role=judgment_debtor].full_name` | |
| Judgment date | Text | `matter.events[type=judgment].date` | |
| Judgment amount ($) | Text | `matter.judgment_amount` | |
| `Proof of Income` | CheckBox | AI decision | Documents to bring |
| `Tax Returns` checkbox + years | CheckBox/Text | AI decision | |
| `Proof of Benefits` | CheckBox | AI decision | |
| `Bank Account Statements` | CheckBox | AI decision | |
| `Evidence of Personal Property` | CheckBox | AI decision | |
| `Other` checkbox + text | CheckBox/Text | AI decision | |
| Date | Text | `today()` | |
| Signature | Text | *leave blank* | Judgment creditor signs |

## AI Hints

- Request ALL document categories unless there's a specific reason not to
- Tax returns for 2-3 years is standard
- "Other" might include: vehicle titles, real estate records, business financial statements

## Validation Checklist

- [ ] 30+ days since judgment date
- [ ] Judgment amount is correct
- [ ] At least some document requests are checked
- [ ] Date and signature present
- [ ] Copy will be sent to judgment debtor

## Related Forms Workflow

```
1. SC-001 — Original claim
2. Judgment entered
3. 30+ days pass without payment
4. SC-003 (this form) — Request for Disclosure
5. SC-006 — Service request (if clerk serves)
6. Disclosure hearing held
```
