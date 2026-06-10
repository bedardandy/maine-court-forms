# CV-183 — Complaint for Recovery Personal Property

**Form Number:** CV-183, Rev. 06/14
**Pages:** 1
**Fillable Fields:** 23
**Category:** Civil — Personal Property Recovery
**Filing Fee:** District Court filing fee
**Companion Forms:** CV-218 (Instructions), CV-188 (Writ of Possession), CV-187 (Notice of Appeal)

## Purpose

This is the complaint form to initiate a summary process action in District Court to recover personal property. The plaintiff claims a right, title, or interest in specific personal property that the defendant possesses and refuses to return, under 14 M.R.S. § 7071.

## Governing Law

- **14 M.R.S. § 7071** — Recovery of personal property (summary process)

## Filing Requirements

1. Filed in District Court only (not Superior Court)
2. Must describe property specifically enough to identify it (make, model, serial number)
3. Must state where the property is located
4. Must allege defendant unlawfully refuses to return it

## Field Mappings

| Field Name | Type | Source | Notes |
|-----------|------|--------|-------|
| `Plaintiff` | Text | `matter.parties[role=plaintiff].full_name` | |
| `Location Town` | Text | `matter.court_location` | District Court location |
| `Docket No` | Text | `matter.docket_number` | Clerk assigns |
| `Defendant` | Text | `matter.parties[role=defendant].full_name` | |
| Plaintiff name (in body) | Text | `matter.parties[role=plaintiff].full_name` | |
| `through his/her attorney` checkbox | CheckBox | `matter.has_attorney` | |
| Property location address | Text | `matter.property_location` | Where property currently is |
| Property location (Maine town) | Text | `matter.property_town` | |
| Property description | Text | AI from matter notes | Detailed description with identifiers |
| Defendant name (paragraph 3) | Text | `matter.parties[role=defendant].full_name` | |
| Writ location address | Text | `matter.property_location` | Same as property location |
| Writ location (Maine town) | Text | `matter.property_town` | |
| Date | Text | `today()` | |
| Plaintiff signature | Text | *leave blank* | |
| Attorney name and bar number | Text | `attorney.full_name` + `attorney.bar_number` | |

## AI Hints

### Property Description
- Must be specific enough that a sheriff could identify and seize the correct items
- Include: make, model, year, serial number, color, condition
- Example: "2019 John Deere X350 riding lawn mower, serial #1M0X350ABCD123456, green/yellow"

### Property Location
- Must specify the physical address where the property is currently located
- This is where the sheriff will go to execute a writ of possession

## Validation Checklist

- [ ] Filed in District Court (not Superior)
- [ ] Property description is specific and identifiable
- [ ] Property location address is complete
- [ ] Both plaintiff and defendant are identified
- [ ] Date is filled in

## Related Forms Workflow

```
1. CV-183 (this form) — Complaint
2. Summons served on defendant
3. Hearing in District Court
4. If judgment for plaintiff:
   a. CV-188 (Writ of Possession for Personal Property)
5. If appealed:
   a. CV-187 (Notice of Appeal)
```
