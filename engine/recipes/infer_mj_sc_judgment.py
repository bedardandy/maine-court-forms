"""MJ-SC family (Small Claims Judgment Debtor) recipe-3 inference.

Covers MJ-SC-001 (Disclosure Affidavit / Periodic Payment Agreement),
MJ-SC-005 (Disclosure Subpoena / Order to Appear), and MJ-SC-012
(Business Disclosure & Installment Agreement).

All three share the judgment creditor/debtor caption + financial
disclosure (gross/net pay, deductions, dependents, expenses) +
installment-payment agreement narrative. One unified script fills
the common widgets; form-specific blocks branch on form_id.

Reads case.facts: judgment_creditor, judgment_debtor, gross_pay,
net_pay, pay_period, dependents, spouse_income, living_expenses,
installment_amount, installment_period, installment_start_date,
judgment_amount, judgment_costs, judgment_date.
"""
from __future__ import annotations

import sys


def _set(answers: dict, fid: str, value: str) -> bool:
    if fid not in answers: return False
    if answers.get(fid): return False
    answers[fid] = value
    return True


def _iso_to_us(iso: str) -> str:
    if not iso or "-" not in iso: return iso
    y, m, d = iso[:10].split("-")
    return f"{m}/{d}/{y}"


def process(kv_map: dict, case: dict) -> tuple[dict, list]:
    out = dict(kv_map)
    changes = []
    facts = case.get("facts") or {}
    parties = case.get("parties") or {}
    form_id = (kv_map.get("_form_id") or "").upper()  # may be absent

    # Determine creditor / debtor from case parties or facts
    creditor = (facts.get("judgment_creditor")
                or (parties.get("plaintiff") or {}).get("full_name")
                or (parties.get("petitioner") or {}).get("full_name") or "")
    debtor = (facts.get("judgment_debtor")
              or (parties.get("defendant") or {}).get("full_name")
              or (parties.get("respondent") or {}).get("full_name") or "")
    debtor_party = parties.get("defendant") or parties.get("respondent") or {}

    # Captions — MJ-SC-001 uses underscored `judgment_creditor`,
    # MJ-SC-012 uses the squashed `judgmentcreditor` without underscores.
    # Fill BOTH variants so the same script covers both forms.
    for fid in ("judgment_creditor", "creditor", "judgmentcreditor"):
        if creditor and _set(out, fid, creditor):
            changes.append((fid, creditor, "creditor"))
    for fid in ("judgment_debtor", "debtor",
                 "judgmentdebtor", "thejudgmentdebtor"):
        if debtor and _set(out, fid, debtor):
            changes.append((fid, debtor, "debtor"))
    # MJ-SC-012 has squashed location_town too
    court = case.get("court") or {}
    for fid in ("location_town", "locationtown"):
        if _set(out, fid, court.get("location", "")):
            changes.append((fid, court.get("location",""), "loc-town"))

    # "I, ___" affiant = debtor
    if debtor and _set(out, "i", debtor):
        changes.append(("i", debtor, "affiant"))

    # Debtor address (item 1)
    debtor_addr = debtor_party.get("address", "")
    if debtor_addr:
        for fid in ("1_my_address_is", "my_address_is",
                     "the_judgment_debtor_presently_resides_at"):
            if _set(out, fid, debtor_addr):
                changes.append((fid, debtor_addr, "debtor-addr"))

    # Everything below states the debtor's sworn financial disclosure —
    # fill ONLY from explicit facts. The old defaults invented an
    # employer, pay, a deductions table, other debts, dependents, spouse
    # income/marital status, expenses, installment terms, and judgment
    # amounts.

    # Employment (item 2 / capacity)
    employer = facts.get("employer_name", "")
    capacity = facts.get("employer_capacity", "")
    if employer and _set(out, "2_i_am_employed_by", employer):
        changes.append(("2_i_am_employed_by", employer, "employer"))
    if capacity and _set(out, "in_the_capacity_of", capacity):
        changes.append(("in_the_capacity_of", capacity, "capacity"))

    # Gross pay / net pay
    gross = facts.get("gross_pay", "")
    net = facts.get("net_pay", "")
    period = facts.get("pay_period", "")
    if gross and _set(out, "3_my_gross_pay_is", f"${gross}"):
        changes.append(("3_my_gross_pay_is", f"${gross}", "gross-pay"))
    if period and _set(out, "per", period):
        changes.append(("per", period, "pay-period"))
    if net and _set(out, "a_court_or_state_agency_is", f"${net}"):
        changes.append(("a_court_or_state_agency_is", f"${net}", "net-pay"))
    if period and _set(out, "per_2", period):
        changes.append(("per_2", period, "pay-period-2"))

    # MJ-SC-001 — ITEM 1-4 deductions table (page 1 y=323-384). Each row
    # has `item_N` (description) + `undefined_N` (dollar amount).
    deductions = facts.get("payroll_deductions") or []
    for i, (desc, amt) in enumerate(deductions[:4], start=1):
        item_fid = f"item_{i}" if i > 0 else "item_1"
        undef_fid = f"undefined" if i == 1 else f"undefined_{i}"
        if _set(out, item_fid, desc):
            changes.append((item_fid, desc, f"deduction-item-{i}"))
        if _set(out, undef_fid, f"${amt}"):
            changes.append((undef_fid, f"${amt}", f"deduction-amt-{i}"))
    # `undefined_5` is the total-deductions amount (sum)
    if deductions:
        try:
            total_ded = sum(float(amt.replace(",", ""))
                            for _, amt in deductions[:4])
            if _set(out, "undefined_5", f"${total_ded:,.2f}"):
                changes.append(("undefined_5", f"${total_ded:,.2f}",
                                  "deduction-total"))
        except Exception:
            pass

    # MJ-SC-001 — DEBT OWED TO 1-3 table (p0 y=449-479). Each row:
    # `debt_owed_to_N` (creditor name), `undefined_{6,8,10}` (total owing),
    # `per_{3,4,5}` (installment period), `undefined_{7,9,11}` (per-payment).
    debts = facts.get("other_debts") or []
    debt_undef_owe = ("undefined_6", "undefined_8", "undefined_10")
    debt_undef_pay = ("undefined_7", "undefined_9", "undefined_11")
    debt_period_fids = ("per_3", "per_4", "per_5")
    for i, (cred, owe, per, pay) in enumerate(debts[:3]):
        creditor_fid = f"debt_owed_to_{i+1}"
        if _set(out, creditor_fid, cred):
            changes.append((creditor_fid, cred, f"debt-creditor-{i+1}"))
        if _set(out, debt_undef_owe[i], f"${owe}"):
            changes.append((debt_undef_owe[i], f"${owe}", f"debt-owe-{i+1}"))
        if _set(out, debt_period_fids[i], per):
            changes.append((debt_period_fids[i], per, f"debt-period-{i+1}"))
        if _set(out, debt_undef_pay[i], f"${pay}"):
            changes.append((debt_undef_pay[i], f"${pay}", f"debt-pay-{i+1}"))

    # Dependents
    dependents = facts.get("dependents", "")
    if dependents:
        for fid in ("7_i_have_dependents", "dependents", "i_have_dependents"):
            if _set(out, fid, dependents):
                changes.append((fid, dependents, "dependents"))

    # Spouse income (the old defaults asserted "$0.00" and "not married")
    spouse_income = facts.get("spouse_income", "")
    spouse_source = facts.get("spouse_source", "")
    if spouse_income:
        for fid in ("8_my_spouse_receives_income_of",):
            if _set(out, fid, f"${spouse_income}"):
                changes.append((fid, f"${spouse_income}", "spouse-income"))

    # Living expenses
    expenses = facts.get("living_expenses", "")
    if expenses:
        for fid in ("9_my_necessary_living_expenses_are",):
            if _set(out, fid, f"${expenses}"):
                changes.append((fid, f"${expenses}", "expenses"))

    # Installment agreement — terms ONLY when explicitly provided (were
    # $75/month commencing on a stock date).
    install_amount = facts.get("installment_amount", "")
    install_period = facts.get("installment_period", "")
    install_start = facts.get("installment_start_date", "")
    install_start_us = _iso_to_us(install_start) if install_start else ""
    if install_amount:
        for fid in ("10_i_agree_to_pay",
                     "agree_to_pay",
                     "5_judgment_debtor_agrees_to_pay",
                     "5_judgmentdebtoragreestopay"):
            if _set(out, fid, f"${install_amount}"):
                changes.append((fid, f"${install_amount}", "install-amt"))
    if install_start_us:
        for fid in ("commencing", "installment_start",
                     "commencingmmddyyyy", "commencing_mmddyyyy"):
            if _set(out, fid, install_start_us):
                changes.append((fid, install_start_us, "install-start"))
    # `per_8` (item-10 pay period on MJ-SC-001), `per_6` (item-5 on MJ-SC-012)
    if install_period:
        for fid in ("per_8", "per_6"):
            if _set(out, fid, install_period):
                changes.append((fid, install_period, "install-period"))

    # MJ-SC-001 — installment payment schedule (page 2): amount + period
    # + payee + commencement. Payee from facts, else the court clerk at
    # the real court location (never a defaulted town).
    payee = facts.get("installment_payee", "")
    if not payee and court.get("location") and install_amount:
        payee = (f"the Clerk of the District Court, "
                  f"{court['location']} location")
    if install_amount and _set(out, "payments_of_1", f"${install_amount}"):
        changes.append(("payments_of_1", f"${install_amount}", "pay-of-1"))
    if install_period and _set(out, "per_9", install_period):
        changes.append(("per_9", install_period, "per-9"))
    if payee and _set(out, "payments_of_2", payee):
        changes.append(("payments_of_2", payee, "pay-of-2-payee"))
    # `to` (item-10 payee on MJ-SC-001 and MJ-SC-012)
    if payee and _set(out, "to", payee):
        changes.append(("to", payee, "install-payee"))
    # `from` (item-8 spouse-income source) — re-use spouse_source
    if spouse_source and _set(out, "from", spouse_source):
        changes.append(("from", spouse_source, "spouse-source"))

    # MJ-SC-001 — balance acknowledgment narrative (item 11 - p1 y=624)
    # — ONLY from explicit facts (was a stock $3,500 balance).
    balance_due = facts.get("balance_due",
                                facts.get("judgment_amount", ""))
    balance_ack = facts.get("balance_acknowledgment", "")
    if not balance_ack and balance_due:
        balance_ack = (f"The parties acknowledge that the balance due, "
                        f"as of this date, is ${balance_due}.")
    if balance_ack and _set(out,
            "the_parties_acknowledge_that_the_balance_due_as_of_this_date",
            balance_ack):
        changes.append((
            "the_parties_acknowledge_that_the_balance_due_as_of_this_date",
            balance_ack, "balance-ack"))

    # MJ-SC-001 — page-2 attorney + signature block (date_mmddyyyy_3,
    # undefined_14, attorney_for_judgment_creditor)
    attorney = parties.get("attorney") or {}
    atty_name = attorney.get("full_name", "")
    if atty_name and _set(out, "attorney_for_judgment_creditor", atty_name):
        changes.append(("attorney_for_judgment_creditor", atty_name,
                          "atty-creditor"))
    sig_date_us = _iso_to_us(case.get("filing_date")
                                or case.get("event_date", ""))
    for fid in ("date_mmddyyyy_3", "undefined_14"):
        if _set(out, fid, sig_date_us):
            changes.append((fid, sig_date_us, "sig-date-3"))

    # MJ-SC-012 — entity type radio — check ONLY when explicitly provided
    # (was defaulted to "corporation").
    entity_type = facts.get("entity_type", "")
    entity_map = {
        "corporation": "corporation",
        "llc": "limitedliabilitycompany",
        "llp": "limitedliabilitypartnership",
        "lp": "limitedpartnership",
        "nonprofit": "nonprofit_corporation",
        "other": "other",
    }
    entity_fid = entity_map.get(entity_type) if entity_type else None
    if entity_fid and _set(out, entity_fid, "X"):
        changes.append((entity_fid, "X", "entity-type"))
    # MJ-SC-012 — gross income / net profit (squashed names)
    if gross and _set(out, "2_judgment_debtorsgrossincome", f"${gross}"):
        changes.append(("2_judgment_debtorsgrossincome", f"${gross}",
                          "gross-mj012"))
    if net and _set(out, "3_judgmentdebtorsnetprofit", f"${net}"):
        changes.append(("3_judgmentdebtorsnetprofit", f"${net}",
                          "net-mj012"))
    # MJ-SC-012 — title for entity signer — ONLY when explicitly provided
    # (was defaulted to "President").
    title = facts.get("debtor_title", "")
    if title and _set(out, "title", title):
        changes.append(("title", title, "debtor-title"))
    if title and _set(out, "inthecapacityof", title):
        changes.append(("inthecapacityof", title, "debtor-capacity"))
    # MJ-SC-012 squashed perjury checkbox — ONLY on an explicit boolean
    # fact; never auto-swear an oath on the affiant's behalf.
    if facts.get("perjury_acknowledged") is True:
        for fid in ("i_swearunderpenaltyofperjurythattheabove_statementsaretruean",
                     "i_swearunderpenaltyofperjurythattheabove_statementsaretrueand"):
            if _set(out, fid, "X"):
                changes.append((fid, "X", "perjury-mj012"))

    # Judgment facts (MJ-SC-005-style — order to appear) — ONLY when
    # explicitly provided (were $3,500 / $120 / stock-date defaults).
    judgment_amount = facts.get("judgment_amount", "")
    judgment_costs = facts.get("judgment_costs", "")
    judgment_date = _iso_to_us(facts.get("judgment_date", ""))
    if judgment_amount and _set(out, "the_judgment_debtor_in_the_amount_of",
                                  f"${judgment_amount}"):
        changes.append(("the_judgment_debtor_in_the_amount_of",
                          f"${judgment_amount}", "judgment-amount"))
    if judgment_costs and _set(out, "plus_costs_of", f"${judgment_costs}"):
        changes.append(("plus_costs_of", f"${judgment_costs}", "judgment-costs"))
    if judgment_date:
        for fid in ("on_mmddyyyy", "on_mmddyyyy_2", "on_mmddyyyy_3"):
            if _set(out, fid, judgment_date):
                changes.append((fid, judgment_date, "judgment-date"))

    # Generic acknowledgements — ONLY on an explicit boolean fact (these
    # were auto-filled "I agree" on the debtor's behalf).
    if facts.get("installment_agreement_acknowledged") is True:
        for fid in ("i_understand_that_if_i_fail_to_make_two_or_more_payments",
                     "i_understand"):
            if _set(out, fid, "I agree"):
                changes.append((fid, "I agree", "acknowledgment"))

    # Notary block — "Personally appeared the above-named ___ and made oath
    # that the foregoing statements are true." The affiant is the disclosing
    # party, i.e. the judgment DEBTOR, never the creditor. build_kv_map's
    # narrative pass stamps this blank with the first-listed party (the
    # creditor), so force-override to the debtor across all field_id variants
    # (spaced + squashed) used by MJ-SC-001/005/012.
    if debtor:
        for fid in ("personally_appeared_the_above_named",
                     "personally_appeared_the_abovenamed",
                     "personallyappearedtheabovenamed"):
            if fid in out and out.get(fid, "") != debtor:
                out[fid] = debtor
                changes.append((fid, debtor, "notary-affiant"))

    # Date in notary block
    notary_date = _iso_to_us(case.get("event_date") or
                                case.get("filing_date") or "2024-12-15")
    for fid in ("date_mmddyyyy", "notary_date_mmddyyyy"):
        if _set(out, fid, notary_date):
            changes.append((fid, notary_date, "notary-date"))

    # Notary signing role
    if _set(out, "clerk_notary_public_attorney", "Notary Public"):
        changes.append(("clerk_notary_public_attorney", "Notary Public",
                          "notary-role"))

    return out, changes


if __name__ == "__main__":
    print("Use via fill_and_audit.py RECIPE3 dispatch (MJ-SC-001/005/012)")
    sys.exit(0)
