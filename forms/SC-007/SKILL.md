# SC-007 — Notice of Small Claims Appeal

**Form Number:** SC-007, Rev. 02/20
**Pages:** 2
**Fillable Fields:** 26
**Category:** Small Claims — Appeal
**Filing Fee:** Appeal filing fee
**Companion Forms:** CV-CR-JV-165 (Transcript Order Form)

## Purpose

This form is used to appeal a small claims judgment to Superior Court. Both plaintiffs and defendants may appeal, but defendants who request a jury trial de novo must also file an affidavit with specific facts showing a genuine issue of material fact.

## Governing Law

- **M.R.S.C.P. 11(b)** — Small claims appeals

## Field Mappings

### Page 1

| Field Name | Type | Source | Notes |
|-----------|------|--------|-------|
| `Plaintiff` | Text | `matter.parties[role=plaintiff].full_name` | |
| `Location Town` | Text | `matter.court_location` | |
| `Docket No` | Text | `matter.docket_number` | |
| `Defendant` | Text | `matter.parties[role=defendant].full_name` | |
| Judgment date | Text | `matter.events[type=judgment].date` | |
| Judgment amount ($) | Text | `matter.judgment_amount` | |

#### If Plaintiff Appealing:

| Field Name | Type | Source | Notes |
|-----------|------|--------|-------|
| `Transcript Order Form attached` (plaintiff) | CheckBox | deterministic | |
| `No transcript available` (plaintiff) | CheckBox | deterministic | |
| Date (plaintiff) | Text | `today()` | |
| Plaintiff signature | Text | *leave blank* | |
| Plaintiff address | Text | `matter.parties[role=plaintiff].address` | |

#### If Defendant Appealing:

| Field Name | Type | Source | Notes |
|-----------|------|--------|-------|
| `do not request jury trial` | CheckBox | AI | |
| `do request jury trial` | CheckBox | AI | |
| Grounds for appeal | Text | AI from matter notes | |
| `Transcript Order Form attached` (defendant) | CheckBox | deterministic | |
| `No transcript available` (defendant) | CheckBox | deterministic | |
| Date (defendant) | Text | `today()` | |
| Defendant signature | Text | *leave blank* | |
| Defendant address | Text | `matter.parties[role=defendant].address` | |

## AI Hints

- Plaintiff appeals go directly to Superior Court (no jury trial option for plaintiff)
- Defendant can request jury trial de novo but must file supporting affidavit
- Appeal grounds should cite specific legal or factual errors

## Validation Checklist

- [ ] Correct section completed (plaintiff OR defendant)
- [ ] Judgment date and amount specified
- [ ] Transcript disposition indicated
- [ ] If defendant requesting jury trial, grounds specified and affidavit filed
- [ ] Date and signature present
- [ ] Filing fee or waiver accompanies

## Related Forms Workflow

```
1. SC-001 — Original claim
2. Small claims judgment
3. SC-007 (this form) — Appeal
4. CV-CR-JV-165 — Transcript Order (if needed)
5. Superior Court proceedings
```
