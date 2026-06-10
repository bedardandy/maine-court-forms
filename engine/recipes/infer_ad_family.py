"""AD family (Adoption) recipe-3 inference.

Three distinct fact patterns share the AD- prefix:
  AD-006: Consent to Adoption (parent's signed consent)
  AD-022: Petition for Disclosure of Adoption Records
  AD-030: Joint Petition for Adoption

Each has different widget layout — this script dispatches on schema
field_id shape (key presence sniffing).
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


def _process_ad006(out: dict, case: dict, changes: list) -> None:
    """AD-006: parent's consent to adoption."""
    facts = case.get("facts") or {}
    parties = case.get("parties") or {}
    court = case.get("court") or {}
    # Consenting party may be on "consenting_parent" (preferred), "parent",
    # or fall back to petitioner/plaintiff for legacy synthetic cases.
    parent = (parties.get("consenting_parent")
              or parties.get("parent") or parties.get("petitioner")
              or parties.get("plaintiff") or {})
    # Adopting parent(s): petitioner is the would-be adoptive parent in a
    # stepparent / kinship adoption. Co-petitioner (if any) is the spouse.
    adoptive = parties.get("petitioner") or parties.get("plaintiff") or {}
    coadoptive = (parties.get("copetitioner")
                   or parties.get("co_petitioner")
                   or parties.get("spouse") or {})
    adoptee = (parties.get("adoptee") or parties.get("minor")
                or parties.get("child") or {})
    # `name_and` widget (p1 y=62, ~200px) is a single short blank
    # following "adoption ... by ___". The "and (name)" of the legal
    # text is either pre-printed or non-fillable, so only ONE name fits.
    # Use the lead adopting parent only — co-petitioner spouse is named
    # separately on AD-030, not here.
    if adoptive.get("full_name"):
        adopting_pair = adoptive["full_name"]
    elif coadoptive.get("full_name"):
        adopting_pair = coadoptive["full_name"]
    else:
        adopting_pair = facts.get("ad_prospective_adoptive_parent",
                                    "the prospective adoptive parent")
    sig_date_us = _iso_to_us(case.get("filing_date", ""))
    fills = [
        ("location", court.get("location", "")),
        ("docket_no_2", case.get("docket_no", "")),
        ("name_of_adoptee", adoptee.get("full_name", "")),
        ("i", parent.get("full_name", "")),
        ("state_in_which_consent_is_executed", "Maine"),
        ("i_have_followed_the_procedure_required_to_make_a_consent_valid_in",
         "Maine"),
        ("under_the_laws_of", "Maine"),
        ("state_of", "Maine"),
        # County from real court data only (was defaulted "Cumberland")
        ("county", court.get("county", "")),
        ("name_and", adopting_pair),
        ("dated", sig_date_us),
        ("dated_2", sig_date_us),
        # `text1` is the dated-on signature widget pair to "dated" (date and
        # signer name side-by-side at p1 y=98). Hold the signer name.
        ("text1", parent.get("full_name", "")),
        ("personally_appeared_the_abovenamed_consenting_parent",
         parent.get("full_name", "")),
        ("party_authorized_to_take_consent",
         facts.get("ad_consent_taker",
                    "Hon. Margaret L. Whitford, Probate Judge")),
    ]
    # Check-box affirmations (all checked by a consenting parent)
    affirmations = [
        "i_want_the_adoption_decree_to_allow_my_child_to_inherit_from_me_18c_mrs_93086a",
        "i_have_followed_the_procedure_required_to_make_a_consent_valid_in",
        "the_court_has_explained_my_parental_rights_and_responsibilities_and_the_consequences_of_this_consent",
        "i_have_been_provided_information_about_the_existence_of_the_state_of_maine_adoption_registry_and_the",
        "the_court_determines_that_this_consent_has_been_duly_executed_and_was_given_freely_after_i_was",
        "the_court_determines_that_this_consent_is_in_the_childs_best_interest",
        "in_accordance_with_18c_mrs_93021b_i_hereby_consent_to_the_adoption_of_the_abovenamed_adoptee_by",
    ]
    for fid, val in fills:
        if val and _set(out, fid, val):
            changes.append((fid, val, f"006-{fid[:20]}"))
    for fid in affirmations:
        if _set(out, fid, "X"):
            changes.append((fid, "X", f"006-aff"))


