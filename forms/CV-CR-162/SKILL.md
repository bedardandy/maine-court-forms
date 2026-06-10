# CV-CR-162 — Notice of Appeal

**Form Number:** CV-CR-162, Rev. 12/18
**Pages:** 1
**Fillable Fields:** 29
**Category:** Cross-Category — Civil/Criminal Appeal
**Filing Fee:** Appeal filing fee
**Companion Forms:** CV-CR-JV-165 (Transcript Order Form)

## Purpose

General-purpose Notice of Appeal form used in civil and criminal cases to appeal from a judgment, order, or ruling to a higher court. This is the standard appeal form when no case-specific appeal form exists (e.g., CV-206 for FED appeals, CV-187 for personal property appeals).

## Governing Law

- **M.R. App. P. 2** — Appeal as of right
- **M.R. App. P. 5(d)** — Statement in lieu of transcript

## Field Mappings

| Field Name | Type | Source | Notes |
|-----------|------|--------|-------|
| `Superior Court` | CheckBox | `matter.court_type == "Superior"` | |
| `District Court` | CheckBox | `matter.court_type == "District"` | |
| `Unified Criminal Docket` | CheckBox | `matter.court_type == "UCD"` | |
| `County` | Text | `matter.court_county` | |
| `Location Town` | Text | `matter.court_location` | |
| `Docket No` | Text | `matter.docket_number` | |
| Appellant name (in body) | Text | `matter.parties[role=appellant].full_name` | |
| Date of order appealed | Text | `matter.events[type=order].date` | |
| `This is a civil appeal` | CheckBox | `matter.case_type == "civil"` | |
| `Maine Tort Claims Act` | CheckBox | AI | If applicable, clerk sends to AG |
| `criminal appeal` checkbox | CheckBox | `matter.case_type == "criminal"` | |
| `presently confined at` | CheckBox | AI | Criminal - in custody |
| Confinement location | Text | AI | Jail/prison name |
| `not in custody` | CheckBox | AI | Criminal - free |
| Defendant address | Text | `matter.parties[role=defendant].address` | |
| `Transcript Order attached` | CheckBox | deterministic | |
| `No transcript ordered` | CheckBox | deterministic | |
| `No recording available` | CheckBox | deterministic | |
| Date | Text | `today()` | |
| Signature | Text | *leave blank* | |
| Address of appellant/attorney | Text | `attorney.address or appellant.address` | |
| Printed name | Text | `attorney.full_name or appellant.full_name` | |
| Bar number | Text | `attorney.bar_number` | If attorney |

## AI Hints

- Use this form for appeals NOT covered by case-specific forms (CV-206, CV-187, SC-007)
- For Maine Tort Claims Act cases, clerk must notify Attorney General
- Criminal appellants: indicate custody status

## Validation Checklist

- [ ] Court type correctly identified
- [ ] Appellant named
- [ ] Date of order appealed specified
- [ ] Civil or Criminal checked
- [ ] Transcript disposition indicated
- [ ] If attorney, bar number included
- [ ] Filing fee or waiver accompanies

## Related Forms Workflow

```
1. Lower court judgment/order
2. CV-CR-162 (this form) — Notice of Appeal
3. CV-CR-JV-165 — Transcript Order Form
4. Appellate proceedings
```
