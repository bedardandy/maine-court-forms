#!/usr/bin/env python3
"""Re-map a form from scratch against its CURRENT blank PDF (vision-grounded).

Used when a form drifted upstream and its widget *names* changed, so the shipped
schema no longer matches the live widgets (vision_map_forms.py can't legend a
drifted form because it keys markers off schema.label == widget.field_name).

This legends markers off the LIVE widgets instead, asks the Qwen-VL cluster to
map each marker to a canonical key by the printed label (same prompt as
vision_map_forms), and rewrites mapping.json + schema.json + fields.csv for the
new PDF. field_id is derived from the (new) widget name; label IS the widget
name, so the engine fills the right AcroForm field.

    MCF_LLM_ENDPOINTS=http://host1:8080/v1,http://host2:8080/v1 \
        python3 tools/remap_from_pdf.py --forms CR-006

Needs the current blank PDF on disk and the local Qwen-VL cluster.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import pathlib
import re
import sys

import fitz
import openai

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from tools.ai_map_forms import _key_ok  # noqa: E402
from tools.vision_map_forms import SYSTEM, _vl_map  # noqa: E402

OSS_ROOT = pathlib.Path(__file__).resolve().parent.parent
ENDPOINTS = os.environ.get("MCF_LLM_ENDPOINTS", "http://localhost:8080/v1").split(",")
VL_MODEL = os.environ.get("MCF_VL_MODEL", "qwen3.6-27b")
MAX_PAGES = 8
FILLABLE = ("Text", "CheckBox", "RadioButton")


def _slug(name: str, used: set) -> str:
    s = re.sub(r"[^a-z0-9]+", "_", (name or "field").lower()).strip("_") or "field"
    base, i = s, 2
    while s in used:
        s = f"{base}_{i}"; i += 1
    used.add(s)
    return s


def _widgets(doc):
    """[(field_id, label, type, page, rect)] for every fillable widget."""
    rows, used = [], set()
    for pno in range(min(doc.page_count, MAX_PAGES)):
        for w in (doc[pno].widgets() or []):
            t = w.field_type_string
            if not any(t.startswith(k) for k in FILLABLE):
                continue
            rows.append((_slug(w.field_name, used), w.field_name,
                         "checkbox" if "Check" in t else "radio" if "Radio" in t else "text",
                         pno, tuple(round(c, 1) for c in w.rect)))
    return rows


def _render_marked(doc, rows, page_idx, marker_start):
    page = doc[page_idx]
    legend, n = {}, marker_start
    for fid, _label, _type, pno, rect in rows:
        if pno != page_idx:
            continue
        r = fitz.Rect(rect)
        page.draw_rect(r, color=(1, 0, 0), width=0.7)
        page.insert_text((max(r.x0 - 11, 1), max(r.y0 + 7, 8)), str(n),
                         fontsize=8, color=(1, 0, 0))
        legend[n] = fid
        n += 1
    return page.get_pixmap(dpi=150).tobytes("png"), legend, n


def remap(fid: str, client) -> dict:
    fdir = OSS_ROOT / "forms" / fid
    doc = fitz.open(str(fdir / f"{fid}.pdf"))
    rows = _widgets(doc)
    valid = {r[0] for r in rows}
    mp, dropped, n = {}, [], 1
    for pno in range(min(doc.page_count, MAX_PAGES)):
        if not any(r[3] == pno for r in rows):
            continue
        png, legend, n = _render_marked(doc, rows, pno, n)
        try:
            answer = _vl_map(client, png)
        except Exception as e:  # noqa: BLE001
            dropped.append(("page", pno, repr(e)[:60])); continue
        for marker, key in answer.items():
            try:
                f = legend.get(int(marker))
            except (ValueError, TypeError):
                f = None
            if f in valid and _key_ok(key):
                mp[f] = key
            else:
                dropped.append((marker, key))
    doc.close()

    # write fields.csv, schema.json, mapping.json for the new PDF
    with open(fdir / "fields.csv", "w", newline="") as fh:
        wr = csv.writer(fh)
        wr.writerow(["field_id", "label", "type", "page", "rect"])
        for f, label, t, pno, rect in rows:
            wr.writerow([f, label, t, pno, ",".join(str(c) for c in rect)])
    schema = {"form_id": fid, "fields": [
        {"field_id": f, "label": label, "type": t, "page": pno, "rect": list(rect)}
        for f, label, t, pno, rect in rows]}
    (fdir / "schema.json").write_text(json.dumps(schema, indent=2) + "\n")
    mapping = {"form_id": fid, "status": "vision-mapped", "model": VL_MODEL,
               "note": "Re-mapped from the current blank after upstream drift "
                       "(tools/remap_from_pdf.py).", "map": mp}
    (fdir / "mapping.json").write_text(json.dumps(mapping, indent=2) + "\n")
    # Keep form.yaml's automation flags in sync: once the form is re-mapped
    # from the current blank, any old engine recipe targeted the superseded
    # revision and mapping.json is the fill path. (CR-004/CR-198/MJ-007
    # drifted exactly this way: form.yaml kept saying automation_status:
    # recipe after a remap, so the repo counted 69 recipe forms against the
    # 66 in mapping.json ground truth.)
    fy = fdir / "form.yaml"
    if fy.exists():
        t = fy.read_text()
        t = t.replace("has_fill_recipe: true", "has_fill_recipe: false")
        t = t.replace("automation_status: recipe",
                      "automation_status: schema-only")
        fy.write_text(t)
    return {"form_id": fid, "widgets": len(rows), "mapped": len(mp), "dropped": len(dropped)}


def main() -> int:
    ap = argparse.ArgumentParser(description="Re-map drifted forms from the current PDF")
    ap.add_argument("--forms", required=True, help="comma list")
    args = ap.parse_args()
    client = openai.OpenAI(base_url=ENDPOINTS[0], api_key="none", timeout=240)
    for fid in [f.strip() for f in args.forms.split(",") if f.strip()]:
        if not (OSS_ROOT / "forms" / fid / f"{fid}.pdf").exists():
            print(f"  {fid}: no local PDF"); continue
        r = remap(fid, client)
        print(f"  {fid}: {r['widgets']} widgets, {r['mapped']} mapped, {r['dropped']} dropped")
    return 0


if __name__ == "__main__":
    sys.exit(main())
