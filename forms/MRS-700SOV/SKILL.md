# MRS-700SOV — MRS-700SOV

**Category:**   |  **Court:** 
**Fields:** 46  |  **Automation:** recipe

## What an agent needs to fill this form

Provide a matter/case object with party names, court (county + location + docket), and any form-specific facts. The field table below lists every fillable widget; map your case data to each `field_id`.

> A dedicated fill recipe exists in `engine/recipes/` and encodes the authoritative, audit-verified mapping (including non-obvious widget quirks). Prefer it over the raw table below.

## Field map

| field_id | type | page | printed label |
|---|---|---|---|
| `clear` | checkbox | 0 | Clear |
| `print` | checkbox | 0 | Print |
| `estate_of_first_name` | text | 0 | Estate of First Name |
| `estate_of_m_i` | text | 0 | Estate of M.I |
| `estate_of_last_name` | text | 0 | Estate of Last Name |
| `social_security_number` | text | 0 | Social Security Number |
| `date_of_death` | text | 0 | Date of death |
| `residency_status` | text | 0 | Residency Status |
| `residency_status_dup1` | text | 0 | Residency Status |
| `state_of_residency` | text | 0 | State of Residency |
| `married_widow_widower_spouse_s_name` | text | 0 | Married/widow/widower, spouse's name |
| `spouse_ssn` | text | 0 | Spouse ssn |
| `personal_rep_first_name` | text | 0 | Personal Rep First Name |
| `personal_rep_m_i` | text | 0 | Personal Rep M.I |
| `personal_rep_last_name` | text | 0 | Personal Rep Last Name |
| `per_rep_ssn` | text | 0 | Per Rep SSN |
| `per_rep_area_code` | text | 0 | Per Rep Area Code |
| `per_rep_telephone_number` | text | 0 | Per Rep Telephone number |
| `per_rep_fax_area_code` | text | 0 | Per Rep Fax Area Code |
| `per_rep_fax_number` | text | 0 | Per Rep Fax number |
| `personal_rep_street_address` | text | 0 | Personal Rep Street Address |
| `personal_rep_city_town` | text | 0 | Personal Rep City/Town |
| `per_rep_state` | text | 0 | Per Rep State |
| `personal_rep_zip_code` | text | 0 | Personal Rep Zip Code |
| `personal_rep_email_address` | text | 0 | Personal Rep Email Address |
| `firm_name` | text | 0 | Firm Name |
| `contact_person_first_name` | text | 0 | Contact Person First Name |
| `contact_person_m_i` | text | 0 | Contact Person M.I |
| `contact_person_last_name` | text | 0 | Contact Person Last Name |
| `contact_person_mailing_address` | text | 0 | Contact Person Mailing Address |
| `contact_person_city_town` | text | 0 | Contact Person City/Town |
| `contact_person_state` | text | 0 | Contact Person State |
| `contact_zip_code` | text | 0 | Contact Zip Code |
| `contact_area_code` | text | 0 | Contact Area Code |
| `contact_telephone_number` | text | 0 | Contact Telephone number |
| `contact_email_address` | text | 0 | contact email address |
| `contact_fax_area_code` | text | 0 | Contact  Fax Area Code |
| `contact_fax_number` | text | 0 | Contact Fax number |
| `signature_line_of_personal_rep` | text | 0 | signature line of personal rep |
| `date_of_signature` | text | 0 | Date of signature |
| `signature_of_preparer` | text | 0 | Signature of Preparer |
| `preparer_ssn_or_ptin` | text | 0 | Preparer SSN or PTIN |
| `date_of_preparer_signature` | text | 0 | Date of Preparer signature |
| `firm_name_or_preparer` | text | 0 | Firm Name or preparer |
| `preparer_address` | text | 0 | Preparer address |
| `preparer_telephone_number` | text | 0 | Preparer telephone number |
