<!-- Reused from prior skills stash; verify against schema.json. -->
# CR-CV-FM-199 — Notice of Change of Address

**Form Number:** CR-CV-FM-199
**Fillable Fields:** 43
**Category:** Cross-Category — Administrative
**Court:** Superior Court / District Court / Unified Criminal Docket

## Purpose

Notifies the court of a party's change of mailing address, physical address, telephone, or email in any pending case type.

## Governing Law

- **19-A M.R.S. § 4008 (confidential contact information in family/PFA cases)**

## Field Mapping Summary

### Page 0

| Field Name | Type | Source |
|-----------|------|--------|
| `Check Box3` | CheckBox | From matter data |
| `undefined_2` | Text | From matter data |
| `V` | Text | From matter data |
| `Check Box4` | CheckBox | From matter data |
| `undefined_3` | Text | From matter data |
| `Superior Court` | CheckBox | `matter.court_type` |
| `District Court` | CheckBox | `matter.court_type` |
| `Unified Criminal Docket` | CheckBox | `matter.docket_number` |
| `County` | Text | `matter.court_county` |
| `Location Town` | Text | `matter.court_location` |
| `Docket No` | Text | `matter.docket_number` |
| `Appeal` | CheckBox | From matter data |
| `Criminal` | CheckBox | From matter data |
| `Family` | CheckBox | From matter data |
| `Civil` | CheckBox | From matter data |
| `Real Estate` | CheckBox | From matter data |
| `Juvenile` | CheckBox | From matter data |
| `Protection from AbuseHarassment` | CheckBox | From matter data |
| `Protective Custody` | CheckBox | From matter data |
| `Mental Health` | CheckBox | From matter data |
| `Recovery of Personal Property` | CheckBox | From matter data |
| `Money Judgment` | CheckBox | From matter data |
| `Small Claims` | CheckBox | From matter data |
| `Forcible Entry  Detainer Eviction` | CheckBox | From matter data |
| `Traffic Violation` | CheckBox | From matter data |
| `Other` | CheckBox | From matter data |
| `undefined_4` | Text | From matter data |
| `My Name` | Text | From matter data |
| `Old Mailing Address 1` | Text | `party.address` |
| `Old Mailing Address 2` | Text | `party.address` |
| *... +13 more fields* | | |


## AI Hints

Multi-case-type form — checkboxes cover Appeal, Criminal, Family, Civil, Real Estate, Juvenile, PFA/Harassment, Protective Custody, Mental Health, Recovery of Personal Property, Money Judgment, Small Claims, FED, Traffic, Other. Confidentiality flag available for cases where contact info is court-protected.

## Validation Checklist

- [ ] Case caption is complete (parties, court, docket number)
- [ ] Date is filled in (mm/dd/yyyy format)
- [ ] Signature line identified (leave blank for physical signature)
- [ ] Correct court type selected (Superior/District)