def _process_ad022(out: dict, case: dict, changes: list) -> None:
    """AD-022: petition for disclosure of adoption records."""
    facts = case.get("facts") or {}
    parties = case.get("parties") or {}
    court = case.get("court") or {}
    petitioner = (parties.get("petitioner") or parties.get("plaintiff")
                   or {})
    adoptee = (parties.get("adoptee") or parties.get("minor")
                or parties.get("child") or {})
    attorney = parties.get("attorney") or {}

    # Petitioner identity (split first/middle/last)
    pl_name = petitioner.get("full_name", "")
    parts = pl_name.split() if pl_name else []
    first = parts[0] if parts else ""
    middle = parts[1] if len(parts) >= 3 else ""
    last = parts[-1] if parts else ""

    # Prefer structured party fields over splitting the raw `address`
    # string, which on synthetic cases is often a bare street only.
    addr = petitioner.get("address", "")
    addr_parts = [p.strip() for p in addr.split(",")] if addr else []
    addr_main = (addr_parts[0] if addr_parts else "") or addr
    addr_city = petitioner.get("city",
                                  addr_parts[1] if len(addr_parts) > 1 else "")
    addr_zip = petitioner.get("zip", "")
    if not addr_zip and len(addr_parts) > 2:
        tokens = addr_parts[2].split()
        addr_zip = tokens[-1] if tokens else ""

    fills = [
        ("district_court", court.get("name", "Maine District Court")),
        ("docket_no_2", case.get("docket_no", "")),
        ("in_the_matter_of_the_adoption_petition_of",
         adoptee.get("full_name", "")),
        ("first", first),
        ("middle", middle),
        ("last", last),
        ("date_of_birth", _iso_to_us(petitioner.get("dob", ""))),
        ("legal_residence", addr_main),
        ("city_town", addr_city),
        ("zip", addr_zip),
        ("mailing_address", addr_main),
        ("city_town_1", addr_city),
        ("zip_1", addr_zip),
        ("relationship", petitioner.get("relationship",
                                          "biological parent")),
    ]
    for fid, val in fills:
        if val and _set(out, fid, val):
            changes.append((fid, val, f"022-{fid[:20]}"))

    # Disclosure-type checkboxes (default: certificate + medical info)
    disclosure_types = facts.get("ad_disclosure_types",
                                    ["to_obtain_a_certificate_of_adoption",
                                     "to_obtain_medical_andor_genetic_information_or"])
    for fid in ("to_obtain_a_certificate_of_adoption",
                 "to_obtain_a_certified_copy_of_the_adoption_record",
                 "to_obtain_medical_andor_genetic_information_or",
                 "to_obtain_other_information_as_specified_below"):
        if fid in disclosure_types and _set(out, fid, "X"):
            changes.append((fid, "X", f"022-disclose"))

    # 5-reason narrative (paragraphs 4_petitioner_states..._1-5)
    reasons = facts.get("ad_disclosure_reasons", [
        "I am the biological parent of the named adoptee and am seeking "
        "to provide updated medical and genetic information that has "
        "become relevant to the adoptee's healthcare.",
        "Recent diagnosis of a hereditary condition in my family makes "
        "this information potentially important to the adoptee's "
        "future medical decisions.",
        "I respect the privacy of the adoption and request that this "
        "information be released only as permitted under 18-C M.R.S.",
        "The information sought is necessary for the limited purpose "
        "described and will not be used to identify the adoptee against "
        "the adoptee's wishes.",
        "No prior petition for disclosure has been filed in this matter.",
    ])
    for i, r in enumerate(reasons[:5], start=1):
        fid = f"4_petitioner_states_the_following_reasons_for_requesting_the_above_documents_andor_information_{i}"
        if r and _set(out, fid, r):
            changes.append((fid, r, f"022-reason-{i}"))

    # Signature block. build_kv_map's narrative pass pre-stamps these widgets
    # (and the attorney block) with the WRONG party (e.g. defendant), so plain
    # _set (fill-if-empty) leaves the pollution. Force-overwrite both blocks to
    # the correct identities, and clear the attorney block when pro se.
    def _force(fid: str, val: str, src: str) -> None:
        if fid in out and out.get(fid) != val:
            out[fid] = val
            changes.append((fid, val, src))

    sig_date = (case.get("filing_date") or case.get("event_date") or "")
    pet_csz = f"{addr_city}, {petitioner.get('state','ME')} {addr_zip}".strip(", ")
    _force("date", _iso_to_us(sig_date), "022-date")
    _force("name_1", pl_name, "022-signer")          # Petitioner Name
    _force("address", addr, "022-addr")               # Petitioner address line 1
    _force("name_2", pet_csz, "022-addr2")            # address line 2 (city/state/zip)
    _force("phone_number", petitioner.get("phone", ""), "022-phone")
    _force("email", petitioner.get("email", ""), "022-email")

    # Attorney block (Name 1_2 / Address_2 / Name 2_2 / Phone Number_2 / Email_2)
    if attorney.get("full_name"):
        atty_csz = (attorney.get("address_2")
                    or f"{attorney.get('city','')}, {attorney.get('state','ME')} "
                       f"{attorney.get('zip','')}".strip(", "))
        _force("name_1_2", attorney.get("full_name", ""), "022-atty-name")
        _force("address_2", attorney.get("address", ""), "022-atty-addr")
        _force("name_2_2", atty_csz, "022-atty-addr2")
        _force("phone_number_2", attorney.get("phone", ""), "022-atty-phone")
        _force("email_2", attorney.get("email", ""), "022-atty-email")
    else:
        for fid in ("name_1_2", "address_2", "name_2_2",
                    "phone_number_2", "email_2"):
            if out.get(fid):
                out[fid] = ""
                changes.append((fid, "", "022-atty-clear"))

    # Notary block
    if _set(out, "personally_appeared_the_above_named", pl_name):
        changes.append(("personally_appeared_the_above_named", pl_name,
                        "022-notary"))


