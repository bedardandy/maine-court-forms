# PandaDoc adapter (spec — not built)

[PandaDoc](https://developers.pandadoc.com) is a document-automation / e-sign
SaaS. The adapter syncs a form's field schema into a PandaDoc **template**
and pushes filled documents via the API, adding e-signature routing on top
of the static PDF.

## Mapping

| PandaDoc concept | Source in this library |
|---|---|
| Template | the form's `<FORM_ID>.pdf` uploaded once |
| Template field (text/date/checkbox) | each `schema.json` field (type-mapped) |
| Field merge name | canonical fact-key from `mapping.json` |
| Recipient roles | `parties` in the canonical fact object |
| Document name / folder | `form.yaml` title / category |

## Type mapping

| schema.json type | PandaDoc field type |
|---|---|
| Text | `text` |
| CheckBox | `checkbox` |
| date-like label (`mapping` → `today()` / `date_of_birth`) | `date` |
| signature label | `signature` |

## Flow

1. **Sync (once per form):** `POST /templates` with the PDF, then create
   fields from `schema.json` rects (PandaDoc uses page + position, which
   the rects supply directly). Store the returned `template_uuid` in a
   side index `catalog/pandadoc_templates.json`.
2. **Fill:** `POST /documents` from `template_uuid` with
   `field_values` = canonical facts resolved through `mapping.json`.
3. **Route:** attach recipients from `parties` for signature.

## Notes

- `schema.json` rects are in PDF points with origin assumptions documented
  in `docs/architecture.md`; confirm PandaDoc's y-origin (top-left) vs the
  schema's before placing fields.
- Recipe-tier forms with computed content should be filled by the engine
  *first*, then uploaded as a finished PDF for signature only (skip field
  creation) — PandaDoc can't reproduce the recipe logic.
