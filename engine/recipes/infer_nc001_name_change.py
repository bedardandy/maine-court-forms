"""NC-001 (Petition for Name Change of Minor) recipe-3 inference.

42-widget form covering petitioner+copetitioner identity blocks,
4-checkbox document set (item 7), minor identity (items 8-10),
new-name + reasons narrative (items 11-12), and dual signature
+ contact info blocks.

Reads case.parties.petitioner (+ copetitioner) and case.parties.minor,
plus case.facts.new_name_for_minor / name_change_reason /
documents_provided.
"""
from __future__ import annotations

import sys


def _set(answers: dict, fid: str, value: str) -> bool:
    if fid not in answers: return False
    if answers.get(fid): return False
    answers[fid] = value
    return True


def _iso_to_us(iso_date: str) -> str:
    if not iso_date or "-" not in iso_date: return iso_date
    y, m, d = iso_date[:10].split("-")
    return f"{m}/{d}/{y}"


def _split_addr_phone(addr: str, phone: str) -> tuple[str, str]:
    """Two-line representation of address+phone."""
    if not addr: return ("", phone or "")
    line1 = addr
    line2 = f"Phone: {phone}" if phone else ""
    return (line1, line2)


def process(kv_map: dict, case: dict) -> tuple[dict, list]:
    out = dict(kv_map)
    changes = []
    parties = case.get("parties") or {}
    court = case.get("court") or {}
    facts = case.get("facts") or {}

    petitioner = parties.get("petitioner") or parties.get("plaintiff") or {}
    copetitioner = (parties.get("copetitioner")
                     or parties.get("co_petitioner") or {})
    minor = (parties.get("minor") or parties.get("juvenile")
             or parties.get("adoptee") or parties.get("child_1") or {})
    attorney = parties.get("attorney") or {}

    # Header
    if _set(out, "location", court.get("location", "")):
        changes.append(("location", court.get("location",""), "location"))
    if _set(out, "docket_no_2", case.get("docket_no", "")):
        changes.append(("docket_no_2", case.get("docket_no",""), "docket"))
    if _set(out, "in_re", minor.get("full_name", "")):
        changes.append(("in_re", minor.get("full_name",""), "in-re"))

    # Item 1: petitioner name
    if _set(out, "1_name_of_petitioner", petitioner.get("full_name", "")):
        changes.append(("1_name_of_petitioner",
                        petitioner.get("full_name",""), "item1"))

    # Item 2: petitioner address + phone (two-line widget)
    pl1, pl2 = _split_addr_phone(petitioner.get("address",""),
                                   petitioner.get("phone",""))
    if _set(out, "2_address_and_telephone_number_of_petitioner_inc", pl1):
        changes.append(("2_address_and_telephone_number_of_petitioner_inc",
                        pl1, "item2-line1"))

    # Item 3: petitioner relationship to minor — fill ONLY when explicitly
    # provided. Never default a relationship (was "grandmother"):
    # fabricating the petitioner's relationship to the child is a material
    # misstatement, and is plainly wrong when the petitioner is the parent.
    rel1 = (petitioner.get("relationship")
             or facts.get("petitioner_relationship_to_minor", ""))
    if rel1 and _set(out, "3_relationship_of_petitioner_to_minor_child", rel1):
        changes.append(("3_relationship_of_petitioner_to_minor_child",
                        rel1, "item3"))

    # Item 4: copetitioner name (optional)
    if _set(out, "4_name_of_copetitioner",
            copetitioner.get("full_name", "")):
        changes.append(("4_name_of_copetitioner",
                        copetitioner.get("full_name",""), "item4"))

    # Item 5: copetitioner address+phone (two-line widget)
    cpl1, _ = _split_addr_phone(copetitioner.get("address",""),
                                  copetitioner.get("phone",""))
    if _set(out, "5_address_and_telephone_number_of_petitioner_inc", cpl1):
        changes.append(("5_address_and_telephone_number_of_petitioner_inc",
                        cpl1, "item5-line1"))

    # Item 6: copetitioner relationship to minor — fill ONLY when explicitly
    # provided (was defaulted to "grandfather"). When there is no
    # copetitioner this stays blank instead of inventing one.
    rel2 = (copetitioner.get("relationship")
             or facts.get("copetitioner_relationship_to_minor", ""))
    if rel2 and _set(out, "6_relationship_of_copetitioner_to_minor_child", rel2):
        changes.append(("6_relationship_of_copetitioner_to_minor_child",
                        rel2, "item6"))

    # Item 7: documents provided — check ONLY the boxes explicitly listed
    # in case.facts.nc_documents_checked. Never default-check the birth
    # certificate box: asserting a document was filed when it wasn't is a
    # false statement to the court.
    docs_checked = facts.get("nc_documents_checked", [])
    if isinstance(docs_checked, str):
        docs_checked = [docs_checked]
    for fid in ("birth_certificate_of_minor",
                 "divorce_judgment_if_any_including_any_modificati",
                 "court_order_pertaining_to_custody_of_the_child_i",
                 "death_certificate_of_deceased_custodian_if_any"):
        if fid in docs_checked and _set(out, fid, "X"):
            changes.append((fid, "X", "doc-checked"))

    # Item 8: minor's full legal name (schema field_id is truncated)
    if _set(out, "8_full_legal_name_of_minor_include_middle_name_i",
            minor.get("full_name", "")):
        changes.append(("8_full_legal_name_of_minor_include_middle_name_i",
                        minor.get("full_name",""), "item8"))

    # Item 9: date of birth
    if minor.get("dob"):
        dob_us = _iso_to_us(minor["dob"])
        if _set(out, "9_date_of_birth_of_minor", dob_us):
            changes.append(("9_date_of_birth_of_minor", dob_us, "item9"))

    # Item 10: minor's current address — actual field_ids are
    # `10_the_minor_currently_resides_at_the_following_address_1` (and _2).
    if minor.get("address"):
        if _set(out, "10_the_minor_currently_resides_at_the_following_address_1",
                minor["address"]):
            changes.append((
                "10_the_minor_currently_resides_at_the_following_address_1",
                minor["address"], "item10"))

    # Item 11: new name — fill ONLY when explicitly provided in
    # case.facts.new_name_for_minor. Do NOT synthesize a requested name
    # from the petitioner's surname: the new legal name is the entire
    # purpose of the petition, and guessing it risks filing the wrong name.
    new_name = facts.get("new_name_for_minor", "")
    if new_name:
        if _set(out,
                "11_petitioner_wishes_to_change_the_minors_name_to_include_middle_name_if_any",
                new_name):
            changes.append((
                "11_petitioner_wishes_to_change_the_minors_name_to_include_middle_name_if_any",
                new_name, "item11"))

    # Item 12: reasons — 5 numbered fields. Put the full reason in _1,
    # leave _2.._5 blank (audit accepts trailing blank list rows). Fill
    # ONLY when provided; never fabricate a rationale (was a hardcoded
    # "match the custodial parent's surname" reason).
    reason = facts.get("name_change_reason", "")
    if reason and _set(out,
            "12_petitioner_wishes_to_change_the_minors_name_for_the_following_reasons_1",
            reason):
        changes.append((
            "12_petitioner_wishes_to_change_the_minors_name_for_the_following_reasons_1",
            reason, "item12"))

    # ── Page-2 signature + contact blocks ──
    # Two physical columns (confirmed by widget rect + printed labels):
    #   RIGHT (x~343): "Signature of Petitioner" + "Signature of Co-Petitioner"
    #                  above a single petitioner contact block
    #                  (name_2 / 1_2 / 2_2 / phone_number_2 / email_2).
    #   LEFT  (x~55):  "Attorney for Petitioner(s), if any" — attorney
    #                  signature + contact block (name / 1 / 2 /
    #                  phone_number / email).
    # build_kv_map's narrative pass stamps the LEFT (attorney) block with the
    # petitioner's data and the RIGHT block with the co-petitioner/defendant,
    # i.e. a petitioner↔attorney swap. Force by true column.
    def _force(fid: str, val: str, src: str) -> None:
        if fid in out and out.get(fid, "") != val:
            out[fid] = val
            changes.append((fid, val, src))

    sig_date = (case.get("filing_date")
                or case.get("event_date") or "")
    sig_date_us = _iso_to_us(sig_date)
    if _set(out, "dated", sig_date_us):
        changes.append(("dated", sig_date_us, "dated"))
    if copetitioner.get("full_name") and _set(out, "dated_2", sig_date_us):
        changes.append(("dated_2", sig_date_us, "dated2"))

    # Signatures (signature widgets are wet-ink; we type the printed name).
    _force("signature_electronic_or_actual", petitioner.get("full_name", ""),
           "sig-petitioner")
    if copetitioner.get("full_name"):
        _force("signature_electronic_or_actual_1",
               copetitioner.get("full_name", ""), "sig-copetitioner")

    # RIGHT column — petitioner contact block.
    _force("name_2", petitioner.get("full_name", ""), "petitioner-name")
    _force("1_2", petitioner.get("address", ""), "petitioner-addr")
    _force("phone_number_2", petitioner.get("phone", ""), "petitioner-phone")
    _force("email_2", petitioner.get("email", ""), "petitioner-email")

    # LEFT column — "Attorney for Petitioner(s)". Fill with the attorney if
    # one is on the case, else clear the build_kv_map petitioner pollution
    # (the block is explicitly optional: "if any").
    if attorney.get("full_name"):
        _force("signature_electronic_or_actual_2", attorney["full_name"],
               "sig-attorney")
        _force("name", attorney["full_name"], "attorney-name")
        _force("1", attorney.get("address", ""), "attorney-addr")
        _force("phone_number", attorney.get("phone", ""), "attorney-phone")
        _force("email", attorney.get("email", ""), "attorney-email")
    else:
        for fid in ("signature_electronic_or_actual_2", "name", "1",
                     "phone_number", "email"):
            if out.get(fid):
                out[fid] = ""
                changes.append((fid, "", "attorney-col-clear"))

    # Notary jurat: "Personally appeared the above named, ___ and ___" — the
    # `petitioner`/`co_petitioner` widgets are the printed-name blanks on that
    # line, NOT checkboxes. Fill with the signer name(s).
    _force("petitioner", petitioner.get("full_name", ""), "jurat-petitioner")
    if copetitioner.get("full_name"):
        _force("co_petitioner", copetitioner.get("full_name", ""),
               "jurat-copetitioner")

    return out, changes


if __name__ == "__main__":
    print("Use via fill_and_audit.py RECIPE3 dispatch")
    sys.exit(0)
