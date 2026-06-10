# CR-CV-FM-265 — Request for Remote Hearing Coordinates

**Form Number:** CR-CV-FM-265
**Fillable Fields:** 17
**Category:** Cross-Category — Procedural
**Court:** Superior Court / District Court / Unified Criminal Docket

## Purpose

Requests the remote hearing connection information (Zoom/phone coordinates) for a scheduled hearing.

## Governing Law

- **JB-05-15 (media coverage notification)**

## Field Mapping Summary

### Page 0

| Field Name | Type | Source |
|-----------|------|--------|
| `Plaintiff` | Text | From matter data |
| `Defendant` | Text | From matter data |
| `Superior Court` | CheckBox | `matter.court_type` |
| `District Court` | CheckBox | `matter.court_type` |
| `Unified Criminal Docket` | CheckBox | `matter.docket_number` |
| `County` | Text | `matter.court_county` |
| `Location Town` | Text | `matter.court_location` |
| `Docket No` | Text | `matter.docket_number` |
| `I name` | Text | From matter data |
| `hearing that is scheduled in this case on mmddyyyy` | Text | From matter data |
| `at` | Text | From matter data |
| `am` | CheckBox | From matter data |
| `pm` | CheckBox | From matter data |
| `Text1` | Text | From matter data |
| `My phone number is` | Text | `party.phone` |
| `Date mmddyyyy` | Text | `today()` or relevant date |
| `undefined` | Text | From matter data |


## AI Hints

Simple one-page form. Party provides email and phone number to receive remote hearing coordinates. Media must still use separate Media Notification form.

## Validation Checklist

- [ ] Case caption is complete (parties, court, docket number)
- [ ] Date is filled in (mm/dd/yyyy format)
- [ ] Signature line identified (leave blank for physical signature)
- [ ] Correct court type selected (Superior/District)
