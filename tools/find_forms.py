#!/usr/bin/env python3
"""Route a fact pattern / matter description to candidate forms.

Deterministic keyword routing over the catalog so an agent (or a human) can go
from "client wants to evict a tenant for nonpayment" to the right form IDs.
Searches:
  - catalog/forms_index.json   (per-form title / category / purpose)
  - catalog/workflows.json     (matter -> ordered form sequences)

    python3 tools/find_forms.py "divorce with two minor children"
    python3 tools/find_forms.py --json "eviction nonpayment of rent"

Returns matching workflows (which list the full form sequence for a matter) and
the top individual forms. Routing only — it does not fill anything.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re

OSS_ROOT = pathlib.Path(__file__).resolve().parent.parent
_STOP = {"the", "a", "an", "of", "for", "to", "and", "or", "with", "in", "on",
         "is", "are", "form", "forms", "maine", "court", "file", "filing",
         "client", "wants", "needs", "case", "matter"}


def _tokens(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9]+", (text or "").lower())
            if w not in _STOP and len(w) > 2}


def find_forms(query: str, k: int = 8) -> dict:
    q = _tokens(query)
    idx = json.loads((OSS_ROOT / "catalog" / "forms_index.json").read_text())
    wf = json.loads((OSS_ROOT / "catalog" / "workflows.json").read_text())["workflows"]

    # workflows: match query against name/description/matter_types
    wf_hits = []
    for key, w in wf.items():
        hay = _tokens(" ".join([w.get("name", ""), w.get("description", ""),
                                " ".join(w.get("matter_types", []))]))
        score = len(q & hay)
        if score:
            wf_hits.append((score, key, w))
    wf_hits.sort(key=lambda x: -x[0])

    # individual forms: weight title/category over purpose
    # `keywords` is an optional per-form synonym bridge (e.g. "postpone" for the
    # Motion to Continue, "father/paternity" for the Parentage complaint) that
    # closes lexical recall gaps title/purpose miss. Surgical by design — only
    # forms a routing miss exposed carry it. Scored at the title weight.
    # `negative_keywords` is the inverse: a form is disqualified entirely when
    # the query hits one of them. Used to keep a generically-titled form out of
    # a matter it doesn't belong to (e.g. the small-claims "Response to
    # Complaint" must not surface for a residential eviction).
    form_hits = []
    for f in idx:
        neg = f.get("negative_keywords", "")
        if isinstance(neg, list):
            neg = " ".join(neg)
        if neg and (q & _tokens(neg)):
            continue
        kw = f.get("keywords", "")
        if isinstance(kw, list):
            kw = " ".join(kw)
        title_c = _tokens(f.get("title", "") + " " + f.get("category", "")
                          + " " + kw)
        purpose = _tokens(f.get("purpose", ""))
        score = 2 * len(q & title_c) + len(q & purpose)
        if score:
            form_hits.append((score, f))
    form_hits.sort(key=lambda x: (-x[0], x[1]["form"]))

    return {
        "query": query,
        "workflows": [
            {"key": key, "name": w["name"], "matter_types": w.get("matter_types", []),
             "forms": [s["form"] for s in w.get("steps", [])]}
            for _, key, w in wf_hits[:3]],
        "forms": [
            {"form": f["form"], "title": f["title"].split(" — ")[-1],
             "category": f.get("category", "")}
            for _, f in form_hits[:k]],
    }


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("query", help="fact pattern / matter description")
    ap.add_argument("--k", type=int, default=8)
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args()
    res = find_forms(args.query, args.k)
    if args.json:
        print(json.dumps(res, indent=2)); return 0
    if res["workflows"]:
        print("Matching workflows (full form sequence for the matter):")
        for w in res["workflows"]:
            print(f"  [{w['key']}] {w['name']} -> {', '.join(w['forms'])}")
    print("\nTop individual forms:")
    for f in res["forms"]:
        print(f"  {f['form']:14} {f['category']:18} {f['title'][:46]}")
    if not res["workflows"] and not res["forms"]:
        print("No matches — try different keywords, or browse catalog/forms_index.json.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
