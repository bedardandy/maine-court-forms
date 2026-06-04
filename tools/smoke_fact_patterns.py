#!/usr/bin/env python3
"""Intake smoke test: narrative fact pattern -> Qwen extract+route -> fill ->
recursive Qwen-VL self-audit -> Opus 4.8 fidelity judge (gated to flagged).

This exercises a DIFFERENT leg than improve_loop/audit_loop. Those test mapping
and box-placement against each form's hand-built sample_case.json. This tests
*intake fidelity*: given a plain-language story (the kind a self-represented
litigant would tell), does the local Qwen cluster (1) route to the right form,
(2) extract a correct canonical fact object (docs/integrations/README.md),
(3) fill it so the values land correctly, and does the filled form faithfully
represent the story with nothing invented or dropped?

Division of labor (see the project memory):
  - local Qwen3.6 cluster (free): routing pick, fact extraction, and the
    recursive VL self-audit + re-extract/re-fill loop.
  - Opus 4.8 (subscription, paced, GATED to forms the VL flagged): the
    end-to-end fidelity judge — reads the rendered filled page(s) + the story +
    the extracted facts and returns a verdict (hallucinated / missing /
    misplaced values, grade).

    python3 tools/smoke_fact_patterns.py                       # whole bank
    python3 tools/smoke_fact_patterns.py --areas family,criminal --limit 6
    python3 tools/smoke_fact_patterns.py --no-opus             # cluster pass only

Endpoints come from MCF_LLM_ENDPOINTS (OpenAI-compatible, e.g.
http://localhost:8080/v1). Opus runs headless via `claude -p` with
ANTHROPIC_API_KEY UNSET so it uses subscription OAuth. Blanks are fetched on
demand. Run artifacts land in evaluations/ (gitignored). Filled output is a
draft, NOT legal advice.
"""
from __future__ import annotations

import argparse
import base64
import datetime
import json
import os
import pathlib
import subprocess
import sys
import tempfile

import fitz  # PyMuPDF
import openai

fitz.TOOLS.mupdf_display_errors(False)  # tagged-PDF structure-tree warnings are noise

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from engine.fill_via_mapping import fill_via_mapping  # noqa: E402
from engine.canonical import is_canonical, to_engine_case  # noqa: E402
from engine.fill_and_audit import fill_one  # noqa: E402
from tools.ai_map_forms import _key_ok  # noqa: E402
from tools.find_forms import find_forms  # noqa: E402

OSS_ROOT = pathlib.Path(__file__).resolve().parent.parent
ENDPOINTS = os.environ.get("MCF_LLM_ENDPOINTS",
                           "http://localhost:8080/v1").split(",")
MODEL = os.environ.get("MCF_LLM_MODEL", "qwen3.6-27b")
OPUS_MODEL = os.environ.get("MCF_OPUS_MODEL", "claude-opus-4-8")
MAX_PAGES = int(os.environ.get("MCF_SMOKE_MAXPAGES", "4"))
DPI = 130

CONTRACT = (
    "Canonical keys: matter.{docket_number,court_county,court_location,"
    "court_type,case_type,filing_date}; parties.<role>.<attr> with role in "
    "{plaintiff,defendant,attorney,other_party,child_1,child_2,...} and attr in "
    "{full_name,first_name,middle_name,last_name,address,city,state,zip,phone,"
    "email,date_of_birth} (attorney also bar_number); party.<attr> (same, plus "
    "signature) for the filing party; facts.<snake_case> for form-specific data. "
    "petitioner->plaintiff, respondent->defendant. Dates as MM/DD/YYYY.")


def _clients() -> list[openai.OpenAI]:
    return [openai.OpenAI(base_url=ep.strip(), api_key="x") for ep in ENDPOINTS]


def _chat(client: openai.OpenAI, prompt: str, system: str | None = None,
          max_tokens: int = 1200, temperature: float = 0.0,
          images: list[bytes] | None = None) -> str:
    content: list | str
    if images:
        content = [{"type": "text", "text": prompt}]
        for png in images:
            b64 = base64.b64encode(png).decode()
            content.append({"type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{b64}"}})
    else:
        content = prompt
    msgs = ([{"role": "system", "content": system}] if system else []) + \
           [{"role": "user", "content": content}]
    r = client.chat.completions.create(
        model=MODEL, max_tokens=max_tokens, temperature=temperature, messages=msgs,
        extra_body={"chat_template_kwargs": {"enable_thinking": False}})
    return (r.choices[0].message.content or "").strip()


