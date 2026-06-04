"""Universal case-data shape for Maine court form fills.

Covers the fields that appear across MOST court forms (county, docket,
parties, attorney, signature dates). Form-specific narrative content
still requires recipe-3 inference scripts per form.

Build a case dict, then `build_kv_map.py` translates it into the
{field_id: value} dictionary each form expects.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class Party:
    full_name: str = ""
    address: str = ""        # full single-line address; consumers split
    mailing_address: str = "" # if different from physical
    city: str = ""
    state: str = "ME"
    zip: str = ""
    phone: str = ""          # primary phone (legacy)
    phone_cell: str = ""
    phone_home: str = ""
    phone_work: str = ""
    email: str = ""
    dob: str = ""            # ISO 8601 YYYY-MM-DD
    relationship: str = ""   # to decedent / minor / etc.
    role: str = ""           # "petitioner", "attorney", etc.

    @property
    def first_name(self) -> str:
        return self.full_name.split()[0] if self.full_name else ""

    @property
    def middle_name(self) -> str:
        parts = self.full_name.split()
        return parts[1] if len(parts) >= 3 else ""

    @property
    def last_name(self) -> str:
        parts = self.full_name.split()
        # Skip trailing "(deceased)" / "Esq." suffixes
        clean = [p for p in parts if p not in ("(deceased)", "Esq.", "Jr.", "Sr.", "II", "III")]
        return clean[-1] if clean else ""

    def to_dict_with_derived(self):
        """asdict() doesn't include @property — emit them here."""
        from dataclasses import asdict
        d = asdict(self)
        d["first_name"] = self.first_name
        d["middle_name"] = self.middle_name
        d["last_name"] = self.last_name
        return d


@dataclass
class Attorney(Party):
    bar_number: str = ""
    firm: str = ""


@dataclass
class Court:
    name: str = "Maine District Court"
    county: str = "Cumberland"
    location: str = "Portland"


@dataclass
class Case:
    case_id: str = ""
    case_no: str = ""           # "2024-CV-00234"
    docket_no: str = ""         # may equal case_no on some forms
    case_type: str = ""         # "civil", "family", "criminal", "probate", ...
    court: Court = field(default_factory=Court)
    filing_date: str = ""       # ISO 8601
    event_date: str = ""        # form-specific anchor date
    notary_county: str = ""     # for jurat blocks; defaults to court.county

    parties: dict[str, Party] = field(default_factory=dict)
    # Conventional keys: petitioner, respondent, plaintiff, defendant,
    # decedent, applicant, minor, guardian, conservator, attorney.

    facts: dict[str, str] = field(default_factory=dict)
    # Free-form: e.g. {"amount_in_controversy": "5,000.00",
    # "marriage_date": "2010-06-15", "children_count": "2"}.

    field_overrides: dict[str, dict[str, str]] = field(default_factory=dict)
    # Per-form explicit overrides keyed by form_id, then field_id:
    # {"FM-008": {"parent_or": "Yes",
    #             "the_custodydetermination_orderhasacceptedjurisdiction": "Yes"}}
    # K:V engine looks up overrides[form_id] before doing its heuristic
    # fill, so checkbox toggles + form-specific narrative can be wired
    # without writing a per-form inference script.

    def to_dict(self) -> dict:
        d = asdict(self)
        # Expand each party with @property-derived fields
        for k, v in (self.parties or {}).items():
            d["parties"][k] = v.to_dict_with_derived()
        return d


# --- Example sample cases for smoke-testing fills ---

