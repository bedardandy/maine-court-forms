#!/usr/bin/env python3
"""Use a local LLM to map a form's field labels to canonical fact-keys.

The regex heuristic in scaffold_forms.py maps ~34% of fillable fields on
average. An LLM reads labels semantically ("Name of Petitioner's Attorney" ->
parties.attorney.full_name, "Date of Marriage" -> facts.marriage_date), lifting
both coverage and correctness. Output is constrained to the canonical fact
object (docs/integrations/README.md) and validated before anything is written;
invalid keys are dropped, never invented into the artifact.

    python3 tools/ai_map_forms.py --limit 100        # lowest-coverage schema-only forms
    python3 tools/ai_map_forms.py --forms AD-001,CV-001

Runs against the local Qwen cluster (OpenAI-compatible endpoints) — no API key
needed. Writes mapping.json with status "ai-mapped" + the model id, distinct
from "draft-heuristic" and "recipe".
"""
from __future__ import annotations

import argparse
import itertools
import json
import os
import pathlib
import re
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

import openai

OSS_ROOT = pathlib.Path(__file__).resolve().parent.parent
MODEL = os.environ.get("MCF_LLM_MODEL", "qwen3.6-27b")
ENDPOINTS = os.environ.get(
    "MCF_LLM_ENDPOINTS", "http://localhost:8080/v1").split(",")

# Canonical keys the model is allowed to emit (docs/integrations/README.md).
_PARTY_ATTRS = ("full_name", "first_name", "middle_name", "last_name",
                "address", "city", "state", "zip", "phone",
                "email", "date_of_birth", "signature")
ALLOWED_EXACT = {
    "matter.docket_number", "matter.court_county", "matter.court_location",
    "matter.court_type", "matter.case_type", "matter.filing_date", "today()",
} | {f"party.{a}" for a in _PARTY_ATTRS}
_PARTIES_RE = re.compile(
    r"^parties\.(plaintiff|defendant|attorney|child_\d+)\."
    r"(full_name|first_name|middle_name|last_name|address|city|state|zip|"
    r"phone|email|date_of_birth|bar_number)$")
_FACTS_RE = re.compile(r"^facts\.[a-z0-9_]+$")


def _key_ok(key: str) -> bool:
    return (key in ALLOWED_EXACT or bool(_PARTIES_RE.match(key))
            or bool(_FACTS_RE.match(key)))


