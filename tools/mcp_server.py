#!/usr/bin/env python3
"""MCP server exposing the Maine court-forms library as agent tools.

Lets an agent (Claude Code / codex / any MCP client) go from a fact pattern to a
filled form by calling tools instead of reading docs:

  find_forms(query)            -> candidate forms + matter workflows
  get_form(form_id)            -> facts needed, mapping trust, field summary
  fill_form(form_id, facts)    -> fill from a canonical fact object -> PDF path

Run:  python3 tools/mcp_server.py        (stdio MCP server)
Register in Claude Code:  claude mcp add maine-court-forms -- python3 tools/mcp_server.py

NOT legal advice. Filled output must be verified against the official form; the
tools surface each form's mapping trust tier and any unresolved/missing facts.
"""
from __future__ import annotations

import json
import pathlib
import ssl
import sys
import urllib.request

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from mcp.server.fastmcp import FastMCP  # noqa: E402
from engine.fill_and_audit import fill_one  # noqa: E402
from engine.fill_via_mapping import fill_via_mapping  # noqa: E402
from engine.canonical import is_canonical, to_engine_case  # noqa: E402
from tools.find_forms import find_forms as _find_forms  # noqa: E402

OSS_ROOT = pathlib.Path(__file__).resolve().parent.parent
mcp = FastMCP("maine-court-forms")


def _ensure_pdf(form_id: str) -> str | None:
    """Fetch the blank PDF from the manifest if it isn't on disk. Returns error or None."""
    pdf = OSS_ROOT / "forms" / form_id / f"{form_id}.pdf"
    if pdf.exists():
        return None
    manifest = json.loads((OSS_ROOT / "catalog" / "pdf_manifest.json").read_text())
    entry = manifest.get("forms", {}).get(form_id)
    if not entry:
        return f"no PDF and no manifest entry for {form_id}"
    try:
        req = urllib.request.Request(entry["url"], headers={"User-Agent": "mcf-mcp"})
        data = urllib.request.urlopen(req, timeout=30,
                                      context=ssl.create_default_context()).read()
        if data[:5] != b"%PDF-":
            return "fetched file is not a PDF"
        pdf.write_bytes(data)
        return None
    except Exception as e:  # noqa: BLE001
        return f"fetch failed: {e}"


def _trust_tier(status: str | None) -> str:
    """Map a mapping.json status to the trust tier surfaced to agents."""
    if status == "recipe":
        return "recipe"
    if status in ("verified", "opus-adjudicated"):
        return "reviewed"
    if status == "no-mappable-fields":
        return "not-fillable"
    return "draft — verify the filled output"


@mcp.tool()
def find_forms(query: str) -> dict:
    """Route a fact pattern / matter description to candidate Maine court forms.

    Args:
        query: plain-language situation, e.g. "evict tenant for nonpayment" or
               "divorce with two minor children".
    Returns matching matter `workflows` (ordered form sequences) and top `forms`.
    """
    return _find_forms(query)


@mcp.tool()
def get_form(form_id: str) -> dict:
    """What an agent needs to fill one form: trust tier, facts needed, field summary.

    Args:
        form_id: e.g. "AD-001".
    """
    fdir = OSS_ROOT / "forms" / form_id
    if not fdir.exists():
        return {"error": f"unknown form {form_id}"}
    import yaml
    meta = yaml.safe_load((fdir / "form.yaml").read_text()) or {}
    mp = json.loads((fdir / "mapping.json").read_text())
    schema = json.loads((fdir / "schema.json").read_text())
    canonical_keys = sorted(set((mp.get("map") or {}).values()))
    return {
        "form_id": form_id,
        "title": meta.get("title"),
        "category": meta.get("category"),
        "court": meta.get("court"),
        "n_fields": schema.get("n_fields") or len(schema.get("fields", [])),
        "mapping_status": mp.get("status"),
        # Shipped mapping.json statuses: verified (render-verified mapping),
        # recipe (form-specific engine code), opus-adjudicated (model-
        # adjudicated mapping), no-mappable-fields (nothing to fill).
        "trust": _trust_tier(mp.get("status")),
        "canonical_keys_used": canonical_keys,
        "skill": (fdir / "SKILL.md").read_text()[:4000] if (fdir / "SKILL.md").exists() else "",
        "sample_case": json.loads((fdir / "examples" / "sample_case.json").read_text()),
    }


@mcp.tool()
def fill_form(form_id: str, facts: dict, out_dir: str = "/tmp/mcf_fill") -> dict:
    """Fill a form from a canonical fact object and return the filled-PDF path.

    Args:
        form_id: e.g. "AD-001".
        facts: a canonical fact object — {matter, parties, party, facts} (see
               get_form's sample_case). An engine-shape case is also accepted.
        out_dir: where to write the filled PDF.
    Returns ok, out_pdf, fields written, and the mapping trust tier to surface.
    """
    fdir = OSS_ROOT / "forms" / form_id
    if not fdir.exists():
        return {"ok": False, "error": f"unknown form {form_id}"}
    err = _ensure_pdf(form_id)
    if err:
        return {"ok": False, "error": err}
    status = json.loads((fdir / "mapping.json").read_text()).get("status")
    if status == "recipe":
        # authoritative engine recipe — runs the form-specific fill logic
        case = to_engine_case(facts) if is_canonical(facts) else facts
        res = fill_one(form_id, case, pathlib.Path(out_dir),
                       schema_path=fdir / "schema.json",
                       pdf_path=fdir / f"{form_id}.pdf")
    else:
        # use the curated mapping.json (verified / opus-adjudicated) directly
        res = fill_via_mapping(form_id, facts, pathlib.Path(out_dir))
    res["mapping_status"] = status
    res["trust"] = _trust_tier(status)
    res["caveat"] = ("Verify against the official form."
                     if status in ("recipe", "verified", "opus-adjudicated")
                     else "Mapping is an un-audited draft — check field "
                          "placement and fill in any unresolved facts.")
    return res


if __name__ == "__main__":
    mcp.run()
