# CR-CV-JV-297 — Personal Identifying Information Attachment

**Form Number:** CR-CV-JV-297
**Fillable Fields:** 49
**Category:** Cross-Category — Administrative
**Court:** Cross-category (Criminal, Civil, Juvenile)

## Purpose

Provides a separate attachment for personal identifying information (PII) that must be redacted or omitted from public court documents per M.R.E.C.S.

## Governing Law

- **M.R.E.C.S. 2, 4(E)(2), 5(B), 6(F)(2) (electronic court system rules on PII redaction)**

## Field Mapping Summary

### Page 0

| Field Name | Type | Source |
|-----------|------|--------|
| `Case Name short title` | Text | From matter data |
| `Docket No` | Text | `matter.docket_number` |
| `Complaint` | CheckBox | From matter data |
| `Indictment` | CheckBox | From matter data |
| `Information` | CheckBox | From matter data |
| `Answer` | CheckBox | From matter data |
| `Motion` | CheckBox | From matter data |
| `Other` | CheckBox | From matter data |
| `undefined` | Text | From matter data |
| `Text1` | Text | From matter data |
| `REFERENCE 1` | Text | From matter data |
| `Full Name` | Text | From matter data |
| `DOB mmddyyyy` | Text | From matter data |
| `Drivers License Number` | Text | From matter data |
| `Financial Account Numbers 1` | Text | From matter data |
| `Financial Account Numbers 2` | Text | From matter data |
| `undefined_2` | Text | From matter data |
| `Phone Number` | Text | `party.phone` |
| `Email Address` | Text | `party.email` |
| `Residential Address 1` | Text | `party.address` |
| `Residential Address 2` | Text | `party.address` |
| `Mailing Add 1` | Text | `party.address` |
| `Mailing Add 2` | Text | `party.address` |
| `REFERENCE 2` | Text | From matter data |
| `Full Name_2` | Text | From matter data |
| `DOB mmddyyyy_2` | Text | From matter data |
| `Drivers License Number_2` | Text | From matter data |
| `Financial Account Numbers 1_2` | Text | From matter data |
| `Financial Account Numbers 2_2` | Text | From matter data |
| `undefined_3` | Text | From matter data |
| *... +19 more fields* | | |


## AI Hints

Contains NONPUBLIC DIGITAL INFORMATION. Supports up to 3 references, each with: full name, DOB, driver's license, financial account numbers, phone, email, residential address, mailing address. Filed as attachment to complaints, indictments, motions, answers, etc. Page 2 has instructions on when/how to use.

## Validation Checklist

- [ ] Case caption is complete (parties, court, docket number)