SYSTEM = """\
You map fields on Maine Judicial Branch court forms to a canonical fact object \
so that automated fillers and integration adapters can populate them. You are \
precise and conservative: a wrong mapping puts the wrong data on a legal \
document, which is worse than leaving a field unmapped.

# The canonical fact object

Every mapped value is a dotted key into this fixed shape. Do NOT invent keys \
outside it.

- matter.docket_number, matter.court_county, matter.court_location,
  matter.court_type, matter.case_type, matter.filing_date
- parties.<role>.<attr> where <role> is exactly one of plaintiff, defendant, or
  attorney, and <attr> is one of: full_name, first_name, middle_name, last_name,
  address, city, state, zip, phone, email, date_of_birth. attorney additionally
  allows bar_number.
- party.<attr> (the single filing party as a flat object): full_name,
  first_name, middle_name, last_name, address, city, state, zip, phone, email,
  date_of_birth, signature.
- Use full_name for a single "Name" box; use first_name/middle_name/last_name
  only for forms with separate First/Middle/Last name boxes.
- parties.child_1, child_2, ... are numbered minor children: a "Child #1 Name"
  field -> parties.child_1.full_name, "Child #2 Date of Birth" ->
  parties.child_2.date_of_birth, etc.
- facts.<snake_case_name> for form-specific data that has no home above
  (e.g. facts.marriage_date, facts.separation_date, facts.grounds,
  facts.property_address, facts.child_full_name). Use lowercase snake_case.
- today() for a field that should be stamped with the current/signing date
  (a bare "Date" or "Dated" line next to a signature).

# Role mapping

Maine forms use petitioner/plaintiff/applicant for the moving party and
respondent/defendant for the other side. Normalize:
- petitioner / plaintiff / applicant  -> parties.plaintiff.*
- respondent / defendant              -> parties.defendant.*
- the filing party's own generic contact block (no opposing party named)
  -> party.*
- any attorney / counsel / "attorney for ..." block -> parties.attorney.*

# Rules

1. Map only fields that capture a concrete data value. Leave UNMAPPED (omit
   from the output): checkboxes/radios that select an option, attestation and
   "I swear/acknowledge" lines, instructional text, headers, county-venue
   checkboxes, and anything whose label you can't confidently tie to a key.
2. Date of birth -> *.date_of_birth. A place of birth, marriage date, service
   date, etc. are NOT dates of birth — use facts.* (e.g. facts.place_of_birth,
   facts.marriage_date) or leave unmapped.
3. A combined "Name and Bar Number" field -> parties.attorney.bar_number.
4. Prefer the most specific role. "Name of Petitioner" -> parties.plaintiff.full_name,
   not party.full_name.
5. Signature lines -> party.signature (or omit). A "Date"/"Dated" line beside a
   signature -> today().
6. When in doubt, leave it unmapped. Coverage is good; wrong data is not.

# Worked example

Fields:
  location (text, "LOCATION")
  docket_no (text, "Docket No.")
  name_of_petitioner (text, "Name of Petitioner")
  date_of_birth (text, "Date of Birth")
  place_of_birth (text, "Place of Birth")
  attorney_name (text, "Attorney Name")
  bar_no (text, "Bar Number")
  i_swear_the_above_is_true (checkbox, "I swear the above is true")
  date (text, "Dated")

Correct mapping:
  location -> matter.court_location
  docket_no -> matter.docket_number
  name_of_petitioner -> parties.plaintiff.full_name
  date_of_birth -> party.date_of_birth
  place_of_birth -> facts.place_of_birth
  attorney_name -> parties.attorney.full_name
  bar_no -> parties.attorney.bar_number
  date -> today()
  (i_swear_the_above_is_true is omitted — it's an attestation checkbox)

Return your answer using the provided JSON schema: a list of {field_id,
canonical_key} objects for the fields you choose to map. Omit fields you leave
unmapped."""

OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "mappings": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "field_id": {"type": "string"},
                    "canonical_key": {"type": "string"},
                },
                "required": ["field_id", "canonical_key"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["mappings"],
    "additionalProperties": False,
}


def _fillable(fields: list[dict]) -> list[dict]:
    return [f for f in fields if f.get("type") in ("text", "checkbox", "radio")]


def _coverage(fdir: pathlib.Path) -> tuple[int, int]:
    mp = json.loads((fdir / "mapping.json").read_text())
    schema = json.loads((fdir / "schema.json").read_text())
    tot = len(schema.get("fields", []))
    return len(mp.get("map") or {}), tot


def _select_forms(limit: int) -> list[str]:
    rows = []
    for fdir in sorted((OSS_ROOT / "forms").iterdir()):
        if not fdir.is_dir():
            continue
        mp = json.loads((fdir / "mapping.json").read_text())
        if mp.get("status") == "recipe":
            continue
        schema = json.loads((fdir / "schema.json").read_text())
        nfill = len(_fillable(schema.get("fields", [])))
        if not (1 <= nfill <= 120):       # skip flat PDFs and the huge ones
            continue
        mapped = len(mp.get("map") or {})
        rows.append((fdir.name, mapped / max(nfill, 1), nfill))
    rows.sort(key=lambda r: (r[1], -r[2]))   # lowest coverage, then most fields
    return [r[0] for r in rows[:limit]]


def _extract_json(text: str) -> dict:
    """Parse the model's JSON answer, tolerating any surrounding prose."""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        i, j = text.find("{"), text.rfind("}")
        if i != -1 and j != -1:
            return json.loads(text[i:j + 1])
        raise


