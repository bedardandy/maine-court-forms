#!/usr/bin/env python3
"""Generate a per-form examples/sample_case.json from the form's own keys.

Historically 332/342 forms shipped the same generic Doe-v-Roe family-matters
sample, so MCP get_form returned a "sample" that didn't exercise the form's
own canonical keys (criminal/eviction/probate forms showed marriage facts).

This tool derives each form's sample from its declared key set
(``mapping.json: facts.used`` — see tools/derive_required_facts.py):

* mapping-tier forms get a minimal case carrying exactly the matter /
  parties / party keys the mapping resolves, plus a synthesized fictional
  value for every ``facts.*`` key (checkbox-only keys get "yes").
* recipe-tier forms keep the full generic base (the generic engine field
  map consumes the standard basics) and add synthesized values for the
  fact keys their recipe reads. Recipes parse typed fact formats —
  structured rows (date+hours logs, deduction tables), enum tokens
  ("admit", "satisfactory"), bare numbers for int()/float(), booleans
  checked with ``is True`` — so those keys get exact typed values from
  TYPED_FACT_VALUES instead of the string heuristics. The enriched
  sample is accepted only if the recipe (a) still runs and (b) keeps
  every widget it filled from the base sample filled while the facts
  demonstrably drive the fill — more widgets filled, or a widget now
  carrying a fact-supplied value instead of a stock/derived fallback.
  Otherwise the form keeps the generic sample (marked "generic": true).
* forms with nothing to exercise (``no-mappable-fields`` / empty key set)
  keep the generic sample with ``"generic": true`` so get_form can say so.

All values are clearly fictional placeholders, same convention as the
generic sample (Doe/Roe/Sample names, example.com, 207-555-01xx phones,
"00000" numbers) — never realistic-looking real-person data, and never a
claimed legal fact. Every generated sample is preflight-validated
(tools/preflight.py) before writing.

Hand-built samples are preserved: the tool only rewrites a sample that is
(semantically) the shared generic copy. Re-runnable / idempotent.

    python3 tools/gen_sample_cases.py            # all forms
    python3 tools/gen_sample_cases.py --forms PA-001 --dry-run
"""
from __future__ import annotations

import argparse
import copy
import json
import pathlib
import sys

OSS_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(OSS_ROOT))

from tools.preflight import preflight_case  # noqa: E402

BASE_PATH = OSS_ROOT / "tools" / "canonical_sample_case.json"

SUMMARY = ("Sample fact pattern for testing form fills. All names, contacts, "
           "dates, and amounts here are fictitious placeholders (Doe/Roe, "
           "example.com, 555 phone range).")

# Roster for roles the generic base doesn't carry.
EXTRA_PARTIES = {
    "other_party": {
        "full_name": "John R. Roe",
        "address": "456 Oak Avenue",
        "city": "Portland", "state": "ME", "zip": "04101",
        "phone": "207-555-0102", "email": "john.roe@example.com",
        "date_of_birth": "1983-06-20",
    },
}
# Numbered children beyond the base's child_1/child_2 (all fictional).
CHILD_NAMES = ["Sam Doe", "Alex Doe", "Riley Doe", "Casey Doe", "Jordan Doe",
               "Quinn Doe", "Avery Doe", "Rowan Doe", "Sage Doe", "Remy Doe",
               "Blake Doe", "Drew Doe"]
CHILD_DOBS = ["2015-04-10", "2018-09-05", "2012-02-14", "2010-07-22",
              "2016-11-03", "2014-05-30", "2019-08-17", "2011-01-25",
              "2013-10-09", "2017-03-12", "2009-12-01", "2020-06-18"]


