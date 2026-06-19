#!/usr/bin/env python3
"""Derive (and merge authored) per-form if/then logic into forms/<ID>/logic.json.

Three deterministic, corpus-wide derived rule families plus any hand-authored
rules:

  workflow companions   catalog/workflows.json -> companion_form rules: a
                        filing's required / conditional companion forms.
  attachment triggers   fields whose id/label says "...is attached"/"exhibit"
                        -> attachment rules: asserting it expects the document.
  time inference        value_type==time fields -> value_inference: a court
                        time H:MM (1-6) without AM/PM is almost certainly PM.

Authored rules live in ``forms/<ID>/logic.authored.json`` (hand-maintained,
legally sourced) and are merged ahead of the derived rules; the deriver never
overwrites them. The evaluator is tools/logic_engine.py; everything is
warnings-only (see docs/logic-rules.md).

A rule targets the mapped canonical fact-key when one exists (so preflight can
evaluate it against the case directly), else ``field:<id>``.

CLI:
    python3 tools/derive_logic.py --all
    python3 tools/derive_logic.py --form CV-007 [--print]
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re

OSS_ROOT = pathlib.Path(__file__).resolve().parent.parent
FORMS = OSS_ROOT / "forms"
WORKFLOWS = OSS_ROOT / "catalog" / "workflows.json"

_ATTACH_RE = re.compile(r"attach|exhibit", re.I)
_FORM_ID_RE = re.compile(r"\b[A-Z]{2,}(?:-[A-Z0-9]+)+\b")


def _humanize(field_id: str) -> str:
    s = field_id.replace("_", " ").strip()
    s = re.sub(r"\s+", " ", s)
    return s[:1].upper() + s[1:] if s else field_id


def _workflow_companions() -> dict[str, list[tuple]]:
    """form_id -> sorted [(companion_id, required, condition)] across all
    workflows that include the form."""
    if not WORKFLOWS.exists():
        return {}
    wf = json.loads(WORKFLOWS.read_text())
    flows = wf.get("workflows", wf) if isinstance(wf, dict) else wf
    out: dict[str, set] = {}
    for f in (flows.values() if isinstance(flows, dict) else flows):
        steps = f.get("steps") or []
        ids = [s.get("form") for s in steps if s.get("form")]
        for s in steps:
            me = s.get("form")
            if not me:
                continue
            for other in steps:
                oid = other.get("form")
                if oid and oid != me:
                    out.setdefault(me, set()).add(
                        (oid, bool(other.get("required")),
                         other.get("condition")))
        del ids
    return {k: sorted(v, key=lambda t: (t[0], t[1], t[2] or ""))
            for k, v in out.items()}


def _target(field_id: str, fid_to_key: dict) -> tuple[str, str]:
    """Return (operand_path, kind) — prefer the mapped canonical key."""
    key = fid_to_key.get(field_id)
    if key and not key.endswith("()"):
        return key, "var"
    return f"field:{field_id}", "field"


def derived_rules(form_id: str) -> list[dict]:
    fdir = FORMS / form_id
    schema = json.loads((fdir / "schema.json").read_text())
    mapping = json.loads((fdir / "mapping.json").read_text())
    fid_to_key = mapping.get("map") or {}
    rules: list[dict] = []

    # 1) workflow companions
    for oid, required, cond in _workflow_companions().get(form_id, []):
        when = {"truthy": f"facts.{cond}"} if cond else None
        msg = (f"Filing {form_id} requires companion form {oid}."
               if required and not cond else
               f"{form_id} is usually filed with {oid}"
               + (f" (when {cond.replace('_', ' ')})." if cond else "."))
        rules.append({
            "id": f"wf-companion-{oid}" + (f"-{cond}" if cond else ""),
            "kind": "companion_form", "severity": "info",
            "when": when, "then": {"form": oid, "required": required},
            "message": msg,
        })

    # 2) attachment triggers
    gpath = fdir / "fill_guidance.json"
    guidance = (json.loads(gpath.read_text()).get("fields", {})
                if gpath.exists() else {})
    for f in schema.get("fields", []):
        fid = f["field_id"]
        blob = f"{fid} {f.get('label') or ''}"
        if not _ATTACH_RE.search(blob):
            continue
        path, _ = _target(fid, fid_to_key)
        doc = _humanize(re.sub(r"_?(is_)?attached.*$", "", fid) or fid)
        rules.append({
            "id": f"attach-{fid}"[:80], "kind": "attachment", "severity": "info",
            "when": {"truthy": path},
            "then": {"attachment": doc},
            "message": (f"You indicated an attachment ('{doc}') — make sure the "
                        "document is actually attached to the filing."),
        })

    # 3) time-of-day inference (court times default to PM)
    for fid, g in guidance.items():
        if g.get("value_type") != "time":
            continue
        path, _ = _target(fid, fid_to_key)
        rules.append({
            "id": f"time-pm-{fid}"[:80], "kind": "value_inference",
            "severity": "info",
            "when": {"matches": [{"var": path} if not path.startswith("field:")
                                 else path, r"^(0?[1-6]):[0-5]\d$"]},
            "then": {"suggest": (
                f"A court time like this without AM/PM is almost always PM — "
                f"confirm '{_humanize(fid)}' is PM, not AM.")},
            "message": (f"'{_humanize(fid)}' looks like an early-hour time with "
                        "no AM/PM; court times are almost always PM — confirm."),
        })
    return rules


def authored_rules(form_id: str) -> list[dict]:
    p = FORMS / form_id / "logic.authored.json"
    if not p.exists():
        return []
    data = json.loads(p.read_text())
    return data.get("rules") or []


def logic_for_form(form_id: str) -> dict:
    rules = authored_rules(form_id) + derived_rules(form_id)
    return {
        "form_id": form_id,
        "generated_by": "tools/derive_logic.py",
        "note": ("If/then fill logic (authored + derived): conditional-required, "
                 "attachment/companion-form triggers, value incompatibilities, "
                 "and value inferences. Warnings-only — evaluated by "
                 "tools/logic_engine.py at preflight/fill time; nothing here "
                 "blocks or alters a fill. Not legal advice."),
        "rules": rules,
    }


def write_one(form_id: str) -> int:
    logic = logic_for_form(form_id)
    (FORMS / form_id / "logic.json").write_text(
        json.dumps(logic, indent=2, ensure_ascii=False) + "\n")
    return len(logic["rules"])


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--all", action="store_true")
    g.add_argument("--form")
    ap.add_argument("--print", dest="show", action="store_true")
    args = ap.parse_args()

    if args.form and args.show:
        print(json.dumps(logic_for_form(args.form), indent=2,
                         ensure_ascii=False))
        return 0

    forms = (sorted(p.parent.name for p in FORMS.glob("*/mapping.json"))
             if args.all else [args.form])
    total = rules = 0
    for fid in forms:
        n = write_one(fid)
        total += 1
        rules += n
        if args.form:
            print(f"{fid}: {n} rules -> {FORMS / fid / 'logic.json'}")
    if args.all:
        print(f"wrote {total} logic.json artifacts ({rules} rules total)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
