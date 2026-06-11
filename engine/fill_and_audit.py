"""End-to-end driver: case + form → filled PDF → Opus 4.7 vision audit.

Usage:
    python3 scripts/fill_and_audit.py --form FM-008
    python3 scripts/fill_and_audit.py --form FM-008 --case-json /tmp/c.json
    python3 scripts/fill_and_audit.py --form-list FM-008,CV-001,CR-002
"""
from __future__ import annotations

import argparse
import csv
import datetime
import json
import os
import pathlib
import subprocess
import sys

# Make scripts/* importable as scripts.<name>
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from .build_kv_map import map_form
from .case_template import (
    sample_family_matters_case, sample_civil_case,
    sample_guardianship_case, pick_sample_case_for)
from .form_filler import fill_form_from_json, fill_form


REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
PDF_ROOT = pathlib.Path(os.environ.get("PDF_ROOT", "pdfs"))


def pick_sample_case(form_id: str) -> dict:
    return pick_sample_case_for(form_id).to_dict()


# Form-specific (recipe-3) inference registry.
# Each entry: form_id → module name in scripts/infer_<form>_*.py
RECIPE3 = {
    "CR-003":    "infer_cr004_bail_bond",
    "CR-004":    "infer_cr004_bail_bond",
    "CR-011":    "infer_cr_community_service",
    "NC-001":    "infer_nc001_name_change",
    "FM-040-A":  "infer_fm040a_child_support",
    "MJ-007":    "infer_mj007_wage_garnishment",
    "FDP-002A":  "infer_fdp002a_mortgage",
    "FDP-003":   "infer_fdp_family",
    "FDP-004":   "infer_fdp_family",
    "FDP-010":   "infer_fdp_family",
    "MJBVB-010": "infer_mjbvb010_motion_continue",
    "CV-037":    "infer_cv037_subpoena",
    # Small claims judgment-debtor family — one script, 3 forms
    "MJ-SC-001": "infer_mj_sc_judgment",
    "MJ-SC-005": "infer_mj_sc_judgment",
    "MJ-SC-012": "infer_mj_sc_judgment",
    # Protection from Abuse family
    "PA-005":    "infer_pa_family",
    "PA-010":    "infer_pa010_motion_dissolve",
    "PA-015":    "infer_pa015_keep_info_private",
    "PA-024":    "infer_pa_family",
    # Adoption family
    "AD-003":    "infer_ad_family",
    "AD-004":    "infer_ad_family",
    "AD-006":    "infer_ad_family",
    "AD-017":    "infer_ad_family",
    "AD-022":    "infer_ad_family",
    "AD-029":    "infer_ad_family",
    "AD-030":    "infer_ad_family",
    "AD-032":    "infer_ad_family",
    "BCCP-2010": "infer_bccp_family",
    "BCCP-2021": "infer_bccp_family",
    # ADA accommodation request family
    "OTH-011":   "infer_oth_disability_request",
    "OTH-012":   "infer_oth_disability_request",
    "OTH-085":   "infer_oth085_limited_appearance",
    # JV family (juvenile court)
    "JV-006-W":  "infer_jv_family",
    "JV-012":    "infer_jv012_notice_appeal",
    "JV-017":    "infer_jv_family",
    "JV-022":    "infer_jv_family",
    "JV-040":    "infer_jv_family",
    "JV-041":    "infer_jv_family",
    "JV-043":    "infer_jv_family",
    "JV-044":    "infer_jv_family",
    # CR community-service / drug-court family
    "CR-198":    "infer_cr_community_service",
    "CR-239":    "infer_cr_community_service",
    # FM admit/deny answer family — FM-227 reclaimed as grandparent
    # visitation response, FM-233 reclaimed as de facto parentage response
    "FM-227":    "infer_fm227_grandparent",
    "FM-233":    "infer_fm233_defacto",
    # FM general family (self-id + magistrate-objection + property)
    # FM-056 reclaimed as dedicated Certificate of Real Estate script
    "FM-056":    "infer_fm056_real_estate",
    "FM-057":    "infer_fm057_keep_info_private",
    "FM-071":    "infer_fm_general",
    "FM-171":    "infer_fm_general",
    "FM-188":    "infer_fm_general",
    "FM-214":    "infer_fm_general",
    # Extend JV family to JV-034, JV-047
    "JV-034":    "infer_jv_family",
    "JV-047":    "infer_jv_family",
    # OTH-015 — language-access form (its own dedicated script)
    "OTH-015":   "infer_oth015_language_access",
    "OTH-133":   "infer_oth133_mediator",
    # OTH interpreter reimbursement family
    "OTH-017":   "infer_oth_interpreter",
    "OTH-131":   "infer_oth_interpreter",
    # GS guardianship family — consent/objection/nomination + minor's consent
    "GS-008":    "infer_gs_family",
    "GS-012":    "infer_gs_family",
    "GS-021":    "infer_gs_family",
    # MJ judgment-debtor disclosure family (MJ-007 stays on its own)
    "MJ-005":    "infer_mj_debtor_disclosure",
    "MJ-009":    "infer_mj_debtor_disclosure",
    "MJ-014":    "infer_mj_debtor_disclosure",
    "MJ-015":    "infer_mj_debtor_disclosure",
    # Extend PA family — PA-025 (relinquished firearms), PA-033 (foreign order)
    "PA-025":    "infer_pa_family",
    "PA-033":    "infer_pa_family",
    # PC (Probate Court / CHIPS) — judicial review + ICWA affidavit
    "PC-034":    "infer_pc_family",
    "PC-044":    "infer_pc_family",
    # MJBVB family — civil violation amendment + fine extension request
    # (MJBVB-010 motion-to-continue keeps its own script)
    "MJBVB-009": "infer_mjbvb_family",
    "MJBVB-017": "infer_mjbvb_family",
}