def _party_for_role(base: dict, role: str) -> dict:
    parties = base.get("parties") or {}
    if role in parties:
        return copy.deepcopy(parties[role])
    if role in EXTRA_PARTIES:
        return copy.deepcopy(EXTRA_PARTIES[role])
    if role.startswith("child_") and role[6:].isdigit():
        i = int(role[6:]) - 1
        return {"full_name": CHILD_NAMES[i % len(CHILD_NAMES)],
                "date_of_birth": CHILD_DOBS[i % len(CHILD_DOBS)],
                "address": "123 Main Street", "city": "Portland",
                "state": "ME", "zip": "04101"}
    # Unknown role (shouldn't ship — preflight would flag it).
    return {"full_name": "Riley T. Doe"}


# Recipe-parsed typed facts. The engine recipes (engine/recipes/infer_*.py)
# consume these keys as structured rows, enum tokens, bare numbers
# (int()/float()), booleans (checked with ``is True``), or strings written
# verbatim into mm/dd/yyyy widgets — the generic string heuristics in
# synth_fact_value() crash or skew those parsers. Values follow the same
# obviously-fictional conventions as the generic base sample (Doe/Roe/Sample
# names, example.com, 207-555-01xx phones, "00000"/"ME-000000" numbers) and
# stay coherent with the base parties (Jane Q. Doe = plaintiff, John R. Roe
# = defendant, Pat L. Lawyer, Esq. = attorney, Sam/Alex Doe = children).
TYPED_FACT_VALUES: dict = {
    # ── AD family (infer_ad_family) ──
    "ad003_role": "guardian",                       # enum -> role checkbox
    "ad003_signer_name": "Riley T. Doe",
    "ad004_petitioners": "Pat R. Sample and Lee A. Sample",
    "ad004_new_name": "Sam Sample",
    "ad017_position": "admit",                      # admit|deny|neither
    "ad017_inherit": "request",                     # request|do_not_request
    "ad032_aliases": "Sam S. Doe (fictional former name)",
    "ad_consent_taker": "Hon. Riley T. Sample, Probate Judge (fictional)",
    "ad_prospective_adoptive_parent": "Pat R. Sample and Lee A. Sample",
    "ad_marriage_date_place": "01/15/2010, Portland, Maine",
    "ad_art_explanation": ("Sample (fictional): no assisted-reproduction "
                           "parentage issues are claimed in this test "
                           "fact pattern."),
    # AD-022 checks membership against the four checkbox field_ids; the
    # base default checks two — list all four so coverage improves.
    "ad_disclosure_types": [
        "to_obtain_a_certificate_of_adoption",
        "to_obtain_a_certified_copy_of_the_adoption_record",
        "to_obtain_medical_andor_genetic_information_or",
        "to_obtain_other_information_as_specified_below",
    ],
    # 5 numbered narrative widgets — keep all five rows filled.
    "ad_disclosure_reasons": [
        f"Sample disclosure reason {i} (fictional) for testing this "
        f"form's fill." for i in range(1, 6)
    ],
    "adoptee_birth_name": "Sam Roe",
    "adoptee_name_after_adoption": "Sam Doe",
    "adoptee_place_of_birth": "Portland, Maine",
    "adoptee_tribe": "Sample Tribal Nation (fictional)",
    # ── FDP-002A (infer_fdp002a_mortgage) — money parsed with float() ──
    "original_loan_amount": "200,000.00",
    "original_amortization_term": "360",
    "original_interest_rate": "4.50",
    "current_unpaid_balance": "180,000.00",
    "current_interest_rate": "4.50",
    "months_past_due": "3",
    "remaining_mortgage_term": "300",
    "current_mortgage_payment": "1,200.00",
    "current_interest_payment": "700.00",
    "current_principal_payment": "300.00",
    "past_due_interest": "2,100.00",
    "advances_escrow_past_due": "600.00",
    "future_interest_advanced_escrow": "2,700.00",  # = 2,100 + 600
    "property_taxes_monthly": "250.00",
    "property_insurance_monthly": "100.00",
    "pmi_monthly": "50.00",
    "current_escrow_payments": "400.00",
    "current_fmv": "210,000.00",
    "fdp_investor": "Acme Example Investment Trust",
    "fdp_preparer_name": "Jane Q. Doe",
    "fdp_preparer_title": "Account Manager",
    "fdp_preparer_firm": "Acme Example Loan Servicing",
    "fdp_preparer_phone": "207-555-0101",
    # ── FM-040-A (infer_fm040a_child_support) — int()/float() ──
    "children_count": "2",                          # matches child_1/child_2
    "higher_income_parent": "Jane Q. Doe",
    "higher_income_gross_weekly": "900.00",
    "lower_income_gross_weekly": "500.00",
    "additional_expenses": "75.00",
    # ── FM general (infer_fm_general) ──
    "fm_self_role": "petitioner",                   # petitioner|defendant
    "fm_paragraph3_choice": "A",
    "other_party_town": "Portland",
    "magistrate_objection": ("Sample objection text (fictional) for "
                             "testing this form's fill."),
    "magistrate_modify": ("Sample modification text (fictional) for "
                          "testing this form's fill."),
    "magistrate_request": ("Sample request text (fictional) for testing "
                           "this form's fill."),
    "fm071_acknowledgments": True,
    "fm071_order_date": "2024-03-01",
    "fm171_divorce_final_date": "2024-03-01",
    "fm171_plaintiff_name_after_divorce": "Jane Q. Sample",
    "fm171_defendant_name_after_divorce": "John R. Roe",
    "fm_action_type": "divorce",
    "fm_property_credits": ("Sample property description (fictional) for "
                            "testing this form's fill."),
    "fm_will_not_be_affected": ("Sample property description (fictional) "
                                "for testing this form's fill."),
    "fm_custody_court": "Sample District Court, Portland (fictional)",
    "fm214_emergency_order": True,
    "fm214_notice_given": True,
    "fm214_order_more_specifically": [
        "Sample order line 1 (fictional) for testing this form's fill.",
        "Sample order line 2 (fictional).",
    ],
    "fm214_relief": [
        "Sample relief request 1 (fictional) for testing this form's fill.",
        "Sample relief request 2 (fictional).",
    ],
    # ── GS family (infer_gs_family) ──
    "gs_section": "consent",            # consent|objection|nomination
    "gs_petition_type": "final_appointment",
    "gs_petition_kind": "final",        # interim|final
    "gs008_duration": "until_majority", # emergency|interim|until_majority
    "gs_reasons": [
        f"Sample guardianship reason {i} (fictional) for testing this "
        f"form's fill." for i in range(1, 4)
    ],
    "reason_for_guardianship": ("Sample guardianship reason 1 (fictional) "
                                "for testing this form's fill."),
    "gs_nominee_reason": ("Sample nominee reason (fictional) for testing "
                          "this form's fill."),
    "gs_minor_tribe": "Sample Tribal Nation (fictional)",
    "gs_minor_tribal_enrollment": "00000",
    # ── JV family (infer_jv_family) ──
    "juvenile_gender": "female",        # male|female|other
    "juvenile_gender_text": "female",
    "jv_signer_role": "parent",         # parent|guardian|legal_custodian
    "jv_state_attorney_name": "Casey L. Sample",
    "jv_state_attorney_bar": "ME-000000",
    "jv_custody_location": "Example Youth Center (fictional)",
    "jv_evaluation_program": "Example Evaluation Program (fictional)",
    "jv_hearing_date": "2024-04-15",
    "jv_appointment_date": "2024-04-01",
    "jv017_before_judge": True,
    "jv040_discharge_other_than_class_abc": True,
    "jv040_filer": "Riley T. Sample, JCCO (fictional)",
    "jv043_filing_attorney": "Pat L. Lawyer, Esq.",
    "jv043_attorney_address": "1 Court Plaza, Suite 100",
    "jv043_attorney_csz": "Portland, ME 04101",
    "jv043_attorney_phone": "207-555-0150",
    "jv043_attorney_email": "attorney@example.com",
    "jv044_attorney": "Pat L. Lawyer, Esq.",
    "jv044_attorney_bar": "ME-000000",
    "jv044_attorney_address": "1 Court Plaza, Suite 100",
    "jv044_attorney_city": "Portland",
    "jv044_attorney_zip": "04101",
    "jv044_attorney_phone": "207-555-0150",
    "jv044_attorney_email": "attorney@example.com",
    "jv044_seal_reasons": ("Sample sealing reasons (fictional) for "
                           "testing this form's fill."),
    "juvenile_doc_office": "Example Regional Office (fictional)",
    "notice_text": ("Sample notice text (fictional) for testing this "
                    "form's fill."),
    "community_service_org": "Acme Example Community Org",
    "community_service_supervisor": "Riley T. Sample",
    "community_service_address": "789 Pine Street",
    "community_service_address_2": "Portland, ME 04101",
    "community_service_phone": "207-555-0199",
    "community_service_supervisor_phone": "207-555-0198",
    "community_service_hours": "20",
    "community_service_hours_total": "20",
    "community_service_completion_date": "2024-06-30",
    # 5 date+hours rows, written verbatim into mm/dd/yyyy widgets.
    "community_service_log": [["04/01/2024", "4"], ["04/08/2024", "4"]],
    "community_service_rating": "satisfactory",
    "community_service_comments": [
        "Sample comment (fictional) for testing this form's fill."],
    # ── MJ debtor disclosure (infer_mj_debtor_disclosure) ──
    "judgment_creditor": "Jane Q. Doe",
    "judgment_debtor": "John R. Roe",
    "affiant_name": "John R. Roe",
    "service_date": "03/10/2024",       # written verbatim (mm/dd/yyyy)
    "event_date": "03/15/2024",         # written verbatim (mm/dd/yyyy)
    "mj_hold_narrative": ("Sample disclosure text (fictional) for testing "
                          "this form's fill."),
    "mj005_debts_narrative": ("Sample debts disclosure (fictional) for "
                              "testing this form's fill."),
    "mj005_property_narrative": ("Sample property disclosure (fictional) "
                                 "for testing this form's fill."),
    "mj_employment_narrative": ("Sample employment information (fictional) "
                                "for testing this form's fill."),
    "mj_principal": "850.00",
    "mj_interest": "15.00",
    "mj_costs": "50.00",
    # printed "for a total of $" sums (computations.json) — keep balanced
    # with the component amounts above so generated samples never carry a
    # COMPUTATION_MISMATCH out of the box.
    "mj_total": "915.00",
    "installment_order_date": "02/01/2024",  # written verbatim
    "mj009_installment_order_date": "2024-02-01",
    "mj009_failed_payment": True,
    "mj009_pay_amount": "100.00",
    "mj009_pay_period": "month",
    "mj009_owed_amount": "1,000.00",
    "mj009_interest": "10.00",
    "mj009_costs": "25.00",
    "mj009_total": "1,035.00",
    "underlying_criminal_docket": "CR-2024-00000",
    # ── MJ-SC judgment family (infer_mj_sc_judgment) ──
    "employer_name": "Acme Example Company",
    "employer_capacity": "office assistant",
    "gross_pay": "600.00",
    "net_pay": "480.00",
    "pay_period": "week",
    # Rows of [description, amount]; amounts summed with float().
    "payroll_deductions": [["Federal income tax", "60.00"],
                           ["State income tax", "20.00"]],
    # Rows of [creditor, total owing, period, per-payment].
    "other_debts": [["Acme Example Finance", "500.00", "month", "50.00"]],
    "dependents": "2",
    "spouse_income": "250.00",
    "spouse_source": "Acme Example Company",
    "living_expenses": "350.00",
    "installment_amount": "100.00",
    "installment_period": "month",
    "installment_start_date": "2024-04-01",
    "installment_payee": "the Clerk of the District Court, Portland location",
    "installment_agreement_acknowledged": True,
    "judgment_amount": "1,200.00",
    "judgment_costs": "60.00",
    "judgment_date": "2024-01-15",
    "balance_due": "1,200.00",
    "balance_acknowledgment": ("The parties acknowledge that the balance "
                               "due, as of this date, is $1,200.00."),
    "perjury_acknowledged": True,
    "entity_type": "corporation",       # corporation|llc|llp|lp|nonprofit
    "debtor_title": "President",
    # ── OTH-085 (infer_oth085_limited_appearance) ──
    "oth085_attorney_name": "Pat L. Lawyer, Esq.",
    "oth085_attorney_bar": "ME-000000",
    "oth085_attorney_address": "1 Court Plaza, Suite 100",
    "oth085_attorney_city": "Portland",
    "oth085_attorney_zip": "04101",
    "oth085_attorney_phone": "207-555-0150",
    "oth085_attorney_email": "attorney@example.com",
    "oth085_court_name": "District Court, Portland location",
    "oth085_represented_parties": "Jane Q. Doe (plaintiff)",
    "oth085_other_parties": "John R. Roe (defendant)",
    # ── OTH-133 (infer_oth133_mediator) ──
    "oth_requester_name": "Pat L. Lawyer, Esq.",
    "oth_requester_firm": "Example Law Office",
    "oth_requester_address": "1 Court Plaza, Suite 100",
    "oth_requester_city": "Portland",
    "oth_requester_zip": "04101",
    "oth_requester_phone": "207-555-0150",
    "oth_requester_email": "attorney@example.com",
    "oth_request_date": "2024-03-15",
    "oth_names_of_counsel": "Pat L. Lawyer, Esq. (counsel for plaintiff)",
    "oth_prior_mentor": "None in this fictional sample fact pattern.",
    "oth_issue_summary": SUMMARY,
    # ── PC family (infer_pc_family) ──
    "pc_hearing_type": "judicial_review",
    "pc_court_date": "04/15/2024",      # written verbatim (mm/dd/yyyy)
    # Rows of [name, DOB mm/dd/yyyy], written verbatim.
    "pc_children": [["Sam Doe", "04/10/2015"], ["Alex Doe", "09/05/2018"]],
    "pc_gal_name": "Lee J. Sample, Esq.",
    "pc_gal_bar": "ME-000000",
    "pc_gal_address": "1 Court Plaza, Suite 100, Portland, ME 04101",
    "pc_case_mgr_report": ("Sample case-manager report (fictional) for "
                           "testing this form's fill."),
    "pc_parent_conditions": "None in this fictional sample fact pattern.",
    "pc_foster_parents": ("Pat R. Sample and Lee A. Sample, "
                          "456 Oak Avenue, Portland, ME 04101"),
    "pc_placement_arranger": "Example Department Office (fictional)",
    "pc_default_location": "Maine District Court, Portland",
    "pc_tribe": "Sample Tribal Nation (fictional)",
    "pc_tribal_enrollment": "00000",
}


