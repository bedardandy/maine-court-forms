#!/usr/bin/env python3
"""Phase 2: fill -> render -> CLUSTER consensus audit -> Opus adjudication.

This is the verification edge that phase 1 (tools/improve_loop.py) sets up: once
a form's mapping.json is `opus-reviewed`, we *fill* it from its canonical sample,
render the result, and check that the values actually land correctly. The local
Qwen-VL cluster does the recursive first pass (N-sample consensus audit, fanned
across your local VLM endpoint(s)); Opus — via the Claude CLI — only
adjudicates the forms the cluster flags.

Division of labor mirrors phase 1:
- local cluster (free, parallel): N audit samples per page, majority-voted so a
  finding survives only if a strict majority of samples agree (kills the audit
  variance the single-shot auditor emits — see the N-sample denoising work).
- Opus (serial, paced): sees the FILLED + marker-numbered page plus the consensus
  findings, confirms real problems, and returns mapping corrections in the same
  marker->key/UNMAP protocol as improve_loop. Truncation/overflow are layout
  defects (rect / text-fit), not mapping bugs, so they are recorded as
  `render_flags` for engine triage rather than "fixed" by changing a key.

Outcome per form:
- consensus audit clean  -> status `verified`.
- mismatch findings      -> Opus corrects the mapping, re-fill, re-audit (<= max-iters).
- residual render flags  -> stays `opus-reviewed`, flags written to the note + report.

    python3 tools/audit_loop.py --forms CV-067 --qwen-samples 5
    python3 tools/audit_loop.py --forms CV-067 --no-opus      # cluster pass only

Never demotes below opus-reviewed; never invents keys (validated against the
canonical contract). Needs the blank PDFs on disk and the local Qwen-VL cluster.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import datetime
import re
import subprocess
import sys
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor

import fitz  # PyMuPDF
import openai

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from engine.fill_via_mapping import fill_via_mapping  # noqa: E402
from tools.ai_map_forms import _key_ok  # noqa: E402
from tools.vision_map_forms import _render_marked, FILLABLE  # noqa: E402
from tools.vision_audit import (AUDIT_PROMPT, VL_ENDPOINTS, VL_MODEL,  # noqa: E402
                                MAX_PAGES, _vl_clients)
from tools.improve_loop import CONTRACT  # noqa: E402
from tools.label_key_lint import _key_family, EXCL as _FAM_EXCL  # noqa: E402


def _family_changes(orig: dict, new: dict) -> list[dict]:
    """Field_ids whose key changed to a DIFFERENT semantic family.

    The OTH-030-class regression: the Opus fix path, to clear a visual audit,
    remaps a box to a value of the wrong family (mailing-address -> phone,
    phone -> email). Such a value renders plausibly, so the gate can't see it.
    A change WITHIN a family (party.address -> parties.defendant.address) is
    routine party-attribution and not flagged; only a cross-family flip is.
    """
    out = []
    for fid_id, new_key in new.items():
        old_key = orig.get(fid_id)
        of, nf = _key_family(old_key), _key_family(new_key)
        if of in _FAM_EXCL and nf in _FAM_EXCL and of != nf:
            out.append({"field_id": fid_id, "old": old_key, "new": new_key,
                        "old_family": of, "new_family": nf})
    return out

OSS_ROOT = pathlib.Path(__file__).resolve().parent.parent
MISMATCH = "mismatched"          # the only key-fixable issue class
RENDER = ("truncated", "overflow")  # layout defects, not mapping bugs
# Opus adjudicator model (subscription via `claude -p`). Default 4.8; override
# with MCF_OPUS_MODEL. The interactive /model picker may not list 4.8, but the
# --model passthrough reaches it.
OPUS_MODEL = os.environ.get("MCF_OPUS_MODEL", "claude-opus-4-8")
OPUS_LABEL = "Opus " + OPUS_MODEL.replace("claude-opus-", "").replace("-", ".")
# Max pages the (expensive) VLM/Opus audit will render per form. Unlike the
# legacy MAX_PAGES=3 "first N pages" window, we audit the pages that actually
# carry MAPPED fillable fields (skipping instruction/blank pages) up to this
# cap — so a long form's page-6 values get verified instead of silently skipped.
AUDIT_PAGE_CAP = int(os.environ.get("MCF_AUDIT_PAGE_CAP", "16"))


def _audit_sample(client, png_bytes: bytes, temperature: float) -> list[dict]:
    """One Qwen-VL audit pass over an in-memory filled page image."""
    import base64
    b64 = base64.b64encode(png_bytes).decode()
    r = client.chat.completions.create(
        model=VL_MODEL, max_tokens=1500, temperature=temperature,
        messages=[{"role": "user", "content": [
            {"type": "text", "text": AUDIT_PROMPT},
            {"type": "image_url",
             "image_url": {"url": f"data:image/png;base64,{b64}"}}]}],
        extra_body={"chat_template_kwargs": {"enable_thinking": False}})
    txt = r.choices[0].message.content or "{}"
    try:
        return json.loads(txt).get("findings", [])
    except json.JSONDecodeError:
        i, j = txt.find("{"), txt.rfind("}")
        return json.loads(txt[i:j + 1]).get("findings", []) if i != -1 else []


def _norm(label: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (label or "").lower()).strip()[:48]


def consensus_audit(clients: list, page_pngs: dict[int, bytes], samples: int,
                    temperature: float = 0.5,
                    min_agree: int | None = None) -> dict[int, list[dict]]:
    """N-sample majority-voted audit per page (the recursive local first pass).

    A finding survives only if >= min_agree of the `samples` runs agree on the
    same (issue, normalized-label) for that page — filtering the one-off findings
    the single-shot auditor hallucinates on otherwise-clean forms.
    Returns {page_no -> [surviving findings]}.
    """
    if min_agree is None:
        min_agree = samples // 2 + 1
    out: dict[int, list[dict]] = {}
    for pno, png_bytes in page_pngs.items():
        def one(i: int) -> list[dict]:
            try:
                return _audit_sample(clients[i % len(clients)], png_bytes,
                                     temperature)
            except Exception:  # noqa: BLE001  (one bad sample shouldn't sink it)
                return []
        with ThreadPoolExecutor(max_workers=min(samples, len(clients) * 2)) as ex:
            runs = list(ex.map(one, range(samples)))
        votes: dict[tuple, list] = {}
        for findings in runs:
            seen = set()
            for f in findings:
                issue = f.get("issue")
                key = (issue, _norm(f.get("field", "")))
                if key in seen:  # one vote per sample per finding
                    continue
                seen.add(key)
                votes.setdefault(key, []).append(f)
        survivors = []
        for (issue, _lbl), insts in votes.items():
            if len(insts) >= min_agree:
                survivors.append({"issue": issue,
                                  "field": insts[0].get("field", ""),
                                  "detail": insts[0].get("detail", ""),
                                  "votes": len(insts)})
        if survivors:
            out[pno] = survivors
    return out


def _opus_adjudicate(marked_png: pathlib.Path, assignments: dict[int, str],
                     findings: list[dict],
                     timeout: int = int(os.environ.get("MCF_OPUS_TIMEOUT", "600")),
                     retries: int = 1) -> dict:
    """Show Opus the FILLED + marked page and the consensus findings.

    Opus confirms the real mismatches and returns mapping corrections in the
    marker->key/UNMAP protocol. Layout defects (truncated/overflow) are out of
    scope for key correction and explicitly excluded in the prompt.
    """
    def _line(m, t):
        name, key, val, prov = t
        s = f"  {m}: [{name}] -> {key}"
        if val:
            s += f'  (rendered "{val}" = {prov})'
        return s
    asg = "\n".join(_line(m, t) for m, t in sorted(assignments.items()))
    flag = "\n".join(f"  - [{f['issue']}] {f['field']}: {f.get('detail','')}"
                     for f in findings)
    prompt = (
        f"Read the image {marked_png}. It is a FILLED Maine court form; each "
        f"field has a small red number. Below, each marker shows its [field name] "
        f"and the canonical fact-key the mapping assigned it:\n{asg}\n\n"
        f"A local audit flagged these possible problems on this page:\n{flag}\n\n"
        f"{CONTRACT}\n\n"
        f"Judging by what is actually printed and filled, list every marker whose "
        f"key is wrong. Check especially:\n"
        f"(1) PARTY SECTION: a field inside a 'Plaintiff(s)' block must use a "
        f"parties.plaintiff.* (or party.*) key, a field in a 'Defendant(s)' block "
        f"a parties.defendant.* key, etc. A field carrying one party's value while "
        f"sitting in another party's block is WRONG.\n"
        f"(2) MULTI-LINE FIELDS: field names that differ only by a trailing number "
        f"(e.g. '... 1' and '... 2', or a '_2' suffix) are usually consecutive "
        f"lines of ONE labeled field (a 2-line address) and MUST share the same "
        f"party/key root; flag any that diverge.\n"
        f"For each wrong marker give the correct key, or 'UNMAP' if that field "
        f"should be blank. IGNORE pure layout issues (text truncated/overflowing "
        f"but on the right field). Omit a marker if it is correct. Reply with ONLY "
        f'compact JSON: {{"corrections":{{"<marker>":"<key or UNMAP>"}}}}. '
        f"Empty if none.")
    env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
    for attempt in range(retries + 1):
        try:
            r = subprocess.run(
                ["claude", "-p", prompt, "--model", OPUS_MODEL,
                 "--allowedTools", "Read"],
                capture_output=True, text=True, timeout=timeout, env=env)
            break
        except subprocess.TimeoutExpired:
            if attempt == retries:
                raise
    out = r.stdout.strip()
    if r.returncode != 0 or not out:
        raise RuntimeError(f"opus call failed (rc={r.returncode}): "
                           f"{r.stderr.strip()[:160]}")
    try:
        i, j = out.find("{"), out.rfind("}")
        return json.loads(out[i:j + 1]).get("corrections", {}) if i != -1 else {}
    except json.JSONDecodeError:
        return {}


def _resolve_value(key: str, facts: dict) -> tuple[str, str]:
    """(rendered value, human provenance) for a canonical key against the case.

    Lets the adjudicator see WHOSE value a field carries — the piece a purely
    visual read is missing (an address looks fine on an address line even when
    it is the wrong party's address).
    """
    try:
        if key == "today()":
            return datetime.date.today().isoformat(), "today's date"
        if key.startswith("parties."):
            _, role, attr = key.split(".", 2)
            v = (facts.get("parties", {}).get(role, {}) or {}).get(attr)
            return (str(v) if v is not None else "",
                    f"the {role.replace('_', ' ')}'s {attr.replace('_', ' ')}")
        if key.startswith("party."):
            attr = key.split(".", 1)[1]
            v = (facts.get("party", {}) or {}).get(attr)
            return (str(v) if v is not None else "",
                    f"the filing party's {attr.replace('_', ' ')}")
        if key.startswith("matter."):
            attr = key.split(".", 1)[1]
            v = (facts.get("matter", {}) or {}).get(attr)
            return (str(v) if v is not None else "",
                    f"the matter {attr.replace('_', ' ')}")
        if key.startswith("facts."):
            attr = key.split(".", 1)[1]
            v = (facts.get("facts", {}) or {}).get(attr)
            return (str(v) if v is not None else "", f"fact '{attr}'")
    except (ValueError, AttributeError):
        pass
    return "", ""


_AFFIRM = {"x", "✓", "yes", "y", "1", "true", "on", "checked", "[x]", "selected"}


def _checkbox_spurious(blank_doc, filled_doc, mp: dict, schema,
                       facts: dict) -> list[dict]:
    """Boxes the FILL checked without an affirmative-token value.

    The visual/Opus audit reads text, not checkbox state, so a box checked
    merely because its mapped value exists (a name/enum string) sailed through
    as `verified` — OTH-030, a PFA complaint, asserted 24 allegations this way.
    Deterministic and engine-independent: compares blank vs filled state so a
    box pre-checked in the blank (a form default) is never flagged; only a box
    the fill flipped on whose value is not an affirmative token is a defect.
    """
    name_to_fid = {f.get("label"): f["field_id"]
                   for f in schema.get("fields", []) if f.get("field_id")}

    def _on(w) -> bool:
        return w.field_value not in (None, "", "Off", "off")

    # Deterministic and cheap (no VLM) — scan the WHOLE document, not the
    # MAX_PAGES visual-audit window. OTH-030's spurious checks were on pages
    # 6-17; a 3-page horizon is exactly why they went unseen.
    blank_on: dict[tuple, bool] = {}
    for pno in range(len(blank_doc)):
        for w in blank_doc[pno].widgets() or []:
            if w.field_type == fitz.PDF_WIDGET_TYPE_CHECKBOX:
                blank_on[(pno, w.field_name)] = _on(w)
    out: list[dict] = []
    for pno in range(len(filled_doc)):
        for w in filled_doc[pno].widgets() or []:
            if w.field_type != fitz.PDF_WIDGET_TYPE_CHECKBOX or not _on(w):
                continue
            if blank_on.get((pno, w.field_name)):
                continue  # checked in the blank too — a form default, not ours
            fid_id = name_to_fid.get(w.field_name)
            key = mp.get(fid_id)
            val = _resolve_value(key, facts)[0] if key else ""
            if str(val).strip().lower() not in _AFFIRM:
                out.append({
                    "issue": MISMATCH, "field": w.field_name, "field_id": fid_id,
                    "detail": f"checkbox checked by fill but value {val!r} (key "
                              f"{key!r}) is not an affirmative token — spurious "
                              "check; a checkbox must be driven by a boolean",
                    "votes": 99})
    return out


def _party_root(key: str | None) -> str | None:
    """The party a key belongs to: 'parties.<role>' or 'party' (else None)."""
    if not key:
        return None
    if key.startswith("parties."):
        return ".".join(key.split(".")[:2])
    if key == "party" or key.startswith("party."):
        return "party"
    return None


def _base_name(name: str) -> str:
    """Field-name stem with trailing line-index markers stripped (' 2', '_2')."""
    b = re.sub(r"(_\d+)+$", "", name or "")
    b = re.sub(r"\s*\d+\s*$", "", b)
    return b.strip().lower()


def _sibling_party_conflicts(schema, mp: dict, blank_doc) -> dict[int, list]:
    """Deterministic: contiguous line-siblings keyed to DIFFERENT parties.

    Two widgets that share a field-name stem, sit at the same x, and are
    vertically adjacent are almost certainly consecutive lines of ONE labeled
    field (a 2-line address). If their keys name different parties, the lower
    line is misattributed — the class the visual audit cannot see. High-recall
    but high-precision: only fires when both keys are party-space and differ.
    Returns {page -> [hard-flag findings]} (votes=99 = must escalate / veto).
    """
    out: dict[int, list] = {}
    # Deterministic and cheap — scan the WHOLE document, not the MAX_PAGES
    # visual-audit window; a misattribution on page 4+ is just as wrong.
    for pno in range(len(blank_doc)):
        items = []
        for w in blank_doc[pno].widgets() or []:
            f = next((x for x in schema["fields"]
                      if x.get("label") == w.field_name
                      and x.get("type") in FILLABLE), None)
            if f:
                items.append((f["field_id"], w.field_name, fitz.Rect(w.rect)))
        groups: dict[str, list] = defaultdict(list)
        for fid_id, fname, rect in items:
            groups[_base_name(fname)].append((fid_id, fname, rect))
        for members in groups.values():
            if len(members) < 2:
                continue
            members.sort(key=lambda t: t[2].y0)
            run = [members[0]]
            for prev, cur in zip(members, members[1:]):
                pr, cr = prev[2], cur[2]
                xover = (min(pr.x1, cr.x1) - max(pr.x0, cr.x0)
                         > 0.5 * min(pr.width, cr.width))
                if xover and -2 <= (cr.y0 - pr.y1) <= 6:
                    run.append(cur)
                else:
                    _emit_run_conflict(run, mp, pno, out)
                    run = [cur]
            _emit_run_conflict(run, mp, pno, out)
    return out


def _child_idx(root: str | None) -> int | None:
    """Numeric N from a 'parties.child_<N>' root, else None."""
    m = re.match(r"parties\.child_(\d+)$", root or "")
    return int(m.group(1)) if m else None


def _emit_run_conflict(run: list, mp: dict, pno: int, out: dict) -> None:
    mapped = [(fid_id, fname, _party_root(mp.get(fid_id)))
              for fid_id, fname, _ in run]
    mapped = [(fid_id, fname, r) for fid_id, fname, r in mapped if r]
    if len(mapped) < 2:
        return
    # Legitimate per-row enumeration: contiguous rows keyed to DISTINCT children
    # (child_1, child_2, ...) are a multi-child table, NOT a misattribution. Only
    # the same-block/different-party case (plaintiff line vs defendant line) is a
    # real conflict. Suppress when every root is a distinct parties.child_<N>.
    idxs = [_child_idx(r) for _, _, r in mapped]
    if all(i is not None for i in idxs) and len(set(idxs)) == len(idxs):
        return
    # Legitimate self-attestation block: the generic filer ('party', whose role
    # is chosen on the form) paired with the explicitly role-neutral opponent
    # ('parties.other_party'). "My name/phone/email" above "the other party's
    # name/phone/email" is two parties by design, not a leak — same category as
    # the child enumeration above. Suppress only this exact pairing so genuine
    # plaintiff↔defendant leaks (the CV-001 class) still escalate.
    roots = {r for _, _, r in mapped}
    if roots == {"party", "parties.other_party"}:
        return
    anchor_fid, anchor_name, anchor = mapped[0]
    for fid_id, fname, r in mapped[1:]:
        if r != anchor:  # both are party-roots (None filtered) and differ
            out.setdefault(pno, []).append({
                "issue": "mismatched", "field": fname, "field_id": fid_id,
                "detail": (f"contiguous line below '{anchor_name}' (keyed "
                           f"{anchor}.*) yet keyed to {r}.* — same block, "
                           f"different party"),
                "votes": 99})


def _mapped_pages(doc, schema, mp: dict, cap: int = AUDIT_PAGE_CAP) -> list[int]:
    """Page indices carrying at least one MAPPED fillable widget, capped.

    Replaces the "first MAX_PAGES pages" heuristic: a value on page 6 is audited,
    while instruction/blank pages are skipped so cost tracks real content.
    """
    label_fid = {f.get("label"): f["field_id"] for f in schema.get("fields", [])
                 if f.get("field_id")}
    pages: list[int] = []
    for pno in range(len(doc)):
        for w in doc[pno].widgets() or []:
            f = next((x for x in schema["fields"]
                      if x.get("label") == w.field_name
                      and x.get("type") in FILLABLE), None)
            if f and mp.get(f["field_id"]):
                pages.append(pno)
                break
    if not pages:  # nothing mapped (shouldn't happen for a verified form)
        pages = list(range(min(len(doc), MAX_PAGES)))
    return pages[:cap]


def _by_page(doc, schema, pages=None) -> dict[int, list]:
    bp: dict[int, list] = {}
    rng = pages if pages is not None else range(min(len(doc), MAX_PAGES))
    for pno in rng:
        for w in doc[pno].widgets() or []:
            f = next((x for x in schema["fields"]
                      if x.get("label") == w.field_name), None)
            if f and f.get("type") in FILLABLE:
                bp.setdefault(pno, []).append((f["field_id"], tuple(w.rect)))
    return bp


def _union_audit(clients: list, page_pngs: dict, samples: int,
                 passes: int) -> tuple[dict, list]:
    """K independent consensus passes; UNION the findings.

    A mismatch escapes review only if it is absent from all `passes` runs — so a
    real defect that survives in any pass still reaches Opus, defeating the
    single-pass variance that can otherwise hide a bug and false-verify it.
    Returns ({page_no -> [mismatch findings]}, [render findings]).
    """
    mism: dict[int, dict] = {}
    rend: dict[tuple, dict] = {}
    for _ in range(passes):
        found = consensus_audit(clients, page_pngs, samples)
        for p, fs in found.items():
            for f in fs:
                k = (f["issue"], _norm(f.get("field", "")))
                if f["issue"] == MISMATCH:
                    mism.setdefault(p, {})[k] = f
                elif f["issue"] in RENDER:
                    rend[k] = f
    return ({p: list(d.values()) for p, d in mism.items()}, list(rend.values()))


def audit_one(fid: str, samples: int, max_iters: int, use_opus: bool,
              outdir: pathlib.Path, report_only: bool = False,
              passes: int = 3) -> dict:
    fdir = OSS_ROOT / "forms" / fid
    mapping = json.loads((fdir / "mapping.json").read_text())
    if mapping.get("status") not in ("opus-reviewed", "verified"):
        return {"form": fid, "status": "skipped", "reason": mapping.get("status")}
    schema = json.loads((fdir / "schema.json").read_text())
    valid_ids = {f["field_id"] for f in schema["fields"]}
    facts = json.loads((fdir / "examples" / "sample_case.json").read_text())
    clients = _vl_clients()

    if report_only:
        # Free intel pass: cluster consensus audit only, NO mapping.json writes,
        # NO Opus, NO git. Classifies the form so a later (Opus-backed) run can
        # spend the serial budget only on the ones with real mismatches. Safe to
        # run concurrently with a committing batch (touches nothing in the repo).
        res = fill_via_mapping(fid, facts, outdir)
        if not res.get("ok"):
            return {"form": fid, "status": "fill-error",
                    "reason": res.get("error")}
        doc = fitz.open(res["out_pdf"])
        apages = _mapped_pages(doc, schema, mapping.get("map") or {})
        page_pngs = {p: doc[p].get_pixmap(dpi=140).tobytes("png") for p in apages}
        found = consensus_audit(clients, page_pngs, samples)
        flat = [f for fs in found.values() for f in fs]
        mism = [f for f in flat if f["issue"] == MISMATCH]
        rend = [f for f in flat if f["issue"] in RENDER]
        status = ("would-verify" if not flat
                  else "needs-opus" if mism else "render-only")
        return {"form": fid, "status": status, "mismatch": len(mism),
                "render_flags": len(rend), "findings": flat}

    orig_map = dict(mapping.get("map") or {})

    def _verify(note: str, render: list, fixes: int) -> dict:
        # Diff-quarantine (lesson #10): the Opus fix path is provenance-blind —
        # to clear a visual audit it can remap a box to the wrong semantic
        # FAMILY (mailing-address -> phone, phone -> email), which renders
        # plausibly and slips the gate. Such a cross-family remap must NOT
        # auto-promote to `verified`; it lands in `map-review` with the diff
        # recorded so a human confirms it (a sentinel fill+render settles it).
        fam = _family_changes(orig_map, mp)
        if fam:
            mapping["map"] = mp
            mapping["status"] = "map-review"
            mapping["map_review"] = fam
            mapping["note"] = (note + f" HELD for review: the fix path made "
                               f"{len(fam)} cross-family key change(s) "
                               "(e.g. " + ", ".join(
                                   f"{c['field_id']}:{c['old_family']}->"
                                   f"{c['new_family']}" for c in fam[:3])
                               + ") — confirm against a render before trusting.")
            if render:
                mapping["render_flags"] = render
            (fdir / "mapping.json").write_text(json.dumps(mapping, indent=2))
            return {"form": fid, "status": "map-review",
                    "family_changes": len(fam), "fixes": fixes,
                    "render_flags": len(render)}
        mapping["status"] = "verified"
        mapping["note"] = note
        mapping.pop("audit_conflicts", None)  # stale once verified
        mapping.pop("map_review", None)
        if render:
            mapping["render_flags"] = render
        else:
            mapping.pop("render_flags", None)
        (fdir / "mapping.json").write_text(json.dumps(mapping, indent=2))
        return {"form": fid, "status": "verified", "fixes": fixes,
                "render_flags": len(render)}

    blank = fitz.open(str(fdir / f"{fid}.pdf"))
    mp = dict(mapping.get("map") or {})
    total_fixes = 0
    for it in range(max_iters):
        res = fill_via_mapping(fid, facts, outdir)
        if not res.get("ok"):
            return {"form": fid, "status": "fill-error",
                    "reason": res.get("error")}
        doc = fitz.open(res["out_pdf"])
        # (0) deterministic checkbox-state veto — the class the visual/Opus audit
        #     is blind to (it reads text, not check state). A box the fill checked
        #     without an affirmative-token value is a hard defect Opus cannot fix,
        #     so block `verified` outright rather than spend an Opus turn on it.
        apages = _mapped_pages(doc, schema, mp)
        cb_spurious = _checkbox_spurious(blank, doc, mp, schema, facts)
        if cb_spurious:
            mapping["map"] = mp
            mapping["audit_conflicts"] = cb_spurious
            mapping["note"] = (mapping.get("note", "").split(" Audit:")[0]
                               + f" Audit: {len(cb_spurious)} checkbox(es) checked "
                                 "without an affirmative-token value (a checkbox must "
                                 "be driven by a boolean) — blocked verification.")
            (fdir / "mapping.json").write_text(json.dumps(mapping, indent=2))
            return {"form": fid, "status": "checkbox-conflict",
                    "conflicts": len(cb_spurious), "fixes": total_fixes}
        page_pngs = {p: doc[p].get_pixmap(dpi=140).tobytes("png") for p in apages}
        # (1) K-pass UNION visual audit: a mismatch survives if ANY pass sees it.
        mismatch_pages, render = _union_audit(clients, page_pngs, samples, passes)
        # (2) deterministic sibling/party conflicts — the class the visual audit
        #     cannot see; these are hard flags with veto power over `verified`.
        det = _sibling_party_conflicts(schema, mp, blank)
        for pno, fs in det.items():
            mismatch_pages.setdefault(pno, []).extend(fs)

        if not mismatch_pages:
            note = (f"Filled from the canonical sample and audited clean by "
                    f"{passes}x{samples}-sample Qwen-VL cluster consensus + "
                    f"deterministic party-attribution check"
                    + (f" ({OPUS_LABEL} corrected an earlier pass)" if total_fixes
                       else "") + ".")
            if render:
                note += f" {len(render)} layout render-flag(s) recorded."
            return _verify(note, render, total_fixes)

        if not use_opus:
            n_mm = sum(len(v) for v in mismatch_pages.values())
            return {"form": fid, "status": "needs-opus", "mismatch": n_mm,
                    "render_flags": len(render),
                    "findings": [f for v in mismatch_pages.values() for f in v]}

        # escalate the union (visual + deterministic) to Opus on the FILLED +
        # marked image, arming each marker with its rendered value + provenance.
        bp = _by_page(fitz.open(str(fdir / f"{fid}.pdf")), schema, pages=apages)
        iter_fixes = 0
        mdoc = fitz.open(res["out_pdf"])
        n, page_legend = 1, {}
        for pno in sorted(bp):
            _png, legend, n = _render_marked(mdoc, bp, pno, n)
            page_legend[pno] = (legend, _png)
        for pno, fs in mismatch_pages.items():
            if pno not in page_legend:
                continue
            legend, png_bytes = page_legend[pno]
            png = outdir / f".audit_{fid}_p{pno}.png"
            png.write_bytes(png_bytes)
            assignments = {}
            for m, fidm in legend.items():
                key = mp.get(fidm, "(unmapped)")
                val, prov = _resolve_value(key, facts) if key != "(unmapped)" \
                    else ("", "")
                assignments[m] = (fidm, key, val, prov)
            try:
                corr = _opus_adjudicate(png, assignments, fs)
            except Exception:  # noqa: BLE001
                png.unlink(missing_ok=True)
                return {"form": fid, "status": "audit-failed",
                        "reason": "opus unreachable", "fixes": total_fixes}
            png.unlink(missing_ok=True)
            for marker, key in corr.items():
                try:
                    fidm = legend.get(int(marker))
                except (ValueError, TypeError):
                    continue
                if fidm not in valid_ids:
                    continue
                if key == "UNMAP":
                    if mp.pop(fidm, None) is not None:
                        iter_fixes += 1
                elif _key_ok(key) and mp.get(fidm) != key:
                    mp[fidm] = key
                    iter_fixes += 1
        total_fixes += iter_fixes
        if iter_fixes:
            mapping["map"] = mp
            (fdir / "mapping.json").write_text(json.dumps(mapping, indent=2))
            continue  # re-fill and re-audit the corrected mapping

        # Opus changed nothing this round. The deterministic check has VETO power:
        # a structural party conflict it still sees blocks `verified`.
        det_left = _sibling_party_conflicts(schema, mp, blank)
        if det_left:
            mapping["map"] = mp
            mapping["audit_conflicts"] = [f for v in det_left.values() for f in v]
            mapping["note"] = (mapping.get("note", "").split(" Audit:")[0]
                               + f" Audit: {sum(len(v) for v in det_left.values())}"
                                 " deterministic party-attribution conflict(s) Opus "
                                 "declined to resolve — left opus-reviewed for "
                                 "manual review.")
            (fdir / "mapping.json").write_text(json.dumps(mapping, indent=2))
            return {"form": fid, "status": "party-conflict",
                    "conflicts": sum(len(v) for v in det_left.values()),
                    "fixes": total_fixes}
        # only soft (visual / sample-data) findings remained; Opus confirmed the
        # mapping is correct -> verify with a residual note.
        n_mm = sum(len(v) for v in mismatch_pages.values())
        note = (f"Filled; {passes}x consensus flagged {n_mm} value(s); {OPUS_LABEL} "
                f"reviewed the filled form and confirmed no mapping change needed.")
        if render:
            note += f" {len(render)} layout render-flag(s) recorded."
        return _verify(note, render, total_fixes)

    # exhausted max_iters while Opus was still changing keys (never converged).
    mapping["map"] = mp
    (fdir / "mapping.json").write_text(json.dumps(mapping, indent=2))
    return {"form": fid, "status": "opus-residual", "fixes": total_fixes}


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--forms", required=True, help="comma list")
    ap.add_argument("--qwen-samples", type=int, default=5, metavar="N",
                    help="consensus audit sample count per page (cluster pass)")
    ap.add_argument("--passes", type=int, default=3, metavar="K",
                    help="independent consensus passes to UNION before the verify "
                         "gate; a mismatch in any pass escalates to Opus")
    ap.add_argument("--max-iters", type=int, default=2)
    ap.add_argument("--no-opus", action="store_true",
                    help="cluster consensus audit only; do not adjudicate/promote")
    ap.add_argument("--report-only", action="store_true",
                    help="free intel pass: consensus audit + classify, but write "
                         "NO mapping.json/git (safe alongside a committing batch)")
    ap.add_argument("--out", type=pathlib.Path, default=pathlib.Path("/tmp/audit2"))
    ap.add_argument("--log", type=pathlib.Path,
                    default=pathlib.Path("/tmp/audit_report.jsonl"))
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    logf = args.log.open("a") if args.report_only else None
    for fid in [f.strip() for f in args.forms.split(",") if f.strip()]:
        r = audit_one(fid, args.qwen_samples, args.max_iters,
                      not args.no_opus, args.out, report_only=args.report_only,
                      passes=args.passes)
        extra = (f"{r.get('fixes',0)} fix(es)" if "fixes" in r
                 else f"{r.get('mismatch',0)} mismatch" if "mismatch" in r
                 else r.get("reason", ""))
        print(f"  {r['form']}: {r['status']} — {extra}"
              + (f", {r['render_flags']} render flag(s)"
                 if r.get("render_flags") else ""))
        if logf:
            logf.write(json.dumps(r) + "\n"); logf.flush()
    if logf:
        logf.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