# (Probate-side AD-007 dispatch lives in probate-forms/scripts/recursive_eval_loop.py
#  — separate repo)



def _apply_recipe3(form_id: str, kv: dict, case: dict) -> tuple[dict, list]:
    mod_name = RECIPE3.get(form_id)
    if not mod_name: return kv, []
    import importlib
    try:
        mod = importlib.import_module(f"engine.recipes.{mod_name}")
        return mod.process(kv, case)
    except Exception as e:
        print(f"  recipe-3 {mod_name} error: {e}")
        return kv, []


# Notary-jurat widget names that recur across many forms. The systemic
# pass fills these last so individual recipe-3 scripts don't each have
# to remember every variant.
_NOTARY_COUNTY_FIDS = (
    "county", "county_1", "county_2", "county_3",
    "state_of_maine_county", "state_of_maine_ss_county",
)
_NOTARY_STATE_FIDS = (
    "state_of", "state_of_maine",
)
_NOTARY_SIGNER_FIDS = (
    "personally_appeared_the_above_named",
    "personally_appeared_the_above_named_petitioner",
    "personally_appeared_the_above_named_plaintiff",
    "personally_appeared_the_above_named_defendant",
    "personally_appeared_the_above_named_respondent",
    "personally_appeared_the_abovenamed_consenting_parent",
)
# "I swear under penalty of perjury..." radio appears in dozens of forms
# with slight suffix variants. Checked ONLY on an explicit
# case.facts.perjury_acknowledged boolean — never auto-sworn.
_PERJURY_SWEAR_FIDS = (
    "i_swear_under_penalty_of_perjury_that_the_above_statements_are_true_and_correct_i_understand_that_these",
    "i_swear_under_penalty_of_perjury_that_the_above_statements_are_true_and_correct_i_understand_that_these_statements",
    "i_swear_under_penalty_of_perjury_that_the_above_statements_are_true_and_correct_i_understand_that_these_statements_are",
    "i_swearunderpenaltyofperjurythattheabove_statementsaretrueandcorrect_i_understandthatthese",
)


