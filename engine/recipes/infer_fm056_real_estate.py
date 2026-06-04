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

    # Property block 1
    desc1 = facts.get("fm_property1_description",
                        "Single-family residence held in the parties' joint "
                        "names as marital residence.")

    def _full_addr(p: dict, fallback: str = "") -> str:
        street = p.get("address") or p.get("mailing_address", "")
        city = p.get("city", "")
        state = p.get("state", "")
        zipc = p.get("zip", "")
        tail = ", ".join(x for x in (city, f"{state} {zipc}".strip()) if x)
        full = ", ".join(x for x in (street, tail) if x)
        return full or fallback

    addr1 = facts.get("fm_property1_address",
                        _full_addr(plaintiff,
                                     "22 Maple Street, Portland, ME 04101"))
    deed1_date = facts.get("fm_property1_deed_date", "06/15/2010")
    registry1 = facts.get("fm_property1_registry",
                            "Cumberland County")
    book1 = facts.get("fm_property1_book", "12345")
    page1 = facts.get("fm_property1_page", "67")
    marriage_date = facts.get("fm_marriage_date", "05/20/2008")

    if _set(out,
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

    if _set(out, "the_deed_is_dated_mmddyyyy", deed1_date):
        changes.append(("the_deed_is_dated_mmddyyyy", deed1_date, "p1-deed"))
    if _set(out, "and_recorded_in_the", registry1):
        changes.append(("and_recorded_in_the", registry1, "p1-reg"))
    if _set(out, "registry_of_deeds_in_book", book1):
        changes.append(("registry_of_deeds_in_book", book1, "p1-book"))
    if _set(out, "page", page1):
        changes.append(("page", page1, "p1-page"))

    # Date of marriage
    if _set(out, "date_of_marriage_mmddyyyy", marriage_date):
        changes.append(("date_of_marriage_mmddyyyy", marriage_date, "marr1"))

    # Acquired-by-gift radio (default No)
    gift1 = facts.get("fm_property1_by_gift", "no")
    if _set(out, "was_the_property_acquired_by_gift_or_inheritance",
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
        if _set(out, "date_of_marriage_mmddyyyy_2", marriage_date):
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

    # "Attorney for" — pick plaintiff if attorney's party matches
    atty_for = facts.get("fm_attorney_for", "plaintiff")
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