def sample_family_matters_case() -> Case:
    """Divorce / family matters fact pattern."""
    return Case(
        case_id="FM-DEMO-001",
        case_no="2024-FM-00321",
        docket_no="2024-FM-00321",
        case_type="family",
        court=Court(name="Maine District Court",
                    county="Cumberland", location="Portland"),
        filing_date="2024-09-12",
        event_date="2024-09-12",
        notary_county="Cumberland",
        field_overrides={
            "FM-008": {
                # Item 1: petitioner is the parent (not a non-parent custodian)
                "parent_or": "Yes",
                # Item 4: court HAS jurisdiction
                "the_custodydetermination_orderhas": "Yes",
                # Item 5: order has not been vacated/modified
                "the_custody_determination_orderhasnot_been": "Yes",
                # Item 8: requests immediate physical custody
                "granttheimmediatephysicalcustodyof_the_childrentothe_petitioner": "Yes",
                # Item 9: requests warrant (default off)
                # perjury checkbox above signature
                "iswear_underpenaltyofperjury": "Yes",
            }
        },
        parties={
            "plaintiff": Party(
                full_name="Sarah J. Whitfield",
                address="142 Pine Ridge Road, Portland, ME 04101",
                mailing_address="P.O. Box 1284, Portland, ME 04104",
                city="Portland", state="ME", zip="04101",
                phone="207-555-0184",
                phone_cell="207-555-0184",
                phone_home="207-555-0125",
                phone_work="207-555-0501",
                email="sarah.whitfield@example.com",
                dob="1985-04-22", role="plaintiff"),
            "defendant": Party(
                full_name="Michael R. Whitfield",
                address="88 Ocean Avenue, Falmouth, ME 04105",
                mailing_address="88 Ocean Avenue, Falmouth, ME 04105",
                city="Falmouth", state="ME", zip="04105",
                phone="207-555-0102",
                phone_cell="207-555-0102",
                phone_home="207-555-0119",
                phone_work="207-555-0888",
                email="m.whitfield@example.com",
                dob="1983-07-15", role="defendant"),
            "attorney": Attorney(
                full_name="Catherine E. Pelletier, Esq.",
                address="14 High Street, Lewiston, ME 04240",
                city="Lewiston", state="ME", zip="04240",
                phone="207-555-0101", email="c.esq@mainelaw.com",
                bar_number="ME-15096", firm="Pelletier Legal Services",
                role="attorney"),
        },
        facts={
            "marriage_date": "2010-06-15",
            "separation_date": "2024-03-01",
            "children_count": "2",
            "ground_for_divorce": "irreconcilable differences",
            # Higher/lower income parents for FM-040-A
            "higher_income_parent": "Plaintiff",
            "higher_income_gross_weekly": "1450",
            "lower_income_gross_weekly": "725",
            # FM admit/deny
            "admit_paragraphs": "1, 2, 4",
            "deny_paragraphs": "3, 5",
            "insufficient_info_paragraphs": "6",
            "affirmative_defenses": "Statute of limitations.",
            "counterclaim": "Counterclaim for equitable distribution of marital assets.",
            # PFA defaults (for cases that route to PA forms)
            "pfa_defendant_height": "5'10\"",
            "pfa_defendant_weight": "180 lbs",
            "pfa_defendant_employer": "Cumberland Industrial Services",
            "pfa_defendant_work_address": "200 Industrial Way, Portland, ME 04101",
            "pfa_motion_request": (
                "extend the existing Protection from Abuse Order for one year."),
            "pfa_hearing_date": "2024-11-15",
            "pfa_hearing_time": "10:00 AM",
            "pfa_officer_name": "Deputy Sarah L. McCabe",
            "pfa_officer_agency": "Cumberland County Sheriff's Office",
            # OTH interpreter
            "interpreter_language": "Spanish ↔ English",
            "interpreter_vendor": "Maine Language Services LLC",
            "interpreter_vendor_code": "MLS-04821",
            "interpreter_payment_address": "212 Industrial Park Road, Portland, ME 04102",
            "interpreter_tier": "Tier 2 — Certified",
            "interpreter_hours": "2.5",
            "interpreter_rate": "75.00",
            # OTH disability accommodation
            "disability_type": "Mobility impairment requiring wheelchair access.",
            "accommodation_request": "Wheelchair-accessible courtroom and large-print documents.",
            "court_case_type": "Family Matters",
            # MRS tax forms
            "taxpayer_ssn": "012-34-5678",
            "residency_status": "Maine resident",
            "entity_name": "Acme Property Holdings LLC",
            "entity_address": "200 Congress St, Portland, ME 04101",
            "entity_type": "Partnership/LLC",
            "entity_ein": "01-2345678",
        },
    )


def sample_civil_case() -> Case:
    """Civil action — small money judgment."""
    return Case(
        case_id="CV-DEMO-001",
        case_no="2024-CV-00892",
        docket_no="2024-CV-00892",
        case_type="civil",
        court=Court(name="Cumberland County Superior Court",
                    county="Cumberland", location="Portland"),
        filing_date="2024-10-04",
        event_date="2024-10-04",
        parties={
            "plaintiff": Party(
                full_name="Acme Lumber Supply LLC",
                address="412 Industrial Park Road, Westbrook, ME 04092",
                city="Westbrook", state="ME", zip="04092",
                phone="207-555-0220", role="plaintiff"),
            "defendant": Party(
                full_name="Daniel A. McKenzie",
                address="78 Beach Avenue, Saco, ME 04072",
                city="Saco", state="ME", zip="04072",
                role="defendant"),
            "attorney": Attorney(
                full_name="Jonathan P. Mitchell, Esq.",
                address="142 Main Street, Portland, ME 04101",
                phone="207-555-0997", email="j.mitchell@mainelaw.com",
                bar_number="ME-7382", firm="Mitchell Law Office"),
        },
        facts={
            "amount_in_controversy": "12,450.00",
            "claim_basis": "Unpaid invoice for delivered goods",
            "invoice_date": "2024-05-18",
        },
    )


