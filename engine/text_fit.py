"""Width-aware text shrinking — shim over the shared ``maine-forms-engine``.

The implementation moved verbatim into the shared package
(``maine_forms_engine.fill.text_fit``; this repo was the extraction donor);
this module keeps the repo's ``engine.text_fit`` import path and API stable.
"""
from maine_forms_engine.fill.text_fit import (  # noqa: F401
    abbreviate_address,
    fit,
    fit_name,
    widget_char_budget,
)
