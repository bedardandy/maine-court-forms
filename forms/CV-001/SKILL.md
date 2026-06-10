# CV-001 — Civil Summary Sheet

**Form Number:** CV-001, Rev. 12/21
**Pages:** 4
**Fillable Fields:** 162
**Category:** Civil — Administrative / Docketing
**Filing Fee:** N/A (accompanies complaint filing)
**Companion Forms:** Required with every civil complaint; CV-261 (Contract Case Cover Sheet) required for contract cases

## Purpose

The Civil Summary Sheet is required by the Clerk of Court to initiate or update the civil docket in Maine Superior or District Court. It collects case classification information including court, parties, nature of action, jury demand, and related case data. This form does not replace filing and service of pleadings.

## Governing Law

- **M.R. Civ. P. 3** — Commencement of action
- **M.R. Civ. P. 11** — Signing and verification of pleadings
- **M.R. Civ. P. 38** — Jury trial demand

## Filing Requirements

1. Must accompany every initial civil complaint, third-party complaint, cross-claim, or counterclaim
2. One box must be checked for nature of action
3. If contract case, CV-261 must be attached
4. Party information must match the complaint exactly

## Field Mappings

### Page 1 — Court & Filing Type

| Field Name | Type | Source | Notes |
|-----------|------|--------|-------|
| `Superior Court County` | CheckBox | `matter.court_type == "Superior"` | Check if Superior Court |
| `COUNTY OF FILING...` (county text) | Text | `matter.court_county` | County name |
| `District Court Location citytown` | CheckBox | `matter.court_type == "District"` | Check if District Court |
| `undefined` | Text | `matter.court_location` | District Court town |
| `Initial Complaint` | CheckBox | `matter.filing_type == "initial"` | Check for new cases |
| `ThirdParty Complaint` | CheckBox | `matter.filing_type == "third_party"` | |
| `CrossClaim or Counterclaim` | CheckBox | `matter.filing_type == "cross_claim"` | |
| `Reinstated or Reopened case` | CheckBox | `matter.filing_type == "reinstated"` | |
| `Docket No` | Text | `matter.docket_number` | For reopened/reinstated cases |

### Page 1 — Nature of Action (checkboxes)

| Field Name | Type | Source | Notes |
|-----------|------|--------|-------|
| Various nature-of-action checkboxes | CheckBox | `matter.nature_of_action` | Only ONE should be checked |
| `Real Estate` checkbox | CheckBox | `matter.involves_real_estate` | Check if real estate involved |

### Pages 2-3 — Party Information

| Field Name | Type | Source | Notes |
|-----------|------|--------|-------|
| Plaintiff name fields | Text | `matter.parties[role=plaintiff].full_name` | Up to multiple plaintiffs |
| Plaintiff address fields | Text | `matter.parties[role=plaintiff].address` | |
| Defendant name fields | Text | `matter.parties[role=defendant].full_name` | |
| Defendant address fields | Text | `matter.parties[role=defendant].address` | |
| Attorney name/bar/address | Text | `attorney.*` | For each represented party |

### Page 4 — Additional Information

| Field Name | Type | Source | Notes |
|-----------|------|--------|-------|
| Jury demand checkbox | CheckBox | `matter.jury_demand` | |
| Related case fields | Text | `matter.related_cases` | If any related docket numbers |
| Date | Text | `today()` | Filing date |
| Signature | Text | *leave blank* | Physical signature |

## AI Hints

### Nature of Action Selection
- Review the complaint to determine the single best-fitting category
- Contract cases MUST also have CV-261 attached
- Debt collection cases require specific subcategory selection
- FED cases should not use this form (they use their own complaint)

### Party Information
- List ALL parties from the complaint
- Include addresses for service purposes
- Attorney information required for represented parties

## Validation Checklist

- [ ] Exactly ONE nature of action box is checked
- [ ] Court type matches (Superior vs District)
- [ ] County/Location is filled in
- [ ] All parties from complaint are listed
- [ ] If contract case, CV-261 is also being filed
- [ ] Filing type is correctly identified
- [ ] Date is filled in

## Related Forms Workflow

```
1. CV-001 (this form) — Summary Sheet
2. Complaint (case-specific form)
3. CV-261 (Contract Cover Sheet) — if contract case
4. Summons — for service on defendant
```
