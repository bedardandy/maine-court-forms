# CV-FM-291 — Court-Paid Attorney Referee Voucher

**Form Number:** CV-FM-291
**Fillable Fields:** 45
**Category:** Civil/Family — Attorney Referee Program
**Court:** District Court
**Related Forms:** CV-FM-288

## Purpose

Payment voucher for court-paid attorney referees to claim hourly fees and mileage reimbursement.

## Governing Law

- **Administrative Order JB-23-04**

## Field Mapping Summary

### Page 0

| Field Name | Type | Source |
|-----------|------|--------|
| `Check Box1` | CheckBox | From matter data |
| `undefined_2` | Text | From matter data |
| `v` | Text | From matter data |
| `DISTRICT COURT` | Text | `matter.court_type` |
| `IN RE` | CheckBox | From matter data |
| `undefined_3` | Text | From matter data |
| `DOCKET NUMBER` | Text | `matter.docket_number` |
| `A copy of the completed and signed Referee Contract is attached as required under JB2304` | CheckBox | From matter data |
| `B TOTAL HOURLY FEE` | Text | From matter data |
| `Number of hours` | Text | From matter data |
| `Voucher exceeds number of allowable hours The voucher exceeds the maximum number of hours` | CheckBox | From matter data |
| `A motion to exceed the maximum allowed hours was filed on mmddyyyy` | CheckBox | From matter data |
| `undefined_4` | Text | From matter data |
| `Attached is a copy of the court orders preapproving the additional time voucher will be denied if court order` | CheckBox | From matter data |
| `C TOTAL MILEAGE REIMBURSEMENT` | Text | From matter data |
| `Date mmddyyyyRow1` | Text | `today()` or relevant date |
| `Origin AddressRow1` | Text | `party.address` |
| `Destination AddressRow1` | Text | `party.address` |
| `Purpose of TravelRow1` | Text | From matter data |
| `Total MilesRow1` | Text | From matter data |
| `Applicable RateRow1` | Text | From matter data |
| `Trip CostRow1` | Text | From matter data |
| `Date mmddyyyyRow2` | Text | `today()` or relevant date |
| `Origin AddressRow2` | Text | `party.address` |
| `Destination AddressRow2` | Text | `party.address` |
| `Purpose of TravelRow2` | Text | From matter data |
| `Total MilesRow2` | Text | From matter data |
| `Applicable RateRow2` | Text | From matter data |
| `Trip CostRow2` | Text | From matter data |
| `Date mmddyyyyRow3` | Text | `today()` or relevant date |
| *... +15 more fields* | | |


## AI Hints

45 fields. Referee submits for payment. Rate: $43.75/hour in 0.1 increments. Must attach: signed referee contract, itemized time statement. Mileage: $0.56/mile after 11/01/2025, $0.54 before. Mileage table with date, origin, destination, purpose, miles, rate, cost. Motion required if exceeding maximum allowed hours. Must submit within 90 days of order conclusion.

## Validation Checklist

- [ ] Case caption is complete (parties, court, docket number)
- [ ] Related forms prepared if needed (CV-FM-288)
