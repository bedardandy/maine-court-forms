# MRS-1099ME — MRS-1099ME

**Category:**   |  **Court:** 
**Fields:** 27  |  **Automation:** recipe

## What an agent needs to fill this form

Provide a matter/case object with party names, court (county + location + docket), and any form-specific facts. The field table below lists every fillable widget; map your case data to each `field_id`.

> A dedicated fill recipe exists in `engine/recipes/` and encodes the authoritative, audit-verified mapping (including non-obvious widget quirks). Prefer it over the raw table below.

## Field map

| field_id | type | page | printed label |
|---|---|---|---|
| `clear` | checkbox | 0 | Clear |
| `print` | checkbox | 0 | Print |
| `1099me_name` | text | 0 | 1099ME Name |
| `1099me_address` | text | 0 | 1099ME Address |
| `1099me_city_state_and_zip_code` | text | 0 | 1099ME City, State and Zip Code |
| `1099me_member_id_number` | text | 0 | 1099ME Member ID Number |
| `1099me_entity_payer_name` | text | 0 | 1099ME Entity/Payer Name |
| `1099me_entity_payer_address` | text | 0 | 1099ME Entity/Payer Address |
| `1099me_entity_payer_city_state_and_zip_code` | text | 0 | 1099ME Entity/Payer City, State and Zip Code |
| `choice_1` | text | 0 | Choice 1 |
| `choice_1_dup1` | text | 0 | Choice 1 |
| `choice_1_dup2` | text | 0 | Choice 1 |
| `1099me_entity_federal_identification_number` | text | 0 | 1099ME Entity Federal Identification Number |
| `1099me_contact_information_name` | text | 0 | 1099ME Contact Information: Name |
| `1099me_phone_number` | text | 0 | 1099ME Phone Number |
| `1099me_corrected` | text | 0 | 1099ME Corrected |
| `1099me_maine_income_tax_withheld_directly_by_the_entity_listed_in_box_c` | text | 0 | 1099ME Maine income tax withheld directly by the entity list |
| `1099me_maine_income_tax_withheld_by_lower_tier_entities` | text | 0 | 1099ME Maine income tax withheld by lower tier entities |
| `1099me_real_estate_withholding_payments` | text | 0 | 1099ME Real estate withholding payments |
| `1099me_a` | text | 0 | 1099ME a) |
| `1099me_a_ein` | text | 0 | 1099ME a) EIN |
| `1099me_b` | text | 0 | 1099ME b) |
| `1099me_b_ein` | text | 0 | 1099ME b) EIN |
| `1099me_c` | text | 0 | 1099ME c) |
| `1099me_c_ein` | text | 0 | 1099ME c) EIN |
| `1099me_d` | text | 0 | 1099ME d) |
| `1099me_d_ein` | text | 0 | 1099ME d) EIN |
