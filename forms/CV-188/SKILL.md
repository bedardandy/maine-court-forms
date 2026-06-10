# CV-188 — Request for Issuance of Writ of Possession for

**Form Number:** CV-188, Rev. 06/14
**Pages:** 1
**Fillable Fields:** 17
**Category:** Civil — Personal Property Recovery / Enforcement
**Filing Fee:** Writ fee
**Companion Forms:** CV-183 (Complaint), judgment

## Purpose

After obtaining a judgment in a personal property recovery action, this form requests the court to issue a Writ of Possession directing the sheriff to retrieve the personal property and deliver it to the plaintiff.

## Governing Law

- **14 M.R.S. § 7071(6)** — Writ of possession for personal property

## Field Mappings

| Field Name | Type | Source | Notes |
|-----------|------|--------|-------|
| `Plaintiff` | Text | `matter.parties[role=plaintiff].full_name` | |
| `Location Town` | Text | `matter.court_location` | |
| `Docket No` | Text | `matter.docket_number` | |
| `Defendant` | Text | `matter.parties[role=defendant].full_name` | |
| Requestor name (in body) | Text | `matter.parties[role=plaintiff].full_name` | |
| Judgment date | Text | `matter.events[type=judgment].date` | |
| Date | Text | `today()` | |
| Signature | Text | *leave blank* | |
| `Plaintiff` checkbox | CheckBox | `matter.signing_party == "plaintiff"` | |
| `Attorney` checkbox | CheckBox | `matter.signing_party == "attorney"` | |
| Name field | Text | `attorney.full_name or plaintiff.full_name` | |
| Address field | Text | `attorney.address or plaintiff.address` | |

## Validation Checklist

- [ ] Judgment date is specified
- [ ] Requestor is the prevailing party
- [ ] Docket number matches

## Related Forms Workflow

```
1. CV-183 — Complaint filed
2. Judgment for plaintiff
3. CV-188 (this form) — Request for writ
4. Sheriff executes writ
```
