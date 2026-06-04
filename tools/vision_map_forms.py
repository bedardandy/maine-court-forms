#!/usr/bin/env python3
"""Vision-grounded mapping: assign canonical keys by what the form SHOWS.

On some forms (esp. merged/poorly-authored PDFs) the AcroForm field *name*
lies — a widget sitting on the printed "Name:" line is internally named
"Date mmddyyyy 2", so name-based mapping (the regex heuristic and the text LLM
in ai_map_forms.py) stamps a date onto a name line. This tool ignores the
field name: it renders the blank form with a numbered red marker on every
fillable widget and asks a vision model to map each marker to a canonical key
based on the *visible printed label* beside it.

    python3 tools/vision_map_forms.py --forms AD-FM-GS-JV-PA-PC-292
    python3 tools/vision_map_forms.py --flagged        # all flagged in catalog/vision_audit.json

Writes mapping.json with status "vision-mapped" + the VL model id. Keys are
validated against the canonical contract (reused from ai_map_forms) before
writing. Needs the blank PDFs on disk and the local Qwen-VL cluster.
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
from tools.ai_map_forms import _key_ok  # noqa: E402  (canonical-key validator)

OSS_ROOT = pathlib.Path(__file__).resolve().parent.parent
VL_ENDPOINTS = os.environ.get(
    "MCF_LLM_ENDPOINTS", "http://localhost:8080/v1").split(",")
VL_MODEL = os.environ.get("MCF_VL_MODEL", "qwen3.6-27b")
MAX_PAGES = 4
FILLABLE = ("text", "checkbox", "radio")

SYSTEM = """\
You read a rendered page of a Maine court form. Each fillable field has a small
red number drawn at its top-left corner and a red box around it. Your job: for
each numbered field, look at the PRINTED LABEL on the form next to that box and
assign the canonical fact-key that the field is asking for. Judge ONLY by the
visible printed label and position — ignore any internal field name.

Canonical keys (use these exactly; do not invent others):
- matter.docket_number, matter.court_county, matter.court_location,
  matter.court_type, matter.case_type, matter.filing_date
- parties.<role>.<attr>, role in {plaintiff, defendant, attorney}, attr in
  {full_name, first_name, middle_name, last_name, address, city, state, zip,
  phone, email, date_of_birth}; attorney also allows bar_number.
  (petitioner/applicant -> plaintiff; respondent -> defendant.)
- party.<attr> for the single filing party (same attrs, plus signature).
- Use full_name for a single "Name" box; use first_name/middle_name/last_name
  for separate First/Middle/Last boxes.
- parties.child_1, child_2, ... are numbered minor children ("Child #1",
  "Child #2" blocks): e.g. parties.child_1.full_name, parties.child_2.date_of_birth.
- facts.<snake_case> for form-specific data with no home above
  (e.g. facts.marriage_date, facts.child_full_name, facts.hearing_date).
- today() for a bare "Date"/"Dated" line next to a signature.

Rules: map only fields whose printed label clearly indicates a data value.
Leave a number out entirely if it's a checkbox option, an attestation, or you
can't read a clear label. A box on a "Name" line is a name (never a date); a
box on a "Date of Birth" line is a date_of_birth; a box on a generic "Date"
line by a signature is today().

