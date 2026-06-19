# Per-field fill-value guidance (`fill_guidance.json`)

Every form ships `forms/<ID>/fill_guidance.json`: for each AcroForm field, what
*kind of text* belongs in it, whether it's required, and whether it's part of a
one-of choice group. It's built deterministically and offline by
`tools/derive_field_guidance.py`, consistent with the fill engine (it reuses
`engine.build_kv_map` heuristics and the canonical mapping keys).

> Not legal advice. Guidance is a machine-derived hint to be verified against
> the official form. Currency/time guidance is conservative because the printed
> `$` / AM-PM are not read by the offline deriver.

## Shape

```jsonc
{
  "form_id": "CV-007",
  "generated_by": "tools/derive_field_guidance.py",
  "value_types": ["address", "bar_number", "case_number", ...],
  "fields": {
    "plaintiff":      { "value_type": "person_name", "required": true,
                        "guidance": "A person's name ..." },
    "date_mmddyyyy":  { "value_type": "date", "format": "us_slash",
                        "required": false, "guidance": "A calendar date." },
    "superior_court": { "value_type": "checkbox", "required": false,
                        "conditional": { "rule": "exactly_one_of",
                          "group": ["superior_court", "district_court", ...] },
                        "guidance": "A checkbox: filled with 'X' ..." }
  }
}
```

## value_type vocabulary

`person_name`, `organization_name`, `address`, `city`, `state`, `zip`,
`phone`, `email`, `date` (with `format`: `us_slash` MM/DD/YYYY or `iso`),
`time`, `currency`, `percent`, `county`, `court_location`, `docket`,
`case_number`, `bar_number`, `checkbox`, `signature`, `free_text`.

Notable conventions, matching engine behavior:
- **currency** — enter digits (e.g. `1,250.00`). Many forms pre-print `$`; the
  engine strips a leading `$` so you don't get `$ $1,250.00`. Verify the form.
- **county** — a Maine county name without "County" (e.g. `Cumberland`).
- **time** — a wall-clock time; if the form pre-prints AM/PM, strike/circle the
  correct one by hand (the engine does not).
- **checkbox** — `"X"` only when the fact is explicitly true; never auto-checked.
- **signature** — a wet-ink/electronic blank, left empty by the engine; a
  signature-block subfield the engine *does* fill (a date-of-signing, a typed
  name) is classified by its mapping instead.
- **compound location** (a single blank labeled e.g. "City, State, ZIP") is
  typed `address`, not its trailing component.

## How it's derived (precedence)

1. checkbox widget → `checkbox`
2. a **mapped** field → its canonical key's type (ground truth — the engine
   fills it); mapped-but-unrecognized → `free_text` (never guessed from the
   widget id)
3. unmapped signature-category field → `signature`
4. unmapped field → subcategory, then field_id token heuristics
5. `required` = the field is mapped to one of `mapping.json` `facts.required`
6. `conditional` = the field is a member of a `constraints.json`
   `mutually_exclusive` (one-of) or `requires` group

## Validation & preflight

- `tools/value_types.py` validates a supplied value against a `value_type`
  (lenient — only high-confidence mismatches). `preflight.py` uses it to emit
  `value-type` **warnings** (never errors) when a fact looks wrong for its
  field (e.g. a phone number in a ZIP field).
- The `evals/guidance/` layer proves the artifact is complete, drift-free,
  type-consistent with the mapping, and that the validators don't false-positive
  (run `python3 -m evals.run --layer guidance`).

## Regenerating

After changing a `mapping.json` or `constraints.json`:

```bash
python3 tools/derive_field_guidance.py --all   # or --form CV-007 [--print]
```

Review the diff and commit; `evals/guidance/test_field_guidance.py` fails on
uncommitted drift.
