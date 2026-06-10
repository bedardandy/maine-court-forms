"""MJ debtor disclosure family recipe-3 inference.

Covers MJ-005 (Judgment Debtor Disclosure) and MJ-014 (Criminal
Restitution / Creditor-Victim affidavit). Both share:
  - judgment_creditor / debtor (caption variants: creditorvictim,
    debtordefendant)
  - location_town, docket_no
  - affiant identity + service date + sworn statement
  - debtor DOB + criminal-matter docket xref (MJ-014 only)

MJ-007 has its own dedicated script (wage garnishment) and is NOT
covered here.
"""
from __future__ import annotations

import sys


def _set(answers: dict, fid: str, value: str) -> bool:
    if fid not in answers: return False
    if answers.get(fid): return False
    answers[fid] = value
    return True


def process(kv_map: dict, case: dict) -> tuple[dict, list]:
    out = dict(kv_map)
    changes = []
    facts = case.get("facts") or {}
    parties = case.get("parties") or {}
    court = case.get("court") or {}

    # Form discriminators. `undefined` / `undefined_2` are generic PDF-source
    # widget names that mean different things per form, so the MJ-015-specific
    # amount/signature assignments below must be gated to MJ-015 only:
    #   - MJ-009  `undefined_2` is the "(plus interest of $___)" amount line.
    #   - MJ-014  `undefined`   is "Telephone:" and `undefined_2` is
    #             "Name of defendant:".
    # Without gating, the MJ-015 block stamped the affiant name into MJ-009's
    # interest field and the principal amount into MJ-014's telephone field.
    is_mj015 = "installment_order_dated_mmddyyyy" in kv_map
    is_mj014 = "mailing_address_of_creditorvictim_1" in kv_map

    # The case-template criminal sample uses defendant + surety; map
    # surety→creditor (victim) and defendant→debtor.
    creditor = (parties.get("creditor")
                or parties.get("victim")
                or parties.get("surety")
                or parties.get("plaintiff") or {})
    debtor = (parties.get("debtor")
              or parties.get("defendant")
              or parties.get("respondent") or {})

    cred_name = (facts.get("judgment_creditor")
                  or creditor.get("full_name", ""))
    debt_name = (facts.get("judgment_debtor")
                  or debtor.get("full_name", ""))

    # Captions — MJ-005 uses judgment_creditor/judgment_debtor;
    # MJ-014 uses creditorvictim/debtordefendant.
    for fid, val in [
        ("judgment_creditor",  cred_name),
        ("judgment_debtor",    debt_name),
        ("creditorvictim",     cred_name),
        ("debtordefendant",    debt_name),
        ("location_town",      court.get("location", "")),
        ("docket_no",          case.get("docket_no", "")),
    ]:
        if val and _set(out, fid, val):
            changes.append((fid, val, "caption"))

    # Affiant — for MJ-005 the debtor is filling out the form themselves
    # ("I, <debtor>, having been served...")
    affiant = facts.get("affiant_name", debt_name)
    if _set(out, "i", affiant):
        changes.append(("i", affiant, "affiant"))
    if _set(out, "now_comes", cred_name):
        changes.append(("now_comes", cred_name, "now-comes"))

    # Service date on Order to Hold and Answer
    svc_date = (facts.get("service_date")
                or facts.get("event_date")
                or case.get("event_date", ""))
    if _set(out, "service_of_the_order_to_hold_and_answer_on_me_on", svc_date):
        changes.append(("service_of_the_order_to_hold_and_answer_on_me_on",
                        svc_date, "service-date"))

    # MJ-005 disclosure narratives — these are sworn statements about the
    # disclosing party's assets. Fill ONLY when explicitly provided (the
    # old defaults swore a clean "no debts/property" disclosure for every
    # fill).
    hold_narrative = facts.get("mj_hold_narrative", "")
    if hold_narrative and _set(out,
            "i_hold_the_above_debts_or_property_but_i_do_not_",
            hold_narrative):
        changes.append(("i_hold_the_above_debts_or_property_but_i_do_not_",
                        hold_narrative, "hold-narr"))

    # MJ-005 wide narrative widgets named text2/text3/text5 (PDF-source
    # generic names — schema artifact, not labels). By rect-y order:
    #   text2 (y=216, 544w): "owed the following debts to the JD" content
    #   text3 (y=336, 543w): "hold the above" continuation / property
    #   text5 (y=474, 252w): printed-name signature
    debts_narr = facts.get("mj005_debts_narrative", "")
    if debts_narr and _set(out, "text2", debts_narr):
        changes.append(("text2", debts_narr, "debts-narr"))

    property_narr = facts.get("mj005_property_narrative", "")
    if property_narr and _set(out, "text3", property_narr):
        changes.append(("text3", property_narr, "property-narr"))

    # text5 is the signature print-name widget
    if _set(out, "text5", affiant):
        changes.append(("text5", affiant, "sig-print"))

    # Sworn-statement line — write ONLY on an explicit boolean fact;
    # never auto-swear an oath on the affiant's behalf.
    swear = ("I swear under penalty of perjury that the above statements "
             "are true and accurate to the best of my knowledge.")
    if (facts.get("perjury_acknowledged") is True
            and _set(out, "i_swear_under_penalty_of_perjury_that_the_above_",
                       swear)):
        changes.append(("i_swear_under_penalty_of_perjury_that_the_above_",
                        swear, "swear"))

    # Date of signature
    sig_date = (case.get("filing_date") or case.get("event_date") or "")
    if sig_date and "T" in sig_date:
        sig_date = sig_date[:10]  # strip ISO time suffix
    if _set(out, "date_mmddyyyy", sig_date):
        changes.append(("date_mmddyyyy", sig_date, "sign-date"))

    # MJ-014: creditor/victim 3-line mailing address (split address)
    cred_addr = creditor.get("address", "")
    if cred_addr:
        addr_lines = [s.strip() for s in cred_addr.split(",")] + ["", "", ""]
        line1 = addr_lines[0]
        line2 = addr_lines[1] if len(addr_lines) > 1 else ""
        line3 = ", ".join(addr_lines[2:]).strip(", ")
        for fid, val in [
            ("mailing_address_of_creditorvictim_1", line1),
            ("mailing_address_of_creditorvictim_2", line2),
            ("mailing_address_of_creditorvictim_3", line3),
        ]:
            if val and _set(out, fid, val):
                changes.append((fid, val, "cred-addr"))

    # MJ-014: criminal docket xref + debtor DOB
    crim_docket = (facts.get("underlying_criminal_docket")
                    or case.get("docket_no", ""))
    if _set(out, "docket_number_of_the_underlying_criminal_matter",
            crim_docket):
        changes.append(("docket_number_of_the_underlying_criminal_matter",
                        crim_docket, "crim-docket"))

    debt_dob = debtor.get("dob", "")
    if _set(out, "defendants_date_of_birth_mmddyyyy", debt_dob):
        changes.append(("defendants_date_of_birth_mmddyyyy",
                        debt_dob, "debtor-dob"))

    # MJ-009 — Motion for Order of Capias (default judgment after missed
    # installment payments). Fills failed-payment narrative, installment
    # order date, payment amount + period, and total owed.
    if "courts_installment_order_dated_mmddyyyy" in kv_map:
        # Installment order date / payment terms / amounts — these state
        # the terms of a real court order and the debt. Fill ONLY when
        # explicitly provided (the old defaults invented an order date,
        # $75/month terms, $1,250 owed and $120 costs).
        inst_date = facts.get("mj009_installment_order_date", "")
        if "-" in str(inst_date):
            y, m, d = str(inst_date)[:10].split("-")
            inst_date_us = f"{m}/{d}/{y}"
        else:
            inst_date_us = inst_date
        if inst_date_us and _set(out, "courts_installment_order_dated_mmddyyyy",
                                   inst_date_us):
            changes.append(("courts_installment_order_dated_mmddyyyy",
                              inst_date_us, "mj009-inst-date"))
        pay_amt = facts.get("mj009_pay_amount",
                                 facts.get("installment_amount", ""))
        pay_per = facts.get("mj009_pay_period",
                                 facts.get("installment_period", ""))
        if pay_amt and _set(out, "pay", f"${pay_amt}"):
            changes.append(("pay", f"${pay_amt}", "mj009-pay"))
        if pay_per and _set(out, "per", pay_per):
            changes.append(("per", pay_per, "mj009-per"))
        # Failure checkbox — check ONLY on an explicit boolean fact (was
        # auto-checked, asserting the debtor missed payments).
        if (facts.get("mj009_failed_payment") is True
                and _set(out, "check_box1", "X")):
            changes.append(("check_box1", "X", "mj009-failed-pay"))
        owed = facts.get("mj009_owed_amount", "")
        if owed and _set(out,
                "the_judgment_creditor_currently_owes_the_judgment_creditor",
                f"${owed}"):
            changes.append(("the_judgment_creditor_currently_owes_the_judgment_creditor",
                              f"${owed}", "mj009-owed"))
        # `undefined_2` is the "(plus interest of $___)" amount on the owed
        # line — a dollar field, NOT a signature. When the owed amount is
        # known, interest defaults to 0.00 rather than fabricating a
        # figure (understates rather than invents).
        interest = facts.get("mj009_interest", "0.00" if owed else "")
        if interest and _set(out, "undefined_2", f"${interest}"):
            changes.append(("undefined_2", f"${interest}", "mj009-interest"))
        costs = facts.get("mj009_costs", "")
        if costs and _set(out, "plus_costs_of", f"${costs}"):
            changes.append(("plus_costs_of", f"${costs}", "mj009-costs"))
        if owed:
            try:
                total = (float(str(owed).replace(",", ""))
                         + float(str(interest or 0).replace(",", ""))
                         + float(str(costs or 0).replace(",", "")))
                if _set(out, "for_a_total_of", f"${total:,.2f}"):
                    changes.append(("for_a_total_of", f"${total:,.2f}",
                                      "mj009-total"))
            except Exception:
                pass

    # MJ-015 — installment-order owed-amount affidavit. Employment
    # narrative ONLY when explicitly provided (the old default asserted
    # the debtor is employed and refused to pay despite demand).
    employment_narr = facts.get("mj_employment_narrative", "")
    if employment_narr:
        # Schema field_id is the long form ending in "_to_be_" — set both
        # variants to be safe.
        for fid in ("employment_information_pursuant_to_14_mrs_3126a8_to_be_",
                     "employment_information_pursuant_to_14_mrs_3126a8_t"):
            if _set(out, fid, employment_narr):
                changes.append((fid, employment_narr, "mj15-employment"))

    install_date = facts.get("installment_order_date", "")
    if install_date and _set(out, "installment_order_dated_mmddyyyy",
                               install_date):
        changes.append(("installment_order_dated_mmddyyyy",
                        install_date, "mj15-install-date"))

    # Balance narrative — ONLY when explicitly provided (was a stock
    # principal-plus-interest description).
    judgment_balance = facts.get("mj_judgment_balance", "")
    if judgment_balance:
        for fid in ("the_judgment_debtor_currently_owes_the_judgment_credito",
                     "the_judgment_debtor_currently_owes_the_judgment_cr"):
            if _set(out, fid, judgment_balance):
                changes.append((fid, judgment_balance, "mj15-balance-narr"))

    # MJ-015 — sworn-statement (longer field_id variant); ONLY on an
    # explicit boolean fact — never auto-swear.
    swear = ("I swear under penalty of perjury that the above statements "
             "are true and accurate to the best of my knowledge.")
    if facts.get("perjury_acknowledged") is True:
        for fid in ("i_swear_under_penalty_of_perjury_that_the_above_stateme",):
            if _set(out, fid, swear):
                changes.append((fid, swear, "mj15-swear-long"))

    # MJ-015 amount line + signature. `undefined`/`undefined_2` collide with
    # other forms (see discriminator note above), so gate to MJ-015.
    # Principal/costs ONLY when explicitly provided (were $2,450/$175
    # stock amounts).
    if is_mj015:
        principal = facts.get("mj_principal", "")
        costs = facts.get("mj_costs", "")
        total = ""
        if principal:
            try:
                total = f"{float(principal.replace(',','')) + float((costs or '0').replace(',','')):,.2f}"
            except Exception:
                total = principal

        if principal and _set(out, "undefined", principal):
            changes.append(("undefined", principal, "mj15-principal"))
        if costs and _set(out, "plus_costs_of", costs):
            changes.append(("plus_costs_of", costs, "mj15-costs"))
        if total and _set(out, "for_a_total_of", total):
            changes.append(("for_a_total_of", total, "mj15-total"))
        # MJ-015 signature field aliased to undefined_2
        if _set(out, "undefined_2", affiant):
            changes.append(("undefined_2", affiant, "mj15-signer"))

    # MJ-014 — `undefined_2` is the "Name of defendant:" field and `undefined`
    # is "Telephone:". Set them explicitly here (the MJ-015 block no longer
    # touches them).
    if is_mj014:
        if _set(out, "undefined_2", debt_name):
            changes.append(("undefined_2", debt_name, "mj14-defendant-name"))
        cred_phone = creditor.get("phone", "")
        if cred_phone and _set(out, "undefined", cred_phone):
            changes.append(("undefined", cred_phone, "mj14-cred-phone"))

    return out, changes


if __name__ == "__main__":
    print("Use via fill_and_audit.py RECIPE3 dispatch")
    sys.exit(0)
