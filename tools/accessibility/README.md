# Filled-form accessibility builder (court-forms)

Ported from the `maine-probate-forms-oss` accessibility builder (which reached
76/79 forms clean PDF/UA-1, fully offline/free) and adapted to this repo. Same
method: a deterministic, schema/caption-driven remediation + OpenDataLoader tag
tree + font repair, validated by veraPDF. Filled output is a draft, **not legal
advice** — verify before filing.

## The pipeline

| step | what | tool |
|---|---|---|
| accessible field names (`/TU`) + title + `/Lang` + tab order | WCAG 1.3.1/4.1.2, 2.4.2, 3.1.1, 2.4.3 | `remediate_form.py` (pikepdf) |
| content/structure tag tree (PDF/UA 7.1/7.2/7.18) | logical reading order, tables | OpenDataLoader (optional) |
| 7.18.4 form-kids fix, CIDSet strip, PDF/UA-id stamp | | `accessibility_pipeline.finalize` |
| font repair (Helvetica→Liberation Sans, ZapfDingbats, ToUnicode) | 7.21.x | `embed_widget_font.py` |

`make_accessible.py` runs all of it from a form id + case.

## The one court-specific adaptation: `/TU` from the printed caption

In probate, `schema.json`'s `label` is human-readable, so `/TU` = label. **In
court-forms the `label` is the raw AcroForm field-name** — often a bare slug
(`1`, `2`, `1_2`, `2_5`, `mmddyyyy_2`) and frequently *misaligned* with the
box's real meaning (see the sentinel/lint findings). Announcing that to a screen
reader is useless or wrong. So `remediate_form.py` derives each widget's
accessible name from its **printed caption** (the same nearest-caption geometry
as `tools/label_key_lint.py`), falling back to a humanized mapping key, then the
schema label:

    /TU = printed caption  |  humanized mapping key  |  schema label

e.g. `Plaintiff`→"Plaintiff name", `LocationTown`→"Location (Town)",
`Datemmddyyyy`→"Date", `signature…`→"Your signature".

## Run

```bash
# one command (blank fetched if absent; gs/OpenDataLoader/veraPDF auto-detected)
python3 tools/accessibility/make_accessible.py --form FM-042 \
    --case case.json --out FM-042.accessible.pdf --verify

# or the steps individually:
python3 tools/accessibility/remediate_form.py filled.pdf step1.pdf --schema forms/FM-042/schema.json
python3 tools/accessibility/accessibility_pipeline.py filled.pdf out.pdf --schema forms/FM-042/schema.json --validate
python3 tools/accessibility/embed_widget_font.py out.pdf final.pdf
```

Every external tool degrades gracefully: no OpenDataLoader → keep field
names/title/lang/tabs and skip the tag tree (never fakes `/MarkInfo Marked` over
an empty tree); no veraPDF → skip validation. Override binaries via
`ODL_PYTHON` / `VERAPDF` / `GHOSTSCRIPT` / `WIDGET_TTF` / `ZAPF_TTF`.

## Two court-specific differences from probate (and their status)

1. **No gs source-font embed on the blank.** Probate fills *flat* PDFs by
   injecting widgets after a gs re-distill, so `-dEmbedAllFonts` on the blank is
   safe. Court blanks already carry AcroForm widgets and `fill_via_mapping` fills
   them in place — `gs pdfwrite` **flattens** those widgets, breaking the fill.
   So `--embed-source-fonts` is OFF by default; the source-font residual
   (7.21.4.1 for fonts the *source* leaves unembedded) needs a **non-flattening**
   in-place embed (Phase 2). Fonts the *fill* introduces are still repaired.
2. **Shared-field split (Phase 2).** Some court forms reuse one AcroForm field
   across semantically different boxes (e.g. OTH-029 `2_5` = a child-DOB table
   cell AND a confidential-address line). A screen reader can't name one field
   two ways, and the mapping can't separate them — both need the field split
   into distinct widgets. That field-rename pass (regenerating schema/mapping
   field-ids in lockstep) is the next phase; see the accessibility roadmap.

## Source fonts: embedded in place (no flatten)

Court source PDFs leave Helvetica AND Times-Roman / Courier unembedded
(7.21.4.1). Since court fills are existing-widget, `embed_widget_font.repair_fonts()`
embeds a metric-compatible Liberation substitute for **every** base-14 text
family in place (Helvetica/Arial→Sans, Times→Serif, Courier→Mono, style-matched),
plus ToUnicode — no gs re-distill, no flatten. The only residual is the
ZapfDingbats checkbox-check glyph (needs a symbol TTF via `ZAPF_TTF`); without
one it's the documented font-only ceiling, so a form with no checkmarks reaches
veraPDF UA-1 **0 fails**.

## Shared-field collisions (`shared_field_report.py`) — Phase 2 worklist

`python3 tools/accessibility/shared_field_report.py` enumerates fields reused
across semantically different boxes (the OTH-029 `2_5` class) — the Phase-2
field-split worklist (**15 collisions across 350 forms**). Radio/checkbox option
groups (which legitimately share a field name) are excluded.

## Fleet baseline (this checkout)

`opendataloader-pdf` (pip, Java 17) and `veraPDF` (`verapdf` on PATH, or set
`VERAPDF`) are installed here, so the full tagged pipeline + validation run.
Representative result — **FM-042: 282 → 1** failed check (the lone ZapfDingbats
residual); content tag tree (7.1/7.2), form-field tags (7.18), Marked (6.2) all
0. A fleet run (`make_accessible --verify` per verified form) buckets each as
clean (0) / other. **Full run over 217 verified forms: 183 clean (84%, 0 fails),
0 errors** (with the synthesized ZapfDingbats embed — up from 71% before it). The
remaining 34 carry small residuals (mostly 1–3 checks), dominated by
OpenDataLoader free-tier tag-tree nits — 7.4.2 heading nesting (18), 7.1 untagged
element (9), 7.10 (3) — plus a few font/ToUnicode stragglers (7.21.7 ×6, .4.1 ×3,
.8 ×3). The tag-tree nits are the same honest free-tier ceiling probate hit
(AF-105); a better tagger or Acrobat would close them.
