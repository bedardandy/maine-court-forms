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

import hashlib
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


def _ensure_pdf(form_id: str) -> tuple[str | None, str]:
    """Fetch the blank PDF from the manifest if it isn't on disk.

    Returns (error, pdf_verify) — error is None on success; pdf_verify is the
    SHA-256 verdict against catalog/pdf_manifest.json ("match",
    "mismatch — upstream form may have been revised", "no-manifest-hash",
    or "on-disk — not re-verified here" for pre-existing blanks, which
    engine.verify.guard_blank checks at fill time).
    """
    pdf = OSS_ROOT / "forms" / form_id / f"{form_id}.pdf"
    if pdf.exists():
        return None, "on-disk — not re-verified here"
    manifest = json.loads((OSS_ROOT / "catalog" / "pdf_manifest.json").read_text())
    entry = manifest.get("forms", {}).get(form_id)
    if not entry:
        return f"no PDF and no manifest entry for {form_id}", "no-manifest-entry"
    try:
        req = urllib.request.Request(entry["url"], headers={"User-Agent": "mcf-mcp"})
        data = urllib.request.urlopen(req, timeout=30,
                                      context=ssl.create_default_context()).read()
        if data[:5] != b"%PDF-":
            return "fetched file is not a PDF", "not-a-pdf"
        expected = entry.get("sha256")
        got = hashlib.sha256(data).hexdigest()
        if not expected:
            verdict = "no-manifest-hash"
        elif got == expected:
            verdict = "match"
        else:
            verdict = (f"mismatch — upstream form may have been revised "
                        f"(manifest {expected[:12]}…, fetched {got[:12]}…)")
        pdf.write_bytes(data)
        return None, verdict
    except Exception as e:  # noqa: BLE001
        return f"fetch failed: {e}", "fetch-failed"


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
        # Targeted-intake declaration (tools/derive_required_facts.py):
        # facts.required = caption facts the form is facially incomplete
        # without; facts.used = every canonical key the fill can consume.
        "facts": mp.get("facts") or {"required": [], "used": canonical_keys},
        "skill": (fdir / "SKILL.md").read_text()[:4000] if (fdir / "SKILL.md").exists() else "",
        "sample_case": json.loads((fdir / "examples" / "sample_case.json").read_text()),
    }


@mcp.tool()
def fill_form(form_id: str, facts: dict, out_dir: str = "/tmp/mcf_fill") -> dict:
    """Fill a form from a canonical fact object and return the filled-PDF path.

    Args:
        form_id: e.g. "AD-001".
        facts: a canonical fact object — {matter, parties, party, facts} (see
               get_form's sample_case). An engine-shape case is accepted only
               for recipe-tier forms; the mapping path rejects it.
        out_dir: where to write the filled PDF.
    Returns ok, out_pdf, fields written, and the mapping trust tier to surface.
    """
    fdir = OSS_ROOT / "forms" / form_id
    if not fdir.exists():
        return {"ok": False, "error": f"unknown form {form_id}"}
    err, pdf_verify = _ensure_pdf(form_id)
    if err:
        return {"ok": False, "error": err, "pdf_verify": pdf_verify}
    status = json.loads((fdir / "mapping.json").read_text()).get("status")
    if status == "recipe":
        # authoritative engine recipe — runs the form-specific fill logic
        case = to_engine_case(facts) if is_canonical(facts) else facts
        res = fill_one(form_id, case, pathlib.Path(out_dir),
                       schema_path=fdir / "schema.json",
                       pdf_path=fdir / f"{form_id}.pdf")
    else:
        # The mapping path resolves CANONICAL keys (matter.* / parties.* /
        # facts.*). An engine-shape case (top-level court/docket_no/...)
        # would resolve almost nothing and produce a near-blank fill —
        # reject it with a clear error instead.
        engine_markers = {"court", "docket_no", "event_date", "filing_date",
                           "case_id", "citation_no"} & set(facts)
        if engine_markers and "matter" not in facts:
            return {"ok": False, "pdf_verify": pdf_verify,
                    "error": ("facts look engine-shape (top-level "
                              f"{sorted(engine_markers)}); the mapping fill "
                              "path needs the canonical fact object "
                              "({matter, parties, party, facts} — see "
                              "get_form's sample_case). Engine-shape cases "
                              "are only accepted for recipe-tier forms.")}
        # use the curated mapping.json (verified / opus-adjudicated) directly
        res = fill_via_mapping(form_id, facts, pathlib.Path(out_dir))
    # Deterministic post-fill verify: reopen the filled PDF and diff the
    # widget values against the intended fid->value map (engine/verify_fill).
    if res.get("ok") and res.get("out_pdf"):
        try:
            from engine.verify_fill import verify_fill as _verify_fill
            if status == "recipe":
                kv_art = pathlib.Path(out_dir) / f"{form_id}.kv.json"
                intended = (json.loads(kv_art.read_text()).get("kv", {})
                            if kv_art.exists() else {})
            else:
                from engine.fill_via_mapping import resolve_mapping
                intended = resolve_mapping(form_id, facts).get("fid_value", {})
            if intended:
                schema = json.loads((fdir / "schema.json").read_text())
                vres = _verify_fill(res["out_pdf"], intended, schema)
                res["fill_verify"] = {"ok": vres["ok"], **vres["summary"]}
        except Exception as e:  # noqa: BLE001 — verify must not block the fill
            res["fill_verify"] = {"ok": None, "error": f"{type(e).__name__}: {e}"}
    res["pdf_verify"] = pdf_verify
    res["mapping_status"] = status
    res["trust"] = _trust_tier(status)
    res["caveat"] = ("Verify against the official form."
                     if status in ("recipe", "verified", "opus-adjudicated")
                     else "Mapping is an un-audited draft — check field "
                          "placement and fill in any unresolved facts.")
    return res


if __name__ == "__main__":
    mcp.run()
