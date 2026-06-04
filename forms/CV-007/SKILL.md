<!-- Reused from prior skills stash; verify against schema.json. -->
# CV-007 — Complaint for Residential Forcible Entry

**Form Number:** CV-007, Rev. 04/23
**Pages:** 2
**Fillable Fields:** 68
**Category:** Civil — Eviction
**Filing Fee:** Yes (clerk sets amount)
**Companion Forms:** CV-034 (Summons, $5 from clerk), CV-100 (Instructions), CV-256 (Info Sheet & Mediation Request), CV-204 (Affidavit of Service)

## Purpose

This is the complaint form to begin a residential eviction (Forcible Entry and Detainer) case in Maine District Court. Filed by a landlord (plaintiff) against tenant(s) (defendant) to recover possession of residential property.

## Governing Law

- **M.R. Civ. P. 80D** — Forcible Entry and Detainer procedure
- **14 M.R.S. §§ 6001–6016** — FED statutes (notice requirements, grounds, procedure)
  - § 6001: Availability of remedy
  - § 6002: Grounds for FED action
  - § 6001-A: Notice to quit requirements
  - § 6002-A: Additional protections for residential tenants
  - § 6003: Procedure and service
  - § 6005: Judgment and writ of possession
  - § 6014: Rent escrow

## Filing Requirements (from CV-100 Instructions)

1. **Notice to Quit** must be served first (in most cases), along with CV-256 Info Sheet
2. **Service**: Summons (CV-034) must be served ≥14 days before hearing
3. **Filing deadline**: File at court ≥3 business days before hearing date
4. Each tenant needs a separate summons
5. Documents to file: original complaint, original summons, return of service, Notice to Quit

## Field Mappings

### Page 1 — Case Information & Complaint Body

| Field Name | Type | Source | Notes |
|-----------|------|--------|-------|
| `Plaintiff` | Text | `matter.parties[role=plaintiff].full_name` | Landlord's name |
| `V` | Text | *auto: "v."* | Leave as-is or auto-fill |
| `Defendants` | Text | `matter.parties[role=defendant].full_name` | Tenant name(s), comma-separated if multiple |
| `And All Other Occupants` | CheckBox | AI decision | Check if there are non-tenant occupants |
| `Location Town` | Text | `matter.court_location` | District Court location (town where property is) |
| `Docket No` | Text | `matter.docket_number` | Leave blank if new filing; clerk assigns |
| `NOW COMES the Plaintiff` | Text | `matter.parties[role=plaintiff].full_name` | Repeat plaintiff's name |
| `1 The plaintiff is the owner...` | Text | `matter.property_address` | Street address of rental property |
| `Maine` | Text | `matter.property_address_line2` | City/town portion of address |

### Page 1 — Basis for Eviction (checkboxes — AI-assisted)

| Field Name | Type | Source | Notes |
|-----------|------|--------|-------|
| `The defendants isare more than` | CheckBox | AI from matter notes | Nonpayment of rent |
| `months in arrears...` | Text | AI from matter notes | Number of months behind |
| `...breached certain terms...` | CheckBox | AI from matter notes | Lease violation |
| `...other conduct...` | CheckBox | AI from matter notes | Other grounds (14 M.R.S. § 6002) |
| `Other please specify` | CheckBox | AI from matter notes | Catch-all |
| `undefined` (other specify text) | Text | AI from matter notes | Describe other grounds |

### Page 1 — Notice to Quit

| Field Name | Type | Source | Notes |
|-----------|------|--------|-------|
| `...served with a Notice to Quit on...` | CheckBox | matter timeline | Check if NTQ was served |
| `undefined_2` (NTQ date) | Text | `matter.events[type=notice_to_quit].date` | MM/DD/YYYY format |
| `...were not served with a Notice to Quit` | CheckBox | matter timeline | Check if no NTQ (rare — only for specific grounds) |

### Page 1 — Attachments

| Field Name | Type | Source | Notes |
|-----------|------|--------|-------|
| `The Notice to Quit served...` | CheckBox | deterministic | Check if NTQ is attached |
| `The lease agreement signed...` | CheckBox | deterministic | Check if lease is attached |
| `Other please specify_2` | CheckBox | AI decision | Other attachments |
| `undefined_3` (other attachment text) | Text | AI | Describe other attachments |
| `There is nothing attached...` | CheckBox | deterministic | Only if nothing attached (unusual) |

### Page 2 — Additional Allegations

| Field Name | Type | Source | Notes |
|-----------|------|--------|-------|
| `Additional allegations...` | CheckBox | AI decision | Check if additional text needed |
| `separate sheet 1` | Text | AI | Additional facts supporting the claim |

