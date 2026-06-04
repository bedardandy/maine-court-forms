<!-- Reused from prior skills stash; verify against schema.json. -->
# MJBVB-017 — Request for Extension of Time to Pay

**Form Number:** MJBVB-017, Rev. Unknown
**Pages:** 1
**Fillable Fields:** 42
**Category:** Violations Bureau
**Court:** Violations Bureau

## Purpose

Form used in violations bureau proceedings in Maine court.

## Governing Law

- **29-A M.R.S.** — Primary statutory authority

## Field Mappings

| Field Name | Type | Page | Notes |
|-----------|------|------|-------|
| `Citation No` | Text | 1 |  |
| `v` | Text | 1 |  |
| `My name is` | Text | 1 |  |
| `My currentmailingaddress is` | Text | 1 | Mailing/street address |
| `My telephone number is` | Text | 1 | Phone number |
| `The year Iwas born was` | Text | 1 |  |
| `Totalamountoffines owed` | Text | 1 |  |
| `Fine due date` | Text | 1 | MM/DD/YYYY format |
| `The reasons Iam requestinga fine extension isare as follows 1` | Text | 1 |  |
| `The reasons Iam requestinga fine extension isare as follows 2` | Text | 1 |  |
| `Imake` | Text | 1 |  |
| `Employedby` | CheckBox | 1 | Check if applicable |
| `Unemployedandreceive` | CheckBox | 1 | Check if applicable |
| `Disabledandreceive` | CheckBox | 1 | Check if applicable |
| `Unemployedandreceive_2` | CheckBox | 1 | Check if applicable |
| `Unemployedbutexpect to startworkingon` | CheckBox | 1 | Check if applicable |
| `Am currentlyexpectinga` | CheckBox | 1 | Check if applicable |
| `Have no source ofincome` | CheckBox | 1 | Check if applicable |
| `Have` | CheckBox | 1 | Check if applicable |
| `Irequest thatthe Courtgrantme` | CheckBox | 1 | Check if applicable |
| `employer` | Text | 1 |  |
| `week` | CheckBox | 1 | Check if applicable |
| `month` | CheckBox | 1 | Check if applicable |
| `two weeks` | CheckBox | 1 | Check if applicable |
| `amount 1` | Text | 1 |  |
| `amount` | Text | 1 |  |
| `amount 2` | Text | 1 |  |
| `start date` | Text | 1 | MM/DD/YYYY format |
| `expected pay` | Text | 1 |  |
| `week_2` | CheckBox | 1 | Check if applicable |
| `month_2` | CheckBox | 1 | Check if applicable |
| `two weeks_2` | CheckBox | 1 | Check if applicable |
| `State or` | CheckBox | 1 | Check if applicable |
| `FederalTax refundin the totalamount of` | CheckBox | 1 | Check if applicable |
| `refund` | Text | 1 |  |
| `cash in my possession` | Text | 1 |  |
| `more days to pay my fine in full` | Text | 1 |  |
| `Date` | Text | 1 | MM/DD/YYYY format |
| `The requestfor an extension oftime is Denied` | CheckBox | 1 | Check if applicable |
| `The request for an extension oftime is Granted The fine is due in fullby` | CheckBox | 1 | Check if applicable |
| `due date` | Text | 1 | MM/DD/YYYY format |
| `Date_2` | Text | 1 | MM/DD/YYYY format |

## AI Hints

- **Deadlines**: Strict filing deadlines apply for post-judgment motions.
- **Service**: Proper service of judgment documents is required.

## Validation Checklist

- [ ] All required party names are filled in
- [ ] Court location/county is correct for venue
- [ ] All dates are in correct format (MM/DD/YYYY)
- [ ] Contact information is complete

## Related Forms

- **MJBVB-009** — VIOLATIONS BUREAU
- **MJBVB-010** — VIOLATIONS BUREAU
- **MJBVB-018** — VIOLATIONS BUREAU
- **MJBVB-020** — VIOLATIONS BUREAU
- **MJBVB-028** — Form MJBVB-028
- **MJBVB-029** — INFORMATION ON TRAFFIC VIOLATION APPEALS

> **Note:** a dedicated fill recipe exists for this form in `engine/recipes/`. The recipe is the authoritative field mapping; this doc is the human-readable companion.
