# CV-FM-202 — Affidavit that Service was Completed by Alternate

**Form Number:** CV-FM-202, Rev. 08/20
**Pages:** 2
**Fillable Fields:** 24
**Category:** Cross-Category — Civil/Family Service of Process
**Filing Fee:** None
**Companion Forms:** CV-FM-072 (Motion for Alternate Service), Court Order for Alternate Service

## Purpose

After the court grants alternate service and the party completes service by the ordered method, this affidavit documents that service was completed as directed. It is filed with the court to prove service.

## Governing Law

- **M.R. Civ. P. 4(g)(3)** — Proof of alternate service

## Field Mappings

| Field Name | Type | Source | Notes |
|-----------|------|--------|-------|
| `Plaintiff` | Text | `matter.parties[role=plaintiff].full_name` | |
| `Superior Court` | CheckBox | `matter.court_type == "Superior"` | |
| `District Court` | CheckBox | `matter.court_type == "District"` | |
| `County` | Text | `matter.court_county` | |
| `Location Town` | Text | `matter.court_location` | |
| `Defendant` | Text | `matter.parties[role=defendant].full_name` | |
| `Docket No` | Text | `matter.docket_number` | |

### Service Method Completed (check applicable)

| Field Name | Type | Source | Notes |
|-----------|------|--------|-------|
| Left at abode | CheckBox | deterministic | |
| Abode address | Text | `matter.parties[role=defendant].address` | |
| Published in newspaper | CheckBox | deterministic | |
| Newspaper name | Text | AI | |
| Mailed published copy | CheckBox | deterministic | If address known |
| Other means | CheckBox | deterministic | |
| Other means description | Text | AI | How served |
| Safeguards followed | CheckBox | deterministic | |
| Safeguards description | Text | AI | What safeguards |
| `Followed all directions` | CheckBox | deterministic | |
| Date | Text | `today()` | |
| Signature | Text | *leave blank* | Under penalty of perjury |
| Notary section | Text | *leave blank* | |

## Validation Checklist

- [ ] Service method matches what court ordered
- [ ] Address/newspaper details match the order
- [ ] Safeguards section completed if court ordered safeguards
- [ ] Date and signature present

## Related Forms Workflow

```
1. CV-FM-072 — Motion for Alternate Service
2. Court Order for Service by Alternate Means
3. Service completed by ordered method
4. CV-FM-202 (this form) — Proof of completion
5. Case proceeds to hearing
```