def _process_ad030(out: dict, case: dict, changes: list) -> None:
    """AD-030: joint petition for adoption."""
    facts = case.get("facts") or {}
    parties = case.get("parties") or {}
    court = case.get("court") or {}
    petitioner = (parties.get("petitioner") or parties.get("plaintiff")
                   or {})
    # In a stepparent adoption, the consenting biological parent is also
    # the joint petitioner. Fall back through consenting_parent if the
    # case wasn't generated with an explicit copetitioner role.
    copetitioner = (parties.get("copetitioner")
                     or parties.get("co_petitioner")
                     or parties.get("spouse")
                     or parties.get("consenting_parent") or {})
    adoptee = (parties.get("adoptee") or parties.get("minor")
                or parties.get("child") or parties.get("child_1") or {})
    attorney = parties.get("attorney") or {}

    def _full_addr(p: dict) -> str:
        street = p.get("address") or p.get("mailing_address", "")
        city = p.get("city", "")
        state = p.get("state", "")
        zipc = p.get("zip", "")
        tail = ", ".join(x for x in (city, f"{state} {zipc}".strip())
                          if x)
        return ", ".join(x for x in (street, tail) if x)

    # Captions
    pet_addr = _full_addr(petitioner)
    cop_addr = _full_addr(copetitioner)
    fills = [
        ("location", court.get("location", "")),
        ("docket_no_2", case.get("docket_no", "")),
        ("name_of_adoptee", adoptee.get("full_name", "")),
        # Petitioner 1 — full addr with city/state/zip
        ("name", petitioner.get("full_name", "")),
        ("date_of_birth", _iso_to_us(petitioner.get("dob", ""))),
        ("legal_residence", pet_addr),
        ("mailing_address", pet_addr),
        ("telephone", petitioner.get("phone", "")),
        # Marriage date/place ONLY when explicitly provided (was a
        # stock "06/14/2008, Portland, Maine").
        ("dateplace_of_marriage",
         facts.get("ad_marriage_date_place", "")),
        # Petitioner 2 — full addr with city/state/zip
        ("name_2", copetitioner.get("full_name", "")),
        ("date_of_birth_2", _iso_to_us(copetitioner.get("dob", ""))),
        ("legal_residence_2", cop_addr),
        ("mailing_address_2", cop_addr),
        ("telephone_2", copetitioner.get("phone", "")),
        ("dateplace_of_marriage_2",
         facts.get("ad_marriage_date_place", "")),
        # Adoptee
        ("name_3", adoptee.get("full_name", "")),
        ("date_of_birth_3", _iso_to_us(adoptee.get("dob", ""))),
        # Birthplace ONLY when explicitly provided (was a stock
        # "Portland, Maine").
        ("place_of_birth", facts.get("adoptee_place_of_birth", "")),
    ]
    # Force-overwrite (not fill-if-empty): build_kv_map's narrative pass
    # pollutes the caption identity widgets (e.g. the adoptee Name `name_3`
    # and the Petitioner-2 Name `name_2`) with the wrong party, and _set would
    # leave it. Only force when the recipe has a real value.
    for fid, val in fills:
        if val and out.get(fid) != val:
            out[fid] = val
            changes.append((fid, val, f"030-{fid[:20]}"))

    # No co-petitioner in this case → clear Petitioner-2 caption block so it
    # doesn't show build_kv_map's stray (e.g. the defendant) instead of blank.
    if not copetitioner.get("full_name"):
        for fid in ("name_2", "date_of_birth_2", "legal_residence_2",
                    "mailing_address_2", "telephone_2",
                    "dateplace_of_marriage_2"):
            if out.get(fid):
                out[fid] = ""
                changes.append((fid, "", "030-copet-clear"))

    # Venue radios (default: adoptee resides here)
    if _set(out, "adoptee_resides_in_this_county_andor", "X"):
        changes.append(("adoptee_resides_in_this_county_andor", "X",
                        "030-venue-adoptee"))
    if _set(out, "petitioners_resides_in_this_county", "X"):
        changes.append(("petitioners_resides_in_this_county", "X",
                        "030-venue-pet"))

    # Past 5-period residences (item 5 in AD-030: adoptee_was_present_1..5)
    primary_addr = (adoptee.get("address") or petitioner.get("address",""))
    if _set(out, "adoptee_was_present_1",
            f"{primary_addr} — entire 5-year period"):
        changes.append(("adoptee_was_present_1",
                        primary_addr, "030-residence-1"))

    # Custody-history checkboxes (radios; default "No")
    for fid in ("havehas_participated_as_a_party_witness_or_in_some_other_capacity_in_other_litigation_concerning_the_custody",
                 "havehas_information_of_a_custody_proceeding_concerning_the_adoptee_pending_in_a_court_in_maine_or_some",
                 "knows_of_a_person_not_a_party_to_this_case_who_has_physical_custody_of_the_adoptee_or_claims_to_have"):
        if _set(out, fid, "No"):
            changes.append((fid, "No", "030-cust-no"))

    # ART (assisted reproduction) — `6_1` is a wide 500px narrative.
    # Default explains a stepparent adoption (most common pattern).
    art_explain = facts.get("ad_art_explanation",
        "Not applicable — the adoptee was conceived and born during "
        "the consenting biological parent's prior marriage. No assisted "
        "reproductive technology was used and there are no donor or "
        "surrogacy claims of parentage to address.")
    if _set(out, "6_1", art_explain):
        changes.append(("6_1", art_explain, "030-art"))

    # Document attachments
    if _set(out, "a_copy_of_the_childs_birth_certificate_and", "X"):
        changes.append(("a_copy_of_the_childs_birth_certificate_and",
                        "X", "030-birthcert"))
    if copetitioner.get("full_name"):
        if _set(out, "a_copy_of_the_joint_petitioners_marriage_certificate",
                "X"):
            changes.append((
                "a_copy_of_the_joint_petitioners_marriage_certificate",
                "X", "030-marrcert"))
    else:
        if _set(out,
                "not_applicable_because_this_petition_is_filed_by_a_single_petitioner",
                "X"):
            changes.append((
                "not_applicable_because_this_petition_is_filed_by_a_single_petitioner",
                "X", "030-single"))

    # Three signature/contact blocks on page 2, by widget position:
    #   Block 1 (Petitioner 1):  Name_4 / Address 1 / Address 2 / Phone Number /
    #                            `attorney_for_petitioners_if_any` (= EMAIL line)
    #   Block 2 (Petitioner 2):  Name_5 / Address 1_2 / Address 2_2 /
    #                            Phone Number_2 / `undefined` (= EMAIL line)
    #   Block 3 (Attorney):      Name_6 / Address 1_3 / Address 2_3 /
    #                            Phone Number_3 / Email
    # build_kv_map's narrative pass pollutes these with the wrong party and the
    # old fill-if-empty left it; force-overwrite each block to its own identity.
    # NOTE: the widget literally named `attorney_for_petitioners_if_any` is
    # physically Block-1's email line, NOT an attorney field — wiring it to the
    # attorney put the attorney's name in the petitioner's email.
    sig_date = _iso_to_us(case.get("filing_date") or "")
    pl_name = petitioner.get("full_name", "")

    def _force(fid: str, val: str, src: str) -> None:
        if fid in out and out.get(fid) != val:
            out[fid] = val
            changes.append((fid, val, src))

    def _csz(p: dict) -> str:
        return (p.get("address_2")
                or f"{p.get('city','')}, {p.get('state','ME')} "
                   f"{p.get('zip','')}".strip(", "))

    for fid in ("text1", "text2", "text3"):
        if _set(out, fid, "X"):
            changes.append((fid, "X", f"030-{fid}"))
    for fid in ("date", "date_2", "date_3", "date_4"):
        _force(fid, sig_date, f"030-{fid}")

    # Block 1 — Petitioner 1
    _force("name_4", petitioner.get("full_name", ""), "030-b1-name")
    _force("address_1", petitioner.get("address", ""), "030-b1-addr")
    _force("address_2", _csz(petitioner), "030-b1-csz")
    _force("phone_number", petitioner.get("phone", ""), "030-b1-phone")
    _force("attorney_for_petitioners_if_any",
           petitioner.get("email", ""), "030-b1-email")

    # Block 2 — Petitioner 2 (co-petitioner); clear if none
    if copetitioner.get("full_name"):
        _force("name_5", copetitioner.get("full_name", ""), "030-b2-name")
        _force("address_1_2", copetitioner.get("address", ""), "030-b2-addr")
        _force("address_2_2", _csz(copetitioner), "030-b2-csz")
        _force("phone_number_2", copetitioner.get("phone", ""), "030-b2-phone")
        _force("undefined", copetitioner.get("email", ""), "030-b2-email")
    else:
        for fid in ("name_5", "address_1_2", "address_2_2",
                    "phone_number_2", "undefined", "date_2"):
            if out.get(fid):
                out[fid] = ""
                changes.append((fid, "", "030-b2-clear"))

    # Block 3 — Attorney; clear if pro se
    if attorney.get("full_name"):
        _force("name_6", attorney.get("full_name", ""), "030-b3-name")
        _force("address_1_3", attorney.get("address", ""), "030-b3-addr")
        _force("address_2_3", _csz(attorney), "030-b3-csz")
        _force("phone_number_3", attorney.get("phone", ""), "030-b3-phone")
        _force("email", attorney.get("email", ""), "030-b3-email")
    else:
        for fid in ("name_6", "address_1_3", "address_2_3",
                    "phone_number_3", "email", "date_3", "text3"):
            if out.get(fid):
                out[fid] = ""
                changes.append((fid, "", "030-b3-clear"))
    if court.get("county") and _set(out, "county", court["county"]):
        changes.append(("county", court["county"], "030-county"))
    if _set(out, "personally_appeared_the_above_named", pl_name):
        changes.append(("personally_appeared_the_above_named", pl_name,
                        "030-notary"))


