# CV-CR-JV-165 — Transcript and Audio Order Form

**Form Number:** CV-CR-JV-165, Rev. 04/25
**Pages:** 3
**Fillable Fields:** 55
**Category:** Cross-Category — Appeals / Records
**Filing Fee:** Varies (MP3 audio $50; paper transcript cost varies)
**Companion Forms:** Notice of Appeal (case-specific), CV-CR-166 (Motion for Transcript at State Expense)

## Purpose

This form orders transcripts or audio recordings of court proceedings, typically for use in appeals. Required when filing an appeal that needs a record of the lower court proceedings. Can also be used for personal reference or use in other pending cases.

## Governing Law

- **M.R. App. P. 5** — Record on appeal (transcripts required for appeals)

## Field Mappings

### Page 1 — Hearing Information & Request Details

| Field Name | Type | Source | Notes |
|-----------|------|--------|-------|
| Plaintiff/State attorney at hearing | Text | `matter.attorneys.plaintiff` | |
| Defendant attorney at hearing | Text | `matter.attorneys.defendant` | |
| GAL at hearing | Text | `matter.gal_name` | If applicable |
| Others present | Text | AI | |

### Purpose of Request

| Field Name | Type | Source | Notes |
|-----------|------|--------|-------|
| `Appeal` checkbox | CheckBox | `matter.transcript_purpose == "appeal"` | |
| `Law Court` | CheckBox | `matter.appeal_to == "Law Court"` | |
| `Superior Court` | CheckBox | `matter.appeal_to == "Superior"` | |
| `Sentence Review Panel` | CheckBox | `matter.appeal_to == "SRP"` | Criminal only |
| `Post-Conviction Review` | CheckBox | `matter.appeal_to == "PCR"` | |
| `Reference` checkbox | CheckBox | `matter.transcript_purpose == "reference"` | |
| `Personal Reference` | CheckBox | deterministic | |
| `For use in another case` | CheckBox | deterministic | |
| Other case docket number | Text | `matter.related_docket` | |
| Court-imposed due date | CheckBox/Text | AI | |

### Type of Request

| Field Name | Type | Source | Notes |
|-----------|------|--------|-------|
| `Paper Transcript` | CheckBox | deterministic | Required for appeals |
| `MP3 Audio Recording` | CheckBox | deterministic | |

### Payment

| Field Name | Type | Source | Notes |
|-----------|------|--------|-------|
| `Private Pay` | CheckBox | `matter.transcript_payment == "private"` | |
| `MCPDS` | CheckBox | `matter.transcript_payment == "mcpds"` | Public defender |
| `Judicial Branch` | CheckBox | `matter.transcript_payment == "judicial"` | |
| `Probate Court` | CheckBox | `matter.transcript_payment == "probate"` | |

### Hearing Details Table

| Field Name | Type | Source | Notes |
|-----------|------|--------|-------|
| Hearing dates (1-5) | Text | `matter.hearing_dates[]` | MM/DD/YYYY |
| Hearing types (1-5) | Text | `matter.hearing_types[]` | e.g., "Trial", "Motion hearing" |
| Courtroom (1-5) | Text | `matter.courtroom` | |

### Page 2 — Case Caption

| Field Name | Type | Source | Notes |
|-----------|------|--------|-------|
| `Plaintiff/Petitioner` | Text | `matter.parties[role=plaintiff].full_name` | |
| `Superior Court` | CheckBox | `matter.court_type == "Superior"` | |
| `District Court` | CheckBox | `matter.court_type == "District"` | |
| `Unified Criminal Docket` | CheckBox | `matter.court_type == "UCD"` | |
| `County` | Text | `matter.court_county` | |
| `Defendant/Respondent` | Text | `matter.parties[role=defendant].full_name` | |
| `Location Town` | Text | `matter.court_location` | |
| `Other Party` | Text | `matter.parties[role=other].full_name` | |
| `Docket No` | Text | `matter.docket_number` | |
| `IN RE` | Text | AI | For guardianship/juvenile/probate |

### Page 2-3 — Contact & Payment Info

| Field Name | Type | Source | Notes |
|-----------|------|--------|-------|
| Ordering party name | Text | `attorney.full_name or party.full_name` | |
| Address/phone/email | Text | `attorney.*` | |
| Bar number | Text | `attorney.bar_number` | |
| Payment method details | Text | AI | Credit card, check, etc. |

## Validation Checklist

- [ ] Purpose of request indicated
- [ ] At least one hearing date listed
- [ ] Payment method selected
- [ ] Case caption complete
- [ ] If appeal, paper transcript is checked (required by M.R. App. P. 5)
- [ ] Contact information complete

## Related Forms Workflow

```
1. Lower court proceeding occurs
2. Notice of Appeal filed (case-specific form)
3. CV-CR-JV-165 (this form) — Filed with Notice of Appeal
4. CV-CR-166 — Motion for Transcript at State Expense (if applicable)
5. Transcript prepared and filed
```
