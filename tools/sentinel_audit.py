#!/usr/bin/env python3
"""Sentinel-render correctness audit: catch wrong-family / wrong-party box maps.

The value-level visual audit (tools/audit_loop.py) is provenance-blind: a real
phone number on an address line, or the defendant's address on a plaintiff line,
*renders* plausibly, so neither the Qwen-VL consensus nor Opus can see it from
the image (lesson #2). A `verified` form can still hold these — OTH-030 did.

This audit cures the blindness by filling each fact-key with a SELF-DESCRIBING
token: ``party.phone`` -> ``FILER_PHONE``, ``parties.defendant.address`` ->
``DEF_ADDR``. Now the provenance is *printed in the rendered value*. A VL model
reads the visible (caption, value) pairs off the page — something it does
reliably — and we DETERMINISTICALLY check the token's encoded (role, family)
against the box's printed caption:

  caption "Defendant's Telephone" + value "FILER_ADDR"  -> role+family mismatch.

So the VL handles the one thing geometry gets wrong on stacked blocks (which
caption a box belongs to) while the self-describing token handles the one thing
the VL gets wrong (provenance) — neither is asked to judge what it's bad at.

    python3 tools/sentinel_audit.py --forms OTH-030
    python3 tools/sentinel_audit.py --status verified --workers 4 --log /tmp/sa.jsonl

Cluster-only + deterministic; no repo writes, no Opus, no git — safe to run
beside anything. Needs blank PDFs on disk and the local Qwen-VL cluster.
"""
from __future__ import annotations

import argparse
import base64
import itertools
import json
import pathlib
import re
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

import fitz  # PyMuPDF
import openai

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from engine.fill_via_mapping import fill_via_mapping  # noqa: E402
from tools.vision_audit import VL_MODEL, _vl_clients  # noqa: E402
from tools.label_key_lint import FAMILY_PATTERNS  # noqa: E402

OSS_ROOT = pathlib.Path(__file__).resolve().parent.parent

# ---- self-describing sentinel fact object --------------------------------
# token = "<ROLE>_<FIELD>"; ROLE and FIELD are both recoverable from the text.
_ROLE_TOKEN = {"party": "FILER", "plaintiff": "PLF", "defendant": "DEF",
               "attorney": "ATT", "other_party": "OTH",
               "child_1": "CH1", "child_2": "CH2", "child_3": "CH3"}
_FIELD_TOKEN = {"full_name": "NAME", "first_name": "FIRST", "middle_name": "MID",
                "last_name": "LAST", "address": "ADDR", "city": "CITY",
                "state": "STATE", "zip": "ZIP", "phone": "PHONE",
                "email": "EMAIL", "date_of_birth": "DOB", "signature": "SIG"}


def _role_block(role_token: str) -> dict:
    return {fk: f"{role_token}_{ft}" for fk, ft in _FIELD_TOKEN.items()}


SENTINEL = {
    "matter": {"court_location": "COURTLOC", "docket_number": "DOCKETNO",
               "court_county": "COUNTY", "court_type": "COURTTYPE"},
    "party": _role_block("FILER"),
    "parties": {role: _role_block(tok)
                for role, tok in _ROLE_TOKEN.items() if role != "party"},
    "facts": {},
}

# ---- token / caption classifiers -----------------------------------------
_FIELD_FAMILY = {"ADDR": "postal", "CITY": "postal", "STATE": "postal",
                 "ZIP": "postal", "PHONE": "phone", "EMAIL": "email",
                 "DOB": "dob"}
_TOKEN_RE = re.compile(
    r"\b(FILER|PLF|DEF|ATT|OTH|CH1|CH2|CH3)_"
    r"(NAME|FIRST|MID|LAST|ADDR|CITY|STATE|ZIP|PHONE|EMAIL|DOB|SIG)\b")
# definite parties (FILER is role-ambiguous — the filer may BE any role).
_DEFINITE_ROLE = {"PLF": "plaintiff", "DEF": "defendant", "ATT": "attorney",
                  "OTH": "other", "CH1": "child", "CH2": "child", "CH3": "child"}
_CAPTION_ROLE = [
    ("plaintiff", re.compile(r"plaintiff|petitioner|complainant", re.I)),
    ("defendant", re.compile(r"defendant|respondent", re.I)),
    ("attorney", re.compile(r"attorney|counsel|\besq\b|bar no", re.I)),
    ("child", re.compile(r"child|minor", re.I)),
]


def _caption_family(text: str) -> str | None:
    for fam, rx in FAMILY_PATTERNS:
        if rx.search(text or ""):
            return fam
    return None


def _caption_role(text: str) -> str | None:
    hits = {r for r, rx in _CAPTION_ROLE if rx.search(text or "")}
    return next(iter(hits)) if len(hits) == 1 else None  # ambiguous -> skip


def _classify(value: str):
    m = _TOKEN_RE.search(value or "")
    if not m:
        return None
    role, field = m.group(1), m.group(2)
    return role, _DEFINITE_ROLE.get(role), _FIELD_FAMILY.get(field), field


EXTRACT_PROMPT = (
    "This image is one page of a filled court form. Read every field that "
    "contains a typed value. For each, report the printed LABEL nearest to it "
    "(the caption to its left or directly above) and the typed VALUE exactly as "
    "shown. Ignore blank fields and checkboxes. Return ONLY compact JSON: "
    '{"fields":[{"caption":"<printed label>","value":"<typed text>"}]}.')


