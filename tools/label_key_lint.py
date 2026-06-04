#!/usr/bin/env python3
"""Caption-vs-key semantic-family lint for ``mapping.json``.

A whole bug class the value-level fill-audit cannot see (lesson #2 / #10): a
field keyed to a value of the WRONG semantic family still *renders* plausibly,
so the visual gate approves it. A box captioned "Telephone number:" filled with
an address looks fine in the image; only the caption-vs-key relationship reveals
the error. The Opus-judge *fix* path is especially prone to this — to clear a
visual audit it will remap a mailing-address box to a phone value (it renders as
a plausible string), so the judge's own output needs this guard.

The discriminator is the widget's **nearest printed caption**, NOT its AcroForm
field-name. Field-names are unreliable: a continuation widget in a stacked
contact block is often named for the block header ("Mailing Address 3_2") while
physically sitting on the "Cell phone:" row — there the phone mapping is CORRECT
and the field-name is a red herring. The printed caption to the widget's left is
ground truth.

Semantic families (mutually exclusive — a box of one must not hold another):
``postal`` (street/mailing/physical address, city, town, state, ZIP — collapsed
into one family because a multi-line address block shares one caption),
``phone``, ``email``, ``dob``. A caption naming MORE than one family is a
combined blob ("Name, current address, telephone number…") and is not flagged.

Run with no args to lint every form; exits non-zero on any violation so it can
gate CI / a pre-push hook. ``--forms A,B`` limits scope. This is a review aid:
every hit is a real caption/key disagreement, but confirm against the render
before "fixing" — see lesson #10 (auto-fixes are the thing this guards against).
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re

import fitz

OSS_ROOT = pathlib.Path(__file__).resolve().parent.parent
FORMS = OSS_ROOT / "forms"

# caption text -> semantic family (order matters: specific before generic).
FAMILY_PATTERNS = [
    ("email", re.compile(r"\be-?mail\b", re.I)),
    ("phone", re.compile(r"\b(telephone|phone|fax|cell|mobile)\b", re.I)),
    ("dob", re.compile(r"\b(date of birth|birth date|d\.?o\.?b\.?)\b", re.I)),
    ("postal", re.compile(
        r"\b(mailing address|street address|physical address|home address|"
        r"work address|address|zip|city|town)\b", re.I)),
]
# mapped-key tail -> semantic family.
KEY_FAMILY = {
    "email": "email", "phone": "phone", "date_of_birth": "dob",
    "address": "postal", "city": "postal", "state": "postal", "zip": "postal",
}
EXCL = {"email", "phone", "dob", "postal"}

# (form, field_id) pairs the caption heuristic flags but a sentinel fill+render
# proves CORRECT — residual caption misattribution on dense stacked contact
# blocks, where the flagged widget's true printed caption is the row above/below
# the one the geometry picked. Confirmed by filling each per-key with a distinct
# token and reading which box it lands in. Keep this list short and evidenced;
# never add a pair without that sentinel-render confirmation.
ALLOWLIST = {
    ("FM-042", "email_2"),   # box renders party.email under the Email: line
    ("FM-068", "email_2"),   # "
    ("FM-070", "email_2"),   # "
    ("MJBVB-018", "telephone"),  # mailing box->addr, telephone box->phone both OK
}


def _caption_families(text: str) -> set[str]:
    return {fam for fam, rx in FAMILY_PATTERNS if rx.search(text or "")}


def _key_family(key: str | None) -> str | None:
    if not isinstance(key, str):
        return None
    return KEY_FAMILY.get(key.split(".")[-1])


def _nearest_caption(page: "fitz.Page", rect: "fitz.Rect") -> str:
    """Printed text immediately left of a widget on the SAME row.

    Picks the span left of the widget whose vertical center is closest to the
    widget's center (same row), then rightmost (nearest the box). Same-row
    matching is what separates a box's own caption from the label of the line
    below it — the failure that made an earlier x-only heuristic misread a
    stacked "mailing address:" / "telephone number:" pair.
    """
    cy = (rect.y0 + rect.y1) / 2
    # A caption must sit on the widget's OWN row. An indented continuation
    # widget (line 2/3 of a stacked "Mailing Address" block) has no left label
    # of its own; without this tolerance the nearest left text is borrowed from
    # an adjacent row ("Phone:" one line below), which manufactures a false
    # mismatch. Require the caption's vertical center to be within ~60% of the
    # widget height of the widget's center — same printed row, not the next one.
    row_tol = max(4.0, 0.6 * (rect.y1 - rect.y0))
    best = None  # (row_dist, -x1, text)
    for blk in page.get_text("dict")["blocks"]:
        for ln in blk.get("lines", []):
            for sp in ln.get("spans", []):
                x0, y0, x1, y1 = sp["bbox"]
                if x1 > rect.x0 + 6:          # must be left of the box
                    continue
                if rect.x0 - x1 > 280:        # too far left to be the caption
                    continue
                row_dist = abs((y0 + y1) / 2 - cy)
                if row_dist > row_tol:        # not on the widget's own row
                    continue
                cand = (round(row_dist, 1), -x1, sp["text"])
                if best is None or cand < best:
                    best = cand
    return best[2].strip() if best else ""


def audit_form(fid: str) -> list[dict]:
    fdir = FORMS / fid
    try:
        mp = (json.loads((fdir / "mapping.json").read_text()).get("map") or {})
        schema = json.loads((fdir / "schema.json").read_text())
        doc = fitz.open(str(fdir / f"{fid}.pdf"))
    except Exception:  # noqa: BLE001 — missing/unreadable: nothing to lint
        return []
    label_to_id = {f.get("label"): f["field_id"]
                   for f in schema.get("fields", []) if f.get("field_id")}
    id_to_key = mp
    viol: list[dict] = []
    for pno in range(doc.page_count):
        for w in (doc[pno].widgets() or []):
            if w.field_type_string not in ("Text", "ComboBox", "ListBox"):
                continue
            fid_id = label_to_id.get(w.field_name)
            if not fid_id or (fid, fid_id) in ALLOWLIST:
                continue
            kf = _key_family(id_to_key.get(fid_id))
            if kf not in EXCL:
                continue
            cap = _nearest_caption(doc[pno], fitz.Rect(w.rect))
            fams = _caption_families(cap)
            if not fams or len(fams) > 1:   # uncaptioned or combined blob
                continue
            if kf not in fams:
                viol.append({
                    "form": fid, "field_id": fid_id,
                    "key": id_to_key.get(fid_id), "page": pno + 1,
                    "caption": cap[:48], "caption_family": next(iter(fams)),
                    "key_family": kf,
                })
    doc.close()
    return viol


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--forms", help="comma list (default: all)")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()
    if args.forms:
        ids = [f.strip() for f in args.forms.split(",") if f.strip()]
    else:
        ids = sorted(p.parent.name for p in FORMS.glob("*/mapping.json"))
    all_viol: list[dict] = []
    for fid in ids:
        all_viol.extend(audit_form(fid))
    if not args.quiet:
        for v in all_viol:
            print(f"  {v['form']:22} pg{v['page']} caption='{v['caption']}' "
                  f"({v['caption_family']}) -> {v['key']!r} ({v['key_family']})")
    print(f"label_key_lint: {len(all_viol)} caption/key mismatch(es) "
          f"across {len(ids)} form(s)")
    return 1 if all_viol else 0


if __name__ == "__main__":
    raise SystemExit(main())
