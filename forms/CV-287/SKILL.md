<!-- Reused from prior skills stash; verify against schema.json. -->
# CV-287 — Debt Buyer Complaint

**Form Number:** CV-287
**Fillable Fields:** 105
**Category:** Civil — Debt Collection
**Court:** Superior Court / District Court

## Purpose

Standardized complaint form for debt buyers filing suit to collect on purchased consumer debts. Required format ensures proper documentation of debt chain.

## Governing Law

- **32 M.R.S. § 11013 (debt buyer requirements)**
- **Maine Fair Debt Collection Practices Act**

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
| `1 The plaintiff` | Text | From matter data |
| `claims that the defendant` | Text | From matter data |
| `2 The claimed amount owed to the plaintiff is` | Text | From matter data |
| `3 The name of the original creditor was` | Text | From matter data |

### Page 1

| Field Name | Type | Source |
|-----------|------|--------|
| `Credit card or student loan debt Plaintiff served the form answer posted by the Bureau of` | CheckBox | From matter data |
| `For medical expenses Plaintiff claims this action does not violate requirements of Maine Law` | CheckBox | From matter data |
| `Consumer debt that is not based on credit card student loan or medical expenses` | CheckBox | From matter data |
| `Plaintiff has provided proper notice` | CheckBox | From matter data |
| `For credit card or student loan debt Plaintiff served the form answer posted by the Bureau of` | CheckBox | From matter data |

### Page 2

| Field Name | Type | Source |
|-----------|------|--------|
| `claim based on the following 1` | Text | From matter data |
| `The debt was purchase on or before 112018 Requirements for a claim for debt purchased` | CheckBox | From matter data |
| `4 Parties and Venue 1` | Text | From matter data |
| `5 Causes of Action 1` | Text | From matter data |
| `The name of the current owner of the debt` | Text | From matter data |
| `The debt at issue was chargedoff At chargeoff` | CheckBox | From matter data |
| `The name of the original creditor` | Text | From matter data |
| `undefined` | Text | From matter data |
| `The account number if any used to identify the debt` | Text | From matter data |

### Page 3

| Field Name | Type | Source |
|-----------|------|--------|
| `If amount due is less than the amount at chargeoff the difference is because` | Text | From matter data |
| `services billed to the consumers account was mmddyyyy` | CheckBox | From matter data |
| `For revolving credit the date of the last extension of credit for the purchase of goods or services` | Text | From matter data |
| `for the lease of goods or as a loan of money was mmddyyyy` | CheckBox | From matter data |
| `undefined_2` | Text | From matter data |
| `The amount and date of the last payment or allegation that no payment has been made` | Text | From matter data |
| `undefined_3` | Text | From matter data |
| `undefined_4` | Text | From matter data |
| `undefined_5` | Text | From matter data |
| `undefined_6` | Text | From matter data |
| `undefined_7` | Text | From matter data |
| `undefined_8` | Text | From matter data |
| `undefined_9` | Text | From matter data |
| `undefined_10` | Text | From matter data |
| `undefined_11` | Text | From matter data |
| `undefined_12` | Text | From matter data |
| `undefined_13` | Text | From matter data |
| `undefined_14` | Text | From matter data |
| `Note If the debt was transferred to multiple entities as part of one transfer list the transfer for each` | Text | From matter data |
| `undefined_15` | Text | From matter data |
| `undefined_16` | Text | From matter data |

### Page 4

