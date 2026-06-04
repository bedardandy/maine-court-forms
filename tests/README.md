# Tests — the fill-engine regression gate

These tests turn the placement-correctness checks that used to be run by hand
into an enforced gate, so a fix can't silently regress (the GS-001 lesson:
`status: "verified"` means "checked once," not "stays correct").

## Layers

| File | What it checks | Needs blank PDFs? | In CI? |
|---|---|---|---|
| `test_recipe_smoke.py` | every recipe-dispatched form runs `process()` without crashing | no | ✅ |
| `test_placement.py` | pinned, render-verified field values (recipe + mapping) | no | ✅ |
| `test_fill_smoke.py` | every mapping-tier form fills end-to-end; OTH-029 field-split fires | yes (auto-skips) | ✅ (skips) |
| `test_opus_judge.py` | Claude Opus 4.8 judges sentinel renders (value-vs-label oracle) | yes | ❌ opt-in |

Blank PDFs are fetched from the official portal, not shipped — so PDF-dependent
tests **auto-skip** when the blank is absent (i.e. they run in full locally and
no-op in CI). The PDF-free recipe smoke + placement pins are the CI gate.

## Run

```bash
# deterministic suite (no install needed beyond pymupdf/pikepdf):
python3 -m unittest discover -s tests -v
# or with pytest:
python3 -m pytest tests/ --ignore=tests/test_opus_judge.py

# the Opus 4.8 semantic judge (opt-in; costs tokens, needs the `claude` CLI):
MCF_OPUS_JUDGE=1 python3 -m unittest tests.test_opus_judge
# or directly, for a report:
python3 tests/opus_judge.py --forms JV-006-W NC-001 PC-034
```

## Adding a pin

When you fix a placement defect and verify it by render, add a line to
`RECIPE_PINS` / `MAPPING_PINS` in `test_placement.py`. The value must be what
the engine actually emits (e.g. dates are US-formatted `MM/DD/YYYY`).

The Opus judge (`opus_judge.py`) runs headless on the Claude subscription via
OAuth — it strips `ANTHROPIC_API_KEY` from the child env so a stale key can't
override the session.
