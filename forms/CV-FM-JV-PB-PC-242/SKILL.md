# CV-FM-JV-PB-PC-242 — Guardian ad Litem's Motion for Pre-Approval of Out-of-State/Overnight Travel Expenses

**Form Number:** CV-FM-JV-PB-PC-242
**Fillable Fields:** 54
**Category:** Cross-Category — GAL Administration
**Court:** Superior Court / District Court
**Related Forms:** CV-FM-JV-PB-PC-024

## Purpose

GAL requests pre-approval from Chief Judge for out-of-state or overnight travel expenses before incurring them.

## Governing Law

- **Administrative Order JB-05-05**

## Field Mapping Summary

### Page 0

| Field Name | Type | Source |
|-----------|------|--------|
| `Check Box1` | CheckBox | From matter data |
| `Plaintiff` | Text | From matter data |
| `Defendant` | Text | From matter data |
| `IN RE` | CheckBox | From matter data |
| `undefined_2` | Text | From matter data |
| `Superior Court` | CheckBox | `matter.court_type` |
| `District Court` | CheckBox | `matter.court_type` |
| `County` | Text | `matter.court_county` |
| `Location Town` | Text | `matter.court_location` |
| `Docket No` | Text | `matter.docket_number` |
| `Pursuant to Administrative Order AO JB055 guardian ad litem GAL` | Text | From matter data |
| `Mileage in the amount of` | CheckBox | From matter data |
| `which represents the following anticipated travel` | Text | From matter data |
| `Anticipated Date mmddyyyyRow1` | Text | `today()` or relevant date |
| `Origin AddressRow1` | Text | `party.address` |
| `Destination AddressRow1` | Text | `party.address` |
| `Total MilesRow1` | Text | From matter data |
| `Anticipated Date mmddyyyyRow2` | Text | `today()` or relevant date |
| `Origin AddressRow2` | Text | `party.address` |
| `Destination AddressRow2` | Text | `party.address` |
| `Total MilesRow2` | Text | From matter data |
| `Anticipated Date mmddyyyyRow3` | Text | `today()` or relevant date |
| `Origin AddressRow3` | Text | `party.address` |
| `Destination AddressRow3` | Text | `party.address` |
| `Total MilesRow3` | Text | From matter data |
| `Total Miles` | Text | From matter data |
| `Text1` | Text | From matter data |
| `applicable state rate` | Text | From matter data |
| `Airfare in the amount of` | CheckBox | From matter data |
| `I have attached a copy of my airfare quote` | Text | From matter data |
| *... +11 more fields* | | |

### Page 1

| Field Name | Type | Source |
|-----------|------|--------|
| `Other` | CheckBox | From matter data |
| `undefined_4` | Text | From matter data |
| `I have submitted this request prior at least 30 days before the expected departure date` | CheckBox | From matter data |
| `I have not submitted this request at least 30 days before the expected departure date because of the following` | CheckBox | From matter data |
| `circumstances 2` | Text | From matter data |
| `1` | Text | From matter data |
| `Check here if you need more space and have attached additional pages` | CheckBox | From matter data |
| `Date mmddyyyy` | Text | `today()` or relevant date |
| `undefined_5` | Text | From matter data |
| `Name` | Text | From matter data |
| `Bar No` | Text | `attorney.bar_number` |
| `Address` | Text | `party.address` |
| `ORDER OF COURT` | Text | From matter data |


## AI Hints

54 fields, 2 pages. Must be approved in writing before expenses incurred. Reimbursed at applicable State rate. Covers: mileage (with travel table), overnight accommodations, airfare (requires quote), meals/incidentals. Encourages telephone/video in lieu of travel. Attach approved motion to GAL voucher (CV-FM-JV-PB-PC-024) for reimbursement.

## Validation Checklist

- [ ] Case caption is complete (parties, court, docket number)
- [ ] Date is filled in (mm/dd/yyyy format)
- [ ] Signature line identified (leave blank for physical signature)
- [ ] Correct court type selected (Superior/District)
- [ ] Related forms prepared if needed (CV-FM-JV-PB-PC-024)
