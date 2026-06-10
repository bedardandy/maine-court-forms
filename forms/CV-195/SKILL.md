# CV-195 — Request for Issuance of Writ of Possession

**Form Number:** CV-195, Rev. 02/13
**Pages:** 1
**Fillable Fields:** 15
**Category:** Civil — Eviction / FED Enforcement
**Filing Fee:** Writ fee
**Companion Forms:** CV-007 (Complaint), CV-204 (Affidavit of Service), judgment

## Purpose

After obtaining a judgment in a Forcible Entry and Detainer (eviction) case, this form requests the court to issue a Writ of Possession directing the sheriff to remove the tenant and restore possession to the landlord. Different sections apply depending on whether the judgment was based on a 30-day or 7-day Notice to Quit.

## Governing Law

- **14 M.R.S. § 6005** — Judgment and writ of possession in FED
- **14 M.R.S. § 6002** — Grounds; reinstatement provision for rent arrearage cases

## Filing Requirements

1. Judgment must have been entered in plaintiff's favor
2. For 7-day NTQ cases: must certify defendant has not paid arrearages to reinstate
3. Cannot issue if tenant paid rent arrearages, current rent, filing fees, and service costs

## Field Mappings

| Field Name | Type | Source | Notes |
|-----------|------|--------|-------|
| `Plaintiff` | Text | `matter.parties[role=plaintiff].full_name` | Landlord |
| `Location Town` | Text | `matter.court_location` | |
| `Docket No` | Text | `matter.docket_number` | |
| `Defendants` | Text | `matter.parties[role=defendant].full_name` | Tenant(s) |
| Requestor name (30-day section) | Text | `matter.parties[role=plaintiff].full_name` | If 30-day NTQ |
| Judgment date (30-day section) | Text | `matter.events[type=judgment].date` | |
| Requestor name (7-day section) | Text | `matter.parties[role=plaintiff].full_name` | If 7-day NTQ |
| Judgment date (7-day section) | Text | `matter.events[type=judgment].date` | |
| Date | Text | `today()` | |
| Signature | Text | *leave blank* | |
| Printed name and bar number | Text | `attorney.full_name` + `attorney.bar_number` | |
| Address | Text | `attorney.address` | |

## AI Hints

### 30-Day vs 7-Day NTQ
- **30-day NTQ**: No-cause termination of tenancy at will. Fill the first section only.
- **7-day NTQ**: Rent arrearage. Fill the second section. Must certify tenant hasn't paid to reinstate.
- Only one section should be completed based on the type of NTQ served.

### Reinstatement Right (7-Day Only)
- Tenant can reinstate by paying all arrearages + current rent + filing fees + service costs
- If tenant has paid, writ CANNOT issue — do not file this form

## Validation Checklist

- [ ] Correct section filled (30-day OR 7-day, not both)
- [ ] Judgment date is specified
- [ ] For 7-day: compliance certification included
- [ ] Docket number matches FED case
- [ ] Date and signature present

## Related Forms Workflow

```
1. CV-007 — FED Complaint
2. CV-034 — Summons served
3. CV-204 — Affidavit of Service
4. Hearing → Judgment for plaintiff
5. CV-195 (this form) — Request for Writ
6. Sheriff executes writ (eviction)
```
