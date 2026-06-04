#!/usr/bin/env python3
"""Recursive self-improvement: local Qwen maps, Opus 4.7 reviews & corrects.

Division of labor: the local Qwen cluster (free) produces the draft mapping;
Opus 4.7 — via the Claude Code subscription, not the API — acts as the judge.
For each form it renders the blank form with a numbered marker on every field,
shows Opus the current marker->canonical-key assignments, and asks Opus to
return only the corrections (markers whose key is wrong given the VISIBLE
label). Corrections are validated against the canonical contract and applied;
the loop can re-judge until Opus accepts or --max-iters is hit.

    python3 tools/improve_loop.py --forms AD-001            # review existing mapping
    python3 tools/improve_loop.py --forms AD-001 --remap    # Qwen re-map first, then Opus

Opus is driven headlessly with `claude -p` (ANTHROPIC_API_KEY unset so it uses
the subscription OAuth). That has usage limits — run in paced batches, not all
350 at once. Writes mapping.json status "opus-reviewed" + iteration count.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys

import fitz  # PyMuPDF

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import openai  # noqa: E402

from tools.ai_map_forms import _key_ok  # noqa: E402
from tools.vision_map_forms import (_render_marked, FILLABLE,  # noqa: E402
                                     VL_ENDPOINTS, _vl_map,
                                     _map_one as _qwen_map_one)
from collections import Counter  # noqa: E402
from concurrent.futures import ThreadPoolExecutor  # noqa: E402

OSS_ROOT = pathlib.Path(__file__).resolve().parent.parent

CONTRACT = (
    "Canonical keys: matter.{docket_number,court_county,court_location,"
    "court_type,case_type,filing_date}; parties.<role>.<attr> with role in "
    "{plaintiff,defendant,attorney,child_1,child_2,...} and attr in "
    "{full_name,first_name,middle_name,last_name,address,city,state,zip,phone,"
    "email,date_of_birth} (attorney also bar_number); party.<attr> (same, plus "
    "signature) for the filing party; facts.<snake_case> for form-specific "
    "data; today() for a bare Date/Dated signature line. petitioner->plaintiff, "
    "respondent->defendant.")


def opus_review(png: pathlib.Path, assignments: dict[int, str],
                author: bool = False,
                timeout: int = int(__import__("os").environ.get("MCF_OPUS_TIMEOUT", "600")),
                retries: int = 2) -> dict:
    """Ask Opus 4.7 (subscription) which marker assignments to change.

    Returns {marker:int -> corrected canonical key or 'UNMAP'} for changes only.
    With author=True Opus also *authors* keys for '(unmapped)' markers whose
    printed label clearly corresponds to a canonical key — expanding coverage,
    not just correcting what Qwen drafted.
    """
    asg = "\n".join(f"  {m}: {k}" for m, k in sorted(assignments.items()))
    task = (
        "list every marker that needs a change: (a) its assigned key is WRONG — "
        "give the correct key; (b) it is '(unmapped)' but its printed label "
        "clearly corresponds to a canonical key — give that key (author it); or "
        "(c) it is mapped but should be left blank — give 'UNMAP'. Omit a marker "
        "if it is already correct, or if it is '(unmapped)' and you are not "
        "confident of the right key (never guess)."
        if author else
        "list the markers whose assigned key is WRONG, with the correct key (or "
        "'UNMAP' if it should not be filled).")
    prompt = (
        f"Read the image {png}. It is a blank Maine court form with a small red "
        f"number on each fillable field. A draft maps each numbered field to a "
        f"canonical fact-key:\n{asg}\n\n{CONTRACT}\n\n"
        f"Judging ONLY by the printed label next to each number, {task} Reply with "
        f'ONLY compact JSON: {{"corrections":{{"<marker>":"<key or UNMAP>"}}}}. '
        f"Empty if no changes.")
    env = {k: v for k, v in __import__("os").environ.items()
           if k != "ANTHROPIC_API_KEY"}
    for attempt in range(retries + 1):
        try:
            r = subprocess.run(
                ["claude", "-p", prompt, "--model",
                 __import__("os").environ.get("MCF_OPUS_MODEL", "claude-opus-4-8"),
                 "--allowedTools", "Read"],
                capture_output=True, text=True, timeout=timeout, env=env)
            break
        except subprocess.TimeoutExpired:
            if attempt == retries:  # the image-read turn can stall; retry once
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


def qwen_consensus(clients: list, fid: str, by_page: dict, valid_ids: set,
                   samples: int, temperature: float = 0.4,
                   min_agree: int | None = None) -> dict:
    """Build a denoised draft map by voting N Qwen-VL samples across the cluster.

    Each marked page is rendered once, then sampled `samples` times (fanned out
    over your local VLM endpoint(s) at a small temperature for diversity). Per marker we
    majority-vote the proposed key and keep it only if at least `min_agree`
    samples agree — filtering one-off hallucinations the local model emits.
    Returns {field_id -> canonical key}. This is the cheap local convergence
    that runs before the (serial, costly) Opus review.
    """
    if min_agree is None:
        min_agree = samples // 2 + 1  # strict majority
    fdir = OSS_ROOT / "forms" / fid
    doc = fitz.open(str(fdir / f"{fid}.pdf"))
    mp: dict[str, str] = {}
    n = 1
    for pno in sorted(by_page):
        png_bytes, legend, n = _render_marked(doc, by_page, pno, n)
        # fan the N samples across the available endpoints in parallel
        def one(i: int) -> dict:
            try:
                return _vl_map(clients[i % len(clients)], png_bytes,
                               temperature=temperature)
            except Exception:  # noqa: BLE001  (one bad sample shouldn't sink it)
                return {}
        with ThreadPoolExecutor(max_workers=min(samples, len(clients) * 2)) as ex:
            answers = list(ex.map(one, range(samples)))
        # collect votes per marker -> key
        votes: dict[int, Counter] = {}
        for ans in answers:
            for marker, key in ans.items():
                try:
                    m = int(marker)
                except (ValueError, TypeError):
                    continue
                if _key_ok(key):
                    votes.setdefault(m, Counter())[key] += 1
        for m, ctr in votes.items():
            key, count = ctr.most_common(1)[0]
            if count >= min_agree:
                fidm = legend.get(m)
                if fidm in valid_ids:
                    mp[fidm] = key
    return mp


def _improve_one(fid: str, remap: bool, max_iters: int,
                 author: bool = False, qwen_samples: int = 0) -> dict:
    fdir = OSS_ROOT / "forms" / fid
    schema = json.loads((fdir / "schema.json").read_text())
    valid_ids = {f["field_id"] for f in schema["fields"]}

    if remap:
        client = openai.OpenAI(base_url=VL_ENDPOINTS[0], api_key="none", timeout=240)
        _qwen_map_one(client, fid)  # Qwen first pass (writes mapping.json)
    mapping = json.loads((fdir / "mapping.json").read_text())
    mp = dict(mapping.get("map") or {})

    doc = fitz.open(str(fdir / f"{fid}.pdf"))
    by_page: dict[int, list] = {}
    for pno in range(min(len(doc), 4)):
        for w in doc[pno].widgets():
            f = next((x for x in schema["fields"]
                      if x.get("label") == w.field_name), None)
            if f and f.get("type") in FILLABLE:
                by_page.setdefault(pno, []).append((f["field_id"], tuple(w.rect)))

    if not by_page:
        # No marker can be placed, so Opus cannot review the form. This happens
        # for flat PDFs (no AcroForm widgets) and for forms whose widget
        # field-names don't match the schema labels. Record that honestly
        # instead of falsely stamping it opus-reviewed (Opus never saw it).
        any_widgets = any(doc[p].widgets() for p in range(min(len(doc), 4)))
        reason = ("widget field-names do not match schema labels"
                  if any_widgets else "no fillable AcroForm widgets in the PDF")
        mapping.update({"status": "no-mappable-fields", "map": {},
                        "note": f"Not mappable by the marker/vision pipeline: "
                                f"{reason}."})
        (fdir / "mapping.json").write_text(json.dumps(mapping, indent=2))
        return {"form": fid, "fixes": 0, "mapped": 0,
                "status": "no-mappable-fields"}

    if qwen_samples > 0:
        # Local recursive convergence: vote N Qwen-VL samples across the
        # cluster into a denoised draft before the (serial, costly) Opus pass.
        clients = [openai.OpenAI(base_url=ep, api_key="none", timeout=240)
                   for ep in VL_ENDPOINTS]
        mp = qwen_consensus(clients, fid, by_page, valid_ids, qwen_samples)

    total_fixes = 0
    reviewed = False  # True once ANY page gets an Opus verdict
    unreviewed_pages: set[int] = set()  # pages whose Opus call failed every attempt
    for _ in range(max_iters):
        doc = fitz.open(str(fdir / f"{fid}.pdf"))  # fresh (markers mutate page)
        n, iter_fixes = 1, 0
        iter_unreviewed: set[int] = set()
        for pno in sorted(by_page):
            png_bytes, legend, n = _render_marked(doc, by_page, pno, n)
            png = OSS_ROOT / f".improve_{fid}_p{pno}.png"
            png.write_bytes(png_bytes)
            assignments = {m: mp.get(fidm, "(unmapped)") for m, fidm in legend.items()}
            try:
                corr = opus_review(png, assignments, author=author)
                reviewed = True
            except Exception:  # noqa: BLE001  (Opus stall / usage limit on ONE page)
                # Partial credit: one page's failure must NOT discard the pages
                # that DID review. Skip this page (keep its draft keys) and go on.
                iter_unreviewed.add(pno)
                png.unlink(missing_ok=True)
                continue
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
        unreviewed_pages = iter_unreviewed  # reflects the final iteration's state
        if iter_fixes == 0:
            break  # Opus accepts (converged) or nothing left to change

    if not reviewed:
        # NO page ever returned a verdict (Opus unreachable / usage limit) —
        # leave the existing mapping intact rather than falsely stamping it.
        return {"form": fid, "fixes": total_fixes, "mapped": len(mp),
                "status": "review-failed"}
    opus_model = __import__("os").environ.get("MCF_OPUS_MODEL", "claude-opus-4-8")
    opus_label = "Opus " + opus_model.replace("claude-opus-", "").replace("-", ".")
    draft = (f"{qwen_samples}-sample Qwen-VL cluster consensus draft"
             if qwen_samples > 0 else "Qwen draft")
    note = (f"{draft} reviewed/corrected by {opus_label} (subscription) from the "
            "rendered form; validated against the contract.")
    if author:
        note = (f"{draft} reviewed by {opus_label} (subscription), which also "
                "authored keys for unmapped fields from the rendered form; "
                "validated against the contract.")
    if unreviewed_pages:
        note += (f" NOTE: page(s) {sorted(p+1 for p in unreviewed_pages)} kept "
                 "their Qwen consensus draft (Opus call did not return for those "
                 "pages); phase-2 fill-audit still gates verification.")
    mapping.update({"status": "opus-reviewed",
                    "model": f"qwen3.6-27b+{opus_model}",
                    "note": note, "map": mp})
    if unreviewed_pages:
        mapping["partial_review_pages"] = sorted(p + 1 for p in unreviewed_pages)
    (fdir / "mapping.json").write_text(json.dumps(mapping, indent=2))
    return {"form": fid, "fixes": total_fixes, "mapped": len(mp),
            "status": "opus-reviewed"}


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--forms", required=True, help="comma list")
    ap.add_argument("--remap", action="store_true",
                    help="Qwen re-maps from scratch before Opus review")
    ap.add_argument("--max-iters", type=int, default=2)
    ap.add_argument("--author", action="store_true",
                    help="Opus also authors keys for unmapped fields (expand "
                         "coverage), not just correct existing assignments")
    ap.add_argument("--qwen-samples", type=int, default=0, metavar="N",
                    help="before Opus, build the draft by majority-voting N "
                         "Qwen-VL samples across the cluster (recursive local "
                         "convergence); 0 = use existing/--remap draft")
    args = ap.parse_args()
    for fid in [f.strip() for f in args.forms.split(",") if f.strip()]:
        r = _improve_one(fid, args.remap, args.max_iters, args.author,
                         args.qwen_samples)
        print(f"  {r['form']}: {r['status']} — {r['fixes']} correction(s), "
              f"{r['mapped']} mapped")
    return 0


if __name__ == "__main__":
    sys.exit(main())
