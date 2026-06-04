# Reference fill engine

The library is integration-agnostic: the per-form folder (`forms/<ID>/`) is the
contract. This `engine/` is an **optional, shared** reference filler that
consumes those folders — it is not required to use the library, but it is how
the project verifies that a form's artifacts actually produce a correct fill.

## Layout

| File | Role |
|---|---|
| `fill.py` | OSS entrypoint — fill one form from a case JSON (see below) |
| `form_filler.py` | low-level AcroForm writer/flattener (PyMuPDF) |
| `build_kv_map.py` | generic `map_form(schema, case)` → `field_id → value` |
| `case_template.py` | case scaffolding helpers used by the generic map |
| `text_fit.py` | width-fit: name initial-collapse, address abbreviation |
| `backfill_attorney_block.py` | shared attorney-block helper (used by a recipe) |
| `fill_and_audit.py` | the reference driver: `fill_one()` orchestration + an optional vision audit |
| `recipes/infer_*.py` | 42 recipe files; the `RECIPE3` dispatch in `fill_and_audit.py` wires 71 form ids to 32 of them (10 files are currently unwired) |
| `examples/case.fami.json` | one engine-shape case for verification |

## Running a fill

```bash
pip install -r ../requirements.txt   # PyMuPDF, PyYAML
python3 -m engine.fill --form AD-022 \
    --case engine/examples/case.fami.json --out /tmp/oss_fill
```

This resolves `forms/AD-022/schema.json` and `forms/AD-022/AD-022.pdf`, runs the
generic field map, applies the form's recipe if one is registered, fills the
notary block, width-fits overflowing names/addresses, and writes
`<ID>.filled.pdf` + `<ID>.kv.json` to the output dir.

> Blank source PDFs are not shipped in git (see `LICENSE.md`), so a fresh clone
> must fetch them first: `python3 tools/fetch_pdfs.py --forms AD-022` (verified
> against `catalog/pdf_manifest.json`). Otherwise the fill won't find
> `forms/<ID>/<ID>.pdf`.

## Filling from mapping.json (verifying a mapping)

`engine/fill.py` runs the generic map + recipes and never reads `mapping.json`.
To exercise `mapping.json` itself — the portable adapter boundary — use
`engine/fill_via_mapping.py`, which resolves each canonical fact-key in a form's
`mapping.json` against a canonical fact object and writes the mapped widgets:

```bash
python3 -m engine.fill_via_mapping --form AD-001   # uses examples/sample_case.json
```

This is what an external adapter conceptually does, and it's how you verify a
draft mapping (fill from it, then check the output). `tools/mapping_coverage.py`
reports per-form mapping completeness (needs no PDFs) to prioritize that work.
Recipe-tier forms have a pointer-only `mapping.json` and are skipped here.

## Two case shapes — important

There are **two distinct data shapes** in this project; do not conflate them:

- **Engine case shape** — what the filler here consumes: top-level `court`
  (`county`/`location`/`name`), `docket_no`/`case_no`, `notary_county`,
  `parties` (role → object), `facts`. See `examples/case.fami.json`.
- **Canonical fact object** — `{matter, parties, party, facts}`, defined in
  `docs/integrations/README.md`. This is what each form's `mapping.json`
  targets, and what external adapters translate their host data into.

The engine fills from the **engine** shape; `mapping.json` is the portable
boundary for **adapters**. `canonical.py` bridges the two: `to_engine_case()`
translates a canonical fact object into an engine case (`matter.*` → `court`/
`docket_no`, `party.date_of_birth` → `dob`, flat `party` → `parties.plaintiff`
when no roles are given). `engine/fill.py` auto-detects the shape, so a form's
`examples/sample_case.json` (canonical) fills end-to-end — through the generic
map **and** the form's recipe. An engine-shape case passes through unchanged.

## Recipes

`fill_and_audit.RECIPE3` maps 71 form ids to 32 recipe modules (several forms
share a family recipe, e.g. `infer_ad_family`); `recipes/` ships 42 `infer_*.py`
files, so 10 are not currently wired into the dispatch. A recipe exposes
`process(kv, case) -> (kv, changes)` and refines the generic map for forms that
a flat field→value map can't express (multi-column rows, composed narrative
blanks, computed dates). For `recipe`-tier forms the recipe is authoritative;
the per-form `mapping.json` is just a pointer to it.

## Not included

- **Vision audit.** `fill_and_audit.py` also contains a render → vision-model
  audit pass (flagging truncation/misalignment). It needs Pillow and a local
  vision-language model endpoint, and its CLI still assumes the engine-repo
  layout — it is not wired for the OSS paths. The fill path above does not use it.
- **Addendum overflow rendering.** `form_filler` references an optional
  `addendum` module for overflow pages; it is not bundled, and `fill_one` calls
  the filler with `addendum_policy="none"`, so overflowing fields are width-fit
  rather than spilled to an addendum page.