def synth_fact_value(key: str, checkbox_only: bool = False) -> str:
    """Deterministic clearly-fictional placeholder for a facts.* key."""
    k = key.lower()
    if checkbox_only:
        return "yes"
    if k == "summary":
        return SUMMARY
    if "spent" in k or "duration" in k:
        return "2 hours"
    if "date" in k or k.endswith("_dob"):
        return "2024-03-15"
    if "time" in k:
        return "9:00 AM"
    if "phone" in k or "telephone" in k:
        return "207-555-0199"
    if "email" in k:
        return "sample@example.com"
    if "address" in k:
        return "789 Pine Street, Portland, ME 04101"
    if "county" in k:
        return "Cumberland"
    if "city" in k or "town" in k:
        return "Portland"
    if k.endswith("state"):
        return "ME"
    if "zip" in k:
        return "04101"
    if ("amount" in k or "fee" in k or "total" in k or "wage" in k
            or "income" in k or "balance" in k or "principal" in k
            or "interest" in k or "payment" in k or "value" in k
            or k.endswith("_sum")):
        return "100.00"
    if "age" in k and "page" not in k:
        return "10"
    if ("employer" in k or "company" in k or "business" in k
            or "organization" in k) and "name" in k:
        return "Acme Example Company"
    if "docket" in k or "number" in k or k.endswith("_no"):
        return "2024-00000"
    if "name" in k:
        return "Riley T. Doe"
    if ("description" in k or "explanation" in k or "details" in k
            or "reason" in k or "grounds" in k or "statement" in k
            or "summary" in k or "other" in k or "issue" in k):
        return "Fictional sample text for testing this form's fill."
    return "Sample (fictional)."