def _process_ad003(out: dict, case: dict, changes: list) -> None:
    """AD-003: Consent to Adoption by DHHS / Agency / Guardian /
    Custodian. Signer is a non-parent role (DHHS officer, licensed
    agency, legal guardian, or legal custodian)."""
    facts = case.get("facts") or {}
    parties = case.get("parties") or {}
    court = case.get("court") or {}
    adoptee = (parties.get("adoptee") or parties.get("minor")
                or parties.get("child") or {})
    # Signer = guardian / DHHS officer — ONLY from a real party or an
    # explicit fact. Never synthesize a consenting signer (was a stock
    # "Catherine M. Whitford"); a fabricated consent signer is a material
    # misstatement on a consent to adoption.
    signer = (parties.get("legal_guardian") or parties.get("guardian")
                or parties.get("consenting_parent") or {})
    if not signer.get("full_name"):
        signer = {"full_name": facts.get("ad003_signer_name", "")}
    adoptive = parties.get("petitioner") or parties.get("plaintiff") or {}

    if _set(out, "location", court.get("location", "")):
        changes.append(("location", court.get("location",""), "003-loc"))
    if _set(out, "docket_no_2", case.get("docket_no", "")):
        changes.append(("docket_no_2", case.get("docket_no",""), "003-dock"))
    if _set(out, "docket_no", case.get("docket_no", "")):
        changes.append(("docket_no", case.get("docket_no",""), "003-dock2"))
    if court.get("county") and _set(out, "county", court["county"]):
        changes.append(("county", court["county"], "003-county"))
    if _set(out, "name_of_adoptee", adoptee.get("full_name", "")):
        changes.append(("name_of_adoptee", adoptee.get("full_name",""),
                          "003-adoptee"))
    if signer["full_name"] and _set(out, "i", signer["full_name"]):
        changes.append(("i", signer["full_name"], "003-signer"))

    # Signer role checkbox — check ONLY when explicitly provided (was
    # defaulted to "legal guardian", asserting the signer's authority).
    role = facts.get("ad003_role", "")
    role_map = {
        "dhhs":     "an_officer_of_the_maine_department_of_health_and_human_services",
        "agency":   "a_duly_licensed_child",
        "guardian": "the_legal_guardian_of_the_abovenamed_adoptee",
        "legal_guardian": "the_legal_guardian_of_the_abovenamed_adoptee",
        "custodian": "the_legal_custodian_of_the_abovenamed_adoptee",
    }
    role_fid = role_map.get(role) if role else None
    if role_fid and _set(out, role_fid, "X"):
        changes.append((role_fid, "X", "003-role"))

    # Adopting parent (single name in `named_adoptee_by` and `name`)
    adopter = adoptive.get("full_name", "")
    if _set(out, "named_adoptee_by", adopter):
        changes.append(("named_adoptee_by", adopter, "003-adopter"))
    if _set(out, "name", adopter):
        changes.append(("name", adopter, "003-name"))

    sig_date_us = _iso_to_us(case.get("filing_date", ""))
    if _set(out, "dated", sig_date_us):
        changes.append(("dated", sig_date_us, "003-date"))
    if _set(out, "personally_appeared_the_abovenamed", signer["full_name"]):
        changes.append(("personally_appeared_the_abovenamed",
                          signer["full_name"], "003-notary"))
    if _set(out, "text1", signer["full_name"]):
        changes.append(("text1", signer["full_name"], "003-text1"))


