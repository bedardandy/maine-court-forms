<!-- Reused from prior skills stash; verify against schema.json. -->
# CV-187 — Notice of Appeal – Recovery of Personal Property

**Form Number:** CV-187, Rev. 06/14
**Pages:** 1
**Fillable Fields:** 23
**Category:** Civil — Personal Property Recovery / Appeal
**Filing Fee:** Appeal filing fee required
**Companion Forms:** CV-183 (original Complaint), CV-CR-JV-165 (Transcript Order Form)

## Purpose

This form is used to appeal a judgment in a personal property recovery (summary process) action under 14 M.R.S. § 7071(8). The appellant may appeal to the Law Court or to Superior Court for a jury trial de novo.

## Governing Law

- **14 M.R.S. § 7071(8)** — Appeal of personal property recovery judgment
- **M.R. App. P. 5(d)** — Statement in lieu of transcript

## Filing Requirements

1. Must be filed in the court that issued the judgment
2. Must include filing fee or motion to waive
3. If represented by attorney, must include bar number
4. Transcript Order Form must be attached (or indicate no transcript)

## Field Mappings

| Field Name | Type | Source | Notes |
|-----------|------|--------|-------|
| `Plaintiff` | Text | `matter.parties[role=plaintiff].full_name` | |
| `Location Town` | Text | `matter.court_location` | |
| `Docket No` | Text | `matter.docket_number` | |
| `Defendant` | Text | `matter.parties[role=defendant].full_name` | |
| Appellant name | Text | `matter.parties[role=appellant].full_name` | Person appealing |
| Date of order appealed | Text | `matter.events[type=judgment].date` | |
| Appeal reasons | Text | AI from matter notes | Legal basis for appeal |
| `as follows` checkbox | CheckBox | AI | Reasons on this form |
| `attached` checkbox | CheckBox | AI | Reasons on separate sheet |
| `Law Court` checkbox | CheckBox | `matter.appeal_to == "Law Court"` | |
| `Superior Court jury trial` checkbox | CheckBox | `matter.appeal_to == "Superior"` | |
| `Transcript Order attached` checkbox | CheckBox | deterministic | |
| `No transcript` checkbox | CheckBox | deterministic | |
| `No recording available` checkbox | CheckBox | deterministic | |
| Date | Text | `today()` | |
| Signature | Text | *leave blank* | |
| Address | Text | `attorney.address or appellant.address` | |
| Printed name | Text | `attorney.full_name or appellant.full_name` | |
| Bar number | Text | `attorney.bar_number` | If attorney |

## AI Hints

- Appeal reasons should cite specific legal errors in the District Court's ruling
- Jury trial de novo requires showing genuine issue regarding right to jury trial

## Validation Checklist

- [ ] Appellant identified
- [ ] Date of order appealed is specified
- [ ] Appeal destination checked (Law Court or Superior Court)
- [ ] Transcript disposition indicated
- [ ] If attorney, bar number included
- [ ] Filing fee or waiver motion accompanies

## Related Forms Workflow

```
1. CV-183 — Original complaint
2. District Court judgment
3. CV-187 (this form) — Notice of Appeal
4. CV-CR-JV-165 — Transcript Order Form (if needed)
5. Superior Court or Law Court proceedings
```
