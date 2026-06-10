# CV-206 — Notice of Appeal – Forcible Entry and Detainer

**Form Number:** CV-206, Rev. 04/14
**Pages:** 2
**Fillable Fields:** 24
**Category:** Civil — Eviction / Appeal
**Filing Fee:** Appeal filing fee
**Companion Forms:** CV-007 (original Complaint), CV-CR-JV-165 (Transcript Order Form)

## Purpose

This form is used to appeal a judgment in a Forcible Entry and Detainer (eviction) case from District Court to Superior Court. The appellant may appeal on questions of law or request a jury trial de novo. Defendants must pay current month's rent or arrearages before filing.

## Governing Law

- **14 M.R.S. § 6008** — Appeal in FED cases
- **M.R. Civ. P. 76F(c)** — Statement in lieu of transcript

## Filing Requirements

1. Defendant must pay current month's rent or rent arrearage before filing (§ 6008(2))
2. Must file in the court that issued the judgment
3. Transcript Order Form should accompany if requesting transcript
4. Sworn under penalty of perjury

## Field Mappings

### Page 1 — Appeal Details

| Field Name | Type | Source | Notes |
|-----------|------|--------|-------|
| `Plaintiff` | Text | `matter.parties[role=plaintiff].full_name` | |
| `Location Town` | Text | `matter.court_location` | |
| `Docket No` | Text | `matter.docket_number` | |
| `Defendant` | Text | `matter.parties[role=defendant].full_name` | |
| Appellant name | Text | `matter.parties[role=appellant].full_name` | |
| Date of judgment/order | Text | `matter.events[type=judgment].date` | |
| `appeal to Superior Court on questions of law` | CheckBox | AI | |
| Questions of law text | Text | AI from matter notes | Legal issues |
| `appeal to Superior Court for jury trial de novo` | CheckBox | AI | |
| Jury trial facts | Text | AI from matter notes | Why jury trial warranted |
| Rent payment checkboxes | CheckBox | AI | Defendant must check one |
| `Transcript Order attached` | CheckBox | deterministic | |
| `No transcript` | CheckBox | deterministic | |
| `No recording available` | CheckBox | deterministic | |

### Page 2 — Signature & Notarization

| Field Name | Type | Source | Notes |
|-----------|------|--------|-------|
| Date | Text | `today()` | |
| Signature | Text | *leave blank* | |
| Printed name | Text | `appellant.full_name` | |
| Address | Text | `appellant.address` | |
| Notary section | Text | *leave blank* | |

## AI Hints

- If defendant is appealing, they MUST pay rent before filing
- Questions of law should cite specific legal errors
- Jury trial de novo requires genuine factual dispute

## Validation Checklist

- [ ] Appellant identified
- [ ] Judgment date specified
- [ ] At least one appeal type checked
- [ ] If defendant: rent payment checkbox checked
- [ ] Transcript disposition indicated
- [ ] Date and signature present

## Related Forms Workflow

```
1. CV-007 — Original FED Complaint
2. District Court judgment
3. CV-206 (this form) — Notice of Appeal
4. CV-CR-JV-165 — Transcript Order (if needed)
5. Superior Court proceedings
```
