# CV-FM-PA-PB-PC-268 — Order Appointing Guardian ad Litem Under M.R. Civ. P. 17(b)

**Form Number:** CV-FM-PA-PB-PC-268
**Fillable Fields:** 87
**Category:** Cross-Category — GAL Appointment
**Court:** District Court

## Purpose

Court order appointing a Guardian ad Litem for a person who cannot meaningfully participate in proceedings, is a minor without representative, or is a defendant served only by publication.

## Governing Law

- **M.R. Civ. P. 17(b) (guardian ad litem appointment)**

## Field Mapping Summary

### Page 0

| Field Name | Type | Source |
|-----------|------|--------|
| `Check Box1` | CheckBox | From matter data |
| `Plaintiff` | Text | From matter data |
| `Defendant` | Text | From matter data |
| `Other party` | Text | From matter data |
| `IN RE` | CheckBox | From matter data |
| `ORDER APPOINTING GUARDIAN AD LITEM UNDER MR CIV P 17b` | Text | From matter data |
| `Location Town` | Text | `matter.court_location` |
| `Docket No` | Text | `matter.docket_number` |
| `appoints a guardian ad litem GAL for` | Text | From matter data |
| `birth is mmddyyyy` | Text | From matter data |
| `The court finds that` | Text | From matter data |
| `not capable of meaningfully participating in the proceeding that has been commenced and does not have a` | CheckBox | From matter data |
| `is a minor who does not have a duly appointed representative or` | CheckBox | From matter data |
| `is a defendant who has been served only by publication and has not appeared` | CheckBox | From matter data |
| `In making this appointment the court has relied on the following information 1` | Text | From matter data |
| `The GALs name is` | Text | From matter data |
| `The GALs mailing address is` | Text | `party.address` |
| `The GALs telephone number is` | Text | `party.phone` |
| `The GALs email address is` | Text | `party.email` |
| `NameRow1` | Text | From matter data |
| `Mailing AddressRow1` | Text | `party.address` |
| `Telephone NumberRow1` | Text | `party.phone` |
| `Email AddressRow1` | Text | `party.email` |
| `Text1` | Text | From matter data |
| `Text2` | Text | From matter data |
| `Text3` | Text | From matter data |
| `Text4` | Text | From matter data |

### Page 1

| Field Name | Type | Source |
|-----------|------|--------|
| `Text5` | Text | From matter data |
| `Text6` | Text | From matter data |
| `Text7` | Text | From matter data |
| `Text8` | Text | From matter data |
| `No party objects to the GAL appointment OR` | CheckBox | From matter data |
| `Plaintiff_2` | CheckBox | From matter data |
| `Defendant_2` | CheckBox | From matter data |
| `Other` | CheckBox | From matter data |
| `appointment of a GAL but after careful consideration the court concludes the following factors support the` | Text | From matter data |
| `appointment 1` | Text | From matter data |
| `PlaintiffPetitioner` | CheckBox | From matter data |
| `DefendantRespondent` | CheckBox | From matter data |
| `Other_2` | CheckBox | From matter data |
| `objects to the fee arrangement below but after careful consideration the court concludes the following factors in` | Text | From matter data |
| `MRGAL 4b4C support the fee arrangement 1` | Text | From matter data |

### Page 2

| Field Name | Type | Source |
|-----------|------|--------|
| `Other duties` | CheckBox | From matter data |
| `1` | Text | From matter data |
| `Flat Fee The GAL will complete all duties required in this order through the completion of mediation for a` | CheckBox | From matter data |
| `If the GAL is required to participate in hearing the fee for hearing will be` | Text | From matter data |
| `undefined_2` | Text | From matter data |
| `undefined_3` | Text | From matter data |
| `Hourly rate The GAL will complete all duties required in this order by spending no more than` | CheckBox | From matter data |
| `undefined_4` | Text | From matter data |
| `hours at an hourly rate of` | Text | From matter data |
| `Pro Bono or minimal fee The GAL will complete all duties required in this order` | CheckBox | From matter data |
| `without charging a fee` | CheckBox | From matter data |
| `for the minimal fee of` | CheckBox | From matter data |
| `undefined_5` | Text | From matter data |
| `Payment by the Court The GALs fees shall be paid by the court pursuant to the guidelines contained in` | CheckBox | From matter data |
| `On or before mmddyyyy` | CheckBox | From matter data |
| `defendantrespondent shall pay` | Text | From matter data |
| `shall pay` | Text | From matter data |
| `The responsibility for payment may be reallocated at the final hearing` | Text | From matter data |
| `other` | Text | From matter data |
| `undefined_6` | Text | From matter data |

### Page 3

| Field Name | Type | Source |
|-----------|------|--------|
| `PlaintiffPetitioner shall pay` | CheckBox | From matter data |
| `MAINE JUDICIAL BRANCH` | Text | From matter data |
| `of each bill defendantrespondent shall pay` | Text | From matter data |
| `bill other` | Text | From matter data |
| `shall pay_2` | Text | From matter data |
| `14 days` | CheckBox | From matter data |
| `week` | CheckBox | From matter data |
| `month after receiving each bill or` | CheckBox | From matter data |
| `PlaintiffPetitioner shall pay_2` | CheckBox | From matter data |
| `per` | Text | From matter data |
| `week_2` | CheckBox | From matter data |
| `month toward the GAL fees and expenses` | CheckBox | From matter data |
| `defendantrespondent shall pay_2` | Text | From matter data |
| `week_3` | CheckBox | From matter data |
| `month toward the GAL fees and expenses_2` | CheckBox | From matter data |
| `and other` | Text | From matter data |
| `shall pay_3` | Text | From matter data |
| `week_4` | CheckBox | From matter data |
| `month The` | CheckBox | From matter data |
| `monthly` | CheckBox | From matter data |
| `biweekly basis The final fee` | CheckBox | From matter data |
| `Date mmddyyyy` | Text | `today()` or relevant date |
| `Justice Maine Superior Court` | CheckBox | `matter.court_type` |
| `Judge` | CheckBox | From matter data |
| `Magistrate Maine District Court` | CheckBox | `matter.court_type` |


## AI Hints

87 fields, 4 pages. Initial appointments only. Court order completed by judge. Sections: basis for appointment, GAL contact info, additional parties needing GAL, scope of duties, fees/expenses authorization, duration, and restrictions. Very detailed duty specifications.

## Validation Checklist

- [ ] Case caption is complete (parties, court, docket number)
