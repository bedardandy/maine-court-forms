#!/usr/bin/env python3
"""Filled court form -> tagged, PDF/UA-identified PDF — shim over the shared
``maine-forms-engine`` (``maine_forms_engine.accessibility.
accessibility_pipeline``; this repo was the extraction donor, byte-identical
at extraction).

Steps: remediate (caption-derived /TU + title + /Lang + tabs) -> OpenDataLoader
content tag tree -> finalize (7.18.4 form-kids fix, CIDSet strip, PDF/UA-id
stamp) -> optional veraPDF validate. External tools come from ``ODL_PYTHON``
and ``VERAPDF`` env vars, as before.

    python3 accessibility_pipeline.py filled.pdf out.pdf \
        --schema forms/<ID>/schema.json [--validate]
"""
from maine_forms_engine.accessibility import remediate_form  # noqa: F401
from maine_forms_engine.accessibility.accessibility_pipeline import (  # noqa: F401
    ODL_PYTHON,
    VERAPDF,
    _fix_form_kids,
    finalize,
    main,
    tag_with_opendataloader,
    validate,
)

if __name__ == "__main__":
    raise SystemExit(main())
