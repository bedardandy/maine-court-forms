#!/usr/bin/env python3
"""Form-field accessibility remediation — shim over the shared
``maine-forms-engine`` (``maine_forms_engine.accessibility.remediate_form``;
this repo was the extraction donor).

Sets each widget's accessible name (/TU), document title, /Lang, and tab
order. This repo's strategy is the package default (``naming="caption"``):
each widget's /TU is derived from the caption text printed next to it on the
page, falling back to the schema label / humanized canonical key. The package
also offers ``--naming schema-label`` (the probate sibling's strategy); the
default output here is unchanged.

    python3 remediate_form.py <filled.pdf> <out.pdf> --schema forms/<ID>/schema.json
"""
from maine_forms_engine.accessibility.remediate_form import (  # noqa: F401
    _accessible_names,
    _clean_caption,
    _humanize_key,
    _is_descriptive,
    _row_words,
    caption_names,
    main,
    remediate,
    schema_label_names,
)

if __name__ == "__main__":
    raise SystemExit(main())
