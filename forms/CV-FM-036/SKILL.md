<!-- Reused from prior skills stash; verify against schema.json. -->
# CV-FM-036 — Acknowledgment of Receipt of Summons and

**Form Number:** CV-FM-036, Rev. 08/24
**Pages:** 2
**Fillable Fields:** 18
**Category:** Cross-Category — Civil/Family Service of Process
**Filing Fee:** None
**Companion Forms:** Summons, Complaint

## Purpose

This form is sent with the summons and complaint (or post-judgment motion, or notice of foreign judgment registration) to the opposing party. When signed and returned, it constitutes valid service under M.R. Civ. P. 4(c)(1). If not returned within 20 days, the court may order the non-returning party to pay sheriff service costs.

## Governing Law

- **M.R. Civ. P. 4(c)(1)** — Service by mail with acknowledgment

## Field Mappings

### Page 1 — Document Being Served

| Field Name | Type | Source | Notes |
|-----------|------|--------|-------|
| Document type checkboxes | CheckBox | deterministic | What is being served |

### Page 2 — Case Caption & Acknowledgment

| Field Name | Type | Source | Notes |
|-----------|------|--------|-------|
| `Plaintiff/Petitioner` | Text | `matter.parties[role=plaintiff].full_name` | |
| `Superior Court` | CheckBox | `matter.court_type == "Superior"` | |
| `District Court` | CheckBox | `matter.court_type == "District"` | |
| `County` | Text | `matter.court_county` | |
| `Location Town` | Text | `matter.court_location` | |
| `Defendant/Respondent` | Text | `matter.parties[role=defendant].full_name` | |
| `Docket No` | Text | `matter.docket_number` | |
| Date | Text | *leave blank* | Recipient fills |
| Signature | Text | *leave blank* | Recipient signs |
| Printed name | Text | *leave blank* | Recipient fills |

## AI Hints

- Like SC-005, this form is mostly completed by the RECIPIENT
- The filing party fills the caption and selects the document type
- Send two copies with a stamped return envelope

## Validation Checklist

- [ ] Caption information complete
- [ ] Correct document type selected
- [ ] Acknowledgment section left blank for recipient
- [ ] Self-addressed stamped envelope included

## Related Forms Workflow

```
1. Complaint/Motion prepared
2. CV-FM-036 (this form) — Sent with documents
3. Recipient signs and returns within 20 days
4. If not returned → CV-FM-072 (Motion for Service by Alternate Means)
```
