#!/usr/bin/env python3
"""Faceted router prototype: matter x instrument x intent, favorites-first.

A re-ranking + facet-recall layer over the deterministic lexical router
(``find_forms``). Design goals, from the intake smoke-test findings:

  - **Matter** (Family/Criminal/Civil/PFA/...) discriminates *substantive,
    initiating* forms (the complaint/petition that starts a case).
  - **Instrument** (Motion/Affidavit/Answer/Notice/Summons/...) discriminates
    the *procedural, cross-category* forms matter can't — the Motion to Continue
    serves six categories, so matter alone can never find it; the action verb
    ("postpone") can. ~half of titles carry the instrument as their lead word,
    so this facet is mostly free.
  - **Intent** (initiate/modify/enforce/respond/terminate) separates three forms
    that are all "Family motions": Complaint for Divorce (initiate) vs Motion to
    Modify (modify) vs Motion for Contempt (enforce). This is what broke the
    fam_motion_modify pattern (landed on a generic motion form).

Crucially this is **bonus-only re-ranking, not a filter**: a candidate enters
the pool if lexical scored it > 0 OR it agrees on >= 2 facets (so a
cross-category Motion with the right instrument+matter is recoverable even at
lexical 0), but a lexical hit is never dropped. So recall >= lexical by
construction, and facets fix rank + recover the cross-category/intent misses.
Favorites = the lead forms of a matching workflow (workflows.json already
encodes the ordered form sequence per matter), boosted to the top.

    python3 tools/route_v2.py "postpone my criminal hearing"
    python3 tools/route_v2.py --benchmark        # vs lexical on the smoke bank
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

OSS_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(OSS_ROOT) not in sys.path:
    sys.path.insert(0, str(OSS_ROOT))

from tools.find_forms import _tokens, find_forms  # noqa: E402

# --------------------------------------------------------------------------- #
# Facet vocabularies
# --------------------------------------------------------------------------- #

# Instrument: canonical -> trigger tokens found in a QUERY. The same canonical
# word is matched against a form's leading title noun.
INSTRUMENTS = {
    "motion": {"motion", "ask", "request", "move", "postpone", "continue",
               "reschedule", "modify", "compel", "suppress", "dismiss"},
    "petition": {"petition", "establish", "guardianship", "adopt", "change"},
    "complaint": {"complaint", "sue", "suing", "lawsuit", "claim", "evict"},
    "affidavit": {"affidavit", "swear", "swearing", "sworn", "financial",
                  "indigency", "indigent"},
    "answer": {"answer", "respond", "response", "reply", "served"},
    "summons": {"summons", "serve", "summon"},
    "notice": {"notice", "notify", "appeal"},
    "subpoena": {"subpoena", "compel", "witness"},
    "appearance": {"appearance", "appear", "represent", "pro"},
    "order": {"order", "proposed"},
    "waiver": {"waiver", "waive", "fee", "afford"},
}

# Intent: the relief/goal the litigant states.
INTENTS = {
    "modify": {"modify", "change", "lower", "raise", "increase", "decrease",
               "adjust", "existing", "already"},
    "enforce": {"enforce", "enforcement", "contempt", "comply", "complying",
                "violated", "owe", "owes", "unpaid", "hasnt", "wont"},
    "respond": {"respond", "answer", "response", "served", "reply", "object"},
    "terminate": {"terminate", "termination", "end", "dismiss", "withdraw"},
    "initiate": {"file", "start", "begin", "initiate", "open", "want", "need"},
    "protect": {"protection", "protect", "abuse", "harassment", "threatened",
                "safety", "stalking"},
}

# Matter: query keyword -> coarse matter bucket (matches the catalog category's
# top-level token). A form whose category is cross-category matches ANY matter.
MATTER_KEYWORDS = {
    "Family": {"divorce", "custody", "parenting", "parental", "marriage",
               "married", "spouse", "child", "children", "support", "parentage",
               "father", "paternity", "alimony"},
    "Criminal": {"criminal", "charged", "crime", "bail", "release", "defendant",
                 "prosecutor", "counsel", "arraignment", "conviction"},
    "Civil": {"contract", "breach", "debt", "money", "judgment", "evict",
              "tenant", "landlord", "rent", "damages", "lawsuit", "creditor"},
    "Small Claims": {"small", "claims", "owed", "borrowed", "lent"},
    "Protection from Abuse": {"protection", "abuse", "harassment", "threatened",
                              "stalking", "boyfriend", "girlfriend"},
    "Adoption": {"adopt", "adoption", "adoptee"},
    "Guardianship": {"guardian", "guardianship", "ward"},
    "Name Change": {"name", "rename", "renamed"},
    "Juvenile": {"juvenile", "delinquency"},
}


def _instrument_of_title(title: str) -> str:
    t = title.split("—", 1)[-1].strip()
    for canon in INSTRUMENTS:
        # title nouns are capitalized; match the canonical word at the start
        if re.match(rf"\b{canon}\b", t, re.IGNORECASE):
            return canon
    return ""


def _intent_of_form(title: str, keywords: str) -> set[str]:
    hay = _tokens(title + " " + keywords)
    out = set()
    if hay & {"modify", "modification", "amend"}:
        out.add("modify")
    if hay & {"contempt", "enforcement", "enforce", "disclosure"}:
        out.add("enforce")
    if hay & {"answer", "response", "objection"}:
        out.add("respond")
    if hay & {"termination", "terminate", "dismissal", "withdrawal"}:
        out.add("terminate")
    if hay & {"complaint", "petition", "application"}:
        out.add("initiate")
    if hay & {"protection", "harassment", "abuse"}:
        out.add("protect")
    return out


def form_facets(f: dict) -> dict:
    cat = f.get("category", "")
    top = cat.split(" — ")[0].strip()
    cross = "cross" in cat.lower() or f.get("form", "").count("-") >= 2 and \
        any(f["form"].startswith(p) for p in ("CR-CV", "CV-FM", "FM-PB",
                                              "CR-CV-FM"))
    kw = f.get("keywords", "")
    if isinstance(kw, list):
        kw = " ".join(kw)
    return {
        "matter": top,
        "cross": cross,
        "instrument": _instrument_of_title(f.get("title", "")),
        "intent": _intent_of_form(f.get("title", ""), kw),
    }


def query_facets(q: str) -> dict:
    toks = _tokens(q)
    matters = {m for m, kws in MATTER_KEYWORDS.items() if toks & kws}
    instruments = {i for i, kws in INSTRUMENTS.items() if toks & kws}
    intents = {i for i, kws in INTENTS.items() if toks & kws}
    return {"matters": matters, "instruments": instruments, "intents": intents}


def _lex_scores(query: str) -> dict:
    """form_id -> lexical rank score (top form = N, next = N-1, ...).

    The uniform gap of 1 per rank is deliberate and well-calibrated against the
    facet bonuses: a +3 instrument match moves a form up ~3 slots, a +6 favorite
    ~6 slots. Bucketing/compressing this (an earlier attempt) destroyed the
    granularity and lowered MRR, so keep the linear rank score.
    """
    res = find_forms(query, k=999)
    return {f["form"]: (len(res["forms"]) - i)
            for i, f in enumerate(res["forms"])}


def _favorites(query: str) -> set[str]:
    """Lead forms of workflows whose name/matter the query matches."""
    qt = _tokens(query)
    wf = json.loads((OSS_ROOT / "catalog" / "workflows.json"
                     ).read_text())["workflows"]
    fav = set()
    for w in wf.values():
        # match on matter_types only — workflow name/description is prose and
        # over-matches (a PFA query hitting a 'contempt' workflow on a stray
        # token). matter_types are curated tags, so they're the precise signal.
        mt = _tokens(" ".join(w.get("matter_types", [])))
        if qt & mt:
            steps = w.get("steps", [])
            if steps:
                fav.add(steps[0]["form"])  # the initiating/primary form
    return fav


def route(query: str, k: int = 8) -> dict:
    idx = json.loads((OSS_ROOT / "catalog" / "forms_index.json").read_text())
    qf = query_facets(query)
    lex = _lex_scores(query)
    fav = _favorites(query)

    ranked = []
    for f in idx:
        fid = f["form"]
        ff = form_facets(f)
        lex_s = lex.get(fid, 0)

        matter_ok = bool(ff["cross"] or (ff["matter"] in qf["matters"])
                         or not qf["matters"])
        instr_ok = bool(ff["instrument"] and ff["instrument"] in qf["instruments"])
        intent_ok = bool(ff["intent"] & qf["intents"])
        agree = sum([ff["matter"] in qf["matters"] or ff["cross"],
                     instr_ok, intent_ok])

        # candidacy: lexical hit OR >=2 facet agreements (keeps the pool tight)
        if lex_s == 0 and agree < 2:
            continue

        score = (lex_s
                 + 3 * instr_ok
                 + 3 * intent_ok
                 + 2 * (ff["matter"] in qf["matters"])
                 + 6 * (fid in fav))
        ranked.append((score, fid, f, dict(matter=ff["matter"],
                       instrument=ff["instrument"], intent=sorted(ff["intent"]),
                       fav=fid in fav, instr_ok=instr_ok, intent_ok=intent_ok)))
    ranked.sort(key=lambda x: (-x[0], x[1]))
    return {
        "query": query,
        "query_facets": {k2: sorted(v) for k2, v in qf.items()},
        "forms": [{"form": fid, "title": f["title"].split(" — ")[-1],
                   "score": s, **why}
                  for s, fid, f, why in ranked[:k]],
    }


def _benchmark() -> int:
    pats = json.loads((OSS_ROOT / "tools" / "smoke" /
                       "fact_patterns.json").read_text())["patterns"]
    idx_ids = {f["form"] for f in
               json.loads((OSS_ROOT / "catalog" / "forms_index.json"
                           ).read_text())}
    K = 8
    agg = {"lex": {"recall": 0, "ranks": []}, "v2": {"recall": 0, "ranks": []}}
    n_rel = 0
    print(f"{'pattern':24} {'gold':10} {'lex':>6} {'v2':>6}")
    for p in pats:
        gold = [g for g in p["expect_forms"] if g in idx_ids]
        if not gold:
            continue
        lex_top = [x["form"] for x in find_forms(p["narrative"], k=K)["forms"]]
        v2_top = [x["form"] for x in route(p["narrative"], k=K)["forms"]]
        for g in gold:
            n_rel += 1
            lr = lex_top.index(g) + 1 if g in lex_top else None
            vr = v2_top.index(g) + 1 if g in v2_top else None
            agg["lex"]["recall"] += int(lr is not None)
            agg["v2"]["recall"] += int(vr is not None)
            if lr:
                agg["lex"]["ranks"].append(lr)
            if vr:
                agg["v2"]["ranks"].append(vr)
            print(f"  {p['id']:22} {g:10} {('#'+str(lr)) if lr else 'MISS':>6} "
                  f"{('#'+str(vr)) if vr else 'MISS':>6}")
    def mrr(ranks):
        return sum(1 / r for r in ranks) / n_rel if n_rel else 0
    print(f"\n{'':24} relevant-forms={n_rel}")
    for name in ("lex", "v2"):
        a = agg[name]
        print(f"  {name:4}  recall@{K}={a['recall']}/{n_rel} "
              f"({100*a['recall']//n_rel}%)  MRR={mrr(a['ranks']):.3f}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("query", nargs="?", help="fact pattern / matter description")
    ap.add_argument("--k", type=int, default=8)
    ap.add_argument("--benchmark", action="store_true",
                    help="compare recall/MRR vs lexical on the smoke bank")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    if args.benchmark:
        return _benchmark()
    if not args.query:
        ap.error("query required (or use --benchmark)")
    res = route(args.query, args.k)
    if args.json:
        print(json.dumps(res, indent=2))
    else:
        print(f"query facets: {res['query_facets']}")
        for f in res["forms"]:
            tag = " ".join(t for t in [
                "FAV" if f["fav"] else "",
                f"instr={f['instrument']}" if f["instr_ok"] else "",
                f"intent={','.join(f['intent'])}" if f["intent_ok"] else "",
            ] if t)
            print(f"  {f['score']:3}  {f['form']:14} {f['title'][:42]:42} {tag}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