def _process_ad004(out: dict, case: dict, changes: list) -> None:
    """AD-004: Consent by Adult Adoptee (18+) to own adoption."""
    facts = case.get("facts") or {}
    parties = case.get("parties") or {}
    court = case.get("court") or {}
    adoptee = (parties.get("adoptee") or parties.get("petitioner")
                or parties.get("minor") or {})
    adoptive_parents = facts.get("ad004_petitioners",
                                       (parties.get("petitioner") or {}).get("full_name",
                                                                                "Robert J. Sterling and Sarah E. Sterling"))

    if _set(out, "location", court.get("location", "")):
        changes.append(("location", court.get("location",""), "004-loc"))
    if _set(out, "docket_no_2", case.get("docket_no", "")):
        changes.append(("docket_no_2", case.get("docket_no",""), "004-dock"))
    if court.get("county") and _set(out, "county", court["county"]):
        changes.append(("county", court["county"], "004-county"))
    if _set(out, "name_of_adoptee", adoptee.get("full_name", "")):
        changes.append(("name_of_adoptee", adoptee.get("full_name",""),
                          "004-adoptee"))

    # Default to standard (non-confirmatory) petition radio
    if _set(out,
            "this_matter_involves_an_adoption_petition_filed_pursuant_to_18c_mrs_9301_and_the_minor_adoptee",
            "X"):
        changes.append((
            "this_matter_involves_an_adoption_petition_filed_pursuant_to_18c_mrs_9301_and_the_minor_adoptee",
            "X", "004-standard"))

    dob_us = _iso_to_us(adoptee.get("dob", ""))
    # Compute age from DOB (use 18+ default if not present)
    age = "18"
    if dob_us and "/" in dob_us:
        try:
            from datetime import date
            y = int(dob_us[-4:])
            age = str(date.today().year - y)
        except Exception:
            pass
    if _set(out, "i_am_the_adoptee_named_above_i_was_born_on", dob_us):
        changes.append(("i_am_the_adoptee_named_above_i_was_born_on",
                          dob_us, "004-dob"))
    if _set(out, "and_i_am", age):
        changes.append(("and_i_am", age, "004-age"))
    if _set(out, "i_understand_that_a_petition_to_adopt_me_has_been_filed_by",
            adoptive_parents):
        changes.append((
            "i_understand_that_a_petition_to_adopt_me_has_been_filed_by",
            adoptive_parents, "004-petitioners"))
    if _set(out, "petitioners_who_will_become_my_legal", "parents"):
        changes.append(("petitioners_who_will_become_my_legal", "parents",
                          "004-relationship"))
    new_name = facts.get("ad004_new_name", "")
    if not new_name and adoptive_parents and adoptee.get("full_name"):
        parts = adoptive_parents.split(" and ")
        if parts:
            surname = parts[0].split()[-1]
            adoptee_first = " ".join(adoptee["full_name"].split()[:-1])
            new_name = f"{adoptee_first} {surname}".strip()
    if _set(out, "and_for_the_change_of_my_name", new_name):
        changes.append(("and_for_the_change_of_my_name", new_name,
                          "004-newname"))

    sig_date_us = _iso_to_us(case.get("filing_date", ""))
    if _set(out, "dated", sig_date_us):
        changes.append(("dated", sig_date_us, "004-date"))
    if _set(out, "text1", adoptee.get("full_name", "")):
        changes.append(("text1", adoptee.get("full_name",""), "004-signer"))
    if _set(out, "printed_name_of_adoptee", adoptee.get("full_name", "")):
        changes.append(("printed_name_of_adoptee",
                          adoptee.get("full_name",""), "004-printed"))
    if _set(out, "personally_appeared_the_abovenamed",
            adoptee.get("full_name", "")):
        changes.append(("personally_appeared_the_abovenamed",
                          adoptee.get("full_name",""), "004-notary"))


