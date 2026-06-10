# CV-281 — Affidavit and Request to Register a Canadian Money Judgment

**Form Number:** CV-281
**Fillable Fields:** 71
**Category:** Civil — Foreign Judgments
**Court:** Superior Court / District Court

## Purpose

Registers a Canadian money judgment in Maine for enforcement.

## Governing Law

- **14 M.R.S. § 761 (registration of Canadian judgments)**

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
| `The Canadian Court rendering the judgment` | Text | From matter data |
| `Canadian CaseDocket Number` | Text | `matter.docket_number` |
| `Plaintiffs` | Text | From matter data |
| `Defendants` | Text | From matter data |
| `Date judgment was entered mmddyyyy` | Text | `today()` or relevant date |
| `Judgment in favor of name` | Text | From matter data |
| `The total judgment award amount` | Text | From matter data |
| `Amount of the judgment being sought with this registration` | Text | From matter data |
| `I was the` | CheckBox | From matter data |
| `plaintiffpetitioner` | CheckBox | From matter data |
| `defendantrespondent in the Canadian action` | CheckBox | From matter data |
| `I was not a party in the Canadian action but I am entitled to seek recognition and enforcement of the` | CheckBox | From matter data |
| `judgment because 1` | Text | From matter data |
| `judgment because 2` | Text | From matter data |

### Page 1

| Field Name | Type | Source |
|-----------|------|--------|
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
| `For the person in whose favor the Canadian judgment was entered if different from above` | CheckBox | From matter data |
| `Name` | Text | From matter data |
| `Mailing Address 1_2` | Text | `party.address` |
| `Mailing Address 2_2` | Text | `party.address` |
| `Mailing Address 3_2` | Text | `party.address` |
| `Phone Number_2` | Text | `party.phone` |
| `Physical Address 1_2` | Text | `party.address` |
| `if different_2` | Text | From matter data |
| `Physical Address 2_2` | Text | `party.address` |
| `Email_2` | Text | `party.email` |
| `Mailing Address 1_3` | Text | `party.address` |
| `Mailing Address 2_3` | Text | `party.address` |
| `Mailing Address 3_3` | Text | `party.address` |
| `Phone Number_3` | Text | `party.phone` |
| `Physical Address 1_3` | Text | `party.address` |
| `if different_3` | Text | From matter data |
| `Physical Address 2_3` | Text | `party.address` |
| `Email_3` | Text | `party.email` |
| `CAD` | Text | From matter data |
| `Exchange rate as of the date the Canadian judgment was entered` | Text | From matter data |
| *... +1 more fields* | | |

### Page 2

| Field Name | Type | Source |
|-----------|------|--------|
| `1` | Text | From matter data |
| `2` | Text | From matter data |
| `3` | Text | From matter data |
| `USD_2` | Text | From matter data |
| `USD_3` | Text | From matter data |
| `USD_4` | Text | From matter data |
| `USD_5` | Text | From matter data |
| `USD_6` | Text | From matter data |
| `The judgment is final conclusive and enforceable under the laws of the Canadian jurisdiction in` | CheckBox | From matter data |
| `The judgment or part of the judgment being registered is within the scope of 14 MRS  761 and` | CheckBox | From matter data |
| `If only part of the judgment is being registered the amounts stated in Section 3 above relate to that` | CheckBox | From matter data |
| `A copy of the Canadian judgment certified by the court that issued it` | CheckBox | From matter data |
| `If the Canadian judgment is not in English a courtprepared copy of the judgment in English or if` | CheckBox | From matter data |
| `The applicable filing fee` | CheckBox | From matter data |

### Page 3

| Field Name | Type | Source |
|-----------|------|--------|
| `I` | Text | From matter data |
| `I swear under penalty of perjury that the above statements are true and correct I understand that` | CheckBox | From matter data |
| `Date mmddyyyy` | Text | `today()` or relevant date |
| `undefined` | Text | From matter data |
| `Printed Name and Maine Bar No if applicable` | Text | `attorney.bar_number` |


## AI Hints

71 fields, 4 pages. Very detailed. Sections: Canadian judgment identification (court, docket, parties, date, amounts), party's role, contact info for both parties, certifications about judgment validity (not satisfied, no appeals pending, not stayed, statute of limitations not expired), required attachments (certified Canadian judgment, affidavit of non-satisfaction). Includes perjury oath and ORDER section.

## Validation Checklist

- [ ] Case caption is complete (parties, court, docket number)
- [ ] Date is filled in (mm/dd/yyyy format)
- [ ] Signature line identified (leave blank for physical signature)
- [ ] Correct court type selected (Superior/District)