def _map_one(client, form_id: str) -> dict:
    fdir = OSS_ROOT / "forms" / form_id
    schema = json.loads((fdir / "schema.json").read_text())
    fields = _fillable(schema.get("fields", []))
    valid_ids = {f["field_id"] for f in schema.get("fields", [])}

    listing = "\n".join(
        f"  {f['field_id']} ({f.get('type')}, "
        f"\"{(f.get('label') or '')[:70]}\")" for f in fields)
    user = (f"Form {form_id}. Map these fillable fields. Return only a compact "
            f'JSON object {{"mappings":[{{"field_id","canonical_key"}}]}} (no '
            f"extra whitespace), omitting fields you leave unmapped:\n{listing}")

    resp = client.chat.completions.create(
        model=MODEL,
        max_tokens=4096,
        temperature=0,
        messages=[{"role": "system", "content": SYSTEM},
                  {"role": "user", "content": user}],
        # qwen3.6 is a reasoning model; disable thinking so the (capped) output
        # budget goes to the answer, not a long <think> block.
        extra_body={"chat_template_kwargs": {"enable_thinking": False}},
    )
    choice = resp.choices[0]
    data = _extract_json(choice.message.content or "{}")

    mp, dropped = {}, []
    for item in data.get("mappings", []):
        fid, key = item.get("field_id"), item.get("canonical_key")
        if fid in valid_ids and _key_ok(key):
            mp[fid] = key
        else:
            dropped.append((fid, key))
    return {"map": mp, "dropped": dropped, "stop": choice.finish_reason}


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--limit", type=int, default=100)
    ap.add_argument("--forms", default="", help="comma list (overrides --limit)")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--log", type=pathlib.Path,
                    default=pathlib.Path("/tmp/ai_map_log.jsonl"))
    args = ap.parse_args()

    # One client per endpoint; round-robin so both cluster nodes share load.
    clients = [openai.OpenAI(base_url=ep, api_key="none", timeout=180)
               for ep in ENDPOINTS]
    pick = itertools.count()

    forms = ([f.strip() for f in args.forms.split(",") if f.strip()]
             if args.forms else _select_forms(args.limit))
    print(f"mapping {len(forms)} forms with {MODEL} "
          f"({args.workers} workers over {len(ENDPOINTS)} nodes)")

    lock = threading.Lock()
    logf = args.log.open("a")
    done = {"n": 0, "added": 0}

    def work(fid: str):
        client = clients[next(pick) % len(clients)]
        before, nfields = _coverage(OSS_ROOT / "forms" / fid)
        try:
            res = _map_one(client, fid)
        except Exception as e:  # noqa: BLE001 — log + continue
            return fid, before, None, nfields, repr(e), []
        fdir = OSS_ROOT / "forms" / fid
        (fdir / "mapping.json").write_text(json.dumps({
            "form_id": fid, "status": "ai-mapped", "model": MODEL,
            "note": "Mapped by a local LLM from field labels, constrained to "
                    "the canonical fact object and validated. Not audit-verified.",
            "map": res["map"],
        }, indent=2))
        return fid, before, len(res["map"]), nfields, None, res["dropped"]

    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futures = {ex.submit(work, f): f for f in forms}
        for fut in as_completed(futures):
            fid, before, after, nfields, err, dropped = fut.result()
            with lock:
                done["n"] += 1
                n = done["n"]
                if err:
                    print(f"  [{n}/{len(forms)}] {fid}: ERROR {err}")
                    logf.write(json.dumps({"form": fid, "error": err}) + "\n")
                else:
                    done["added"] += max(0, after - before)
                    print(f"  [{n}/{len(forms)}] {fid}: {before}->{after} mapped "
                          f"({len(dropped)} dropped)")
                    logf.write(json.dumps({"form": fid, "before": before,
                                           "after": after, "nfields": nfields,
                                           "dropped": dropped}) + "\n")
                logf.flush()
    print(f"\ndone. net mapped-field delta: +{done['added']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