def _checkbox_only_keys(fdir: pathlib.Path, mapping: dict) -> set[str]:
    """facts.* keys whose every mapped widget is a checkbox -> fill 'yes'."""
    try:
        schema = json.loads((fdir / "schema.json").read_text())
    except Exception:  # noqa: BLE001
        return set()
    type_by_fid: dict[str, set[str]] = {}
    for f in schema.get("fields", []):
        type_by_fid.setdefault(f.get("field_id"), set()).add(
            (f.get("type") or "").lower())
    key_types: dict[str, set[str]] = {}
    for fid, key in (mapping.get("map") or {}).items():
        key_types.setdefault(key, set()).update(
            type_by_fid.get(fid, {"?"}))
    return {k for k, ts in key_types.items() if ts == {"checkbox"}}


def _recipe_run(form_id: str, case: dict) -> dict:
    """Run a form's registered recipe over a case (PDF-free), as the recipe
    smoke test does: canonical->engine translation + map_form +
    recipe.process (the recipes read the ENGINE case shape: court/docket_no
    top-level — running them on the raw canonical object understates what
    a real fill produces)."""
    import importlib

    from engine.build_kv_map import map_form
    from engine.canonical import is_canonical, to_engine_case
    from engine.fill_and_audit import RECIPE3
    schema = json.loads(
        (OSS_ROOT / "forms" / form_id / "schema.json").read_text())
    ec = to_engine_case(case) if is_canonical(case) else case
    kv, _ = map_form(schema, ec)
    mod = importlib.import_module(f"engine.recipes.{RECIPE3[form_id]}")
    out, _changes = mod.process(kv, ec)
    return out


