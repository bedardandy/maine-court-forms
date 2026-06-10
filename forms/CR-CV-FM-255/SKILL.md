# CR-CV-FM-255 — Notice Regarding Electronic Service

**Form Number:** CR-CV-FM-255, Rev. 12/20
**Pages:** 1
**Fillable Fields:** 23
**Category:** Cross-Category — Electronic Service
**Filing Fee:** None
**Companion Forms:** None (standalone)

## Purpose

This form allows self-represented parties to opt in to receiving service of documents by email instead of regular mail. Represented parties are automatically subject to electronic service under the court rules. This form is exchanged between parties, NOT filed with the court.

## Governing Law

- **M.R. Civ. P. 5** — Service of pleadings and papers
- **M.R.U.Cr.P. 49(d)** — Electronic service in criminal cases

## Field Mappings

| Field Name | Type | Source | Notes |
|-----------|------|--------|-------|
| `Plaintiff/Petitioner` | Text | `matter.parties[role=plaintiff].full_name` | |
| `Superior Court` | CheckBox | `matter.court_type == "Superior"` | |
| `District Court` | CheckBox | `matter.court_type == "District"` | |
| `Unified Criminal Docket` | CheckBox | `matter.court_type == "UCD"` | |
| `County` | Text | `matter.court_county` | |
| `Defendant/Respondent` | Text | `matter.parties[role=defendant].full_name` | |
| `Location Town` | Text | `matter.court_location` | |
| `Docket No` | Text | `matter.docket_number` | |
| `Electronic Receipt` opt-in checkbox | CheckBox | AI decision | |
| Email address for e-service | Text | `party.email` | |
| `Electronic Service` opt-in checkbox | CheckBox | AI decision | Can send electronically |
| Email for sending | Text | `party.email` | |
| `Opt Out` checkbox | CheckBox | AI decision | Revoking prior opt-in |
| Date | Text | `today()` | |
| Signature | Text | *leave blank* | |
| Printed name | Text | `party.full_name` | |
| Mailing address | Text | `party.address` | |
| Phone | Text | `party.phone` | |
| Email (contact) | Text | `party.email` | |

## AI Hints

- This form is for SELF-REPRESENTED parties only
- Attorneys are already subject to e-service requirements
- Do NOT file with court — exchange directly with other parties
- Both "Electronic Receipt" (receiving) and "Electronic Service" (sending) can be opted into

## Validation Checklist

- [ ] Party is self-represented (not for attorneys)
- [ ] Email address provided if opting in
- [ ] Either opt-in or opt-out selected (not both)
- [ ] Form will be sent to other parties (not filed with court)

## Related Forms Workflow

```
1. Case initiated
2. CR-CV-FM-255 (this form) — Exchanged between parties
3. Subsequent service by email (if opted in)
```
