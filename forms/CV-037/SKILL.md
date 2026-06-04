<!-- Reused from prior skills stash; verify against schema.json. -->
# CV-037 — Subpoena for Hearing on Motion

**Form Number:** CV-037, Rev. 06/14
**Pages:** 2
**Fillable Fields:** 22
**Category:** Civil — Contempt / Enforcement
**Filing Fee:** None for subpoena issuance
**Companion Forms:** Motion for Contempt (attorney-drafted), Return of Service (page 2)

## Purpose

This subpoena compels a party to appear at a hearing on a Motion for Contempt filed against them. It commands appearance at a specific court date/time and may also require production of documents. Page 2 contains the Return of Service for the process server.

## Governing Law

- **M.R. Civ. P. 66(d)** — Contempt proceedings
- **M.R. Civ. P. 45** — Subpoenas generally

## Filing Requirements

1. Must be served with a copy of the Motion for Contempt attached
2. The opposing party must file a written answer at least 3 days before hearing
3. May be issued by clerk or attorney

## Field Mappings

### Page 1 — Case Caption & Subpoena

| Field Name | Type | Source | Notes |
|-----------|------|--------|-------|
| `Plaintiff` | Text | `matter.parties[role=plaintiff].full_name` | |
| `Defendant` | Text | `matter.parties[role=defendant].full_name` | |
| `Superior Court` | CheckBox | `matter.court_type == "Superior"` | |
| `District Court` | CheckBox | `matter.court_type == "District"` | |
| `County` | Text | `matter.court_county` | |
| `Location Town` | Text | `matter.court_location` | |
| `Docket No` | Text | `matter.docket_number` | |
| `TO` (subpoena recipient) | Text | `matter.parties[role=respondent].full_name` | Person being subpoenaed |
| `Plaintiff_2` (recipient is plaintiff) | CheckBox | AI decision | Check if subpoenaed person is plaintiff |
| `Defendant_2` (recipient is defendant) | CheckBox | AI decision | Check if subpoenaed person is defendant |
| Hearing date | Text | `matter.events[type=hearing].date` | MM/DD/YYYY |
| Hearing time | Text | `matter.events[type=hearing].time` | |
| `am` | CheckBox | AI from hearing time | |
| `pm` | CheckBox | AI from hearing time | |
| Court location address | Text | `matter.court_address` | |
| Document production checkbox | CheckBox | AI decision | Check if documents requested |
| Document description | Text | AI | What to bring |
| `Plaintiff_3` (issued on behalf of) | CheckBox | `matter.filing_party == "plaintiff"` | |
| `Defendant_3` | CheckBox | `matter.filing_party == "defendant"` | |
| Date issued | Text | `today()` | |
| Signature | Text | *leave blank* | Clerk or attorney signs |
| `Deputy Clerk` / `Attorney at Law` | CheckBox | deterministic | Who is issuing |

### Page 2 — Return of Service

| Field Name | Type | Source | Notes |
|-----------|------|--------|-------|
| County of service | Text | `matter.service_county` | |
| Service date | Text | `matter.events[type=service].date` | |
| Additional service details | Text | *leave blank* | Process server completes |

## AI Hints

- Determine who is being subpoenaed (usually the defendant in a contempt motion)
- If document production is requested, list specific documents relevant to the contempt allegation
- Common contempt scenarios: failure to pay support, failure to comply with court order

## Validation Checklist

- [ ] Correct party identified as subpoena recipient
- [ ] Hearing date and time are filled in
- [ ] AM/PM is checked
- [ ] Court location is complete
- [ ] Motion for Contempt will be attached when served
- [ ] Issued-on-behalf-of matches the moving party

## Related Forms Workflow

```
1. Motion for Contempt (attorney-drafted)
2. CV-037 (this form) — Subpoena
3. Service on opposing party
4. Hearing
```

> **Note:** a dedicated fill recipe exists for this form in `engine/recipes/`. The recipe is the authoritative field mapping; this doc is the human-readable companion.