def _process_ad017(out: dict, case: dict, changes: list) -> None:
    """AD-017: Notice to Putative Parent (response to adoption petition).

    Putative parent admits/denies/neither paternity and requests/declines
    inheritance rights. Schema has admission radio + request radio +
    signature/notary block.
    """
    facts = case.get("facts") or {}
    parties = case.get("parties") or {}
    court = case.get("court") or {}
    adoptee = (parties.get("adoptee") or parties.get("minor")
                or parties.get("child") or {})
    putative = (parties.get("non_consenting_parent")
                  or parties.get("putative_parent")
                  or parties.get("biological_parent_2") or {})
    legal_parent = (parties.get("consenting_parent")
                      or parties.get("petitioner") or {})

    if _set(out, "location", court.get("location", "")):
        changes.append(("location", court.get("location",""), "017-loc"))
    if _set(out, "docket_no_2", case.get("docket_no", "")):
        changes.append(("docket_no_2", case.get("docket_no",""), "017-dock"))
    adoptee_name = adoptee.get("full_name", "")
    if _set(out, "name_of_adoptee", adoptee_name):
        changes.append(("name_of_adoptee", adoptee_name, "017-adoptee"))
    if _set(out, "name", putative.get("full_name", "")):
        changes.append(("name", putative.get("full_name",""), "017-putative"))
    if _set(out, "name_of_legal_parents_1", legal_parent.get("full_name", "")):
        changes.append(("name_of_legal_parents_1",
                          legal_parent.get("full_name",""), "017-legal-1"))
    # Position + inheritance election — these admit/deny parentage and
    # elect inheritance rights; check ONLY when explicitly provided
    # (were defaulted to "admit" + "request").
    admit = facts.get("ad017_position", "")  # admit|deny|neither
    admit_map = {
        "admit":   "i_admit_that_i_am_a_biological_parent_of_the_child",
        "neither": "i_neither_admit_nor_deny_that_i_am_a_biological_parent_of_the_child",
    }
    admit_fid = admit_map.get(admit) if admit else None
    if admit_fid and _set(out, admit_fid, "X"):
        changes.append((admit_fid, "X", "017-position"))
    inherit = facts.get("ad017_inherit", "")  # request|do_not_request
    if inherit:
        inherit_fid = ("request" if inherit == "request"
                         else "do_not_request_that_my_child_be_entitled_to_inherit")
        if _set(out, inherit_fid, "X"):
            changes.append((inherit_fid, "X", "017-inherit"))
    sig_date = _iso_to_us(case.get("filing_date", ""))
    if _set(out, "dated", sig_date):
        changes.append(("dated", sig_date, "017-date"))
    if _set(out, "text1", putative.get("full_name", "")):
        changes.append(("text1", putative.get("full_name",""), "017-signer"))
    if _set(out, "personally_appeared_the_above_named_putative_parent",
            putative.get("full_name", "")):
        changes.append(("personally_appeared_the_above_named_putative_parent",
                          putative.get("full_name",""), "017-notary"))


