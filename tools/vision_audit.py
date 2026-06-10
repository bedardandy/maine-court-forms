#!/usr/bin/env python3
"""Vision-audit filled forms to flag render-level fill defects.

Fills a form from its mapping.json + canonical sample (engine.fill_via_mapping),
renders each page, and asks a local vision-language model to flag *filled*
fields that are truncated, overflowing/overlapping, or whose value clearly
doesn't match the printed label. This is the verification edge for promoting a
draft `mapping.json` toward "verified" (see docs/STATUS.md): a clean audit is
evidence the mapped values land correctly; findings point at the fields to fix.

    python3 tools/vision_audit.py --sample 12
    python3 tools/vision_audit.py --forms AD-015,FM-218

Blank fields are ignored (the generic sample doesn't carry every fact, so many
fields are legitimately empty). Needs the blank PDFs on disk (tools/fetch_pdfs.py)
and the local Qwen-VL cluster. Writes findings to --log.
"""
from __future__ import annotations

import argparse
import base64
import itertools
import json
import os
import pathlib
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

import fitz  # PyMuPDF
import openai

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from engine.fill_via_mapping import fill_via_mapping  # noqa: E402

OSS_ROOT = pathlib.Path(__file__).resolve().parent.parent
VL_ENDPOINTS = os.environ.get(
    "MCF_LLM_ENDPOINTS", "http://localhost:8080/v1").split(",")
VL_MODEL = os.environ.get("MCF_VL_MODEL", "qwen3.6-27b")
MAX_PAGES = 3   # audit the first few pages; bulk of fields live up front

AUDIT_PROMPT = (
    "You are auditing one page of a filled Maine court form (the image). "
    "Consider ONLY fields that contain filled-in text; ignore every blank/empty "
    "field. Flag a filled field only if it is clearly: 'truncated' (text cut off "
    "by the field box edge), 'overflow' (text overlaps other text or printed "
    "lines), or 'mismatched' (the filled value plainly doesn't fit the printed "
    "label beside it, e.g. a date written on a name line). Return ONLY compact "
    'JSON: {"findings":[{"field":"<printed label>","issue":"truncated|overflow|'
    'mismatched","detail":"<short>"}]}. If nothing is wrong, return {"findings":[]}.'
)


def _vl_clients():
    return [openai.OpenAI(base_url=ep, api_key="none", timeout=180)
            for ep in VL_ENDPOINTS]


def _audit_image(client, png: pathlib.Path) -> list[dict]:
    b64 = base64.b64encode(png.read_bytes()).decode()
    r = client.chat.completions.create(
        model=VL_MODEL, max_tokens=1500, temperature=0,
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


def _select(sample: int) -> list[str]:
    out = []
    for p in sorted(OSS_ROOT.glob("forms/*/mapping.json")):
        m = json.loads(p.read_text())
        fid = p.parent.name
        if m.get("status") != "ai-mapped" or len(m.get("map") or {}) < 5:
            continue
        if not (p.parent / f"{fid}.pdf").exists():
            continue
        out.append(fid)
        if len(out) >= sample:
            break
    return out


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sample", type=int, default=12)
    ap.add_argument("--forms", default="")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--out", type=pathlib.Path, default=pathlib.Path("/tmp/va"))
    ap.add_argument("--log", type=pathlib.Path,
                    default=pathlib.Path("/tmp/vision_audit.jsonl"))
    args = ap.parse_args()

    forms = ([f.strip() for f in args.forms.split(",") if f.strip()]
             if args.forms else _select(args.sample))
    clients = _vl_clients()
    pick = itertools.count()
    args.out.mkdir(parents=True, exist_ok=True)
    logf = args.log.open("w")
    lock = threading.Lock()
    print(f"vision-auditing {len(forms)} ai-mapped forms with {VL_MODEL} "
          f"({args.workers} workers over {len(clients)} nodes)")

    def work(fid: str):
        client = clients[next(pick) % len(clients)]
        facts = json.loads((OSS_ROOT / "forms" / fid / "examples"
                            / "sample_case.json").read_text())
        res = fill_via_mapping(fid, facts, args.out)
        if not res.get("ok"):
            return fid, None, [{"issue": "fill_error", "detail": res.get("error")}]
        doc = fitz.open(res["out_pdf"])
        findings = []
        for pno in range(min(len(doc), MAX_PAGES)):
            png = args.out / f"{fid}_p{pno}.png"
            doc[pno].get_pixmap(dpi=130).save(png)
            try:
                findings += _audit_image(client, png)
            except Exception as e:  # noqa: BLE001
                findings.append({"issue": "audit_error", "detail": repr(e)[:80]})
        return fid, res["fields_written"], findings

    clean = flagged = total_findings = done = 0
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(work, f): f for f in forms}
        for fut in as_completed(futs):
            fid, filled, findings = fut.result()
            real = [f for f in findings if f.get("issue") not in
                    ("audit_error", "fill_error")]
            with lock:
                done += 1
                total_findings += len(real)
                if real:
                    flagged += 1
                else:
                    clean += 1
                tag = (f"-> {real[0].get('issue')}: {real[0].get('field','')[:30]}"
                       if real else "(clean)")
                print(f"  [{done}/{len(forms)}] {fid}: {filled} filled, "
                      f"{len(real)} finding(s) {tag}")
                logf.write(json.dumps({"form": fid, "fields_written": filled,
                                       "findings": findings}) + "\n")
                logf.flush()
    print(f"\nclean: {clean} | flagged: {flagged} | total findings: {total_findings}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
