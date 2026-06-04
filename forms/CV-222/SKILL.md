<!-- Reused from prior skills stash; verify against schema.json. -->
# CV-222 — Application for Transfer to Business and Consumer Docket

**Form Number:** CV-222
**Fillable Fields:** 125
**Category:** Civil — Business Court
**Court:** Superior Court / District Court

## Purpose

Application to transfer a civil case to the Business and Consumer Docket (BCD), Maine's specialized business court.

## Field Mapping Summary

### Page 0

| Field Name | Type | Source |
|-----------|------|--------|
| `Plaintiff` | Text | From matter data |
| `Superior Court` | CheckBox | `matter.court_type` |
| `District Court` | CheckBox | `matter.court_type` |
| `County` | Text | `matter.court_county` |
| `V` | Text | From matter data |
| `undefined` | Text | From matter data |
| `Location Town` | Text | `matter.court_location` |
| `NAME OF EACH PARTY SUBMITTING THIS APPLICATION 1` | Text | From matter data |
| `Check Box1` | CheckBox | From matter data |
| `Check Box2` | CheckBox | From matter data |
| `NAME OF EACH PARTY SUBMITTING THIS APPLICATION 2` | Text | From matter data |
| `Check Box3` | CheckBox | From matter data |
| `Check Box4` | CheckBox | From matter data |
| `NAME OF EACH PARTY SUBMITTING THIS APPLICATION 3` | Text | From matter data |
| `Check Box5` | CheckBox | From matter data |
| `Check Box6` | CheckBox | From matter data |
| `NAME OF EACH PARTY SUBMITTING THIS APPLICATION 4` | Text | From matter data |
| `Check Box7` | CheckBox | From matter data |
| `Check Box8` | CheckBox | From matter data |
| `Is at least one party a business entity` | RadioButton | From matter data |
| `Is at least one party a business entity` | RadioButton | From matter data |
| `PLAINTIFFSRow1` | Text | From matter data |
| `Text4` | Text | From matter data |
| `Text8` | Text | From matter data |
| `Text1` | Text | From matter data |
| `Text5` | Text | From matter data |
| `Text9` | Text | From matter data |
| `Text2` | Text | From matter data |
| `Text6` | Text | From matter data |
| `Text10` | Text | From matter data |
| *... +27 more fields* | | |

### Page 1

| Field Name | Type | Source |
|-----------|------|--------|
| `Do all of the parties appearing in the case agree to a transfer` | RadioButton | From matter data |
| `Do all of the parties appearing in the case agree to a transfer` | RadioButton | From matter data |
| `Do all of the parties appearing in the case agree to a transfer` | RadioButton | From matter data |
| `undefined_9` | RadioButton | From matter data |
| `undefined_9` | RadioButton | From matter data |
| `undefined_9` | RadioButton | From matter data |
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
| `1` | Text | From matter data |
| `Check Box9` | CheckBox | From matter data |
| `Check Box14` | CheckBox | From matter data |
| `Check Box15` | CheckBox | From matter data |
| `Check Box10` | CheckBox | From matter data |
| `Check Box17` | CheckBox | From matter data |
| `Check Box16` | CheckBox | From matter data |
| *... +35 more fields* | | |

### Page 2

| Field Name | Type | Source |
|-----------|------|--------|
| `Date mmddyyyy` | Text | `today()` or relevant date |
| `undefined_44` | Text | From matter data |
| `Bar Number if applicable` | Text | `attorney.bar_number` |


## AI Hints

125 fields — very complex, 3-page form. Collects: parties submitting, whether business entity involved, all plaintiffs/defendants with counsel and email, related cases for consolidation, subject matter categories, case description, jury demand status, pending motions, consent of parties. Subject matters include: breach of contract, fiduciary duty, class action, 80B/80C appeals, securities, shareholder derivative, trade secrets, IP, financial transactions, UCC, unfair trade practices, antitrust, commercial real estate.

## Validation Checklist

- [ ] Case caption is complete (parties, court, docket number)
- [ ] Correct court type selected (Superior/District)