def _process_ad032(out: dict, case: dict, changes: list) -> None:
    """AD-032: Adult Adoptee Name Change Petition.

    Adult adoptee requests name change post-adoption. Schema has name
    + aliases + DOB + mailing address + signature block + contact info.
    """
    facts = case.get("facts") or {}
    parties = case.get("parties") or {}
    court = case.get("court") or {}
    adoptee = (parties.get("adoptee") or parties.get("petitioner")
                or parties.get("plaintiff") or {})

    if _set(out, "location", court.get("location", "")):
        changes.append(("location", court.get("location",""), "032-loc"))
    if _set(out, "docket_no_2", case.get("docket_no", "")):
        changes.append(("docket_no_2", case.get("docket_no",""), "032-dock"))
    # AD-032 is a single-party form (the adult adoptee). build_kv_map's
    # narrative pass stamps the contact/signature widgets with whatever party
    # its heuristic guessed (often the defendant), so fill-if-empty left the
    # wrong identity. Force-overwrite every identity/contact field to the
    # adoptee.
    def _force(fid: str, val: str, src: str) -> None:
        if fid in out and out.get(fid) != val:
            out[fid] = val
            changes.append((fid, val, src))

    _force("full_name_first_middle_last", adoptee.get("full_name", ""),
           "032-name")
    # Aliases ONLY when explicitly provided — "None" is itself a factual
    # assertion that the adoptee has no other names.
    if facts.get("ad032_aliases"):
        _force("aliases_including_maiden_name",
               facts["ad032_aliases"], "032-aliases")
    _force("date_of_birth_mmddyyyy", _iso_to_us(adoptee.get("dob", "")),
           "032-dob")
    addr_parts = [adoptee.get("address",""),
                    f"{adoptee.get('city','')}, "
                    f"{adoptee.get('state','ME')} {adoptee.get('zip','')}".strip(', ')]
    full_addr = ", ".join(p for p in addr_parts if p)
    _force("mailing_address", full_addr, "032-addr")
    _force("following_email_address", adoptee.get("email", ""), "032-email")
    sig_date = _iso_to_us(case.get("filing_date", ""))
    for fid in ("date", "date_2"):
        _force(fid, sig_date, "032-date")
    for fid in ("text1", "text2"):
        _force(fid, adoptee.get("full_name", ""), "032-signer")
    _force("address_1", addr_parts[0], "032-addr1")
    _force("address_2", addr_parts[1], "032-addr2")
    _force("phone_number", adoptee.get("phone", ""), "032-phone")


