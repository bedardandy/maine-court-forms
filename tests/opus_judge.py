#!/usr/bin/env python3
"""Opus 4.8 sentinel-render judge — the semantic placement oracle.

The deterministic suite (test_placement.py) pins KNOWN values; this judge is
the open-ended check: it fills a form with the sample case, renders the
page(s) carrying the fields of interest, and asks Claude Opus 4.8 whether each
printed value sits under a label consistent with its MEANING (the value-vs-
label oracle — see feedback-placement-sentinel-oracle). It catches placement
defects we haven't pinned yet, the way the manual sweep did.

Opt-in and never in CI: it needs a local blank PDF and the `claude` CLI, and it
costs tokens. Runs Opus headless on the subscription via OAuth — ANTHROPIC_API_KEY
is stripped from the child env (a stale/invalid key would otherwise override the
session and fail auth).

    python3 tests/opus_judge.py --forms JV-006-W NC-001 PC-034
    python3 tests/opus_judge.py            # the full pinned placement set
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from tests.helpers import sample_case, schema, has_pdf  # noqa: E402

MODEL = os.environ.get("MCF_OPUS_MODEL", "claude-opus-4-8")
TIMEOUT = int(os.environ.get("MCF_OPUS_TIMEOUT", "300"))

# Default set: the forms whose placement we fixed + render-verified.
DEFAULT_FORMS = ["JV-006-W", "NC-001", "MJ-SC-012", "MJ-009", "PC-034", "OTH-029"]

PROMPT = """Read the rendered court-form page image at {img}.

This page was filled from a known fact pattern. Below is the GROUND TRUTH —
the value that each field SHOULD contain and what it means:

{gt}

Your job: decide whether each printed value sits under a label consistent with
its MEANING. A defect is a value printed under a label for a DIFFERENT concept
(e.g. a docket number on the "Location" line, one party's name in another
party's block, a person's name in a dollar/amount field). Ignore blank fields
and cosmetic spacing.

Respond with ONLY a JSON object, no prose:
{{"verdict": "clean" | "misplaced",
  "errors": [{{"value": "...", "printed_under_label": "...", "should_be": "..."}}],
  "summary": "one sentence"}}"""


def render(form: str, out_dir: pathlib.Path) -> dict[int, pathlib.Path]:
    """Fill `form` with its sample case and render each field-bearing page."""
    import fitz
    from engine.fill_via_mapping import fill_via_mapping
    from engine.fill_and_audit import RECIPE3

    case = sample_case(form)
    fdir = REPO / "forms" / form
    if form in RECIPE3:
        from engine.fill_and_audit import fill_one
        r = fill_one(form, case, out_dir,
                     schema_path=fdir / "schema.json",
                     pdf_path=fdir / f"{form}.pdf")
    else:
        r = fill_via_mapping(form, case, out_dir)
    if not r.get("ok"):
        raise RuntimeError(r.get("error", "fill failed"))
    filled = pathlib.Path(r["out_pdf"])
    pages = sorted({f.get("page", 0) for f in schema(form)["fields"]})
    d = fitz.open(str(filled))
    d.bake(annots=True, widgets=True)
    imgs = {}
    for p in pages:
        if p >= len(d):
            continue
        pix = d[p].get_pixmap(matrix=fitz.Matrix(2.2, 2.2))
        ip = out_dir / f"p{p}.jpg"
        ip.write_bytes(pix.tobytes("jpeg", jpg_quality=90))
        imgs[p] = ip
    return imgs


def ground_truth(form: str, page: int) -> str:
    """label -> expected value for the fields on `page` (best-effort)."""
    from engine.fill_via_mapping import resolve_mapping
    from engine.fill_and_audit import RECIPE3
    lines = []
    sch = {f["field_id"]: f for f in schema(form)["fields"]}
    if form in RECIPE3:
        from tests.helpers import recipe_output
        vals = recipe_output(form)
    else:
        vals = resolve_mapping(form, sample_case(form)).get("fid_value", {})
    for fid, v in vals.items():
        f = sch.get(fid)
        if not f or f.get("page") != page or not v:
            continue
        lines.append(f"  '{f.get('label', fid)}' should = {v!r}")
    return "\n".join(lines) or "  (no mapped values on this page)"


def _parse(stdout: str) -> dict | None:
    m = re.search(r"\{.*\}", stdout, re.DOTALL)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except Exception:
        return None


def judge_page(img: pathlib.Path, gt: str) -> dict:
    prompt = PROMPT.format(img=img, gt=gt)
    env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
    try:
        r = subprocess.run(
            ["claude", "-p", prompt, "--model", MODEL, "--allowedTools", "Read"],
            capture_output=True, text=True, timeout=TIMEOUT, env=env, cwd=str(REPO))
    except subprocess.TimeoutExpired:
        return {"verdict": "error", "summary": "timeout"}
    out = (r.stdout or "")
    if "session limit" in (out + (r.stderr or "")).lower():
        return {"verdict": "error", "summary": "session_limit"}
    return _parse(out) or {"verdict": "error", "summary": "unparseable",
                           "raw": out[:160]}


def judge_form(form: str) -> dict:
    if not has_pdf(form):
        return {"form": form, "verdict": "skip", "summary": "no blank PDF"}
    with tempfile.TemporaryDirectory() as td:
        out = pathlib.Path(td)
        try:
            imgs = render(form, out)
        except Exception as e:  # noqa: BLE001
            return {"form": form, "verdict": "error", "summary": f"render: {e!r}"}
        page_results = []
        for p, img in imgs.items():
            gt = ground_truth(form, p)
            if gt.strip().startswith("(no mapped"):
                continue
            v = judge_page(img, gt)
            v["page"] = p
            page_results.append(v)
    misplaced = [r for r in page_results if r.get("verdict") == "misplaced"]
    verdict = "misplaced" if misplaced else (
        "clean" if page_results else "no_values")
    return {"form": form, "verdict": verdict, "pages": page_results}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--forms", nargs="*", default=DEFAULT_FORMS)
    a = ap.parse_args()
    results = [judge_form(f) for f in a.forms]
    print(json.dumps(results, indent=2))
    bad = [r for r in results if r["verdict"] == "misplaced"]
    print(f"\n{len(results)} judged | misplaced: {len(bad)} "
          f"{[r['form'] for r in bad]}")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