def _json_block(text: str):
    """Pull the first JSON object/array out of an LLM reply."""
    for op, cl in (("{", "}"), ("[", "]")):
        i, j = text.find(op), text.rfind(cl)
        if i != -1 and j > i:
            try:
                return json.loads(text[i:j + 1])
            except json.JSONDecodeError:
                continue
    return None


# --------------------------------------------------------------------------- #
# form catalog (trusted + fillable only)
# --------------------------------------------------------------------------- #
def _flatten_keys(obj, prefix: str = "") -> set[str]:
    """Flatten a canonical fact object into dotted leaf keys.

    Used to derive the expected key-set for recipe-tier forms (whose
    mapping.json is a pointer with an empty ``map``) from their
    examples/sample_case.json, so they can still constrain extraction.
    """
    out: set[str] = set()
    if isinstance(obj, dict):
        for k, v in obj.items():
            key = f"{prefix}.{k}" if prefix else k
            if isinstance(v, dict):
                out |= _flatten_keys(v, key)
            else:
                out.add(key)
    return out


def trusted_fillable() -> dict[str, dict]:
    """form_id -> {keys, status, tier, title} for fillable forms.

    Two fillable tiers:
      - ``mapping`` (status verified/recipe with a non-empty ``map``): filled
        via engine.fill_via_mapping; expected keys = set(map.values()).
      - ``recipe`` (status recipe with an empty pointer ``map``): the highest
        trust tier, filled via engine.fill (map_form + form recipe). These were
        previously excluded — which silently dropped 71 authoritative forms
        (e.g. NC-001 Petition for Change of Name) from routing, so a name-change
        narrative could only land on the adoption forms. Expected keys are
        derived from the form's examples/sample_case.json.
    """
    out: dict[str, dict] = {}
    idx = {f["form"]: f for f in
           json.loads((OSS_ROOT / "catalog" / "forms_index.json").read_text())}
    for d in sorted((OSS_ROOT / "forms").iterdir()):
        mp = d / "mapping.json"
        if not mp.exists():
            continue
        try:
            m = json.loads(mp.read_text())
        except json.JSONDecodeError:
            continue
        status = m.get("status")
        if status not in ("recipe", "verified"):
            continue
        mapd = m.get("map") or {}
        if mapd:
            tier = "mapping"
            keys = sorted({v for v in mapd.values()
                           if isinstance(v, str) and "." in v
                           and not v.endswith("()")})
        elif status == "recipe":
            # Pointer-only recipe form: derive expected keys from the sample.
            sample = d / "examples" / "sample_case.json"
            if not sample.exists():
                continue
            try:
                keys = sorted(k for k in _flatten_keys(
                    json.loads(sample.read_text())) if "." in k)
            except json.JSONDecodeError:
                continue
            if not keys:
                continue
            tier = "recipe"
        else:
            continue
        out[d.name] = {
            "keys": keys, "status": status, "tier": tier,
            "title": (idx.get(d.name, {}).get("title", d.name)).split(" — ")[-1],
            "category": idx.get(d.name, {}).get("category", ""),
        }
    return out


# --------------------------------------------------------------------------- #
# 1. route + pick
# --------------------------------------------------------------------------- #
def route_and_pick(client, narrative: str, catalog: dict, want: int = 2,
                   hint: list[str] | None = None) -> tuple[list[str], dict]:
    cand = [f["form"] for f in find_forms(narrative, k=12)["forms"]
            if f["form"] in catalog]
    # fold soft hints in (only if they're trusted+fillable) so a routing miss
    # doesn't blank the whole pattern — recorded separately for routing eval.
    for h in (hint or []):
        if h in catalog and h not in cand:
            cand.append(h)
    if not cand:
        return [], {"candidates": [], "reason": "no trusted+fillable candidate"}
    menu = "\n".join(f"  {fid}: {catalog[fid]['title']}" for fid in cand)
    prompt = (
        f"A person describes their situation:\n\"{narrative}\"\n\n"
        f"Here are candidate Maine court forms (id: title):\n{menu}\n\n"
        f"Choose the {want} form(s) that best fit what they are trying to file, "
        f"most relevant first. Only choose from the ids listed. Reply ONLY with "
        f'JSON: {{"forms":["ID",...]}}.')
    picked: list[str] = []
    try:
        ans = _json_block(_chat(client, prompt, max_tokens=200)) or {}
        picked = [f for f in ans.get("forms", []) if f in cand][:want]
    except Exception as e:  # noqa: BLE001
        picked = []
    if not picked:
        picked = cand[:1]  # lexical top as fallback
    return picked, {"candidates": cand, "picked": picked}


