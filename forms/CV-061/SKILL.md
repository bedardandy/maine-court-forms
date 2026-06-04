<!-- Reused from prior skills stash; verify against schema.json. -->
# CV-061 — Affidavit and Request for Default

**Form Number:** CV-061, Rev. 10/22
**Pages:** 3
**Fillable Fields:** 79
**Category:** Civil — Default Judgment
**Filing Fee:** Additional fee if judgment ≥ $10,000 (M.R. Civ. P. 55(e))
**Companion Forms:** CV-001 (Civil Summary Sheet), original complaint

## Purpose

This form is used to request entry of default and default judgment when a defendant has failed to appear, plead, or otherwise defend a civil action. The affiant (plaintiff or plaintiff's attorney) must swear to specific facts including the defendant's failure to respond, non-military status, and the amount owed.

## Governing Law

- **M.R. Civ. P. 55** — Default and default judgment
- **50 U.S.C. § 3911, § 3931** — Servicemembers Civil Relief Act (no default against active military)
- **M.R. Civ. P. 11** — Signing and verification

## Filing Requirements

1. Defendant must have failed to appear, plead, or otherwise defend
2. Must verify defendant is not in military service
3. Must provide notice as required by M.R. Civ. P. 55(f)
4. If amount ≥ $10,000, additional fee required
5. If claim is for sum certain, specify exact amount

## Field Mappings

### Page 1 — Case Caption & Affidavit Statements

| Field Name | Type | Source | Notes |
|-----------|------|--------|-------|
| `Plaintiff` | Text | `matter.parties[role=plaintiff].full_name` | |
| `Superior Court` | CheckBox | `matter.court_type == "Superior"` | |
| `District Court` | CheckBox | `matter.court_type == "District"` | |
| `BCD` | CheckBox | `matter.court_type == "BCD"` | Business & Consumer Docket |
| `County` | Text | `matter.court_county` | |
| `Location Town` | Text | `matter.court_location` | |
| `Defendant` | Text | `matter.parties[role=defendant].full_name` | |
| `Docket No` | Text | `matter.docket_number` | |
| `Attorney for Plaintiff` checkbox | CheckBox | `matter.has_attorney` | |
| `Plaintiff represents` checkbox | CheckBox | `!matter.has_attorney` | Self-represented |
| Defendant name (in body) | Text | `matter.parties[role=defendant].full_name` | |
| 1a — Failed to appear | CheckBox | AI from matter notes | Most common |
| 1b — Appeared but failed to plead | CheckBox | AI from matter notes | |
| 1b details | Text | AI | How defendant failed |
| 2a — Not minor/incompetent | CheckBox | deterministic (usually) | |
| 2b — Is minor/incompetent | CheckBox | AI | Rare |
| 3 — Not in military service | Text | AI from matter notes | Evidence of non-military status |
| 4a — Sum certain amount | Text | `matter.amount_claimed` | Dollar amount |
| 4b — Negotiable instrument attached | CheckBox | deterministic | |
| 4c — Not sum certain | CheckBox | AI | If damages need hearing |

### Page 2 — Venue & Notice

| Field Name | Type | Source | Notes |
|-----------|------|--------|-------|
| 5 — Venue facts | Text | AI | Why venue is proper |
| 6 — Notice provided | CheckBox | deterministic | M.R. Civ. P. 55(f) compliance |
| Oath/signature | Text | *leave blank* | Physical signature |
| Date | Text | `today()` | |
| Notary section | Text | *leave blank* | Notary completes |

### Page 3 — Contact Information

| Field Name | Type | Source | Notes |
|-----------|------|--------|-------|
| Attorney name/address/phone/email | Text | `attorney.*` | |
| Plaintiff contact info | Text | `matter.parties[role=plaintiff].*` | |
| Defendant contact info | Text | `matter.parties[role=defendant].*` | |

## AI Hints

### Military Status Verification
- Must provide specific facts showing defendant is not in active military service
- Common evidence: employment records, recent communication, SCRA website check
- Example: "Defendant is employed at [employer] in [city], Maine as verified on [date]"

### Venue Facts
- Explain why the court has jurisdiction
- Common: defendant resides in county, contract performed in county, injury occurred in county

### Sum Certain vs. Not Sum Certain
- Sum certain: exact amount calculable from contract, promissory note, etc.
- Not sum certain: damages requiring assessment (hearing needed)

## Validation Checklist

- [ ] Defendant identified correctly
- [ ] Either 1a or 1b checked (failure to appear/defend)
- [ ] Military status verified with specific facts
- [ ] Amount specified if sum certain (4a), or 4c checked
- [ ] Venue facts provided
- [ ] Notice compliance checked (item 6)
- [ ] Date filled in
- [ ] Either "Attorney for Plaintiff" or "Plaintiff" checked as affiant

## Related Forms Workflow

```
1. Complaint filed and served
2. Defendant fails to respond
3. CV-061 (this form) — Request for Default
4. Default entered by clerk
5. Default judgment (by clerk if sum certain, by court if not)
```
