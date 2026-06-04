<!-- Reused from prior skills stash; verify against schema.json. -->
# CV-223 — Judicial Recommendation for Transfer to Business and Consumer Docket

**Form Number:** CV-223
**Fillable Fields:** 39
**Category:** Civil — Business Court
**Court:** Superior Court / District Court
**Related Forms:** CV-222

## Purpose

Judge's recommendation to transfer a case to the Business and Consumer Docket.

## Field Mapping Summary

### Page 0

| Field Name | Type | Source |
|-----------|------|--------|
| `Plaintiff` | Text | From matter data |
| `Superior Court` | CheckBox | `matter.court_type` |
| `District Court` | CheckBox | `matter.court_type` |
| `County` | Text | `matter.court_county` |
| `Location Town` | Text | `matter.court_location` |
| `Defendant` | Text | From matter data |
| `Docket No` | Text | `matter.docket_number` |
| `Breach of Contract` | CheckBox | From matter data |
| `Breach of Warranty` | CheckBox | From matter data |
| `Breach of Fiduciary Duty` | CheckBox | From matter data |
| `Class Action` | CheckBox | From matter data |
| `80B Appeal involving a business entity` | CheckBox | From matter data |
| `80C Appeal involving a business entity` | CheckBox | From matter data |
| `Internal governance of business entity` | CheckBox | From matter data |
| `Securities transactions` | CheckBox | From matter data |
| `Shareholder derivative action` | CheckBox | From matter data |
| `Confidential or trade secret` | CheckBox | From matter data |
| `Intellectual property` | CheckBox | From matter data |
| `Financial transactions` | CheckBox | From matter data |
| `UCC transactions` | CheckBox | From matter data |
| `Unfair trade practices` | CheckBox | From matter data |
| `Antitrust or other trade regulations` | CheckBox | From matter data |
| `Commercial real estate` | CheckBox | From matter data |
| `Other describe` | CheckBox | From matter data |
| `Are there any pending motions` | Text | From matter data |
| `Check Box1` | CheckBox | From matter data |
| `Check Box2` | CheckBox | From matter data |
| `Check Box3` | CheckBox | From matter data |
| `Check Box4` | CheckBox | From matter data |
| `Check Box5` | CheckBox | From matter data |
| *... +9 more fields* | | |


## AI Hints

Completed by judge, not parties. Clerk attaches updated docket record. Same subject matter categories as CV-222. Includes sections for pending motions, business entity involvement, estimated trial length, recommended BCD judge, and judicial recommendation text.

## Validation Checklist

- [ ] Case caption is complete (parties, court, docket number)
- [ ] Correct court type selected (Superior/District)
- [ ] Related forms prepared if needed (CV-222)
