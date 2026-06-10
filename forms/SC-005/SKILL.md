# SC-005 — Acknowledgment of Service

**Form Number:** SC-005, Rev. 02/20
**Pages:** 1
**Fillable Fields:** 14
**Category:** Small Claims — Service of Process
**Filing Fee:** None
**Companion Forms:** SC-001 (Statement of Claim), SC-010 (Service Instructions)

## Purpose

This form is sent to the defendant along with the Statement of Claim (or Notice of Disclosure Hearing). The defendant signs and returns it to acknowledge receipt, which constitutes valid service. If not returned within 20 days, alternative service methods are needed.

## Governing Law

- **M.R.S.C.P. 4** — Service in small claims

## Field Mappings

| Field Name | Type | Source | Notes |
|-----------|------|--------|-------|
| `Plaintiff/Judgment Creditor` | Text | `matter.parties[role=plaintiff].full_name` | |
| `Location Town` | Text | `matter.court_location` | |
| `Docket No` | Text | `matter.docket_number` | |
| `Defendant/Judgment Debtor` | Text | `matter.parties[role=defendant].full_name` | |
| `Statement of Claim` checkbox | CheckBox | deterministic | What is being served |
| `Notice of Disclosure Hearing` checkbox | CheckBox | deterministic | |
| Date (acknowledgment) | Text | *leave blank* | Defendant fills |
| Signature | Text | *leave blank* | Defendant signs |
| Printed name | Text | *leave blank* | Defendant fills |
| Title/authority | Text | *leave blank* | If accepting on behalf of entity |

## AI Hints

- This form is mostly filled by the DEFENDANT, not the plaintiff
- Plaintiff only fills the caption (party names, court, docket) and checks the type of document being served
- Two copies should be sent to defendant with a stamped return envelope

## Validation Checklist

- [ ] Caption information matches case
- [ ] Correct document type checked (Statement of Claim or Disclosure)
- [ ] Acknowledgment section left blank for defendant

## Related Forms Workflow

```
1. SC-001 — Statement of Claim prepared
2. SC-005 (this form) — Sent with claim to defendant
3. Defendant signs and returns within 20 days
4. File signed acknowledgment with court
```
