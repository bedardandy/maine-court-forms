# CV-282 — Petition to Recognize a Foreign Country Money Judgment

**Form Number:** CV-282
**Fillable Fields:** 68
**Category:** Civil — Foreign Judgments
**Court:** Superior Court / District Court

## Purpose

Petitions Maine court to recognize a money judgment from a foreign country (non-US, non-Canadian) under the Uniform Foreign-Country Money Judgments Recognition Act.

## Governing Law

- **14 M.R.S. §§ 8801-8812 (Uniform Foreign-Country Money Judgments Recognition Act)**

## Field Mapping Summary

### Page 0

| Field Name | Type | Source |
|-----------|------|--------|
| `PlaintiffPetitioner` | Text | From matter data |
| `DefendantPetitioner` | Text | From matter data |
| `Superior Court` | CheckBox | `matter.court_type` |
| `District Court` | CheckBox | `matter.court_type` |
| `County` | Text | `matter.court_county` |
| `Location Town` | Text | `matter.court_location` |
| `Docket No` | Text | `matter.docket_number` |
| `The foreign country court rendering the judgment` | Text | From matter data |
| `CaseDocket number` | Text | `matter.docket_number` |
| `Plaintiffs` | Text | From matter data |
| `Defendants` | Text | From matter data |
| `Date judgment was entered mmddyyyy` | Text | `today()` or relevant date |
| `Judgment in favor of name` | Text | From matter data |
| `Total judgment amount in foreign currency` | Text | From matter data |
| `Exchange rate as of the date the foreign judgment was entered` | Text | From matter data |
| `Amount of the judgment in USD as of the date entered` | Text | From matter data |
| `Amount of the judgment sought to be recognized` | Text | From matter data |
| `Additional amounts sought and basis for example specific costs fees or expenses` | CheckBox | From matter data |
| `1` | Text | From matter data |
| `2` | Text | From matter data |
| `3` | Text | From matter data |

### Page 1

| Field Name | Type | Source |
|-----------|------|--------|
| `I was the` | CheckBox | From matter data |
| `plaintiffpetitioner` | CheckBox | From matter data |
| `defendantrespondent in the foreign country action` | CheckBox | From matter data |
| `I was not a party in the original action but I am entitled to seek recognition and enforcement of the` | CheckBox | From matter data |
| `judgment because 1` | Text | From matter data |
| `judgment because 2` | Text | From matter data |
| `Text1` | Text | From matter data |
| `Mailing Address 1` | Text | `party.address` |
| `Mailing Address 2` | Text | `party.address` |
| `Mailing Address 3` | Text | `party.address` |
| `Phone Number` | Text | `party.phone` |
| `Physical Address 1` | Text | `party.address` |
| `if different` | Text | From matter data |
| `Physical Address 2` | Text | `party.address` |
| `Email` | Text | `party.email` |
| `Name and Maine Bar Number` | Text | `attorney.bar_number` |
| `Same as above` | CheckBox | From matter data |
| `Name` | Text | From matter data |
| `Mailing Address 1_2` | Text | `party.address` |
| `Mailing Address 2_2` | Text | `party.address` |
| `Mailing Address 3_2` | Text | `party.address` |
| `Phone Number_2` | Text | `party.phone` |
| `Physical Address 1_2` | Text | `party.address` |
| `if different_2` | Text | From matter data |
| `Physical Address 2_2` | Text | `party.address` |
| `Email_2` | Text | `party.email` |
| `Name_2` | Text | From matter data |
| `Mailing Address 1_3` | Text | `party.address` |
| `Mailing Address 2_3` | Text | `party.address` |
| `Mailing Address 3_3` | Text | `party.address` |
| *... +5 more fields* | | |

### Page 2

| Field Name | Type | Source |
|-----------|------|--------|
| `The foreign country judgment is final conclusive and enforceable under the laws of` | CheckBox | From matter data |
| `under which it was rendered` | Text | From matter data |
| `The foreign country judgment or part of the judgment is within the scope of 14 MRS  88018812` | CheckBox | From matter data |
| `If only part of the judgment is being sought to be recognized the amounts stated in Section 1 above` | CheckBox | From matter data |
| `A copy of the foreign country judgment certified by the court that issued it` | CheckBox | From matter data |
| `If the original judgment is not in English a courtprepared copy of the judgment in English or if such a` | CheckBox | From matter data |
| `The applicable filing fee` | CheckBox | From matter data |
| `judgment be recognized in the State of Maine pursuant to the` | Text | From matter data |
| `Uniform Foreign Country MoneyJudgments Recognition Act 14 MRS  88018812` | Text | From matter data |
| `Date mmddyyyy` | Text | `today()` or relevant date |
| `Text2` | Text | From matter data |
| `Printed Name and Maine Bar No if applicable` | Text | `attorney.bar_number` |


## AI Hints

68 fields, 3 pages. Similar structure to CV-281 but for non-Canadian foreign countries. Includes currency conversion fields (foreign currency amount, exchange rate, USD equivalent). Same certification sections about judgment validity. Must be filed as separate civil action with filing fee.

## Validation Checklist

- [ ] Case caption is complete (parties, court, docket number)
- [ ] Date is filled in (mm/dd/yyyy format)
- [ ] Signature line identified (leave blank for physical signature)
- [ ] Correct court type selected (Superior/District)
