<!-- Reused from prior skills stash; verify against schema.json. -->
# CV-256 — Residential FED Information Sheet and Mediation Request

**Form Number:** CV-256
**Fillable Fields:** 12
**Category:** Civil — Eviction
**Court:** District Court
**Related Forms:** CV-007, CV-100

## Purpose

Information sheet for tenants facing eviction, with option to request mediation. Must be served with the Notice to Quit or complaint/summons.

## Governing Law

- **14 M.R.S. §§ 6001-6016 (FED statutes)**

## Field Mapping Summary

### Page 1

| Field Name | Type | Source |
|-----------|------|--------|
| `I would like mediation in my case` | CheckBox | From matter data |
| `the defendant tenant` | CheckBox | From matter data |
| `the plaintiff landlord` | CheckBox | From matter data |
| `My Name is please print` | Text | `signer.full_name` |
| `My cell phone number is` | Text | `party.phone` |
| `My email address is` | Text | `party.email` |
| `The name of the other party listed on the summons and complaint is` | Text | From matter data |
| `To the best of my knowledge the other partys cell phone number is` | Text | `party.phone` |
| `To the best of my knowledge the other partys email address is` | Text | `party.email` |
| `The address of rental property is` | Text | `party.address` |
| `Date mmddyyyy` | Text | `today()` or relevant date |
| `undefined` | Text | From matter data |


## AI Hints

Two pages. Page 1: information about legal help (Pine Tree Legal, Legal Services for Maine Elders), explanation of Notice to Quit and eviction process. Page 2: mediation request section — tenant or landlord can request mediation by filling out contact info and returning to court.

## Validation Checklist

- [ ] Case caption is complete (parties, court, docket number)
- [ ] Date is filled in (mm/dd/yyyy format)
- [ ] Signature line identified (leave blank for physical signature)
- [ ] Related forms prepared if needed (CV-007, CV-100)
