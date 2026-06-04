<!-- Reused from prior skills stash; verify against schema.json. -->
# CV-145 — Report of ADR Conference and Order

**Form Number:** CV-145, Rev. 01/02
**Pages:** 2
**Fillable Fields:** 60
**Category:** Civil — Alternative Dispute Resolution
**Filing Fee:** None
**Companion Forms:** Scheduling Order (court-generated)

## Purpose

This form reports the outcome of an Alternative Dispute Resolution (ADR) conference in Superior Court. It documents whether the case was unresolved, partially resolved, or fully resolved through mediation, early neutral evaluation, or arbitration, and is submitted to the court as an order.

## Governing Law

- **M.R. Civ. P. 16B** — Alternative Dispute Resolution
- **4 M.R.S. § 18-B** — Court ADR programs

## Filing Requirements

1. Filed after ADR conference is completed
2. Must be signed by all participating counsel/parties
3. If fully resolved, may include stipulated judgment terms
4. Filed in Superior Court only

## Field Mappings

### Page 1 — Case Caption & Conference Details

| Field Name | Type | Source | Notes |
|-----------|------|--------|-------|
| `Plaintiff` | Text | `matter.parties[role=plaintiff].full_name` | |
| `County` | Text | `matter.court_county` | Superior Court only |
| `Location Town` | Text | `matter.court_location` | |
| `Defendant` | Text | `matter.parties[role=defendant].full_name` | |
| `Docket No` | Text | `matter.docket_number` | |
| `Mediation` | CheckBox | `matter.adr_type == "mediation"` | |
| `Early Neutral Evaluation` | CheckBox | `matter.adr_type == "ENE"` | |
| `Arbitration` | CheckBox | `matter.adr_type == "arbitration"` | |
| ADR conference date(s) | Text | `matter.events[type=adr].date` | |
| Plaintiff(s) who attended | Text | `matter.parties[role=plaintiff].full_name` | |
| Defendant(s) who attended | Text | `matter.parties[role=defendant].full_name` | |
| Plaintiff counsel | Text | `attorney.full_name` | |
| Defendant counsel | Text | `matter.parties[role=defendant].attorney` | |
| Other participants | Text | AI | Mediator, etc. |

### Page 1 — Disposition

| Field Name | Type | Source | Notes |
|-----------|------|--------|-------|
| A — Unresolved | CheckBox | AI from matter notes | Trial proceeds per scheduling order |
| B — Partially Resolved | CheckBox | AI from matter notes | |
| B.1 — Stipulated facts | Text | AI | Facts parties agree on |
| B.2 — Legal issues for trial | Text | AI | Remaining issues |
| B.3 — Case management recommendations | Text | AI | |

### Page 2 — Full Resolution & Signatures

| Field Name | Type | Source | Notes |
|-----------|------|--------|-------|
| C — Fully Resolved | CheckBox | AI from matter notes | |
| Settlement terms | Text | AI | If parties consent to include |
| Counsel signatures (multiple) | Text | *leave blank* | All counsel sign |
| Court approval/order section | Text | *leave blank* | Court fills |

## AI Hints

- ADR conferences are confidential; only report disposition, not negotiation details
- If partially resolved, clearly delineate what's resolved vs. what remains for trial
- Mediator name typically not included (confidentiality)

## Validation Checklist

- [ ] Exactly one disposition checked (A, B, or C)
- [ ] ADR type checked
- [ ] Conference date(s) filled in
- [ ] All attending participants listed
- [ ] If partially resolved, sections B.1-B.3 completed
- [ ] Signature lines available for all counsel

## Related Forms Workflow

```
1. Court scheduling order (includes ADR deadline)
2. ADR conference held
3. CV-145 (this form) — Report filed
4. If unresolved: trial proceeds
5. If resolved: judgment entered
```