def _apply_notary_block(kv: dict, case: dict) -> int:
    """Fill notary-jurat widgets (county / state / personally appeared)
    on any form that has them but didn't get them filled by recipe-3.
    Returns count of fills added."""
    court = case.get("court") or {}
    parties = case.get("parties") or {}
    facts = case.get("facts") or {}
    # Jurat county ONLY from real case data (was defaulted "Cumberland",
    # fabricating where the oath was taken). Unknown -> leave blank for
    # the notary to complete.
    county = (case.get("notary_county")
              or court.get("county", ""))
    state = "Maine"
    # Best-guess signer: first available party with a name.
    signer = ""
    for role in ("petitioner", "plaintiff", "defendant", "respondent",
                  "applicant", "parent"):
        p = parties.get(role) or {}
        if p.get("full_name"):
            signer = p["full_name"]
            break
    added = 0
    for fid in _NOTARY_COUNTY_FIDS:
        if fid in kv and not kv.get(fid) and county:
            kv[fid] = county
            added += 1
    for fid in _NOTARY_STATE_FIDS:
        if fid in kv and not kv.get(fid):
            kv[fid] = state
            added += 1
    for fid in _NOTARY_SIGNER_FIDS:
        if fid in kv and not kv.get(fid) and signer:
            kv[fid] = signer
            added += 1
    # The perjury oath belongs to the signer; check it ONLY when the
    # case explicitly says so (was auto-checked on every form that had
    # the box).
    if facts.get("perjury_acknowledged") is True:
        for fid in _PERJURY_SWEAR_FIDS:
            if fid in kv and not kv.get(fid):
                kv[fid] = "X"
                added += 1
    return added


