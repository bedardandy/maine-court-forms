<!-- Reused from prior skills stash; verify against schema.json. -->
# CV-FM-PB-299 — Attorney Voucher

**Form Number:** CV-FM-PB-299
**Fillable Fields:** 55
**Category:** Cross-Category — Attorney Payment
**Court:** District Court

## Purpose

Payment voucher for court-appointed attorneys in Title 18-C (guardianship/adoption), Title 19-A TPR, civil commitment, and extreme risk protection order cases.

## Field Mapping Summary

### Page 0

| Field Name | Type | Source |
|-----------|------|--------|
| `Check Box4` | CheckBox | From matter data |
| `undefined_2` | Text | From matter data |
| `v` | Text | From matter data |
| `DISTRICT COURT` | Text | `matter.court_type` |
| `IN RE` | CheckBox | From matter data |
| `TYPE OF CASE you must choose ONE` | Text | From matter data |
| `DOCKET NUMBER` | Text | `matter.docket_number` |
| `Title 18C matter eg guardianship of a minor or adoption` | CheckBox | From matter data |
| `Title 19A termination of parental rights case petitioner only` | CheckBox | From matter data |
| `Civil commitment case` | CheckBox | From matter data |
| `Extreme risk protection order case` | CheckBox | From matter data |
| `Text4` | Text | From matter data |
| `In 01 increments You must attach itemization of time` | Text | From matter data |
| `Date mmddyyyyRow1` | Text | `today()` or relevant date |
| `Origin AddressRow1` | Text | `party.address` |
| `Destination AddressRow1` | Text | `party.address` |
| `Total MilesRow1` | Text | From matter data |
| `Applicable RateRow1` | Text | From matter data |
| `Trip CostRow1` | Text | From matter data |
| `Purpose of TravelRow1` | Text | From matter data |
| `Date mmddyyyyRow2` | Text | `today()` or relevant date |
| `Origin AddressRow2` | Text | `party.address` |
| `Destination AddressRow2` | Text | `party.address` |
| `Total MilesRow2` | Text | From matter data |
| `Applicable RateRow2` | Text | From matter data |
| `Trip CostRow2` | Text | From matter data |
| `Purpose of TravelRow2` | Text | From matter data |
| `Date mmddyyyyRow3` | Text | `today()` or relevant date |
| `Origin AddressRow3` | Text | `party.address` |
| `Destination AddressRow3` | Text | `party.address` |
| *... +25 more fields* | | |


## AI Hints

55 fields, 1 page. Case types: Title 18-C matters, Title 19-A TPR (petitioner only), civil commitment, extreme risk protection orders. Rate: $150/hour in 0.1 increments. Mileage: $0.56/mile after 11/01/2025, $0.54 before. Must attach itemized billing and receipts for expenses.

## Validation Checklist

- [ ] Case caption is complete (parties, court, docket number)