# --------------------------------------------------------------------------- #
# 2. extract canonical fact object
# --------------------------------------------------------------------------- #
def _set_key(obj: dict, dotted: str, value):
    parts = dotted.split(".")
    cur = obj
    for p in parts[:-1]:
        cur = cur.setdefault(p, {})
    cur[parts[-1]] = value


def extract(client, narrative: str, fid: str, keys: list[str],
            feedback: str | None = None) -> tuple[dict, dict]:
    keylist = "\n".join(f"  {k}" for k in keys)
    fixup = (f"\n\nA previous attempt to fill this form had these problems — "
             f"correct the fact object accordingly (omit a value that does not "
             f"belong in a box, shorten an over-long value, fix a mis-keyed "
             f"fact):\n{feedback}\n" if feedback else "")
    prompt = (
        f"{CONTRACT}\n\nA person describes their situation:\n\"{narrative}\"\n\n"
        f"Form {fid} consumes exactly these canonical keys:\n{keylist}\n\n"
        f"Produce the canonical fact object for THIS form. Rules: only emit keys "
        f"from the list above; fill a key only if the narrative clearly supports "
        f"it; OMIT any key you cannot support (do not guess, do not invent names, "
        f"dates, or docket numbers). Use the person as the filing `party` and "
        f"`parties.plaintiff`/`parties.petitioner`-equivalent unless they are "
        f"clearly the defendant/respondent. Reply ONLY with a flat JSON object of "
        f'"<dotted.key>": "<value>" pairs.{fixup}')
    raw = _chat(client, prompt, max_tokens=1400)
    flat = _json_block(raw) or {}
    facts: dict = {}
    kept, dropped = {}, []
    allowed = set(keys)
    for k, v in (flat.items() if isinstance(flat, dict) else []):
        if not isinstance(v, str) or not v.strip():
            continue
        if k in allowed and _key_ok(k):
            _set_key(facts, k, v.strip())
            kept[k] = v.strip()
        else:
            dropped.append(k)
    return facts, {"kept": kept, "dropped": dropped, "n_kept": len(kept)}


# --------------------------------------------------------------------------- #
# render + VL self-audit
# --------------------------------------------------------------------------- #
def render(pdf: pathlib.Path, out_dir: pathlib.Path, max_pages: int) -> list[pathlib.Path]:
    doc = fitz.open(str(pdf))
    pngs = []
    for i in range(min(max_pages, doc.page_count)):
        p = out_dir / f"{pdf.stem}_p{i + 1}.png"
        doc[i].get_pixmap(dpi=DPI).save(str(p))
        pngs.append(p)
    doc.close()
    return pngs


VL_AUDIT = (
    "You are checking whether a filled Maine court form page faithfully reflects "
    "the facts that were supposed to be entered. The facts entered were:\n{facts}\n\n"
    "Look ONLY at the typed-in values on this page (ignore the pre-printed form "
    "text). List concrete problems, each as one of: WRONG (a typed value does not "
    "match the facts), MISPLACED (a value is in the wrong field/box for its "
    "label), OVERFLOW (a value is cut off or runs past its box), MISSING (a fact "
    "that clearly belongs on this page was not entered). If the page looks "
    'correct, return an empty list. Reply ONLY JSON: {{"problems":[{{"type":'
    '"WRONG|MISPLACED|OVERFLOW|MISSING","detail":"..."}}]}}.')


def vl_audit(client, facts: dict, pngs: list[pathlib.Path]) -> list[dict]:
    problems: list[dict] = []
    facts_s = json.dumps(facts, ensure_ascii=False)
    for png in pngs:
        try:
            raw = _chat(client, VL_AUDIT.format(facts=facts_s),
                        images=[png.read_bytes()], max_tokens=900, temperature=0.0)
            ans = _json_block(raw) or {}
            for p in ans.get("problems", []):
                if isinstance(p, dict) and p.get("detail"):
                    problems.append({"page": png.name, "type": p.get("type", "?"),
                                     "detail": str(p["detail"])[:240]})
        except Exception as e:  # noqa: BLE001
            problems.append({"page": png.name, "type": "AUDIT_ERROR",
                             "detail": str(e)[:160]})
    return problems


