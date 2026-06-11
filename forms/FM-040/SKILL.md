# FM-040 — Child Support Worksheet

**Form Number:** FM-040, Rev. 02/20
**Pages:** 4
**Fillable Fields:** 105
**Category:** Family
**Court:** District Court / Family Division

## Purpose

This worksheet/financial form is used to calculate or document financial information in family cases.

## Governing Law

- **19-A M.R.S. §  2001**
- **19-A M.R.S. §§ 2001**

## Computed lines (printed arithmetic)

Declared in `computations.json` (evaluated by the shared engine on the mapping fill path). Omit a computed key (with its inputs supplied) and the engine fills it from the formula printed on the form (`computed_fields` in the result); supply it and your value is written **as-is** — a contradiction only adds a `COMPUTATION_MISMATCH` warning.

| computed key | printed instruction |
|---|---|
| `facts.basic_weekly_support_total` | Total number of children (a) multiplied by amount from table (b) = 9c. |
| `facts.child_care_total` | Total: 11. |
| `facts.combined_adjusted_gross_income` | c. (Add lines 7a and 7b.) |
| `facts.non_primary_pays_as_support` | Non-Primary Care Provider Adjustments (Amounts paid directly by Non-Primary Care Provider) Weekly health insurance (line 10) - $ Weekly child care (line 11) - $ Extraordinary Medical Expenses (line 12) - $ Non-Primary Care Provider pays as support = $ |
| `facts.total_extraordinary_medical_expenses` | Total: 12. |
| `facts.total_weekly_health_insurance_cost` | Total: 10. |

`facts.amount_from_table` is a **supplied** fact, never computed: the filer reads it off the printed Child Support Table per the page-3 instructions ("CALCULATING 'AMOUNT FROM TABLE' FOR LINE 9 OF THE WORKSHEET"); the statutory table is never embedded. Line 13 ("Add lines 9c, 10, 11 and 12; if biweekly, multiply x 2") is conditional and the line-14 multiplications operate on the percent entries of line 8 (`facts.share_of_adjusted_income_primary` / `facts.share_of_adjusted_income_non_primary`), so those lines are deliberately not declared (see `computations.json`).

## Field Mappings

| Field Name | Type | Page | Notes |
|-----------|------|------|-------|
| `Plaintiff` | Text | 1 |  |
| `LocationTown` | Text | 1 | Court location |
| `DocketNo` | Text | 1 | Court docket number |
| `Defendant` | Text | 1 |  |
| `Supplementalworksheet attached` | CheckBox | 1 | Check if applicable |
| `Plaintiff_2` | CheckBox | 1 | Check if applicable |
| `Defendant_2` | CheckBox | 1 | Check if applicable |
| `Both` | CheckBox | 1 | Check if applicable |
| `Plaintiff_3` | CheckBox | 1 | Check if applicable |
| `Plaintiff_4` | CheckBox | 1 | Check if applicable |
| `Plaintiff_5` | CheckBox | 1 | Check if applicable |
| `Defendant_3` | CheckBox | 1 | Check if applicable |
| `Defendant_4` | CheckBox | 1 | Check if applicable |
| `Defendant_5` | CheckBox | 1 | Check if applicable |
| `Neither` | CheckBox | 1 | Check if applicable |
| `Neither_2` | CheckBox | 1 | Check if applicable |
| `Neither_3` | CheckBox | 1 | Check if applicable |
| `Childs NameRow1` | Text | 1 |  |
| `DateofBirthmmddyyyyRow1` | Text | 1 | MM/DD/YYYY format |
| `Childs NameRow2` | Text | 1 |  |
| `DateofBirthmmddyyyyRow2` | Text | 1 | MM/DD/YYYY format |
| `Childs NameRow3` | Text | 1 |  |
| `DateofBirthmmddyyyyRow3` | Text | 1 | MM/DD/YYYY format |
| `Childs NameRow4` | Text | 1 |  |
| `DateofBirthmmddyyyyRow4` | Text | 1 | MM/DD/YYYY format |
| `Childs NameRow5` | Text | 1 |  |
| `DateofBirthmmddyyyyRow5` | Text | 1 | MM/DD/YYYY format |
| `Childs NameRow6` | Text | 1 |  |
| `DateofBirthmmddyyyyRow6` | Text | 1 | MM/DD/YYYY format |
| `Selfsupport reserve` | CheckBox | 1 | Check if applicable |
| `Belowpovertylevel` | CheckBox | 1 | Check if applicable |
| `gross income 1` | Text | 1 |  |
| `gross income 2` | Text | 1 |  |
| `support paid 1` | Text | 1 |  |
| `support paid 2` | Text | 1 |  |
| `child support 1` | Text | 1 |  |
| `child support 2` | Text | 1 |  |
| `Subtractlines4aand 4b fromline36 Other children living with nonprimarycare providerSeeinstructionsonpage 3` | Text | 1 |  |
| `other children` | Text | 1 |  |
| `a Subtractlines4a and4b fromline3` | Text | 1 |  |
| `b Subtractline 6fromline 5` | Text | 1 |  |
| `c Addlines7aand 7bb` | Text | 1 |  |
| `percent 1` | Text | 1 |  |
| `percent 2` | Text | 1 |  |
| `Totalnumber ofchildrena` | Text | 2 |  |
| `multiplied byamountfromtableb` | Text | 2 |  |
| `9c` | Text | 2 |  |
| `1` | Text | 2 |  |
| `2` | Text | 2 |  |
| `3` | Text | 2 |  |
| `4` | Text | 2 |  |
| `5` | Text | 2 |  |
| `6` | Text | 2 |  |
| `undefined` | Text | 2 |  |
| `undefined_2` | Text | 2 |  |
| `undefined_3` | Text | 2 |  |
| `undefined_4` | Text | 2 |  |
| `undefined_5` | Text | 2 |  |
| `undefined_6` | Text | 2 |  |
| `10` | Text | 2 |  |

*... and 45 additional fields (see fields.json for complete list)*

## AI Hints

- **Service Requirements**: Ensure proper service on all parties.
- **Financial Disclosure**: If financial issues involved, FM-043 Financial Statement may be required.
- **Child-Related**: If children involved, parenting plan and child support worksheets may be needed.
- **Docket Number**: Leave blank for new filings; clerk assigns. Enter if responding to existing case.
- **Complex Form**: This form has 105 fields. Consider section-by-section completion.

## Validation Checklist

- [ ] All required party names are filled in
- [ ] Court location/county is correct for venue
- [ ] Docket number included (if existing case)
- [ ] All dates are in correct format (MM/DD/YYYY)
- [ ] Service of process addressed
- [ ] Financial disclosures attached if required

## Related Forms

- **FM-002** — Family and Probate Matter Summary Sheet
- **FM-004** — COMPLAINT FOR DIVORCE
- **FM-006** — COMPLAINT FOR DETERMINATION OF PARENTAGE,
- **FM-008** — PETITION FOR EXPEDITED ENFORCEMENT
- **FM-020** — ENTRY OF APPEARANCE
- **FM-040-A** — SUPPLEMENTAL CHILD SUPPORT WORKSHEET
- **FM-042** — CERTIFICATE IN LIEU OF FINANCIAL STATEMENT
- **FM-043** — FINANCIAL STATEMENT
- **FM-050** — CHILD SUPPORT AFFIDAVIT
- **FM-052** — FEDERAL AFFIDAVIT
