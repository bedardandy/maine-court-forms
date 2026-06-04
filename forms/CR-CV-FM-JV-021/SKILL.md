<!-- Reused from prior skills stash; verify against schema.json. -->
# CR-CV-FM-JV-021 — Entry of Appearance

**Form Number:** CR-CV-FM-JV-021, Rev. 12/20
**Pages:** 1
**Fillable Fields:** 28
**Category:** Cross-Category — All Case Types
**Filing Fee:** None
**Companion Forms:** None (standalone, filed in any case type)

## Purpose

This form enters an attorney's appearance as counsel for a party, or a self-represented party's appearance, in any Maine court case (civil, criminal, family, juvenile). Filed with the clerk and served on all other parties.

## Governing Law

- **M.R. Civ. P. 89** — Appearance of attorneys
- **M.R.U.Cr.P. 44** — Right to and assignment of counsel

## Field Mappings

| Field Name | Type | Source | Notes |
|-----------|------|--------|-------|
| `Plaintiff` | Text | `matter.parties[role=plaintiff].full_name` | |
| `Superior Court` | CheckBox | `matter.court_type == "Superior"` | |
| `District Court` | CheckBox | `matter.court_type == "District"` | |
| `Unified Criminal Docket` | CheckBox | `matter.court_type == "UCD"` | |
| `County` | Text | `matter.court_county` | |
| `Defendant` | Text | `matter.parties[role=defendant].full_name` | |
| `Location Town` | Text | `matter.court_location` | |
| `Other Party` | Text | `matter.parties[role=other].full_name` | If applicable |
| `Docket No` | Text | `matter.docket_number` | |

### Counsel Appearing

| Field Name | Type | Source | Notes |
|-----------|------|--------|-------|
| `counsel for plaintiff` | CheckBox | `attorney.represents == "plaintiff"` | |
| `counsel for defendant` | CheckBox | `attorney.represents == "defendant"` | |
| `counsel for other party` | CheckBox | `attorney.represents == "other"` | |
| Party name (for counsel) | Text | `matter.parties[role=client].full_name` | |

### Self-Represented Appearing

| Field Name | Type | Source | Notes |
|-----------|------|--------|-------|
| `self-represented plaintiff` | CheckBox | `party.self_represented and party.role == "plaintiff"` | |
| `self-represented defendant` | CheckBox | `party.self_represented and party.role == "defendant"` | |
| `self-represented other party` | CheckBox | `party.self_represented and party.role == "other"` | |
| Party name (self-represented) | Text | `party.full_name` | |

### Contact Information

| Field Name | Type | Source | Notes |
|-----------|------|--------|-------|
| Date | Text | `today()` | |
| Signature | Text | *leave blank* | |
| Name | Text | `attorney.full_name or party.full_name` | |
| Bar Number | Text | `attorney.bar_number` | Required for attorneys |
| Address | Text | `attorney.address or party.address` | |
| Telephone | Text | `attorney.phone or party.phone` | |
| Email | Text | `attorney.email or party.email` | |

## Validation Checklist

- [ ] Either counsel or self-represented section completed (not both)
- [ ] Party being represented is identified
- [ ] Bar number provided (if attorney)
- [ ] Contact information complete
- [ ] Date filled in
- [ ] Filed with clerk AND served on all parties

## Related Forms Workflow

```
1. Case filed
2. CR-CV-FM-JV-021 (this form) — Entry of Appearance
3. All future papers served on appearing counsel/party
```
