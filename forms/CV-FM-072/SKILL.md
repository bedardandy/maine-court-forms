# CV-FM-072 — Motion for Service by Alternate Means and

**Form Number:** CV-FM-072, Rev. 08/20
**Pages:** 2
**Fillable Fields:** 56
**Category:** Cross-Category — Civil/Family Service of Process
**Filing Fee:** Motion filing fee may apply
**Companion Forms:** CV-FM-036 (Acknowledgment), CV-FM-202 (Affidavit of Alternate Service Completion)

## Purpose

When standard service methods fail (mail acknowledgment not returned, sheriff unable to serve), this form requests court permission to serve by alternate means: leaving at abode, publication in newspaper, or other means. Includes an affidavit documenting failed service attempts.

## Governing Law

- **M.R. Civ. P. 4(g)** — Service by alternate means

## Field Mappings

### Page 1 — Case Caption & Service Method Requested

| Field Name | Type | Source | Notes |
|-----------|------|--------|-------|
| `Plaintiff` | Text | `matter.parties[role=plaintiff].full_name` | |
| `Superior Court` | CheckBox | `matter.court_type == "Superior"` | |
| `District Court` | CheckBox | `matter.court_type == "District"` | |
| `County` | Text | `matter.court_county` | |
| `Location Town` | Text | `matter.court_location` | |
| `Defendant` | Text | `matter.parties[role=defendant].full_name` | |
| `Docket No` | Text | `matter.docket_number` | |

### Requested Service Method (check ONE)

| Field Name | Type | Source | Notes |
|-----------|------|--------|-------|
| Option 1 — Leave at abode | CheckBox | AI decision | |
| Abode address | Text | `matter.parties[role=defendant].address` | |
| Option 2 — Publication | CheckBox | AI decision | |
| Newspaper name | Text | AI | Local newspaper |
| Newspaper location | Text | AI | County/municipality |
| Option 3 — Other means | CheckBox | AI decision | |
| Other means description | Text | AI | E.g., email, social media |

### Affidavit of Failed Attempts (check ALL that apply)

| Field Name | Type | Source | Notes |
|-----------|------|--------|-------|
| 1 — Mailed CV-036, waited 20 days | CheckBox | deterministic | |
| Mailing address | Text | `matter.parties[role=defendant].address` | |
| Mailing recipient name | Text | `matter.parties[role=defendant].full_name` | |
| 2 — Sheriff attempted service | CheckBox | deterministic | |
| Sheriff's county | Text | `matter.service_county` | |
| 3 — Family matters: certified mail | CheckBox | deterministic | Family cases only |
| Certified mail details | Text | AI | |

### Page 2 — Oath & Signature

| Field Name | Type | Source | Notes |
|-----------|------|--------|-------|
| Date | Text | `today()` | |
| Signature | Text | *leave blank* | Under penalty of perjury |
| Notary section | Text | *leave blank* | |

## AI Hints

### Choosing Service Method
- **Leave at abode**: Most common. Use when you know the address but person avoids service.
- **Publication**: Use when defendant's whereabouts are unknown. Must use newspaper in county most likely to reach them.
- **Other**: Courts increasingly allow service by email or social media in appropriate cases.

### Family Matters
- Additional requirement: must also attempt certified/registered mail (item 3)
- This applies to divorce, parental rights, and other family cases

## Validation Checklist

- [ ] Exactly ONE service method requested
- [ ] At least one failed attempt documented in affidavit
- [ ] Sheriff's statement will be attached (if sheriff attempted)
- [ ] For family matters: certified mail also attempted
- [ ] Date and signature present

## Related Forms Workflow

```
1. CV-FM-036 — Acknowledgment sent (not returned)
2. Sheriff attempts service (unsuccessful)
3. CV-FM-072 (this form) — Motion for alternate service
4. Court issues Order for Service by Alternate Means
5. Serve by ordered method
6. CV-FM-202 — Affidavit that alternate service completed
```