# --------------------------------------------------------------------------- #
# Opus 4.8 fidelity judge (gated, headless, subscription)
# --------------------------------------------------------------------------- #
def opus_judge(narrative: str, facts: dict, pngs: list[pathlib.Path],
               timeout: int = 600) -> dict:
    imgs = " ".join(str(p) for p in pngs)
    prompt = (
        f"Read these rendered filled Maine court form page image(s): {imgs}\n\n"
        f"They were filled from this person's story:\n\"{narrative}\"\n\n"
        f"The values entered were:\n{json.dumps(facts, ensure_ascii=False)}\n\n"
        f"You are the fidelity judge. Considering ONLY the typed-in values "
        f"(ignore pre-printed form text), decide whether the filled form "
        f"faithfully represents the story. Report: values that are HALLUCINATED "
        f"(not supported by the story), facts MISSING from the form, values that "
        f"are MISPLACED (wrong box for their label) or truncated, and an overall "
        f'grade. Reply ONLY compact JSON: {{"grade":"pass|minor|major",'
        f'"hallucinated":["..."],"missing":["..."],"misplaced":["..."],'
        f'"notes":"one sentence"}}.')
    env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
    try:
        r = subprocess.run(
            ["claude", "-p", prompt, "--model", OPUS_MODEL, "--allowedTools", "Read"],
            capture_output=True, text=True, timeout=timeout, env=env)
    except subprocess.TimeoutExpired:
        return {"grade": "error", "notes": "opus timeout"}
    out = (r.stdout or "").strip()
    if r.returncode != 0 or not out:
        return {"grade": "error",
                "notes": f"opus rc={r.returncode}: {(r.stderr or '')[:120]}"}
    return _json_block(out) or {"grade": "error", "notes": "unparseable opus reply"}


# --------------------------------------------------------------------------- #
# driver
# --------------------------------------------------------------------------- #
def fetch_blank(fid: str) -> bool:
    if (OSS_ROOT / "forms" / fid / f"{fid}.pdf").exists():
        return True
    subprocess.run([sys.executable, "tools/fetch_pdfs.py", "--forms", fid],
                   cwd=OSS_ROOT, capture_output=True, text=True)
    return (OSS_ROOT / "forms" / fid / f"{fid}.pdf").exists()


def _fill(fid: str, facts: dict, tier: str, work: pathlib.Path) -> dict:
    """Fill a form via the path its trust tier requires.

    ``mapping`` tier -> engine.fill_via_mapping (mapping.json-driven).
    ``recipe`` tier -> engine.fill (map_form + form recipe), driven from the
    same canonical fact object. Both return {ok, out_pdf, fields_written}.
    """
    if tier == "recipe":
        fdir = OSS_ROOT / "forms" / fid
        case = to_engine_case(facts) if is_canonical(facts) else facts
        try:
            r = fill_one(fid, case, work, schema_path=fdir / "schema.json",
                         pdf_path=fdir / f"{fid}.pdf")
        except Exception as e:  # recipe inference can raise on sparse cases
            return {"ok": False, "error": f"recipe-fill: {e}"}
        return {"ok": r.get("ok"), "out_pdf": r.get("out_pdf"),
                "fields_written": r.get("fields_written_to_pdf"),
                "error": r.get("error")}
    return fill_via_mapping(fid, facts, work)


