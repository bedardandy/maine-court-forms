# CV-204 — Affidavit of Service – Forcible Entry & Detainer

**Form Number:** CV-204, Rev. 08/20
**Pages:** 1
**Fillable Fields:** 9
**Category:** Civil — Eviction / Service of Process
**Filing Fee:** None
**Companion Forms:** CV-007 (Complaint), CV-034 (Summons)

## Purpose

This affidavit documents that service of the FED summons and complaint was completed by alternative means after three unsuccessful attempts by the sheriff. It certifies that the documents were mailed and left at the defendant's abode, as required by 14 M.R.S. § 6004.

## Governing Law

- **14 M.R.S. § 6004** — Service in FED actions
- **M.R. Civ. P. 80D** — FED procedure

## Filing Requirements

1. Sheriff must have made 3 good faith attempts on 3 different days
2. Sheriff's written statement of attempts must be attached
3. Summons/complaint must also be mailed first class AND left at abode
4. Filed before hearing date

## Field Mappings

| Field Name | Type | Source | Notes |
|-----------|------|--------|-------|
| `Plaintiff` | Text | `matter.parties[role=plaintiff].full_name` | |
| `Location Town` | Text | `matter.court_location` | |
| `Docket No` | Text | `matter.docket_number` | |
| `Defendant` | Text | `matter.parties[role=defendant].full_name` | |
| County of sheriff service | Text | `matter.service_county` | |
| Date | Text | `today()` | |
| Signature | Text | *leave blank* | (Attorney for) Plaintiff signs |
| Notary/Clerk name | Text | *leave blank* | Notary completes |
| Notary date/signature | Text | *leave blank* | |

## AI Hints

- This is used for ALTERNATIVE service only — when personal service failed
- The sheriff's written statement of attempts is a required attachment
- County should match where the property is located

## Validation Checklist

- [ ] Sheriff's county identified
- [ ] Sheriff's written statement will be attached
- [ ] All three service requirements met (3 attempts, mail, abode)
- [ ] Date filled in
- [ ] Docket number matches FED case

## Related Forms Workflow

```
1. CV-007 — Complaint filed
2. CV-034 — Summons issued
3. Sheriff attempts personal service (3 times)
4. CV-204 (this form) — Affidavit of alternative service
5. Hearing proceeds
```
