# Contributing

This library is built form-by-form. The smallest useful contribution is
improving a single form folder; the most valuable is verifying a mapping
against a real filled output.

## Adding or regenerating forms

The per-form folders are generated, not hand-written, from upstream source
data. Use the scaffold tool:

```bash
# --skills-stash is optional; omit --forms to scaffold every form.
python3 tools/scaffold_forms.py \
  --engine-repo  /path/to/engine-repo \
  --pdf-stash    /path/to/blank/pdfs \
  --skills-stash /path/to/prior/skills \
  --forms AD-001,AD-022
```

It writes `schema.json`, `fields.csv`, `form.yaml`, `README.md`,
`SKILL.md`, `mapping.json`, and copies the PDF. It never edits the source
repos.

## Verifying a form (the high-value work)

A form is **production-ready** when its `mapping.json` is verified, not
just heuristic:

1. Fill it with `examples/sample_case.json` (or a real fact object).
2. Flatten and visually check the output (or run the engine's vision
   audit).
3. Fix the mapping / promote to a recipe if there are `truncated`,
   `wrong_position`, `wrong_column`, or `blank_required` findings.
4. Flip `form.yaml: automation_status` to `recipe` (or note "verified" in
   `mapping.json` `status`) once it audits clean.

## Mapping quality bar

- `mapping.json` `status` is the trust tier. Shipped values: `recipe` (engine recipe), `verified` (render-verified mapping), `opus-adjudicated` (model-adjudicated), `no-mappable-fields`. Intermediate pipeline statuses (`draft-heuristic`, `ai-mapped`, `vision-mapped`, `opus-reviewed`) are written by tools/ during remapping and must be promoted before shipping.
- `status: recipe` → authoritative; do not hand-edit (regenerate from the
  recipe in `engine/recipes/`).
- Never invent canonical fact-keys ad hoc — reuse the shape in
  `docs/integrations/README.md` so mappings stay portable across adapters.

## Scope discipline

One form (or one form family) per PR. Don't bundle engine changes with form
data changes. Keep run artifacts out of git (see `.gitignore`).
