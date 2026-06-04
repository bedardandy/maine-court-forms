#!/usr/bin/env python3
"""Detect shared-AcroForm-field collisions — the worklist for the field split.

Some court source PDFs reuse ONE form field across two semantically different
boxes: every widget with the same field name is the same AcroForm field, so it
always holds the same value and (for accessibility) can carry only one `/TU`.
When those appearances mean different things — e.g. OTH-029 field `2_5` is a
child-DOB table cell on pg4 AND the "Mailing address" line of the embedded
confidential-address affidavit on pg12 — no single mapping key is right in both
places, and a screen reader can't name the field correctly. The fix is a
field-rename SPLIT (one distinct field per appearance); see the accessibility
roadmap.

This is the deterministic, model-free detector that produces the split worklist:
for every field with >1 widget appearance, it compares the appearances' printed
captions and semantic families and flags the ones that DIFFER (a true collision)
while ignoring benign repeats (a docket-number header repeated per page, all
"Docket No." -> not flagged).

    python3 tools/accessibility/shared_field_report.py            # all forms
    python3 tools/accessibility/shared_field_report.py --forms OTH-029
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

import fitz

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent.parent))
from remediate_form import _row_words, _clean_caption  # caption geometry
from tools.label_key_lint import FAMILY_PATTERNS  # caption -> family

OSS_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
FORMS = OSS_ROOT / "forms"
_CHECKISH = {"CheckBox", "RadioButton"}


def _family(text: str) -> str | None:
    fams = {f for f, rx in FAMILY_PATTERNS if rx.search(text or "")}
    return next(iter(fams)) if len(fams) == 1 else None


def _norm(cap: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (cap or "").lower())


def audit_form(fid: str) -> list[dict]:
    fdir = FORMS / fid
    try:
        doc = fitz.open(str(fdir / f"{fid}.pdf"))
    except Exception:  # noqa: BLE001
        return []
    mp = {}
    mp_path = fdir / "mapping.json"
    if mp_path.exists():
        mp = json.loads(mp_path.read_text()).get("map") or {}
    schema = json.loads((fdir / "schema.json").read_text())
    id_by_label = {f.get("label"): f.get("field_id") for f in schema["fields"]}

    # group every widget appearance by its AcroForm field name
    by_name: dict[str, list] = {}
    for pno in range(doc.page_count):
        for w in (doc[pno].widgets() or []):
            r = fitz.Rect(w.rect)
            side = "right" if w.field_type_string in _CHECKISH else "left"
            cap = _clean_caption(_row_words(doc[pno], r, side)) \
                or _clean_caption(_row_words(doc[pno], r, "left" if side == "right" else "right"))
            by_name.setdefault(w.field_name, []).append(
                {"page": pno + 1, "caption": cap[:60], "family": _family(cap),
                 "type": w.field_type_string})
    doc.close()

    flags = []
    for name, apps in by_name.items():
        if len(apps) < 2:
            continue
        # A radio group legitimately shares one field name across its option
        # widgets (one field, N export values) — that is correct AcroForm design,
        # not a collision. Skip any group that is all radio/checkbox kids.
        if all(a["type"] in _CHECKISH for a in apps):
            continue
        caps = {_norm(a["caption"]) for a in apps if a["caption"]}
        fams = {a["family"] for a in apps if a["family"]}
        # collision: appearances carry different captions AND (different families
        # OR one is clearly a distinct label) — not a benign repeated header.
        differing_caption = len(caps) > 1
        differing_family = len(fams) > 1
        if differing_caption and (differing_family or len(caps) == len(
                [a for a in apps if a["caption"]])):
            flags.append({
                "form": fid, "field": id_by_label.get(name, name),
                "mapped_key": mp.get(id_by_label.get(name)),
                "appearances": apps})
    return flags


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--forms", help="comma list (default: all)")
    ap.add_argument("--json", action="store_true", help="emit JSON worklist")
    args = ap.parse_args()
    ids = ([f.strip() for f in args.forms.split(",") if f.strip()] if args.forms
           else sorted(p.parent.name for p in FORMS.glob("*/mapping.json")))
    allf = []
    for fid in ids:
        allf.extend(audit_form(fid))
    if args.json:
        print(json.dumps(allf, indent=2))
    else:
        for f in allf:
            apps = "; ".join(f"pg{a['page']}:'{a['caption']}'({a['family']})"
                             for a in f["appearances"])
            print(f"  {f['form']:14} {f['field']:24} key={f['mapped_key']}")
            print(f"      {apps}")
    print(f"shared_field_report: {len(allf)} collision(s) across {len(ids)} form(s)")
    return 1 if allf else 0


if __name__ == "__main__":
    raise SystemExit(main())
