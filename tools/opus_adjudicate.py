#!/usr/bin/env python3
"""Opus adjudication pass over vision-mapped (draft) court-form mappings.

The Qwen-VL remap (tools/remap_from_pdf.py) produces draft mappings fast but errs
on ambiguous fields (e.g. a bail-surety block mapped onto plaintiff roles). This
sends each field's printed caption (read from the live PDF) plus the draft
canonical key to Opus via the local ``claude`` CLI (session-auth — the env
ANTHROPIC_API_KEY is an OAuth token rejected by the Messages API, so it is
stripped) and asks Opus to correct keys that don't match the caption. Promotes
mapping.json status to ``opus-adjudicated``.

    python3 tools/opus_adjudicate.py --forms CR-004,CR-006

Text-only (caption-grounded); needs the blank PDF on disk.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import pathlib
import re
import subprocess
import sys

import fitz

ROOT = pathlib.Path(__file__).resolve().parent.parent

VOCAB = """\
matter.{docket_number,court_county,court_location,court_type,case_type,filing_date}
parties.<role>.<attr> where role in {plaintiff,defendant,attorney}
  (petitioner/applicant->plaintiff; respondent->defendant) and attr in
  {full_name,first_name,middle_name,last_name,address,city,state,zip,phone,email,
  date_of_birth}; attorney also allows bar_number.
parties.child_1.<attr>, parties.child_2.<attr>, ... for numbered minor children.
party.<attr> for the single filing party (same attrs, plus signature).
facts.<snake_case> for form-specific data with no home above.
today()  signature"""

SYSTEM = (
    "You audit a DRAFT field-mapping for a Maine court form. A vision model "
    "assigned each fillable field a canonical fact-key. Catch keys that do not "
    "match the field's printed caption and correct them, using ONLY this "
    "controlled vocabulary (facts.<snake_case> for anything with no clean home):\n"
    + VOCAB +
    "\n\nReturn ONLY compact JSON: {\"corrections\":{\"<field_id>\":\"<correct_key>\"},"
    "\"remove\":[\"<field_id>\"],\"notes\":\"<one line>\"}. Include a field_id in "
    "\"corrections\" ONLY if you change its key; in \"remove\" if it should not be "
    "mapped (an instruction, attestation, or checkbox option). Judge by the "
    "caption: a 'City/Town of residence' is never a last_name; a name line is a "
    "name, never a date; a bare 'Date' by a signature is today(). On a bail "
    "surety/bond form the person posting bail is the filing party (party.*) or "
    "facts.*, not the plaintiff. If every key is right, return empty corrections.")


def _captions(fid: str) -> dict:
    """field_id -> printed caption, from the live PDF (left of text, right of checkbox)."""
    fdir = ROOT / "forms" / fid
    rows = list(csv.DictReader(open(fdir / "fields.csv")))
    doc = fitz.open(str(fdir / f"{fid}.pdf"))
    words_by_page = {p: doc[p].get_text("words") for p in range(doc.page_count)}
    caps = {}
    for r in rows:
        try:
            x0, y0, x1, y1 = [float(c) for c in r["rect"].split(",")]
            pno = int(r["page"])
        except (ValueError, KeyError):
            caps[r["field_id"]] = r.get("label", ""); continue
        words = words_by_page.get(pno, [])
        ymid = (y0 + y1) / 2
        is_cb = (r.get("type") in ("checkbox", "radio"))
        row = [w for w in words if w[1] <= ymid <= w[3]]
        side = ([w for w in row if w[0] >= x1 - 2] if is_cb
                else [w for w in row if w[2] <= x0 + 2])
        side.sort(key=lambda w: w[0])
        seg = side[:8] if is_cb else side[-10:]
        cap = re.sub(r"\s+", " ", " ".join(w[4] for w in seg)).strip()[:120]
        caps[r["field_id"]] = cap or r.get("label", "")
    doc.close()
    return caps


def _opus(system: str, user: str, timeout: float = 1500.0) -> str:
    env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
    p = subprocess.run(["claude", "-p", "--output-format", "json"],
                       input=system + "\n\n---\n\n" + user,
                       capture_output=True, text=True, env=env, timeout=timeout)
    if p.returncode != 0:
        raise RuntimeError(f"claude CLI failed: {p.stderr[:200]}")
    return json.loads(p.stdout)["result"]


def _parse_json(txt: str) -> dict:
    try:
        return json.loads(txt)
    except json.JSONDecodeError:
        i, j = txt.find("{"), txt.rfind("}")
        return json.loads(txt[i:j + 1]) if i != -1 else {}


def adjudicate(fid: str) -> dict:
    fdir = ROOT / "forms" / fid
    mapping = json.loads((fdir / "mapping.json").read_text())
    mp = mapping["map"]
    caps = _captions(fid)
    lines = [f"{f} | caption={caps.get(f,'')!r} | draft_key={k}" for f, k in mp.items()]
    user = f"Form: {fid}\n\nFields (field_id | caption | draft_key):\n" + "\n".join(lines)
    out = _parse_json(_opus(SYSTEM, user))
    corr = {f: out.get("corrections", {})[f] for f in out.get("corrections", {})
            if f in mp and out["corrections"][f] != mp[f]}
    removed = [f for f in out.get("remove", []) if f in mp]
    for f, k in corr.items():
        mp[f] = k
    for f in removed:
        mp.pop(f, None)
    mapping["map"] = mp
    mapping["status"] = "opus-adjudicated"
    mapping["adjudication"] = {"model": "claude-opus (cli)", "corrected": corr,
                               "removed": removed, "notes": out.get("notes", "")}
    (fdir / "mapping.json").write_text(json.dumps(mapping, indent=2) + "\n")
    return {"form_id": fid, "fields": len(mp), "corrected": len(corr),
            "removed": len(removed), "notes": out.get("notes", "")[:90]}


def main() -> int:
    ap = argparse.ArgumentParser(description="Opus adjudication of vision-mapped court drafts")
    ap.add_argument("--forms", required=True)
    args = ap.parse_args()
    for fid in [f.strip() for f in args.forms.split(",") if f.strip()]:
        try:
            r = adjudicate(fid)
            print(f"  {fid}: {r['fields']} fields, {r['corrected']} corrected, "
                  f"{r['removed']} removed | {r['notes']}")
        except Exception as e:  # noqa: BLE001
            print(f"  {fid}: ADJUDICATION FAILED: {repr(e)[:120]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
