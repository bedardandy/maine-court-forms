# Architecture

## The form folder is the unit

Everything is organized around a self-contained `forms/<FORM_ID>/` folder.
No tool needs to reach outside the folder to fill a form (except the
optional shared `engine/`). This is what makes the library portable and
lets forms be added, reviewed, and shipped one at a time.

## Data flow

```
official PDF ──► schema extraction ──► schema.json (field id/type/rect/page)
                                           │
catalog (title, court, law, source) ──────┼──► form.yaml + README.md
                                           │
field labels + recipes ────────────────────┼──► mapping.json + SKILL.md
                                           ▼
                          canonical fact object ──► [filler] ──► filled PDF
                                                        │
                                                   [vision audit] ──► findings
```

## Schema notes

- `schema.json` field `rect` is `[x0, y0, x1, y1]` in PDF points.
- `field_id` is a normalized, stable handle for the AcroForm widget; the
  printed `label` is the human text nearest the widget (best-effort and
  occasionally off-by-one on dense forms — recipes correct these).
- `by_category` / `by_risk_tier` summarize fields for triage.

## Fill tiers

| Tier | What fills it | When |
|---|---|---|
| `schema-only` | generic schema filler + `mapping.json` | most forms |
| `recipe` | a dedicated `engine/recipes/infer_*.py` | forms with quirks |

Recipes exist because some forms can't be filled by a flat field→value map:
multi-column rows, narrative blanks that need composed sentences, computed
dates, font auto-fit for long values, or off-by-one label schemas. A recipe
encodes that logic and is the authoritative mapping for its form.

## Audit (optional but recommended)

The reference engine includes a vision audit: render the filled+flattened
PDF, ask a vision model to flag `truncated`, `blank_required`,
`wrong_position`, `wrong_column`, `overlaps_glyph`. Run it N times and take
consensus to denoise. This is how the recipe mappings were verified and is
the feedback edge an agentic integration should close the loop on.

## Text-fitting

A large share of real fill defects are width problems, not logic problems:
a name or address that overflows its widget. The engine handles this
systemically (USPS address abbreviation, name initial-collapse, font
auto-fit) before falling back to widget widening. Integrators reusing the
engine get this for free; those building their own filler should budget for
it.