def _process_ad029(out: dict, case: dict, changes: list) -> None:
    """AD-029: Maine Adoption Information Form.

    Three-section data sheet: A=adoptee birth/adoption names+DOB+tribal,
    B=biological parents (×2 name+address), C=current/adoptive parents
    (×2 name+address). Petitioner contact block + attorney block at
    bottom.
    """
    facts = case.get("facts") or {}
    parties = case.get("parties") or {}
    court = case.get("court") or {}
    adoptee = (parties.get("adoptee") or parties.get("minor")
                or parties.get("child") or parties.get("child_1") or {})
    petitioner = (parties.get("petitioner") or parties.get("plaintiff")
                    or {})
    copetitioner = (parties.get("copetitioner")
                     or parties.get("co_petitioner")
                     or parties.get("spouse")
                     or parties.get("consenting_parent") or {})
    bio_parent_1 = (parties.get("consenting_parent")
                     or parties.get("biological_parent_1")
                     or copetitioner or {})
    bio_parent_2 = (parties.get("non_consenting_parent")
                     or parties.get("biological_parent_2") or {})
    attorney = parties.get("attorney") or {}

    # Caption
    if _set(out, "location", court.get("location", "")):
        changes.append(("location", court.get("location",""), "029-loc"))
    if _set(out, "docket_no_2", case.get("docket_no", "")):
        changes.append(("docket_no_2", case.get("docket_no",""), "029-dock"))
    if _set(out, "name_of_adoptee", adoptee.get("full_name", "")):
        changes.append(("name_of_adoptee", adoptee.get("full_name",""),
                          "029-adoptee"))

    # Section A — adoptee info
    birth_name = facts.get("adoptee_birth_name",
                              adoptee.get("full_name", ""))
    if _set(out, "1_birth_name", birth_name):
        changes.append(("1_birth_name", birth_name, "029-birth"))
    new_name = facts.get("adoptee_name_after_adoption",
                            adoptee.get("full_name", ""))
    if petitioner.get("full_name"):
        # In stepparent adoption, adoptee takes petitioner's surname
        pet_surname = petitioner["full_name"].split()[-1]
        adoptee_first = " ".join(adoptee.get("full_name","").split()[:-1])
        if adoptee_first:
            new_name = f"{adoptee_first} {pet_surname}".strip()
    if _set(out, "2_name_after_adoption_if_different", new_name):
        changes.append(("2_name_after_adoption_if_different", new_name,
                          "029-new-name"))
    if _set(out, "3_birthdate", _iso_to_us(adoptee.get("dob", ""))):
        changes.append(("3_birthdate", _iso_to_us(adoptee.get("dob","")),
                          "029-birthdate"))
    # ICWA-critical: only filled when the case explicitly provides the
    # tribal affiliation (was defaulted "Not applicable").
    if facts.get("adoptee_tribe") and _set(
            out, "4_tribal_affiliation_name_of_tribe",
            facts["adoptee_tribe"]):
        changes.append(("4_tribal_affiliation_name_of_tribe",
                          facts["adoptee_tribe"], "029-tribe"))

    # Section B — biological parents
    def _addr_full(p: dict) -> str:
        s = p.get("address","")
        c = p.get("city","")
        st = p.get("state","")
        z = p.get("zip","")
        tail = ", ".join(x for x in (c, f"{st} {z}".strip()) if x)
        return ", ".join(x for x in (s, tail) if x)

    if _set(out, "1_biological_parent_name", bio_parent_1.get("full_name", "")):
        changes.append(("1_biological_parent_name",
                          bio_parent_1.get("full_name",""), "029-bio1"))
    if _set(out, "address", _addr_full(bio_parent_1)):
        changes.append(("address", _addr_full(bio_parent_1), "029-bio1-addr"))
    if _set(out, "2_biological_parent_name", bio_parent_2.get("full_name", "")):
        changes.append(("2_biological_parent_name",
                          bio_parent_2.get("full_name",""), "029-bio2"))
    if _set(out, "address_2", _addr_full(bio_parent_2)):
        changes.append(("address_2", _addr_full(bio_parent_2), "029-bio2-addr"))

    # Sections C/petitioner/signature/attorney: build_kv_map's narrative pass
    # pollutes these identity widgets (the petitioner-address row got the
    # attorney address; the attorney-name row got the petitioner), and fill-if-
    # empty left it. Force-overwrite each to its own party; clear the attorney
    # block when pro se.
    def _force(fid: str, val: str, src: str) -> None:
        if fid in out and out.get(fid) != val:
            out[fid] = val
            changes.append((fid, val, src))

    # Section C — current/adoptive parents
    _force("1_name", petitioner.get("full_name", ""), "029-pet")
    _force("address_3", _addr_full(petitioner), "029-pet-addr")
    if copetitioner.get("full_name"):
        _force("2_name", copetitioner.get("full_name", ""), "029-copet")
        _force("address_4", _addr_full(copetitioner), "029-copet-addr")
    else:
        for fid in ("2_name", "address_4"):
            if out.get(fid):
                out[fid] = ""
                changes.append((fid, "", "029-copet-clear"))

    # Petitioner contact block
    _force("name", petitioner.get("full_name", ""), "029-name")
    _force("address_5", _addr_full(petitioner), "029-name-addr")
    _force("telephone", petitioner.get("phone", ""), "029-tel")

    # Signature block
    sig_date_us = _iso_to_us(case.get("filing_date", ""))
    _force("text2", petitioner.get("full_name", ""), "029-sig")
    _force("text1", sig_date_us, "029-sig-date")
    _force("date_3", sig_date_us, "029-date3")

    # Attorney block (clear when pro se)
    if attorney.get("full_name"):
        _force("name_1", attorney.get("full_name", ""), "029-atty")
        _force("address_6", _addr_full(attorney), "029-atty-addr")
        _force("name_2", attorney.get("full_name", ""), "029-atty-2")
        _force("phone_number", attorney.get("phone", ""), "029-atty-phone")
        _force("email", attorney.get("email", ""), "029-atty-email")
    else:
        for fid in ("name_1", "address_6", "name_2", "phone_number", "email"):
            if out.get(fid):
                out[fid] = ""
                changes.append((fid, "", "029-atty-clear"))


def process(kv_map: dict, case: dict) -> tuple[dict, list]:
    out = dict(kv_map)
    changes: list = []

    # Dispatch on schema-field-key presence
    if "name_of_adoptee" in out and "i_have_followed_the_procedure_required_to_make_a_consent_valid_in" in out:
        _process_ad006(out, case, changes)
    elif "first" in out and "middle" in out and "to_obtain_a_certificate_of_adoption" in out:
        _process_ad022(out, case, changes)
    elif "name_of_adoptee" in out and "adoptee_resides_in_this_county_andor" in out:
        _process_ad030(out, case, changes)
    elif "1_birth_name" in out and "4_tribal_affiliation_name_of_tribe" in out:
        _process_ad029(out, case, changes)
    elif ("i_admit_that_i_am_a_biological_parent_of_the_child" in out
            and "name_of_legal_parents_1" in out):
        _process_ad017(out, case, changes)
    elif ("full_name_first_middle_last" in out
            and "aliases_including_maiden_name" in out):
        _process_ad032(out, case, changes)
    elif ("the_legal_guardian_of_the_abovenamed_adoptee" in out
            and "an_officer_of" in out):
        _process_ad003(out, case, changes)
    elif ("i_am_the_adoptee_named_above_i_was_born_on" in out
            and "printed_name_of_adoptee" in out):
        _process_ad004(out, case, changes)

    return out, changes


if __name__ == "__main__":
    print("Use via fill_and_audit.py RECIPE3 dispatch")
    sys.exit(0)