| Field Name | Type | Source |
|-----------|------|--------|
| `Interest andor fees were assessed after the date of chargeoff as listed on the next page` | CheckBox | From matter data |
| `Text1` | Text | From matter data |
| `fee 1` | Text | From matter data |
| `interestfees 1` | Text | From matter data |
| `mmddyyyy 1` | Text | From matter data |
| `Text2` | Text | From matter data |
| `fee 2` | Text | From matter data |
| `interestfees 2` | Text | From matter data |
| `mmddyyyy 2` | Text | From matter data |
| `Text3` | Text | From matter data |
| `fee 3` | Text | From matter data |
| `interestfees 3` | Text | From matter data |
| `mmddyyyy 3` | Text | From matter data |
| `fee 4` | Text | From matter data |
| `interestfees 4` | Text | From matter data |
| `mmddyyyy 4` | Text | From matter data |
| `Text4` | Text | From matter data |
| `Attorney fees are requested` | CheckBox | From matter data |
| `document that shows Defendants liability for attorney fees 1` | Text | From matter data |
| `Plaintiff makes the following other claims or allegations` | CheckBox | From matter data |
| `1_2` | Text | From matter data |
| `C Plaintiff requests the following relief 1` | Text | From matter data |
| `Plaintiff possesses documentation identified in 32 MRS  110139I  J and has attached` | CheckBox | From matter data |

### Page 5

| Field Name | Type | Source |
|-----------|------|--------|
| `Attached are affidavits incorporating the required documents by reference The documentation` | CheckBox | From matter data |
| `A copy of the contract application or other document showing Defendant agreed to and owes the` | CheckBox | From matter data |
| `A document provided to Defendant before chargeoff showing Defendant owes the debt` | CheckBox | From matter data |
| `The most recent monthly statement showing the extension of credit for purchase of goods or` | CheckBox | From matter data |
| `The last payment` | CheckBox | From matter data |
| `The last balance transfer` | CheckBox | From matter data |
| `The amount due at chargeoff plus interest and fees imposed` | CheckBox | From matter data |
| `Check Box6` | CheckBox | From matter data |
| `Other documents establishing the existence amount and terms and conditions of the debt if any 1` | Text | From matter data |
| `Check Box7` | CheckBox | From matter data |
| `Other documents establishing the existence amount and terms and conditions of the debt if any 2` | Text | From matter data |
| `Check Box8` | CheckBox | From matter data |
| `Other documents establishing the existence amount and terms and conditions of the debt if any 3` | Text | From matter data |
| `Check Box9` | CheckBox | From matter data |
| `Other documents establishing the existence amount and terms and conditions of the debt if any 4` | Text | From matter data |
| `Plaintiff has attached as Exhibit B documents identifying the original creditor and each bill of sale` | CheckBox | From matter data |
| `Plaintiff has attached as Exhibit C affidavits related to the attached documents` | CheckBox | From matter data |
| `Plaintiff has requested attorney fees and attached as Exhibit D documentation showing Plaintiff is` | CheckBox | From matter data |
| `Check Box10` | CheckBox | From matter data |
| `Description and exhibit letter of other documents attached if any 1` | Text | From matter data |
| `Check Box11` | CheckBox | From matter data |
| `Description and exhibit letter of other documents attached if any 2` | Text | From matter data |
| `Check Box12` | CheckBox | From matter data |
| `Description and exhibit letter of other documents attached if any 3` | Text | From matter data |
| `Check Box13` | CheckBox | From matter data |
| `Description and exhibit letter of other documents attached if any 4` | Text | From matter data |

### Page 6

| Field Name | Type | Source |
|-----------|------|--------|
| `Date mmddyyyy` | Text | `today()` or relevant date |
| `Text5` | Text | From matter data |
| `undefined_25` | CheckBox | From matter data |
| `Attorney for` | CheckBox | From matter data |
| `Printed Name and Bar Number if applicable` | Text | `attorney.bar_number` |
| `1_3` | Text | From matter data |
| `2_3` | Text | From matter data |
| `3_2` | Text | From matter data |
| `Telephone` | Text | `party.phone` |
| `Email` | Text | `party.email` |


## AI Hints

105 fields, 7 pages — one of the most complex forms. Covers: parties/venue, causes of action, original creditor, current debt owner, charge-off details, account numbers, payment history, assignment chain with dates/amounts, statute of limitations calculation, required attachments (signed agreement, account statements, assignment documents). Separate sections for credit card, student loan, and medical debt. Includes defendant's answer form reference.

## Validation Checklist

- [ ] Case caption is complete (parties, court, docket number)
- [ ] Correct court type selected (Superior/District)
