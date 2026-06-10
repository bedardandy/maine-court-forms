#!/usr/bin/env python3
"""Canonical fact object -> engine-case adapter — shim over the shared
``maine-forms-engine``.

The implementation moved verbatim into ``maine_forms_engine.fill.canonical``
(this repo was the extraction donor); this module keeps the repo's
``engine.canonical`` import path and API stable.
"""
from maine_forms_engine.fill.canonical import (  # noqa: F401
    _PARTY_KEY_REMAP,
    _remap_party,
    is_canonical,
    to_engine_case,
)
