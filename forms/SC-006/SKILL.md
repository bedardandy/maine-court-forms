# SC-006 — Affidavit and Request for Service

**Form Number:** SC-006, Rev. 01/25
**Pages:** 2
**Fillable Fields:** 16
**Category:** Small Claims — Service of Process
**Filing Fee:** May apply for sheriff service
**Companion Forms:** SC-001 (Statement of Claim), SC-003 (Disclosure Request)

## Purpose

This form requests the court clerk to arrange service of the Statement of Claim or Notice of Disclosure Hearing on the defendant. The plaintiff certifies they have filed fewer than three small claims this month and provides the defendant's service address.

## Governing Law

- **M.R.S.C.P. 4(b)** — Service by clerk
- **M.R.S.C.P. 12(a)(2)** — Disclosure hearing service

## Field Mappings

| Field Name | Type | Source | Notes |
|-----------|------|--------|-------|
| `Plaintiff` | Text | `matter.parties[role=plaintiff].full_name` | |
| `Location Town` | Text | `matter.court_location` | |
| `Docket No` | Text | `matter.docket_number` | |
| `Defendant` | Text | `matter.parties[role=defendant].full_name` | |
| Affiant name | Text | `matter.parties[role=plaintiff].full_name` | |
| `Statement of Claim` checkbox | CheckBox | deterministic | |
| `Notice of Disclosure Hearing` checkbox | CheckBox | deterministic | |
| Defendant service address | Text | `matter.parties[role=defendant].address` | Complete address |
| Date | Text | `today()` | |
| Signature | Text | *leave blank* | Under penalty of perjury |

## Validation Checklist

- [ ] Defendant's complete service address provided
- [ ] Correct document type checked
- [ ] Filed fewer than 3 small claims this month certified
- [ ] Date and signature present

## Related Forms Workflow

```
1. SC-001 — Statement of Claim
2. SC-006 (this form) — Request clerk to arrange service
3. Clerk mails via U.S. Mail → SC-005 acknowledgment
4. If mail fails → clerk may arrange sheriff service (if fee waived)
```