def fill_one(form_id: str, case: dict, out_dir: pathlib.Path,
             schema_path: pathlib.Path | None = None,
             pdf_path: pathlib.Path | None = None) -> dict:
    # Paths default to this repo's form-by-form layout; callers (e.g. the
    # engine/fill.py entrypoint) can also pass schema.json / blank PDF
    # explicitly.
    schema_path = schema_path or (REPO_ROOT / "forms" / form_id
                                  / "schema.json")
    if not schema_path.exists():
        return {"form_id": form_id, "ok": False, "error": "no schema"}
    schema = json.loads(schema_path.read_text())
    pdf_path = pdf_path or (PDF_ROOT / schema["source_pdf"])
    if not pdf_path.exists():
        return {"form_id": form_id, "ok": False,
                "error": f"PDF not found: {pdf_path}"}

    # Computed facts (computations.json next to schema.json; see
    # maine_forms_engine.computations). Recipe-tier forms have pointer-only
    # mappings, so the mapped computations routing (fill_via_mapping) never
    # sees them — the facts-only evaluator runs here instead: a target the
    # case OMITS whose inputs are all present is computed from the form's
    # printed arithmetic and merged into the case BEFORE the recipe runs;
    # a supplied target is never overridden, a contradiction only yields a
    # COMPUTATION_MISMATCH warning. The result/kv-artifact keys
    # (computed_fields / computation_warnings / computation_notes) match
    # the mapped path so harness consumers see one shape. A malformed
    # computations.json (bad op / cycle) raises, same as the mapped path.
    _comp_extra: dict = {}
    try:
        from maine_forms_engine.computations import (
            evaluate as _eval_computations,
            load_computations as _load_computations)
    except ImportError:  # engine without the computations layer
        _computations = None
    else:
        _computations = _load_computations(schema_path.parent)
    if _computations is not None:
        _comp = _eval_computations(_computations, case)
        if _comp["computed"]:
            # Never mutate the caller's case (it may be reused across forms).
            case = dict(case)
            for e in _comp["computed"]:
                key, val = e["key"], e["value"]
                case[key] = val  # flat key — engine lookups resolve flat first
                head, _, rest = key.partition(".")
                if rest and isinstance(case.get(head), dict):
                    sub = dict(case[head])
                    sub[rest] = val
                    case[head] = sub  # nested — recipes read case["facts"][...]
        _comp_extra["computed_fields"] = _comp["computed"]
        _comp_extra["computation_warnings"] = _comp["warnings"]
        if _comp["notes"]:
            _comp_extra["computation_notes"] = _comp["notes"]

    kv, stats = map_form(schema, case)
    # Apply form-specific recipe-3 inference if registered
    kv, recipe3_changes = _apply_recipe3(form_id, kv, case)
    # Coerce all values to strings — Qwen-generated cases may have
    # ints/floats/lists/dicts which PyMuPDF's pdf_set_field_value
    # rejects (needs char const *).
    for k, v in list(kv.items()):
        if v is None:
            kv[k] = ""
        elif not isinstance(v, str):
            try:
                kv[k] = json.dumps(v) if isinstance(v, (list, dict)) else str(v)
            except Exception:
                kv[k] = str(v)
    # Systemic ISO-timestamp strip: any value that looks like a full
    # ISO timestamp ("2024-03-15T09:30:00Z") gets reduced to the date
    # part. This catches recipe-3 scripts that pass case.event_date /
    # case.filing_date directly to a "date" widget without conversion.
    for k, v in list(kv.items()):
        if isinstance(v, str) and len(v) >= 19 and v[4] == "-" and v[7] == "-" and v[10] == "T":
            kv[k] = v[:10]
    if recipe3_changes:
        stats["recipe3_applied"] = len(recipe3_changes)
        stats["filled"] += sum(1 for f, v, _s in recipe3_changes if v)

    # Post-recipe-3: propagate values to _dup1/_dup2 siblings (so a
    # recipe-3 script that writes `line_16` populates `line_16_dup1` etc.).
    dup_extra = 0
    for fid in list(kv):
        if "_dup" in fid or not kv.get(fid): continue
        for suffix in ("_dup1", "_dup2", "_dup3", "_dup4"):
            dup_fid = fid + suffix
            if dup_fid in kv and not kv[dup_fid]:
                kv[dup_fid] = kv[fid]
                dup_extra += 1
    if dup_extra:
        stats["dup_propagated_post_recipe3"] = dup_extra
        stats["filled"] += dup_extra

    # Systemic notary-jurat fill — county / state / personally appeared
    notary_added = _apply_notary_block(kv, case)
    if notary_added:
        stats["notary_block_fills"] = notary_added
        stats["filled"] += notary_added

    # Systemic width-fit pass (surfaced by the Qwen edge-case probe:
    # widget_width was the #1 limitation at 98 majors). For any value
    # that OVERFLOWS its widget's char budget, fit it:
    #   - person names -> initial-collapse (never truncate a legal name)
    #   - addresses    -> postal abbreviation
    # Conservative: only touches values that actually overflow, so
    # Opus-validated fills with normal-length values are untouched.
    from .text_fit import fit as _fit, widget_char_budget
    party_names = {(p.get("full_name") or "").strip()
                   for p in (case.get("parties") or {}).values()
                   if isinstance(p, dict) and p.get("full_name")}
    def _is_name_field(f: dict) -> bool:
        if f.get("category") != "party_attr":
            return False
        if (f.get("subcategory") or "") in (
                "address", "phone", "email", "dob", "docket_no",
                "county", "bar_number"):
            return False
        # Exclude date/DOB/number widgets by field_id token, so a
        # date value never gets name-collapsed even if it slips the
        # digit guard.
        fl = f["field_id"].lower()
        if any(t in fl for t in ("date", "dob", "birth", "_no",
                                  "number", "zip", "amount", "phone")):
            return False
        return True

    name_fids = {f["field_id"] for f in schema["fields"]
                 if _is_name_field(f)}
    rect_by_fid = {f["field_id"]: f.get("rect") for f in schema["fields"]}
    width_fits = 0
    for fid, v in list(kv.items()):
        if not isinstance(v, str) or not v:
            continue
        rect = rect_by_fid.get(fid)
        if not rect:
            continue
        budget = widget_char_budget(rect)
        if len(v) <= budget:
            continue
        is_name = (v.strip() in party_names) or (fid in name_fids
                                                 and not any(ch.isdigit()
                                                             for ch in v))
        # Address widgets aren't always named "address" — also catch
        # legal_residence / mailing / residence (Opus adjudication
        # confirmed AD-030/AD-022 "Legal Residence" truncations).
        fl = fid.lower()
        is_addr = any(t in fl for t in ("address", "legal_residence",
                                         "mailing", "residence", "street"))
        if is_name:
            nv = _fit(v, budget, name=True)
        elif is_addr:
            nv = _fit(v, budget, address=True)
        else:
            continue  # leave narrative/other to recipe-specific handling
        if nv != v:
            kv[fid] = nv
            width_fits += 1
    if width_fits:
        stats["width_fits"] = width_fits
    # Translate field_id (snake_case) back to the raw PDF widget name
    # since form_filler keys by PDF widget name. Some schemas have
    # duplicate field_ids (e.g. GS-021 "interim" appears twice, once as
    # a radio button and once as a body checkbox) — both widgets must
    # receive the value, so build a multimap and fan out.
    fid_to_widgets: dict[str, list[str]] = {}
    for f in schema["fields"]:
        fid_to_widgets.setdefault(f["field_id"], []).append(f["label"])
    field_data: dict[str, str] = {}
    for fid, v in kv.items():
        if not v or fid not in fid_to_widgets:
            continue
        for widget_label in fid_to_widgets[fid]:
            field_data[widget_label] = v
    if any(len(labels) > 1 for labels in fid_to_widgets.values()):
        stats["dup_field_id_fanout"] = sum(
            len(labels) - 1
            for fid, labels in fid_to_widgets.items()
            if len(labels) > 1 and kv.get(fid))

    # Yellow light — declarative paradox constraints (constraints.json next
    # to schema.json; keys are schema field_ids, evaluated against the
    # resolved kv). Warnings only: they never block or alter the fill, and
    # no constraints file means no report key at all.
    constraint_warnings = None
    try:
        from maine_forms_engine.constraints import (
            evaluate as _eval_constraints, load_constraints as _load_constraints)
        _cons = _load_constraints(schema_path.parent)
        if _cons is not None:
            constraint_warnings = _eval_constraints(_cons, kv)
    except Exception:  # noqa: BLE001 — diagnostics must never break a fill
        pass

    out_dir.mkdir(parents=True, exist_ok=True)
    out_pdf = out_dir / f"{form_id}.filled.pdf"
    fill_form(str(pdf_path), field_data, str(out_pdf),
              form_id=form_id, addendum_policy="none")

    # Also write the kv + stats artifact
    kv_artifact = {
        "form_id": form_id, "case_id": case.get("case_id"),
        "kv": kv, "stats": stats,
        "fields_written_to_pdf": len(field_data),
    }
    if constraint_warnings is not None:
        kv_artifact["constraint_warnings"] = constraint_warnings
    kv_artifact.update(_comp_extra)
    (out_dir / f"{form_id}.kv.json").write_text(json.dumps(kv_artifact,
                                                           indent=2))
    res = {"form_id": form_id, "ok": True, "out_pdf": str(out_pdf),
           "stats": stats,
           "fields_written_to_pdf": len(field_data),
           **_comp_extra}
    if constraint_warnings is not None:
        res["constraint_warnings"] = constraint_warnings
    return res