def run_form(client, narrative: str, fid: str, meta: dict, run_dir: pathlib.Path,
             max_iters: int, use_opus: bool) -> dict:
    rec: dict = {"form": fid, "title": meta["title"], "status": meta["status"],
                 "tier": meta.get("tier", "mapping")}
    if not fetch_blank(fid):
        rec["result"] = "blank-missing"
        return rec
    work = run_dir / fid
    work.mkdir(parents=True, exist_ok=True)
    feedback = None
    history = []
    for it in range(1, max_iters + 1):
        facts, exinfo = extract(client, narrative, fid, meta["keys"], feedback)
        if not facts:
            rec["result"] = "no-facts-extracted"
            rec["extract"] = exinfo
            return rec
        out = _fill(fid, facts, meta.get("tier", "mapping"), work)
        if not out.get("ok"):
            rec["result"] = "fill-failed"
            rec["error"] = out.get("error")
            rec["extract"] = exinfo
            return rec
        pdf = pathlib.Path(out["out_pdf"])
        pngs = render(pdf, work, MAX_PAGES)
        problems = vl_audit(client, facts, pngs)
        history.append({"iter": it, "n_kept": exinfo["n_kept"],
                        "fields_written": out.get("fields_written"),
                        "n_problems": len(problems)})
        rec.update({"facts": facts, "extract": exinfo,
                    "fields_written": out.get("fields_written"),
                    "problems": problems, "iters": history,
                    "pages": [p.name for p in pngs]})
        if not problems or it == max_iters:
            break
        # recurse: feed the flagged problems back into the next extraction
        feedback = "\n".join(f"- {p['type']}: {p['detail']}" for p in problems)

    flagged = bool(rec.get("problems"))
    if use_opus and flagged:
        rec["opus"] = opus_judge(narrative, rec["facts"],
                                 [work / n for n in rec["pages"]])
        rec["result"] = "opus-judged"
    elif flagged:
        rec["result"] = "flagged-no-opus"
    else:
        rec["result"] = "qwen-clean"
    return rec


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bank", type=pathlib.Path,
                    default=OSS_ROOT / "tools" / "smoke" / "fact_patterns.json")
    ap.add_argument("--areas", help="comma list to filter (family,pfa,money,"
                    "namechange,criminal)")
    ap.add_argument("--limit", type=int, default=0, help="cap number of patterns")
    ap.add_argument("--forms-per", type=int, default=2,
                    help="max forms to fill per pattern")
    ap.add_argument("--max-iters", type=int, default=2,
                    help="recursive re-extract/re-fill attempts per form")
    ap.add_argument("--no-opus", action="store_true",
                    help="cluster pass only; skip the Opus fidelity judge")
    ap.add_argument("--out", type=pathlib.Path, default=None)
    a = ap.parse_args()

    pats = json.loads(a.bank.read_text())["patterns"]
    if a.areas:
        sel = {x.strip() for x in a.areas.split(",")}
        pats = [p for p in pats if p["area"] in sel]
    if a.limit:
        pats = pats[:a.limit]

    catalog = trusted_fillable()
    client = _clients()[0]
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = a.out or (OSS_ROOT / "evaluations" / f"smoke_{ts}")
    run_dir.mkdir(parents=True, exist_ok=True)
    print(f"intake smoke test: {len(pats)} pattern(s), model={MODEL} @ "
          f"{ENDPOINTS}, opus={'off' if a.no_opus else OPUS_MODEL}\n"
          f"catalog: {len(catalog)} trusted+fillable forms\nrun dir: {run_dir}\n")

    results = []
    for pi, p in enumerate(pats, 1):
        print(f"[{pi}/{len(pats)}] {p['id']} ({p['area']})")
        picked, route = route_and_pick(client, p["narrative"], catalog,
                                       want=a.forms_per, hint=p.get("expect_forms"))
        hit = bool(set(picked) & set(p.get("expect_forms", [])))
        print(f"    routed -> {picked}  (expected hint {p.get('expect_forms')}, "
              f"hit={hit})")
        forms = []
        for fid in picked:
            r = run_form(client, p["narrative"], fid, catalog[fid], run_dir,
                         a.max_iters, use_opus=not a.no_opus)
            g = (r.get("opus") or {}).get("grade")
            print(f"    {fid}: {r['result']}"
                  + (f" | {r.get('fields_written')} fields, "
                     f"{len(r.get('problems', []))} vl-flags" if 'problems' in r else "")
                  + (f" | opus={g}" if g else ""))
            forms.append(r)
        results.append({"id": p["id"], "area": p["area"],
                        "narrative": p["narrative"], "routing": route,
                        "route_hint_hit": hit, "forms": forms})
        (run_dir / "results.json").write_text(json.dumps(results, indent=2))

    _summarize(results, run_dir)
    print(f"\nfull report: {run_dir}/results.json  +  {run_dir}/summary.tsv")
    return 0


def _summarize(results: list[dict], run_dir: pathlib.Path):
    rows = ["pattern\tarea\troute_hit\tform\tresult\tfields\tvl_flags\topus_grade"]
    tally = {"qwen-clean": 0, "opus-judged": 0, "flagged-no-opus": 0,
             "fill-failed": 0, "no-facts-extracted": 0, "blank-missing": 0}
    grades = {"pass": 0, "minor": 0, "major": 0, "error": 0}
    n_forms = route_hits = 0
    for r in results:
        route_hits += int(r["route_hint_hit"])
        for f in r["forms"]:
            n_forms += 1
            tally[f["result"]] = tally.get(f["result"], 0) + 1
            g = (f.get("opus") or {}).get("grade")
            if g:
                grades[g] = grades.get(g, 0) + 1
            rows.append("\t".join(str(x) for x in [
                r["id"], r["area"], r["route_hint_hit"], f["form"], f["result"],
                f.get("fields_written", ""), len(f.get("problems", [])), g or ""]))
    (run_dir / "summary.tsv").write_text("\n".join(rows) + "\n")
    print(f"\n=== summary: {len(results)} patterns, {n_forms} form fills ===")
    print(f"routing hint hit: {route_hits}/{len(results)}")
    print("results: " + ", ".join(f"{k}={v}" for k, v in tally.items() if v))
    if any(grades.values()):
        print("opus grades: " + ", ".join(f"{k}={v}" for k, v in grades.items() if v))


if __name__ == "__main__":
    raise SystemExit(main())
