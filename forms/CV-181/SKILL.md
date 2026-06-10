# CV-181 — Request for (Alias/Pluries) Writ of Execution

**Form Number:** CV-181, Rev. 08/20
**Pages:** 1
**Fillable Fields:** 21
**Category:** Civil — Judgment Enforcement
**Filing Fee:** Writ fee (set by court)
**Companion Forms:** Original Writ of Execution

## Purpose

This form requests a renewal writ of execution when the original writ has expired or been returned unsatisfied. It allows a judgment creditor to obtain a new writ to enforce a money judgment, provided certain conditions are met under 14 M.R.S. § 4651-A.

## Governing Law

- **14 M.R.S. § 4651-A** — Renewal writs of execution
- **14 M.R.S. § 4656** — Lost or destroyed writs
- **14 M.R.S. § 2018** — Void executions
- **M.R. Civ. P. 11** — Signing and verification

## Filing Requirements

1. Original writ must have been issued less than 10 years ago
2. Judgment must not yet be satisfied
3. Must certify compliance with all conditions in item 3
4. Must mail copy to judgment debtor
5. If original writ lost/destroyed, must attach affidavit per § 4656

## Field Mappings

| Field Name | Type | Source | Notes |
|-----------|------|--------|-------|
| `Plaintiff` | Text | `matter.parties[role=plaintiff].full_name` | Judgment creditor |
| `Superior Court` | CheckBox | `matter.court_type == "Superior"` | |
| `District Court` | CheckBox | `matter.court_type == "District"` | |
| `County` | Text | `matter.court_county` | |
| `Location Town` | Text | `matter.court_location` | |
| `Defendant` | Text | `matter.parties[role=defendant].full_name` | Judgment debtor |
| `Docket No` | Text | `matter.docket_number` | |
| `plaintiff` checkbox | CheckBox | `matter.requesting_party == "plaintiff"` | Who requests |
| `defendant` checkbox | CheckBox | `matter.requesting_party == "defendant"` | |
| Original writ issue date | Text | `matter.events[type=writ_issued].date` | |
| Original amount (debt/damage) | Text | `matter.judgment_amount` | |
| Original costs | Text | `matter.judgment_costs` | |
| Writ returned to court (date) | Text | `matter.events[type=writ_returned].date` | |
| `Was returned` checkbox | CheckBox | deterministic | |
| `Was lost/destroyed` checkbox | CheckBox | deterministic | |
| `Is attached` checkbox | CheckBox | deterministic | |
| Debtor mailing address | Text | `matter.parties[role=defendant].address` | For item 3e |
| Date | Text | `today()` | |
| Signature | Text | *leave blank* | Applicant signs under oath |
| Notary section | Text | *leave blank* | Clerk/notary completes |

## AI Hints

- Calculate whether original writ is less than 10 years old
- Verify judgment amount hasn't been partially satisfied (adjust if needed)
- Debtor address is critical — must be current known address

## Validation Checklist

- [ ] Original writ date is within 10 years
- [ ] Judgment amounts are specified
- [ ] One disposition of original writ is checked (returned/lost/attached)
- [ ] Debtor mailing address provided for item 3e
- [ ] Date filled in
- [ ] Requesting party checkbox matches

## Related Forms Workflow

```
1. Original judgment entered
2. Original writ of execution issued
3. CV-181 (this form) — Renewal request
4. New writ issued by court
5. Sheriff executes on debtor's property
```
