"""FM-056 (Certificate of Real Estate — Family Matter) recipe-3
inference.

Used in divorce/separation cases to identify real-estate interests
of either party. The form repeats the property block twice (for two
separate properties) and has page-2 acquisition-method radios and
attorney signature block.

Reads case.parties.plaintiff/defendant + case.facts.fm_property_*.
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
    court = case.get("court") or {}

    plaintiff = (parties.get("plaintiff") or parties.get("petitioner") or {})
    defendant = (parties.get("defendant") or parties.get("respondent") or {})
    attorney = parties.get("attorney") or {}

    # Caption
    if _set(out, "plaintiff", plaintiff.get("full_name", "")):
        changes.append(("plaintiff", plaintiff.get("full_name",""), "pl"))
    if _set(out, "defendant", defendant.get("full_name", "")):
        changes.append(("defendant", defendant.get("full_name",""), "df"))
    if _set(out, "location_town", court.get("location", "")):
        changes.append(("location_town", court.get("location",""), "loc"))
    if _set(out, "docket_no", case.get("docket_no", "")):
        changes.append(("docket_no", case.get("docket_no",""), "dock"))

    # Property block 1 — every value here describes a recorded interest in
    # real estate. Fill ONLY from explicit fm_property1_* / fm_marriage_date
    # facts. The old defaults invented a property description, address,
    # deed date, registry, book/page numbers, and a marriage date — all
    # material misstatements on a certificate filed with the court.
    desc1 = facts.get("fm_property1_description", "")

    # Property address ONLY from the explicit fact — a party's home
    # address is not necessarily the property at issue.
    addr1 = facts.get("fm_property1_address", "")
    deed1_date = facts.get("fm_property1_deed_date", "")
    registry1 = facts.get("fm_property1_registry", "")
    book1 = facts.get("fm_property1_book", "")
    page1 = facts.get("fm_property1_page", "")
    marriage_date = facts.get("fm_marriage_date", "")

    if desc1 and _set(out,
            "one_or_both_parties_have_an_interest_in_the_following_real_estate",
            desc1):
        changes.append((
            "one_or_both_parties_have_an_interest_in_the_following_real_estate",
            desc1, "p1-desc"))

    # Street address split (2 lines)
    parts = [p.strip() for p in addr1.split(",")] if addr1 else []
    line1 = parts[0] if parts else ""
    line2 = ", ".join(parts[1:])
    if _set(out, "street_address_do_not_use_mailing_address_if_different_1",
            line1):
        changes.append((
            "street_address_do_not_use_mailing_address_if_different_1",
            line1, "p1-addr1"))
    if _set(out, "street_address_do_not_use_mailing_address_if_different_2",
            line2):
        changes.append((
            "street_address_do_not_use_mailing_address_if_different_2",
            line2, "p1-addr2"))

    if deed1_date and _set(out, "the_deed_is_dated_mmddyyyy", deed1_date):
        changes.append(("the_deed_is_dated_mmddyyyy", deed1_date, "p1-deed"))
    if registry1 and _set(out, "and_recorded_in_the", registry1):
        changes.append(("and_recorded_in_the", registry1, "p1-reg"))
    if book1 and _set(out, "registry_of_deeds_in_book", book1):
        changes.append(("registry_of_deeds_in_book", book1, "p1-book"))
    if page1 and _set(out, "page", page1):
        changes.append(("page", page1, "p1-page"))

    # Date of marriage — ONLY when explicitly provided
    if marriage_date and _set(out, "date_of_marriage_mmddyyyy",
                                marriage_date):
        changes.append(("date_of_marriage_mmddyyyy", marriage_date, "marr1"))

    # Acquired-by-gift radio — answer ONLY when explicitly provided (was
    # defaulted to "No", asserting how the property was acquired).
    gift1 = facts.get("fm_property1_by_gift", "")
    if gift1 and _set(out, "was_the_property_acquired_by_gift_or_inheritance",
            gift1.title()):
        changes.append(("was_the_property_acquired_by_gift_or_inheritance",
                        gift1.title(), "p1-gift"))

    # Property block 2 (use defaults indicating no second property by
    # default — fill only if case has explicit facts)
    desc2 = facts.get("fm_property2_description", "")
    if desc2:
        if _set(out,
                "one_or_both_parties_have_an_interest_in_the_following_real_estate_2",
                desc2):
            changes.append((
                "one_or_both_parties_have_an_interest_in_the_following_real_estate_2",
                desc2, "p2-desc"))
        addr2 = facts.get("fm_property2_address", "")
        parts2 = [p.strip() for p in addr2.split(",")] if addr2 else []
        if parts2:
            if _set(out,
                    "street_address_do_not_use_mailing_address_if_different_1_2",
                    parts2[0]):
                changes.append((
                    "street_address_do_not_use_mailing_address_if_different_1_2",
                    parts2[0], "p2-addr1"))
            if _set(out,
                    "street_address_do_not_use_mailing_address_if_different_2_2",
                    ", ".join(parts2[1:])):
                changes.append((
                    "street_address_do_not_use_mailing_address_if_different_2_2",
                    ", ".join(parts2[1:]), "p2-addr2"))
        deed2_date = facts.get("fm_property2_deed_date", "")
        if deed2_date:
            if _set(out, "the_deed_is_dated_mmddyyyy_2", deed2_date):
                changes.append(("the_deed_is_dated_mmddyyyy_2",
                                deed2_date, "p2-deed"))
        registry2 = facts.get("fm_property2_registry", "")
        if registry2:
            if _set(out, "and_recorded_in_the_2", registry2):
                changes.append(("and_recorded_in_the_2", registry2,
                                "p2-reg"))
        book2 = facts.get("fm_property2_book", "")
        page2 = facts.get("fm_property2_page", "")
        if book2 and _set(out, "registry_of_deeds_in_book_2", book2):
            changes.append(("registry_of_deeds_in_book_2", book2, "p2-book"))
        if page2 and _set(out, "page_2", page2):
            changes.append(("page_2", page2, "p2-page"))
        if _set(out, "plaintiff_2", plaintiff.get("full_name","")):
            changes.append(("plaintiff_2", plaintiff.get("full_name",""),
                            "p2-pl"))
        if _set(out, "defendant_2", defendant.get("full_name","")):
            changes.append(("defendant_2", defendant.get("full_name",""),
                            "p2-df"))
        if marriage_date and _set(out, "date_of_marriage_mmddyyyy_2",
                                    marriage_date):
            changes.append(("date_of_marriage_mmddyyyy_2",
                            marriage_date, "p2-marr"))

    # "Additional certificate attached" checkbox (default unchecked)
    additional = facts.get("fm_additional_real_estate", "no")
    if additional.lower() in ("yes", "y", "true", "1"):
        if _set(out,
                "one_or_both_parties_have_an_interest_in_additional_real_estate_and_have_attached_another_certificate",
                "X"):
            changes.append((
                "one_or_both_parties_have_an_interest_in_additional_real_estate_and_have_attached_another_certificate",
                "X", "addl"))

    # Signature date
    sig_date = (case.get("filing_date") or case.get("event_date") or "")
    if _set(out, "date_mmddyyyy", _iso_to_us(sig_date)):
        changes.append(("date_mmddyyyy", _iso_to_us(sig_date), "sig-date"))

    # Attorney info — falls back to plaintiff (pro-se) when no attorney
    signer_name = (attorney.get("full_name")
                    or plaintiff.get("full_name", ""))
    if signer_name and _set(out, "print_name", signer_name):
        changes.append(("print_name", signer_name, "att-name"))
    if attorney.get("bar_number"):
        if _set(out, "bar_number", attorney["bar_number"]):
            changes.append(("bar_number", attorney["bar_number"], "att-bar"))

    # "Attorney for" — ONLY when explicitly provided (was defaulted to
    # "plaintiff", asserting who counsel represents even in pro-se fills).
    atty_for = facts.get("fm_attorney_for", "")
    if atty_for:
        if _set(out, "attorney_for", atty_for.title()):
            changes.append(("attorney_for", atty_for.title(), "att-for"))
        # Plaintiff/defendant_3 checkboxes for who the attorney represents
        if atty_for.lower() == "plaintiff":
            if _set(out, "plaintiff_3", "X"):
                changes.append(("plaintiff_3", "X", "pl3"))
        else:
            if _set(out, "defendant_3", "X"):
                changes.append(("defendant_3", "X", "df3"))

    # Signature widget
    if attorney.get("full_name") and _set(
            out, "undefined", attorney["full_name"]):
        changes.append(("undefined", attorney["full_name"], "sig"))

    return out, changes


if __name__ == "__main__":
    print("Use via fill_and_audit.py RECIPE3 dispatch")
    sys.exit(0)