def sample_criminal_case() -> Case:
    """Criminal / bail bond fact pattern (CR-*).

    Includes a `surety` party so CR-004-style real-estate-lien bonds
    populate `i` (affiant), `of` (town), `street`, `dollars`, etc.
    """
    return Case(
        case_id="CR-DEMO-001",
        case_no="2024-CR-04421",
        docket_no="2024-CR-04421",
        case_type="criminal",
        court=Court(name="Unified Criminal Docket",
                    county="Cumberland", location="Portland"),
        filing_date="2024-07-08",
        event_date="2024-07-08",
        notary_county="Cumberland",
        parties={
            "defendant": Party(
                full_name="Daniel A. McKenzie",
                address="78 Beach Avenue, Saco, ME 04072",
                city="Saco", state="ME", zip="04072",
                phone="207-555-0102", dob="1990-07-15",
                role="defendant"),
            "surety": Party(
                full_name="Marie L. McKenzie",
                address="14 Spring Street, Saco, ME 04072",
                city="Saco", state="ME", zip="04072",
                phone="207-555-0118",
                role="surety", relationship="mother"),
            "attorney": Attorney(
                full_name="Jonathan P. Mitchell, Esq.",
                address="142 Main Street, Portland, ME 04101",
                phone="207-555-0997", email="j.mitchell@mainelaw.com",
                bar_number="ME-7382"),
        },
        facts={
            "offense": "operating under the influence",
            "bond_amount": "5,000.00",
            "penal_sum": "5,000.00",
            "registry_vol": "1234",
            "registry_page": "567",
        },
    )


def sample_guardianship_case() -> Case:
    """Guardianship-of-minor petition fact pattern (AD / GS / JV)."""
    return Case(
        case_id="GS-DEMO-001",
        case_no="2024-GS-00457",
        docket_no="2024-GS-00457",
        case_type="guardianship",
        court=Court(name="Maine Probate Court",
                    county="Cumberland", location="Portland"),
        filing_date="2024-08-22",
        event_date="2024-08-22",
        notary_county="Cumberland",
        parties={
            "petitioner": Party(
                full_name="Anne M. LeBlanc",
                address="22 Maple Street, Portland, ME 04101",
                city="Portland", state="ME", zip="04101",
                phone="207-555-0344",
                email="anne.leblanc@example.com",
                dob="1975-02-14", role="petitioner",
                relationship="grandmother"),
            "copetitioner": Party(
                full_name="Robert J. LeBlanc",
                address="22 Maple Street, Portland, ME 04101",
                city="Portland", state="ME", zip="04101",
                phone="207-555-0344", role="copetitioner",
                relationship="grandfather"),
            "minor": Party(
                full_name="Leo James Bennett",
                address="22 Maple Street, Portland, ME 04101",
                dob="2018-11-20", role="minor"),
            "attorney": Attorney(
                full_name="Margaret A. Sullivan, Esq.",
                address="28 Elm Street, Bangor, ME 04401",
                phone="207-555-0241",
                email="m.sullivan@mainelaw.com",
                bar_number="ME-9241",
                firm="Sullivan & Associates"),
        },
        facts={
            "reason_for_guardianship": "Parents incarcerated",
            "minor_age": "6",
            "consent_status": "consenting",
            # NC-001 / NC-003 name change facts
            "new_name_for_minor": "Leo James LeBlanc",
            "name_change_reason": (
                "To match the surname of the custodial grandmother "
                "with whom the minor resides and to provide consistency "
                "in school, medical, and identification records."),
            "documents_provided": (
                "Certified birth certificate, school enrollment records, "
                "and grandparent's government-issued ID"),
        },
    )


def pick_sample_case_for(form_id: str) -> Case:
    """Dispatch a representative sample case by form prefix."""
    prefix = form_id.split("-")[0]
    if prefix in ("FM",):
        return sample_family_matters_case()
    if prefix in ("AD", "GS", "JV", "PA", "NC"):
        return sample_guardianship_case()
    if prefix in ("CR", "MJ", "MJBVB"):
        return sample_criminal_case()
    return sample_civil_case()


if __name__ == "__main__":
    import json
    c = sample_family_matters_case()
    print(json.dumps(c.to_dict(), indent=2, default=str)[:1200])