def _recipe_accepts(form_id: str, base: dict,
                    enriched: dict) -> tuple[bool, str]:
    """(accepted, reason-if-not). The enriched sample must run the recipe
    and extend the base sample's coverage: every widget the recipe filled
    from the base stays filled (a value may legitimately change when an
    explicit fact takes precedence over a party-derived or stock fallback)
    and the facts must demonstrably drive the fill — more widgets filled,
    or a widget now carrying a fact-supplied value. Crashes — a synthesized
    value violating the recipe's typed fact format — reject the
    enrichment; the rejection reason is recorded on the generic sample as
    "generic_reason" so honesty over coverage stays auditable."""
    try:
        base_out = _recipe_run(form_id, base)
        new_out = _recipe_run(form_id, enriched)
    except Exception as e:  # noqa: BLE001 — synthesized value broke recipe
        return False, (f"recipe rejected the synthesized facts "
                       f"({type(e).__name__}) — typed fact format mismatch")
    base_filled = {k for k, v in base_out.items() if v}
    new_filled = {k for k, v in new_out.items() if v}
    if not base_filled <= new_filled:
        return False, ("enriching with this form's fact keys loses fills "
                       "the generic sample produced")
    if new_out == base_out:
        return False, ("the recipe reads no facts that reach this form's "
                       "widgets (it fills from case/party data only), so "
                       "a fact-enriched sample changes nothing")
    return True, ""