def _parse_audit_json(content: str) -> dict:
    """Extract the {alignment_ok, issues[]} object from a model reply."""
    content = content.strip()
    if content.startswith("```"):
        content = content.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    start, end = content.find("{"), content.rfind("}")
    try:
        if start != -1:
            return json.loads(content[start:end+1])
    except json.JSONDecodeError:
        pass
    return {"alignment_ok": None, "issues": [], "raw": content[:200]}


def _audit_page_once(img_path: pathlib.Path, prompt_template: str,
                       env: dict) -> dict:
    """Run Opus 4.7 vision audit on one image. Returns parsed dict
    with {alignment_ok, issues, raw}."""
    prompt = prompt_template.replace("{IMAGE_PATH}", str(img_path))
    cmd = ["claude", "-p", prompt, "--model", "opus",
           "--allowedTools", "Read", "--output-format", "text"]
    r = subprocess.run(cmd, capture_output=True, text=True, env=env,
                        timeout=600)
    return _parse_audit_json(r.stdout.strip())


# Local VL endpoint(s), OpenAI-compatible /v1. Set MCF_LLM_ENDPOINTS to a
# comma-separated list of your own hosts; defaults to localhost.
LOCAL_VL_ENDPOINTS = os.environ.get(
    "MCF_LLM_ENDPOINTS", "http://localhost:8080/v1").split(",")