### Page 2 — Signature Block

| Field Name | Type | Source | Notes |
|-----------|------|--------|-------|
| `Maine_2` | Text | `matter.property_address_full` | County/state line |
| `Date mmddyyyy` | Text | `today()` | Filing date |
| `undefined_4` (signature) | Text | *leave blank* | Physical signature required |
| `Plaintiff_2` | CheckBox | `filing_party == "plaintiff"` | Check if plaintiff signing |
| `Attorney for Plaintiff` | CheckBox | `filing_party == "attorney"` | Check if attorney signing |
| `Printed Name` | Text | `attorney.full_name or plaintiff.full_name` | Signer's printed name |
| `Bar Number if applicable` | Text | `attorney.bar_number` | Attorney bar number |

### Page 2 — Plaintiff/Attorney Contact (left column)

| Field Name | Type | Source | Notes |
|-----------|------|--------|-------|
| `Plaintiff Attorney 1` | Text | `attorney.full_name` | Attorney name |
| `Mailing Address` | Text | `attorney.address_line1` | |
| `Plaintiff Attorney 2` | Text | `attorney.address_line2` | City, State, ZIP |
| `undefined_5` | Text | `attorney.address_line3` | Additional address |
| `Telephone Office` | Text | `attorney.phone_office` | |
| `Email` | Text | `attorney.email` | |

### Page 2 — Plaintiff Contact (right column)

| Field Name | Type | Source | Notes |
|-----------|------|--------|-------|
| `Plaintiff 1` | Text | `plaintiff.full_name` | |
| `Mailing Address_2` | Text | `plaintiff.address_line1` | |
| `Plaintiff 2` | Text | `plaintiff.address_line2` | |
| `undefined_6` | Text | `plaintiff.address_line3` | |
| `Telephone Cell` | Text | `plaintiff.phone` | |
| `Email_2` | Text | `plaintiff.email` | |

### Page 2 — Defendant/Attorney Contact (two sections, same pattern)

Fields follow same pattern: `Defendant Attorney 1/2`, `Defendant 1/2`, `Mailing Address`, `Telephone`, `Email` — source from `matter.parties[role=defendant]` and their attorney if known.

## AI Hints

### Basis for Eviction
- **Nonpayment**: Most common. Calculate months from matter billing/rent records. Must specify exact months in arrears.
- **Lease violation**: Describe specific clause violated. Common: unauthorized pets, subletting, property damage.
- **Other conduct**: Includes criminal activity, nuisance. Cite specific statute subsection from 14 M.R.S. § 6002.
- Usually only ONE basis is checked, but multiple are allowed.

### Notice to Quit Timing
- **Nonpayment**: 7-day notice required (14 M.R.S. § 6002(1))
- **Lease violation**: 7-day notice with opportunity to cure (14 M.R.S. § 6002(2))
- **No-cause (tenancy at will)**: 30-day notice required (14 M.R.S. § 6002(4))
- **Criminal activity**: No notice required in some cases

### Court Location
- File in the District Court division where the **property is located**, not where the plaintiff lives.
- Maine District Courts: [list varies by county]

### Common Mistakes to Validate Against
1. Filing in wrong court location (must be where property is)
2. Not naming all tenants on the lease as defendants
3. Insufficient notice period (count days carefully)
4. Missing CV-256 Information Sheet (required since 2023)
5. Not filing ≥3 business days before hearing
6. Listing multiple tenants on one summons (each needs their own)

## Validation Checklist

- [ ] Plaintiff name matches property owner/landlord records
- [ ] All tenants on lease named as defendants
- [ ] Property address is complete and matches lease
- [ ] Court location matches property county/town
- [ ] At least one eviction basis is checked
- [ ] If nonpayment, months in arrears is specified
- [ ] Notice to Quit section is completed (date or "not served" checked)
- [ ] At least one attachment checkbox is checked (NTQ and/or lease)
- [ ] Date is filled in
- [ ] Signer checkbox matches who is signing (plaintiff vs attorney)
- [ ] If attorney, bar number is provided
- [ ] Contact info complete for at least plaintiff OR attorney

## Related Forms Workflow

```
1. Notice to Quit (drafted by attorney/landlord, no court form)
   + CV-256 (FED Info Sheet & Mediation Request) — serve with NTQ
2. CV-007 (this form) — Complaint
3. CV-034 (Summons) — $5 from clerk, one per defendant
4. [Service by sheriff or other method]
5. CV-204 (Affidavit of Service) — proof of service
6. [Hearing]
7. CV-195 (Request for Writ of Possession) — if judgment in plaintiff's favor
```