def _extract(client, png_b64: str) -> list[dict]:
    r = client.chat.completions.create(
        model=VL_MODEL, max_tokens=2000, temperature=0,
        messages=[{"role": "user", "content": [
            {"type": "text", "text": EXTRACT_PROMPT},
            {"type": "image_url",
             "image_url": {"url": f"data:image/png;base64,{png_b64}"}}]}],
        extra_body={"chat_template_kwargs": {"enable_thinking": False}})
    txt = r.choices[0].message.content or "{}"
    try:
        return json.loads(txt).get("fields", [])
    except json.JSONDecodeError:
        i, j = txt.find("{"), txt.rfind("}")
        if i == -1 or j == -1:
            return []
        try:
            return json.loads(txt[i:j + 1]).get("fields", [])
        except json.JSONDecodeError:
            return []


def _compare(caption: str, value: str) -> dict | None:
    """Flag a (caption, value) pair whose token disagrees with the caption."""
    cls = _classify(value)
    if not cls:
        return None
    _role, def_role, fam, field = cls
    cap_fam, cap_role = _caption_family(caption), _caption_role(caption)
    if cap_fam and fam and cap_fam != fam:
        return {"kind": "family", "caption": caption[:50], "value": value,
                "caption_family": cap_fam, "value_family": fam}
    if cap_role and def_role and cap_role != def_role and def_role != "child":
        # role mismatch: caption names one party, the value belongs to another.
        # child captions vary wildly (tables) — too noisy, skip that direction.
        return {"kind": "role", "caption": caption[:50], "value": value,
                "caption_role": cap_role, "value_role": def_role}
    return None


def _mapped_pages(doc, schema, mp, cap=16) -> list[int]:
    fillable = {"text", "char", "combobox", "listbox"}
    want = {f["label"] for f in schema.get("fields", [])
            if f.get("field_id") in mp and f.get("type") in fillable}
    pages = [p for p in range(doc.page_count)
             if any(w.field_name in want for w in (doc[p].widgets() or []))]
    return pages[:cap] or list(range(min(doc.page_count, 3)))


def audit_form(fid: str, client, outdir: pathlib.Path) -> dict:
    fdir = OSS_ROOT / "forms" / fid
    schema = json.loads((fdir / "schema.json").read_text())
    mp = json.loads((fdir / "mapping.json").read_text()).get("map") or {}
    if not mp:
        return {"form": fid, "status": "no-map"}
    res = fill_via_mapping(fid, SENTINEL, outdir)
    if not res.get("ok"):
        return {"form": fid, "status": "fill-error", "reason": res.get("error")}
    doc = fitz.open(res["out_pdf"])
    flags = []
    for p in _mapped_pages(doc, schema, mp):
        b64 = base64.b64encode(doc[p].get_pixmap(dpi=150).tobytes("png")).decode()
        try:
            pairs = _extract(client, b64)
        except Exception:  # noqa: BLE001
            continue
        for pair in pairs:
            f = _compare(str(pair.get("caption", "")), str(pair.get("value", "")))
            if f:
                f["page"] = p + 1
                flags.append(f)
    doc.close()
    return {"form": fid, "status": "flagged" if flags else "clean",
            "flags": flags}


def _select(status_filter: str | None) -> list[str]:
    out = []
    for p in sorted(OSS_ROOT.glob("forms/*/mapping.json")):
        m = json.loads(p.read_text())
        fid = p.parent.name
        if status_filter and m.get("status") != status_filter:
            continue
        if not (m.get("map")) or not (p.parent / f"{fid}.pdf").exists():
            continue
        out.append(fid)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--forms", default="")
    ap.add_argument("--status", default="verified",
                    help="only audit forms with this status (default: verified)")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--out", type=pathlib.Path, default=pathlib.Path("/tmp/sa"))
    ap.add_argument("--log", type=pathlib.Path,
                    default=pathlib.Path("/tmp/sentinel_audit.jsonl"))
    args = ap.parse_args()
    forms = ([f.strip() for f in args.forms.split(",") if f.strip()]
             if args.forms else _select(args.status))
    clients = _vl_clients()
    args.out.mkdir(parents=True, exist_ok=True)
    pick = itertools.count()
    lock = threading.Lock()
    logf = args.log.open("w")
    print(f"sentinel-auditing {len(forms)} form(s) with {VL_MODEL} "
          f"({args.workers} workers / {len(clients)} nodes)")
    n_flagged = 0

    def work(fid):
        return audit_form(fid, clients[next(pick) % len(clients)], args.out)

    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(work, f): f for f in forms}
        for fut in as_completed(futs):
            r = fut.result()
            with lock:
                logf.write(json.dumps(r) + "\n")
                logf.flush()
                if r["status"] == "flagged":
                    n_flagged += 1
                    print(f"  [FLAG] {r['form']}: "
                          + "; ".join(f"{x['kind']} '{x['value']}' under "
                                      f"'{x['caption']}'" for x in r["flags"][:4]))
                elif r["status"] not in ("clean",):
                    print(f"  [{r['status']}] {r['form']}")
    print(f"done: {n_flagged} flagged of {len(forms)}")
    logf.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