LOCAL_VL_MODEL = os.environ.get("LOCAL_VL_MODEL", "qwen3.6-27b")


def _audit_page_once_local(img_path: pathlib.Path, prompt_template: str,
                            env: dict, endpoint: str | None = None) -> dict:
    """Local Qwen-VL audit of one page image via llama.cpp-server.

    NB: per the qwen36 name-hallucination finding, this auditor is trusted
    for alignment/completeness verdicts (blank_required, wrong_position,
    wrong_column, truncated) but NOT for verifying exact name/number
    spelling — those need a character-by-character or Opus verify pass.
    """
    import base64
    import random
    import urllib.request

    ep = endpoint or random.choice(LOCAL_VL_ENDPOINTS)
    # Strip the Read-tool instruction; the image is sent inline instead.
    prompt = prompt_template.replace(
        "Use the Read tool to load the image at: {IMAGE_PATH}",
        "Audit the attached page image.").replace("{IMAGE_PATH}", "")
    b64 = base64.standard_b64encode(img_path.read_bytes()).decode("ascii")
    payload = {
        "model": LOCAL_VL_MODEL,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url",
                 "image_url": {"url": f"data:image/png;base64,{b64}"}},
            ],
        }],
        "temperature": 0.2, "max_tokens": 4096,
        "chat_template_kwargs": {"enable_thinking": False},
    }
    req = urllib.request.Request(
        f"{ep}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=900) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        content = body["choices"][0]["message"]["content"]
        return _parse_audit_json(content)
    except Exception as e:
        return {"alignment_ok": None, "issues": [],
                "raw": f"local-audit-error: {e}"}


def _consensus_merge(samples: list[dict], min_votes: int) -> dict:
    """Merge N audit samples for one page. An issue counts if its
    (kind, normalized-label-prefix) key appears in ≥min_votes samples.
    Surviving issues take the first sample's full record; per-issue
    vote count is recorded in `votes`. alignment_ok is True iff
    no surviving major issues."""
    from collections import defaultdict
    buckets: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for samp in samples:
        for iss in samp.get("issues") or []:
            kind = (iss.get("kind") or "").lower().strip()
            label = (iss.get("label") or "").lower().strip()[:30]
            buckets[(kind, label)].append(iss)
    merged = []
    for (kind, label), occurrences in buckets.items():
        if len(occurrences) >= min_votes:
            rep = dict(occurrences[0])
            rep["votes"] = f"{len(occurrences)}/{len(samples)}"
            merged.append(rep)
    has_major = any(i.get("severity") == "major" for i in merged)
    return {"alignment_ok": not has_major, "issues": merged,
            "n_samples": len(samples), "min_votes": min_votes}


def flatten_pdf(src_pdf: pathlib.Path, dst_pdf: pathlib.Path) -> pathlib.Path:
    """Bake AcroForm widget appearances into static page content so the
    rendered image is faithful to a printed copy (no live form fields).
    Returns dst_pdf. Uses PyMuPDF's widget→annotation conversion."""
    import fitz
    doc = fitz.open(str(src_pdf))
    for page in doc:
        # Ensure each widget has an up-to-date appearance stream, then
        # convert the form field to baked page content.
        w = page.first_widget
        while w:
            try:
                w.update()
            except Exception:
                pass
            w = w.next
    # bake_annots=True flattens widget/annotation appearances into content.
    doc.bake(annots=True, widgets=True)
    doc.save(str(dst_pdf), garbage=4, deflate=True)
    doc.close()
    return dst_pdf


def audit_one(form_id: str, filled_pdf: pathlib.Path,
              out_dir: pathlib.Path, *, repeats: int = 1,
              auditor: str = "opus", flatten: bool = False) -> dict:
    """Vision-audit a filled PDF. auditor='opus' uses Opus via the
    Claude CLI; auditor='local' uses a local Qwen-VL endpoint.
    With repeats>1, runs N audits per page in parallel and merges via
    majority-vote consensus on (kind, label) — denoises per-run variance.
    flatten=True bakes widgets into page content before rendering."""
    env = dict(os.environ)
    env.pop("ANTHROPIC_API_KEY", None)
    env.pop("ANTHROPIC_AUTH_TOKEN", None)
    from PIL import Image
    import fitz
    from concurrent.futures import ThreadPoolExecutor

    if flatten:
        flat = out_dir / f"{form_id}.flat.pdf"
        try:
            filled_pdf = flatten_pdf(filled_pdf, flat)
        except Exception as e:
            print(f"  flatten failed ({e}); rendering live widgets")

    audit_fn = (_audit_page_once_local if auditor == "local"
                else _audit_page_once)

    doc = fitz.open(str(filled_pdf))
    # Qwen follows the nuanced Opus exclusions worst (drives over-flagging),
    # so the local auditor gets a terser, conservative, exclusion-hammering
    # prompt variant.
    prompt_file = ("alignment_audit_qwen.md" if auditor == "local"
                   else "alignment_audit.md")
    prompt_path = REPO_ROOT / "prompts" / prompt_file
    if not prompt_path.exists():
        raise FileNotFoundError(
            f"vision-audit prompt not found: {prompt_path}. The prompts/ "
            "directory is not shipped in this repo — the audit step is "
            "optional research tooling. Run without --audit, or supply "
            f"prompts/{prompt_file} to enable it.")
    prompt_template = prompt_path.read_text()

    # Render each page once.
    img_paths = []
    for pno in range(doc.page_count):
        pix = doc[pno].get_pixmap(matrix=fitz.Matrix(200/72, 200/72))
        img_path = out_dir / f"{form_id}.p{pno+1}.png"
        pix.save(str(img_path))
        img = Image.open(img_path)
        if max(img.size) > 1600:
            scale = 1600 / max(img.size)
            img = img.resize(
                (int(img.size[0]*scale), int(img.size[1]*scale)),
                Image.LANCZOS)
            img.save(img_path)
        img_paths.append(img_path)
    n_pages = doc.page_count
    doc.close()

    repeats = max(1, repeats)
    min_votes = (repeats // 2) + 1  # strict majority for odd N; ⌈N/2⌉ for even

    # Run N audits per page (parallel across all page×sample tasks).
    page_results = []
    if repeats == 1:
        for img_path in img_paths:
            res = audit_fn(img_path, prompt_template, env)
            page_results.append({
                "page": int(img_path.stem.rsplit(".p",1)[-1]),
                **res})
    else:
        tasks = [(pno, sno, img_paths[pno])
                  for pno in range(n_pages)
                  for sno in range(repeats)]
        with ThreadPoolExecutor(max_workers=min(8, len(tasks))) as ex:
            futs = {ex.submit(audit_fn, t[2],
                                prompt_template, env): (t[0], t[1])
                     for t in tasks}
            per_page_samples: dict[int, list[dict]] = {
                p: [] for p in range(n_pages)}
            for fut, (pno, sno) in futs.items():
                per_page_samples[pno].append(fut.result())
        for pno in range(n_pages):
            merged = _consensus_merge(per_page_samples[pno], min_votes)
            page_results.append({"page": pno + 1,
                                  "samples": per_page_samples[pno],
                                  **merged})

    (out_dir / f"{form_id}.audit.json").write_text(json.dumps({
        "form_id": form_id, "repeats": repeats,
        "pages": page_results,
    }, indent=2))
    n_major = sum(len([i for i in p.get("issues", [])
                        if i.get("severity") == "major"])
                    for p in page_results)
    n_minor = sum(len([i for i in p.get("issues", [])
                        if i.get("severity") == "minor"])
                    for p in page_results)
    return {"form_id": form_id, "pages": n_pages,
            "major": n_major, "minor": n_minor, "repeats": repeats}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--form", help="Form ID (e.g., FM-008)")
    ap.add_argument("--form-list", help="Comma-separated form IDs")
    ap.add_argument("--case-json", type=pathlib.Path)
    ap.add_argument("--out-dir", type=pathlib.Path,
                    default=pathlib.Path("intermediate") /
                            datetime.datetime.utcnow().strftime("kv_%Y%m%dT%H%M%S"))
    ap.add_argument("--audit", action="store_true",
                    help="Also run the vision audit (opt-in: needs the "
                         "prompts/ templates, which are not shipped, plus "
                         "an Opus CLI or local VL endpoint)")
    ap.add_argument("--skip-audit", action="store_true",
                    help=argparse.SUPPRESS)  # legacy no-op; audit is opt-in
    ap.add_argument("--audit-repeats", type=int, default=1,
                    help="Run vision audit N times per page and "
                         "keep issues that appear in ⌈N/2⌉+ samples. "
                         "N=3 denoises ~±2-3 majors of audit variance.")
    ap.add_argument("--auditor", choices=["opus", "local"], default="opus",
                    help="opus=Claude vision (CLI); local=a local "
                         "Qwen-VL endpoint (free, alignment-only).")
    ap.add_argument("--flatten", action="store_true",
                    help="Bake widgets into page content before rendering "
                         "(faithful printed-form view).")
    args = ap.parse_args()

    if args.form_list:
        forms = [f.strip() for f in args.form_list.split(",")]
    elif args.form:
        forms = [args.form]
    else:
        print("Provide --form or --form-list", file=sys.stderr)
        return 1

    case = (json.loads(args.case_json.read_text())
            if args.case_json else None)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    summary_rows = []
    for form_id in forms:
        c = case or pick_sample_case(form_id)
        fill_result = fill_one(form_id, c, args.out_dir)
        if not fill_result["ok"]:
            summary_rows.append({"form_id": form_id, "ok": False,
                                  "error": fill_result.get("error")})
            continue
        row = {"form_id": form_id, "filled_ok": True,
                **{k: v for k, v in fill_result["stats"].items()
                   if k != "by_category_filled"},
                "fields_written_to_pdf": fill_result["fields_written_to_pdf"]}
        if args.audit and not args.skip_audit:
            audit = audit_one(form_id,
                              pathlib.Path(fill_result["out_pdf"]),
                              args.out_dir,
                              repeats=args.audit_repeats,
                              auditor=args.auditor,
                              flatten=args.flatten)
            row.update({"audit_pages": audit["pages"],
                        "audit_major": audit["major"],
                        "audit_minor": audit["minor"]})
        summary_rows.append(row)
        print(f"  {form_id}: filled={row.get('filled')}/{row['total_fields']}, "
              f"audit_major={row.get('audit_major','?')}")

    summary_path = args.out_dir / "summary.tsv"
    if summary_rows:
        cols = list(summary_rows[0].keys())
        with summary_path.open("w") as fh:
            w = csv.DictWriter(fh, fieldnames=cols, delimiter="\t",
                                 extrasaction="ignore")
            w.writeheader()
            for r in summary_rows: w.writerow(r)
        print(f"summary: {summary_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