def build_sample(fdir: pathlib.Path, base: dict) -> tuple[dict, str]:
    """Return (sample_case, kind) — kind in generated-mapping /
    generated-recipe / generic."""
    mapping = json.loads((fdir / "mapping.json").read_text())
    status = mapping.get("status")
    facts_block = mapping.get("facts") or {}
    used = facts_block.get("used") or []
    checkbox_only = _checkbox_only_keys(fdir, mapping)

    if not used:  # no-mappable-fields or nothing derivable
        case = copy.deepcopy(base)
        case["generic"] = True
        return case, "generic"

    if status == "recipe":
        # Recipes run on top of the generic engine field map, which consumes
        # the standard base; enrich it with the recipe's own fact keys.
        case = copy.deepcopy(base)
        for key in used:
            if key.startswith("facts."):
                fk = key.split(".", 1)[1]
                if fk in TYPED_FACT_VALUES:
                    val = copy.deepcopy(TYPED_FACT_VALUES[fk])
                else:
                    val = synth_fact_value(fk, fk in checkbox_only)
                case.setdefault("facts", {}).setdefault(fk, val)
        case["facts"]["summary"] = SUMMARY
        accepted, why = _recipe_accepts(fdir.name, base, case)
        if not accepted:
            case = copy.deepcopy(base)
            case["generic"] = True
            case["generic_reason"] = why
            return case, "generic"
        return case, "generated-recipe"

    # Mapping-tier: carry exactly the keys this form's mapping resolves.
    case: dict = {"matter": {}}
    base_matter = base.get("matter") or {}
    for key in used:
        parts = key.split(".")
        if parts[0] == "matter" and len(parts) == 2:
            case["matter"][parts[1]] = base_matter.get(
                parts[1], synth_fact_value(parts[1]))
        elif parts[0] == "party" and len(parts) == 2:
            case.setdefault("party", {})[parts[1]] = (
                base.get("party") or {}).get(parts[1],
                                             synth_fact_value(parts[1]))
        elif parts[0] == "parties" and len(parts) == 3:
            role, attr = parts[1], parts[2]
            roster = _party_for_role(base, role)
            case.setdefault("parties", {}).setdefault(role, {})[attr] = \
                roster.get(attr, synth_fact_value(attr))
        elif parts[0] == "facts" and len(parts) == 2:
            fk = parts[1]
            case.setdefault("facts", {})[fk] = synth_fact_value(
                fk, key in checkbox_only)
    case.setdefault("facts", {})["summary"] = SUMMARY
    return case, "generated-mapping"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--forms", default="", help="comma list; omit for all")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true",
                    help="also overwrite hand-built (non-generic) samples")
    args = ap.parse_args()
    base = json.loads(BASE_PATH.read_text())
    if args.forms:
        dirs = [OSS_ROOT / "forms" / f.strip()
                for f in args.forms.split(",") if f.strip()]
    else:
        dirs = sorted(p for p in (OSS_ROOT / "forms").iterdir() if p.is_dir())
    counts: dict[str, int] = {}
    failures = []
    for fdir in dirs:
        sp = fdir / "examples" / "sample_case.json"
        if not (fdir / "mapping.json").exists():
            continue
        if sp.exists() and not args.force:
            current = json.loads(sp.read_text())
            cur_nogen = {k: v for k, v in current.items()
                         if k not in ("generic", "generic_reason")}
            if cur_nogen != base:
                counts["kept-hand-built"] = counts.get("kept-hand-built", 0) + 1
                continue
        sample, kind = build_sample(fdir, base)
        pre = preflight_case(sample)
        if not pre["ok"] or pre["warnings"]:
            failures.append((fdir.name, pre["errors"] + pre["warnings"]))
            continue
        counts[kind] = counts.get(kind, 0) + 1
        if args.dry_run:
            continue
        sp.parent.mkdir(exist_ok=True)
        sp.write_text(json.dumps(sample, indent=2) + "\n")
    print(json.dumps(counts))
    if failures:
        for name, issues in failures:
            print(f"PREFLIGHT FAIL {name}: {issues}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
