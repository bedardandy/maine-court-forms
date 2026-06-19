"""Shared scaffolding for the evaluation suite (``evals/``).

The *evals* are distinct from ``tests/``: tests pin internal invariants
(field placement, schema drift); evals assert the **product contract** an
LLM/automation consumer relies on — that the documented
route -> understand -> extract -> preflight -> fill -> verify flow chains and
yields a correct completed form (see ``docs/agent-workflow.md``).

Everything here is deterministic, dependency-light, and PDF-free. It reuses
the engine and the test helpers rather than re-deriving anything:

    tests/helpers.py   -> recipe_dispatch, mapping_forms, sample_case,
                          recipe_output, mapping_values, has_pdf
    tools/preflight.py -> preflight_case
    tools/find_forms   -> find_forms
"""
from __future__ import annotations

import datetime
import functools
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
FORMS = REPO / "forms"

# tests/helpers.py is the single source of truth for "how do I fill form X
# without a PDF". Import it rather than reimplementing the engine plumbing.
sys.path.insert(0, str(REPO / "tests"))
import helpers  # noqa: E402

# Strict catalog id contract (also the audit's form_id-validator pattern).
FORM_ID_RE = r"^[A-Z]+(?:-[A-Z0-9]+)+$"


@functools.lru_cache(maxsize=1)
def all_mappings() -> dict[str, dict]:
    """{form_id: parsed mapping.json} for every form."""
    out: dict[str, dict] = {}
    for mp in sorted(FORMS.glob("*/mapping.json")):
        m = json.loads(mp.read_text())
        out[m["form_id"]] = m
    return out


def status_of(form_id: str) -> str:
    return all_mappings().get(form_id, {}).get("status", "unknown")


def is_recipe(form_id: str) -> bool:
    return form_id in helpers.recipe_dispatch()


def fillable_forms() -> list[str]:
    """Every form that *should* produce content: recipe-tier or mapping-tier
    (non-empty map) with a committed sample case. Excludes
    ``no-mappable-fields``."""
    seen: set[str] = set()
    out: list[str] = []
    for fid in helpers.recipe_dispatch():
        if (FORMS / fid / "examples" / "sample_case.json").exists():
            seen.add(fid)
            out.append(fid)
    for fid in helpers.mapping_forms():
        if fid not in seen:
            out.append(fid)
    return sorted(out)


def filled_kv(form_id: str) -> dict:
    """field_id -> resolved value for any fillable form (PDF-free).

    Recipe-tier goes through the recipe; mapping-tier through resolve_mapping.
    """
    if is_recipe(form_id):
        return helpers.recipe_output(form_id)
    return helpers.mapping_values(form_id)


# --- determinism normalization ------------------------------------------
# ``today()`` mappings stamp the run date, which would churn goldens daily.
# Normalize the current date (both rendered formats) to a stable token so a
# golden captures "this field is today's date" without pinning the date.
_TODAY = datetime.date.today()
_TODAY_TOKENS = {
    _TODAY.strftime("%m/%d/%Y"): "<TODAY:mm/dd/yyyy>",
    _TODAY.strftime("%-m/%-d/%Y"): "<TODAY:m/d/yyyy>",
    _TODAY.strftime("%Y-%m-%d"): "<TODAY:iso>",
}


def normalize(kv: dict) -> dict:
    """Replace any value equal to today's date with a stable token."""
    out = {}
    for k, v in kv.items():
        out[k] = _TODAY_TOKENS.get(v, v) if isinstance(v, str) else v
    return out
