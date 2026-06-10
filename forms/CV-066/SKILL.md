# CV-066 — Petition and Order for Military Certification

**Form Number:** CV-066
**Fillable Fields:** 23
**Category:** Civil — Service/Military
**Court:** Superior Court / District Court

## Purpose

Petitions the court to issue an order to military branches to determine if a party is in active military service, when their whereabouts cannot be ascertained.

## Governing Law

- **50 App U.S.C. § 582 (Servicemembers Civil Relief Act)**

## Field Mapping Summary

### Page 0

| Field Name | Type | Source |
|-----------|------|--------|
| `Plaintiff` | Text | From matter data |
| `Defendant` | Text | From matter data |
| `Superior Court` | CheckBox | `matter.court_type` |
| `District Court` | CheckBox | `matter.court_type` |
| `County` | Text | `matter.court_county` |
| `Location Town` | Text | `matter.court_location` |
| `Docket No` | Text | `matter.docket_number` |
| `RESPECTFULLY REPRESENTS` | Text | From matter data |
| `of citytown` | Text | From matter data |
| `in the County of 1` | Text | `matter.court_county` |
| `and State of` | Text | From matter data |
| `in the County of 2` | Text | `matter.court_county` |
| `of citytown_2` | Text | From matter data |
| `undefined` | Text | From matter data |
| `and State of_2` | Text | From matter data |
| `undefined_2` | Text | From matter data |
| `That it is impossible to ascertain by reasonable diligence the whereabouts of said` | Text | From matter data |
| `whose date of birth is mmddyyyy` | Text | `today()` or relevant date |
| `service number is` | Text | From matter data |
| `and other identifying characteristics are as follows 1` | Text | From matter data |
| `Date mmddyyyy` | Text | `today()` or relevant date |
| `undefined_3` | Text | From matter data |
| `Address reply to 1` | Text | `party.address` |


## AI Hints

Used when a party cannot be located and military status must be verified. Collects identifying info: DOB, service number, physical characteristics. Court orders military branches (Army, Air Force, Navy, Marines, Coast Guard) to certify service status. SSN required on separate form.

## Validation Checklist

- [ ] Case caption is complete (parties, court, docket number)
- [ ] Date is filled in (mm/dd/yyyy format)
- [ ] Signature line identified (leave blank for physical signature)
- [ ] Correct court type selected (Superior/District)
