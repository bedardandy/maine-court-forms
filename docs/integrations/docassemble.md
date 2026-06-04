# docassemble adapter (spec — not built)

[docassemble](https://docassemble.org) is the de-facto open-source guided
-interview engine for legal forms (used widely by legal aid / LSC). It is
the closest existing OSS analog to this library and the highest-value
adapter: it turns a form folder into a web interview that ends in a filled,
downloadable PDF.

## Mapping

| docassemble concept | Source in this library |
|---|---|
| interview `question` blocks | derived from `SKILL.md` "facts needed" + `fields.csv` |
| variable names | canonical fact-keys from `mapping.json` |
| `pdf template file` | the form's `<FORM_ID>.pdf` |
| `fields:` (PDF field → variable) | inverse of `mapping.json` (field_id → fact-key) |
| metadata / title | `form.yaml` (title, category, source_url) |

## Generated artifact

A `docassemble` package per form (or per family), e.g.
`maine_AD_001.yml`:

```yaml
metadata:
  title: AD-001 — Petition for Adoption and Change of Name
---
objects:
  - matter: DAObject
  - petitioner: Individual
---
question: |
  Court information
fields:
  - County: matter.court_county
  - Docket number: matter.docket_number
---
attachment:
  - name: AD-001
    pdf template file: AD-001.pdf
    fields:
      - "name_of_petitioner": ${ petitioner.name.full() }
      - "docket_no_2": ${ matter.docket_number }
      # ...inverse of mapping.json
```

## Generator sketch

`tools/gen_docassemble.py <FORM_ID>`:
1. Load `mapping.json`; invert to `{field_id: fact_key}`.
2. Group fact-keys into interview pages (court block, party block,
   form-specific). `SKILL.md` order is a reasonable default page order.
3. Emit the `attachment.fields` list from the inverted map.
4. Copy the PDF into the package's `data/templates/`.

## Open questions

- Checkbox/radio widgets need value enumeration — pull from `schema.json`
  widget options where present.
- Recipe forms encode logic docassemble can't express declaratively
  (computed narratives, font auto-fit). For those, call the engine as a
  docassemble background action rather than using native `pdf template`.