Return ONLY compact JSON mapping marker number (as a string) to canonical key
for the fields you map: {"map":{"3":"parties.plaintiff.full_name","7":"today()"}}."""


def _render_marked(doc, fields_by_page, page_idx, marker_start):
    """Draw numbered markers on page; return (png_bytes, {marker:int -> field_id})."""
    page = doc[page_idx]
    legend, n = {}, marker_start
    for fid, rect in fields_by_page.get(page_idx, []):
        r = fitz.Rect(rect)
        page.draw_rect(r, color=(1, 0, 0), width=0.7)
        x = max(r.x0 - 11, 1)
        page.insert_text((x, max(r.y0 + 7, 8)), str(n), fontsize=8, color=(1, 0, 0))
        legend[n] = fid
        n += 1
    pix = page.get_pixmap(dpi=150)
    return pix.tobytes("png"), legend, n


def _vl_map(client, png: bytes, temperature: float = 0.0) -> dict:
    b64 = base64.b64encode(png).decode()
    r = client.chat.completions.create(
        model=VL_MODEL, max_tokens=2500, temperature=temperature,
        messages=[{"role": "user", "content": [
            {"type": "text", "text": SYSTEM},
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}}]}],
        extra_body={"chat_template_kwargs": {"enable_thinking": False}})
    txt = r.choices[0].message.content or "{}"
    try:
        return json.loads(txt).get("map", {})
    except json.JSONDecodeError:
        i, j = txt.find("{"), txt.rfind("}")
        return json.loads(txt[i:j + 1]).get("map", {}) if i != -1 else {}


def _map_one(client, fid: str) -> dict:
    fdir = OSS_ROOT / "forms" / fid
    schema = json.loads((fdir / "schema.json").read_text())
    valid_ids = {f["field_id"] for f in schema["fields"]}
    name_to_fid = {f.get("label"): f["field_id"] for f in schema["fields"]}

    doc = fitz.open(str(fdir / f"{fid}.pdf"))
    # group fillable widgets by page using the live PDF widget rects
    by_page: dict[int, list] = {}
    for pno in range(min(len(doc), MAX_PAGES)):
        for w in doc[pno].widgets():
            f = next((x for x in schema["fields"]
                      if x.get("label") == w.field_name), None)
            if f and f.get("type") in FILLABLE:
                by_page.setdefault(pno, []).append((f["field_id"], tuple(w.rect)))

    mp, dropped, n = {}, [], 1
    for pno in range(min(len(doc), MAX_PAGES)):
        if pno not in by_page:
            continue
        png, legend, n = _render_marked(doc, by_page, pno, n)
        try:
            answer = _vl_map(client, png)
        except Exception as e:  # noqa: BLE001
            dropped.append(("page", pno, repr(e)[:60]))
            continue
        for marker, key in answer.items():
            try:
                fid_for = legend.get(int(marker))
            except (ValueError, TypeError):
                fid_for = None
            if fid_for in valid_ids and _key_ok(key):
                mp[fid_for] = key
            else:
                dropped.append((marker, key))
    return {"map": mp, "dropped": dropped}


def _flagged() -> list[str]:
    rep = json.loads((OSS_ROOT / "catalog" / "vision_audit.json").read_text())
    return [f for f, v in rep["forms"].items() if v["result"] == "flagged"]


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--forms", default="")
    ap.add_argument("--flagged", action="store_true",
                    help="re-map all forms flagged in catalog/vision_audit.json")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--log", type=pathlib.Path,
                    default=pathlib.Path("/tmp/vision_map_log.jsonl"))
    args = ap.parse_args()

    if args.forms:
        forms = [f.strip() for f in args.forms.split(",") if f.strip()]
    elif args.flagged:
        forms = _flagged()
    else:
        print("specify --forms or --flagged"); return 2

    clients = [openai.OpenAI(base_url=ep, api_key="none", timeout=240)
               for ep in VL_ENDPOINTS]
    pick = itertools.count()
    lock = threading.Lock()
    logf = args.log.open("w")
    print(f"vision-mapping {len(forms)} forms with {VL_MODEL}")

    def work(fid):
        before = len(json.loads((OSS_ROOT / "forms" / fid / "mapping.json").read_text())
                     .get("map") or {})
        try:
            res = _map_one(clients[next(pick) % len(clients)], fid)
        except Exception as e:  # noqa: BLE001
            return fid, before, None, repr(e)
        (OSS_ROOT / "forms" / fid / "mapping.json").write_text(json.dumps({
            "form_id": fid, "status": "vision-mapped", "model": VL_MODEL,
            "note": "Mapped by a vision model from the rendered form's visible "
                    "labels (set-of-marks), bypassing misleading AcroForm field "
                    "names. Validated against the canonical contract. Not audit-verified.",
            "map": res["map"],
        }, indent=2))
        return fid, before, len(res["map"]), None

    done = 0
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(work, f): f for f in forms}
        for fut in as_completed(futs):
            fid, before, after, err = fut.result()
            with lock:
                done += 1
                if err:
                    print(f"  [{done}/{len(forms)}] {fid}: ERROR {err}")
                else:
                    print(f"  [{done}/{len(forms)}] {fid}: {before}->{after} mapped")
                logf.write(json.dumps({"form": fid, "before": before,
                                       "after": after, "error": err}) + "\n")
                logf.flush()
    return 0


if __name__ == "__main__":
    sys.exit(main())
