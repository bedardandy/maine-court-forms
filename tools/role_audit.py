#!/usr/bin/env python3
"""Deterministic role / checkbox mapping guard.

Two latent mapping-bug classes the value-level fill-audit cannot see, because
both produce a *plausible* rendered value while being semantically wrong:

1. **Opponent pinned to a fixed role on a self-role-select form.** Forms where
   the filer chooses their own role ("I am the ( ) plaintiff ( ) defendant")
   must key "the other party" to the role-neutral ``parties.other_party.*`` —
   never to ``parties.plaintiff.*`` / ``parties.defendant.*``. A fixed role
   collides with the filer whenever the filer is that role, and a single
   plaintiff-filing sample case hides it. (See OTH-045 / CV-256.)

2. **A checkbox driven by a non-boolean value.** A checkbox is boolean: it is
   checked by a token (X / Yes / 1 / true), not by a name, address or enum
   string. Keying a checkbox to ``parties.*.full_name`` or ``matter.court_type``
   checks the box whenever the value merely exists, which over-checks role
   boxes and every option of an enum-radio. (See OTH-030: 24 spurious checks.)

Run with no args to audit every form; exits non-zero if any violation is found,
so it can gate CI / a pre-push hook. ``--forms A,B`` limits the scope.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re

import fitz

OSS_ROOT = pathlib.Path(__file__).resolve().parent.parent
FORMS = OSS_ROOT / "forms"

# Form lets the filer pick their own role -> any fixed-role opponent is suspect.
SELECT_RE = re.compile(
    r"i am\s*\(?\s*(select|check)\s*one"
    r"|i am\s+the\s+(plaintiff|defendant|petitioner|respondent|landlord|tenant)"
    r"|\(\s*(select|check)\s*one\s*\)",
    re.I,
)
OTHER_RE = re.compile(
    r"other party|opposing party|name of the other", re.I)
FIXED_ROLES = ("parties.plaintiff", "parties.defendant")
# Keys a checkbox must never be driven by (they are not boolean).
NON_BOOL_SUFFIX = (
    "full_name", "first_name", "middle_name", "last_name",
    "address", "city", "state", "zip", "phone", "email",
    "date_of_birth", "court_type", "docket_number",
)


def _role(key: str | None) -> str | None:
    if not isinstance(key, str):
        return None
    if key.startswith("parties."):
        return ".".join(key.split(".")[:2])
    if key == "party" or key.startswith("party."):
        return "party"
    return None


def _is_non_bool_value_key(key: str | None) -> bool:
    if not isinstance(key, str):
        return False
    tail = key.split(".")[-1]
    return tail in NON_BOOL_SUFFIX or key in ("matter.court_county",)


def audit_form(fid: str) -> list[dict]:
    """Return a list of violation dicts for one form (empty == clean)."""
    fdir = FORMS / fid
    try:
        mapping = json.loads((fdir / "mapping.json").read_text())
        schema = json.loads((fdir / "schema.json").read_text())
        doc = fitz.open(str(fdir / f"{fid}.pdf"))
    except Exception:  # noqa: BLE001 — missing PDF / unreadable: nothing to audit
        return []
    mp = mapping.get("map") or {}
    fillable = {"text", "char", "combobox", "listbox"}
    viol: list[dict] = []

    full_text = " ".join(pg.get_text() for pg in doc)
    self_select = bool(SELECT_RE.search(full_text))

    # widget type per AcroForm field-name (a field is one type)
    name_type: dict[str, str] = {}
    for pno in range(doc.page_count):
        for w in (doc[pno].widgets() or []):
            name_type.setdefault(w.field_name, w.field_type_string)
    name_to_fid = {f.get("label"): f["field_id"]
                   for f in schema.get("fields", []) if f.get("field_id")}
    # A field_id may back several widgets; a case-folded field-name collision
    # ("Plaintiff" text + "plaintiff" checkbox) collapses a caption AND a
    # checkbox onto one id. There the value mapping legitimately serves the
    # TEXT widget and the engine refuses to check the box on a name, so it is
    # NOT a violation. Only a field_id whose widgets are ALL checkbox/radio is.
    fid_types: dict[str, set] = {}
    for name, t in name_type.items():
        fi = name_to_fid.get(name)
        if fi:
            fid_types.setdefault(fi, set()).add(t)

    # (1) opponent pinned to a fixed role on a self-select form
    if self_select:
        for pno in range(min(doc.page_count, 16)):
            pg = doc[pno]
            wl = []
            for w in (pg.widgets() or []):
                f = next((x for x in schema["fields"]
                          if x.get("label") == w.field_name
                          and x.get("type") in fillable), None)
                if f:
                    wl.append((f["field_id"], fitz.Rect(w.rect)))
            if not wl:
                continue
            for b in pg.get_text("dict")["blocks"]:
                for ln in b.get("lines", []):
                    spans = ln.get("spans", [])
                    txt = "".join(s["text"] for s in spans)
                    if not OTHER_RE.search(txt):
                        continue
                    y0 = min(s["bbox"][1] for s in spans)
                    y1 = max(s["bbox"][3] for s in spans)
                    x1 = max(s["bbox"][2] for s in spans)
                    same = [w for w in wl
                            if (w[1].y0 < y1 and w[1].y1 > y0)
                            and w[1].x0 >= x1 - 40]
                    below = [w for w in wl if 0 <= (w[1].y0 - y1) <= 26]
                    cand = (sorted(same, key=lambda w: w[1].x0)
                            or sorted(below, key=lambda w: w[1].y0))
                    if not cand:
                        continue
                    fid_id = cand[0][0]
                    if _role(mp.get(fid_id)) in FIXED_ROLES:
                        viol.append({
                            "form": fid, "kind": "opponent-fixed-role",
                            "field_id": fid_id, "key": mp.get(fid_id),
                            "label": txt.strip()[:60],
                            "detail": "self-role-select form keys 'the other "
                                      "party' to a fixed role; use "
                                      "parties.other_party.*",
                        })

    # (2) checkbox / radio driven by a non-boolean value
    for fid_id, key in mp.items():
        types = fid_types.get(fid_id, set())
        sole_check = types and types <= {"CheckBox", "RadioButton"}
        if sole_check and _is_non_bool_value_key(key):
            viol.append({
                "form": fid, "kind": "checkbox-non-boolean",
                "field_id": fid_id, "key": key,
                "detail": "checkbox/radio keyed to a non-boolean value; a "
                          "checkbox must be driven by a boolean fact / token",
            })
    doc.close()
    return viol


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--forms", help="comma list (default: all)")
    ap.add_argument("--quiet", action="store_true",
                    help="only print the summary line")
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
            print(f"  [{v['kind']}] {v['form']} {v['field_id']} -> "
                  f"{v.get('key')!r}  {v.get('label', v['detail'])}")
    by_kind: dict[str, int] = {}
    for v in all_viol:
        by_kind[v["kind"]] = by_kind.get(v["kind"], 0) + 1
    print(f"role_audit: {len(all_viol)} violation(s) across {len(ids)} form(s)"
          f"{' — ' + ', '.join(f'{k}={n}' for k, n in by_kind.items()) if by_kind else ''}")
    return 1 if all_viol else 0


if __name__ == "__main__":
    raise SystemExit(main())
