"""Shared helpers for the fill-engine test suite.

Deterministic, dependency-light (stdlib unittest + the engine itself). The
recipe/mapping checks are PDF-FREE — they run `map_form` + the recipe, or
`resolve_mapping`, against each form's committed schema.json + sample case, so
they run in CI without the (unshipped) blank PDFs. PDF-dependent checks live in
their own modules and skip when the blank is absent.
"""
from __future__ import annotations

import functools
import importlib
import json
import pathlib

REPO = pathlib.Path(__file__).resolve().parent.parent
FORMS = REPO / "forms"


@functools.lru_cache(maxsize=1)
def recipe_dispatch() -> dict:
    """{form_id: recipe_module_name} from the engine's RECIPE3 table."""
    fa = importlib.import_module("engine.fill_and_audit")
    return dict(fa.RECIPE3)


@functools.lru_cache(maxsize=1)
def mapping_forms() -> list[str]:
    """Mapping-tier forms (non-recipe, non-empty map) with a sample case."""
    out = []
    for mp in sorted(FORMS.glob("*/mapping.json")):
        m = json.loads(mp.read_text())
        fid = m["form_id"]
        if m.get("status") == "recipe" or not m.get("map"):
            continue
        if (FORMS / fid / "examples" / "sample_case.json").exists():
            out.append(fid)
    return out


def sample_case(form_id: str) -> dict | None:
    p = FORMS / form_id / "examples" / "sample_case.json"
    if not p.exists():
        return None
    from engine.canonical import is_canonical, to_engine_case
    c = json.loads(p.read_text())
    return to_engine_case(c) if is_canonical(c) else c


def schema(form_id: str) -> dict:
    return json.loads((FORMS / form_id / "schema.json").read_text())


def recipe_output(form_id: str) -> dict:
    """Run the form's recipe over its sample case; return the filled kv dict.

    PDF-free: builds the kv map from schema + case, then runs `process`.
    """
    from engine.build_kv_map import map_form
    case = sample_case(form_id)
    if case is None:
        raise RuntimeError(f"{form_id}: no sample_case.json")
    kv, _ = map_form(schema(form_id), case)
    mod_name = recipe_dispatch()[form_id]
    mod = importlib.import_module(f"engine.recipes.{mod_name}")
    out, _changes = mod.process(kv, case)
    return out


def mapping_values(form_id: str) -> dict:
    """field_id -> resolved value for a mapping-tier form (PDF-free)."""
    from engine.fill_via_mapping import resolve_mapping
    res = resolve_mapping(form_id, sample_case(form_id))
    return res.get("fid_value", {})


def pdf_path(form_id: str) -> pathlib.Path:
    return FORMS / form_id / f"{form_id}.pdf"


def has_pdf(form_id: str) -> bool:
    return pdf_path(form_id).exists()
