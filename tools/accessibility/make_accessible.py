#!/usr/bin/env python3
"""One-command accessible filled court form — the whole a11y product in a driver.

Ported from maine-probate-forms-oss. Produces a PDF/UA-1-oriented accessible
filled form, fully offline/free, from a form id + canonical fact object:

  [1/6] blank   ensure the blank source PDF is on disk (tools/fetch_pdfs.py)
  [2/6] embed   ghostscript re-distill to embed the SOURCE fonts on the BLANK
                (before fill — embedding a filled form would flatten it)
  [3/6] fill    engine.fill_via_mapping from the case (mapping.json-driven)
  [4/6] tag     caption-driven /TU + title + /Lang + tab order (remediate_form),
                then OpenDataLoader content tag tree + PDF/UA id (pipeline)
  [5/6] repair  embed the widget/checkbox fonts the fill introduces + ToUnicode
  [6/6] verify  optional veraPDF UA-1 report

Every external tool (ghostscript, opendataloader-pdf, veraPDF) is auto-detected
and OPTIONAL — a missing one degrades with a warning, not a failure. Override
binaries via GHOSTSCRIPT / ODL_PYTHON / VERAPDF / WIDGET_TTF / ZAPF_TTF.

    python3 tools/accessibility/make_accessible.py --form FM-042 \
        --case case.json --out FM-042.accessible.pdf --verify

This repo ships no court PDFs; the blank is fetched at runtime from the official
portal. Filled output is a draft, NOT legal advice — verify before filing.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent.parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from engine.fill_via_mapping import fill_via_mapping  # noqa: E402
import accessibility_pipeline as pipe  # noqa: E402
import embed_widget_font  # noqa: E402
import split_shared_fields  # noqa: E402
import pikepdf  # noqa: E402

OSS_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
GHOSTSCRIPT = os.environ.get("GHOSTSCRIPT", "gs")


def _embed_fonts_on_blank(blank: pathlib.Path, out: pathlib.Path) -> bool:
    """gs re-distill embedding all fonts. Run on the BLANK (pre-fill): a re-distill
    of a FILLED form flattens widgets + strips ToUnicode, exploding UA-1."""
    try:
        subprocess.run(
            [GHOSTSCRIPT, "-q", "-dNOPAUSE", "-dBATCH", "-sDEVICE=pdfwrite",
             "-dEmbedAllFonts=true", "-dSubsetFonts=true", "-dCompatibilityLevel=1.7",
             f"-sOutputFile={out}",
             "-c", "<</NeverEmbed [ ]>> setdistillerparams", "-f", str(blank)],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return out.exists()
    except Exception:  # noqa: BLE001
        return False


def _temp_form_root(fid: str, blank_pdf: pathlib.Path) -> pathlib.Path:
    """A throwaway forms-root whose <fid>.pdf is `blank_pdf`, with schema/mapping/
    examples symlinked back, so engine.fill_via_mapping fills the chosen blank."""
    root = pathlib.Path(tempfile.mkdtemp(prefix="a11y_root_"))
    fdir = root / fid
    fdir.mkdir(parents=True)
    src = OSS_ROOT / "forms" / fid
    for name in ("schema.json", "mapping.json", "examples"):
        if (src / name).exists():
            os.symlink(src / name, fdir / name)
    shutil.copy(blank_pdf, fdir / f"{fid}.pdf")
    return root


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--form", required=True)
    ap.add_argument("--case", type=pathlib.Path,
                    help="canonical fact object JSON (default: the form's sample)")
    ap.add_argument("--out", type=pathlib.Path, required=True)
    ap.add_argument("--source", type=pathlib.Path,
                    help="blank PDF (default: forms/<ID>/<ID>.pdf)")
    ap.add_argument("--lang", default="en-US")
    ap.add_argument("--title", default=None)
    ap.add_argument("--embed-source-fonts", action="store_true",
                    help="gs re-distill to embed SOURCE fonts on the blank. OFF by "
                    "default: unlike probate's flat PDFs (widgets injected after "
                    "gs), court blanks already carry AcroForm widgets and gs "
                    "pdfwrite flattens them, breaking the fill. A non-flattening "
                    "source-font embed is future work; fill-introduced fonts are "
                    "still repaired in [5/6].")
    ap.add_argument("--verify", action="store_true", help="run veraPDF UA-1")
    a = ap.parse_args()

    fdir = OSS_ROOT / "forms" / a.form
    schema = fdir / "schema.json"
    if not schema.exists():
        print(f"unknown form {a.form} (no {schema})", file=sys.stderr)
        return 2
    blank = a.source or (fdir / f"{a.form}.pdf")
    if not blank.exists():
        print(f"[1/6] blank MISSING: {blank}\n      fetch it first: "
              f"python3 tools/fetch_pdfs.py --forms {a.form}", file=sys.stderr)
        return 2
    print(f"[1/6] blank   {blank}")

    case = a.case or (fdir / "examples" / "sample_case.json")
    facts = json.loads(pathlib.Path(case).read_text())
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="a11y_"))

    # [2/6] embed source fonts on the blank (optional, pre-fill)
    fill_root = OSS_ROOT / "forms"
    if not a.embed_source_fonts:
        print("[2/6] embed   skipped (court blanks are pre-widgeted; gs would "
              "flatten them — pass --embed-source-fonts only for flat sources)")
    else:
        emb = tmp / "blank_embed.pdf"
        if _embed_fonts_on_blank(blank, emb):
            fill_root = _temp_form_root(a.form, emb)
            print("[2/6] embed   source fonts embedded on blank (ghostscript)")
        else:
            print("[2/6] embed   ghostscript unavailable — skipping source-font "
                  "embed (set GHOSTSCRIPT); fill fonts still repaired in [5/6]",
                  file=sys.stderr)

    # [2.5] split shared AcroForm fields (forms/<ID>/field_splits.json) on the
    # blank so each appearance becomes its own field — its own /TU and value,
    # instead of one field reused across semantically different boxes.
    splits = split_shared_fields.specs_for(a.form)
    if splits:
        blank_now = (fill_root / a.form / f"{a.form}.pdf") if fill_root != (OSS_ROOT / "forms") else blank
        sp = pikepdf.open(str(blank_now))
        n = split_shared_fields.split(sp, splits)
        if n:
            if fill_root == (OSS_ROOT / "forms"):
                fill_root = _temp_form_root(a.form, blank)  # stage symlinks first
            sp.save(str(fill_root / a.form / f"{a.form}.pdf"))
            print(f"[2.5]  split  {n} shared field(s) -> own field+/TU")
        sp.close()

    # [3/6] fill
    res = fill_via_mapping(a.form, facts, tmp, forms_root=fill_root)
    if not res.get("ok"):
        print(f"[3/6] fill FAILED: {res.get('error')}", file=sys.stderr)
        return 1
    filled = pathlib.Path(res["out_pdf"])
    print(f"[3/6] fill    {res['fields_written']} field(s) written")

    # [4/6] tag (remediate + OpenDataLoader + finalize) via the pipeline
    tagged = tmp / "tagged.pdf"
    done, title = pipe.remediate_form.remediate(
        str(filled), str(tmp / "step1.pdf"), str(schema), a.lang, a.title)
    try:
        odl = pipe.tag_with_opendataloader(tmp / "step1.pdf", tmp)
        tree = "with content tag tree"
    except Exception:  # noqa: BLE001
        odl = tmp / "step1.pdf"
        tree = "field names/title/lang/tabs only (OpenDataLoader absent)"
    pipe.finalize(str(odl), str(tagged))
    print(f"[4/6] tag     /TU {done['tu_set']}/{done['tu_total']}, "
          f"title '{title}', {tree}")

    # [5/6] repair fill-introduced fonts (+ ToUnicode)
    try:
        embed_widget_font_main(tagged, a.out)
        print(f"[5/6] repair  widget/subset fonts embedded -> {a.out}")
    except Exception as e:  # noqa: BLE001
        shutil.copy(tagged, a.out)
        print(f"[5/6] repair  font embed skipped ({type(e).__name__}: {e})",
              file=sys.stderr)

    # [6/6] verify
    if a.verify:
        print("[6/6] verify  " + pipe.validate(str(a.out)).replace("\n", "\n        "))
    else:
        print("[6/6] verify  skipped (pass --verify for veraPDF UA-1)")
    return 0


def embed_widget_font_main(inp: pathlib.Path, out: pathlib.Path):
    """Embed all unembedded base-14 text fonts (+ optional ZapfDingbats) + ToUnicode."""
    import pikepdf
    pdf = pikepdf.open(str(inp))
    embed_widget_font.repair_fonts(pdf, zapf=embed_widget_font.ZAPF)
    pdf.save(str(out))


if __name__ == "__main__":
    raise SystemExit(main())
